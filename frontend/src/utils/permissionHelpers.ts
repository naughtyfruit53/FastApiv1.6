// frontend/src/utils/permissionHelpers.ts

/**
 * Permission checking utilities for 3-layer security model
 * Provides standardized functions for checking permissions, entitlements, and tenant access
 */

import {
  UserRole,
  ModuleStatus,
  SUPER_ADMIN_ROLES,
  ORG_ADMIN_ROLES,
  RBAC_ONLY_MODULES,
  ALWAYS_ON_MODULES,
  getRoleLevel,
  isModuleEnabled as checkModuleEnabled,
  type UserPermissions,
  type ModuleEntitlement,
  type OrgEntitlements,
} from '../constants/rbac';

// ============================================================================
// ROLE CHECKING (Layer 3 - RBAC)
// ============================================================================

/**
 * Check if user is super admin
 */
export function isSuperAdmin(role: string | undefined): boolean {
  if (!role) return false;
  return SUPER_ADMIN_ROLES.has(role);
}

/**
 * Check if user is organization admin
 */
export function isOrgAdmin(role: string | undefined): boolean {
  if (!role) return false;
  return ORG_ADMIN_ROLES.has(role);
}

/**
 * Check if user can manage another role
 */
export function canManageRole(managerRole: string, targetRole: string): boolean {
  return getRoleLevel(managerRole) > getRoleLevel(targetRole);
}

/**
 * Check if user has specific permission
 */
export function hasPermission(
  userPermissions: UserPermissions | null,
  permission: string
): boolean {
  if (!userPermissions) return false;

  // Super admins bypass permission checks
  if (isSuperAdmin(userPermissions.role)) {
    return true;
  }

  // Check exact match
  if (userPermissions.permissions.includes(permission)) {
    return true;
  }

  // Check wildcard match (e.g., "crm.*" matches "crm.read")
  for (const perm of userPermissions.permissions) {
    if (perm.endsWith('.*')) {
      const module = perm.slice(0, -2);
      if (permission.startsWith(`${module}.`)) {
        return true;
      }
    }
  }

  return false;
}

/**
 * Check if user has any of the specified permissions
 */
export function hasAnyPermission(
  userPermissions: UserPermissions | null,
  permissions: string[]
): boolean {
  return permissions.some((perm) => hasPermission(userPermissions, perm));
}

/**
 * Check if user has all specified permissions
 */
export function hasAllPermissions(
  userPermissions: UserPermissions | null,
  permissions: string[]
): boolean {
  return permissions.every((perm) => hasPermission(userPermissions, perm));
}

/**
 * Get user's accessible modules based on permissions
 */
export function getAccessibleModules(
  userPermissions: UserPermissions | null
): Set<string> {
  if (!userPermissions) return new Set();

  const modules = new Set<string>();

  // Extract modules from permissions
  for (const perm of userPermissions.permissions) {
    if (perm.includes('.')) {
      const module = perm.split('.')[0];
      modules.add(module);
    } else if (perm.includes('_')) {
      // Handle format like "crm_admin"
      const module = perm.split('_')[0];
      modules.add(module);
    }
  }

  return modules;
}

// ============================================================================
// ENTITLEMENT CHECKING (Layer 2)
// ============================================================================

/**
 * Check if module is always-on (doesn't require entitlement)
 */
export function isAlwaysOnModule(moduleKey: string): boolean {
  return ALWAYS_ON_MODULES.has(moduleKey.toLowerCase());
}

/**
 * Check if module is RBAC-only (permissions only, no entitlement check)
 */
export function isRBACOnlyModule(moduleKey: string): boolean {
  return RBAC_ONLY_MODULES.has(moduleKey.toLowerCase());
}

/**
 * Check if entitlement check is required for module
 */
export function shouldCheckEntitlement(moduleKey: string): boolean {
  return !isAlwaysOnModule(moduleKey) && !isRBACOnlyModule(moduleKey);
}

/**
 * Check if module is entitled (enabled or trial)
 */
export function isModuleEntitled(
  entitlements: OrgEntitlements | null,
  moduleKey: string
): boolean {
  if (!entitlements) return false;

  // Always-on modules are always entitled
  if (isAlwaysOnModule(moduleKey)) {
    return true;
  }

  // RBAC-only modules don't require entitlement
  if (isRBACOnlyModule(moduleKey)) {
    return true;
  }

  const module = entitlements.entitlements[moduleKey.toLowerCase()];
  if (!module) return false;

  return checkModuleEnabled(module.status, module.trial_expires_at);
}

/**
 * Check if submodule is entitled
 */
export function isSubmoduleEntitled(
  entitlements: OrgEntitlements | null,
  moduleKey: string,
  submoduleKey: string
): boolean {
  if (!entitlements) return false;

  // First check if module is entitled
  if (!isModuleEntitled(entitlements, moduleKey)) {
    return false;
  }

  const module = entitlements.entitlements[moduleKey.toLowerCase()];
  if (!module) return false;

  // If no submodules defined, default to entitled
  if (!module.submodules || !(submoduleKey in module.submodules)) {
    return true;
  }

  return module.submodules[submoduleKey] === true;
}

/**
 * Get module status
 */
export function getModuleStatus(
  entitlements: OrgEntitlements | null,
  moduleKey: string
): ModuleStatus {
  if (!entitlements) return ModuleStatus.UNKNOWN;

  if (isAlwaysOnModule(moduleKey)) {
    return ModuleStatus.ENABLED;
  }

  if (isRBACOnlyModule(moduleKey)) {
    return ModuleStatus.ENABLED;
  }

  const module = entitlements.entitlements[moduleKey.toLowerCase()];
  return (module?.status as ModuleStatus) || ModuleStatus.UNKNOWN;
}

/**
 * Check if module is in trial period
 */
export function isModuleTrial(
  entitlements: OrgEntitlements | null,
  moduleKey: string
): boolean {
  if (!entitlements) return false;

  const module = entitlements.entitlements[moduleKey.toLowerCase()];
  return module?.status === ModuleStatus.TRIAL;
}

/**
 * Get trial expiry date for module
 */
export function getTrialExpiry(
  entitlements: OrgEntitlements | null,
  moduleKey: string
): Date | null {
  if (!entitlements) return null;

  const module = entitlements.entitlements[moduleKey.toLowerCase()];
  if (module?.status === ModuleStatus.TRIAL && module.trial_expires_at) {
    return new Date(module.trial_expires_at);
  }

  return null;
}

/**
 * Get all entitled modules
 */
export function getEntitledModules(
  entitlements: OrgEntitlements | null
): Set<string> {
  if (!entitlements) return new Set();

  const modules = new Set<string>();

  for (const [moduleKey, module] of Object.entries(entitlements.entitlements)) {
    if (checkModuleEnabled(module.status, module.trial_expires_at)) {
      modules.add(moduleKey);
    }
  }

  return modules;
}

// ============================================================================
// COMBINED CHECKING (All 3 Layers)
// ============================================================================

/**
 * Check if user can access module (entitlement + permission)
 */
export function canAccessModule(
  userPermissions: UserPermissions | null,
  entitlements: OrgEntitlements | null,
  moduleKey: string,
  action: string = 'read'
): boolean {
  // Super admins bypass all checks
  if (userPermissions && isSuperAdmin(userPermissions.role)) {
    return true;
  }

  // Layer 2: Check entitlement
  if (shouldCheckEntitlement(moduleKey)) {
    if (!isModuleEntitled(entitlements, moduleKey)) {
      return false;
    }
  }

  // Layer 3: Check permission
  const permission = `${moduleKey}.${action}`;
  if (!hasPermission(userPermissions, permission)) {
    return false;
  }

  return true;
}

/**
 * Check if user can access submodule (entitlement + permission)
 */
export function canAccessSubmodule(
  userPermissions: UserPermissions | null,
  entitlements: OrgEntitlements | null,
  moduleKey: string,
  submoduleKey: string,
  action: string = 'read'
): boolean {
  // Super admins bypass all checks
  if (userPermissions && isSuperAdmin(userPermissions.role)) {
    return true;
  }

  // Layer 2: Check entitlement
  if (shouldCheckEntitlement(moduleKey)) {
    if (!isSubmoduleEntitled(entitlements, moduleKey, submoduleKey)) {
      return false;
    }
  }

  // Layer 3: Check permission
  const permission = `${moduleKey}_${submoduleKey}_access`;
  if (!hasPermission(userPermissions, permission)) {
    // Fallback to module-level permission
    const modulePermission = `${moduleKey}.${action}`;
    if (!hasPermission(userPermissions, modulePermission)) {
      return false;
    }
  }

  return true;
}

/**
 * Filter menu items based on entitlements and permissions
 */
export function filterMenuItems<T extends { moduleKey?: string; permission?: string }>(
  items: T[],
  userPermissions: UserPermissions | null,
  entitlements: OrgEntitlements | null
): T[] {
  return items.filter((item) => {
    // Check permission if specified
    if (item.permission && !hasPermission(userPermissions, item.permission)) {
      return false;
    }

    // Check entitlement if module key specified
    if (item.moduleKey) {
      if (shouldCheckEntitlement(item.moduleKey)) {
        if (!isModuleEntitled(entitlements, item.moduleKey)) {
          return false;
        }
      }
    }

    return true;
  });
}

/**
 * Get denial reason for module access
 */
export function getAccessDenialReason(
  userPermissions: UserPermissions | null,
  entitlements: OrgEntitlements | null,
  moduleKey: string,
  action: string = 'read'
): string | null {
  // Super admins always have access
  if (userPermissions && isSuperAdmin(userPermissions.role)) {
    return null;
  }

  // Check entitlement
  if (shouldCheckEntitlement(moduleKey)) {
    if (!isModuleEntitled(entitlements, moduleKey)) {
      const status = getModuleStatus(entitlements, moduleKey);
      if (status === ModuleStatus.TRIAL) {
        return `Trial period for module '${moduleKey}' has expired`;
      }
      return `Module '${moduleKey}' is not enabled for your organization`;
    }
  }

  // Check permission
  const permission = `${moduleKey}.${action}`;
  if (!hasPermission(userPermissions, permission)) {
    return `You do not have '${permission}' permission for this action`;
  }

  return null;
}

// ============================================================================
// TENANT CHECKING (Layer 1)
// ============================================================================

/**
 * Validate organization ID is set
 */
export function validateOrgContext(orgId: number | null | undefined): boolean {
  return orgId !== null && orgId !== undefined && orgId > 0;
}

/**
 * Check if user belongs to organization
 */
export function userBelongsToOrg(
  userOrgId: number | null | undefined,
  targetOrgId: number | null | undefined
): boolean {
  if (!validateOrgContext(userOrgId) || !validateOrgContext(targetOrgId)) {
    return false;
  }
  return userOrgId === targetOrgId;
}
