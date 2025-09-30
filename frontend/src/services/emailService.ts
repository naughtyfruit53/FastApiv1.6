// frontend/src/services/emailService.ts
import { api } from '../lib/api';

export interface SnappyMailConfig {
  imap_host: string;
  imap_port: number;
  smtp_host: string;
  smtp_port: number;
  use_ssl: boolean;
  email: string;
}

// Legacy SnappyMail functions
export const getSnappyMailConfig = async (userId: number): Promise<SnappyMailConfig | null> => {
  try {
    const response = await api.get(`/mail/config/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch SnappyMail config:', error);
    return null;
  }
};

export const getSnappyMailUrl = async (userId: number): Promise<string> => {
  const config = await getSnappyMailConfig(userId);
  const fallbackUrl = process.env.NEXT_PUBLIC_SNAPPYMAIL_URL || 'http://localhost:8888';
  if (config) {
    // Prefill login with user's email for easy access (user enters password in SnappyMail)
    return `${fallbackUrl}/?login=${encodeURIComponent(config.email)}`;
  }
  return fallbackUrl;
};

// Email Module Types
export interface EmailAddress {
  name?: string;
  email: string;
}

export interface EmailAttachment {
  id: number;
  filename: string;
  original_filename: string;
  content_type?: string;
  size_bytes?: number;
  is_inline: boolean;
  is_safe?: boolean;
  is_quarantined: boolean;
  download_count: number;
  last_downloaded_at?: string;
  created_at: string;
}

export interface Email {
  id: number;
  message_id: string;
  subject: string;
  from_address: string;
  from_name?: string;
  reply_to?: string;
  to_addresses: EmailAddress[];
  cc_addresses?: EmailAddress[];
  bcc_addresses?: EmailAddress[];
  body_text?: string;
  body_html?: string;
  status: 'unread' | 'read' | 'archived' | 'deleted' | 'flagged';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_flagged: boolean;
  is_important: boolean;
  has_attachments: boolean;
  sent_at: string;
  received_at: string;
  folder?: string;
  labels?: string[];
  customer_id?: number;
  vendor_id?: number;
  thread_id?: number;
  size_bytes?: number;
  created_at: string;
  updated_at?: string;
  attachments?: EmailAttachment[];
}

export interface EmailThread {
  id: number;
  thread_id: string;
  subject: string;
  original_subject: string;
  participants: string[];
  primary_participants: string[];
  message_count: number;
  unread_count: number;
  has_attachments: boolean;
  status: 'unread' | 'read' | 'archived' | 'deleted' | 'flagged';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  is_flagged: boolean;
  is_important: boolean;
  first_message_at: string;
  last_message_at: string;
  last_activity_at: string;
  customer_id?: number;
  vendor_id?: number;
  folder?: string;
  labels?: string[];
  organization_id: number;
  account_id: number;
  created_at: string;
  updated_at?: string;
}

export interface MailAccount {
  id: number;
  name: string;
  email_address: string;
  display_name?: string;
  account_type: 'imap' | 'gmail_api' | 'outlook_api';
  provider?: string;
  oauth_token_id?: number;
  sync_enabled: boolean;
  sync_frequency_minutes: number;
  sync_folders?: string[];
  is_active: boolean;
  sync_status: string;
  last_sync_at?: string;
  last_sync_error?: string;
  total_messages_synced: number;
  organization_id: number;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface ComposeEmail {
  to: EmailAddress[];
  cc?: EmailAddress[];
  bcc?: EmailAddress[];
  subject: string;
  body_text?: string;
  body_html?: string;
  reply_to_id?: number;
  forward_from_id?: number;
  attachments?: File[];
  template_id?: number;
  template_data?: Record<string, any>;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  request_delivery_receipt?: boolean;
  request_read_receipt?: boolean;
}

export interface EmailListResponse {
  emails: Email[];
  total_count: number;
  offset: number;
  limit: number;
  has_more: boolean;
  folder: string;
}

// Email Service API
class EmailService {
  private baseUrl = '/api/v1/email';

  // Account Management
  async getMailAccounts(): Promise<MailAccount[]> {
    const response = await api.get(`${this.baseUrl}/accounts`);
    return response.data;
  }

  async getMailAccount(accountId: number): Promise<MailAccount> {
    const response = await api.get(`${this.baseUrl}/accounts/${accountId}`);
    return response.data;
  }

  async createMailAccount(accountData: Partial<MailAccount>): Promise<MailAccount> {
    const response = await api.post(`${this.baseUrl}/accounts`, accountData);
    return response.data;
  }

  async updateMailAccount(accountId: number, updates: Partial<MailAccount>): Promise<MailAccount> {
    const response = await api.put(`${this.baseUrl}/accounts/${accountId}`, updates);
    return response.data;
  }

  async deleteMailAccount(accountId: number): Promise<{ message: string }> {
    const response = await api.delete(`${this.baseUrl}/accounts/${accountId}`);
    return response.data;
  }

  // Email Operations
  async getEmails(
    accountId: number,
    folder: string = 'INBOX',
    limit: number = 50,
    offset: number = 0,
    statusFilter?: string
  ): Promise<EmailListResponse> {
    const params = new URLSearchParams({
      folder,
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (statusFilter) {
      params.append('status_filter', statusFilter);
    }
    
    const response = await api.get(`${this.baseUrl}/accounts/${accountId}/emails?${params}`);
    return response.data;
  }

  async getEmail(emailId: number, includeAttachments: boolean = true): Promise<Email> {
    const params = new URLSearchParams({
      include_attachments: includeAttachments.toString(),
    });
    
    const response = await api.get(`${this.baseUrl}/emails/${emailId}?${params}`);
    return response.data;
  }

  async updateEmailStatus(emailId: number, status: Email['status']): Promise<{ message: string; new_status: string }> {
    const response = await api.put(`${this.baseUrl}/emails/${emailId}/status`, { new_status: status });
    return response.data;
  }

  // Thread Operations
  async getEmailThreads(
    accountId?: number,
    statusFilter?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<EmailThread[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (accountId) {
      params.append('account_id', accountId.toString());
    }
    if (statusFilter) {
      params.append('status_filter', statusFilter);
    }
    
    const response = await api.get(`${this.baseUrl}/threads?${params}`);
    return response.data;
  }

  async getEmailThread(threadId: number): Promise<EmailThread> {
    const response = await api.get(`${this.baseUrl}/threads/${threadId}`);
    return response.data;
  }

  // Compose & Send
  async composeEmail(email: ComposeEmail, accountId: number): Promise<{ message: string; email_id: number }> {
    const formData = new FormData();
    
    // Add basic email data
    formData.append('to', JSON.stringify(email.to));
    if (email.cc) formData.append('cc', JSON.stringify(email.cc));
    if (email.bcc) formData.append('bcc', JSON.stringify(email.bcc));
    formData.append('subject', email.subject);
    if (email.body_text) formData.append('body_text', email.body_text);
    if (email.body_html) formData.append('body_html', email.body_html);
    if (email.reply_to_id) formData.append('reply_to_id', email.reply_to_id.toString());
    if (email.forward_from_id) formData.append('forward_from_id', email.forward_from_id.toString());
    if (email.template_id) formData.append('template_id', email.template_id.toString());
    if (email.template_data) formData.append('template_data', JSON.stringify(email.template_data));
    if (email.priority) formData.append('priority', email.priority);
    
    // Add attachments
    if (email.attachments) {
      email.attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });
    }

    const response = await api.post(`${this.baseUrl}/accounts/${accountId}/send`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Attachments
  async downloadAttachment(attachmentId: number): Promise<{ message: string; filename: string }> {
    const response = await api.get(`${this.baseUrl}/attachments/${attachmentId}/download`);
    return response.data;
  }

  // Sync Operations
  async triggerSync(accountId: number, fullSync: boolean = false, folder?: string): Promise<{ message: string; account_id: number }> {
    const response = await api.post(`${this.baseUrl}/accounts/${accountId}/sync`, {
      full_sync: fullSync,
      folder,
    });
    return response.data;
  }

  async getSyncStatus(accountId: number): Promise<any> {
    const response = await api.get(`${this.baseUrl}/accounts/${accountId}/status`);
    return response.data;
  }

  // Template Operations (for voucher integration)
  async getEmailTemplates(): Promise<any[]> {
    const response = await api.get('/api/v1/templates/email');
    return response.data;
  }

  async applyTemplate(templateId: number, data: Record<string, any>): Promise<{ subject: string; body_html: string }> {
    const response = await api.post(`/api/v1/templates/email/${templateId}/render`, data);
    return response.data;
  }
}

export const emailService = new EmailService();