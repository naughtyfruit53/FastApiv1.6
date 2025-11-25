// frontend/src/services/activityService.ts
import api from "../lib/api";

export interface RecentActivity {
  id: string;
  type: 'sale' | 'purchase' | 'customer' | 'vendor' | 'product' | 'user' | 'voucher';
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
  total_count: number;
  generated_at: string;
}

const activityService = {
  getRecentActivities: async (limit: number = 10): Promise<ActivityResponse> => {
    try {
      const response = await api.get<ActivityResponse>(`/organizations/recent-activities?limit=${limit}`);
      return response.data;
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
      voucher: "📋"
    };
    return iconMap[type] || "📝";
  },

  formatActivityTime: (timestamp: string): string => {
    if (!timestamp) {
      console.warn('Missing timestamp for activity');
      return 'Recent';
    }

    const activityTime = new Date(timestamp);
    
    if (isNaN(activityTime.getTime())) {
      console.error('Invalid timestamp format:', timestamp);
      return 'Invalid Date';
    }
    
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - activityTime.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago}`;
    
    return activityTime.toLocaleDateString();
  }
};

export default activityService;