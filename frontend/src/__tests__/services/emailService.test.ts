/**
 * @jest-environment jsdom
 */

import { emailService, MailAccount, ComposeEmail } from '../../services/emailService';
import { api } from '../../lib/api';

// Mock the api module
jest.mock('../../lib/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }
}));

const mockApi = api as jest.Mocked<typeof api>;

describe('EmailService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getMailAccounts', () => {
    it('should fetch mail accounts successfully', async () => {
      const mockAccounts: MailAccount[] = [
        {
          id: 1,
          name: 'Test Account',
          email_address: 'test@example.com',
          display_name: 'Test User',
          account_type: 'gmail_api',
          provider: 'google',
          sync_enabled: true,
          sync_frequency_minutes: 15,
          sync_folders: ['INBOX'],
          is_active: true,
          sync_status: 'active',
          total_messages_synced: 100,
          organization_id: 1,
          user_id: 1,
          created_at: '2023-01-01T00:00:00Z'
        }
      ];

      mockApi.get.mockResolvedValue({ data: mockAccounts });

      const result = await emailService.getMailAccounts();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/email/accounts');
      expect(result).toEqual(mockAccounts);
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Failed to fetch accounts';
      mockApi.get.mockRejectedValue(new Error(errorMessage));

      await expect(emailService.getMailAccounts()).rejects.toThrow(errorMessage);
    });
  });

  describe('getEmails', () => {
    it('should fetch emails with correct parameters', async () => {
      const mockEmailsResponse = {
        emails: [
          {
            id: 1,
            message_id: 'test-message-1',
            subject: 'Test Email',
            from_address: 'sender@example.com',
            from_name: 'Sender Name',
            to_addresses: [{ email: 'test@example.com' }],
            body_text: 'Test email body',
            status: 'unread' as const,
            priority: 'normal' as const,
            is_flagged: false,
            is_important: false,
            has_attachments: false,
            sent_at: '2023-01-01T10:00:00Z',
            received_at: '2023-01-01T10:00:00Z',
            folder: 'INBOX',
            created_at: '2023-01-01T10:00:00Z'
          }
        ],
        total_count: 1,
        offset: 0,
        limit: 50,
        has_more: false,
        folder: 'INBOX'
      };

      mockApi.get.mockResolvedValue({ data: mockEmailsResponse });

      const result = await emailService.getEmails(1, 'INBOX', 50, 0, 'unread');

      expect(mockApi.get).toHaveBeenCalledWith(
        '/api/v1/email/accounts/1/emails?folder=INBOX&limit=50&offset=0&status_filter=unread'
      );
      expect(result).toEqual(mockEmailsResponse);
    });

    it('should handle optional parameters correctly', async () => {
      const mockEmailsResponse = {
        emails: [],
        total_count: 0,
        offset: 0,
        limit: 25,
        has_more: false,
        folder: 'SENT'
      };

      mockApi.get.mockResolvedValue({ data: mockEmailsResponse });

      await emailService.getEmails(1, 'SENT', 25, 0);

      expect(mockApi.get).toHaveBeenCalledWith(
        '/api/v1/email/accounts/1/emails?folder=SENT&limit=25&offset=0'
      );
    });
  });

  describe('updateEmailStatus', () => {
    it('should update email status successfully', async () => {
      const mockResponse = { message: 'Status updated', new_status: 'read' };
      mockApi.put.mockResolvedValue({ data: mockResponse });

      const result = await emailService.updateEmailStatus(1, 'read');

      expect(mockApi.put).toHaveBeenCalledWith(
        '/api/v1/email/emails/1/status',
        { new_status: 'read' }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('composeEmail', () => {
    it('should compose and send email with attachments', async () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const composeData: ComposeEmail = {
        to: [{ email: 'recipient@example.com', name: 'Recipient' }],
        cc: [{ email: 'cc@example.com' }],
        subject: 'Test Subject',
        body_html: '<p>Test body</p>',
        priority: 'high',
        attachments: [mockFile]
      };

      const mockResponse = { message: 'Email sent', email_id: 123 };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await emailService.composeEmail(composeData, 1);

      expect(mockApi.post).toHaveBeenCalledWith(
        '/api/v1/email/accounts/1/send',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle compose without attachments', async () => {
      const composeData: ComposeEmail = {
        to: [{ email: 'recipient@example.com' }],
        subject: 'Simple Test',
        body_text: 'Simple text body'
      };

      const mockResponse = { message: 'Email sent', email_id: 124 };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await emailService.composeEmail(composeData, 1);

      expect(mockApi.post).toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });
  });

  describe('triggerSync', () => {
    it('should trigger manual sync', async () => {
      const mockResponse = { message: 'Sync triggered', account_id: 1 };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await emailService.triggerSync(1, true, 'INBOX');

      expect(mockApi.post).toHaveBeenCalledWith(
        '/api/v1/email/accounts/1/sync',
        { full_sync: true, folder: 'INBOX' }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('downloadAttachment', () => {
    it('should download attachment successfully', async () => {
      const mockResponse = { message: 'Attachment download', filename: 'test.pdf' };
      mockApi.get.mockResolvedValue({ data: mockResponse });

      const result = await emailService.downloadAttachment(1);

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/email/attachments/1/download');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getEmailTemplates', () => {
    it('should fetch email templates', async () => {
      const mockTemplates = [
        { id: 1, name: 'Invoice Template', description: 'Template for invoices' },
        { id: 2, name: 'Welcome Email', description: 'Welcome new customers' }
      ];
      mockApi.get.mockResolvedValue({ data: mockTemplates });

      const result = await emailService.getEmailTemplates();

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/templates/email');
      expect(result).toEqual(mockTemplates);
    });
  });

  describe('applyTemplate', () => {
    it('should apply template with data', async () => {
      const templateData = { customer_name: 'John Doe', amount: 1000 };
      const mockResponse = {
        subject: 'Invoice for John Doe',
        body_html: '<p>Dear John Doe, your invoice amount is $1000</p>'
      };
      mockApi.post.mockResolvedValue({ data: mockResponse });

      const result = await emailService.applyTemplate(1, templateData);

      expect(mockApi.post).toHaveBeenCalledWith(
        '/api/v1/templates/email/1/render',
        templateData
      );
      expect(result).toEqual(mockResponse);
    });
  });
});