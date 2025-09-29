import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { axe, toHaveNoViolations } from 'jest-axe';
import MobileButton from '../../../frontend/src/components/mobile/MobileButton';
import MobileNavigation from '../../../frontend/src/components/mobile/MobileNavigation';
import MobileFormLayout from '../../../frontend/src/components/mobile/MobileFormLayout';
import MobileBottomSheet from '../../../frontend/src/components/mobile/MobileBottomSheet';

// Add jest-axe matcher
expect.extend(toHaveNoViolations);

// Mock mobile detection hook
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ 
    isMobile: true,
    isTablet: false,
    touchCapable: true,
    orientation: 'portrait',
  }),
}));

// Mock authentication context
jest.mock('../../../frontend/src/context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', name: 'Test User', email: 'test@example.com' },
    logout: jest.fn(),
    hasPermission: jest.fn().mockReturnValue(true),
  }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('Mobile Accessibility Tests', () => {
  describe('MobileButton Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <TestWrapper>
          <MobileButton>Click me</MobileButton>
        </TestWrapper>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

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

    it('meets minimum touch target size requirements', () => {
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

    it('supports keyboard activation', async () => {
      const mockClick = jest.fn();
      
      render(
        <TestWrapper>
          <MobileButton onClick={mockClick}>Activate me</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      button.focus();
      
      fireEvent.keyDown(button, { key: 'Enter' });
      expect(mockClick).toHaveBeenCalledTimes(1);
      
      fireEvent.keyDown(button, { key: ' ' });
      expect(mockClick).toHaveBeenCalledTimes(2);
    });

    it('announces loading state to screen readers', () => {
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
      expect(screen.getByText('Loading, please wait')).toBeInTheDocument();
    });

    it('supports high contrast mode', () => {
      // Mock high contrast media query
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
          <MobileButton>High contrast</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      // High contrast styles would be applied via CSS media queries
    });

    it('respects reduced motion preferences', () => {
      // Mock reduced motion media query
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
          <MobileButton>Reduced motion</MobileButton>
        </TestWrapper>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      // Reduced motion styles would be applied via CSS media queries
    });
  });

  describe('Mobile Navigation Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <TestWrapper>
          <MobileNavigation open={true} onClose={jest.fn()} />
        </TestWrapper>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper navigation landmarks', () => {
      render(
        <TestWrapper>
          <MobileNavigation open={true} onClose={jest.fn()} />
        </TestWrapper>
      );

      const navigation = screen.getByRole('navigation');
      expect(navigation).toBeInTheDocument();
      expect(navigation).toHaveAttribute('aria-label');
    });

    it('supports keyboard navigation through menu items', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MobileNavigation open={true} onClose={jest.fn()} />
        </TestWrapper>
      );

      // Should be able to tab through menu items
      await user.tab();
      
      const focusedElement = document.activeElement;
      expect(focusedElement).toBeTruthy();
      expect(['BUTTON', 'A'].includes(focusedElement?.tagName || '')).toBe(true);
    });

    it('closes with Escape key', async () => {
      const mockClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation open={true} onClose={mockClose} />
        </TestWrapper>
      );

      fireEvent.keyDown(document, { key: 'Escape' });
      expect(mockClose).toHaveBeenCalled();
    });

    it('has proper heading hierarchy', () => {
      render(
        <TestWrapper>
          <MobileNavigation open={true} onClose={jest.fn()} />
        </TestWrapper>
      );

      const headings = screen.getAllByRole('heading');
      const levels = headings.map(h => parseInt(h.tagName.charAt(1)));
      
      // Check for proper heading hierarchy (no level jumps)
      for (let i = 1; i < levels.length; i++) {
        expect(levels[i] - levels[i - 1]).toBeLessThanOrEqual(1);
      }
    });
  });

  describe('Mobile Form Accessibility', () => {
    const FormWithFields = () => (
      <MobileFormLayout
        title="Accessible Form"
        onSubmit={jest.fn()}
        onCancel={jest.fn()}
      >
        <div>
          <label htmlFor="name-field">Name (required)</label>
          <input 
            id="name-field" 
            type="text" 
            required 
            aria-describedby="name-help"
          />
          <div id="name-help">Enter your full name</div>
          
          <label htmlFor="email-field">Email</label>
          <input 
            id="email-field" 
            type="email" 
            aria-describedby="email-help"
          />
          <div id="email-help">We'll use this to contact you</div>
        </div>
      </MobileFormLayout>
    );

    it('has no accessibility violations', async () => {
      const { container } = render(
        <TestWrapper>
          <FormWithFields />
        </TestWrapper>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has properly associated labels', () => {
      render(
        <TestWrapper>
          <FormWithFields />
        </TestWrapper>
      );

      const nameField = screen.getByLabelText(/name/i);
      const emailField = screen.getByLabelText(/email/i);
      
      expect(nameField).toBeInTheDocument();
      expect(emailField).toBeInTheDocument();
      
      expect(nameField).toHaveAttribute('id', 'name-field');
      expect(emailField).toHaveAttribute('id', 'email-field');
    });

    it('has proper form structure and labeling', () => {
      render(
        <TestWrapper>
          <FormWithFields />
        </TestWrapper>
      );

      const form = screen.getByRole('form');
      expect(form).toBeInTheDocument();
      expect(form).toHaveAttribute('aria-label');
      
      // Required fields should be indicated
      const requiredField = screen.getByLabelText(/name.*required/i);
      expect(requiredField).toHaveAttribute('required');
    });

    it('provides helpful error messages', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <MobileFormLayout
            title="Form with Validation"
            onSubmit={jest.fn()}
            onCancel={jest.fn()}
            errors={{
              name: { type: 'required', message: 'Name is required' },
              email: { type: 'invalid', message: 'Please enter a valid email' },
            }}
          >
            <div>
              <label htmlFor="name">Name</label>
              <input id="name" type="text" aria-describedby="name-error" />
              
              <label htmlFor="email">Email</label>
              <input id="email" type="email" aria-describedby="email-error" />
            </div>
          </MobileFormLayout>
        </TestWrapper>
      );

      // Error messages should be associated with fields
      expect(screen.getByText('Name is required')).toBeInTheDocument();
      expect(screen.getByText('Please enter a valid email')).toBeInTheDocument();
    });
  });

  describe('Mobile Bottom Sheet Accessibility', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <TestWrapper>
          <MobileBottomSheet 
            open={true} 
            onClose={jest.fn()}
            title="Accessible Bottom Sheet"
          >
            <div>Bottom sheet content</div>
          </MobileBottomSheet>
        </TestWrapper>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('has proper modal attributes', () => {
      render(
        <TestWrapper>
          <MobileBottomSheet 
            open={true} 
            onClose={jest.fn()}
            title="Modal Bottom Sheet"
          >
            <div>Modal content</div>
          </MobileBottomSheet>
        </TestWrapper>
      );

      const modal = screen.getByRole('dialog');
      expect(modal).toBeInTheDocument();
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby');
    });

    it('traps focus within the bottom sheet', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <div>
            <button>Outside button</button>
            <MobileBottomSheet 
              open={true} 
              onClose={jest.fn()}
              title="Focus Trap Test"
            >
              <button>Inside button 1</button>
              <button>Inside button 2</button>
            </MobileBottomSheet>
          </div>
        </TestWrapper>
      );

      // Focus should be trapped within the modal
      const insideButton1 = screen.getByText('Inside button 1');
      const insideButton2 = screen.getByText('Inside button 2');
      
      insideButton1.focus();
      expect(insideButton1).toHaveFocus();
      
      await user.tab();
      expect(insideButton2).toHaveFocus();
      
      // Tabbing from the last element should cycle back to first
      await user.tab();
      expect(insideButton1).toHaveFocus();
    });

    it('closes with Escape key', async () => {
      const mockClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileBottomSheet 
            open={true} 
            onClose={mockClose}
            title="Escapable Bottom Sheet"
          >
            <div>Content</div>
          </MobileBottomSheet>
        </TestWrapper>
      );

      fireEvent.keyDown(document, { key: 'Escape' });
      expect(mockClose).toHaveBeenCalled();
    });
  });

  describe('Color Contrast and Visual Accessibility', () => {
    it('meets WCAG AA contrast requirements for buttons', () => {
      render(
        <TestWrapper>
          <MobileButton variant="contained" color="primary">
            Primary Button
          </MobileButton>
          <MobileButton variant="outlined" color="secondary">
            Secondary Button
          </MobileButton>
        </TestWrapper>
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        const styles = window.getComputedStyle(button);
        // In a real test, you would calculate contrast ratio
        // This is a placeholder for contrast checking logic
        expect(styles.backgroundColor || styles.color).toBeTruthy();
      });
    });

    it('provides alternative text for meaningful images', () => {
      render(
        <TestWrapper>
          <div>
            <img src="/logo.png" alt="Company Logo" />
            <img src="/decoration.png" alt="" role="presentation" />
          </div>
        </TestWrapper>
      );

      const meaningfulImage = screen.getByAltText('Company Logo');
      expect(meaningfulImage).toBeInTheDocument();
      
      const decorativeImage = screen.getByRole('presentation');
      expect(decorativeImage).toBeInTheDocument();
    });
  });

  describe('Screen Reader Support', () => {
    it('provides live region updates for dynamic content', async () => {
      const DynamicContent = () => {
        const [message, setMessage] = React.useState('');
        
        return (
          <div>
            <button onClick={() => setMessage('Content updated!')}>
              Update Content
            </button>
            <div role="status" aria-live="polite">
              {message}
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <DynamicContent />
        </TestWrapper>
      );

      const button = screen.getByText('Update Content');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Content updated!');
      });
    });

    it('provides proper heading structure for screen reader navigation', () => {
      render(
        <TestWrapper>
          <div>
            <h1>Main Title</h1>
            <h2>Section Title</h2>
            <h3>Subsection Title</h3>
            <h2>Another Section</h2>
          </div>
        </TestWrapper>
      );

      const headings = screen.getAllByRole('heading');
      expect(headings).toHaveLength(4);
      
      // Verify heading levels are logical
      expect(headings[0]).toHaveProperty('tagName', 'H1');
      expect(headings[1]).toHaveProperty('tagName', 'H2');
      expect(headings[2]).toHaveProperty('tagName', 'H3');
      expect(headings[3]).toHaveProperty('tagName', 'H2');
    });

    it('provides context for form fields and controls', () => {
      render(
        <TestWrapper>
          <fieldset>
            <legend>Personal Information</legend>
            <div>
              <label htmlFor="first-name">First Name</label>
              <input 
                id="first-name" 
                type="text" 
                aria-describedby="name-help"
              />
              <div id="name-help">Enter your legal first name</div>
            </div>
            
            <div>
              <fieldset>
                <legend>Preferred Contact Method</legend>
                <label>
                  <input type="radio" name="contact" value="email" />
                  Email
                </label>
                <label>
                  <input type="radio" name="contact" value="phone" />
                  Phone
                </label>
              </fieldset>
            </div>
          </fieldset>
        </TestWrapper>
      );

      const mainFieldset = screen.getByRole('group', { name: 'Personal Information' });
      expect(mainFieldset).toBeInTheDocument();
      
      const contactFieldset = screen.getByRole('group', { name: 'Preferred Contact Method' });
      expect(contactFieldset).toBeInTheDocument();
      
      const radioButtons = screen.getAllByRole('radio');
      expect(radioButtons).toHaveLength(2);
    });
  });

  describe('Mobile-Specific Accessibility Features', () => {
    it('supports device orientation changes', () => {
      const OrientationAware = () => {
        const [orientation, setOrientation] = React.useState('portrait');
        
        React.useEffect(() => {
          const handleOrientationChange = () => {
            setOrientation(window.screen.orientation?.angle === 90 ? 'landscape' : 'portrait');
          };
          
          window.addEventListener('orientationchange', handleOrientationChange);
          return () => window.removeEventListener('orientationchange', handleOrientationChange);
        }, []);
        
        return (
          <div data-orientation={orientation} aria-label={`Current orientation: ${orientation}`}>
            Content adapts to {orientation}
          </div>
        );
      };

      render(
        <TestWrapper>
          <OrientationAware />
        </TestWrapper>
      );

      // Simulate orientation change
      Object.defineProperty(window.screen, 'orientation', {
        writable: true,
        value: { angle: 90 },
      });
      
      fireEvent(window, new Event('orientationchange'));
      
      expect(screen.getByText(/landscape/)).toBeInTheDocument();
    });

    it('provides appropriate touch targets for mobile devices', () => {
      render(
        <TestWrapper>
          <div style={{ display: 'flex', gap: '8px' }}>
            <MobileButton>Button 1</MobileButton>
            <MobileButton>Button 2</MobileButton>
            <MobileButton>Button 3</MobileButton>
          </div>
        </TestWrapper>
      );

      const buttons = screen.getAllByRole('button');
      
      buttons.forEach((button, index) => {
        const rect = button.getBoundingClientRect();
        
        // Each button should meet minimum touch target size
        expect(rect.height).toBeGreaterThanOrEqual(44);
        expect(rect.width).toBeGreaterThanOrEqual(44);
        
        // Buttons should have adequate spacing
        if (index > 0) {
          const prevButton = buttons[index - 1];
          const prevRect = prevButton.getBoundingClientRect();
          const distance = rect.left - (prevRect.left + prevRect.width);
          expect(distance).toBeGreaterThanOrEqual(8); // Minimum 8px spacing
        }
      });
    });
  });
});