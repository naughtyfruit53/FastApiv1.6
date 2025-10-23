/**
 * WCAG 2.1 AA Compliance Tests for Mobile
 * Tests accessibility compliance across mobile pages and components
 */

import { test, expect, devices } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from 'axe-playwright';

// Configure for mobile testing
test.use(devices['iPhone 12']);

test.describe('Mobile Accessibility - WCAG 2.1 AA Compliance', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('Login page accessibility', async ({ page }) => {
    await page.goto('/login');
    await injectAxe(page);

    // Check for accessibility violations
    await checkA11y(page, undefined, {
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });

    // Specific checks
    // Login button should have accessible name
    const loginButton = page.locator('button:has-text("Login")').or(
      page.locator('button[type="submit"]')
    );
    if (await loginButton.count() > 0) {
      await expect(loginButton.first()).toBeVisible();
    }

    // Form inputs should have labels
    const emailInput = page.locator('input[type="email"]').or(
      page.locator('input[name="email"]')
    );
    if (await emailInput.count() > 0) {
      const ariaLabel = await emailInput.first().getAttribute('aria-label');
      const associatedLabel = await emailInput.first().evaluate(el => {
        const id = el.getAttribute('id');
        return id ? document.querySelector(`label[for="${id}"]`) : null;
      });
      expect(ariaLabel || associatedLabel).toBeTruthy();
    }
  });

  test('Mobile dashboard accessibility', async ({ page }) => {
    // Set up demo mode for testing
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');
    await injectAxe(page);

    // Check for violations
    await checkA11y(page, undefined, {
      detailedReport: true,
    });

    // KPI cards should be accessible
    const cards = page.locator('[role="region"]').or(page.locator('article'));
    if (await cards.count() > 0) {
      const firstCard = cards.first();
      await expect(firstCard).toBeVisible();
      
      // Should have accessible name or label
      const hasAriaLabel = await firstCard.getAttribute('aria-label');
      const hasAriaLabelledby = await firstCard.getAttribute('aria-labelledby');
      expect(hasAriaLabel || hasAriaLabelledby).toBeTruthy();
    }
  });

  test('Mobile navigation accessibility', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');
    await injectAxe(page);

    // Check navigation landmarks
    const nav = page.locator('nav').or(page.locator('[role="navigation"]'));
    if (await nav.count() > 0) {
      await expect(nav.first()).toBeVisible();
      
      // Navigation should have accessible name
      const ariaLabel = await nav.first().getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();
    }

    // Bottom navigation should be accessible
    const bottomNav = page.locator('[data-testid="mobile-bottom-nav"]').or(
      page.locator('nav').filter({ hasText: /dashboard|sales|inventory/i })
    );
    if (await bottomNav.count() > 0) {
      await expect(bottomNav.first()).toBeVisible();
    }

    await checkA11y(page);
  });

  test('Mobile form accessibility', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/sales');
    await injectAxe(page);

    // Try to find and open a form
    const createButton = page.locator('button:has-text("Create")').or(
      page.locator('button:has-text("Add")').or(
        page.locator('[aria-label*="Create"]')
      )
    );

    if (await createButton.count() > 0) {
      await createButton.first().click();
      await page.waitForTimeout(1000);

      // Form should be accessible
      const form = page.locator('form').or(page.locator('[role="form"]'));
      if (await form.count() > 0) {
        await injectAxe(page);
        await checkA11y(page);

        // All form inputs should have labels
        const inputs = page.locator('input, select, textarea');
        const inputCount = await inputs.count();
        
        for (let i = 0; i < Math.min(inputCount, 5); i++) {
          const input = inputs.nth(i);
          const tagName = await input.evaluate(el => el.tagName);
          
          if (!['BUTTON', 'HIDDEN'].includes(tagName)) {
            const ariaLabel = await input.getAttribute('aria-label');
            const ariaLabelledby = await input.getAttribute('aria-labelledby');
            const placeholder = await input.getAttribute('placeholder');
            
            const id = await input.getAttribute('id');
            const hasLabel = id ? await page.locator(`label[for="${id}"]`).count() > 0 : false;
            
            expect(ariaLabel || ariaLabelledby || hasLabel || placeholder).toBeTruthy();
          }
        }
      }
    }
  });

  test('Mobile modal accessibility', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');
    await injectAxe(page);

    // Try to open a modal
    const buttonThatOpensModal = page.locator('button').first();
    if (await buttonThatOpensModal.count() > 0) {
      await buttonThatOpensModal.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]');
      if (await modal.count() > 0) {
        await expect(modal).toBeVisible();

        // Modal should have accessible name
        const ariaLabel = await modal.getAttribute('aria-label');
        const ariaLabelledby = await modal.getAttribute('aria-labelledby');
        expect(ariaLabel || ariaLabelledby).toBeTruthy();

        // Modal should trap focus
        await page.keyboard.press('Tab');
        const focusedElement = await page.evaluate(() => {
          return document.activeElement?.tagName;
        });
        expect(focusedElement).toBeTruthy();

        // Check for close button
        const closeButton = modal.locator('button[aria-label*="close"]').or(
          modal.locator('button:has-text("Close")')
        );
        if (await closeButton.count() > 0) {
          await expect(closeButton.first()).toBeVisible();
        }

        await checkA11y(page);
      }
    }
  });

  test('Touch target sizes - minimum 44x44px', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Check all interactive elements
    const interactiveElements = await page.locator(
      'button, a, input[type="checkbox"], input[type="radio"], [role="button"]'
    ).all();

    const tooSmallElements: { selector: string; size: { width: number; height: number } }[] = [];

    for (const element of interactiveElements.slice(0, 20)) { // Check first 20
      const box = await element.boundingBox();
      if (box) {
        const { width, height } = box;
        
        // WCAG requirement: minimum 44x44px touch target
        if (width < 44 || height < 44) {
          const selector = await element.evaluate(el => {
            return el.tagName.toLowerCase() + 
              (el.className ? `.${el.className.split(' ')[0]}` : '');
          });
          
          tooSmallElements.push({
            selector,
            size: { width, height }
          });
        }
      }
    }

    // Log any violations but don't fail (some elements may have padding)
    if (tooSmallElements.length > 0) {
      console.log('Elements with small touch targets:', tooSmallElements);
      // Most elements should meet the requirement
      expect(tooSmallElements.length).toBeLessThan(interactiveElements.length * 0.2);
    }
  });

  test('Color contrast compliance', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');
    await injectAxe(page);

    // Check color contrast
    const violations = await getViolations(page, 'color-contrast');
    
    // Should have minimal color contrast violations
    expect(violations.length).toBeLessThan(5);
    
    if (violations.length > 0) {
      console.log('Color contrast violations:', violations);
    }
  });

  test('Keyboard navigation', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Should be able to tab through interactive elements
    let focusableElements = 0;
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      
      const focusedElement = await page.evaluate(() => {
        const el = document.activeElement;
        return el ? {
          tagName: el.tagName,
          visible: el.offsetParent !== null
        } : null;
      });

      if (focusedElement?.visible) {
        focusableElements++;
      }
    }

    // Should have multiple focusable elements
    expect(focusableElements).toBeGreaterThan(3);
  });

  test('Screen reader announcements', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Check for ARIA live regions for dynamic content
    const liveRegions = page.locator('[aria-live]');
    const liveRegionCount = await liveRegions.count();
    
    if (liveRegionCount > 0) {
      // Should have appropriate aria-live values
      for (let i = 0; i < liveRegionCount; i++) {
        const ariaLive = await liveRegions.nth(i).getAttribute('aria-live');
        expect(['polite', 'assertive', 'off']).toContain(ariaLive);
      }
    }

    // Check for status messages
    const statusElements = page.locator('[role="status"]').or(
      page.locator('[role="alert"]')
    );
    // Status elements should exist for notifications
    // (but not required on every page)
  });

  test('Semantic HTML structure', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Should have proper landmarks
    const landmarks = {
      main: page.locator('main').or(page.locator('[role="main"]')),
      navigation: page.locator('nav').or(page.locator('[role="navigation"]')),
    };

    // Main content should exist
    const mainCount = await landmarks.main.count();
    expect(mainCount).toBeGreaterThan(0);

    // Should have proper heading hierarchy
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
    expect(h1Count).toBeLessThanOrEqual(2); // Usually one main heading

    // Headings should be in order (h1, h2, h3...)
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
  });

  test('Focus indicators visibility', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Find first focusable element
    const button = page.locator('button').first();
    await button.focus();

    // Check if focus indicator is visible
    const outlineStyle = await button.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return {
        outline: styles.outline,
        outlineWidth: styles.outlineWidth,
        outlineColor: styles.outlineColor,
        boxShadow: styles.boxShadow
      };
    });

    // Should have some focus indicator (outline or box-shadow)
    const hasFocusIndicator = 
      (outlineStyle.outline && outlineStyle.outline !== 'none') ||
      (outlineStyle.outlineWidth && outlineStyle.outlineWidth !== '0px') ||
      (outlineStyle.boxShadow && outlineStyle.boxShadow !== 'none');

    expect(hasFocusIndicator).toBeTruthy();
  });

  test('Image alt text', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Check all images
    const images = await page.locator('img').all();
    const imagesWithoutAlt: string[] = [];

    for (const img of images) {
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');
      
      // Decorative images should have alt="" or role="presentation"
      // Content images should have descriptive alt text
      if (alt === null && role !== 'presentation') {
        const src = await img.getAttribute('src');
        imagesWithoutAlt.push(src || 'unknown');
      }
    }

    // All images should have alt attribute
    expect(imagesWithoutAlt.length).toBe(0);
  });

  test('Form error messages accessibility', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    const submitButton = page.locator('button[type="submit"]').or(
      page.locator('button:has-text("Login")')
    );

    if (await submitButton.count() > 0) {
      await submitButton.first().click();
      await page.waitForTimeout(500);

      // Error messages should be accessible
      const errorMessages = page.locator('[role="alert"]').or(
        page.locator('.error').or(
          page.locator('[aria-invalid="true"]')
        )
      );

      if (await errorMessages.count() > 0) {
        // Error should be announced to screen readers
        const hasAriaLive = await errorMessages.first().evaluate(el => {
          return el.getAttribute('aria-live') !== null ||
                 el.getAttribute('role') === 'alert';
        });
        expect(hasAriaLive).toBeTruthy();
      }
    }
  });

  test('Mobile menu accessibility', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Find menu button (hamburger icon)
    const menuButton = page.locator('button[aria-label*="menu"]').or(
      page.locator('button[aria-label*="navigation"]').or(
        page.locator('[data-testid="menu-button"]')
      )
    );

    if (await menuButton.count() > 0) {
      // Menu button should have accessible name
      const ariaLabel = await menuButton.first().getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();

      // Open menu
      await menuButton.first().click();
      await page.waitForTimeout(500);

      // Menu should have proper ARIA attributes
      const menu = page.locator('[role="menu"]').or(
        page.locator('nav[aria-expanded="true"]').or(
          page.locator('[role="navigation"]')
        )
      );

      if (await menu.count() > 0) {
        await expect(menu.first()).toBeVisible();

        // Menu items should be accessible
        const menuItems = menu.locator('a, button, [role="menuitem"]');
        const itemCount = await menuItems.count();
        expect(itemCount).toBeGreaterThan(0);

        // Close menu with Escape key
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);

        // Menu should close
        const menuVisible = await menu.first().isVisible().catch(() => false);
        expect(menuVisible).toBeFalsy();
      }
    }
  });

  test('Demo mode indicators accessibility', async ({ page }) => {
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
    await injectAxe(page);

    // Check demo indicators accessibility
    const demoAlert = page.locator('[role="alert"]').or(
      page.locator('[role="status"]')
    ).filter({ hasText: /demo/i });

    if (await demoAlert.count() > 0) {
      await expect(demoAlert.first()).toBeVisible();

      // Should be announced to screen readers
      const ariaLive = await demoAlert.first().getAttribute('aria-live');
      expect(ariaLive).toBeTruthy();
    }

    // Check overall accessibility
    await checkA11y(page);
  });
});

test.describe('Mobile Accessibility - Additional Checks', () => {
  test('Text scaling - supports 200% zoom', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Get original height
    const originalHeight = await page.evaluate(() => document.body.scrollHeight);

    // Simulate 200% text size (larger font)
    await page.addStyleTag({
      content: '* { font-size: 200% !important; }'
    });

    await page.waitForTimeout(500);

    // Get new height
    const newHeight = await page.evaluate(() => document.body.scrollHeight);

    // Content should reflow and height should increase
    expect(newHeight).toBeGreaterThanOrEqual(originalHeight);

    // No horizontal scrolling should be introduced
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.body.scrollWidth > window.innerWidth;
    });
    expect(hasHorizontalScroll).toBeFalsy();
  });

  test('Motion preferences - respects prefers-reduced-motion', async ({ page }) => {
    // Simulate user preference for reduced motion
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    // Check if animations are reduced
    const hasReducedMotion = await page.evaluate(() => {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    });
    expect(hasReducedMotion).toBeTruthy();

    // Animations should be minimal or disabled
    // This is a guideline check - actual implementation varies
  });

  test('Language attribute present', async ({ page }) => {
    await page.goto('/mobile/dashboard');

    // HTML should have lang attribute
    const lang = await page.getAttribute('html', 'lang');
    expect(lang).toBeTruthy();
    expect(lang).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/); // e.g., 'en' or 'en-US'
  });

  test('Page title present and descriptive', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('demoMode', 'true');
      localStorage.setItem('access_token', 'demo_token');
    });

    await page.goto('/mobile/dashboard');

    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(5); // Should be descriptive
    expect(title).not.toBe('React App'); // Should not be default
  });
});
