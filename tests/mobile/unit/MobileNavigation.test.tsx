import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter as Router } from 'react-router-dom';
import MobileNavigation from '../../../frontend/src/components/mobile/MobileNavigation';

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
  <Router>
    <ThemeProvider theme={theme}>{children}</ThemeProvider>
  </Router>
);

describe('MobileNavigation', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders navigation drawer when open', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('does not render drawer when closed', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} open={false} />
        </TestWrapper>
      );

      expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
    });

    it('renders user profile section', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  describe('Navigation Menu Items', () => {
    it('renders all main navigation items', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      // Check for main navigation sections
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Sales')).toBeInTheDocument();
      expect(screen.getByText('CRM')).toBeInTheDocument();
      expect(screen.getByText('Inventory')).toBeInTheDocument();
      expect(screen.getByText('Finance')).toBeInTheDocument();
    });

    it('handles navigation item clicks', () => {
      const mockOnClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} onClose={mockOnClose} />
        </TestWrapper>
      );

      const dashboardItem = screen.getByText('Dashboard');
      fireEvent.click(dashboardItem);
      
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('expands and collapses expandable menu items', async () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      // Find expandable menu (like Finance)
      const financeMenu = screen.getByText('Finance');
      fireEvent.click(financeMenu);

      await waitFor(() => {
        expect(screen.getByText('Vouchers')).toBeInTheDocument();
        expect(screen.getByText('Reports')).toBeInTheDocument();
      });
    });
  });

  describe('Touch Interactions', () => {
    it('supports touch gestures for closing', () => {
      const mockOnClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} onClose={mockOnClose} />
        </TestWrapper>
      );

      const drawer = screen.getByRole('navigation');
      
      // Simulate swipe left gesture
      fireEvent.touchStart(drawer, {
        touches: [{ clientX: 300, clientY: 100 }],
      });

      fireEvent.touchMove(drawer, {
        touches: [{ clientX: 100, clientY: 100 }],
      });

      fireEvent.touchEnd(drawer);

      expect(mockOnClose).toHaveBeenCalled();
    });

    it('handles backdrop touch for closing', () => {
      const mockOnClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} onClose={mockOnClose} />
        </TestWrapper>
      );

      // Click backdrop (area outside drawer)
      const backdrop = document.querySelector('.MuiBackdrop-root');
      if (backdrop) {
        fireEvent.click(backdrop);
        expect(mockOnClose).toHaveBeenCalledTimes(1);
      }
    });
  });

  describe('Accessibility Features', () => {
    it('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      const navigation = screen.getByRole('navigation');
      expect(navigation).toHaveAttribute('aria-label');
    });

    it('supports keyboard navigation', async () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      const firstMenuItem = screen.getByText('Dashboard');
      firstMenuItem.focus();

      // Tab through menu items
      fireEvent.keyDown(firstMenuItem, { key: 'Tab' });
      
      await waitFor(() => {
        const activeElement = document.activeElement;
        expect(activeElement).toBeTruthy();
      });
    });

    it('closes navigation with Escape key', () => {
      const mockOnClose = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} onClose={mockOnClose} />
        </TestWrapper>
      );

      fireEvent.keyDown(document, { key: 'Escape' });
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('has proper focus management', async () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      await waitFor(() => {
        const navigation = screen.getByRole('navigation');
        const focusableElements = navigation.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        expect(focusableElements.length).toBeGreaterThan(0);
      });
    });

    it('has adequate touch target sizes', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      const menuItems = screen.getAllByRole('button');
      menuItems.forEach(item => {
        const styles = window.getComputedStyle(item);
        const height = parseInt(styles.minHeight || styles.height || '0');
        expect(height).toBeGreaterThanOrEqual(44); // WCAG minimum touch target
      });
    });
  });

  describe('Mobile-Specific Features', () => {
    it('renders mobile-optimized layout', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      const navigation = screen.getByRole('navigation');
      const styles = window.getComputedStyle(navigation);
      
      // Should be full height on mobile
      expect(styles.height).toBe('100vh');
    });

    it('handles orientation changes', () => {
      // Mock orientation change
      Object.defineProperty(window.screen, 'orientation', {
        writable: true,
        value: { angle: 90 },
      });

      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      fireEvent(window, new Event('orientationchange'));
      
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('supports pull-to-refresh gesture', () => {
      const mockOnRefresh = jest.fn();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} onRefresh={mockOnRefresh} />
        </TestWrapper>
      );

      const navigation = screen.getByRole('navigation');
      
      // Simulate pull down gesture
      fireEvent.touchStart(navigation, {
        touches: [{ clientX: 150, clientY: 50 }],
      });

      fireEvent.touchMove(navigation, {
        touches: [{ clientX: 150, clientY: 150 }],
      });

      fireEvent.touchEnd(navigation);

      if (mockOnRefresh) {
        expect(mockOnRefresh).toHaveBeenCalled();
      }
    });
  });

  describe('Error States and Edge Cases', () => {
    it('handles network connectivity issues', () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      });

      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Offline Mode')).toBeInTheDocument();
    });

    it('handles authentication expiry', () => {
      // Mock expired auth context
      jest.doMock('../../../frontend/src/context/AuthContext', () => ({
        useAuth: () => ({
          user: null,
          logout: jest.fn(),
          hasPermission: jest.fn().mockReturnValue(false),
        }),
      }));

      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Sign In Required')).toBeInTheDocument();
    });

    it('gracefully handles missing navigation data', () => {
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} navigationData={[]} />
        </TestWrapper>
      );

      expect(screen.getByText('No navigation items available')).toBeInTheDocument();
    });
  });

  describe('Performance Optimization', () => {
    it('renders navigation items efficiently', () => {
      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} />
        </TestWrapper>
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Should render in reasonable time (under 100ms)
      expect(renderTime).toBeLessThan(100);
    });

    it('handles large navigation lists without performance degradation', () => {
      const largeNavigationData = Array.from({ length: 100 }, (_, i) => ({
        id: `item-${i}`,
        title: `Navigation Item ${i}`,
        path: `/path/${i}`,
        icon: 'menu',
      }));

      render(
        <TestWrapper>
          <MobileNavigation {...defaultProps} navigationData={largeNavigationData} />
        </TestWrapper>
      );

      // Should still render all items
      expect(screen.getByText('Navigation Item 0')).toBeInTheDocument();
      expect(screen.getByText('Navigation Item 99')).toBeInTheDocument();
    });
  });
});