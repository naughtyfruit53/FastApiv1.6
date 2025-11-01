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
  entitlements: AppEntitlementsResponse | null | undefined;
  isAdmin: boolean; // org_admin or super_admin
  isSuperAdmin?: boolean;
}

/**
 * Evaluate menu item access based on entitlements
 * 
 * Rules:
 * - Super admin: always enabled
 * - Missing/disabled module:
 *   - Non-admin: disabled (show but not clickable)
 *   - Admin: disabled (with lock, tooltip, CTA)
 * - Trial module: enabled with "Trial" badge
 * - Submodule disabled: mirrors module rules
 * - Email: always enabled, irrespective of module
 * 
 * @param params Menu access parameters
 * @returns MenuItemAccess result
 */
export function evalMenuItemAccess(params: MenuAccessParams): MenuItemAccess {
  const { requireModule, requireSubmodule, entitlements, isAdmin: _isAdmin, isSuperAdmin } = params;

  // Super admin bypasses all checks
  if (isSuperAdmin) {
    return { result: 'enabled' };
  }

  // Special case: Email always enabled
  if (requireModule === 'email' || requireSubmodule?.module === 'email' || params.requireModule?.includes('email')) {
    return { result: 'enabled' };
  }

  // If no entitlement requirement, allow access
  if (!requireModule && !requireSubmodule) {
    return { result: 'enabled' };
  }

  // If entitlements not loaded yet, show as disabled temporarily
  if (!entitlements) {
    return { result: 'disabled', reason: 'Loading entitlements...' };
  }

  // Determine module and submodule to check
  const moduleKey = requireSubmodule ? requireSubmodule.module : requireModule;
  const submoduleKey = requireSubmodule?.submodule;

  if (!moduleKey) {
    // No requirement, allow access
    return { result: 'enabled' };
  }

  // Get module entitlement
  const moduleEnt = entitlements.entitlements[moduleKey];

  if (!moduleEnt || moduleEnt.status === 'disabled') {
    // Module is disabled or not found
    const reason = `Module '${moduleKey}' is disabled. Contact your administrator to enable it.`;
    return {
      result: 'disabled',
      reason,
    };
  }

  // Check if module is in trial
  const isTrial = moduleEnt.status === 'trial';
  const trialExpiresAt = moduleEnt.trial_expires_at ? new Date(moduleEnt.trial_expires_at) : null;

  // Check trial expiration
  if (isTrial && trialExpiresAt && trialExpiresAt < new Date()) {
    // Trial expired
    const reason = `Module '${moduleKey}' trial has expired. Please upgrade to continue using this feature.`;
    return {
      result: 'disabled',
      reason,
    };
  }

  // If checking submodule
  if (submoduleKey) {
    const submoduleEnabled = moduleEnt.submodules?.[submoduleKey];

    // If submodule entry doesn't exist, default to enabled (inherit from module)
    if (submoduleEnabled === undefined) {
      return {
        result: 'enabled',
        isTrial,
        trialExpiresAt,
      };
    }

    // Check if submodule is disabled
    if (submoduleEnabled === false) {
      const reason = `Feature '${submoduleKey}' is disabled. Contact your administrator to enable it.`;
      return {
        result: 'disabled',
        reason,
      };
    }
  }

  // Module/submodule is enabled or in trial
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