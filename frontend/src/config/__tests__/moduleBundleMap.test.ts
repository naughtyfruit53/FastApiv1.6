// frontend/src/config/__tests__/moduleBundleMap.test.ts

import {
  MODULE_BUNDLES,
  getBundleModules,
  getModuleBundles,
  getSelectedBundlesFromModules,
  computeModuleChanges,
} from '../moduleBundleMap';

describe('moduleBundleMap', () => {
  describe('MODULE_BUNDLES', () => {
    it('should have all expected bundles', () => {
      const bundleKeys = MODULE_BUNDLES.map((b) => b.key);
      expect(bundleKeys).toContain('crm');
      expect(bundleKeys).toContain('erp');
      expect(bundleKeys).toContain('manufacturing');
      expect(bundleKeys).toContain('finance');
      expect(bundleKeys).toContain('service');
      expect(bundleKeys).toContain('hr');
      expect(bundleKeys).toContain('analytics');
    });

    it('should map CRM to sales and marketing', () => {
      const crm = MODULE_BUNDLES.find((b) => b.key === 'crm');
      expect(crm?.modules).toEqual(['sales', 'marketing']);
    });

    it('should map ERP to master_data, vouchers, inventory, projects, tasks_calendar', () => {
      const erp = MODULE_BUNDLES.find((b) => b.key === 'erp');
      expect(erp?.modules).toEqual([
        'master_data',
        'vouchers',
        'inventory',
        'projects',
        'tasks_calendar',
      ]);
    });

    it('should map Manufacturing to manufacturing', () => {
      const manufacturing = MODULE_BUNDLES.find((b) => b.key === 'manufacturing');
      expect(manufacturing?.modules).toEqual(['manufacturing']);
    });

    it('should map Finance to accounting and finance', () => {
      const finance = MODULE_BUNDLES.find((b) => b.key === 'finance');
      expect(finance?.modules).toEqual(['accounting', 'finance']);
    });

    it('should map Service to service', () => {
      const service = MODULE_BUNDLES.find((b) => b.key === 'service');
      expect(service?.modules).toEqual(['service']);
    });

    it('should map HR to hr (not hr_management)', () => {
      const hr = MODULE_BUNDLES.find((b) => b.key === 'hr');
      expect(hr?.modules).toEqual(['hr']);
    });

    it('should map Analytics to reports_analytics and ai_analytics', () => {
      const analytics = MODULE_BUNDLES.find((b) => b.key === 'analytics');
      expect(analytics?.modules).toEqual(['reports_analytics', 'ai_analytics']);
    });
  });

  describe('getBundleModules', () => {
    it('should return modules for selected bundles', () => {
      const modules = getBundleModules(['crm', 'erp']);
      expect(modules).toContain('sales');
      expect(modules).toContain('marketing');
      expect(modules).toContain('master_data');
      expect(modules).toContain('vouchers');
      expect(modules).toContain('inventory');
      expect(modules).toContain('projects');
      expect(modules).toContain('tasks_calendar');
    });

    it('should return empty array for no bundles', () => {
      const modules = getBundleModules([]);
      expect(modules).toEqual([]);
    });

    it('should return unique modules', () => {
      const modules = getBundleModules(['crm', 'crm']);
      expect(modules).toEqual(['sales', 'marketing']);
    });

    it('should handle unknown bundle keys gracefully', () => {
      const modules = getBundleModules(['unknown_bundle']);
      expect(modules).toEqual([]);
    });
  });

  describe('getModuleBundles', () => {
    it('should return bundles containing a module', () => {
      const bundles = getModuleBundles('sales');
      expect(bundles).toEqual(['crm']);
    });

    it('should return multiple bundles if module is in multiple bundles', () => {
      // Note: In current implementation, modules are unique to bundles
      // But this tests the logic if that changes
      const bundles = getModuleBundles('master_data');
      expect(bundles).toContain('erp');
    });

    it('should return empty array for unknown module', () => {
      const bundles = getModuleBundles('unknown_module');
      expect(bundles).toEqual([]);
    });
  });

  describe('getSelectedBundlesFromModules', () => {
    it('should return bundles when all their modules are enabled', () => {
      const bundles = getSelectedBundlesFromModules(['sales', 'marketing']);
      expect(bundles).toContain('crm');
    });

    it('should not return bundle if not all modules are enabled', () => {
      const bundles = getSelectedBundlesFromModules(['sales']); // Missing marketing
      expect(bundles).not.toContain('crm');
    });

    it('should return multiple bundles', () => {
      const bundles = getSelectedBundlesFromModules([
        'sales',
        'marketing',
        'manufacturing',
      ]);
      expect(bundles).toContain('crm');
      expect(bundles).toContain('manufacturing');
    });

    it('should return ERP bundle when all ERP modules are enabled', () => {
      const bundles = getSelectedBundlesFromModules([
        'master_data',
        'vouchers',
        'inventory',
        'projects',
        'tasks_calendar',
      ]);
      expect(bundles).toContain('erp');
    });

    it('should return empty array when no modules are enabled', () => {
      const bundles = getSelectedBundlesFromModules([]);
      expect(bundles).toEqual([]);
    });
  });

  describe('computeModuleChanges', () => {
    it('should compute enabled changes', () => {
      const changes = computeModuleChanges([], ['crm']);
      expect(changes).toContainEqual({
        module_key: 'sales',
        status: 'enabled',
      });
      expect(changes).toContainEqual({
        module_key: 'marketing',
        status: 'enabled',
      });
    });

    it('should compute disabled changes', () => {
      const changes = computeModuleChanges(['sales', 'marketing'], []);
      expect(changes).toContainEqual({
        module_key: 'sales',
        status: 'disabled',
      });
      expect(changes).toContainEqual({
        module_key: 'marketing',
        status: 'disabled',
      });
    });

    it('should compute no changes when state is same', () => {
      const changes = computeModuleChanges(['sales', 'marketing'], ['crm']);
      expect(changes).toEqual([]);
    });

    it('should compute mixed changes', () => {
      const changes = computeModuleChanges(
        ['sales', 'marketing'],
        ['erp', 'manufacturing']
      );
      
      // Should disable sales and marketing
      expect(changes).toContainEqual({
        module_key: 'sales',
        status: 'disabled',
      });
      expect(changes).toContainEqual({
        module_key: 'marketing',
        status: 'disabled',
      });
      
      // Should enable ERP modules
      expect(changes).toContainEqual({
        module_key: 'master_data',
        status: 'enabled',
      });
      expect(changes).toContainEqual({
        module_key: 'manufacturing',
        status: 'enabled',
      });
    });

    it('should handle complex scenario with multiple bundles', () => {
      const changes = computeModuleChanges(
        ['sales', 'marketing', 'manufacturing'],
        ['crm', 'finance']
      );
      
      // sales and marketing should remain (no change)
      expect(changes.find((c) => c.module_key === 'sales')).toBeUndefined();
      expect(changes.find((c) => c.module_key === 'marketing')).toBeUndefined();
      
      // manufacturing should be disabled
      expect(changes).toContainEqual({
        module_key: 'manufacturing',
        status: 'disabled',
      });
      
      // finance modules should be enabled
      expect(changes).toContainEqual({
        module_key: 'accounting',
        status: 'enabled',
      });
      expect(changes).toContainEqual({
        module_key: 'finance',
        status: 'enabled',
      });
    });
  });
});
