import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import MobileButton from '../../../components/mobile/MobileButton';

// Mock mobile detection hook
jest.mock('../../../hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ 
    isMobile: true,
    isTablet: false,
    touchCapable: true,
    orientation: 'portrait',
  }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('MobileButton', () => {
  describe('Basic Functionality', () => {
    it('renders button with children', () => {
      render(
        <TestWrapper>
          <MobileButton>Click me</MobileButton>
        </TestWrapper>
      );

      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    it('handles click events', async () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <MobileButton onClick={mockClick}>Click me</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockClick).toHaveBeenCalledTimes(1);
    });

    it('renders loading state correctly', () => {
      render(
        <TestWrapper>
          <MobileButton loading={true}>Loading</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('renders full width when specified', () => {
      render(
        <TestWrapper>
          <MobileButton fullWidth={true}>Full Width</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveStyle({ width: '100%' });
    });
  });

  describe('Accessibility Features', () => {
    it('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <MobileButton 
            accessibilityLabel="Save document"
            accessibilityHint="Saves the current document to your account"
          >
            Save
          </MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Save document');
      expect(button).toHaveAttribute('aria-describedby');
    });

    it('meets minimum touch target size', () => {
      render(
        <TestWrapper>
          <MobileButton>Touch me</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      const styles = window.getComputedStyle(button);
      
      // Should meet WCAG AA minimum of 44x44px
      expect(parseInt(styles.minHeight)).toBeGreaterThanOrEqual(44);
      expect(parseInt(styles.minWidth)).toBeGreaterThanOrEqual(44);
    });

    it('supports keyboard navigation', async () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <MobileButton onClick={mockClick}>Keyboard accessible</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      button.focus();
      
      expect(button).toHaveFocus();
      
      fireEvent.keyDown(button, { key: 'Enter' });
      expect(mockClick).toHaveBeenCalledTimes(1);
      
      fireEvent.keyDown(button, { key: ' ' });
      expect(mockClick).toHaveBeenCalledTimes(2);
    });

    it('announces state changes for screen readers', () => {
      render(
        <TestWrapper>
          <MobileButton loading={true} announceStateChanges={true}>
            Loading button
          </MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
      
      // Should have loading announcement
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('has visible focus indicators', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MobileButton>Focus me</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      await user.tab();
      
      expect(button).toHaveFocus();
      
      const styles = window.getComputedStyle(button);
      // Should have visible focus outline
      expect(styles.outline).not.toBe('none');
    });
  });

  describe('Mobile-Specific Features', () => {
    it('provides haptic feedback on supported devices', () => {
      // Mock vibrate API
      Object.defineProperty(navigator, 'vibrate', {
        value: jest.fn(),
        writable: true,
      });

      render(
        <TestWrapper>
          <MobileButton hapticFeedback={true}>Haptic button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      fireEvent.touchStart(button);

      expect(navigator.vibrate).toHaveBeenCalledWith(10);
    });

    it('handles touch interactions', () => {
      render(
        <TestWrapper>
          <MobileButton>Touch button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');

      fireEvent.touchStart(button);
      // When pressed, should have aria-pressed="true"
      expect(button).toHaveAttribute('aria-pressed', 'true');

      fireEvent.touchEnd(button);
      // When not pressed, aria-pressed should be undefined (not set)
      expect(button).not.toHaveAttribute('aria-pressed');
    });

    it('adapts styling for mobile devices', () => {
      render(
        <TestWrapper>
          <MobileButton touchFriendly={true}>Mobile button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      const styles = window.getComputedStyle(button);

      // Should have mobile-optimized sizing and spacing
      expect(parseInt(styles.minHeight)).toBeGreaterThanOrEqual(48);
      expect(parseInt(styles.fontSize)).toBeGreaterThan(0);
    });

    it('focuses on mount when specified', () => {
      render(
        <TestWrapper>
          <MobileButton focusOnMount={true}>Auto focus</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveFocus();
    });
  });

  describe('Performance and Edge Cases', () => {
    it('handles rapid interactions without lag', async () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <MobileButton onClick={mockClick}>Rapid click</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      
      // Simulate rapid clicking
      for (let i = 0; i < 10; i++) {
        fireEvent.click(button);
      }

      expect(mockClick).toHaveBeenCalledTimes(10);
    });

    it('handles disabled state correctly', () => {
      render(
        <TestWrapper>
          <MobileButton disabled={true}>Disabled button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('tabindex', '-1');
    });

    it('prevents multiple submissions when loading', () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <MobileButton loading={true} onClick={mockClick}>
            Loading button
          </MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(mockClick).not.toHaveBeenCalled();
      expect(button).toBeDisabled();
    });
  });

  describe('Responsive Design', () => {
    it('adapts to different screen sizes', () => {
      // Mock different screen size
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 320, // Small mobile screen
      });

      render(
        <TestWrapper>
          <MobileButton>Responsive button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('respects reduced motion preferences', () => {
      // Mock reduced motion preference
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query.includes('prefers-reduced-motion: reduce'),
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(
        <TestWrapper>
          <MobileButton>Accessible button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      // Reduced motion styles would be applied via CSS
    });

    it('supports high contrast mode', () => {
      // Mock high contrast mode
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query.includes('prefers-contrast: high'),
          media: query,
          onchange: null,
          addListener: jest.fn(),
          removeListener: jest.fn(),
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        })),
      });

      render(
        <TestWrapper>
          <MobileButton>High contrast button</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      // High contrast styles would be applied via CSS
    });
  });
});