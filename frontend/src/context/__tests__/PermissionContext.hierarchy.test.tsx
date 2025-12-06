// frontend/src/context/__tests__/PermissionContext.hierarchy.test.tsx

import { renderHook, waitFor } from '@testing-library/react';
import { PermissionProvider, usePermissions } from '../PermissionContext';
import { AuthContext } from '../AuthContext';
import React from 'react';

// Mock axios
jest.mock('axios', () => {
  const mockAxios = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    create: jest.fn(() => mockAxios),
    defaults: {
      baseURL: '',
      headers: {
        common: {},
      },
    },
    interceptors: {
      request: {
        use: jest.fn(),
        eject: jest.fn(),
      },
      response: {
        use: jest.fn(),
        eject: jest.fn(),
      },
    },
  };
  return mockAxios;
});

// Mock rbacService
jest.mock('../../services/rbacService', () => ({
  __esModule: true,
  default: {
    getUserPermissions: jest.fn(),
  },
}));

import axios from 'axios';
import rbacService from '../../services/rbacService';

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedRbacService = rbacService as jest.Mocked<typeof rbacService>;

describe('PermissionContext - Hierarchy and Format Detection', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    username: 'testuser',
    full_name: 'Test User',
    role: 'manager',
    organization_id: 100,
    is_active: true,
    is_super_admin: false,
  };

  const createWrapper = (user: any = mockUser) => {
    return ({ children }: { children: React.ReactNode }) => (
      <AuthContext.Provider
        value={{
          user,
          loading: false,
          login: jest.fn(),
          logout: jest.fn(),
          organizationId: 100,
          updateUser: jest.fn(),
        } as any}
      >
        <PermissionProvider>{children}</PermissionProvider>
      </AuthContext.Provider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock permission format endpoint
    mockedAxios.get.mockImplementation((url: string) => {
      if (url === '/api/v1/system/permission-format') {
        return Promise.resolve({
          data: {
            primary_format: 'dotted',
            compatibility: true,
            legacy_formats: ['underscore', 'colon'],
            hierarchy_enabled: true,
            version: '1.0',
            migration_status: 'in_progress',
          },
        });
      }
      return Promise.reject(new Error('Not found'));
    });
  });

  describe('Permission Format Detection', () => {
    it('should load permission format configuration on mount', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory.read'],
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.permissionFormat).toEqual({
        primaryFormat: 'dotted',
        compatibility: true,
        legacyFormats: ['underscore', 'colon'],
        hierarchyEnabled: true,
      });
    });

    it('should use default configuration if API fails', async () => {
      mockedAxios.get.mockRejectedValue(new Error('API error'));
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory.read'],
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.permissionFormat).toEqual({
        primaryFormat: 'dotted',
        compatibility: true,
        legacyFormats: ['underscore', 'colon'],
        hierarchyEnabled: true,
      });
    });
  });

  describe('Dotted Format Permission Checking', () => {
    beforeEach(() => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory.read', 'products.create', 'crm.admin'],
      });
    });

    it('should check permissions in dotted format', async () => {
      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.hasPermission('inventory', 'read')).toBe(true);
      expect(result.current.hasPermission('products', 'create')).toBe(true);
      expect(result.current.hasPermission('inventory', 'write')).toBe(false);
    });

    it('should support legacy underscore format with compatibility mode', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory_read', 'products_create'],
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.hasPermission('inventory', 'read')).toBe(true);
      expect(result.current.hasPermission('products', 'create')).toBe(true);
    });

    it('should support legacy colon format with compatibility mode', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory:read', 'products:create'],
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.hasPermission('inventory', 'read')).toBe(true);
      expect(result.current.hasPermission('products', 'create')).toBe(true);
    });
  });

  describe('Permission Hierarchy', () => {
    it('should grant child permissions when user has parent permission', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['master_data.read'], // Parent permission
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should have parent permission
      expect(result.current.hasPermission('master_data', 'read')).toBe(true);
      
      // Should have child permissions through hierarchy
      expect(result.current.hasPermission('vendors', 'read')).toBe(true);
      expect(result.current.hasPermission('products', 'read')).toBe(true);
      expect(result.current.hasPermission('inventory', 'read')).toBe(true);
      
      // Should NOT have unrelated permissions
      expect(result.current.hasPermission('vendors', 'create')).toBe(false);
    });

    it('should handle crm.admin hierarchy', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['crm.admin'], // Parent permission
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should have child permissions
      expect(result.current.hasPermission('crm', 'settings')).toBe(true);
      expect(result.current.hasPermission('crm', 'commission')).toBe(false); // Not a direct match
      
      // Test with hasAnyPermission for full permission string
      expect(result.current.hasAnyPermission(['crm.commission.read'])).toBe(true);
      expect(result.current.hasAnyPermission(['crm.commission.create'])).toBe(true);
    });

    it('should not grant parent permission from child permission', async () => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['vendors.read'], // Child permission only
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should have child permission
      expect(result.current.hasPermission('vendors', 'read')).toBe(true);
      
      // Should NOT have parent permission
      expect(result.current.hasPermission('master_data', 'read')).toBe(false);
    });
  });

  describe('hasAnyPermission with dotted format', () => {
    beforeEach(() => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory.read', 'products.create'],
      });
    });

    it('should check any permission in dotted format', async () => {
      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.hasAnyPermission(['inventory.read', 'inventory.write'])).toBe(true);
      expect(result.current.hasAnyPermission(['inventory.write', 'inventory.delete'])).toBe(false);
    });
  });

  describe('hasAllPermissions with dotted format', () => {
    beforeEach(() => {
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: ['inventory.read', 'products.create'],
      });
    });

    it('should check all permissions in dotted format', async () => {
      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.hasAllPermissions(['inventory.read', 'products.create'])).toBe(true);
      expect(result.current.hasAllPermissions(['inventory.read', 'inventory.write'])).toBe(false);
    });
  });

  describe('Super Admin', () => {
    it('should grant all permissions to super admin', async () => {
      const superAdminUser = { ...mockUser, is_super_admin: true };
      mockedRbacService.getUserPermissions.mockResolvedValue({
        permissions: [],
      });

      const { result } = renderHook(() => usePermissions(), {
        wrapper: createWrapper(superAdminUser),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.isSuperAdmin).toBe(true);
      expect(result.current.hasPermission('any', 'permission')).toBe(true);
      expect(result.current.hasAnyPermission(['any.permission'])).toBe(true);
      expect(result.current.hasAllPermissions(['any.permission', 'another.permission'])).toBe(true);
    });
  });
});
