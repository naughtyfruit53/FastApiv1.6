/**
 * Accessibility Helper Utilities
 * 
 * Provides utilities for improving accessibility and WCAG compliance.
 */

/**
 * Check if color contrast meets WCAG AA standards
 * @param foreground - Foreground color (hex or rgb)
 * @param background - Background color (hex or rgb)
 * @returns Object with contrast ratio and compliance status
 */
export function checkColorContrast(
  foreground: string,
  background: string
): { ratio: number; isAA: boolean; isAAA: boolean } {
  const rgb1 = hexToRgb(foreground);
  const rgb2 = hexToRgb(background);

  if (!rgb1 || !rgb2) {
    return { ratio: 0, isAA: false, isAAA: false };
  }

  const l1 = getRelativeLuminance(rgb1);
  const l2 = getRelativeLuminance(rgb2);

  const ratio = l1 > l2 ? (l1 + 0.05) / (l2 + 0.05) : (l2 + 0.05) / (l1 + 0.05);

  return {
    ratio: Math.round(ratio * 100) / 100,
    isAA: ratio >= 4.5, // WCAG AA for normal text
    isAAA: ratio >= 7, // WCAG AAA for normal text
  };
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  // Remove # if present
  hex = hex.replace(/^#/, '');

  // Parse hex values
  if (hex.length === 3) {
    hex = hex
      .split('')
      .map(char => char + char)
      .join('');
  }

  if (hex.length !== 6) {
    return null;
  }

  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  return { r, g, b };
}

/**
 * Calculate relative luminance
 */
function getRelativeLuminance(rgb: { r: number; g: number; b: number }): number {
  const rsRGB = rgb.r / 255;
  const gsRGB = rgb.g / 255;
  const bsRGB = rgb.b / 255;

  const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
  const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
  const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/**
 * Generate ARIA label for buttons
 */
export function generateAriaLabel(
  action: string,
  context?: string,
  additionalInfo?: string
): string {
  const parts = [action];
  if (context) parts.push(context);
  if (additionalInfo) parts.push(additionalInfo);
  return parts.join(' - ');
}

/**
 * Add keyboard navigation support
 */
export function handleKeyboardNavigation(
  event: React.KeyboardEvent,
  onSelect: () => void,
  onEscape?: () => void
): void {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    onSelect();
  } else if (event.key === 'Escape' && onEscape) {
    event.preventDefault();
    onEscape();
  }
}

/**
 * Create skip link for keyboard navigation
 */
export function createSkipLink(targetId: string, label: string = 'Skip to main content'): {
  href: string;
  label: string;
  onClick: (e: React.MouseEvent) => void;
} {
  return {
    href: `#${targetId}`,
    label,
    onClick: (e: React.MouseEvent) => {
      e.preventDefault();
      const target = document.getElementById(targetId);
      if (target) {
        target.focus();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },
  };
}

/**
 * Manage focus trap for modals
 */
export class FocusTrap {
  private container: HTMLElement;
  private firstFocusableElement: HTMLElement | null = null;
  private lastFocusableElement: HTMLElement | null = null;
  private previousActiveElement: HTMLElement | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
    this.updateFocusableElements();
  }

  activate(): void {
    this.previousActiveElement = document.activeElement as HTMLElement;
    this.updateFocusableElements();

    // Focus first element
    if (this.firstFocusableElement) {
      this.firstFocusableElement.focus();
    }

    // Add event listener
    this.container.addEventListener('keydown', this.handleKeyDown);
  }

  deactivate(): void {
    this.container.removeEventListener('keydown', this.handleKeyDown);

    // Restore focus to previous element
    if (this.previousActiveElement) {
      this.previousActiveElement.focus();
    }
  }

  private updateFocusableElements(): void {
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    const focusableElements = Array.from(
      this.container.querySelectorAll<HTMLElement>(focusableSelectors)
    );

    this.firstFocusableElement = focusableElements[0] || null;
    this.lastFocusableElement = focusableElements[focusableElements.length - 1] || null;
  }

  private handleKeyDown = (event: KeyboardEvent): void => {
    if (event.key !== 'Tab') return;

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusableElement) {
        event.preventDefault();
        this.lastFocusableElement?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusableElement) {
        event.preventDefault();
        this.firstFocusableElement?.focus();
      }
    }
  };
}

/**
 * Announce message to screen readers
 */
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Check if reduced motion is preferred
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get accessible animation duration
 */
export function getAccessibleAnimationDuration(defaultDuration: number): number {
  return prefersReducedMotion() ? 0 : defaultDuration;
}

/**
 * Validate form field for accessibility
 */
export interface FieldAccessibility {
  hasLabel: boolean;
  hasAriaLabel: boolean;
  hasPlaceholder: boolean;
  hasErrorMessage: boolean;
  isAccessible: boolean;
  issues: string[];
}

export function validateFieldAccessibility(field: HTMLInputElement): FieldAccessibility {
  const issues: string[] = [];
  const hasLabel = !!field.labels?.length;
  const hasAriaLabel = !!field.getAttribute('aria-label') || !!field.getAttribute('aria-labelledby');
  const hasPlaceholder = !!field.placeholder;
  const hasErrorMessage = !!field.getAttribute('aria-describedby') || !!field.getAttribute('aria-errormessage');

  if (!hasLabel && !hasAriaLabel) {
    issues.push('Field is missing a label or aria-label');
  }

  if (field.required && !field.getAttribute('aria-required')) {
    issues.push('Required field is missing aria-required attribute');
  }

  if (field.getAttribute('aria-invalid') === 'true' && !hasErrorMessage) {
    issues.push('Invalid field is missing error message');
  }

  return {
    hasLabel,
    hasAriaLabel,
    hasPlaceholder,
    hasErrorMessage,
    isAccessible: issues.length === 0,
    issues,
  };
}

/**
 * Create accessible error message ID
 */
export function createErrorId(fieldId: string): string {
  return `${fieldId}-error`;
}

/**
 * Create accessible description ID
 */
export function createDescriptionId(fieldId: string): string {
  return `${fieldId}-description`;
}

export default {
  checkColorContrast,
  generateAriaLabel,
  handleKeyboardNavigation,
  createSkipLink,
  FocusTrap,
  announceToScreenReader,
  prefersReducedMotion,
  getAccessibleAnimationDuration,
  validateFieldAccessibility,
  createErrorId,
  createDescriptionId,
};
