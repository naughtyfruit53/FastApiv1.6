// frontend/src/services/emailService.ts
import api from "../lib/api";

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
  account_id?: number; // Added for original account lookup
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
  to_email: string;
  cc?: string;
  bcc?: string;
  subject: string;
  body: string;
  attachments?: File[];
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  reply_to_id?: number;
  forward_from_id?: number;
  template_id?: number;
  template_data?: Record<string, any>;
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

// Email Service API functions
export const getMailAccounts = async (): Promise<MailAccount[]> => {
  try {
    console.log('[EmailService] Fetching mail accounts');
    const response = await api.get('/email/accounts');
    console.log('[EmailService] Mail accounts response:', response.data);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch mail accounts:', error);
    throw error;
  }
};

export const getMailAccount = async (accountId: number): Promise<MailAccount> => {
  try {
    const response = await api.get(`/email/accounts/${accountId}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch mail account:', error);
    throw error;
  }
};

export const getMailAccountForEmail = async (emailId: number): Promise<MailAccount> => {
  try {
    const response = await api.get(`/email/emails/${emailId}/account`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch account for email:', error);
    throw error;
  }
};

export const createMailAccount = async (accountData: Partial<MailAccount>): Promise<MailAccount> => {
  try {
    const response = await api.post('/email/accounts', accountData);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to create mail account:', error);
    throw error;
  }
};

export const updateMailAccount = async (accountId: number, updates: Partial<MailAccount>): Promise<MailAccount> => {
  try {
    const response = await api.put(`/email/accounts/${accountId}`, updates);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to update mail account:', error);
    throw error;
  }
};

export const deleteMailAccount = async (accountId: number): Promise<{ message: string }> => {
  try {
    const response = await api.delete(`/email/accounts/${accountId}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to delete mail account:', error);
    throw error;
  }
};

export const getEmails = async (
  accountId: number,
  folder: string = 'INBOX',
  limit: number = 50,
  offset: number = 0,
  statusFilter?: string
): Promise<EmailListResponse> => {
  try {
    const params = new URLSearchParams({
      folder,
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (statusFilter) {
      params.append('status_filter', statusFilter);
    }
    
    const response = await api.get(`/email/accounts/${accountId}/emails?${params}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch emails:', error);
    throw error;
  }
};

export const getEmail = async (emailId: number, includeAttachments: boolean = true): Promise<Email> => {
  try {
    const params = new URLSearchParams({
      include_attachments: includeAttachments.toString(),
    });
    
    const response = await api.get(`/email/emails/${emailId}?${params}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch email:', error);
    throw error;
  }
};

export const updateEmailStatus = async (emailId: number, status: Email['status']): Promise<{ message: string; new_status: string }> => {
  try {
    const response = await api.put(`/email/emails/${emailId}/status`, { new_status: status });
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to update email status:', error);
    throw error;
  }
};

export const getEmailThreads = async (
  accountId?: number,
  statusFilter?: string,
  limit: number = 50,
  offset: number = 0
): Promise<EmailThread[]> => {
  try {
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
    
    const response = await api.get(`/email/threads?${params}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch email threads:', error);
    throw error;
  }
};

export const getEmailThread = async (threadId: number): Promise<EmailThread> => {
  try {
    const response = await api.get(`/email/threads/${threadId}`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch email thread:', error);
    throw error;
  }
};

export const composeEmail = async (email: ComposeEmail, accountId: number): Promise<{ message: string; email_id: number }> => {
  try {
    const params = new URLSearchParams();
    params.append('account_id', accountId.toString());
    params.append('to_email', email.to_email);
    params.append('subject', email.subject);
    params.append('body', email.body);
    if (email.cc) params.append('cc', email.cc);
    if (email.bcc) params.append('bcc', email.bcc);
    if (email.priority) params.append('priority', email.priority);
    if (email.reply_to_id) params.append('reply_to_id', email.reply_to_id.toString());
    if (email.forward_from_id) params.append('forward_from_id', email.forward_from_id.toString());
    if (email.template_id) params.append('template_id', email.template_id.toString());
    if (email.template_data) params.append('template_data', JSON.stringify(email.template_data));

    let response;
    if (email.attachments && email.attachments.length > 0) {
      const formData = new FormData();
      email.attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });
      response = await api.post(`/email/compose?${params.toString()}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } else {
      response = await api.post(`/email/compose?${params.toString()}`, {});
    }
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to compose email:', error);
    throw error;
  }
};

export const downloadAttachment = async (attachmentId: number): Promise<{ message: string; filename: string }> => {
  try {
    const response = await api.get(`/email/attachments/${attachmentId}/download`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to download attachment:', error);
    throw error;
  }
};

export const triggerSync = async (accountId: number, fullSync: boolean = false, folder?: string): Promise<{ message: string; account_id: number }> => {
  try {
    const response = await api.post(`/email/accounts/${accountId}/sync`, {
      full_sync: fullSync,
      folder,
    });
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to trigger sync:', error);
    throw error;
  }
};

export const getSyncStatus = async (accountId: number): Promise<any> => {
  try {
    const response = await api.get(`/email/accounts/${accountId}/status`);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to get sync status:', error);
    throw error;
  }
};

export const getEmailTemplates = async (): Promise<any[]> => {
  try {
    const response = await api.get('/templates/email');
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to fetch email templates:', error);
    return [];
  }
};

export const applyTemplate = async (templateId: number, data: Record<string, any>): Promise<{ subject: string; body_html: string }> => {
  try {
    const response = await api.post(`/templates/email/${templateId}/render`, data);
    return response.data;
  } catch (error) {
    console.error('[EmailService] Failed to apply template:', error);
    throw error;
  }
};