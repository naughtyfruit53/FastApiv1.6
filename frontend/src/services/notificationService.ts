// src/services/notificationService.ts
// Service for managing notifications and templates in the Service CRM

import api from '../lib/api';

// Types for notification system
export interface NotificationTemplate {
  id: number;
  organization_id: number;
  name: string;
  description?: string;
  template_type: string;
  channel: string;
  subject?: string;
  body: string;
  html_body?: string;
  trigger_event?: string;
  trigger_conditions?: Record<string, any>;
  variables?: string[];
  is_active: boolean;
  created_by?: number;
  created_at: string;
  updated_at?: string;
}

export interface NotificationTemplateCreate {
  name: string;
  description?: string;
  template_type: string;
  channel: string;
  subject?: string;
  body: string;
  html_body?: string;
  trigger_event?: string;
  trigger_conditions?: Record<string, any>;
  variables?: string[];
  is_active?: boolean;
}

export interface NotificationTemplateUpdate {
  name?: string;
  description?: string;
  template_type?: string;
  channel?: string;
  subject?: string;
  body?: string;
  html_body?: string;
  trigger_event?: string;
  trigger_conditions?: Record<string, any>;
  variables?: string[];
  is_active?: boolean;
}

export interface NotificationLog {
  id: number;
  organization_id: number;
  template_id?: number;
  recipient_type: string;
  recipient_id?: number;
  recipient_identifier: string;
  channel: string;
  subject?: string;
  content: string;
  status: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
  clicked_at?: string;
  error_message?: string;
  retry_count: number;
  max_retries: number;
  trigger_event?: string;
  context_data?: Record<string, any>;
  created_by?: number;
  created_at: string;
  updated_at?: string;
}

export interface NotificationSendRequest {
  template_id?: number;
  recipient_type: string;
  recipient_id: number;
  channel: string;
  variables?: Record<string, any>;
  override_content?: string;
  override_subject?: string;
}

export interface BulkNotificationRequest {
  template_id?: number;
  subject?: string;
  content: string;
  channel: string;
  recipient_type: string;
  recipient_ids?: number[];
  segment_name?: string;
  variables?: Record<string, any>;
}

export interface NotificationSendResponse {
  notification_id: number;
  status: string;
  message: string;
}

export interface BulkNotificationResponse {
  total_recipients: number;
  successful_sends: number;
  failed_sends: number;
  notification_ids: number[];
  errors: string[];
}

export interface NotificationAnalytics {
  period_days: number;
  total_notifications: number;
  status_breakdown: Record<string, number>;
  channel_breakdown: Record<string, number>;
}

export interface TemplateTestData {
  variables?: Record<string, any>;
}

export interface TemplateTestResponse {
  template_id: number;
  template_name: string;
  channel: string;
  test_subject?: string;
  test_content: string;
  variables_used: Record<string, any>;
}

// Constants
export const NOTIFICATION_CHANNELS = ['email', 'sms', 'push', 'in_app'] as const;
export const TEMPLATE_TYPES = ['appointment_reminder', 'service_completion', 'follow_up', 'marketing', 'system'] as const;
export const RECIPIENT_TYPES = ['customer', 'user'] as const;
export const BULK_RECIPIENT_TYPES = ['customers', 'segment', 'users'] as const;
export const NOTIFICATION_STATUSES = ['pending', 'sent', 'delivered', 'failed', 'bounced'] as const;

export type NotificationChannel = typeof NOTIFICATION_CHANNELS[number];
export type TemplateType = typeof TEMPLATE_TYPES[number];
export type RecipientType = typeof RECIPIENT_TYPES[number];
export type BulkRecipientType = typeof BULK_RECIPIENT_TYPES[number];
export type NotificationStatus = typeof NOTIFICATION_STATUSES[number];

// Template Management API
export const getNotificationTemplates = async (params: {
  channel?: NotificationChannel;
  template_type?: TemplateType;
  is_active?: boolean;
  signal?: AbortSignal;
} = {}): Promise<NotificationTemplate[]> => {
  const { signal, ...queryParams } = params;
  const response = await api.get('/api/v1/notifications/templates', {
    params: queryParams,
    signal
  });
  return response.data;
};

export const getNotificationTemplate = async (
  templateId: number,
  signal?: AbortSignal
): Promise<NotificationTemplate> => {
  const response = await api.get(`/api/v1/notifications/templates/${templateId}`, { signal });
  return response.data;
};

export const createNotificationTemplate = async (
  templateData: NotificationTemplateCreate
): Promise<NotificationTemplate> => {
  const response = await api.post('/api/v1/notifications/templates', templateData);
  return response.data;
};

export const updateNotificationTemplate = async (
  templateId: number,
  updateData: NotificationTemplateUpdate
): Promise<NotificationTemplate> => {
  const response = await api.put(`/api/v1/notifications/templates/${templateId}`, updateData);
  return response.data;
};

export const deleteNotificationTemplate = async (templateId: number): Promise<void> => {
  await api.delete(`/api/v1/notifications/templates/${templateId}`);
};

// Notification Sending API
export const sendNotification = async (
  request: NotificationSendRequest
): Promise<NotificationSendResponse> => {
  const response = await api.post('/api/v1/notifications/send', request);
  return response.data;
};

export const sendBulkNotification = async (
  request: BulkNotificationRequest
): Promise<BulkNotificationResponse> => {
  const response = await api.post('/api/v1/notifications/send-bulk', request);
  return response.data;
};

// Notification Logs API
export const getNotificationLogs = async (params: {
  recipient_type?: string;
  status?: NotificationStatus;
  channel?: NotificationChannel;
  limit?: number;
  offset?: number;
  signal?: AbortSignal;
} = {}): Promise<NotificationLog[]> => {
  const { signal, ...queryParams } = params;
  const response = await api.get('/api/v1/notifications/logs', {
    params: queryParams,
    signal
  });
  return response.data;
};

export const getNotificationLog = async (
  logId: number,
  signal?: AbortSignal
): Promise<NotificationLog> => {
  const response = await api.get(`/api/v1/notifications/logs/${logId}`, { signal });
  return response.data;
};

// Analytics API
export const getNotificationAnalytics = async (
  days: number = 30,
  signal?: AbortSignal
): Promise<NotificationAnalytics> => {
  const response = await api.get('/api/v1/notifications/analytics/summary', {
    params: { days },
    signal
  });
  return response.data;
};

// Template Testing API
export const testNotificationTemplate = async (
  templateId: number,
  testData: TemplateTestData = {}
): Promise<TemplateTestResponse> => {
  const response = await api.post(`/api/v1/notifications/templates/${templateId}/test`, testData);
  return response.data;
};

// Utility functions
export const getChannelDisplayName = (channel: NotificationChannel): string => {
  const channelNames: Record<NotificationChannel, string> = {
    email: 'Email',
    sms: 'SMS',
    push: 'Push Notification',
    in_app: 'In-App'
  };
  return channelNames[channel] || channel;
};

export const getTemplateTypeDisplayName = (type: TemplateType): string => {
  const typeNames: Record<TemplateType, string> = {
    appointment_reminder: 'Appointment Reminder',
    service_completion: 'Service Completion',
    follow_up: 'Follow-up',
    marketing: 'Marketing',
    system: 'System'
  };
  return typeNames[type] || type;
};

export const getStatusDisplayName = (status: NotificationStatus): string => {
  const statusNames: Record<NotificationStatus, string> = {
    pending: 'Pending',
    sent: 'Sent',
    delivered: 'Delivered',
    failed: 'Failed',
    bounced: 'Bounced'
  };
  return statusNames[status] || status;
};

export const getStatusColor = (status: NotificationStatus): string => {
  const statusColors: Record<NotificationStatus, string> = {
    pending: 'text-yellow-600 bg-yellow-100',
    sent: 'text-blue-600 bg-blue-100',
    delivered: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
    bounced: 'text-orange-600 bg-orange-100'
  };
  return statusColors[status] || 'text-gray-600 bg-gray-100';
};

// React Query keys for caching
export const notificationQueryKeys = {
  all: ['notifications'] as const,
  templates: () => [...notificationQueryKeys.all, 'templates'] as const,
  templatesFiltered: (filters: Record<string, any>) => 
    [...notificationQueryKeys.templates(), filters] as const,
  template: (id: number) => [...notificationQueryKeys.templates(), id] as const,
  logs: () => [...notificationQueryKeys.all, 'logs'] as const,
  logsFiltered: (filters: Record<string, any>) => 
    [...notificationQueryKeys.logs(), filters] as const,
  log: (id: number) => [...notificationQueryKeys.logs(), id] as const,
  analytics: (days: number) => [...notificationQueryKeys.all, 'analytics', days] as const,
} as const;