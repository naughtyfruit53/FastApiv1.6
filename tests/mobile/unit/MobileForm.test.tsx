import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import MobileFormLayout from '../../../frontend/src/components/mobile/MobileFormLayout';

// Mock mobile detection hook
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ 
    isMobile: true,
    isTablet: false,
    touchCapable: true,
    orientation: 'portrait',
  }),
}));

// Mock react-hook-form
jest.mock('react-hook-form', () => ({
  useForm: () => ({
    register: jest.fn(),
    handleSubmit: jest.fn((fn) => fn),
    formState: { errors: {}, isSubmitting: false },
    setValue: jest.fn(),
    getValues: jest.fn(),
    watch: jest.fn(),
    reset: jest.fn(),
  }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('Mobile Form Components', () => {
  describe('MobileFormLayout', () => {
    const defaultProps = {
      title: 'Test Form',
      onSubmit: jest.fn(),
      onCancel: jest.fn(),
      children: (
        <div>
          <input type="text" placeholder="Name" data-testid="name-input" />
          <input type="email" placeholder="Email" data-testid="email-input" />
        </div>
      ),
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    describe('Basic Rendering and Layout', () => {
      it('renders form with title', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        expect(screen.getByText('Test Form')).toBeInTheDocument();
      });

      it('renders form children', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        expect(screen.getByTestId('name-input')).toBeInTheDocument();
        expect(screen.getByTestId('email-input')).toBeInTheDocument();
      });

      it('renders submit and cancel buttons', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      });

      it('applies mobile-optimized styling', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const form = screen.getByRole('form');
        const styles = window.getComputedStyle(form);
        
        // Should have mobile-friendly padding and spacing
        expect(styles.padding).toBeTruthy();
      });
    });

    describe('Form Interactions', () => {
      it('handles form submission', async () => {
        const mockSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onSubmit={mockSubmit} />
          </TestWrapper>
        );

        const submitButton = screen.getByRole('button', { name: /submit/i });
        fireEvent.click(submitButton);

        await waitFor(() => {
          expect(mockSubmit).toHaveBeenCalledTimes(1);
        });
      });

      it('handles form cancellation', async () => {
        const mockCancel = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onCancel={mockCancel} />
          </TestWrapper>
        );

        const cancelButton = screen.getByRole('button', { name: /cancel/i });
        fireEvent.click(cancelButton);

        expect(mockCancel).toHaveBeenCalledTimes(1);
      });

      it('shows loading state during submission', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} isSubmitting={true} />
          </TestWrapper>
        );

        const submitButton = screen.getByRole('button', { name: /submit/i });
        expect(submitButton).toBeDisabled();
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
    });

    describe('Touch and Gesture Support', () => {
      it('handles touch interactions on form fields', async () => {
        const user = userEvent.setup();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const nameInput = screen.getByTestId('name-input');
        
        await user.click(nameInput);
        await user.type(nameInput, 'John Doe');

        expect(nameInput).toHaveFocus();
        expect(nameInput).toHaveValue('John Doe');
      });

      it('supports swipe to dismiss on mobile', () => {
        const mockCancel = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onCancel={mockCancel} swipeToDismiss={true} />
          </TestWrapper>
        );

        const form = screen.getByRole('form');
        
        // Simulate swipe down gesture
        fireEvent.touchStart(form, {
          touches: [{ clientX: 150, clientY: 50 }],
        });

        fireEvent.touchMove(form, {
          touches: [{ clientX: 150, clientY: 200 }],
        });

        fireEvent.touchEnd(form);

        expect(mockCancel).toHaveBeenCalled();
      });

      it('handles virtual keyboard adjustments', () => {
        // Mock viewport height change (keyboard appearance)
        Object.defineProperty(window, 'visualViewport', {
          writable: true,
          value: { height: 400 }, // Reduced height simulating keyboard
        });

        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const form = screen.getByRole('form');
        fireEvent(window, new Event('resize'));

        // Form should adjust to keyboard presence
        expect(form).toHaveStyle({ paddingBottom: '20px' });
      });
    });

    describe('Accessibility Features', () => {
      it('has proper ARIA labels and roles', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const form = screen.getByRole('form');
        expect(form).toHaveAttribute('aria-label');
        
        const submitButton = screen.getByRole('button', { name: /submit/i });
        expect(submitButton).toHaveAttribute('aria-describedby');
      });

      it('supports keyboard navigation', async () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const nameInput = screen.getByTestId('name-input');
        const emailInput = screen.getByTestId('email-input');
        const submitButton = screen.getByRole('button', { name: /submit/i });

        // Tab through form elements
        nameInput.focus();
        fireEvent.keyDown(nameInput, { key: 'Tab' });
        
        await waitFor(() => {
          expect(emailInput).toHaveFocus();
        });

        fireEvent.keyDown(emailInput, { key: 'Tab' });
        
        await waitFor(() => {
          expect(submitButton).toHaveFocus();
        });
      });

      it('handles form submission with Enter key', async () => {
        const mockSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onSubmit={mockSubmit} />
          </TestWrapper>
        );

        const nameInput = screen.getByTestId('name-input');
        nameInput.focus();
        
        fireEvent.keyDown(nameInput, { key: 'Enter' });

        await waitFor(() => {
          expect(mockSubmit).toHaveBeenCalled();
        });
      });

      it('handles form cancellation with Escape key', async () => {
        const mockCancel = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onCancel={mockCancel} />
          </TestWrapper>
        );

        fireEvent.keyDown(document, { key: 'Escape' });

        expect(mockCancel).toHaveBeenCalled();
      });

      it('has adequate touch target sizes', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          const rect = button.getBoundingClientRect();
          expect(rect.height).toBeGreaterThanOrEqual(44); // WCAG minimum
        });
      });

      it('provides clear error messaging', () => {
        const errors = {
          name: { type: 'required', message: 'Name is required' },
          email: { type: 'invalid', message: 'Invalid email format' },
        };

        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} errors={errors} />
          </TestWrapper>
        );

        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Invalid email format')).toBeInTheDocument();
      });

      it('announces form state changes to screen readers', async () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        // Should have live regions for announcements
        const liveRegion = document.querySelector('[aria-live]');
        expect(liveRegion).toBeInTheDocument();
      });
    });

    describe('Form Validation', () => {
      it('validates required fields before submission', async () => {
        const mockSubmit = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout 
              {...defaultProps} 
              onSubmit={mockSubmit}
              validationRules={{
                name: { required: 'Name is required' },
                email: { required: 'Email is required' },
              }}
            />
          </TestWrapper>
        );

        const submitButton = screen.getByRole('button', { name: /submit/i });
        fireEvent.click(submitButton);

        await waitFor(() => {
          expect(screen.getByText('Name is required')).toBeInTheDocument();
          expect(screen.getByText('Email is required')).toBeInTheDocument();
          expect(mockSubmit).not.toHaveBeenCalled();
        });
      });

      it('validates field format in real-time', async () => {
        const user = userEvent.setup();
        
        render(
          <TestWrapper>
            <MobileFormLayout 
              {...defaultProps}
              validationRules={{
                email: { 
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email format'
                  }
                },
              }}
            />
          </TestWrapper>
        );

        const emailInput = screen.getByTestId('email-input');
        
        await user.click(emailInput);
        await user.type(emailInput, 'invalid-email');
        await user.tab(); // Trigger blur event

        await waitFor(() => {
          expect(screen.getByText('Invalid email format')).toBeInTheDocument();
        });
      });

      it('clears validation errors when fields are corrected', async () => {
        const user = userEvent.setup();
        
        render(
          <TestWrapper>
            <MobileFormLayout 
              {...defaultProps}
              errors={{ email: { type: 'invalid', message: 'Invalid email format' } }}
            />
          </TestWrapper>
        );

        expect(screen.getByText('Invalid email format')).toBeInTheDocument();

        const emailInput = screen.getByTestId('email-input');
        await user.clear(emailInput);
        await user.type(emailInput, 'valid@example.com');

        await waitFor(() => {
          expect(screen.queryByText('Invalid email format')).not.toBeInTheDocument();
        });
      });
    });

    describe('Mobile-Specific Features', () => {
      it('adjusts layout for different screen orientations', () => {
        // Test portrait orientation
        Object.defineProperty(window.screen, 'orientation', {
          writable: true,
          value: { angle: 0 },
        });

        const { rerender } = render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        let form = screen.getByRole('form');
        expect(form).toHaveClass('portrait-layout');

        // Test landscape orientation
        Object.defineProperty(window.screen, 'orientation', {
          value: { angle: 90 },
        });

        rerender(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        form = screen.getByRole('form');
        expect(form).toHaveClass('landscape-layout');
      });

      it('handles pull-to-refresh on form', () => {
        const mockRefresh = jest.fn();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} onRefresh={mockRefresh} />
          </TestWrapper>
        );

        const form = screen.getByRole('form');
        
        // Simulate pull down gesture at top of form
        fireEvent.touchStart(form, {
          touches: [{ clientX: 150, clientY: 10 }],
        });

        fireEvent.touchMove(form, {
          touches: [{ clientX: 150, clientY: 100 }],
        });

        fireEvent.touchEnd(form);

        expect(mockRefresh).toHaveBeenCalled();
      });

      it('optimizes input types for mobile keyboards', () => {
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps}>
              <input type="tel" data-testid="phone-input" />
              <input type="number" data-testid="number-input" />
              <input type="url" data-testid="url-input" />
            </MobileFormLayout>
          </TestWrapper>
        );

        expect(screen.getByTestId('phone-input')).toHaveAttribute('type', 'tel');
        expect(screen.getByTestId('number-input')).toHaveAttribute('type', 'number');
        expect(screen.getByTestId('url-input')).toHaveAttribute('type', 'url');
      });
    });

    describe('Performance and Edge Cases', () => {
      it('handles rapid form interactions without lag', async () => {
        const user = userEvent.setup();
        
        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        const nameInput = screen.getByTestId('name-input');
        
        // Rapid typing simulation
        const startTime = performance.now();
        await user.type(nameInput, 'Quick brown fox jumps over lazy dog');
        const endTime = performance.now();
        
        expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
      });

      it('handles network connectivity issues gracefully', () => {
        // Mock offline state
        Object.defineProperty(navigator, 'onLine', {
          writable: true,
          value: false,
        });

        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps} />
          </TestWrapper>
        );

        expect(screen.getByText(/offline mode/i)).toBeInTheDocument();
        
        const submitButton = screen.getByRole('button', { name: /submit/i });
        expect(submitButton).toBeDisabled();
      });

      it('recovers gracefully from JavaScript errors', () => {
        // Mock console error to test error boundaries
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        
        const ThrowError = () => {
          throw new Error('Test error');
        };

        render(
          <TestWrapper>
            <MobileFormLayout {...defaultProps}>
              <ThrowError />
            </MobileFormLayout>
          </TestWrapper>
        );

        expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
        
        consoleSpy.mockRestore();
      });
    });
  });
});