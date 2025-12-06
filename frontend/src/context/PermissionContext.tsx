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
import axios from 'axios';
import { PERMISSION_HIERARCHY } from '../constants/rbac';

interface PermissionContextType {
  /** User's all permissions */
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
  
  /** Permission format configuration from backend */
  permissionFormat: {
    primaryFormat: string;
    compatibility: boolean;
    legacyFormats: string[];
    hierarchyEnabled: boolean;
  } | null;
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
  permissionFormat: null,
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
  const [permissionFormat, setPermissionFormat] = useState<{
    primaryFormat: string;
    compatibility: boolean;
    legacyFormats: string[];
    hierarchyEnabled: boolean;
  } | null>(null);

  /**
   * Load permission format configuration from backend
   */
  const loadPermissionFormat = useCallback(async () => {
    try {
      const response = await axios.get('/api/v1/system/permission-format');
      setPermissionFormat({
        primaryFormat: response.data.primary_format,
        compatibility: response.data.compatibility,
        legacyFormats: response.data.legacy_formats || [],
        hierarchyEnabled: response.data.hierarchy_enabled || false,
      });
    } catch (err) {
      console.warn('Could not load permission format configuration, using defaults:', err);
      // Default to dotted format with compatibility
      setPermissionFormat({
        primaryFormat: 'dotted',
        compatibility: true,
        legacyFormats: ['underscore', 'colon'],
        hierarchyEnabled: true,
      });
    }
  }, []);

  /**
   * Check if user has permission considering hierarchy
   * @param permission - Permission to check
   * @param userPermissions - List of user's permissions
   * @returns true if user has the permission directly or through hierarchy
   */
  const checkWithHierarchy = useCallback((permission: string, userPermissions: string[]): boolean => {
    // Direct match
    if (userPermissions.includes(permission)) {
      return true;
    }

    // Check hierarchy - if user has a parent permission, they have all child permissions
    for (const [parentPerm, childPerms] of Object.entries(PERMISSION_HIERARCHY)) {
      if (userPermissions.includes(parentPerm) && childPerms.includes(permission)) {
        return true;
      }
    }

    return false;
  }, []);

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
      
      // Load permission format if not already loaded
      if (!permissionFormat) {
        await loadPermissionFormat();
      }
      
      // Call backend endpoint to get current user's permissions
      const response = await rbacService.getUserPermissions(user.id);
      
      const userPermissions = response.permissions || [];
      
      setPermissions(userPermissions);
      setIsSuperAdmin(user.is_super_admin || false);
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load user permissions';
      setError(errorMessage);
      
      // On error, set empty permissions (fail closed)
      setPermissions([]);
      setIsSuperAdmin(false);
    } finally {
      setLoading(false);
    }
  }, [user, permissionFormat, loadPermissionFormat]);

  /**
   * Load permissions on mount and when user changes
   */
  useEffect(() => {
    loadPermissionFormat();
  }, [loadPermissionFormat]);

  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  /**
   * Compatibility shim to map legacy permission formats to dotted format
   * TODO: Remove after full migration (target: Q2 2026) - Track via GitHub Issue
   * Monitor: /api/v1/system/permission-format migration_status field
   * @param module - Module name
   * @param action - Action name
   * @returns Array of permission strings to check (dotted + legacy if compatibility enabled)
   */
  const getPermissionVariants = useCallback((module: string, action: string): string[] => {
    const variants: string[] = [];
    
    // Primary format: dotted
    const permDot = `${module}.${action}`;
    variants.push(permDot);
    
    // Add legacy formats if compatibility is enabled
    if (permissionFormat?.compatibility) {
      if (permissionFormat.legacyFormats.includes('underscore')) {
        variants.push(`${module}_${action}`);
      }
      if (permissionFormat.legacyFormats.includes('colon')) {
        variants.push(`${module}:${action}`);
      }
    }
    
    return variants;
  }, [permissionFormat]);

  /**
   * Check if user has a specific permission
   * Supports dotted format (primary) and legacy formats (compatibility)
   * Includes hierarchy logic when enabled
   * @param module - Module name (e.g., 'inventory', 'admin')
   * @param action - Action name (e.g., 'read', 'create', 'update', 'delete')
   * @returns true if user has the explicit permission
   */
  const hasPermission = useCallback((module: string, action: string): boolean => {
    if (isSuperAdmin) {
      return true;
    }
    
    // Get all permission variants to check
    const variants = getPermissionVariants(module, action);
    
    // Check direct match for any variant
    const hasDirectMatch = variants.some(variant => permissions.includes(variant));
    if (hasDirectMatch) {
      return true;
    }
    
    // Check hierarchy if enabled
    if (permissionFormat?.hierarchyEnabled) {
      return variants.some(variant => checkWithHierarchy(variant, permissions));
    }
    
    return false;
  }, [permissions, isSuperAdmin, permissionFormat, getPermissionVariants, checkWithHierarchy]);

  /**
   * Check if user has any of the specified permissions
   * @param permissionList - Array of permission strings (e.g., ['voucher.read', 'voucher.create'])
   * @returns true if user has at least one of the explicit permissions
   */
  const hasAnyPermission = useCallback((permissionList: string[]): boolean => {
    if (isSuperAdmin) {
      return true;
    }
    return permissionList.some(permission => {
      // Support both dotted format and module.action split
      const [module, action] = permission.split(/[.]/);
      if (module && action) {
        return hasPermission(module, action);
      }
      // Fallback: check direct permission string
      return permissions.includes(permission) || 
             (permissionFormat?.hierarchyEnabled && checkWithHierarchy(permission, permissions));
    });
  }, [hasPermission, isSuperAdmin, permissions, permissionFormat, checkWithHierarchy]);

  /**
   * Check if user has all of the specified permissions
   * @param permissionList - Array of permission strings
   * @returns true if user has all of the explicit permissions
   */
  const hasAllPermissions = useCallback((permissionList: string[]): boolean => {
    if (isSuperAdmin) {
      return true;
    }
    return permissionList.every(permission => {
      // Support both dotted format and module.action split
      const [module, action] = permission.split(/[.]/);
      if (module && action) {
        return hasPermission(module, action);
      }
      // Fallback: check direct permission string
      return permissions.includes(permission) || 
             (permissionFormat?.hierarchyEnabled && checkWithHierarchy(permission, permissions));
    });
  }, [hasPermission, isSuperAdmin, permissions, permissionFormat, checkWithHierarchy]);

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
    permissionFormat,
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
          <p>Required permission: <code>{module}.{action}</code></p>  {/* CHANGED: Use dot format in message */}
          <p>Please contact your administrator to request access.</p>
        </div>
      );
    }
    
    return <Component {...props} />;
  };
}

export default PermissionProvider;
