import api from '../lib/api';

export interface AutoMLRunCreate {
  run_name: string;
  task_type: string;
  target_column: string;
  feature_columns: string[];
  metric: string;
  framework?: string;
  time_budget?: number;
  max_trials?: number;
  dataset_config?: any;
  description?: string;
}

export interface AutoMLRun {
  id: number;
  organization_id: number;
  run_name: string;
  task_type: string;
  framework: string;
  status: string;
  progress: number;
  current_trial: number;
  max_trials: number;
  best_model_name: string | null;
  best_score: number | null;
  target_column: string;
  feature_columns: string[];
  metric: string;
  time_budget: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface AutoMLDashboard {
  total_runs: number;
  completed_runs: number;
  running_runs: number;
  recent_runs: Array<{
    id: number;
    run_name: string;
    task_type: string;
    status: string;
    best_score: number | null;
    created_at: string;
  }>;
}

export interface AutoMLModelCandidate {
  id: number;
  trial_number: number;
  model_name: string;
  algorithm: string;
  score: number;
  training_time: number;
  evaluation_metrics: any;
  feature_importance: any;
  created_at: string;
}

const automlService = {
  // Dashboard
  getDashboard: async (): Promise<AutoMLDashboard> => {
    const response = await api.get('/automl/dashboard');
    return response.data;
  },

  // AutoML Runs
  createRun: async (data: AutoMLRunCreate): Promise<AutoMLRun> => {
    const response = await api.post('/automl/runs', data);
    return response.data;
  },

  getRuns: async (params?: {
    status?: string;
    task_type?: string;
  }): Promise<AutoMLRun[]> => {
    const response = await api.get('/automl/runs', { params });
    return response.data;
  },

  getRun: async (runId: number): Promise<AutoMLRun> => {
    const response = await api.get(`/automl/runs/${runId}`);
    return response.data;
  },

  getLeaderboard: async (
    runId: number,
    topN: number = 10
  ): Promise<AutoMLModelCandidate[]> => {
    const response = await api.get(`/automl/runs/${runId}/leaderboard`, {
      params: { top_n: topN },
    });
    return response.data;
  },

  cancelRun: async (runId: number): Promise<{ message: string; run_id: number; status: string }> => {
    const response = await api.post(`/automl/runs/${runId}/cancel`);
    return response.data;
  },
};

export default automlService;
