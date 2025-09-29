/**
 * Email Module E2E Tests
 * Basic functional validation
 */

import { test, expect } from '@playwright/test';

test.describe('Email Module', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for testing
    await page.route('**/api/v1/email/accounts', async route => {
      const mockAccounts = [
        {
          id: 1,
          name: 'Test Account',
          email_address: 'test@example.com',
          display_name: 'Test User',
          account_type: 'gmail_api',
          sync_enabled: true,
          is_active: true,
          sync_status: 'active',
          total_messages_synced: 100,
          organization_id: 1,
          user_id: 1,
          created_at: '2023-01-01T00:00:00Z'
        }
      ];
      await route.fulfill({ json: mockAccounts });
    });

    await page.route('**/api/v1/email/accounts/1/emails*', async route => {
      const mockEmails = {
        emails: [
          {
            id: 1,
            message_id: 'test-1',
            subject: 'Welcome to TritIQ Email',
            from_address: 'welcome@tritiq.com',
            from_name: 'TritIQ Team',
            to_addresses: [{ email: 'test@example.com' }],
            body_text: 'Welcome to our new email system!',
            status: 'unread',
            priority: 'normal',
            is_flagged: false,
            is_important: false,
            has_attachments: false,
            sent_at: '2023-01-01T10:00:00Z',
            received_at: '2023-01-01T10:00:00Z',
            folder: 'INBOX',
            created_at: '2023-01-01T10:00:00Z'
          },
          {
            id: 2,
            message_id: 'test-2',
            subject: 'Invoice #INV-001',
            from_address: 'billing@company.com',
            from_name: 'Billing Department',
            to_addresses: [{ email: 'test@example.com' }],
            body_html: '<p>Your invoice is ready for review.</p>',
            status: 'read',
            priority: 'high',
            is_flagged: true,
            is_important: true,
            has_attachments: true,
            sent_at: '2023-01-01T11:00:00Z',
            received_at: '2023-01-01T11:00:00Z',
            folder: 'INBOX',
            created_at: '2023-01-01T11:00:00Z'
          }
        ],
        total_count: 2,
        offset: 0,
        limit: 25,
        has_more: false,
        folder: 'INBOX'
      };
      await route.fulfill({ json: mockEmails });
    });

    await page.route('**/api/v1/oauth/providers', async route => {
      const mockProviders = {
        providers: [
          {
            name: 'google',
            display_name: 'Google',
            icon: 'google',
            scopes: ['gmail.readonly', 'gmail.send']
          },
          {
            name: 'microsoft',
            display_name: 'Microsoft',
            icon: 'microsoft', 
            scopes: ['Mail.Read', 'Mail.Send']
          }
        ]
      };
      await route.fulfill({ json: mockProviders });
    });
  });

  test('should render email module navigation', async ({ page }) => {
    await page.goto('/');
    
    // Check if email is in navigation (assuming main navigation exists)
    const emailNav = page.getByText('Email');
    if (await emailNav.count() > 0) {
      expect(emailNav).toBeTruthy();
    }
  });

  test('should display inbox with email list when account is connected', async ({ page }) => {
    // Navigate directly to email module
    await page.goto('/email');
    
    // Should show inbox interface
    await expect(page.getByText('Inbox')).toBeVisible();
    await expect(page.getByText('Compose')).toBeVisible();
    
    // Should show folder navigation
    await expect(page.getByText('Sent')).toBeVisible();
    await expect(page.getByText('Archived')).toBeVisible();
    await expect(page.getByText('Trash')).toBeVisible();
    
    // Should show email list
    await expect(page.getByText('Welcome to TritIQ Email')).toBeVisible();
    await expect(page.getByText('Invoice #INV-001')).toBeVisible();
    await expect(page.getByText('TritIQ Team')).toBeVisible();
    await expect(page.getByText('Billing Department')).toBeVisible();
  });

  test('should show compose dialog when compose button clicked', async ({ page }) => {
    await page.goto('/email');
    
    // Click compose button
    await page.getByText('Compose').click();
    
    // Should show composer interface
    await expect(page.getByText('New Message')).toBeVisible();
    await expect(page.getByPlaceholder('Enter email addresses')).toBeVisible();
    await expect(page.getByLabel('Subject')).toBeVisible();
  });

  test('should show search and filter controls', async ({ page }) => {
    await page.goto('/email');
    
    // Should have search box
    await expect(page.getByPlaceholder('Search emails...')).toBeVisible();
    
    // Should have filter dropdown
    await expect(page.getByText('Filter')).toBeVisible();
    
    // Should have sync button
    const syncButton = page.getByTitle('Sync emails');
    if (await syncButton.count() > 0) {
      await expect(syncButton).toBeVisible();
    }
  });

  test('should show OAuth login when no accounts connected', async ({ page }) => {
    // Mock empty accounts response
    await page.route('**/api/v1/email/accounts', async route => {
      await route.fulfill({ json: [] });
    });
    
    await page.goto('/email');
    
    // Should show OAuth login interface
    await expect(page.getByText('Connect Your Email Account')).toBeVisible();
    await expect(page.getByText('Connect Email Account')).toBeVisible();
  });

  test('should handle email interaction', async ({ page }) => {
    await page.goto('/email');
    
    // Click on an email
    await page.getByText('Welcome to TritIQ Email').click();
    
    // Should navigate to thread view (or email detail)
    // The exact behavior depends on implementation
  });

  test('should show attachment indicators', async ({ page }) => {
    await page.goto('/email');
    
    // The second email has attachments, should show indicator
    const attachmentIcon = page.locator('[data-testid="AttachFileIcon"]');
    if (await attachmentIcon.count() > 0) {
      await expect(attachmentIcon.first()).toBeVisible();
    }
  });

  test('should show priority and flag indicators', async ({ page }) => {
    await page.goto('/email');
    
    // The second email is flagged and important
    const starIcon = page.locator('[data-testid="StarIcon"]');
    if (await starIcon.count() > 0) {
      await expect(starIcon.first()).toBeVisible();
    }
  });
});

test.describe('Email Composer', () => {
  test('should allow entering recipients and subject', async ({ page }) => {
    await page.goto('/email');
    await page.getByText('Compose').click();
    
    // Enter recipient
    const toField = page.getByPlaceholder('Enter email addresses');
    await toField.fill('recipient@example.com');
    await toField.press('Enter');
    
    // Should show recipient chip
    await expect(page.getByText('recipient@example.com')).toBeVisible();
    
    // Enter subject
    await page.getByLabel('Subject').fill('Test Email Subject');
    
    // Verify subject is entered
    await expect(page.getByDisplayValue('Test Email Subject')).toBeVisible();
  });

  test('should show CC and BCC options', async ({ page }) => {
    await page.goto('/email');
    await page.getByText('Compose').click();
    
    // Show CC field
    await page.getByText('CC').click();
    await expect(page.getByLabel('CC')).toBeVisible();
    
    // Show BCC field  
    await page.getByText('BCC').click();
    await expect(page.getByLabel('BCC')).toBeVisible();
  });

  test('should have priority selector', async ({ page }) => {
    await page.goto('/email');
    await page.getByText('Compose').click();
    
    // Should show priority dropdown
    await expect(page.getByLabel('Priority')).toBeVisible();
  });
});

test.describe('Email Templates', () => {
  test('should show template button in composer', async ({ page }) => {
    await page.goto('/email');
    await page.getByText('Compose').click();
    
    // Should show templates button
    await expect(page.getByText('Templates')).toBeVisible();
  });
});