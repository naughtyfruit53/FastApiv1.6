/**
 * Financial Modeling API Service
 */

import { apiClient } from './client';

export interface FinancialModel {
  id: number;
  organization_id: number;
  model_name: string;
  model_type: string;
  model_version: string;
  analysis_start_date: string;
  analysis_end_date: string;
  forecast_years: number;
  assumptions: any;
  projections: any;
  valuation_results: any;
  is_approved: boolean;
  is_template: boolean;
  template_category?: string;
  created_at: string;
  updated_at: string;
  created_by_id?: number;
  approved_by_id?: number;
}

export interface DCFModel {
  id: number;
  financial_model_id: number;
  organization_id: number;
  cost_of_equity: number;
  cost_of_debt: number;
  tax_rate: number;
  debt_to_equity_ratio: number;
  wacc: number;
  terminal_growth_rate: number;
  terminal_value_multiple?: number;
  terminal_value: number;
  pv_of_fcf: number;
  pv_of_terminal_value: number;
  enterprise_value: number;
  equity_value: number;
  shares_outstanding?: number;
  value_per_share?: number;
  cash_flow_projections: any;
  calculated_at: string;
}

export interface ScenarioAnalysis {
  id: number;
  financial_model_id: number;
  organization_id: number;
  scenario_name: string;
  scenario_type: string;
  scenario_description?: string;
  assumption_changes: any;
  scenario_results: any;
  variance_from_base?: any;
  probability?: number;
  risk_adjusted_value?: number;
  created_at: string;
  created_by_id?: number;
}

export interface TradingComparable {
  id: number;
  organization_id: number;
  company_name: string;
  ticker_symbol?: string;
  industry: string;
  market_cap?: number;
  revenue_ttm?: number;
  ebitda_ttm?: number;
  net_income_ttm?: number;
  ev_revenue_multiple?: number;
  ev_ebitda_multiple?: number;
  pe_ratio?: number;
  additional_metrics?: any;
  data_source: string;
  as_of_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by_id?: number;
}

export interface ModelTemplate {
  id: number;
  template_name: string;
  template_category: string;
  industry?: string;
  description?: string;
  model_type: string;
  default_assumptions: any;
  projection_structure: any;
  is_active: boolean;
  is_public: boolean;
  complexity_level: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
  created_by_id?: number;
}

// Request/Create types
export interface CreateFinancialModelRequest {
  model_name: string;
  model_type: string;
  model_version?: string;
  analysis_start_date: string;
  analysis_end_date: string;
  forecast_years?: number;
  assumptions: any;
  template_category?: string;
}

export interface UpdateFinancialModelRequest {
  model_name?: string;
  assumptions?: any;
  projections?: any;
  is_approved?: boolean;
}

export interface CreateDCFModelRequest {
  financial_model_id: number;
  cost_of_equity: number;
  cost_of_debt: number;
  tax_rate: number;
  debt_to_equity_ratio: number;
  terminal_growth_rate: number;
  terminal_value_multiple?: number;
  shares_outstanding?: number;
}

export interface CreateScenarioRequest {
  financial_model_id: number;
  scenario_name: string;
  scenario_type: string;
  scenario_description?: string;
  assumption_changes: any;
  probability?: number;
}

export interface CreateTradingComparableRequest {
  company_name: string;
  ticker_symbol?: string;
  industry: string;
  market_cap?: number;
  revenue_ttm?: number;
  ebitda_ttm?: number;
  net_income_ttm?: number;
  ev_revenue_multiple?: number;
  ev_ebitda_multiple?: number;
  pe_ratio?: number;
  additional_metrics?: any;
  data_source?: string;
  as_of_date: string;
}

export interface ComprehensiveValuationRequest {
  company_name: string;
  dcf_assumptions?: any;
  industry_filter?: string;
  size_range?: any;
  dcf_weight?: number;
  trading_comps_weight?: number;
  transaction_comps_weight?: number;
}

// Query parameters
export interface GetModelsParams {
  skip?: number;
  limit?: number;
  model_type?: string;
  is_template?: boolean;
  is_approved?: boolean;
}

export interface GetComparablesParams {
  skip?: number;
  limit?: number;
  industry?: string;
  is_active?: boolean;
  lookback_years?: number;
}

export interface GetTemplatesParams {
  template_category?: string;
  industry?: string;
  complexity_level?: string;
  is_public?: boolean;
}

class FinancialModelingApiService {
  private baseUrl = '/api/v1/financial-modeling';

  // Financial Models
  async getFinancialModels(params?: GetModelsParams): Promise<FinancialModel[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/models${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async getFinancialModel(modelId: number): Promise<FinancialModel> {
    const response = await apiClient.get(`${this.baseUrl}/models/${modelId}`);
    return response.data;
  }

  async createFinancialModel(data: CreateFinancialModelRequest): Promise<FinancialModel> {
    const response = await apiClient.post(`${this.baseUrl}/models`, data);
    return response.data;
  }

  async updateFinancialModel(modelId: number, data: UpdateFinancialModelRequest): Promise<FinancialModel> {
    const response = await apiClient.put(`${this.baseUrl}/models/${modelId}`, data);
    return response.data;
  }

  async deleteFinancialModel(modelId: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/models/${modelId}`);
  }

  // DCF Models
  async getDCFModel(modelId: number): Promise<DCFModel> {
    const response = await apiClient.get(`${this.baseUrl}/models/${modelId}/dcf`);
    return response.data;
  }

  async createDCFModel(modelId: number, data: CreateDCFModelRequest): Promise<DCFModel> {
    const response = await apiClient.post(`${this.baseUrl}/models/${modelId}/dcf`, data);
    return response.data;
  }

  // Scenario Analysis
  async getScenarios(modelId: number): Promise<ScenarioAnalysis[]> {
    const response = await apiClient.get(`${this.baseUrl}/models/${modelId}/scenarios`);
    return response.data;
  }

  async createScenario(data: CreateScenarioRequest): Promise<ScenarioAnalysis> {
    const response = await apiClient.post(
      `${this.baseUrl}/models/${data.financial_model_id}/scenarios`, 
      data
    );
    return response.data;
  }

  // Trading Comparables
  async getTradingComparables(params?: GetComparablesParams): Promise<TradingComparable[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/trading-comparables${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createTradingComparable(data: CreateTradingComparableRequest): Promise<TradingComparable> {
    const response = await apiClient.post(`${this.baseUrl}/trading-comparables`, data);
    return response.data;
  }

  async updateTradingComparable(id: number, data: Partial<CreateTradingComparableRequest>): Promise<TradingComparable> {
    const response = await apiClient.put(`${this.baseUrl}/trading-comparables/${id}`, data);
    return response.data;
  }

  // Transaction Comparables
  async getTransactionComparables(params?: GetComparablesParams): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/transaction-comparables${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createTransactionComparable(data: any): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/transaction-comparables`, data);
    return response.data;
  }

  // Comprehensive Valuation
  async performComprehensiveValuation(data: ComprehensiveValuationRequest): Promise<any> {
    const response = await apiClient.post(`${this.baseUrl}/comprehensive-valuation`, data);
    return response.data;
  }

  // Ratio Analysis
  async getRatioAnalysis(asOfDate?: string): Promise<any> {
    const params = asOfDate ? `?as_of_date=${asOfDate}` : '';
    const response = await apiClient.get(`${this.baseUrl}/ratio-analysis${params}`);
    return response.data;
  }

  // Templates
  async getModelTemplates(params?: GetTemplatesParams): Promise<ModelTemplate[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/templates${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }

  async createModelFromTemplate(templateId: number, modelName: string): Promise<FinancialModel> {
    const response = await apiClient.post(
      `${this.baseUrl}/models/from-template/${templateId}?model_name=${encodeURIComponent(modelName)}`
    );
    return response.data;
  }

  // Audit Trail
  async getModelAuditTrail(modelId: number, params?: { skip?: number; limit?: number }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get(
      `${this.baseUrl}/models/${modelId}/audit-trail${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    );
    return response.data;
  }
}

export const financialModelingApi = new FinancialModelingApiService();