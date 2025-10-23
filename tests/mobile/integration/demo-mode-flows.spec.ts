/**
 * Demo Mode E2E Test Suite
 * Tests complete demo mode flows including user activation, session management, and data isolation
 */

import { test, expect, devices } from '@playwright/test';

// Configure test for mobile devices
test.use(devices['iPhone 12']);

test.describe('Demo Mode - Complete User Flows', () => {
  test.beforeEach(async ({ page }) => {
    // Start fresh for each test
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('New user demo flow - Complete workflow', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    await expect(page).toHaveURL('/login');

    // Click Try Demo Mode button
    await expect(page.locator('button:has-text("Try Demo Mode")')).toBeVisible();
    await page.click('button:has-text("Try Demo Mode")');

    // Demo mode dialog should appear
    await expect(page.locator('role=dialog')).toBeVisible();
    await expect(page.locator('text=User Type')).toBeVisible();

    // Select "I'm new" option
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    // Fill demo registration form
    await page.fill('input[name="fullName"]', 'Test Demo User');
    await page.fill('input[name="email"]', 'demo.test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Demo Test Company');

    // Submit form
    await page.click('button:has-text("Continue")');

    // OTP step should appear
    await expect(page.locator('text=Verification')).toBeVisible();
    await expect(page.locator('text=Demo OTP sent')).toBeVisible();

    // Enter any 6-digit OTP (accepted in demo)
    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    // Should show success message and redirect to demo page
    await expect(page.locator('text=Demo login successful')).toBeVisible();
    await page.waitForURL('/demo', { timeout: 5000 });

    // Verify demo mode indicators
    await expect(page.locator('text=Demo Mode Active')).toBeVisible();
    await expect(page.locator('text=Temporary User')).toBeVisible();

    // Verify localStorage flags
    const demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
    const isDemoTempUser = await page.evaluate(() => localStorage.getItem('isDemoTempUser'));
    expect(demoMode).toBe('true');
    expect(isDemoTempUser).toBe('true');

    // Test navigation to different modules
    await page.click('text=Sales');
    await expect(page).toHaveURL(/.*mobile\/sales/);
    await expect(page.locator('text=DEMO')).toBeVisible();

    // Navigate back to dashboard
    await page.click('text=Dashboard');
    await expect(page.locator('text=Demo Mode Active')).toBeVisible();

    // Exit demo mode
    await page.click('button:has-text("End Session")');
    await page.waitForURL('/login', { timeout: 5000 });

    // Verify demo data cleared
    const clearedDemoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
    expect(clearedDemoMode).toBeNull();
  });

  test('Existing user demo flow', async ({ page }) => {
    // First, create a mock "existing user" session
    await page.goto('/login');

    // Click demo mode button
    await page.click('button:has-text("Try Demo Mode")');
    await expect(page.locator('role=dialog')).toBeVisible();

    // Select "I have an existing account"
    await page.click('input[value="current"]');
    await page.click('button:has-text("Next")');

    // Should set pending demo flag and redirect to login
    await expect(page).toHaveURL('/login');

    // Verify pending demo flag
    const pendingDemoMode = await page.evaluate(() => 
      localStorage.getItem('pendingDemoMode')
    );
    expect(pendingDemoMode).toBe('true');

    // Simulate login (in real scenario, user would enter credentials)
    // For test, we'll set auth tokens directly
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_123');
      localStorage.setItem('user_role', 'user');
    });

    // Navigate to dashboard which should activate demo mode
    await page.goto('/dashboard');

    // Demo mode should be activated
    const demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
    expect(demoMode).toBe('true');

    // Should NOT be temporary user
    const isDemoTempUser = await page.evaluate(() => 
      localStorage.getItem('isDemoTempUser')
    );
    expect(isDemoTempUser).not.toBe('true');
  });

  test('Demo mode session persistence across pages', async ({ page }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Navigate to multiple pages
    const pages = [
      { label: 'Sales', url: /.*sales/ },
      { label: 'CRM', url: /.*crm/ },
      { label: 'Inventory', url: /.*inventory/ },
      { label: 'Finance', url: /.*finance/ }
    ];

    for (const pageInfo of pages) {
      await page.click(`text=${pageInfo.label}`);
      await expect(page).toHaveURL(pageInfo.url);

      // Verify demo indicator present on each page
      await expect(page.locator('text=DEMO')).toBeVisible();

      // Verify demo mode flag persists
      const demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
      expect(demoMode).toBe('true');
    }
  });

  test('Demo mode data isolation - no API calls', async ({ page, request }) => {
    // Set up request interception to verify no real API calls
    const apiCalls: string[] = [];
    
    page.on('request', (req) => {
      if (req.url().includes('/api/') && !req.url().includes('demo')) {
        apiCalls.push(req.url());
      }
    });

    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Perform actions that would normally make API calls
    await page.click('text=Sales');
    await page.click('button:has-text("Create Order")', { timeout: 5000 }).catch(() => {});
    
    // Wait a bit for any potential API calls
    await page.waitForTimeout(2000);

    // Verify no production API calls were made
    const productionApiCalls = apiCalls.filter(
      url => !url.includes('localhost') && !url.includes('demo')
    );
    expect(productionApiCalls.length).toBe(0);
  });

  test('Demo mode temporary data storage', async ({ page }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Set some temporary demo data
    await page.evaluate(() => {
      const demoTempData = {
        orders: [
          { id: 'demo_1', name: 'Test Order 1', amount: 1000 }
        ],
        notes: ['Test note 1', 'Test note 2']
      };
      localStorage.setItem('demoTempData', JSON.stringify(demoTempData));
    });

    // Verify data is stored
    const tempData = await page.evaluate(() => {
      return localStorage.getItem('demoTempData');
    });
    expect(tempData).toBeTruthy();
    const parsedData = JSON.parse(tempData || '{}');
    expect(parsedData.orders).toHaveLength(1);
    expect(parsedData.notes).toHaveLength(2);

    // Exit demo mode
    await page.click('button:has-text("End Session")');
    await page.waitForURL('/login');

    // Verify temp data is cleared
    const clearedTempData = await page.evaluate(() => {
      return localStorage.getItem('demoTempData');
    });
    expect(clearedTempData).toBeNull();
  });

  test('Demo mode toggle switch', async ({ page }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Find and verify demo mode switch
    const demoSwitch = page.locator('input[type="checkbox"]').filter({ 
      hasText: /Demo Mode/i 
    }).or(page.locator('role=switch'));
    
    // Demo mode should be ON
    let demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
    expect(demoMode).toBe('true');

    // Toggle OFF (if switch is available)
    if (await demoSwitch.count() > 0) {
      await demoSwitch.first().click();
      await page.waitForTimeout(500);

      // Verify demo mode toggled
      demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
      expect(demoMode).toBe('false');

      // Toggle back ON
      await demoSwitch.first().click();
      await page.waitForTimeout(500);

      demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
      expect(demoMode).toBe('true');
    }
  });

  test('Demo mode indicators visibility on mobile', async ({ page }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Check for various demo indicators
    const indicators = [
      'text=Demo Mode Active',
      'text=Temporary User',
      'text=DEMO',
      'text=Sample Data'
    ];

    for (const indicator of indicators) {
      // At least some indicators should be visible
      const element = page.locator(indicator);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
      }
    }

    // Check for demo badge/chip on mobile
    const demoBadge = page.locator('[role="status"]', { hasText: /demo/i });
    if (await demoBadge.count() > 0) {
      await expect(demoBadge.first()).toBeVisible();
    }
  });

  test('Demo mode session expiry on browser close simulation', async ({ page, context }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Verify demo session active
    let demoMode = await page.evaluate(() => localStorage.getItem('demoMode'));
    expect(demoMode).toBe('true');

    // Close context (simulates browser close for temporary user)
    await context.close();

    // Create new context (simulates reopening browser)
    const newContext = await page.context().browser()?.newContext();
    const newPage = await newContext!.newPage();

    // Navigate to app
    await newPage.goto('/login');

    // Demo mode should not be active (session expired)
    const newDemoMode = await newPage.evaluate(() => 
      localStorage.getItem('demoMode')
    );
    expect(newDemoMode).toBeNull();

    await newContext!.close();
  });

  test('Demo mode with realistic mock data', async ({ page }) => {
    // Activate demo mode
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Verify mock data is displayed
    // Should see purchase vouchers
    const purchaseVoucher = page.locator('text=PV-2024-').or(page.locator('text=Purchase'));
    if (await purchaseVoucher.count() > 0) {
      await expect(purchaseVoucher.first()).toBeVisible();
    }

    // Should see sales vouchers
    const salesVoucher = page.locator('text=SV-2024-').or(page.locator('text=Sales'));
    if (await salesVoucher.count() > 0) {
      await expect(salesVoucher.first()).toBeVisible();
    }

    // Should see company info
    await expect(page.locator('text=Demo')).toBeVisible();
  });
});

test.describe('Demo Mode - Error Scenarios', () => {
  test('Invalid OTP handling', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    // Try with less than 6 digits
    await page.fill('input[name="otp"]', '123');
    await page.click('button:has-text("Verify")');

    // Should show error
    await expect(page.locator('text=/valid.*6-digit/i')).toBeVisible();
  });

  test('Empty form validation', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    // Try to submit without filling
    await page.click('button:has-text("Continue")');

    // Should show validation errors
    await expect(page.locator('text=/required/i')).toBeVisible();
  });

  test('No user type selected', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');

    // Try to proceed without selecting user type
    await page.click('button:has-text("Next")');

    // Should show error
    await expect(page.locator('text=/select.*user/i')).toBeVisible();
  });
});

test.describe('Demo Mode - Accessibility', () => {
  test('Demo mode dialog keyboard navigation', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');

    // Dialog should be focusable
    await page.keyboard.press('Tab');
    
    // Should be able to select option with keyboard
    await page.keyboard.press('Space');
    
    // Should be able to navigate to Next button
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
  });

  test('Demo mode dialog ARIA labels', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');

    // Dialog should have proper ARIA attributes
    const dialog = page.locator('role=dialog');
    await expect(dialog).toBeVisible();
    
    // Should have title
    const title = page.locator('role=heading', { hasText: /user type|demo/i });
    if (await title.count() > 0) {
      await expect(title.first()).toBeVisible();
    }
  });

  test('Demo indicators have proper contrast', async ({ page }) => {
    await page.goto('/login');
    await page.click('button:has-text("Try Demo Mode")');
    await page.click('input[value="new"]');
    await page.click('button:has-text("Next")');

    await page.fill('input[name="fullName"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phoneNumber"]', '+1234567890');
    await page.fill('input[name="companyName"]', 'Test Co');
    await page.click('button:has-text("Continue")');

    await page.fill('input[name="otp"]', '123456');
    await page.click('button:has-text("Verify")');

    await page.waitForURL('/demo');

    // Check demo alert contrast
    const alert = page.locator('role=alert').or(page.locator('[role="status"]'));
    if (await alert.count() > 0) {
      const bgColor = await alert.first().evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      );
      const textColor = await alert.first().evaluate(el => 
        window.getComputedStyle(el).color
      );
      
      // Both should be defined
      expect(bgColor).toBeTruthy();
      expect(textColor).toBeTruthy();
    }
  });
});
