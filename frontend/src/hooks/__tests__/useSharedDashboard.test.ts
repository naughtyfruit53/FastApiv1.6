// frontend/src/hooks/__tests__/useSharedDashboard.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useSharedDashboard } from '../useSharedDashboard';
import { useAuth } from '../../context/AuthContext';
import adminService from '../../services/adminService';
import activityService from '../../services/activityService';

// Mock dependencies
jest.mock('../../context/AuthContext');
jest.mock('../../services/adminService');
jest.mock('../../services/activityService');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockAdminService = adminService as jest.Mocked<typeof adminService>;
const mockActivityService = activityService as jest.Mocked<typeof activityService>;

describe('useSharedDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with loading state when user is null', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      displayRole: null,
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: false,
      getAuthHeaders: jest.fn(() => ({})),
    });

    const { result } = renderHook(() => useSharedDashboard());

    // When user is null, loading should be false but statistics should be null
    expect(result.current.loading).toBe(false);
    expect(result.current.statistics).toBe(null);
    expect(result.current.error).toBe(null);
  });

  it('should fetch app statistics for super admin', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@test.com',
      is_super_admin: true,
      role: 'super_admin',
      organization_id: null,
      must_change_password: false,
    };

    const mockAppStats = {
      total_licenses_issued: 100,
      active_organizations: 85,
      trial_organizations: 15,
      total_active_users: 500,
      super_admins_count: 5,
      new_licenses_this_month: 10,
      plan_breakdown: { premium: 70, trial: 15, basic: 15 },
      system_health: { status: 'healthy', uptime: '99.9%' },
      generated_at: '2024-01-15T10:00:00Z',
    };

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      displayRole: 'Super Admin',
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: true,
      getAuthHeaders: jest.fn(() => ({ Authorization: 'Bearer token' })),
    });

    mockAdminService.getAppStatistics.mockResolvedValue(mockAppStats);

    const { result } = renderHook(() => useSharedDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.isSuperAdmin).toBe(true);
    expect(result.current.statistics).toMatchObject(mockAppStats);
    expect(mockAdminService.getAppStatistics).toHaveBeenCalledTimes(1);
  });

  it('should fetch org statistics for regular user', async () => {
    const mockUser = {
      id: '2',
      email: 'user@test.com',
      is_super_admin: false,
      role: 'user',
      organization_id: 'org-123',
      must_change_password: false,
    };

    const mockOrgStats = {
      total_products: 150,
      total_products_trend: 5,
      total_products_direction: 'up' as const,
      total_customers: 250,
      total_customers_trend: 8,
      total_customers_direction: 'up' as const,
      total_vendors: 50,
      total_vendors_trend: 2,
      total_vendors_direction: 'up' as const,
      active_users: 25,
      active_users_trend: 3,
      active_users_direction: 'up' as const,
      monthly_sales: 500000,
      monthly_sales_trend: 12,
      monthly_sales_direction: 'up' as const,
      inventory_value: 750000,
      inventory_value_trend: 7,
      inventory_value_direction: 'up' as const,
      plan_type: 'premium',
      storage_used_gb: 2.5,
      generated_at: '2024-01-15T10:00:00Z',
    };

    const mockActivities = {
      activities: [
        {
          id: '1',
          type: 'sale',
          title: 'New Sale',
          description: 'Sale created for customer ABC',
          timestamp: '2024-01-15T09:00:00Z',
          user_name: 'John Doe',
        },
      ],
    };

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      displayRole: 'User',
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: true,
      getAuthHeaders: jest.fn(() => ({ Authorization: 'Bearer token' })),
    });

    mockAdminService.getOrgStatistics.mockResolvedValue(mockOrgStats);
    mockActivityService.getRecentActivities.mockResolvedValue(mockActivities);

    const { result } = renderHook(() => useSharedDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.isSuperAdmin).toBe(false);
    expect(result.current.statistics).toMatchObject(mockOrgStats);
    expect(result.current.recentActivities).toEqual(mockActivities.activities);
    expect(mockAdminService.getOrgStatistics).toHaveBeenCalledTimes(1);
    expect(mockActivityService.getRecentActivities).toHaveBeenCalledWith(5);
  });

  it('should handle error states correctly', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@test.com',
      is_super_admin: true,
      role: 'super_admin',
      organization_id: null,
      must_change_password: false,
    };

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      displayRole: 'Super Admin',
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: true,
      getAuthHeaders: jest.fn(() => ({ Authorization: 'Bearer token' })),
    });

    mockAdminService.getAppStatistics.mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useSharedDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('API Error');
    expect(result.current.statistics).toBe(null);
  });

  it('should generate correct stats cards for super admin', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@test.com',
      is_super_admin: true,
      role: 'super_admin',
      organization_id: null,
      must_change_password: false,
    };

    const mockAppStats = {
      total_licenses_issued: 100,
      active_organizations: 85,
      trial_organizations: 15,
      total_active_users: 500,
      super_admins_count: 5,
      new_licenses_this_month: 10,
      plan_breakdown: { premium: 70, trial: 15, basic: 15 },
      system_health: { status: 'healthy', uptime: '99.9%' },
      generated_at: '2024-01-15T10:00:00Z',
    };

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      displayRole: 'Super Admin',
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: true,
      getAuthHeaders: jest.fn(() => ({ Authorization: 'Bearer token' })),
    });

    mockAdminService.getAppStatistics.mockResolvedValue(mockAppStats);

    const { result } = renderHook(() => useSharedDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const statsCards = result.current.getStatsCards();
    
    expect(statsCards).toHaveLength(9);
    expect(statsCards[0]).toMatchObject({
      title: 'Total Licenses Issued',
      value: 100,
      description: 'Total organization licenses created',
    });
    expect(statsCards[1]).toMatchObject({
      title: 'Active Organizations',
      value: 85,
      description: 'Organizations with active status',
    });
  });

  it('should calculate activation rate correctly', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@test.com',
      is_super_admin: true,
      role: 'super_admin',
      organization_id: null,
      must_change_password: false,
    };

    const mockAppStats = {
      total_licenses_issued: 100,
      active_organizations: 85,
      trial_organizations: 15,
      total_active_users: 500,
      super_admins_count: 5,
      new_licenses_this_month: 10,
      plan_breakdown: { premium: 70, trial: 15, basic: 15 },
      system_health: { status: 'healthy', uptime: '99.9%' },
      generated_at: '2024-01-15T10:00:00Z',
    };

    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      displayRole: 'Super Admin',
      login: jest.fn(),
      logout: jest.fn(),
      refreshUser: jest.fn(),
      updateUser: jest.fn(),
      isOrgContextReady: true,
      getAuthHeaders: jest.fn(() => ({ Authorization: 'Bearer token' })),
    });

    mockAdminService.getAppStatistics.mockResolvedValue(mockAppStats);

    const { result } = renderHook(() => useSharedDashboard());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const activationRate = result.current.getActivationRate();
    expect(activationRate).toBe(85); // 85/100 * 100 = 85%
  });
});