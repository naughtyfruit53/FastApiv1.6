/**
 * Menu Access Integration Tests
 * Tests for menu access evaluation with various entitlement scenarios
 */

import { evalMenuItemAccess, MenuAccessParams } from '../menuAccess';
import { AppEntitlementsResponse } from '../../services/entitlementsApi';

describe('Menu Access Evaluation', () => {
  describe('Module Entitlements', () => {
    it('should enable menu item when module is enabled', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        erp: {
          module_key: 'erp',
          status: 'enabled',
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'erp',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });

    it('should disable menu item when module is disabled', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        erp: {
          module_key: 'erp',
          status: 'disabled',
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'erp',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('disabled');
    });

    it('should enable menu item with trial badge when module is in trial', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        manufacturing: {
          module_key: 'manufacturing',
          status: 'trial',
          trial_expires_at: new Date(Date.now() + 86400000).toISOString(), // 1 day from now
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
      expect(result.isTrial).toBe(true);
    });

    it('should disable menu item when trial has expired', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        manufacturing: {
          module_key: 'manufacturing',
          status: 'trial',
          trial_expires_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'manufacturing',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('expired');
    });
  });

  describe('Submodule Entitlements', () => {
    it('should enable menu item when submodule is enabled', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        erp: {
          module_key: 'erp',
          status: 'enabled',
          submodules: {
            customers: true,
          },
        },
      };

      const params: MenuAccessParams = {
        requireSubmodule: { module: 'erp', submodule: 'customers' },
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });

    it('should disable menu item when submodule is disabled', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        erp: {
          module_key: 'erp',
          status: 'enabled',
          submodules: {
            customers: false,
          },
        },
      };

      const params: MenuAccessParams = {
        requireSubmodule: { module: 'erp', submodule: 'customers' },
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('disabled');
    });

    it('should inherit module status when submodule is not explicitly set', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        erp: {
          module_key: 'erp',
          status: 'enabled',
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireSubmodule: { module: 'erp', submodule: 'products' },
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });
  });

  describe('Special Cases', () => {
    it('should always enable email module', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {};

      const params: MenuAccessParams = {
        requireModule: 'email',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });

    it('should enable settings for super admin', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {};

      const params: MenuAccessParams = {
        requireModule: 'settings',
        entitlements,
        isAdmin: true,
        isSuperAdmin: true,
        orgId: null,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });

    it('should disable when entitlements are not loaded', () => {
      const params: MenuAccessParams = {
        requireModule: 'erp',
        entitlements: null,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('disabled');
      expect(result.reason).toContain('Loading');
    });

    it('should enable when no module requirement is specified', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {};

      const params: MenuAccessParams = {
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.result).toBe('enabled');
    });
  });

  describe('Error Messages', () => {
    it('should provide helpful error message for disabled module', () => {
      const entitlements: AppEntitlementsResponse['entitlements'] = {
        crm: {
          module_key: 'crm',
          status: 'disabled',
          submodules: {},
        },
      };

      const params: MenuAccessParams = {
        requireModule: 'crm',
        entitlements,
        isAdmin: false,
      };

      const result = evalMenuItemAccess(params);
      expect(result.reason).toContain('crm');
      expect(result.reason).toContain('disabled');
      expect(result.reason).toContain('administrator');
    });
  });
});
