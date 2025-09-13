/**
 * Mobile Accessibility Testing Utilities
 * Provides tools for automated and manual accessibility validation
 */

import { test, expect, Page } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from 'axe-playwright';

export interface AccessibilityTestOptions {
  includeTags?: string[];
  excludeTags?: string[];
  rules?: Record<string, { enabled: boolean }>;
  detailedReport?: boolean;
}

export class MobileAccessibilityTester {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Initialize accessibility testing on the page
   */
  async initialize(): Promise<void> {
    await injectAxe(this.page);
  }

  /**
   * Run comprehensive WCAG 2.1 AA compliance check
   */
  async runWCAGComplianceCheck(options: AccessibilityTestOptions = {}): Promise<void> {
    const defaultOptions = {
      includeTags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
      detailedReport: true,
      detailedReportOptions: { html: true },
      ...options,
    };

    await checkA11y(this.page, null, defaultOptions);
  }

  /**
   * Test touch target sizes (minimum 44x44px)
   */
  async validateTouchTargets(): Promise<{ passed: boolean; violations: any[] }> {
    const violations = await this.page.evaluate(() => {
      const touchTargets = document.querySelectorAll('button, a, input, [role="button"], [tabindex]');
      const violations: any[] = [];

      touchTargets.forEach((element, index) => {
        const rect = element.getBoundingClientRect();
        const computedStyle = window.getComputedStyle(element);
        
        // Skip hidden elements
        if (rect.width === 0 || rect.height === 0 || computedStyle.display === 'none') {
          return;
        }

        const minSize = 44;
        if (rect.width < minSize || rect.height < minSize) {
          violations.push({
            element: element.tagName,
            selector: element.id ? `#${element.id}` : `${element.tagName}:nth-child(${index + 1})`,
            size: { width: rect.width, height: rect.height },
            expected: { width: minSize, height: minSize },
            text: element.textContent?.trim() || 'No text content',
          });
        }
      });

      return violations;
    });

    return {
      passed: violations.length === 0,
      violations,
    };
  }

  /**
   * Test color contrast ratios
   */
  async validateColorContrast(): Promise<void> {
    await checkA11y(this.page, null, {
      rules: {
        'color-contrast': { enabled: true },
        'color-contrast-enhanced': { enabled: true },
      },
    });
  }

  /**
   * Test keyboard navigation accessibility
   */
  async validateKeyboardNavigation(): Promise<{ passed: boolean; issues: string[] }> {
    const issues: string[] = [];

    // Test Tab navigation
    await this.page.keyboard.press('Tab');
    const firstFocused = await this.page.evaluate(() => document.activeElement?.tagName);
    
    if (!firstFocused || !['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(firstFocused)) {
      issues.push('First tab stop is not a focusable element');
    }

    // Test focus indicators
    const focusIndicatorVisible = await this.page.evaluate(() => {
      const activeElement = document.activeElement;
      if (!activeElement) return false;
      
      const styles = window.getComputedStyle(activeElement);
      return (
        styles.outline !== 'none' ||
        styles.outlineWidth !== '0px' ||
        styles.boxShadow !== 'none'
      );
    });

    if (!focusIndicatorVisible) {
      issues.push('No visible focus indicator on focused element');
    }

    // Test Escape key behavior
    await this.page.keyboard.press('Escape');
    
    return {
      passed: issues.length === 0,
      issues,
    };
  }

  /**
   * Test screen reader compatibility
   */
  async validateScreenReaderSupport(): Promise<{ passed: boolean; issues: string[] }> {
    const issues: string[] = [];

    // Check for proper heading structure
    const headingStructure = await this.page.evaluate(() => {
      const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
      const levels = headings.map(h => parseInt(h.tagName.charAt(1)));
      
      for (let i = 1; i < levels.length; i++) {
        if (levels[i] > levels[i - 1] + 1) {
          return false;
        }
      }
      return true;
    });

    if (!headingStructure) {
      issues.push('Improper heading hierarchy detected');
    }

    // Check for missing alt text on images
    const imagesWithoutAlt = await this.page.evaluate(() => {
      const images = Array.from(document.querySelectorAll('img'));
      return images.filter(img => !img.alt && !img.getAttribute('aria-label')).length;
    });

    if (imagesWithoutAlt > 0) {
      issues.push(`${imagesWithoutAlt} images missing alt text`);
    }

    // Check for form labels
    const unlabeledInputs = await this.page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
      return inputs.filter(input => {
        const id = input.id;
        const label = document.querySelector(`label[for="${id}"]`);
        const ariaLabel = input.getAttribute('aria-label');
        const ariaLabelledBy = input.getAttribute('aria-labelledby');
        
        return !label && !ariaLabel && !ariaLabelledBy;
      }).length;
    });

    if (unlabeledInputs > 0) {
      issues.push(`${unlabeledInputs} form inputs missing labels`);
    }

    return {
      passed: issues.length === 0,
      issues,
    };
  }

  /**
   * Test mobile-specific accessibility features
   */
  async validateMobileAccessibility(): Promise<{ passed: boolean; issues: string[] }> {
    const issues: string[] = [];

    // Test viewport meta tag
    const hasViewportMeta = await this.page.evaluate(() => {
      const viewport = document.querySelector('meta[name="viewport"]');
      return !!viewport && viewport.getAttribute('content')?.includes('width=device-width');
    });

    if (!hasViewportMeta) {
      issues.push('Missing or incorrect viewport meta tag');
    }

    // Test for zoom constraints
    const hasZoomConstraints = await this.page.evaluate(() => {
      const viewport = document.querySelector('meta[name="viewport"]');
      const content = viewport?.getAttribute('content') || '';
      return content.includes('user-scalable=no') || content.includes('maximum-scale=1');
    });

    if (hasZoomConstraints) {
      issues.push('Zoom is disabled - accessibility violation');
    }

    // Test touch target spacing
    const touchTargetSpacing = await this.page.evaluate(() => {
      const interactiveElements = Array.from(document.querySelectorAll('button, a, input, [role="button"]'));
      const violations: any[] = [];

      for (let i = 0; i < interactiveElements.length; i++) {
        const current = interactiveElements[i].getBoundingClientRect();
        
        for (let j = i + 1; j < interactiveElements.length; j++) {
          const other = interactiveElements[j].getBoundingClientRect();
          
          const distance = Math.sqrt(
            Math.pow(current.x - other.x, 2) + Math.pow(current.y - other.y, 2)
          );
          
          if (distance < 8 && distance > 0) { // 8px minimum spacing
            violations.push({
              element1: interactiveElements[i].tagName,
              element2: interactiveElements[j].tagName,
              distance,
            });
          }
        }
      }

      return violations;
    });

    if (touchTargetSpacing.length > 0) {
      issues.push(`${touchTargetSpacing.length} touch target spacing violations`);
    }

    return {
      passed: issues.length === 0,
      issues,
    };
  }

  /**
   * Generate comprehensive accessibility report
   */
  async generateAccessibilityReport(): Promise<AccessibilityReport> {
    const wcagResults = await this.runComprehensiveWCAGCheck();
    const touchTargets = await this.validateTouchTargets();
    const keyboard = await this.validateKeyboardNavigation();
    const screenReader = await this.validateScreenReaderSupport();
    const mobile = await this.validateMobileAccessibility();

    const overallScore = this.calculateAccessibilityScore([
      wcagResults.passed,
      touchTargets.passed,
      keyboard.passed,
      screenReader.passed,
      mobile.passed,
    ]);

    return {
      timestamp: new Date().toISOString(),
      url: this.page.url(),
      overallScore,
      passed: overallScore >= 90,
      wcag: wcagResults,
      touchTargets,
      keyboard,
      screenReader,
      mobile,
      recommendations: this.generateRecommendations({
        wcagResults,
        touchTargets,
        keyboard,
        screenReader,
        mobile,
      }),
    };
  }

  private async runComprehensiveWCAGCheck(): Promise<{ passed: boolean; violations: any[] }> {
    try {
      await this.runWCAGComplianceCheck();
      return { passed: true, violations: [] };
    } catch (error) {
      const violations = await getViolations(this.page);
      return { passed: false, violations };
    }
  }

  private calculateAccessibilityScore(results: boolean[]): number {
    const passedCount = results.filter(Boolean).length;
    return Math.round((passedCount / results.length) * 100);
  }

  private generateRecommendations(results: any): string[] {
    const recommendations: string[] = [];

    if (!results.touchTargets.passed) {
      recommendations.push('Increase touch target sizes to minimum 44x44px');
    }

    if (!results.keyboard.passed) {
      recommendations.push('Implement visible focus indicators and proper keyboard navigation');
    }

    if (!results.screenReader.passed) {
      recommendations.push('Add missing ARIA labels and improve semantic markup');
    }

    if (!results.mobile.passed) {
      recommendations.push('Fix mobile-specific accessibility issues (viewport, touch spacing)');
    }

    return recommendations;
  }
}

// Types
export interface AccessibilityReport {
  timestamp: string;
  url: string;
  overallScore: number;
  passed: boolean;
  wcag: { passed: boolean; violations: any[] };
  touchTargets: { passed: boolean; violations: any[] };
  keyboard: { passed: boolean; issues: string[] };
  screenReader: { passed: boolean; issues: string[] };
  mobile: { passed: boolean; issues: string[] };
  recommendations: string[];
}