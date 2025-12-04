// frontend/src/hooks/usePermissionCheck.ts

/**
 * Custom hook for 3-layer permission checking
 * Combines tenant context, entitlements, and RBAC permissions
 */

import { useContext, useCallback, useMemo } from 'react';
import { AuthContext } from '../context/AuthContext';
import { OrganizationContext } from '../context/OrganizationContext';
import { useEntitlements } from './useEntitlements';
import {
  canAccessModule,
  canAccessSubmodule,
  hasPermission,
  isModuleEntitled,
  isSubmoduleEntitled,
  getModuleStatus,
  getAccessDenialReason,
  isSuperAdmin,
  isOrgAdmin,
  canManageRole,
  validateOrgContext,
  userBelongsToOrg,
} from '../utils/permissionHelpers';
import {
  type OrgEntitlements,
  type PermissionCheck,
  EnforcementLevel,
} from '../constants/rbac';
import { ACCESS_TOKEN_KEY } from '../constants/auth';

/**
 * Hook for comprehensive permission checking across all 3 layers
 */
export function usePermissionCheck() {
  // Layer 1: Tenant - NEW: Defensive check for undefined context object
  let orgContext;
  if (typeof OrganizationContext === 'undefined') {
    console.error('[usePermissionCheck] OrganizationContext is undefined. Check imports and file paths. Using fallback null organizationId.');
    orgContext = null; // Fallback to prevent crash
  } else {
    orgContext = useContext(OrganizationContext);
  }
  const organizationId = orgContext?.organizationId ?? null;

  // Layer 3: RBAC - NEW: Defensive check for undefined context object
  let authContext;
  if (typeof AuthContext === 'undefined') {
    console.error('[usePermissionCheck] AuthContext is undefined. Check imports and file paths. Using fallback null user.');
    authContext = null; // Fallback to prevent crash
  } else {
    authContext = useContext(AuthContext);
  }
  const user = authContext?.user ?? null;
  const userPermissions = authContext?.userPermissions ?? null;

  // Layer 2: Entitlements
  const token = typeof window !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
  const { entitlements, isLoading: entitlementsLoading } = useEntitlements(
    organizationId ?? undefined,
    token ?? undefined
  );

  // NEW: If any context is null, treat as loading
  const contextsLoading = orgContext === null || authContext === null;

  // ============================================================================
  // Layer 1: Tenant Checks
  // ============================================================================

  const hasTenantContext = useMemo(() => {
    return validateOrgContext(organizationId);
  }, [organizationId]);

  const checkTenantAccess = useCallback(
    (targetOrgId: number): boolean => {
      // Super admins can access any org
      if (user && isSuperAdmin(user.role)) {
        return true;
      }

      return userBelongsToOrg(user?.organization_id, targetOrgId);
    },
    [user]
  );

  // ============================================================================
  // Layer 2: Entitlement Checks
  // ============================================================================

  const checkModuleEntitled = useCallback(
    (moduleKey: string): boolean => {
      return isModuleEntitled(
        entitlements as OrgEntitlements | null,
        moduleKey
      );
    },
    [entitlements]
  );

  const checkSubmoduleEntitled = useCallback(
    (moduleKey: string, submoduleKey: string): boolean => {
      return isSubmoduleEntitled(
        entitlements as OrgEntitlements | null,
        moduleKey,
        submoduleKey
      );
    },
    [entitlements]
  );

  const getModuleEntitlementStatus = useCallback(
    (moduleKey: string) => {
      return getModuleStatus(entitlements as OrgEntitlements | null, moduleKey);
    },
    [entitlements]
  );

  // ============================================================================
  // Layer 3: RBAC Checks
  // ============================================================================

  const checkPermission = useCallback(
    (permission: string): boolean => {
      return hasPermission(userPermissions, permission);
    },
    [userPermissions]
  );

  const checkUserRole = useCallback(
    (role: string): boolean => {
      return user?.role === role;
    },
    [user]
  );

  const checkIsSuperAdmin = useCallback(() => {
    return user ? isSuperAdmin(user.role) : false;
  }, [user]);

  const checkIsOrgAdmin = useCallback(() => {
    return user ? isOrgAdmin(user.role) : false;
  }, [user]);

  const checkCanManageRole = useCallback(
    (targetRole: string): boolean => {
      return user ? canManageRole(user.role || '', targetRole) : false;
    },
    [user]
  );

  // ============================================================================
  // Combined Checks (All 3 Layers)
  // ============================================================================

  const checkModuleAccess = useCallback(
    (moduleKey: string, action: string = 'read'): PermissionCheck => {
      // NEW: If permissions not loaded, treat as loading state
      if (userPermissions === null) {
        return {
          hasPermission: false,
          isLoading: true,
          reason: 'Permissions are loading',
          enforcementLevel: EnforcementLevel.RBAC,
        };
      }

      // Layer 1: Tenant - Allow super_admin without tenant context
      const isSuper = checkIsSuperAdmin();
      if (!hasTenantContext && !isSuper) {
        return {
          hasPermission: false,
          reason: 'Organization context is required',
          enforcementLevel: EnforcementLevel.TENANT,
        };
      }

      // Full bypass for super_admin
      if (isSuper) {
        return {
          hasPermission: true,
          enforcementLevel: EnforcementLevel.RBAC,
        };
      }

      // Perform combined check
      const hasAccess = canAccessModule(
        userPermissions,
        entitlements as OrgEntitlements | null,
        moduleKey,
        action
      );

      if (!hasAccess) {
        const reason = getAccessDenialReason(
          userPermissions,
          entitlements as OrgEntitlements | null,
          moduleKey,
          action
        );

        // Determine enforcement level based on reason
        let level = EnforcementLevel.RBAC;
        if (reason?.includes('not enabled') || reason?.includes('Trial period')) {
          level = EnforcementLevel.ENTITLEMENT;
        }

        return {
          hasPermission: false,
          reason: reason || 'Access denied',
          enforcementLevel: level,
        };
      }

      return {
        hasPermission: true,
        enforcementLevel: EnforcementLevel.RBAC,
      };
    },
    [hasTenantContext, userPermissions, entitlements, checkIsSuperAdmin]
  );

  const checkSubmoduleAccess = useCallback(
    (
      moduleKey: string,
      submoduleKey: string,
      action: string = 'read'
    ): PermissionCheck => {
      // NEW: If permissions not loaded, treat as loading state
      if (userPermissions === null) {
        return {
          hasPermission: false,
          isLoading: true,
          reason: 'Permissions are loading',
          enforcementLevel: EnforcementLevel.RBAC,
        };
      }

      // Layer 1: Tenant - Allow super_admin without tenant context
      const isSuper = checkIsSuperAdmin();
      if (!hasTenantContext && !isSuper) {
        return {
          hasPermission: false,
          reason: 'Organization context is required',
          enforcementLevel: EnforcementLevel.TENANT,
        };
      }

      // Full bypass for super_admin
      if (isSuper) {
        return {
          hasPermission: true,
          enforcementLevel: EnforcementLevel.RBAC,
        };
      }

      // Perform combined check
      const hasAccess = canAccessSubmodule(
        userPermissions,
        entitlements as OrgEntitlements | null,
        moduleKey,
        submoduleKey,
        action
      );

      if (!hasAccess) {
        const reason = getAccessDenialReason(
          userPermissions,
          entitlements as OrgEntitlements | null,
          moduleKey,
          action
        );

        let level = EnforcementLevel.RBAC;
        if (reason?.includes('not enabled') || reason?.includes('Trial period')) {
          level = EnforcementLevel.ENTITLEMENT;
        }

        return {
          hasPermission: false,
          reason: reason || 'Access denied',
          enforcementLevel: level,
        };
      }

      return {
        hasPermission: true,
        enforcementLevel: EnforcementLevel.RBAC,
      };
    },
    [hasTenantContext, userPermissions, entitlements, checkIsSuperAdmin]
  );

  // ============================================================================
  // Utility Functions
  // ============================================================================

  const isLoading = useMemo(() => {
    return contextsLoading || entitlementsLoading || (authContext?.loading ?? true) || (authContext?.permissionsLoading ?? false);  // NEW: Include contextsLoading
  }, [contextsLoading, entitlementsLoading, authContext?.loading, authContext?.permissionsLoading]);

  const isReady = useMemo(() => {
    // For super_admin, ready even without tenant context
    const isSuper = checkIsSuperAdmin();
    return !isLoading && (hasTenantContext || isSuper) && user !== null && userPermissions !== null;
  }, [isLoading, hasTenantContext, user, userPermissions, checkIsSuperAdmin]);

  // ============================================================================
  // Return API
  // ============================================================================

  return {
    // State
    isLoading,
    isReady,
    user,
    organizationId,
    userPermissions,
    entitlements,

    // Layer 1: Tenant
    hasTenantContext,
    checkTenantAccess,

    // Layer 2: Entitlements
    checkModuleEntitled,
    checkSubmoduleEntitled,
    getModuleEntitlementStatus,

    // Layer 3: RBAC
    checkPermission,
    checkUserRole,
    checkIsSuperAdmin,
    checkIsOrgAdmin,
    checkCanManageRole,

    // Combined (All Layers)
    checkModuleAccess,
    checkSubmoduleAccess,
  };
}

/**
 * Hook for simple boolean permission check
 * Returns true/false without detailed reason
 */
export function useHasPermission(permission: string): boolean {
  const { checkPermission } = usePermissionCheck();
  return checkPermission(permission);
}

/**
 * Hook for simple module access check
 * Returns true/false without detailed reason
 */
export function useHasModuleAccess(
  moduleKey: string,
  action: string = 'read'
): boolean {
  const { checkModuleAccess } = usePermissionCheck();
  const result = checkModuleAccess(moduleKey, action);
  return result.hasPermission;
}

/**
 * Hook for checking multiple permissions
 * Returns object with individual check results
 */
export function useHasPermissions(permissions: string[]): Record<string, boolean> {
  const { checkPermission } = usePermissionCheck();

  return useMemo(() => {
    const results: Record<string, boolean> = {};
    for (const perm of permissions) {
      results[perm] = checkPermission(perm);
    }
    return results;
  }, [permissions, checkPermission]);
}
