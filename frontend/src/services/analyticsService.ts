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

// ===========================================
// ML ANALYTICS INTERFACES AND SERVICE
// ===========================================

export interface MLAnalyticsDashboard {
  total_models: number;
  active_models: number;
  total_predictions: number;
  total_anomalies_detected: number;
  unresolved_anomalies: number;
  active_data_sources: number;
  model_performance_summary: Array<{
    model_id: number;
    model_name: string;
    model_type: string;
    accuracy_score?: number;
    prediction_count: number;
    is_active: boolean;
  }>;
  recent_anomalies: Array<{
    id: number;
    organization_id: number;
    anomaly_model_id: number;
    detected_at: string;
    severity: string;
    anomaly_score: number;
    affected_data: Record<string, any>;
    is_resolved: boolean;
    created_at: string;
  }>;
  prediction_trends: Record<string, any>;
}

export interface PredictiveModel {
  id: number;
  organization_id: number;
  model_name: string;
  model_type: string;
  description?: string;
  algorithm: string;
  version: string;
  accuracy_score?: number;
  precision_score?: number;
  recall_score?: number;
  f1_score?: number;
  mae?: number;
  rmse?: number;
  r2_score?: number;
  is_active: boolean;
  deployed_at?: string;
  prediction_count: number;
  last_prediction_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface AnomalyDetectionModel {
  id: number;
  organization_id: number;
  detection_name: string;
  anomaly_type: string;
  description?: string;
  algorithm: string;
  detection_config: Record<string, any>;
  threshold_config: Record<string, any>;
  monitored_metrics: string[];
  detection_frequency: string;
  is_active: boolean;
  last_detection_at?: string;
  anomalies_detected_count: number;
  created_at: string;
  updated_at?: string;
}

export interface AnomalyDetectionResult {
  id: number;
  organization_id: number;
  anomaly_model_id: number;
  detected_at: string;
  severity: string;
  anomaly_score: number;
  affected_data: Record<string, any>;
  expected_range?: Record<string, any>;
  actual_value?: Record<string, any>;
  context?: Record<string, any>;
  root_cause_analysis?: string;
  is_resolved: boolean;
  resolved_at?: string;
  resolution_notes?: string;
  is_false_positive: boolean;
  false_positive_reason?: string;
  created_at: string;
}

export interface ExternalDataSource {
  id: number;
  organization_id: number;
  source_name: string;
  source_type: string;
  description?: string;
  connection_config: Record<string, any>;
  data_schema?: Record<string, any>;
  field_mapping?: Record<string, any>;
  sync_frequency: string;
  is_active: boolean;
  sync_status: string;
  last_sync_at?: string;
  next_sync_at?: string;
  last_error?: string;
  total_records_synced: number;
  last_sync_duration_seconds?: number;
  created_at: string;
  updated_at?: string;
}

export interface PredictionRequest {
  model_id: number;
  input_data: Record<string, any>;
  context_metadata?: Record<string, any>;
}

export interface PredictionResponse {
  prediction_id: number;
  model_id: number;
  predicted_value: Record<string, any>;
  confidence_score?: number;
  prediction_timestamp: string;
}

export interface PredictionHistory {
  id: number;
  organization_id: number;
  model_id: number;
  prediction_timestamp: string;
  input_data: Record<string, any>;
  predicted_value: Record<string, any>;
  confidence_score?: number;
  actual_value?: Record<string, any>;
  prediction_error?: number;
  context_metadata?: Record<string, any>;
  created_at: string;
}

export const mlAnalyticsService = {
  // Dashboard
  getDashboard: async (): Promise<MLAnalyticsDashboard> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/dashboard");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get ML analytics dashboard");
    }
  },

  // Predictive Models
  getPredictiveModels: async (
    model_type?: string,
    is_active?: boolean
  ): Promise<PredictiveModel[]> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/models/predictive", {
        params: { model_type, is_active },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get predictive models");
    }
  },

  getPredictiveModel: async (modelId: number): Promise<PredictiveModel> => {
    try {
      const response = await api.get(`/api/v1/ml-analytics/models/predictive/${modelId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get predictive model");
    }
  },

  createPredictiveModel: async (modelData: any): Promise<PredictiveModel> => {
    try {
      const response = await api.post("/api/v1/ml-analytics/models/predictive", modelData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create predictive model");
    }
  },

  updatePredictiveModel: async (
    modelId: number,
    modelData: any
  ): Promise<PredictiveModel> => {
    try {
      const response = await api.put(
        `/api/v1/ml-analytics/models/predictive/${modelId}`,
        modelData
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update predictive model");
    }
  },

  deletePredictiveModel: async (modelId: number): Promise<void> => {
    try {
      await api.delete(`/api/v1/ml-analytics/models/predictive/${modelId}`);
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete predictive model");
    }
  },

  trainPredictiveModel: async (modelId: number, trainingParams?: any): Promise<any> => {
    try {
      const response = await api.post(
        `/api/v1/ml-analytics/models/predictive/${modelId}/train`,
        { model_id: modelId, training_parameters: trainingParams }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to train predictive model");
    }
  },

  deployPredictiveModel: async (modelId: number, deploymentConfig?: any): Promise<PredictiveModel> => {
    try {
      const response = await api.post(
        `/api/v1/ml-analytics/models/predictive/${modelId}/deploy`,
        { model_id: modelId, deployment_config: deploymentConfig }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to deploy predictive model");
    }
  },

  // Anomaly Detection
  getAnomalyDetectionModels: async (
    anomaly_type?: string,
    is_active?: boolean
  ): Promise<AnomalyDetectionModel[]> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/anomaly-detection/models", {
        params: { anomaly_type, is_active },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get anomaly detection models");
    }
  },

  createAnomalyDetectionModel: async (modelData: any): Promise<AnomalyDetectionModel> => {
    try {
      const response = await api.post("/api/v1/ml-analytics/anomaly-detection/models", modelData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create anomaly detection model");
    }
  },

  getAnomalyDetectionResults: async (
    model_id?: number,
    is_resolved?: boolean,
    severity?: string,
    limit?: number
  ): Promise<AnomalyDetectionResult[]> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/anomaly-detection/results", {
        params: { model_id, is_resolved, severity, limit },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get anomaly detection results");
    }
  },

  resolveAnomaly: async (
    anomalyId: number,
    resolutionData: {
      resolution_notes: string;
      is_false_positive: boolean;
      false_positive_reason?: string;
    }
  ): Promise<AnomalyDetectionResult> => {
    try {
      const response = await api.post(
        `/api/v1/ml-analytics/anomaly-detection/results/${anomalyId}/resolve`,
        resolutionData
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to resolve anomaly");
    }
  },

  // External Data Sources
  getExternalDataSources: async (
    source_type?: string,
    is_active?: boolean
  ): Promise<ExternalDataSource[]> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/data-sources", {
        params: { source_type, is_active },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get external data sources");
    }
  },

  createExternalDataSource: async (sourceData: any): Promise<ExternalDataSource> => {
    try {
      const response = await api.post("/api/v1/ml-analytics/data-sources", sourceData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create external data source");
    }
  },

  // Predictions
  makePrediction: async (
    predictionRequest: PredictionRequest
  ): Promise<PredictionResponse> => {
    try {
      const response = await api.post("/api/v1/ml-analytics/predictions", predictionRequest);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to make prediction");
    }
  },

  getPredictionHistory: async (
    model_id?: number,
    limit?: number
  ): Promise<PredictionHistory[]> => {
    try {
      const response = await api.get("/api/v1/ml-analytics/predictions/history", {
        params: { model_id, limit },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get prediction history");
    }
  },

  // Advanced Analytics
  performAdvancedAnalytics: async (analyticsRequest: {
    analysis_type: string;
    data_source: string;
    parameters: Record<string, any>;
    date_range?: Record<string, string>;
  }): Promise<any> => {
    try {
      const response = await api.post("/api/v1/ml-analytics/advanced-analytics", analyticsRequest);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to perform advanced analytics");
    }
  },
};
