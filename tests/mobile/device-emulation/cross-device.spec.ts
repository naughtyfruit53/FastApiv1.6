/**
 * Device Emulation Test Suite
 * Tests mobile components across different device configurations
 */

const devices = [
  {
    name: 'iPhone 12',
    width: 390,
    height: 844,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    touch: true,
  },
  {
    name: 'iPhone 12 Pro Max',
    width: 428,
    height: 926,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    touch: true,
  },
  {
    name: 'Samsung Galaxy S21',
    width: 360,
    height: 800,
    userAgent: 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36',
    touch: true,
  },
  {
    name: 'iPad Air',
    width: 820,
    height: 1180,
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    touch: true,
  },
  {
    name: 'Desktop',
    width: 1920,
    height: 1080,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    touch: false,
  },
];

import { test, expect } from '@playwright/test';

devices.forEach(device => {
  test.describe(`${device.name} - Mobile Components`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: device.width, height: device.height });
      await page.setUserAgent(device.userAgent);
    });

    test('should render mobile layout correctly', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Check if mobile layout is detected and rendered
      if (device.touch) {
        await expect(page.locator('[data-testid="mobile-layout"]')).toBeVisible();
        await expect(page.locator('[data-testid="desktop-layout"]')).not.toBeVisible();
      } else {
        await expect(page.locator('[data-testid="desktop-layout"]')).toBeVisible();
        await expect(page.locator('[data-testid="mobile-layout"]')).not.toBeVisible();
      }
    });

    test('should handle touch interactions on swipeable cards', async ({ page }) => {
      if (!device.touch) {
        test.skip('Touch interactions only available on touch devices');
      }

      await page.goto('/mobile/dashboard');
      
      const card = page.locator('[data-testid="swipeable-card"]').first();
      await expect(card).toBeVisible();

      // Test swipe gesture
      const cardBounds = await card.boundingBox();
      if (cardBounds) {
        await page.touchscreen.tap(cardBounds.x + cardBounds.width / 2, cardBounds.y + cardBounds.height / 2);
        
        // Swipe right
        await page.touchscreen.tap(cardBounds.x + 50, cardBounds.y + cardBounds.height / 2);
        await page.mouse.move(cardBounds.x + cardBounds.width - 50, cardBounds.y + cardBounds.height / 2);
        
        // Check if action is revealed
        await expect(page.locator('[data-testid="swipe-action"]')).toBeVisible();
      }
    });

    test('should open bottom sheet correctly', async ({ page }) => {
      if (!device.touch) {
        test.skip('Bottom sheet primarily for touch devices');
      }

      await page.goto('/mobile/dashboard');
      
      const trigger = page.locator('[data-testid="bottom-sheet-trigger"]');
      await trigger.click();
      
      await expect(page.locator('[data-testid="bottom-sheet"]')).toBeVisible();
      
      // Test dismissal by backdrop
      await page.locator('[data-testid="bottom-sheet-backdrop"]').click();
      await expect(page.locator('[data-testid="bottom-sheet"]')).not.toBeVisible();
    });

    test('should handle contextual menu correctly', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const menuTarget = page.locator('[data-testid="contextual-menu-target"]');
      
      if (device.touch) {
        // Long press for mobile
        await menuTarget.press('ArrowDown', { delay: 600 });
      } else {
        // Right click for desktop
        await menuTarget.click({ button: 'right' });
      }
      
      await expect(page.locator('[data-testid="contextual-menu"]')).toBeVisible();
      
      // Test menu action
      await page.locator('[data-testid="menu-action-edit"]').click();
      await expect(page.locator('[data-testid="contextual-menu"]')).not.toBeVisible();
    });

    test('should maintain accessibility standards', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Check for proper ARIA labels
      const interactiveElements = page.locator('button, [role="button"], a, input');
      const count = await interactiveElements.count();
      
      for (let i = 0; i < count; i++) {
        const element = interactiveElements.nth(i);
        const ariaLabel = await element.getAttribute('aria-label');
        const textContent = await element.textContent();
        
        // Every interactive element should have accessible text
        expect(ariaLabel || textContent).toBeTruthy();
      }
      
      // Check color contrast (simplified check)
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();
      
      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const styles = await button.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            backgroundColor: computed.backgroundColor,
            color: computed.color,
          };
        });
        
        // Ensure buttons have contrasting colors
        expect(styles.backgroundColor).not.toBe(styles.color);
      }
    });

    test('should handle keyboard navigation', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Test tab navigation
      await page.keyboard.press('Tab');
      const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
      expect(['BUTTON', 'A', 'INPUT']).toContain(firstFocused);
      
      await page.keyboard.press('Tab');
      const secondFocused = await page.evaluate(() => document.activeElement?.tagName);
      expect(['BUTTON', 'A', 'INPUT']).toContain(secondFocused);
      
      // Test escape key
      await page.keyboard.press('Escape');
      // Should close any open overlays
    });

    test('should handle different orientations', async ({ page }) => {
      if (!device.touch) {
        test.skip('Orientation testing only for mobile devices');
      }

      // Portrait
      await page.setViewportSize({ width: device.width, height: device.height });
      await page.goto('/mobile/dashboard');
      
      const portraitLayout = await page.locator('[data-testid="mobile-layout"]').isVisible();
      expect(portraitLayout).toBe(true);
      
      // Landscape
      await page.setViewportSize({ width: device.height, height: device.width });
      await page.reload();
      
      const landscapeLayout = await page.locator('[data-testid="mobile-layout"]').isVisible();
      expect(landscapeLayout).toBe(true);
    });

    test('should perform well under load', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Start performance monitoring
      await page.evaluate(() => performance.mark('test-start'));
      
      // Simulate multiple interactions
      const cards = page.locator('[data-testid="swipeable-card"]');
      const cardCount = await cards.count();
      
      for (let i = 0; i < Math.min(cardCount, 10); i++) {
        if (device.touch) {
          await cards.nth(i).tap();
        } else {
          await cards.nth(i).click();
        }
        await page.waitForTimeout(100);
      }
      
      // End performance monitoring
      await page.evaluate(() => performance.mark('test-end'));
      
      const performanceMetrics = await page.evaluate(() => {
        performance.measure('test-duration', 'test-start', 'test-end');
        const measure = performance.getEntriesByName('test-duration')[0];
        return measure.duration;
      });
      
      // Should complete interactions within reasonable time
      expect(performanceMetrics).toBeLessThan(5000); // 5 seconds
    });

    test('should handle network conditions', async ({ page }) => {
      // Simulate slow network
      await page.route('**/*', route => {
        setTimeout(() => route.continue(), 1000);
      });
      
      await page.goto('/mobile/dashboard');
      
      // Should show loading states
      await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();
      
      // Should eventually load content
      await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible({ timeout: 10000 });
    });

    test('should maintain state across navigation', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Set some state (e.g., open a bottom sheet)
      await page.locator('[data-testid="bottom-sheet-trigger"]').click();
      await expect(page.locator('[data-testid="bottom-sheet"]')).toBeVisible();
      
      // Navigate away and back
      await page.goto('/mobile/sales');
      await page.goBack();
      
      // State should be preserved or gracefully reset
      await expect(page.locator('[data-testid="mobile-layout"]')).toBeVisible();
    });
  });
});