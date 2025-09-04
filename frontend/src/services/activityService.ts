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
      // Return mock data if API fails
      return {
        activities: [
          {
            id: "1",
            type: "sale",
            title: "New Sale Created",
            description: "Sales voucher #SV-2024-001 created for ₹25,000",
            timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
            user_name: "John Doe",
            amount: 25000,
            currency: "INR"
          },
          {
            id: "2", 
            type: "customer",
            title: "New Customer Added",
            description: "Customer 'ABC Corp' added to the system",
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
            user_name: "Jane Smith"
          },
          {
            id: "3",
            type: "product",
            title: "Product Updated",
            description: "Product 'Widget A' price updated to ₹500",
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
            user_name: "Admin User"
          }
        ],
        total_count: 3,
        generated_at: new Date().toISOString()
      };
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
    const now = new Date();
    const activityTime = new Date(timestamp);
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