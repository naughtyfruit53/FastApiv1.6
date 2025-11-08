/**
 * Test strict menu access enforcement without fallback logic
 * Validates that super admins must have explicit entitlements and permissions
 */

import {
  evalMenuItemAccess,
  isMenuItemEnabled,
  isMenuItemVisible,
  getMenuItemBadge,
  getMenuItemTooltip,
  MenuAccessParams,
} from '../menuAccess';
import { AppEntitlementsResponse } from '../../services/entitlementsApi';

describe('menuAccess - Strict Enforcement', () => {
  describe('Super Admin - No Bypass', () => {
    it('should deny super admin access to disabled module', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          sales: {
            status: 'disabled',
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'sales',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      // Super admin should be DENIED access to disabled module
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('sales');
      expect(result.reason).toContain('disabled');
    });

    it('should deny super admin access to missing module', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      // Super admin should be DENIED access to missing module
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('manufacturing');
    });

    it('should grant super admin access only when module is enabled', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          inventory: {
            status: 'enabled',
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'inventory',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      // Super admin should be GRANTED access only with explicit entitlement
      expect(result.result).toBe('enabled');
    });
  });

  describe('Module Entitlement Checks', () => {
    it('should disable menu item when module is disabled', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          crm: {
            status: 'disabled',
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'crm',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('crm');
      expect(result.reason).toContain('disabled');
    });

    it('should disable menu item when module is missing', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        requireModule: 'hr',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('hr');
    });

    it('should enable menu item when module is enabled', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          finance: {
            status: 'enabled',
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'finance',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('enabled');
    });
  });

  describe('Submodule Entitlement Checks', () => {
    it('should disable menu item when submodule is disabled', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          crm: {
            status: 'enabled',
            submodules: {
              lead_management: false,
            },
          },
        },
      };

      const params: MenuAccessParams = {
        requireSubmodule: { module: 'crm', submodule: 'lead_management' },
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('lead_management');
    });

    it('should deny super admin access to disabled submodule', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          sales: {
            status: 'enabled',
            submodules: {
              quotations: false,
            },
          },
        },
      };

      const params: MenuAccessParams = {
        requireSubmodule: { module: 'sales', submodule: 'quotations' },
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      // Super admin should be DENIED access to disabled submodule
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('quotations');
    });
  });

  describe('Email Module - Always Enabled', () => {
    it('should always enable email for super admin', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        requireModule: 'email',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('enabled');
    });

    it('should always enable email for regular user', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        requireModule: 'email',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('enabled');
    });
  });

  describe('Trial Module Handling', () => {
    it('should enable menu item for trial module', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          manufacturing: {
            status: 'trial',
            trial_expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('enabled');
      expect(result.isTrial).toBe(true);
    });

    it('should disable menu item for expired trial', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          analytics: {
            status: 'trial',
            trial_expires_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'analytics',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('expired');
    });
  });

  describe('Loading State', () => {
    it('should show disabled with loading message when entitlements not loaded', () => {
      const params: MenuAccessParams = {
        requireModule: 'sales',
        entitlements: null,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('Loading');
    });

    it('should show disabled even for super admin when entitlements loading', () => {
      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements: null,
        isAdmin: true,
        isSuperAdmin: true,
      };

      const result = evalMenuItemAccess(params);

      // Super admin should also wait for entitlements to load
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('Loading');
    });
  });

  describe('Helper Functions', () => {
    it('isMenuItemEnabled should return false for disabled module', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          sales: { status: 'disabled', submodules: {} },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'sales',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
      };

      // Should be disabled even for super admin
      expect(isMenuItemEnabled(params)).toBe(false);
    });

    it('isMenuItemVisible should return true (items always visible)', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        requireModule: 'sales',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      // Items are always visible (just disabled)
      expect(isMenuItemVisible(params)).toBe(true);
    });

    it('getMenuItemBadge should return "Trial" for trial modules', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          manufacturing: {
            status: 'trial',
            trial_expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            submodules: {},
          },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      expect(getMenuItemBadge(params)).toBe('Trial');
    });

    it('getMenuItemTooltip should return reason for disabled items', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {
          hr: { status: 'disabled', submodules: {} },
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'hr',
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const tooltip = getMenuItemTooltip(params);
      expect(tooltip).toBeTruthy();
      expect(tooltip).toContain('hr');
      expect(tooltip).toContain('disabled');
    });
  });

  describe('No Requirement Cases', () => {
    it('should enable items with no module requirement', () => {
      const entitlements: AppEntitlementsResponse = {
        organization_id: 1,
        entitlements: {},
      };

      const params: MenuAccessParams = {
        entitlements,
        isAdmin: false,
        isSuperAdmin: false,
      };

      const result = evalMenuItemAccess(params);

      expect(result.result).toBe('enabled');
    });
  });
});
