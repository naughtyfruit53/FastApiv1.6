// frontend/src/services/analyticsService.ts

import api from '../lib/api';

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
    recentInteractionsLimit: number = 5
  ): Promise<CustomerAnalyticsData> => {
    try {
      const response = await api.get(`/analytics/customers/${customerId}/analytics`, {
        params: {
          include_recent_interactions: includeRecentInteractions,
          recent_interactions_limit: recentInteractionsLimit,
        },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get customer analytics');
    }
  },

  getSegmentAnalytics: async (
    segmentName: string,
    includeTimeline: boolean = true,
    timelineDays: number = 30
  ): Promise<SegmentAnalyticsData> => {
    try {
      const response = await api.get(`/analytics/segments/${segmentName}/analytics`, {
        params: {
          include_timeline: includeTimeline,
          timeline_days: timelineDays,
        },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get segment analytics');
    }
  },

  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    try {
      const response = await api.get('/analytics/dashboard/metrics');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get dashboard metrics');
    }
  },

  getAvailableSegments: async (): Promise<string[]> => {
    try {
      const response = await api.get('/analytics/segments');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get available segments');
    }
  },

  getOrganizationSummary: async () => {
    try {
      const response = await api.get('/analytics/organization/summary');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organization analytics summary');
    }
  }
};