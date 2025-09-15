// components/analytics/__tests__/UnifiedAnalyticsDashboard.test.tsx
/**
 * Comprehensive test suite for Unified Analytics Dashboard
 * Tests role-based access, multi-tenancy, and real-time functionality
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { jest } from '@jest/globals';
import UnifiedAnalyticsDashboard from '../UnifiedAnalyticsDashboard';
import { useAuth } from '../../../hooks/useAuth';
import { rbacService } from '../../../services/rbacService';
import { analyticsService } from '../../../services/analyticsService';

// Mock the hooks and services
jest.mock('../../../hooks/useAuth');
jest.mock('../../../services/rbacService');
jest.mock('../../../services/analyticsService');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockRbacService = rbacService as jest.Mocked<typeof rbacService>;
const mockAnalyticsService = analyticsService as jest.Mocked<typeof analyticsService>;

describe('UnifiedAnalyticsDashboard', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    // Reset mocks
    jest.clearAllMocks();

    // Default mock implementations
    mockAnalyticsService.getDashboardMetrics.mockResolvedValue({
      total_customers: 150,
      total_interactions_today: 25,
      total_interactions_week: 180,
      total_interactions_month: 750,
      top_segments: [
        { segment_name: 'Premium', customer_count: 45 },
        { segment_name: 'Standard', customer_count: 105 },
      ],
      recent_activity: [],
      calculated_at: '2024-01-15T10:00:00Z',
    });

    mockRbacService.getCurrentUserPermissions.mockResolvedValue([
      'crm_view',
      'customer_analytics_view',
      'sales_view',
      'service_view',
    ]);
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  describe('Authentication and Access Control', () => {
    it('should show authentication error when user is not logged in', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      expect(screen.getByText(/authentication required/i)).toBeInTheDocument();
    });

    it('should show no modules available when user has no permissions', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'standard_user',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      mockRbacService.getCurrentUserPermissions.mockResolvedValue([]);

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/no analytics modules available/i)).toBeInTheDocument();
      });
    });

    it('should display available modules based on user permissions', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /customer/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /sales/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /service/i })).toBeInTheDocument();
      });
    });
  });

  describe('Multi-tenancy Support', () => {
    it('should display organization context for org users', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 123,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Org: 123')).toBeInTheDocument();
        expect(screen.getByText(/analytics data is scoped to your organization/i)).toBeInTheDocument();
      });
    });

    it('should display platform context for platform users', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'admin@platform.com',
          full_name: 'Platform Admin',
          role: 'super_admin',
          organization_id: null,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Platform')).toBeInTheDocument();
      });
    });

    it('should show super admin privileges message', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'admin@platform.com',
          full_name: 'Platform Admin',
          role: 'super_admin',
          organization_id: 123,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/super admin access allows cross-organization analytics/i)).toBeInTheDocument();
      });
    });
  });

  describe('Dashboard Functionality', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });
    });

    it('should display customer analytics data', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument(); // Total customers
        expect(screen.getByText('25')).toBeInTheDocument(); // Interactions today
        expect(screen.getByText('Total Customers')).toBeInTheDocument();
        expect(screen.getByText('Interactions Today')).toBeInTheDocument();
      });
    });

    it('should handle analytics data loading states', async () => {
      mockAnalyticsService.getDashboardMetrics.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          total_customers: 150,
          total_interactions_today: 25,
          total_interactions_week: 180,
          total_interactions_month: 750,
          top_segments: [],
          recent_activity: [],
          calculated_at: '2024-01-15T10:00:00Z',
        }), 100))
      );

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      // Should show loading skeleton initially
      expect(screen.getByTestId('skeleton') || document.querySelector('.MuiSkeleton-root')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument();
      });
    });

    it('should handle analytics data error states', async () => {
      mockAnalyticsService.getDashboardMetrics.mockRejectedValue(
        new Error('Failed to load analytics')
      );

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load customer analytics/i)).toBeInTheDocument();
      });
    });

    it('should allow tab navigation between modules', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const customerTab = screen.getByRole('tab', { name: /customer/i });
        const salesTab = screen.getByRole('tab', { name: /sales/i });

        fireEvent.click(salesTab);
        expect(salesTab).toHaveAttribute('aria-selected', 'true');

        fireEvent.click(customerTab);
        expect(customerTab).toHaveAttribute('aria-selected', 'true');
      });
    });
  });

  describe('Real-time Features', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });
    });

    it('should have real-time toggle enabled by default', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const realTimeSwitch = screen.getByRole('checkbox', { name: /real-time/i });
        expect(realTimeSwitch).toBeChecked();
      });
    });

    it('should allow toggling real-time updates', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const realTimeSwitch = screen.getByRole('checkbox', { name: /real-time/i });
        
        fireEvent.click(realTimeSwitch);
        expect(realTimeSwitch).not.toBeChecked();

        fireEvent.click(realTimeSwitch);
        expect(realTimeSwitch).toBeChecked();
      });
    });

    it('should have refresh button that triggers data reload', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const refreshButton = screen.getByRole('button', { name: /refresh data/i });
        fireEvent.click(refreshButton);
      });

      // Should trigger analytics service calls
      expect(mockAnalyticsService.getDashboardMetrics).toHaveBeenCalled();
    });
  });

  describe('Filter and Export Features', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });
    });

    it('should show filter menu when filter button is clicked', async () => {
      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const filterButton = screen.getByRole('button', { name: /filter/i });
        fireEvent.click(filterButton);

        expect(screen.getByText('Last 7 days')).toBeInTheDocument();
        expect(screen.getByText('Last 30 days')).toBeInTheDocument();
        expect(screen.getByText('Last 90 days')).toBeInTheDocument();
        expect(screen.getByText('Custom range')).toBeInTheDocument();
      });
    });

    it('should have export functionality', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        const exportButton = screen.getByRole('button', { name: /export/i });
        fireEvent.click(exportButton);

        expect(consoleSpy).toHaveBeenCalledWith('Exporting analytics data...');
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Role-based Module Access', () => {
    it('should show only dashboard module when user has no specific permissions', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'standard_user',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      mockRbacService.getCurrentUserPermissions.mockResolvedValue([]);

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.queryByRole('tab', { name: /customer/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('tab', { name: /sales/i })).not.toBeInTheDocument();
      });
    });

    it('should show only customer module when user has CRM permissions', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'standard_user',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      mockRbacService.getCurrentUserPermissions.mockResolvedValue(['crm_view']);

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /customer/i })).toBeInTheDocument();
        expect(screen.queryByRole('tab', { name: /sales/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('tab', { name: /finance/i })).not.toBeInTheDocument();
      });
    });

    it('should show all modules for users with comprehensive permissions', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'admin@example.com',
          full_name: 'Admin User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });

      mockRbacService.getCurrentUserPermissions.mockResolvedValue([
        'crm_view',
        'customer_analytics_view',
        'sales_view',
        'sales_analytics_view',
        'service_view',
        'service_analytics_view',
        'finance_view',
        'finance_analytics_view',
        'project_view',
        'project_analytics_view',
      ]);

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /customer/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /sales/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /service/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /finance/i })).toBeInTheDocument();
        expect(screen.getByRole('tab', { name: /projects/i })).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'Test User',
          role: 'admin',
          organization_id: 1,
        },
        login: jest.fn(),
        logout: jest.fn(),
        isLoading: false,
        error: null,
      });
    });

    it('should handle network errors gracefully', async () => {
      mockRbacService.getCurrentUserPermissions.mockRejectedValue(
        new Error('Network error')
      );

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        // Should still render with default permissions
        expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
      });
    });

    it('should handle partial data loading failures', async () => {
      mockAnalyticsService.getDashboardMetrics.mockRejectedValue(
        new Error('Analytics service unavailable')
      );

      renderWithProviders(<UnifiedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load customer analytics/i)).toBeInTheDocument();
      });
    });
  });
});