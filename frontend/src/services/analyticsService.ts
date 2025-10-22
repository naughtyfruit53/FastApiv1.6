// frontend/src/services/analyticsService.ts
import api from "../lib/api";
export interface CustomerAnalyticsData {
  customer_id: number;
  customer_name: string;
  total_interactions: number;
  last_interaction_date?: string;
  interaction_types: Record<string, number>;
  interaction_status: Record<string, number>;
  segments: Array<{
    segment_name: string;
    segment_value?: number;
    assigned_date: string;
    description?: string;
  }>;
  recent_interactions: Array<{
    interaction_type: string;
    subject: string;
    status: string;
    interaction_date: string;
  }>;
  calculated_at: string;
}
export interface SegmentAnalyticsData {
  segment_name: string;
  total_customers: number;
  total_interactions: number;
  avg_interactions_per_customer: number;
  interaction_distribution: Record<string, number>;
  activity_timeline: Array<{
    date: string;
    interaction_count: number;
  }>;
  calculated_at: string;
}
export interface DashboardMetrics {
  total_customers: number;
  total_interactions_today: number;
  total_interactions_week: number;
  total_interactions_month: number;
  top_segments: Array<{
    segment_name: string;
    customer_count: number;
  }>;
  recent_activity: Array<{
    customer_name: string;
    interaction_type: string;
    interaction_date: string;
  }>;
  calculated_at: string;
}
export const analyticsService = {
  getCustomerAnalytics: async (
    customerId: number,
    includeRecentInteractions: boolean = true,
    recentInteractionsLimit: number = 5,
  ): Promise<CustomerAnalyticsData> => {
    try {
      const response = await api.get(
        `/analytics/customers/${customerId}/analytics`,
        {
          params: {
            include_recent_interactions: includeRecentInteractions,
            recent_interactions_limit: recentInteractionsLimit,
          },
        },
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get customer analytics");
    }
  },
  getSegmentAnalytics: async (
    segmentName: string,
    includeTimeline: boolean = true,
    timelineDays: number = 30,
  ): Promise<SegmentAnalyticsData> => {
    try {
      const response = await api.get(
        `/analytics/segments/${segmentName}/analytics`,
        {
          params: {
            include_timeline: includeTimeline,
            timeline_days: timelineDays,
          },
        },
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get segment analytics");
    }
  },
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    try {
      const response = await api.get("/analytics/dashboard/metrics");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get dashboard metrics");
    }
  },
  getAvailableSegments: async (): Promise<string[]> => {
    try {
      const response = await api.get("/analytics/segments");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get available segments");
    }
  },
  getOrganizationSummary: async () => {
    try {
      const response = await api.get("/analytics/organization/summary");
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to get organization analytics summary",
      );
    }
  },

  // ===========================================
  // ADVANCED ANALYTICS ENDPOINTS
  // ===========================================

  getAdvancedMetrics: async (metricType: string, timeRange?: string) => {
    try {
      const response = await api.get(`/analytics/advanced/${metricType}`, {
        params: { time_range: timeRange },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get advanced metrics");
    }
  },

  getTrendAnalysis: async (metric: string, period: string = '30d') => {
    try {
      const response = await api.get('/analytics/trends', {
        params: { metric, period },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get trend analysis");
    }
  },

  getComparativeAnalysis: async (metrics: string[], compareBy: string = 'period') => {
    try {
      const response = await api.get('/analytics/comparative', {
        params: { metrics: metrics.join(','), compare_by: compareBy },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get comparative analysis");
    }
  },

  getCustomReport: async (reportConfig: {
    metrics: string[];
    dimensions: string[];
    filters?: Record<string, any>;
    date_range?: { start: string; end: string };
  }) => {
    try {
      const response = await api.post('/analytics/custom-report', reportConfig);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to generate custom report");
    }
  },

  exportAnalytics: async (format: 'csv' | 'excel' | 'pdf', dataType: string) => {
    try {
      const response = await api.get(`/analytics/export/${dataType}`, {
        params: { format },
        responseType: 'blob',
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to export analytics");
    }
  },

  getRealtimeMetrics: async () => {
    try {
      const response = await api.get('/analytics/realtime');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get realtime metrics");
    }
  },

  getPredictiveInsights: async (metricType: string, horizon: number = 30) => {
    try {
      const response = await api.get('/analytics/predictive', {
        params: { metric_type: metricType, horizon },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get predictive insights");
    }
  },
};
