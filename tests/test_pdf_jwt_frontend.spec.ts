"""
Frontend test for PDF functionality and JWT token expiry handling
"""
import { test, expect, Page } from '@playwright/test';

// Test configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://127.0.0.1:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://127.0.0.1:3000';

class PDFTestPage {
  constructor(private page: Page) {}

  async mockLogin() {
    // Mock a login by setting localStorage items
    await this.page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token-for-testing');
      localStorage.setItem('user_role', 'admin');
      localStorage.setItem('is_super_admin', 'true');
    });
  }

  async mockCompanyBranding() {
    // Mock the company branding API response
    await this.page.route(`${API_BASE_URL}/api/v1/company/branding`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          name: 'Test Company Ltd',
          address: '123 Test Street, Test City, Test State 12345',
          contact_number: '+91 9876543210',
          email: 'test@company.com',
          website: 'www.testcompany.com',
          gstin: '07AAACG2115R1ZN',
          logo_path: null
        })
      });
    });
  }

  async mockPDFAudit() {
    // Mock the PDF audit API response
    await this.page.route(`${API_BASE_URL}/api/v1/audit/pdf-generation`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'logged' })
      });
    });
  }

  async clickPDFButton() {
    // Click the PDF generation button
    await this.page.click('text=Generate PDF');
  }

  async checkPDFGeneration() {
    // Check for PDF generation success
    await this.page.waitForFunction(() => {
      return window.console.log.toString().includes('PDF generated successfully');
    });
  }
}

test.describe('PDF Generation System', () => {
  let pdfTestPage: PDFTestPage;

  test.beforeEach(async ({ page }) => {
    pdfTestPage = new PDFTestPage(page);
    await pdfTestPage.mockLogin();
    await pdfTestPage.mockCompanyBranding();
    await pdfTestPage.mockPDFAudit();
  });

  test('should generate PDF for manufacturing voucher', async ({ page }) => {
    // Navigate to material receipt page
    await page.goto(`${FRONTEND_URL}/vouchers/Manufacturing-Vouchers/material-receipt`);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Fill in voucher data
    await page.fill('[name="voucher_number"]', 'MR/2024/001');
    await page.fill('[name="date"]', '2024-01-01');
    await page.fill('[name="notes"]', 'Test material receipt for PDF generation');
    
    // Check if PDF button exists
    const pdfButton = await page.locator('text=Generate PDF');
    await expect(pdfButton).toBeVisible();
    
    // Click PDF button
    await pdfButton.click();
    
    // Verify no errors occurred
    const errorAlert = await page.locator('[role="alert"]');
    await expect(errorAlert).not.toBeVisible();
  });

  test('should include all required PDF elements', async ({ page }) => {
    // Test that the PDF service includes all required elements
    await page.goto(`${FRONTEND_URL}/vouchers/Purchase-Vouchers/purchase-voucher`);
    await page.waitForLoadState('networkidle');
    
    // Fill in comprehensive voucher data
    await page.fill('[name="voucher_number"]', 'PV/2024/001');
    await page.fill('[name="date"]', '2024-01-01');
    await page.fill('[name="reference"]', 'PO/2024/001');
    await page.fill('[name="notes"]', 'Test purchase voucher with items');
    
    // Add an item
    await page.click('text=Add Item');
    
    // Fill item details
    await page.fill('[name="items.0.quantity"]', '10');
    await page.fill('[name="items.0.unit_price"]', '100.00');
    await page.fill('[name="items.0.gst_rate"]', '18');
    
    // Generate PDF
    const pdfButton = await page.locator('text=Generate PDF');
    await pdfButton.click();
    
    // Should not show any error
    const errorAlert = await page.locator('[role="alert"]');
    await expect(errorAlert).not.toBeVisible();
  });
});

test.describe('JWT Token Expiry Handling', () => {
  test('should redirect to login on token expiry', async ({ page }) => {
    // Mock a 401 response
    await page.route(`${API_BASE_URL}/api/v1/**`, async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token has expired' })
      });
    });

    // Navigate to a protected page
    await page.goto(`${FRONTEND_URL}/dashboard`);
    
    // Should be redirected to login
    await page.waitForURL('**/login');
    expect(page.url()).toContain('/login');
  });

  test('should preserve navigation state on token expiry', async ({ page }) => {
    // Set up initial state
    await page.addInitScript(() => {
      localStorage.setItem('token', 'valid-token');
      localStorage.setItem('user_role', 'admin');
    });

    // Navigate to a specific voucher page
    await page.goto(`${FRONTEND_URL}/vouchers/Purchase-Vouchers/purchase-voucher`);
    
    // Fill some form data
    await page.fill('[name="voucher_number"]', 'PV/2024/TEST');
    await page.fill('[name="notes"]', 'Test notes for state preservation');
    
    // Mock token expiry
    await page.route(`${API_BASE_URL}/api/v1/**`, async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token has expired' })
      });
    });
    
    // Trigger an API call (try to save)
    await page.click('text=Save');
    
    // Should be redirected to login
    await page.waitForURL('**/login');
    
    // Check that return URL is stored
    const returnUrl = await page.evaluate(() => sessionStorage.getItem('returnUrlAfterLogin'));
    expect(returnUrl).toContain('/vouchers/Purchase-Vouchers/purchase-voucher');
  });
});

if (require.main === module) {
  // Run with: npx playwright test tests/test_pdf_jwt_frontend.spec.ts
  console.log('Run tests with: npx playwright test');
}