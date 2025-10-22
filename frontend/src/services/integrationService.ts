// frontend/src/services/integrationService.ts
/**
 * Integration Service for External Services
 * Handles Slack, WhatsApp, Google Workspace, and other integrations
 */

import api from '../lib/api';

export interface IntegrationConfig {
  id?: number;
  name: string;
  type: 'slack' | 'whatsapp' | 'google_workspace' | 'custom';
  enabled: boolean;
  config: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface SlackConfig {
  workspace_url: string;
  bot_token: string;
  webhook_url?: string;
  channel?: string;
  notifications_enabled: boolean;
}

export interface WhatsAppConfig {
  account_sid: string;
  auth_token: string;
  phone_number: string;
  business_profile_id?: string;
  notifications_enabled: boolean;
}

export interface GoogleWorkspaceConfig {
  client_id: string;
  client_secret: string;
  redirect_uri: string;
  scopes: string[];
  calendar_sync: boolean;
  contacts_sync: boolean;
  drive_sync: boolean;
}

export interface IntegrationStatus {
  integration_id: number;
  status: 'active' | 'inactive' | 'error';
  last_sync?: string;
  error_message?: string;
  sync_count?: number;
}

class IntegrationService {
  // ===========================================
  // SLACK INTEGRATION
  // ===========================================
  
  async getSlackIntegrations(): Promise<IntegrationConfig[]> {
    const response = await api.get('/api/v1/integrations/slack');
    return response.data;
  }

  async createSlackIntegration(config: SlackConfig): Promise<IntegrationConfig> {
    const response = await api.post('/api/v1/integrations/slack', {
      name: 'Slack Integration',
      type: 'slack',
      enabled: true,
      config,
    });
    return response.data;
  }

  async updateSlackIntegration(id: number, config: Partial<SlackConfig>): Promise<IntegrationConfig> {
    const response = await api.put(`/api/v1/integrations/slack/${id}`, { config });
    return response.data;
  }

  async testSlackConnection(id: number): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/api/v1/integrations/slack/${id}/test`);
    return response.data;
  }

  async sendSlackMessage(id: number, message: string, channel?: string): Promise<void> {
    await api.post(`/api/v1/integrations/slack/${id}/send`, { message, channel });
  }

  // ===========================================
  // WHATSAPP INTEGRATION
  // ===========================================
  
  async getWhatsAppIntegrations(): Promise<IntegrationConfig[]> {
    const response = await api.get('/api/v1/integrations/whatsapp');
    return response.data;
  }

  async createWhatsAppIntegration(config: WhatsAppConfig): Promise<IntegrationConfig> {
    const response = await api.post('/api/v1/integrations/whatsapp', {
      name: 'WhatsApp Integration',
      type: 'whatsapp',
      enabled: true,
      config,
    });
    return response.data;
  }

  async updateWhatsAppIntegration(id: number, config: Partial<WhatsAppConfig>): Promise<IntegrationConfig> {
    const response = await api.put(`/api/v1/integrations/whatsapp/${id}`, { config });
    return response.data;
  }

  async testWhatsAppConnection(id: number): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/api/v1/integrations/whatsapp/${id}/test`);
    return response.data;
  }

  async sendWhatsAppMessage(id: number, to: string, message: string): Promise<void> {
    await api.post(`/api/v1/integrations/whatsapp/${id}/send`, { to, message });
  }

  // ===========================================
  // GOOGLE WORKSPACE INTEGRATION
  // ===========================================
  
  async getGoogleWorkspaceIntegrations(): Promise<IntegrationConfig[]> {
    const response = await api.get('/api/v1/integrations/google-workspace');
    return response.data;
  }

  async createGoogleWorkspaceIntegration(config: GoogleWorkspaceConfig): Promise<IntegrationConfig> {
    const response = await api.post('/api/v1/integrations/google-workspace', {
      name: 'Google Workspace Integration',
      type: 'google_workspace',
      enabled: true,
      config,
    });
    return response.data;
  }

  async updateGoogleWorkspaceIntegration(id: number, config: Partial<GoogleWorkspaceConfig>): Promise<IntegrationConfig> {
    const response = await api.put(`/api/v1/integrations/google-workspace/${id}`, { config });
    return response.data;
  }

  async authorizeGoogleWorkspace(id: number): Promise<{ auth_url: string }> {
    const response = await api.get(`/api/v1/integrations/google-workspace/${id}/authorize`);
    return response.data;
  }

  async handleGoogleWorkspaceCallback(id: number, code: string): Promise<{ success: boolean }> {
    const response = await api.post(`/api/v1/integrations/google-workspace/${id}/callback`, { code });
    return response.data;
  }

  async syncGoogleCalendar(id: number): Promise<{ synced_events: number }> {
    const response = await api.post(`/api/v1/integrations/google-workspace/${id}/sync-calendar`);
    return response.data;
  }

  async syncGoogleContacts(id: number): Promise<{ synced_contacts: number }> {
    const response = await api.post(`/api/v1/integrations/google-workspace/${id}/sync-contacts`);
    return response.data;
  }

  // ===========================================
  // GENERAL INTEGRATION MANAGEMENT
  // ===========================================
  
  async getAllIntegrations(): Promise<IntegrationConfig[]> {
    const response = await api.get('/api/v1/integrations');
    return response.data;
  }

  async getIntegration(id: number): Promise<IntegrationConfig> {
    const response = await api.get(`/api/v1/integrations/${id}`);
    return response.data;
  }

  async deleteIntegration(id: number): Promise<void> {
    await api.delete(`/api/v1/integrations/${id}`);
  }

  async enableIntegration(id: number): Promise<IntegrationConfig> {
    const response = await api.post(`/api/v1/integrations/${id}/enable`);
    return response.data;
  }

  async disableIntegration(id: number): Promise<IntegrationConfig> {
    const response = await api.post(`/api/v1/integrations/${id}/disable`);
    return response.data;
  }

  async getIntegrationStatus(id: number): Promise<IntegrationStatus> {
    const response = await api.get(`/api/v1/integrations/${id}/status`);
    return response.data;
  }

  async getIntegrationLogs(id: number, limit: number = 50): Promise<any[]> {
    const response = await api.get(`/api/v1/integrations/${id}/logs`, {
      params: { limit },
    });
    return response.data;
  }

  // ===========================================
  // WEBHOOK MANAGEMENT
  // ===========================================
  
  async createWebhook(integrationId: number, url: string, events: string[]): Promise<any> {
    const response = await api.post(`/api/v1/integrations/${integrationId}/webhooks`, {
      url,
      events,
    });
    return response.data;
  }

  async getWebhooks(integrationId: number): Promise<any[]> {
    const response = await api.get(`/api/v1/integrations/${integrationId}/webhooks`);
    return response.data;
  }

  async deleteWebhook(integrationId: number, webhookId: number): Promise<void> {
    await api.delete(`/api/v1/integrations/${integrationId}/webhooks/${webhookId}`);
  }

  async testWebhook(integrationId: number, webhookId: number): Promise<{ success: boolean }> {
    const response = await api.post(`/api/v1/integrations/${integrationId}/webhooks/${webhookId}/test`);
    return response.data;
  }
}

export const integrationService = new IntegrationService();
export default integrationService;
