/**
 * AI Service for frontend
 * Handles chatbot, intent classification, business advice, and AI analytics
 */

import axios from 'axios';
import { getApiUrl } from '../utils/config';

const API_BASE_URL = getApiUrl();

// Types
export interface ChatMessage {
  message: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  intent?: string;
  confidence?: number;
  actions?: Array<{
    type: string;
    label: string;
    data: any;
  }>;
  suggestions?: string[];
}

export interface IntentClassificationRequest {
  message: string;
}

export interface IntentClassificationResponse {
  intent: string;
  confidence: number;
  entities: Record<string, any>;
}

export interface BusinessAdviceRequest {
  category: 'inventory' | 'cash_flow' | 'sales' | 'customer_retention';
  context?: Record<string, any>;
}

export interface BusinessAdviceResponse {
  category: string;
  recommendations: Array<{
    title: string;
    description: string;
    priority: string;
    actionable_steps: string[];
  }>;
}

export interface AIModel {
  id: number;
  model_name: string;
  model_type: string;
  status: string;
  accuracy_score?: number;
  prediction_count: number;
}

export interface PredictionRequest {
  model_id: number;
  input_data: Record<string, any>;
  prediction_context?: string;
  business_entity_type?: string;
  business_entity_id?: number;
}

export interface PredictionResponse {
  prediction_id: string;
  prediction_output: Record<string, any>;
  confidence_score?: number;
}

export interface AIAnalyticsDashboard {
  total_models: number;
  active_models: number;
  models_in_training: number;
  total_predictions_today: number;
  total_predictions_week: number;
  total_predictions_month: number;
  average_model_accuracy?: number;
  active_anomalies: number;
  critical_anomalies: number;
  active_insights: number;
  high_priority_insights: number;
  automation_workflows: number;
  active_automations: number;
}

export interface SmartInsight {
  category: string;
  priority: string;
  title: string;
  message: string;
  action: string;
  action_label: string;
  generated_at: string;
}

class AIService {
  private getHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  // ============================================================================
  // CHATBOT SERVICES
  // ============================================================================

  /**
   * Process a chat message with the AI chatbot
   */
  async processChatMessage(request: ChatMessage): Promise<ChatResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/chatbot/process`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error processing chat message:', error);
      throw error;
    }
  }

  /**
   * Get contextual chat suggestions
   */
  async getChatSuggestions(): Promise<{ suggestions: string[] }> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/chatbot/suggestions`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting chat suggestions:', error);
      throw error;
    }
  }

  /**
   * Get business insights powered by AI
   */
  async getBusinessInsights(): Promise<{ insights: SmartInsight[]; recommendations: string[] }> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/chatbot/business-insights`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting business insights:', error);
      throw error;
    }
  }

  // ============================================================================
  // AI AGENT SERVICES
  // ============================================================================

  /**
   * Classify user intent from a message
   */
  async classifyIntent(request: IntentClassificationRequest): Promise<IntentClassificationResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/ai/intent/classify`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error classifying intent:', error);
      throw error;
    }
  }

  /**
   * Get business advice for a specific category
   */
  async getBusinessAdvice(request: BusinessAdviceRequest): Promise<BusinessAdviceResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/ai/advice`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting business advice:', error);
      throw error;
    }
  }

  /**
   * Get available business advice categories
   */
  async getAdviceCategories(): Promise<{ categories: Array<{ id: string; name: string; description: string }> }> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/ai/advice/categories`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting advice categories:', error);
      throw error;
    }
  }

  /**
   * Get navigation suggestions
   */
  async getNavigationSuggestions(query?: string): Promise<{ suggestions: Array<{ path: string; label: string; category: string }> }> {
    try {
      const params = query ? { query } : {};
      const response = await axios.get(
        `${API_BASE_URL}/ai/navigation/suggestions`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting navigation suggestions:', error);
      throw error;
    }
  }

  /**
   * Get quick actions based on context
   */
  async getQuickActions(context?: string): Promise<{ quick_actions: Array<any> }> {
    try {
      const params = context ? { context } : {};
      const response = await axios.get(
        `${API_BASE_URL}/ai/navigation/quickactions`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting quick actions:', error);
      throw error;
    }
  }

  /**
   * Get smart insights
   */
  async getSmartInsights(category?: string): Promise<{ insights: SmartInsight[] }> {
    try {
      const params = category ? { category } : {};
      const response = await axios.get(
        `${API_BASE_URL}/ai/insights/smart`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting smart insights:', error);
      throw error;
    }
  }

  /**
   * Get personalized recommendations
   */
  async getRecommendations(context?: string): Promise<{ recommendations: string[] }> {
    try {
      const params = context ? { context } : {};
      const response = await axios.get(
        `${API_BASE_URL}/ai/insights/recommendations`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting recommendations:', error);
      throw error;
    }
  }

  /**
   * Get chatbot configuration
   */
  async getChatbotConfig(): Promise<any> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/ai/chatbot/config`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting chatbot config:', error);
      throw error;
    }
  }

  // ============================================================================
  // AI ANALYTICS SERVICES
  // ============================================================================

  /**
   * Get AI analytics dashboard data
   */
  async getAIAnalyticsDashboard(): Promise<AIAnalyticsDashboard> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/dashboard`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting AI analytics dashboard:', error);
      throw error;
    }
  }

  /**
   * Get AI models
   */
  async getAIModels(status?: string, model_type?: string): Promise<AIModel[]> {
    try {
      const params: any = {};
      if (status) params.status = status;
      if (model_type) params.model_type = model_type;
      
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/models`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting AI models:', error);
      throw error;
    }
  }

  /**
   * Get a specific AI model
   */
  async getAIModel(modelId: number): Promise<AIModel> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/models/${modelId}`,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting AI model:', error);
      throw error;
    }
  }

  /**
   * Make a prediction using an AI model
   */
  async makePrediction(request: PredictionRequest): Promise<PredictionResponse> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/ai-analytics/predict`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Error making prediction:', error);
      throw error;
    }
  }

  /**
   * Get prediction results
   */
  async getPredictionResults(modelId?: number, limit: number = 100): Promise<PredictionResponse[]> {
    try {
      const params: any = { limit };
      if (modelId) params.model_id = modelId;
      
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/predictions`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting prediction results:', error);
      throw error;
    }
  }

  /**
   * Detect anomalies
   */
  async detectAnomalies(dataSource: string, timeRangeHours: number = 24): Promise<any[]> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/ai-analytics/anomalies/detect`,
        null,
        {
          headers: this.getHeaders(),
          params: {
            data_source: dataSource,
            time_range_hours: timeRangeHours
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      throw error;
    }
  }

  /**
   * Get active anomalies
   */
  async getActiveAnomalies(severity?: string): Promise<any[]> {
    try {
      const params = severity ? { severity } : {};
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/anomalies`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting active anomalies:', error);
      throw error;
    }
  }

  /**
   * Generate AI insights
   */
  async generateInsights(categories?: string[]): Promise<any[]> {
    try {
      const params = categories ? { categories: categories.join(',') } : {};
      const response = await axios.post(
        `${API_BASE_URL}/ai-analytics/insights/generate`,
        null,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error generating insights:', error);
      throw error;
    }
  }

  /**
   * Get active AI insights
   */
  async getActiveInsights(priority?: string, category?: string): Promise<any[]> {
    try {
      const params: any = {};
      if (priority) params.priority = priority;
      if (category) params.category = category;
      
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/insights`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting active insights:', error);
      throw error;
    }
  }

  /**
   * Get automation workflows
   */
  async getAutomationWorkflows(workflowType?: string, isActive?: boolean): Promise<any[]> {
    try {
      const params: any = {};
      if (workflowType) params.workflow_type = workflowType;
      if (isActive !== undefined) params.is_active = isActive;
      
      const response = await axios.get(
        `${API_BASE_URL}/ai-analytics/workflows`,
        { headers: this.getHeaders(), params }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting automation workflows:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const aiService = new AIService();
export default aiService;
