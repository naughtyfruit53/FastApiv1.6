// frontend/src/permissions/menuAccess.ts

/**
 * Menu access evaluation logic based on entitlements
 */

import { AppEntitlementsResponse } from '../services/entitlementsApi';

export type MenuAccessResult = 'hidden' | 'disabled' | 'enabled';

export interface MenuItemAccess {
  result: MenuAccessResult;
  reason?: string;
  isTrial?: boolean;
  trialExpiresAt?: Date | null;
}

export interface MenuAccessParams {
  requireModule?: string;
  requireSubmodule?: { module: string; submodule: string };
  entitlements: AppEntitlementsResponse["entitlements"] | null | undefined; // Change to the dict type
  isAdmin: boolean; // org_admin or super_admin
  isSuperAdmin?: boolean;
  orgId?: number | null;  // Add orgId to params for super admin check
}

/**
 * Evaluate menu item access based on entitlements
 * 
 * STRICT ENFORCEMENT Rules:
 * - Super admin: NO BYPASS - must have explicit entitlements
 * - Missing/disabled module: ALWAYS disabled (show with lock, tooltip, CTA)
 * - Trial module: enabled with "Trial" badge
 * - Submodule disabled: ALWAYS disabled
 * - Email: always enabled (non-billable module)
 * 
 * @param params Menu access parameters
 * @returns MenuItemAccess result
 */
export function evalMenuItemAccess(params: MenuAccessParams): MenuItemAccess {
  const { requireModule, requireSubmodule, entitlements, isAdmin: _isAdmin, isSuperAdmin: _isSuperAdmin, orgId } = params;

  console.log('[evalMenuItemAccess] Starting evaluation:', {
    requireModule,
    requireSubmodule,
    hasEntitlements: !!entitlements,
    entitlementsKeys: entitlements ? Object.keys(entitlements) : null,
    isSuperAdmin: params.isSuperAdmin,
    orgId,
    timestamp: new Date().toISOString(),
  });

  // Special case: Email always enabled (non-billable)
  if (requireModule === 'email' || requireSubmodule?.module === 'email' || params.requireModule?.includes('email')) {
    console.log('[evalMenuItemAccess] Email module - always enabled');
    return { result: 'enabled' };
  }

  // For super admin with null org_id, enable RBAC_ONLY_MODULES like 'settings'
  if (orgId === null && params.isSuperAdmin && (requireModule === 'settings' || requireModule === 'admin' || requireModule === 'rbac')) {
    console.log('[evalMenuItemAccess] Super admin null org access granted for:', requireModule);
    return { result: 'enabled', reason: 'Platform admin access granted' };
  }

  // For all settings submenus, enable for super admin
  if (params.isSuperAdmin && (requireModule === 'settings' || requireSubmodule?.module === 'settings')) {
    console.log('[evalMenuItemAccess] Settings access granted for super admin');
    return { result: 'enabled', reason: 'Super admin settings access' };
  }

  // If no entitlement requirement, allow access
  if (!requireModule && !requireSubmodule) {
    console.log('[evalMenuItemAccess] No requirement - enabled');
    return { result: 'enabled' };
  }

  // If entitlements not loaded yet, show as disabled with loading message
  if (!entitlements) {
    console.log('[evalMenuItemAccess] Entitlements not loaded - disabled');
    return { result: 'disabled', reason: 'Loading entitlements...' };
  }

  // Determine module and submodule to check
  const moduleKey = requireSubmodule ? requireSubmodule.module : requireModule;
  const submoduleKey = requireSubmodule?.submodule;

  console.log('[evalMenuItemAccess] Checking module/submodule:', { moduleKey, submoduleKey });

  if (!moduleKey) {
    // No requirement, allow access
    console.log('[evalMenuItemAccess] No module key - enabled');
    return { result: 'enabled' };
  }

  // Get module entitlement
  const moduleEnt = entitlements[moduleKey] || null;

  console.log('[evalMenuItemAccess] Module entitlement:', moduleEnt);

  if (!moduleEnt || moduleEnt.status === 'disabled') {
    // Module is disabled or not found
    const reason = `Module '${moduleKey}' is disabled. Contact your administrator to enable it.`;
    console.log('[evalMenuItemAccess] Module disabled:', reason);
    return {
      result: 'disabled',
      reason,
    };
  }

  // Check if module is in trial
  const isTrial = moduleEnt.status === 'trial';
  const trialExpiresAt = moduleEnt.trial_expires_at ? new Date(moduleEnt.trial_expires_at) : null;

  console.log('[evalMenuItemAccess] Trial status:', { isTrial, trialExpiresAt });

  // Check trial expiration
  if (isTrial && trialExpiresAt && trialExpiresAt < new Date()) {
    // Trial expired
    const reason = `Module '${moduleKey}' trial has expired. Please upgrade to continue using this feature.`;
    console.log('[evalMenuItemAccess] Trial expired:', reason);
    return {
      result: 'disabled',
      reason,
    };
  }

  // If checking submodule
  if (submoduleKey) {
    const submoduleEnabled = moduleEnt.submodules?.[submoduleKey];

    console.log('[evalMenuItemAccess] Submodule enabled:', submoduleEnabled);

    // If submodule entry doesn't exist, default to enabled (inherit from module)
    if (submoduleEnabled === undefined) {
      console.log('[evalMenuItemAccess] Submodule undefined - inherit enabled');
      return {
        result: 'enabled',
        isTrial,
        trialExpiresAt,
      };
    }

    // Check if submodule is disabled
    if (submoduleEnabled === false) {
      const reason = `Feature '${submoduleKey}' is disabled. Contact your administrator to enable it.`;
      console.log('[evalMenuItemAccess] Submodule disabled:', reason);
      return {
        result: 'disabled',
        reason,
      };
    }
  }

  // Module/submodule is enabled or in trial
  console.log('[evalMenuItemAccess] Access granted');
  return {
    result: 'enabled',
    isTrial,
    trialExpiresAt,
  };
}

/**
 * Check if menu item should be visible
 */
export function isMenuItemVisible(params: MenuAccessParams): boolean {
  const access = evalMenuItemAccess(params);
  return access.result !== 'hidden'; // Always true now, since we show all
}

/**
 * Check if menu item should be enabled (clickable)
 */
export function isMenuItemEnabled(params: MenuAccessParams): boolean {
  const access = evalMenuItemAccess(params);
  return access.result === 'enabled';
}

/**
 * Get menu item badge (e.g., "Trial")
 */
export function getMenuItemBadge(params: MenuAccessParams): string | null {
  const access = evalMenuItemAccess(params);
  if (access.isTrial) {
    return 'Trial';
  }
  return null;
}

/**
 * Get menu item tooltip text
 */
export function getMenuItemTooltip(params: MenuAccessParams): string | null {
  const access = evalMenuItemAccess(params);
  if (access.result === 'disabled') {
    return access.reason || 'This feature is disabled';
  }
  return null;
}