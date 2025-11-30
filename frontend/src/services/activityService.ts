// frontend/src/services/activityService.ts
import api from "../lib/api";

// Raw activity from backend audit log
interface RawActivity {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  user_id: number;
  organization_id: number;
  description?: string;
  created_at: string;
  user_name?: string;
}

export interface RecentActivity {
  id: string;
  type: 'sale' | 'purchase' | 'customer' | 'vendor' | 'product' | 'user' | 'voucher' | 'order' | 'settings' | 'other';
  title: string;
  description: string;
  timestamp: string;
  user_name?: string;
  icon?: string;
  amount?: number;
  currency?: string;
}

export interface ActivityResponse {
  activities: RecentActivity[];
  total_count?: number;
  generated_at?: string;
}

// Map entity_type and action to human-readable title and type
const mapActivityToTitle = (entityType: string, action: string): { title: string; type: RecentActivity['type'] } => {
  const actionMap: Record<string, string> = {
    create: 'created',
    update: 'updated',
    delete: 'deleted',
    read: 'viewed'
  };
  
  const entityMap: Record<string, { label: string; type: RecentActivity['type'] }> = {
    voucher: { label: 'Voucher', type: 'voucher' },
    purchase_order: { label: 'Purchase Order', type: 'purchase' },
    sales_order: { label: 'Sales Order', type: 'sale' },
    sales_voucher: { label: 'Sales Voucher', type: 'sale' },
    purchase_voucher: { label: 'Purchase Voucher', type: 'purchase' },
    customer: { label: 'Customer', type: 'customer' },
    vendor: { label: 'Vendor', type: 'vendor' },
    product: { label: 'Product', type: 'product' },
    user: { label: 'User', type: 'user' },
    invoice: { label: 'Invoice', type: 'voucher' },
    order: { label: 'Order', type: 'order' },
    settings: { label: 'Settings', type: 'settings' },
    organization: { label: 'Organization', type: 'settings' }
  };
  
  const entity = entityMap[entityType.toLowerCase()] || { label: entityType, type: 'other' as const };
  const actionVerb = actionMap[action.toLowerCase()] || action;
  
  return {
    title: `${entity.label} ${actionVerb}`,
    type: entity.type
  };
};

const activityService = {
  getRecentActivities: async (limit: number = 10): Promise<ActivityResponse> => {
    try {
      const response = await api.get(`/organizations/recent-activities?limit=${limit}`);
      const data = response.data;
      
      // Transform backend activities to frontend format
      const activities: RecentActivity[] = (data.activities || []).map((raw: RawActivity) => {
        const { title, type } = mapActivityToTitle(raw.entity_type, raw.action);
        return {
          id: String(raw.id),
          type,
          title,
          description: raw.description || `${raw.action} on ${raw.entity_type}${raw.entity_id ? ` #${raw.entity_id}` : ''}`,
          timestamp: raw.created_at,
          user_name: raw.user_name
        };
      });
      
      return {
        activities,
        total_count: activities.length,
        generated_at: data.generated_at || new Date().toISOString()
      };
    } catch (error) {
      console.error("Failed to fetch recent activities:", error);
      throw error;
    }
  },

  getActivityIcon: (type: RecentActivity['type']): string => {
    const iconMap: Record<RecentActivity['type'], string> = {
      sale: "💰",
      purchase: "🛒", 
      customer: "👤",
      vendor: "🏢",
      product: "📦",
      user: "👥",
      voucher: "📋",
      order: "📦",
      settings: "⚙️",
      other: "📝"
    };
    return iconMap[type] || "📝";
  },

  formatActivityTime: (timestamp: string): string => {
    if (!timestamp) {
      return 'Unknown time';
    }

    const activityTime = new Date(timestamp);
    
    if (isNaN(activityTime.getTime())) {
      return 'Invalid Date';
    }
    
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - activityTime.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return activityTime.toLocaleDateString();
  }
};

export default activityService;
