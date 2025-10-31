// frontend/src/context/PermissionContext.tsx

/**
 * Permission Context - Manages user permissions for RBAC enforcement
 * 
 * This context provides:
 * - User's current permissions
 * - Permission checking utility functions
 * - Automatic permission refresh on login/logout
 * 
 * Usage:
 * ```tsx
 * import { usePermissions } from '@/context/PermissionContext';
 * 
 * const MyComponent = () => {
 *   const { hasPermission, permissions, loading } = usePermissions();
 *   
 *   if (loading) return <Spinner />;
 *   
 *   if (!hasPermission('voucher', 'create')) {
 *     return <AccessDenied />;
 *   }
 *   
 *   return <VoucherForm />;
 * };
 * ```
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import rbacService from '../services/rbacService';

interface PermissionContextType {
  /** List of all permissions the current user has */
  permissions: string[];
  
  /** Check if user has a specific permission */
  hasPermission: (module: string, action: string) => boolean;
  
  /** Check if user has any of the specified permissions */
  hasAnyPermission: (permissionList: string[]) => boolean;
  
  /** Check if user has all of the specified permissions */
  hasAllPermissions: (permissionList: string[]) => boolean;
  
  /** Loading state for initial permission fetch */
  loading: boolean;
  
  /** Error state if permission fetch fails */
  error: string | null;
  
  /** Manually refresh permissions (e.g., after role change) */
  refreshPermissions: () => Promise<void>;
  
  /** Check if user is super admin (bypasses all permission checks) */
  isSuperAdmin: boolean;
}

const PermissionContext = createContext<PermissionContextType>({
  permissions: [],
  hasPermission: () => false,
  hasAnyPermission: () => false,
  hasAllPermissions: () => false,
  loading: true,
  error: null,
  refreshPermissions: async () => {},
  isSuperAdmin: false,
});

interface PermissionProviderProps {
  children: React.ReactNode;
}

export const PermissionProvider: React.FC<PermissionProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const [permissions, setPermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState(false);

  /**
   * Load permissions from backend
   */
  const loadPermissions = useCallback(async () => {
    if (!user?.id) {
      setPermissions([]);
      setIsSuperAdmin(false);
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      
      // Call backend endpoint to get current user's permissions
      const response = await rbacService.getUserPermissions(user.id);
      
      const userPermissions = response.permissions || [];
      
      setPermissions(userPermissions);
      setIsSuperAdmin(user.is_super_admin || false);
      
      console.log('[PermissionContext] Loaded permissions:', userPermissions.length, 'permissions');
      if (user.is_super_admin) {
        console.log('[PermissionContext] User is super admin - all permissions granted');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load user permissions';
      setError(errorMessage);
      console.error('[PermissionContext] Error loading permissions:', err);
      
      // On error, set empty permissions (fail closed)
      setPermissions([]);
      setIsSuperAdmin(false);
    } finally {
      setLoading(false);
    }
  }, [user]);

  /**
   * Load permissions on mount and when user changes
   */
  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  /**
   * Check if user has a specific permission
   * @param module - Module name (e.g., 'voucher', 'inventory', 'admin')
   * @param action - Action name (e.g., 'read', 'create', 'update', 'delete')
   * @returns true if user has the permission or is super admin
   */
  const hasPermission = useCallback((module: string, action: string): boolean => {
    // Super admins bypass all permission checks
    if (isSuperAdmin) {
      return true;
    }
    
    const permUnderscore = `${module}_${action}`;
    const permColon = `${module}:${action}`;
    const hasPerm = permissions.includes(permUnderscore) || permissions.includes(permColon);
    
    console.log(`Checking permission: ${permUnderscore} or ${permColon} - Result: ${hasPerm}`);
    
    return hasPerm;
  }, [permissions, isSuperAdmin]);

  /**
   * Check if user has any of the specified permissions
   * @param permissionList - Array of permission strings (e.g., ['voucher_read', 'voucher_create'])
   * @returns true if user has at least one of the permissions or is super admin
   */
  const hasAnyPermission = useCallback((permissionList: string[]): boolean => {
    // Super admins bypass all permission checks
    if (isSuperAdmin) {
      return true;
    }
    
    return permissionList.some(permission => {
      // Support both formats in list
      const [module, action] = permission.split(/[_:]/); // split on _ or :
      return hasPermission(module, action);
    });
  }, [hasPermission, isSuperAdmin]);

  /**
   * Check if user has all of the specified permissions
   * @param permissionList - Array of permission strings
   * @returns true if user has all of the permissions or is super admin
   */
  const hasAllPermissions = useCallback((permissionList: string[]): boolean => {
    // Super admins bypass all permission checks
    if (isSuperAdmin) {
      return true;
    }
    
    return permissionList.every(permission => {
      const [module, action] = permission.split(/[_:]/);
      return hasPermission(module, action);
    });
  }, [hasPermission, isSuperAdmin]);

  /**
   * Manually refresh permissions
   * Useful after role changes or permission updates
   */
  const refreshPermissions = useCallback(async () => {
    await loadPermissions();
  }, [loadPermissions]);

  const value: PermissionContextType = {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    loading,
    error,
    refreshPermissions,
    isSuperAdmin,
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
};

/**
 * Hook to access permission context
 * @throws Error if used outside of PermissionProvider
 */
export const usePermissions = (): PermissionContextType => {
  const context = useContext(PermissionContext);
  
  if (!context) {
    throw new Error('usePermissions must be used within a PermissionProvider');
  }
  
  return context;
};

/**
 * Higher-order component to protect routes based on permissions
 * 
 * Usage:
 * ```tsx
 * export default withPermission(MyComponent, 'voucher', 'create');
 * ```
 */
export function withPermission<P extends object>(
  Component: React.ComponentType<P>,
  module: string,
  action: string
): React.FC<P> {
  return (props: P) => {
    const { hasPermission, loading } = usePermissions();
    
    if (loading) {
      return <div>Loading permissions...</div>;
    }
    
    if (!hasPermission(module, action)) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>You don't have permission to access this resource.</p>
          <p>Required permission: <code>{module}_{action}</code></p>
          <p>Please contact your administrator to request access.</p>
        </div>
      );
    }
    
    return <Component {...props} />;
  };
}

export default PermissionContext;