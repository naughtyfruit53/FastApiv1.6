// frontend/src/utils/permissionNormalizer.ts

/**
 * Permission Normalization Utility
 * 
 * Backend returns permissions with actions like: *.read, *.manage, *.list, *.access
 * Frontend menuConfig expects: *.view
 * 
 * This utility normalizes backend permissions to work with frontend permission checks.
 */

interface NormalizedPermissions {
  permissions: string[];
  modules: Set<string>;
  submodules: Record<string, Set<string>>;
}

/**
 * Normalizes backend permissions to frontend-compatible format
 * 
 * Rules:
 * 1. *.read, *.list, *.access, *.manage → *.view
 * 2. If any permission exists in a module namespace, grant module.view
 * 3. Extract modules and submodules from permission strings
 * 
 * @param backendPermissions Array of permission strings from backend
 * @returns Normalized permissions object
 */
export function normalizePermissions(backendPermissions: string[]): NormalizedPermissions {
  const normalized = new Set<string>();
  const modules = new Set<string>();
  const submodules: Record<string, Set<string>> = {};

  // Mapping of backend actions to frontend actions
  const actionMapping: Record<string, string> = {
    'read': 'view',
    'list': 'view',
    'access': 'view',
    'manage': 'view',
    'write': 'create',
    'update': 'edit',
    'delete': 'delete',
    'create': 'create',
    'edit': 'edit',
  };

  for (const permission of backendPermissions) {
    // Add original permission
    normalized.add(permission);

    // Parse permission: "module.action" or "module_submodule.action"
    const parts = permission.split('.');
    if (parts.length < 2) continue;

    const action = parts[parts.length - 1];
    const resourcePath = parts.slice(0, -1).join('.');

    // Normalize action
    const normalizedAction = actionMapping[action] || action;
    const normalizedPermission = `${resourcePath}.${normalizedAction}`;
    normalized.add(normalizedPermission);

    // Extract module and submodule
    const resourceParts = resourcePath.split('_');
    const module = resourceParts[0];
    
    // Add module
    modules.add(module);

    // Add module.view if any permission exists in this module
    normalized.add(`${module}.view`);

    // Handle submodules
    if (resourceParts.length > 1) {
      const submodule = resourceParts.slice(1).join('_');
      if (!submodules[module]) {
        submodules[module] = new Set<string>();
      }
      submodules[module].add(submodule);
    }
  }

  return {
    permissions: Array.from(normalized),
    modules,
    submodules,
  };
}

// Cache for normalized permissions to avoid repeated processing
const normalizationCache = new WeakMap<string[], NormalizedPermissions>();

/**
 * Checks if a user has a specific permission after normalization
 * Uses memoization to avoid repeated normalization of the same permission set
 * 
 * @param userPermissions Array of user's permissions
 * @param requiredPermission Permission to check
 * @returns boolean
 */
export function hasNormalizedPermission(
  userPermissions: string[],
  requiredPermission: string
): boolean {
  // Try to get cached normalized permissions
  let normalized = normalizationCache.get(userPermissions);
  
  if (!normalized) {
    // Cache miss - normalize and cache
    normalized = normalizePermissions(userPermissions);
    normalizationCache.set(userPermissions, normalized);
  }
  
  // Check exact match
  if (normalized.permissions.includes(requiredPermission)) {
    return true;
  }

  // Check wildcard permissions (e.g., 'finance.*' matches 'finance.view')
  const [module, action] = requiredPermission.split('.');
  if (normalized.permissions.includes(`${module}.*`)) {
    return true;
  }

  return false;
}

/**
 * Checks if a user has access to a module
 * 
 * @param userPermissions Array of user's permissions
 * @param module Module name
 * @returns boolean
 */
export function hasModuleAccess(
  userPermissions: string[],
  module: string
): boolean {
  const normalized = normalizePermissions(userPermissions);
  return normalized.modules.has(module);
}

/**
 * Checks if a user has access to a submodule
 * 
 * @param userPermissions Array of user's permissions
 * @param module Module name
 * @param submodule Submodule name
 * @returns boolean
 */
export function hasSubmoduleAccess(
  userPermissions: string[],
  module: string,
  submodule: string
): boolean {
  const normalized = normalizePermissions(userPermissions);
  return normalized.submodules[module]?.has(submodule) || false;
}

/**
 * Gets all modules a user has access to
 * 
 * @param userPermissions Array of user's permissions
 * @returns Array of module names
 */
export function getUserModules(userPermissions: string[]): string[] {
  const normalized = normalizePermissions(userPermissions);
  return Array.from(normalized.modules);
}

/**
 * Gets all submodules a user has access to for a specific module
 * 
 * @param userPermissions Array of user's permissions
 * @param module Module name
 * @returns Array of submodule names
 */
export function getUserSubmodules(
  userPermissions: string[],
  module: string
): string[] {
  const normalized = normalizePermissions(userPermissions);
  return Array.from(normalized.submodules[module] || []);
}
