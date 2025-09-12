/**
 * Forecasting API Service
 */

import { apiClient } from './client';

export interface FinancialForecast {
  id: number;
  organization_id: number;
  forecast_name: string;
  forecast_type: string;
  forecast_method: string;
  base_period_start: string;
  base_period_end: string;
  forecast_start: string;
  forecast_end: string;
  frequency: string;
  model_parameters: any;
  business_drivers: any;
  historical_data: any;
  forecast_data: any;
  confidence_intervals?: any;
  accuracy_metrics?: any;
  last_validation_date?: string;
  validation_period_accuracy?: number;
  status: string;
  is_baseline: boolean;
  created_at: string;
  updated_at: string;
  created_by_id?: number;
  approved_by_id?: number;
  approved_at?: string;
}

export interface MLForecastModel {
  id: number;
  organization_id: number;
  model_name: string;
  model_type: string;
  target_variable: string;
  features: string[];
  hyperparameters: any;
  preprocessing_steps: any;
  training_period_start: string;
  training_period_end: string;
  training_data_size: number;
  training_accuracy?: number;
  validation_accuracy?: number;
  test_accuracy?: number;
  mae?: number;
  rmse?: number;
  mape?: number;
  feature_importance?: any;
  model_file_path?: string;
  model_version: string;
  is_active: boolean;
  is_production: boolean;
  trained_at: string;
  created_by_id?: number;
}

export interface MLPrediction {
  id: number;
  ml_model_id: number;
  organization_id: number;
  prediction_date: string;
  predicted_value: number;
  confidence_score?: number;
  lower_bound?: number;
  upper_bound?: number;
  input_features: any;
  actual_value?: number;
  prediction_error?: number;
  predicted_at: string;
}

export interface RiskAnalysis {
  id: number;
  organization_id: number;
  risk_category: string;
  risk_name: string;
  risk_description?: string;
  probability: number;
  impact_score: number;
  risk_score: number;
  potential_financial_impact?: number;
  key_indicators: any;
  threshold_values: any;
  current_indicator_values?: any;
  alert_level: string;
  is_active_alert: boolean;
  mitigation_strategies?: string;
  mitigation_status?: string;
  created_at: string;
  updated_at: string;
  last_assessed_at?: string;
  created_by_id?: number;
}

export interface AutomatedInsight {
  id: number;
  organization_id: number;
  insight_type: string;
  insight_category: string;
  title: string;
  description: string;
  data_sources: string[];
  analysis_method: string;
  confidence_score: number;
  importance_score: number;
  potential_impact?: string;
  recommended_actions?: string;
  supporting_metrics?: any;
  visualization_data?: any;
  status: string;
  user_feedback?: string;
  usefulness_rating?: number;
  generated_at: string;
  expires_at?: string;
  reviewed_by_id?: number;
  reviewed_at?: string;
}

export interface ForecastDashboard {
  active_forecasts: number;
  forecast_accuracy_avg: number;
  recent_predictions: any[];
  risk_alerts: any[];
  key_insights: any[];
  performance_metrics: any;
  trend_analysis: any;
}

// Request types
export interface CreateForecastRequest {
  forecast_name: string;
  forecast_type: string;
  forecast_method: string;
  base_period_start: string;
  base_period_end: string;
  forecast_start: string;
  forecast_end: string;
  frequency: string;
  model_parameters: any;
  business_drivers: any;
  historical_data: any;
}

export interface UpdateForecastRequest {
  forecast_name?: string;
  model_parameters?: any;
  business_drivers?: any;
  status?: string;
  is_baseline?: boolean;
}

export interface CreateMLModelRequest {
  model_name: string;
  model_type: string;
  target_variable: string;
  features: string[];
  hyperparameters: any;
  preprocessing_steps: any;
  training_period_start: string;
  training_period_end: string;
  training_data: any;
}

export interface PredictionRequest {
  model_id: number;
  prediction_date: string;
  input_features: any;
  include_confidence?: boolean;
}

export interface CreateRiskAnalysisRequest {
  risk_category: string;
  risk_name: string;
  risk_description?: string;
  probability: number;
  impact_score: number;
  potential_financial_impact?: number;
  key_indicators: any;
  threshold_values: any;
  mitigation_strategies?: string;
}

export interface UpdateInsightRequest {
  status?: string;
  user_feedback?: string;
  usefulness_rating?: number;
}

// Query parameters
export interface GetForecastsParams {
  skip?: number;
  limit?: number;
  forecast_type?: string;
  forecast_method?: string;
  status?: string;
  is_baseline?: boolean;
}

export interface GetMLModelsParams {
  skip?: number;
  limit?: number;
  model_type?: string;
  target_variable?: string;
  is_active?: boolean;
  is_production?: boolean;
}

export interface GetPredictionsParams {
  model_id?: number;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}

export interface GetRiskAnalysisParams {
  risk_category?: string;
  alert_level?: string;
  is_active_alert?: boolean;
  skip?: number;
  limit?: number;
}

export interface GetInsightsParams {
  insight_type?: string;
  insight_category?: string;
  status?: string;
  min_importance?: number;
  skip?: number;
  limit?: number;
}

class ForecastingApiService {
  private baseUrl = '/api/v1/forecasting';

  // Financial Forecasts
  async getForecasts(params?: GetForecastsParams): Promise<FinancialForecast[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/forecasts${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async getForecast(forecastId: number): Promise<FinancialForecast> {
    const response = await apiClient.get(`${this.baseUrl}/forecasts/${forecastId}`);
    return response.data;
  }

  async createForecast(data: CreateForecastRequest): Promise<FinancialForecast> {
    const response = await apiClient.post(`${this.baseUrl}/forecasts`, data);
    return response.data;
  }

  async updateForecast(forecastId: number, data: UpdateForecastRequest): Promise<FinancialForecast> {
    const response = await apiClient.put(`${this.baseUrl}/forecasts/${forecastId}`, data);
    return response.data;
  }

  async deleteForecast(forecastId: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/forecasts/${forecastId}`);
  }

  // Business Drivers
  async getBusinessDrivers(forecastId: number, params?: { driver_category?: string; is_active?: boolean }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/forecasts/${forecastId}/drivers${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createBusinessDriver(forecastId: number, data: any): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/forecasts/${forecastId}/drivers`, data);
    return response.data;
  }

  // ML Models
  async getMLModels(params?: GetMLModelsParams): Promise<MLForecastModel[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/ml-models${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createMLModel(data: CreateMLModelRequest): Promise<MLForecastModel> {
    const response = await apiClient.post(`${this.baseUrl}/ml-models`, data);
    return response.data;
  }

  // Predictions
  async getPredictions(params?: GetPredictionsParams): Promise<MLPrediction[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/predictions${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createPrediction(data: PredictionRequest): Promise<MLPrediction> {
    const response = await apiClient.post(`${this.baseUrl}/predictions`, data);
    return response.data;
  }

  // Risk Analysis
  async getRiskAnalyses(params?: GetRiskAnalysisParams): Promise<RiskAnalysis[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/risk-analysis${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createRiskAnalysis(data: CreateRiskAnalysisRequest): Promise<RiskAnalysis> {
    const response = await apiClient.post(`${this.baseUrl}/risk-analysis`, data);
    return response.data;
  }

  async updateRiskAnalysis(riskId: number, data: Partial<CreateRiskAnalysisRequest>): Promise<RiskAnalysis> {
    const response = await apiClient.put(`${this.baseUrl}/risk-analysis/${riskId}`, data);
    return response.data;
  }

  // Risk Events
  async createRiskEvent(data: any): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/risk-events`, data);
    return response.data;
  }

  // Automated Insights
  async getAutomatedInsights(params?: GetInsightsParams): Promise<AutomatedInsight[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/insights${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async generateInsights(dataSources: string[], analysisPeriodDays: number = 30): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/insights/generate`, null, {
      params: {
        data_sources: dataSources,
        analysis_period_days: analysisPeriodDays
      }
    });
    return response.data;
  }

  async updateInsight(insightId: number, data: UpdateInsightRequest): Promise<AutomatedInsight> {
    const response = await apiClient.put(`${this.baseUrl}/insights/${insightId}`, data);
    return response.data;
  }

  // Dashboard
  async getForecastDashboard(): Promise<ForecastDashboard> {
    const response = await apiClient.get(`${this.baseUrl}/dashboard`);
    return response.data;
  }

  // Advanced Analytics
  async createMultivariateForecast(data: any): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/multivariate-forecast`, data);
    return response.data;
  }

  async performSensitivityAnalysis(data: any): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/sensitivity-analysis`, data);
    return response.data;
  }

  async getEarlyWarningSignals(params?: { severity?: string; min_confidence?: number }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/early-warning-signals${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  // Forecast Versions
  async getForecastVersions(forecastId: number): Promise<any[]> {
    const response = await apiClient.get(`${this.baseUrl}/forecasts/${forecastId}/versions`);
    return response.data;
  }

  async analyzeForecastAccuracy(forecastId: number, actualData: any): Promise<any> {
    const response = await apiClient.post(
      `${this.baseUrl}/forecasts/${forecastId}/accuracy-analysis`,
      actualData
    );
    return response.data;
  }
}

export const forecastingApi = new ForecastingApiService();