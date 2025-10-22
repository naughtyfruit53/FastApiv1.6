// frontend/src/services/__tests__/integrationService.test.ts

import { jest } from '@jest/globals';
import integrationService from '../integrationService';
import api from '../../lib/api';

jest.mock('../../lib/api');
const mockApi = api as jest.Mocked<typeof api>;

describe('integrationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApi.get.mockResolvedValue({ data: {} });
    mockApi.post.mockResolvedValue({ data: {} });
    mockApi.put.mockResolvedValue({ data: {} });
    mockApi.delete.mockResolvedValue({ data: {} });
  });

  describe('Slack Integration', () => {
    it('should get slack integrations', async () => {
      const mockIntegrations = [{ id: 1, name: 'Slack', type: 'slack' }];
      mockApi.get.mockResolvedValue({ data: mockIntegrations });

      const result = await integrationService.getSlackIntegrations();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/slack');
      expect(result).toEqual(mockIntegrations);
    });

    it('should create slack integration', async () => {
      const config = {
        workspace_url: 'https://workspace.slack.com',
        bot_token: 'xoxb-token',
        notifications_enabled: true,
      };
      const mockResponse = { id: 1, name: 'Slack Integration', type: 'slack', enabled: true, config };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await integrationService.createSlackIntegration(config);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/slack', {
        name: 'Slack Integration',
        type: 'slack',
        enabled: true,
        config,
      });
      expect(result).toEqual(mockResponse);
    });

    it('should update slack integration', async () => {
      const config = { bot_token: 'new-token' };
      mockApi.put.mockResolvedValue({ data: { id: 1, config } });

      await integrationService.updateSlackIntegration(1, config);

      expect(mockApi.put).toHaveBeenCalledWith('/api/v1/integrations/slack/1', { config });
    });

    it('should test slack connection', async () => {
      const mockResponse = { success: true, message: 'Connection successful' };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await integrationService.testSlackConnection(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/slack/1/test');
      expect(result).toEqual(mockResponse);
    });

    it('should send slack message', async () => {
      await integrationService.sendSlackMessage(1, 'Hello', '#general');

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/slack/1/send', {
        message: 'Hello',
        channel: '#general',
      });
    });
  });

  describe('WhatsApp Integration', () => {
    it('should get whatsapp integrations', async () => {
      const mockIntegrations = [{ id: 1, name: 'WhatsApp', type: 'whatsapp' }];
      mockApi.get.mockResolvedValue({ data: mockIntegrations });

      const result = await integrationService.getWhatsAppIntegrations();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/whatsapp');
      expect(result).toEqual(mockIntegrations);
    });

    it('should create whatsapp integration', async () => {
      const config = {
        account_sid: 'AC123',
        auth_token: 'token123',
        phone_number: '+1234567890',
        notifications_enabled: true,
      };
      mockApi.post.mockResolvedValue({ data: { id: 1, config } });

      await integrationService.createWhatsAppIntegration(config);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/whatsapp', {
        name: 'WhatsApp Integration',
        type: 'whatsapp',
        enabled: true,
        config,
      });
    });

    it('should send whatsapp message', async () => {
      await integrationService.sendWhatsAppMessage(1, '+1234567890', 'Hello');

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/whatsapp/1/send', {
        to: '+1234567890',
        message: 'Hello',
      });
    });
  });

  describe('Google Workspace Integration', () => {
    it('should get google workspace integrations', async () => {
      const mockIntegrations = [{ id: 1, name: 'Google Workspace', type: 'google_workspace' }];
      mockApi.get.mockResolvedValue({ data: mockIntegrations });

      const result = await integrationService.getGoogleWorkspaceIntegrations();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/google-workspace');
      expect(result).toEqual(mockIntegrations);
    });

    it('should authorize google workspace', async () => {
      const mockResponse = { auth_url: 'https://accounts.google.com/oauth' };
      mockApi.get.mockResolvedValue({ data: mockResponse });

      const result = await integrationService.authorizeGoogleWorkspace(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/google-workspace/1/authorize');
      expect(result).toEqual(mockResponse);
    });

    it('should handle google workspace callback', async () => {
      mockApi.post.mockResolvedValue({ data: { success: true } });

      await integrationService.handleGoogleWorkspaceCallback(1, 'auth-code');

      expect(mockApi.post).toHaveBeenCalledWith(
        '/api/v1/integrations/google-workspace/1/callback',
        { code: 'auth-code' }
      );
    });

    it('should sync google calendar', async () => {
      mockApi.post.mockResolvedValue({ data: { synced_events: 10 } });

      const result = await integrationService.syncGoogleCalendar(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/google-workspace/1/sync-calendar');
      expect(result).toEqual({ synced_events: 10 });
    });
  });

  describe('General Integration Management', () => {
    it('should get all integrations', async () => {
      const mockIntegrations = [
        { id: 1, type: 'slack' },
        { id: 2, type: 'whatsapp' },
      ];
      mockApi.get.mockResolvedValue({ data: mockIntegrations });

      const result = await integrationService.getAllIntegrations();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations');
      expect(result).toEqual(mockIntegrations);
    });

    it('should get single integration', async () => {
      const mockIntegration = { id: 1, name: 'Test Integration' };
      mockApi.get.mockResolvedValue({ data: mockIntegration });

      const result = await integrationService.getIntegration(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/1');
      expect(result).toEqual(mockIntegration);
    });

    it('should delete integration', async () => {
      await integrationService.deleteIntegration(1);

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/integrations/1');
    });

    it('should enable integration', async () => {
      mockApi.post.mockResolvedValue({ data: { id: 1, enabled: true } });

      await integrationService.enableIntegration(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/1/enable');
    });

    it('should disable integration', async () => {
      mockApi.post.mockResolvedValue({ data: { id: 1, enabled: false } });

      await integrationService.disableIntegration(1);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/1/disable');
    });

    it('should get integration status', async () => {
      const mockStatus = {
        integration_id: 1,
        status: 'active' as const,
        last_sync: '2024-01-15T10:00:00Z',
      };
      mockApi.get.mockResolvedValue({ data: mockStatus });

      const result = await integrationService.getIntegrationStatus(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/1/status');
      expect(result).toEqual(mockStatus);
    });

    it('should get integration logs', async () => {
      const mockLogs = [{ id: 1, message: 'Log entry' }];
      mockApi.get.mockResolvedValue({ data: mockLogs });

      const result = await integrationService.getIntegrationLogs(1, 100);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/1/logs', {
        params: { limit: 100 },
      });
      expect(result).toEqual(mockLogs);
    });
  });

  describe('Webhook Management', () => {
    it('should create webhook', async () => {
      const mockWebhook = { id: 1, url: 'https://example.com/webhook' };
      mockApi.post.mockResolvedValue({ data: mockWebhook });

      const result = await integrationService.createWebhook(1, 'https://example.com/webhook', ['event1']);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/1/webhooks', {
        url: 'https://example.com/webhook',
        events: ['event1'],
      });
      expect(result).toEqual(mockWebhook);
    });

    it('should get webhooks', async () => {
      const mockWebhooks = [{ id: 1 }, { id: 2 }];
      mockApi.get.mockResolvedValue({ data: mockWebhooks });

      const result = await integrationService.getWebhooks(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/integrations/1/webhooks');
      expect(result).toEqual(mockWebhooks);
    });

    it('should delete webhook', async () => {
      await integrationService.deleteWebhook(1, 2);

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/integrations/1/webhooks/2');
    });

    it('should test webhook', async () => {
      mockApi.post.mockResolvedValue({ data: { success: true } });

      const result = await integrationService.testWebhook(1, 2);

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/integrations/1/webhooks/2/test');
      expect(result).toEqual({ success: true });
    });
  });
});
