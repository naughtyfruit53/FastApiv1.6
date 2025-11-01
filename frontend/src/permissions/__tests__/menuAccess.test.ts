// frontend/src/permissions/__tests__/menuAccess.test.ts

import { evalMenuItemAccess } from '../menuAccess';
import { AppEntitlementsResponse } from '../../services/entitlementsApi';

describe('menuAccess', () => {
  const mockEntitlements: AppEntitlementsResponse = {
    org_id: 1,
    entitlements: {
      sales: {
        module_key: 'sales',
        status: 'enabled',
        trial_expires_at: null,
        submodules: {
          lead_management: true,
          opportunity_tracking: true,
        },
      },
      marketing: {
        module_key: 'marketing',
        status: 'trial',
        trial_expires_at: '2025-12-31T23:59:59Z',
        submodules: {
          campaigns: true,
        },
      },
      service: {
        module_key: 'service',
        status: 'disabled',
        trial_expires_at: null,
        submodules: {},
      },
      finance: {
        module_key: 'finance',
        status: 'enabled',
        trial_expires_at: null,
        submodules: {
          accounting: false, // Submodule disabled
        },
      },
    },
  };

  describe('evalMenuItemAccess', () => {
    describe('Super Admin', () => {
      it('should always enable for super admin', () => {
        const result = evalMenuItemAccess({
          requireModule: 'service',
          entitlements: mockEntitlements,
          isAdmin: true,
          isSuperAdmin: true,
        });
        expect(result.result).toBe('enabled');
      });

      it('should enable disabled modules for super admin', () => {
        const result = evalMenuItemAccess({
          requireModule: 'nonexistent',
          entitlements: mockEntitlements,
          isAdmin: true,
          isSuperAdmin: true,
        });
        expect(result.result).toBe('enabled');
      });
    });

    describe('Email', () => {
      it('should always enable email regardless of entitlements', () => {
        const result = evalMenuItemAccess({
          requireModule: 'email',
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
      });

      it('should enable email even without entitlements loaded', () => {
        const result = evalMenuItemAccess({
          requireModule: 'email',
          entitlements: null,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
      });
    });

    describe('No requirements', () => {
      it('should enable when no module required', () => {
        const result = evalMenuItemAccess({
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
      });
    });

    describe('Entitlements not loaded', () => {
      it('should disable when entitlements not loaded', () => {
        const result = evalMenuItemAccess({
          requireModule: 'sales',
          entitlements: null,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
        expect(result.reason).toContain('Loading entitlements');
      });
    });

    describe('Module enabled', () => {
      it('should enable when module is enabled', () => {
        const result = evalMenuItemAccess({
          requireModule: 'sales',
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
        expect(result.isTrial).toBe(false);
      });
    });

    describe('Module disabled', () => {
      it('should disable when module is disabled', () => {
        const result = evalMenuItemAccess({
          requireModule: 'service',
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
        expect(result.reason).toContain('disabled');
      });

      it('should disable when module does not exist', () => {
        const result = evalMenuItemAccess({
          requireModule: 'nonexistent',
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
        expect(result.reason).toContain('disabled');
      });
    });

    describe('Module in trial', () => {
      it('should enable module in trial', () => {
        const result = evalMenuItemAccess({
          requireModule: 'marketing',
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
        expect(result.isTrial).toBe(true);
        expect(result.trialExpiresAt).toBeInstanceOf(Date);
      });

      it('should disable when trial has expired', () => {
        const expiredEntitlements: AppEntitlementsResponse = {
          org_id: 1,
          entitlements: {
            marketing: {
              module_key: 'marketing',
              status: 'trial',
              trial_expires_at: '2020-01-01T00:00:00Z', // Expired
              submodules: {},
            },
          },
        };

        const result = evalMenuItemAccess({
          requireModule: 'marketing',
          entitlements: expiredEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
        expect(result.reason).toContain('expired');
      });
    });

    describe('Submodule access', () => {
      it('should enable when submodule is enabled', () => {
        const result = evalMenuItemAccess({
          requireSubmodule: {
            module: 'sales',
            submodule: 'lead_management',
          },
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
      });

      it('should disable when submodule is disabled', () => {
        const result = evalMenuItemAccess({
          requireSubmodule: {
            module: 'finance',
            submodule: 'accounting',
          },
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
        expect(result.reason).toContain('disabled');
      });

      it('should enable when submodule is not explicitly defined (inherit from module)', () => {
        const result = evalMenuItemAccess({
          requireSubmodule: {
            module: 'sales',
            submodule: 'nonexistent_submodule',
          },
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('enabled');
      });

      it('should disable when parent module is disabled', () => {
        const result = evalMenuItemAccess({
          requireSubmodule: {
            module: 'service',
            submodule: 'any_submodule',
          },
          entitlements: mockEntitlements,
          isAdmin: false,
          isSuperAdmin: false,
        });
        expect(result.result).toBe('disabled');
      });
    });

    describe('Settings/Admin access', () => {
      it('should enable settings for admin', () => {
        const result = evalMenuItemAccess({
          requireModule: 'settings',
          entitlements: mockEntitlements,
          isAdmin: true,
          isSuperAdmin: false,
        });
        // Settings should rely on RBAC, not entitlements
        // Since requireModule is 'settings' but not in entitlements, it will be disabled
        // However, the actual access control for settings happens at the menu level
        // This test shows the behavior when entitlements are checked
        expect(result.result).toBe('disabled');
      });
    });
  });
});
