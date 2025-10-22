/**
 * A/B Testing Service
 * Service for managing A/B test experiments and variants
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AB_TESTING_API = `${API_BASE_URL}/api/v1/ab-testing`;

export enum ExperimentStatus {
  DRAFT = 'draft',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export enum VariantType {
  CONTROL = 'control',
  TREATMENT = 'treatment',
}

export interface Experiment {
  id: number;
  organization_id: number;
  experiment_name: string;
  description?: string;
  status: ExperimentStatus;
  traffic_split?: Record<string, number>;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface Variant {
  id: number;
  experiment_id: number;
  variant_name: string;
  variant_type: VariantType;
  model_id?: number;
  model_version?: string;
  traffic_percentage: number;
  model_config?: Record<string, any>;
  created_at: string;
}

export interface ExperimentCreate {
  experiment_name: string;
  description?: string;
  traffic_split?: Record<string, number>;
}

export interface VariantCreate {
  variant_name: string;
  variant_type: VariantType;
  model_id?: number;
  model_version?: string;
  traffic_percentage?: number;
  model_config?: Record<string, any>;
}

export interface Assignment {
  experiment_id: number;
  variant: Variant;
  assigned: boolean;
}

export interface ResultCreate {
  experiment_id: number;
  variant_id: number;
  metric_name: string;
  metric_value: number;
  user_id?: number;
  session_id?: string;
  metadata?: Record<string, any>;
}

export interface ExperimentResults {
  experiment_id: number;
  experiment_name: string;
  status: ExperimentStatus;
  start_date?: string;
  end_date?: string;
  variants: Record<string, VariantResults>;
}

export interface VariantResults {
  sample_size: number;
  metrics: Record<string, MetricStats>;
}

export interface MetricStats {
  count: number;
  mean: number;
  min: number;
  max: number;
  sum: number;
}

class ABTestingService {
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // ============================================================================
  // EXPERIMENT MANAGEMENT
  // ============================================================================

  async createExperiment(data: ExperimentCreate): Promise<Experiment> {
    const response = await axios.post<Experiment>(
      `${AB_TESTING_API}/experiments`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async listExperiments(
    status?: ExperimentStatus,
    skip: number = 0,
    limit: number = 100
  ): Promise<Experiment[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());

    const response = await axios.get<Experiment[]>(
      `${AB_TESTING_API}/experiments?${params.toString()}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getExperiment(experimentId: number): Promise<Experiment> {
    const response = await axios.get<Experiment>(
      `${AB_TESTING_API}/experiments/${experimentId}`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async updateExperiment(
    experimentId: number,
    updates: Partial<ExperimentCreate>
  ): Promise<Experiment> {
    const response = await axios.patch<Experiment>(
      `${AB_TESTING_API}/experiments/${experimentId}`,
      updates,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async startExperiment(experimentId: number): Promise<Experiment> {
    const response = await axios.post<Experiment>(
      `${AB_TESTING_API}/experiments/${experimentId}/start`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async pauseExperiment(experimentId: number): Promise<Experiment> {
    const response = await axios.post<Experiment>(
      `${AB_TESTING_API}/experiments/${experimentId}/pause`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async completeExperiment(experimentId: number): Promise<Experiment> {
    const response = await axios.post<Experiment>(
      `${AB_TESTING_API}/experiments/${experimentId}/complete`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // VARIANT MANAGEMENT
  // ============================================================================

  async createVariant(experimentId: number, data: VariantCreate): Promise<Variant> {
    const response = await axios.post<Variant>(
      `${AB_TESTING_API}/experiments/${experimentId}/variants`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getVariants(experimentId: number): Promise<Variant[]> {
    const response = await axios.get<Variant[]>(
      `${AB_TESTING_API}/experiments/${experimentId}/variants`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // ============================================================================
  // ASSIGNMENT AND TRACKING
  // ============================================================================

  async assignVariant(
    experimentId: number,
    userId?: number,
    sessionId?: string
  ): Promise<Assignment> {
    const response = await axios.post<Assignment>(
      `${AB_TESTING_API}/assign`,
      { experiment_id: experimentId, user_id: userId, session_id: sessionId },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async recordResult(data: ResultCreate): Promise<any> {
    const response = await axios.post(
      `${AB_TESTING_API}/results`,
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async getExperimentResults(experimentId: number): Promise<ExperimentResults> {
    const response = await axios.get<ExperimentResults>(
      `${AB_TESTING_API}/experiments/${experimentId}/results`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }
}

export default new ABTestingService();
