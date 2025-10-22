// frontend/src/services/aiAgentService.ts
/**
 * AI Agent Service
 * Handles modular AI agents for various business functions
 */

import api from '../lib/api';

export interface AIAgent {
  id: number;
  name: string;
  type: 'customer_service' | 'sales' | 'analytics' | 'recommendation' | 'chatbot' | 'automation';
  description: string;
  status: 'active' | 'inactive' | 'training';
  capabilities: string[];
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AgentTask {
  id: number;
  agent_id: number;
  task_type: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface AgentMetrics {
  agent_id: number;
  total_tasks: number;
  successful_tasks: number;
  failed_tasks: number;
  average_response_time: number;
  accuracy_rate?: number;
  uptime_percentage: number;
  last_active: string;
}

export interface AgentRecommendation {
  id: number;
  agent_id: number;
  type: 'product' | 'action' | 'insight' | 'optimization';
  title: string;
  description: string;
  confidence: number;
  data: Record<string, any>;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
}

class AIAgentService {
  // ===========================================
  // AGENT MANAGEMENT
  // ===========================================
  
  async getAgents(): Promise<AIAgent[]> {
    const response = await api.get('/api/v1/ai-agents');
    return response.data;
  }

  async getAgent(id: number): Promise<AIAgent> {
    const response = await api.get(`/api/v1/ai-agents/${id}`);
    return response.data;
  }

  async createAgent(agent: Omit<AIAgent, 'id' | 'created_at' | 'updated_at'>): Promise<AIAgent> {
    const response = await api.post('/api/v1/ai-agents', agent);
    return response.data;
  }

  async updateAgent(id: number, updates: Partial<AIAgent>): Promise<AIAgent> {
    const response = await api.put(`/api/v1/ai-agents/${id}`, updates);
    return response.data;
  }

  async deleteAgent(id: number): Promise<void> {
    await api.delete(`/api/v1/ai-agents/${id}`);
  }

  async activateAgent(id: number): Promise<AIAgent> {
    const response = await api.post(`/api/v1/ai-agents/${id}/activate`);
    return response.data;
  }

  async deactivateAgent(id: number): Promise<AIAgent> {
    const response = await api.post(`/api/v1/ai-agents/${id}/deactivate`);
    return response.data;
  }

  // ===========================================
  // AGENT TASKS
  // ===========================================
  
  async executeTask(agentId: number, taskType: string, input: Record<string, any>): Promise<AgentTask> {
    const response = await api.post(`/api/v1/ai-agents/${agentId}/tasks`, {
      task_type: taskType,
      input,
    });
    return response.data;
  }

  async getTask(agentId: number, taskId: number): Promise<AgentTask> {
    const response = await api.get(`/api/v1/ai-agents/${agentId}/tasks/${taskId}`);
    return response.data;
  }

  async getTasks(agentId: number, params?: { status?: string; limit?: number }): Promise<AgentTask[]> {
    const response = await api.get(`/api/v1/ai-agents/${agentId}/tasks`, { params });
    return response.data;
  }

  async cancelTask(agentId: number, taskId: number): Promise<void> {
    await api.post(`/api/v1/ai-agents/${agentId}/tasks/${taskId}/cancel`);
  }

  // ===========================================
  // AGENT RECOMMENDATIONS
  // ===========================================
  
  async getRecommendations(agentId: number, filters?: {
    type?: string;
    priority?: string;
    limit?: number;
  }): Promise<AgentRecommendation[]> {
    const response = await api.get(`/api/v1/ai-agents/${agentId}/recommendations`, {
      params: filters,
    });
    return response.data;
  }

  async acceptRecommendation(agentId: number, recommendationId: number): Promise<void> {
    await api.post(`/api/v1/ai-agents/${agentId}/recommendations/${recommendationId}/accept`);
  }

  async rejectRecommendation(agentId: number, recommendationId: number, reason?: string): Promise<void> {
    await api.post(`/api/v1/ai-agents/${agentId}/recommendations/${recommendationId}/reject`, {
      reason,
    });
  }

  // ===========================================
  // AGENT METRICS & ANALYTICS
  // ===========================================
  
  async getAgentMetrics(agentId: number): Promise<AgentMetrics> {
    const response = await api.get(`/api/v1/ai-agents/${agentId}/metrics`);
    return response.data;
  }

  async getAllAgentMetrics(): Promise<Record<number, AgentMetrics>> {
    const response = await api.get('/api/v1/ai-agents/metrics');
    return response.data;
  }

  async getAgentPerformance(agentId: number, timeRange: string): Promise<any> {
    const response = await api.get(`/api/v1/ai-agents/${agentId}/performance`, {
      params: { time_range: timeRange },
    });
    return response.data;
  }

  // ===========================================
  // CHATBOT AGENT (Specific)
  // ===========================================
  
  async sendChatbotMessage(message: string, context?: Record<string, any>): Promise<{
    response: string;
    intent?: string;
    confidence?: number;
    suggestions?: string[];
  }> {
    const response = await api.post('/api/v1/ai-agents/chatbot/message', {
      message,
      context,
    });
    return response.data;
  }

  async getChatbotHistory(sessionId?: string, limit: number = 50): Promise<any[]> {
    const response = await api.get('/api/v1/ai-agents/chatbot/history', {
      params: { session_id: sessionId, limit },
    });
    return response.data;
  }

  async trainChatbot(trainingData: Array<{ input: string; output: string }>): Promise<{
    success: boolean;
    message: string;
  }> {
    const response = await api.post('/api/v1/ai-agents/chatbot/train', {
      training_data: trainingData,
    });
    return response.data;
  }

  // ===========================================
  // SALES AGENT (Specific)
  // ===========================================
  
  async getSalesInsights(): Promise<{
    opportunities: any[];
    forecasts: any[];
    recommendations: any[];
  }> {
    const response = await api.get('/api/v1/ai-agents/sales/insights');
    return response.data;
  }

  async predictSalesConversion(leadId: number): Promise<{
    probability: number;
    factors: Array<{ factor: string; impact: number }>;
    recommended_actions: string[];
  }> {
    const response = await api.get(`/api/v1/ai-agents/sales/predict/${leadId}`);
    return response.data;
  }

  async getSalesForecast(period: string): Promise<{
    predicted_revenue: number;
    confidence_interval: { lower: number; upper: number };
    contributing_factors: any[];
  }> {
    const response = await api.get('/api/v1/ai-agents/sales/forecast', {
      params: { period },
    });
    return response.data;
  }

  // ===========================================
  // ANALYTICS AGENT (Specific)
  // ===========================================
  
  async getAnomalyDetection(dataType: string): Promise<{
    anomalies: Array<{
      timestamp: string;
      value: number;
      expected_value: number;
      severity: 'low' | 'medium' | 'high';
      description: string;
    }>;
  }> {
    const response = await api.get('/api/v1/ai-agents/analytics/anomalies', {
      params: { data_type: dataType },
    });
    return response.data;
  }

  async getPredictiveAnalytics(metric: string, horizon: number): Promise<{
    predictions: Array<{ date: string; value: number; confidence: number }>;
    trend: 'increasing' | 'decreasing' | 'stable';
    insights: string[];
  }> {
    const response = await api.get('/api/v1/ai-agents/analytics/predict', {
      params: { metric, horizon },
    });
    return response.data;
  }

  async getBusinessInsights(): Promise<{
    key_insights: Array<{
      title: string;
      description: string;
      impact: 'positive' | 'negative' | 'neutral';
      action_items: string[];
    }>;
  }> {
    const response = await api.get('/api/v1/ai-agents/analytics/insights');
    return response.data;
  }

  // ===========================================
  // AUTOMATION AGENT (Specific)
  // ===========================================
  
  async createAutomation(config: {
    name: string;
    trigger: string;
    conditions: any[];
    actions: any[];
    enabled: boolean;
  }): Promise<any> {
    const response = await api.post('/api/v1/ai-agents/automation/rules', config);
    return response.data;
  }

  async getAutomations(): Promise<any[]> {
    const response = await api.get('/api/v1/ai-agents/automation/rules');
    return response.data;
  }

  async updateAutomation(id: number, updates: any): Promise<any> {
    const response = await api.put(`/api/v1/ai-agents/automation/rules/${id}`, updates);
    return response.data;
  }

  async deleteAutomation(id: number): Promise<void> {
    await api.delete(`/api/v1/ai-agents/automation/rules/${id}`);
  }

  async getAutomationHistory(limit: number = 50): Promise<any[]> {
    const response = await api.get('/api/v1/ai-agents/automation/history', {
      params: { limit },
    });
    return response.data;
  }
}

export const aiAgentService = new AIAgentService();
export default aiAgentService;
