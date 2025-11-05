// frontend/src/hooks/__tests__/usePermissionCheck.test.tsx

import { renderHook, waitFor } from '@testing-library/react';
import { usePermissionCheck, useHasPermission, useHasModuleAccess } from '../usePermissionCheck';
import { AuthContext } from '../../context/AuthContext';
import { OrganizationContext } from '../../context/OrganizationContext';
import { useEntitlements } from '../useEntitlements';
import React from 'react';

// Mock the useEntitlements hook
jest.mock('../useEntitlements');

const mockUseEntitlements = useEntitlements as jest.MockedFunction<typeof useEntitlements>;

describe('usePermissionCheck', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    username: 'testuser',
    full_name: 'Test User',
    role: 'manager',
    organization_id: 100,
    is_active: true,
  };

  const mockUserPermissions = [
    'crm.read',
    'crm.write',
    'inventory.read',
  ];

  const mockEntitlements = {
    organization_id: 100,
    enabled_modules: ['crm', 'inventory'],
    disabled_modules: ['manufacturing'],
    trial_modules: ['finance'],
    module_settings: {
      crm: { status: 'enabled', trial_until: null },
      inventory: { status: 'enabled', trial_until: null },
      manufacturing: { status: 'disabled', trial_until: null },
      finance: { status: 'trial', trial_until: '2025-12-31' },
    },
  };

  const createWrapper = (
    user: any = mockUser,
    organizationId: number | null = 100,
    entitlements: any = mockEntitlements,
    loading: boolean = false
  ) => {
    return ({ children }: { children: React.ReactNode }) => (
      <AuthContext.Provider
        value={{
          user,
          userPermissions: mockUserPermissions,
          loading,
          login: jest.fn(),
          logout: jest.fn(),
          organizationId,
          updateUser: jest.fn(),
        } as any}
      >
        <OrganizationContext.Provider
          value={{
            organizationId,
            setOrganizationId: jest.fn(),
          } as any}
        >
          {children}
        </OrganizationContext.Provider>
      </AuthContext.Provider>
    );
  };

  beforeEach(() => {
    mockUseEntitlements.mockReturnValue({
      entitlements: mockEntitlements,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    } as any);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Layer 1: Tenant Checks', () => {
    it('should detect valid tenant context', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.hasTenantContext).toBe(true);
      expect(result.current.organizationId).toBe(100);
    });

    it('should detect missing tenant context', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(mockUser, null),
      });

      expect(result.current.hasTenantContext).toBe(false);
      expect(result.current.organizationId).toBeNull();
    });

    it('should validate tenant access for same org', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkTenantAccess(100)).toBe(true);
    });

    it('should deny tenant access for different org', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkTenantAccess(200)).toBe(false);
    });

    it('should allow super admin to access any org', () => {
      const superAdminUser = { ...mockUser, role: 'super_admin' };
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(superAdminUser),
      });

      expect(result.current.checkTenantAccess(200)).toBe(true);
      expect(result.current.checkTenantAccess(300)).toBe(true);
    });
  });

  describe('Layer 2: Entitlement Checks', () => {
    it('should detect enabled module', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkModuleEntitled('crm')).toBe(true);
      expect(result.current.checkModuleEntitled('inventory')).toBe(true);
    });

    it('should detect disabled module', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkModuleEntitled('manufacturing')).toBe(false);
    });

    it('should detect trial module', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkModuleEntitled('finance')).toBe(true);
    });

    it('should get module status correctly', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.getModuleEntitlementStatus('crm')).toBe('enabled');
      expect(result.current.getModuleEntitlementStatus('manufacturing')).toBe('disabled');
      expect(result.current.getModuleEntitlementStatus('finance')).toBe('trial');
    });
  });

  describe('Layer 3: RBAC Checks', () => {
    it('should detect user has permission', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkPermission('crm.read')).toBe(true);
      expect(result.current.checkPermission('crm.write')).toBe(true);
    });

    it('should detect user lacks permission', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkPermission('crm.delete')).toBe(false);
      expect(result.current.checkPermission('manufacturing.read')).toBe(false);
    });

    it('should check user role', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.checkUserRole('manager')).toBe(true);
      expect(result.current.checkUserRole('admin')).toBe(false);
    });

    it('should detect super admin', () => {
      const superAdminUser = { ...mockUser, role: 'super_admin' };
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(superAdminUser),
      });

      expect(result.current.checkIsSuperAdmin()).toBe(true);
    });

    it('should detect org admin', () => {
      const adminUser = { ...mockUser, role: 'admin' };
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(adminUser),
      });

      expect(result.current.checkIsOrgAdmin()).toBe(true);
    });

    it('should check role management capabilities', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      // Manager can manage executive
      expect(result.current.checkCanManageRole('executive')).toBe(true);
      // Manager cannot manage admin
      expect(result.current.checkCanManageRole('admin')).toBe(false);
    });
  });

  describe('Combined Checks (All 3 Layers)', () => {
    it('should grant access when all layers pass', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      const access = result.current.checkModuleAccess('crm', 'read');
      
      expect(access.hasPermission).toBe(true);
    });

    it('should deny access when tenant context missing', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(mockUser, null),
      });

      const access = result.current.checkModuleAccess('crm', 'read');
      
      expect(access.hasPermission).toBe(false);
      expect(access.reason).toContain('Organization context');
      expect(access.enforcementLevel).toBe('TENANT');
    });

    it('should deny access when module not entitled', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      const access = result.current.checkModuleAccess('manufacturing', 'read');
      
      expect(access.hasPermission).toBe(false);
      expect(access.enforcementLevel).toBe('ENTITLEMENT');
    });

    it('should deny access when permission missing', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      const access = result.current.checkModuleAccess('inventory', 'write');
      
      expect(access.hasPermission).toBe(false);
      expect(access.enforcementLevel).toBe('RBAC');
    });

    it('should grant submodule access with proper entitlement', () => {
      const entitlementsWithSubmodules = {
        ...mockEntitlements,
        module_settings: {
          ...mockEntitlements.module_settings,
          crm: {
            status: 'enabled',
            trial_until: null,
            submodules: {
              leads: { enabled: true },
              opportunities: { enabled: true },
            },
          },
        },
      };

      mockUseEntitlements.mockReturnValue({
        entitlements: entitlementsWithSubmodules,
        isLoading: false,
        error: null,
        refetch: jest.fn(),
      } as any);

      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(mockUser, 100, entitlementsWithSubmodules),
      });

      const access = result.current.checkSubmoduleAccess('crm', 'leads', 'read');
      
      expect(access.hasPermission).toBe(true);
    });
  });

  describe('Loading and Ready States', () => {
    it('should be loading when entitlements are loading', () => {
      mockUseEntitlements.mockReturnValue({
        entitlements: null,
        isLoading: true,
        error: null,
        refetch: jest.fn(),
      } as any);

      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.isReady).toBe(false);
    });

    it('should be loading when auth is loading', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(mockUser, 100, mockEntitlements, true),
      });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.isReady).toBe(false);
    });

    it('should be ready when all data is loaded', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isReady).toBe(true);
    });

    it('should not be ready without tenant context', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(mockUser, null),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isReady).toBe(false);
    });

    it('should not be ready without user', () => {
      const { result } = renderHook(() => usePermissionCheck(), {
        wrapper: createWrapper(null),
      });

      expect(result.current.isReady).toBe(false);
    });
  });

  describe('useHasPermission helper hook', () => {
    it('should return true for granted permission', () => {
      const { result } = renderHook(() => useHasPermission('crm.read'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBe(true);
    });

    it('should return false for denied permission', () => {
      const { result } = renderHook(() => useHasPermission('crm.delete'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBe(false);
    });
  });

  describe('useHasModuleAccess helper hook', () => {
    it('should return true for accessible module', () => {
      const { result } = renderHook(() => useHasModuleAccess('crm', 'read'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBe(true);
    });

    it('should return false for inaccessible module', () => {
      const { result } = renderHook(() => useHasModuleAccess('manufacturing', 'read'), {
        wrapper: createWrapper(),
      });

      expect(result.current).toBe(false);
    });
  });
});
