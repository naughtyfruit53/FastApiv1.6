import { test, expect } from '@playwright/test';
import { MobileAccessibilityTester } from '../utils/accessibilityTester';

test.describe('Mobile Accessibility Compliance', () => {
  let accessibilityTester: MobileAccessibilityTester;

  test.beforeEach(async ({ page }) => {
    accessibilityTester = new MobileAccessibilityTester(page);
    await accessibilityTester.initialize();
  });

  test.describe('WCAG 2.1 AA Compliance', () => {
    test('should pass WCAG 2.1 AA standards on dashboard', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      await accessibilityTester.runWCAGComplianceCheck();
    });

    test('should pass WCAG 2.1 AA standards on sales page', async ({ page }) => {
      await page.goto('/mobile/sales');
      await accessibilityTester.runWCAGComplianceCheck();
    });

    test('should pass WCAG 2.1 AA standards on CRM page', async ({ page }) => {
      await page.goto('/mobile/crm');
      await accessibilityTester.runWCAGComplianceCheck();
    });

    test('should pass WCAG 2.1 AA standards on inventory page', async ({ page }) => {
      await page.goto('/mobile/inventory');
      await accessibilityTester.runWCAGComplianceCheck();
    });

    test('should pass WCAG 2.1 AA standards on finance page', async ({ page }) => {
      await page.goto('/mobile/finance');
      await accessibilityTester.runWCAGComplianceCheck();
    });
  });

  test.describe('Touch Target Validation', () => {
    test('should have adequate touch target sizes on all pages', async ({ page }) => {
      const pages = [
        '/mobile/dashboard',
        '/mobile/sales',
        '/mobile/crm',
        '/mobile/inventory',
        '/mobile/finance',
        '/mobile/hr',
        '/mobile/service',
        '/mobile/reports',
        '/mobile/settings',
      ];

      for (const pageUrl of pages) {
        await page.goto(pageUrl);
        const result = await accessibilityTester.validateTouchTargets();
        
        expect(result.passed, 
          `Touch target violations on ${pageUrl}: ${JSON.stringify(result.violations, null, 2)}`
        ).toBe(true);
      }
    });

    test('should have adequate spacing between touch targets', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const spacingResult = await page.evaluate(() => {
        const interactiveElements = Array.from(
          document.querySelectorAll('button, a, input, [role="button"], [tabindex]:not([tabindex="-1"])')
        );
        const violations: any[] = [];

        for (let i = 0; i < interactiveElements.length; i++) {
          const currentRect = interactiveElements[i].getBoundingClientRect();
          
          for (let j = i + 1; j < interactiveElements.length; j++) {
            const otherRect = interactiveElements[j].getBoundingClientRect();
            
            // Calculate distance between centers
            const distance = Math.sqrt(
              Math.pow(currentRect.x + currentRect.width / 2 - (otherRect.x + otherRect.width / 2), 2) +
              Math.pow(currentRect.y + currentRect.height / 2 - (otherRect.y + otherRect.height / 2), 2)
            );
            
            // Minimum spacing should be 8px
            if (distance < 8 && distance > 0) {
              violations.push({
                element1: {
                  tag: interactiveElements[i].tagName,
                  text: (interactiveElements[i] as HTMLElement).textContent?.trim(),
                },
                element2: {
                  tag: interactiveElements[j].tagName,
                  text: (interactiveElements[j] as HTMLElement).textContent?.trim(),
                },
                distance,
              });
            }
          }
        }
        
        return violations;
      });

      expect(spacingResult.length, 
        `Touch target spacing violations: ${JSON.stringify(spacingResult, null, 2)}`
      ).toBe(0);
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support full keyboard navigation', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Test tab navigation
      let focusedElements = 0;
      const maxTabs = 20; // Reasonable limit to prevent infinite loops
      
      for (let i = 0; i < maxTabs; i++) {
        await page.keyboard.press('Tab');
        
        const activeElement = await page.evaluate(() => {
          const element = document.activeElement;
          return element ? {
            tagName: element.tagName,
            type: (element as HTMLInputElement).type || null,
            role: element.getAttribute('role'),
            tabIndex: element.tabIndex,
            text: element.textContent?.trim().substring(0, 50),
          } : null;
        });

        if (activeElement && activeElement.tabIndex >= 0) {
          focusedElements++;
        }
      }

      expect(focusedElements).toBeGreaterThan(0);
    });

    test('should have visible focus indicators', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      await page.keyboard.press('Tab');
      
      const focusIndicator = await page.evaluate(() => {
        const activeElement = document.activeElement;
        if (!activeElement) return null;
        
        const styles = window.getComputedStyle(activeElement);
        const pseudoStyles = window.getComputedStyle(activeElement, ':focus');
        
        return {
          outline: styles.outline,
          outlineWidth: styles.outlineWidth,
          outlineColor: styles.outlineColor,
          boxShadow: styles.boxShadow,
          border: styles.border,
          pseudoOutline: pseudoStyles.outline,
          pseudoBoxShadow: pseudoStyles.boxShadow,
        };
      });

      const hasVisibleFocus = 
        (focusIndicator?.outline && focusIndicator.outline !== 'none') ||
        (focusIndicator?.outlineWidth && focusIndicator.outlineWidth !== '0px') ||
        (focusIndicator?.boxShadow && focusIndicator.boxShadow !== 'none') ||
        (focusIndicator?.pseudoOutline && focusIndicator.pseudoOutline !== 'none') ||
        (focusIndicator?.pseudoBoxShadow && focusIndicator.pseudoBoxShadow !== 'none');

      expect(hasVisibleFocus).toBe(true);
    });

    test('should handle escape key properly', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Open a modal or bottom sheet if available
      const triggerSelector = '[data-testid="bottom-sheet-trigger"], [data-testid="modal-trigger"], button';
      const trigger = await page.locator(triggerSelector).first();
      
      if (await trigger.isVisible()) {
        await trigger.click();
        
        // Press escape
        await page.keyboard.press('Escape');
        
        // Verify modal/sheet is closed
        const modalOpen = await page.locator('[data-testid="modal"], [data-testid="bottom-sheet"]').isVisible();
        expect(modalOpen).toBe(false);
      }
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const headingStructure = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        const structure = headings.map(h => ({
          level: parseInt(h.tagName.charAt(1)),
          text: h.textContent?.trim(),
        }));
        
        // Check for proper hierarchy
        for (let i = 1; i < structure.length; i++) {
          if (structure[i].level > structure[i - 1].level + 1) {
            return {
              valid: false,
              violation: `Heading level jumps from h${structure[i - 1].level} to h${structure[i].level}`,
              structure,
            };
          }
        }
        
        return { valid: true, structure };
      });

      expect(headingStructure.valid, 
        `Invalid heading hierarchy: ${headingStructure.violation}`
      ).toBe(true);
      
      expect(headingStructure.structure.length).toBeGreaterThan(0);
    });

    test('should have proper ARIA labels and descriptions', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const ariaViolations = await page.evaluate(() => {
        const violations: any[] = [];
        
        // Check buttons without accessible names
        const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
        buttons.forEach((button, index) => {
          const hasAccessibleName = 
            button.textContent?.trim() ||
            button.getAttribute('aria-label') ||
            button.getAttribute('aria-labelledby') ||
            button.querySelector('img')?.getAttribute('alt');
          
          if (!hasAccessibleName) {
            violations.push({
              type: 'missing-accessible-name',
              element: 'button',
              index,
            });
          }
        });
        
        // Check form inputs without labels
        const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
        inputs.forEach((input, index) => {
          const id = input.id;
          const hasLabel = 
            document.querySelector(`label[for="${id}"]`) ||
            input.getAttribute('aria-label') ||
            input.getAttribute('aria-labelledby') ||
            input.getAttribute('aria-describedby');
          
          if (!hasLabel) {
            violations.push({
              type: 'missing-form-label',
              element: input.tagName,
              type_attr: (input as HTMLInputElement).type,
              index,
            });
          }
        });
        
        // Check images without alt text
        const images = Array.from(document.querySelectorAll('img'));
        images.forEach((img, index) => {
          const hasAltText = 
            img.getAttribute('alt') ||
            img.getAttribute('aria-label') ||
            img.getAttribute('role') === 'presentation' ||
            img.getAttribute('aria-hidden') === 'true';
          
          if (!hasAltText) {
            violations.push({
              type: 'missing-alt-text',
              element: 'img',
              src: img.src,
              index,
            });
          }
        });
        
        return violations;
      });

      expect(ariaViolations.length, 
        `ARIA violations found: ${JSON.stringify(ariaViolations, null, 2)}`
      ).toBe(0);
    });

    test('should announce dynamic content changes', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Look for ARIA live regions
      const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').count();
      
      // There should be at least one live region for dynamic content
      expect(liveRegions).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe('Color and Contrast', () => {
    test('should meet color contrast requirements', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      await accessibilityTester.validateColorContrast();
    });

    test('should not rely solely on color for information', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Check for color-only indicators
      const colorOnlyViolations = await page.evaluate(() => {
        const violations: any[] = [];
        
        // Look for elements that might use color-only communication
        const potentialElements = Array.from(document.querySelectorAll(
          '.error, .success, .warning, .info, [class*="color"], [style*="color"]'
        ));
        
        potentialElements.forEach((element, index) => {
          const hasNonColorIndicator = 
            element.textContent?.trim() ||
            element.querySelector('svg, img, icon') ||
            element.getAttribute('aria-label') ||
            element.getAttribute('title');
          
          if (!hasNonColorIndicator) {
            violations.push({
              type: 'color-only-communication',
              element: element.tagName,
              className: element.className,
              index,
            });
          }
        });
        
        return violations;
      });

      // This is a heuristic check - manual review may be needed
      expect(colorOnlyViolations.length).toBeLessThanOrEqual(3);
    });
  });

  test.describe('Mobile-Specific Accessibility', () => {
    test('should have proper viewport configuration', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const viewportMeta = await page.evaluate(() => {
        const viewport = document.querySelector('meta[name="viewport"]');
        return viewport ? viewport.getAttribute('content') : null;
      });

      expect(viewportMeta).toBeTruthy();
      expect(viewportMeta).toContain('width=device-width');
      expect(viewportMeta).not.toContain('user-scalable=no');
      expect(viewportMeta).not.toContain('maximum-scale=1');
    });

    test('should support zoom up to 200%', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      // Test zoom capability
      await page.evaluate(() => {
        document.body.style.zoom = '200%';
      });
      
      // Check if content is still accessible
      const isUsable = await page.evaluate(() => {
        const viewport = {
          width: window.innerWidth,
          height: window.innerHeight,
        };
        
        const buttons = Array.from(document.querySelectorAll('button'));
        const visibleButtons = buttons.filter(btn => {
          const rect = btn.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0 && 
                 rect.left >= 0 && rect.top >= 0 &&
                 rect.right <= viewport.width && rect.bottom <= viewport.height;
        });
        
        return visibleButtons.length > 0;
      });

      expect(isUsable).toBe(true);
      
      // Reset zoom
      await page.evaluate(() => {
        document.body.style.zoom = '100%';
      });
    });
  });

  test.describe('Comprehensive Accessibility Report', () => {
    test('should generate full accessibility report', async ({ page }) => {
      await page.goto('/mobile/dashboard');
      
      const report = await accessibilityTester.generateAccessibilityReport();
      
      // Log report for analysis
      console.log('Accessibility Report:', JSON.stringify(report, null, 2));
      
      expect(report.passed).toBe(true);
      expect(report.overallScore).toBeGreaterThanOrEqual(90);
      
      // Specific checks
      expect(report.wcag.passed).toBe(true);
      expect(report.touchTargets.passed).toBe(true);
      expect(report.keyboard.passed).toBe(true);
      expect(report.screenReader.passed).toBe(true);
      expect(report.mobile.passed).toBe(true);
    });
  });
});