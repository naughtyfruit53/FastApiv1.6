// frontend/src/services/serviceAnalyticsService.ts

import api from '../lib/api';

// Enums matching the backend
export enum ReportPeriod {
  TODAY = 'today',
  WEEK = 'week',
  MONTH = 'month',
  QUARTER = 'quarter',
  YEAR = 'year',
  CUSTOM = 'custom'
}

export enum MetricType {
  JOB_COMPLETION = 'job_completion',
  TECHNICIAN_PERFORMANCE = 'technician_performance',
  CUSTOMER_SATISFACTION = 'customer_satisfaction',
  JOB_VOLUME = 'job_volume',
  SLA_COMPLIANCE = 'sla_compliance'
}

// Interfaces matching the backend schemas
export interface TimeSeriesDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface JobCompletionMetrics {
  total_jobs: number;
  completed_jobs: number;
  pending_jobs: number;
  cancelled_jobs: number;
  completion_rate: number;
  average_completion_time_hours?: number;
  on_time_completion_rate: number;
  jobs_by_status: Record<string, number>;
  completion_trend: TimeSeriesDataPoint[];
}

export interface TechnicianPerformanceMetrics {
  technician_id: number;
  technician_name: string;
  total_jobs_assigned: number;
  jobs_completed: number;
  jobs_in_progress: number;
  average_completion_time_hours?: number;
  customer_rating_average?: number;
  utilization_rate: number;
  efficiency_score: number;
}

export interface CustomerSatisfactionMetrics {
  total_feedback_received: number;
  average_overall_rating: number;
  average_service_quality?: number;
  average_technician_rating?: number;
  average_timeliness_rating?: number;
  average_communication_rating?: number;
  satisfaction_distribution: Record<string, number>;
  nps_score?: number;
  recommendation_rate?: number;
  satisfaction_trend: TimeSeriesDataPoint[];
}

export interface JobVolumeMetrics {
  total_jobs: number;
  jobs_per_day_average: number;
  peak_day?: string;
  peak_day_count: number;
  volume_trend: TimeSeriesDataPoint[];
  jobs_by_priority: Record<string, number>;
  jobs_by_customer: Array<{
    customer_id: number;
    customer_name: string;
    job_count: number;
  }>;
}

export interface SLAComplianceMetrics {
  total_jobs_with_sla: number;
  sla_met_count: number;
  sla_breached_count: number;
  overall_compliance_rate: number;
  average_resolution_time_hours?: number;
  compliance_by_priority: Record<string, number>;
  compliance_trend: TimeSeriesDataPoint[];
  breach_reasons: Record<string, number>;
}

export interface AnalyticsDashboard {
  organization_id: number;
  report_period: ReportPeriod;
  start_date: string;
  end_date: string;
  job_completion: JobCompletionMetrics;
  technician_performance: TechnicianPerformanceMetrics[];
  customer_satisfaction: CustomerSatisfactionMetrics;
  job_volume: JobVolumeMetrics;
  sla_compliance: SLAComplianceMetrics;
  generated_at: string;
}

export interface AnalyticsRequest {
  start_date?: string;
  end_date?: string;
  period?: ReportPeriod;
  technician_id?: number;
  customer_id?: number;
}

export interface ReportConfiguration {
  id: number;
  organization_id: number;
  name: string;
  description?: string;
  metric_types: MetricType[];
  filters: Record<string, any>;
  schedule_enabled: boolean;
  schedule_frequency?: string;
  email_recipients: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TechnicianOption {
  id: number;
  name: string;
  email: string;
}

export interface CustomerOption {
  id: number;
  name: string;
  email: string;
}

export const serviceAnalyticsService = {
  /**
   * Get complete analytics dashboard
   */
  getAnalyticsDashboard: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<AnalyticsDashboard> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/dashboard`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get analytics dashboard');
    }
  },

  /**
   * Get job completion metrics
   */
  getJobCompletionMetrics: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<JobCompletionMetrics> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/job-completion`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get job completion metrics');
    }
  },

  /**
   * Get technician performance metrics (requires manager permissions)
   */
  getTechnicianPerformanceMetrics: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<TechnicianPerformanceMetrics[]> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/technician-performance`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get technician performance metrics');
    }
  },

  /**
   * Get customer satisfaction metrics
   */
  getCustomerSatisfactionMetrics: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<CustomerSatisfactionMetrics> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/customer-satisfaction`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get customer satisfaction metrics');
    }
  },

  /**
   * Get job volume metrics
   */
  getJobVolumeMetrics: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<JobVolumeMetrics> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/job-volume`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get job volume metrics');
    }
  },

  /**
   * Get SLA compliance metrics (requires manager permissions)
   */
  getSLAComplianceMetrics: async (
    organizationId: number,
    filters: AnalyticsRequest = {}
  ): Promise<SLAComplianceMetrics> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/sla-compliance`, {
        params: filters
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get SLA compliance metrics');
    }
  },

  /**
   * Get available technicians for filtering
   */
  getAvailableTechnicians: async (organizationId: number): Promise<TechnicianOption[]> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/technicians`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get available technicians');
    }
  },

  /**
   * Get available customers for filtering
   */
  getAvailableCustomers: async (organizationId: number): Promise<CustomerOption[]> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/customers`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get available customers');
    }
  },

  /**
   * Get report configurations
   */
  getReportConfigurations: async (
    organizationId: number,
    activeOnly: boolean = true
  ): Promise<ReportConfiguration[]> => {
    try {
      const response = await api.get(`/service-analytics/organizations/${organizationId}/analytics/report-configurations`, {
        params: { active_only: activeOnly }
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get report configurations');
    }
  },

  /**
   * Create a new report configuration (requires manager permissions)
   */
  createReportConfiguration: async (
    organizationId: number,
    config: Omit<ReportConfiguration, 'id' | 'organization_id' | 'created_at' | 'updated_at'>
  ): Promise<ReportConfiguration> => {
    try {
      const response = await api.post(`/service-analytics/organizations/${organizationId}/analytics/report-configurations`, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to create report configuration');
    }
  },

  /**
   * Export analytics data
   */
  exportAnalyticsData: async (
    organizationId: number,
    exportRequest: {
      format: string;
      metric_types: MetricType[];
      filters: AnalyticsRequest;
      include_raw_data?: boolean;
    }
  ): Promise<Blob> => {
    try {
      const response = await api.post(
        `/service-analytics/organizations/${organizationId}/analytics/export`,
        exportRequest,
        {
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to export analytics data');
    }
  }
};