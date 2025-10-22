// frontend/src/services/__tests__/aiAgentService.test.ts

import { jest } from '@jest/globals';
import aiAgentService from '../aiAgentService';
import api from '../../lib/api';

jest.mock('../../lib/api');
const mockApi = api as jest.Mocked<typeof api>;

describe('aiAgentService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApi.get.mockResolvedValue({ data: {} });
    mockApi.post.mockResolvedValue({ data: {} });
    mockApi.put.mockResolvedValue({ data: {} });
    mockApi.delete.mockResolvedValue({ data: {} });
  });

  describe('Agent Management', () => {
    it('should get all agents', async () => {
      const mockAgents = [
        { id: 1, name: 'Sales Agent', type: 'sales', status: 'active' },
        { id: 2, name: 'Support Agent', type: 'customer_service', status: 'active' },
      ];
      mockApi.get.mockResolvedValue({ data: mockAgents });

      const result = await aiAgentService.getAgents();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents');
      expect(result).toEqual(mockAgents);
    });

    it('should get single agent', async () => {
      const mockAgent = { id: 1, name: 'Sales Agent', type: 'sales' };
      mockApi.get.mockResolvedValue({ data: mockAgent });

      const result = await aiAgentService.getAgent(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1');
      expect(result).toEqual(mockAgent);
    });

    it('should create agent', async () => {
      const newAgent = {
        name: 'Analytics Agent',
        type: 'analytics' as const,
        description: 'Provides analytics insights',
        status: 'active' as const,
        capabilities: ['data_analysis', 'reporting'],
        config: {},
      };
      mockApi.post.mockResolvedValue({ data: { id: 1, ...newAgent } });

      const result = await aiAgentService.createAgent(newAgent);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents', newAgent);
      expect(result.id).toBe(1);
    });

    it('should update agent', async () => {
      const updates = { name: 'Updated Agent', status: 'inactive' as const };
      mockApi.put.mockResolvedValue({ data: { id: 1, ...updates } });

      const result = await aiAgentService.updateAgent(1, updates);

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/ai-agents/1', updates);
      expect(result).toEqual({ id: 1, ...updates });
    });

    it('should delete agent', async () => {
      await aiAgentService.deleteAgent(1);

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/ai-agents/1');
    });

    it('should activate agent', async () => {
      mockApi.post.mockResolvedValue({ data: { id: 1, status: 'active' } });

      const result = await aiAgentService.activateAgent(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/activate');
      expect(result.status).toBe('active');
    });

    it('should deactivate agent', async () => {
      mockApi.post.mockResolvedValue({ data: { id: 1, status: 'inactive' } });

      const result = await aiAgentService.deactivateAgent(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/deactivate');
      expect(result.status).toBe('inactive');
    });
  });

  describe('Agent Tasks', () => {
    it('should execute task', async () => {
      const taskInput = { customer_id: 123, query: 'sales forecast' };
      mockApi.post.mockResolvedValue({
        data: { id: 1, agent_id: 1, task_type: 'forecast', input: taskInput, status: 'pending' },
      });

      const result = await aiAgentService.executeTask(1, 'forecast', taskInput);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/tasks', {
        task_type: 'forecast',
        input: taskInput,
      });
      expect(result.status).toBe('pending');
    });

    it('should get task', async () => {
      const mockTask = { id: 1, agent_id: 1, status: 'completed' };
      mockApi.get.mockResolvedValue({ data: mockTask });

      const result = await aiAgentService.getTask(1, 1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1/tasks/1');
      expect(result).toEqual(mockTask);
    });

    it('should get tasks with filters', async () => {
      const mockTasks = [{ id: 1 }, { id: 2 }];
      mockApi.get.mockResolvedValue({ data: mockTasks });

      const result = await aiAgentService.getTasks(1, { status: 'completed', limit: 10 });

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1/tasks', {
        params: { status: 'completed', limit: 10 },
      });
      expect(result).toEqual(mockTasks);
    });

    it('should cancel task', async () => {
      await aiAgentService.cancelTask(1, 2);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/tasks/2/cancel');
    });
  });

  describe('Agent Recommendations', () => {
    it('should get recommendations', async () => {
      const mockRecommendations = [
        { id: 1, type: 'product', confidence: 0.85, priority: 'high' },
      ];
      mockApi.get.mockResolvedValue({ data: mockRecommendations });

      const result = await aiAgentService.getRecommendations(1, { type: 'product' });

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1/recommendations', {
        params: { type: 'product' },
      });
      expect(result).toEqual(mockRecommendations);
    });

    it('should accept recommendation', async () => {
      await aiAgentService.acceptRecommendation(1, 2);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/recommendations/2/accept');
    });

    it('should reject recommendation with reason', async () => {
      await aiAgentService.rejectRecommendation(1, 2, 'Not applicable');

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/1/recommendations/2/reject', {
        reason: 'Not applicable',
      });
    });
  });

  describe('Agent Metrics', () => {
    it('should get agent metrics', async () => {
      const mockMetrics = {
        agent_id: 1,
        total_tasks: 100,
        successful_tasks: 95,
        failed_tasks: 5,
        average_response_time: 1.5,
        uptime_percentage: 99.9,
        last_active: '2024-01-15T10:00:00Z',
      };
      mockApi.get.mockResolvedValue({ data: mockMetrics });

      const result = await aiAgentService.getAgentMetrics(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1/metrics');
      expect(result).toEqual(mockMetrics);
    });

    it('should get all agent metrics', async () => {
      const mockMetrics = { 1: {}, 2: {} };
      mockApi.get.mockResolvedValue({ data: mockMetrics });

      const result = await aiAgentService.getAllAgentMetrics();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/metrics');
      expect(result).toEqual(mockMetrics);
    });

    it('should get agent performance', async () => {
      const mockPerformance = { data: 'performance_data' };
      mockApi.get.mockResolvedValue({ data: mockPerformance });

      const result = await aiAgentService.getAgentPerformance(1, '30d');

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/1/performance', {
        params: { time_range: '30d' },
      });
      expect(result).toEqual(mockPerformance);
    });
  });

  describe('Chatbot Agent', () => {
    it('should send chatbot message', async () => {
      mockApi.post.mockResolvedValue({
        data: { response: 'Hello!', intent: 'greeting', confidence: 0.95 },
      });

      const result = await aiAgentService.sendChatbotMessage('Hi there', { user_id: 123 });

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/chatbot/message', {
        message: 'Hi there',
        context: { user_id: 123 },
      });
      expect(result.response).toBe('Hello!');
    });

    it('should get chatbot history', async () => {
      const mockHistory = [{ message: 'Hi', response: 'Hello' }];
      mockApi.get.mockResolvedValue({ data: mockHistory });

      const result = await aiAgentService.getChatbotHistory('session-123', 20);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/chatbot/history', {
        params: { session_id: 'session-123', limit: 20 },
      });
      expect(result).toEqual(mockHistory);
    });

    it('should train chatbot', async () => {
      const trainingData = [
        { input: 'What is your name?', output: 'I am an AI assistant' },
      ];
      mockApi.post.mockResolvedValue({ data: { success: true, message: 'Training complete' } });

      const result = await aiAgentService.trainChatbot(trainingData);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/chatbot/train', {
        training_data: trainingData,
      });
      expect(result.success).toBe(true);
    });
  });

  describe('Sales Agent', () => {
    it('should get sales insights', async () => {
      const mockInsights = {
        opportunities: [{ id: 1 }],
        forecasts: [{ period: 'Q1' }],
        recommendations: [{ type: 'action' }],
      };
      mockApi.get.mockResolvedValue({ data: mockInsights });

      const result = await aiAgentService.getSalesInsights();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/sales/insights');
      expect(result).toEqual(mockInsights);
    });

    it('should predict sales conversion', async () => {
      mockApi.get.mockResolvedValue({
        data: {
          probability: 0.75,
          factors: [{ factor: 'engagement', impact: 0.8 }],
          recommended_actions: ['Follow up within 24 hours'],
        },
      });

      const result = await aiAgentService.predictSalesConversion(123);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/sales/predict/123');
      expect(result.probability).toBe(0.75);
    });

    it('should get sales forecast', async () => {
      mockApi.get.mockResolvedValue({
        data: {
          predicted_revenue: 100000,
          confidence_interval: { lower: 90000, upper: 110000 },
          contributing_factors: [],
        },
      });

      const result = await aiAgentService.getSalesForecast('Q2');

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/sales/forecast', {
        params: { period: 'Q2' },
      });
      expect(result.predicted_revenue).toBe(100000);
    });
  });

  describe('Analytics Agent', () => {
    it('should detect anomalies', async () => {
      mockApi.get.mockResolvedValue({
        data: {
          anomalies: [
            {
              timestamp: '2024-01-15T10:00:00Z',
              value: 100,
              expected_value: 50,
              severity: 'high',
              description: 'Unusual spike',
            },
          ],
        },
      });

      const result = await aiAgentService.getAnomalyDetection('revenue');

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/analytics/anomalies', {
        params: { data_type: 'revenue' },
      });
      expect(result.anomalies).toHaveLength(1);
    });

    it('should get predictive analytics', async () => {
      mockApi.get.mockResolvedValue({
        data: {
          predictions: [{ date: '2024-02-01', value: 1000, confidence: 0.9 }],
          trend: 'increasing',
          insights: ['Expected growth'],
        },
      });

      const result = await aiAgentService.getPredictiveAnalytics('sales', 30);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/analytics/predict', {
        params: { metric: 'sales', horizon: 30 },
      });
      expect(result.trend).toBe('increasing');
    });

    it('should get business insights', async () => {
      mockApi.get.mockResolvedValue({
        data: {
          key_insights: [
            {
              title: 'Revenue Growth',
              description: 'Revenue increased by 20%',
              impact: 'positive',
              action_items: ['Continue current strategy'],
            },
          ],
        },
      });

      const result = await aiAgentService.getBusinessInsights();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/analytics/insights');
      expect(result.key_insights).toHaveLength(1);
    });
  });

  describe('Automation Agent', () => {
    it('should create automation', async () => {
      const config = {
        name: 'Auto-assign leads',
        trigger: 'lead_created',
        conditions: [{ field: 'score', operator: '>', value: 80 }],
        actions: [{ type: 'assign', target: 'sales_team' }],
        enabled: true,
      };
      mockApi.post.mockResolvedValue({ data: { id: 1, ...config } });

      const result = await aiAgentService.createAutomation(config);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/ai-agents/automation/rules', config);
      expect(result.id).toBe(1);
    });

    it('should get automations', async () => {
      const mockAutomations = [{ id: 1, name: 'Auto-assign' }];
      mockApi.get.mockResolvedValue({ data: mockAutomations });

      const result = await aiAgentService.getAutomations();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/automation/rules');
      expect(result).toEqual(mockAutomations);
    });

    it('should update automation', async () => {
      const updates = { enabled: false };
      mockApi.put.mockResolvedValue({ data: { id: 1, ...updates } });

      const result = await aiAgentService.updateAutomation(1, updates);

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/ai-agents/automation/rules/1', updates);
      expect(result.enabled).toBe(false);
    });

    it('should delete automation', async () => {
      await aiAgentService.deleteAutomation(1);

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/ai-agents/automation/rules/1');
    });

    it('should get automation history', async () => {
      const mockHistory = [{ id: 1, executed_at: '2024-01-15T10:00:00Z' }];
      mockApi.get.mockResolvedValue({ data: mockHistory });

      const result = await aiAgentService.getAutomationHistory(100);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/ai-agents/automation/history', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockHistory);
    });
  });
});
