// frontend/src/config/moduleBundleMap.ts

/**
 * Module bundle mapping for ModuleSelectionModal
 * Maps high-level bundles to specific module entitlements
 */

export interface BundleModule {
  key: string;
  displayName: string;
  modules: string[];
}

/**
 * Bundle to module mapping
 * - CRM → [sales, marketing]
 * - ERP → [master_data, vouchers, inventory, projects, tasks_calendar]
 * - Manufacturing → [manufacturing]
 * - Finance → [accounting, finance]
 * - Service → [service]
 * - HR → [hr] (legacy hr_management alias)
 * - Analytics → [reports_analytics, ai_analytics]
 */
export const MODULE_BUNDLES: BundleModule[] = [
  {
    key: 'crm',
    displayName: 'CRM',
    modules: ['sales', 'marketing'],
  },
  {
    key: 'erp',
    displayName: 'ERP',
    modules: ['master_data', 'vouchers', 'inventory', 'projects', 'tasks_calendar'],
  },
  {
    key: 'manufacturing',
    displayName: 'Manufacturing',
    modules: ['manufacturing'],
  },
  {
    key: 'finance',
    displayName: 'Finance',
    modules: ['accounting', 'finance'],
  },
  {
    key: 'service',
    displayName: 'Service',
    modules: ['service'],
  },
  {
    key: 'hr',
    displayName: 'HR',
    modules: ['hr'], // Maps to hr, not hr_management (legacy-safe)
  },
  {
    key: 'analytics',
    displayName: 'Analytics',
    modules: ['reports_analytics', 'ai_analytics'],
  },
];

/**
 * Get all modules for a set of selected bundles
 */
export function getBundleModules(selectedBundles: string[]): string[] {
  const modules = new Set<string>();
  
  selectedBundles.forEach((bundleKey) => {
    const bundle = MODULE_BUNDLES.find((b) => b.key === bundleKey);
    if (bundle) {
      bundle.modules.forEach((mod) => modules.add(mod));
    }
  });
  
  return Array.from(modules);
}

/**
 * Get bundles for a given module
 */
export function getModuleBundles(moduleKey: string): string[] {
  const bundles: string[] = [];
  
  MODULE_BUNDLES.forEach((bundle) => {
    if (bundle.modules.includes(moduleKey)) {
      bundles.push(bundle.key);
    }
  });
  
  return bundles;
}

/**
 * Get selected bundles from current module entitlements
 */
export function getSelectedBundlesFromModules(enabledModules: string[]): string[] {
  const selectedBundles = new Set<string>();
  
  MODULE_BUNDLES.forEach((bundle) => {
    // If all modules in the bundle are enabled, select the bundle
    const allEnabled = bundle.modules.every((mod) => enabledModules.includes(mod));
    if (allEnabled) {
      selectedBundles.add(bundle.key);
    }
  });
  
  return Array.from(selectedBundles);
}

/**
 * Compute module changes (diff) between current and target state
 */
export interface ModuleChange {
  module_key: string;
  status: 'enabled' | 'disabled';
}

export function computeModuleChanges(
  currentModules: string[],
  targetBundles: string[]
): ModuleChange[] {
  const targetModules = getBundleModules(targetBundles);
  const changes: ModuleChange[] = [];
  
  // Get all unique modules from all bundles
  const allModules = new Set<string>();
  MODULE_BUNDLES.forEach((bundle) => {
    bundle.modules.forEach((mod) => allModules.add(mod));
  });
  
  // Compute diff
  allModules.forEach((moduleKey) => {
    const currentlyEnabled = currentModules.includes(moduleKey);
    const shouldBeEnabled = targetModules.includes(moduleKey);
    
    if (currentlyEnabled !== shouldBeEnabled) {
      changes.push({
        module_key: moduleKey,
        status: shouldBeEnabled ? 'enabled' : 'disabled',
      });
    }
  });
  
  return changes;
}
