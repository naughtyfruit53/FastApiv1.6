// frontend/src/config/moduleBundleMap.ts

/**
 * Module bundle mapping for ModuleSelectionModal
 * Maps high-level bundles to specific module entitlements
 */

export interface BundleModule {
  key: string;
  displayName: string;
  submodules: string[]; // Renamed from modules to submodules for clarity
}

/**
 * Bundle to module mapping
 * Bundle key is the module_key, submodules are descriptive
 * - crm: sales, marketing
 * - erp: master_data, vouchers, inventory, projects, tasks_calendar
 * - manufacturing: manufacturing
 * - finance: accounting, finance
 * - service: service
 * - hr: hr
 * - analytics: reports_analytics, ai_analytics
 */
export const MODULE_BUNDLES: BundleModule[] = [
  {
    key: 'crm',
    displayName: 'CRM',
    submodules: ['sales', 'marketing'],
  },
  {
    key: 'erp',
    displayName: 'ERP',
    submodules: ['master_data', 'vouchers', 'inventory', 'projects', 'tasks_calendar'],
  },
  {
    key: 'manufacturing',
    displayName: 'Manufacturing',
    submodules: ['manufacturing'],
  },
  {
    key: 'finance',
    displayName: 'Finance',
    submodules: ['accounting', 'finance'],
  },
  {
    key: 'service',
    displayName: 'Service',
    submodules: ['service'],
  },
  {
    key: 'hr',
    displayName: 'HR',
    submodules: ['hr'],
  },
  {
    key: 'analytics',
    displayName: 'Analytics',
    submodules: ['reports_analytics', 'ai_analytics'],
  },
];

/**
 * Get all module_keys for a set of selected bundles
 */
export function getBundleModules(selectedBundles: string[]): string[] {
  return selectedBundles; // Now returns the bundle keys, which are module_keys
}

/**
 * Get bundles for a given module
 */
export function getModuleBundles(moduleKey: string): string[] {
  const bundles: string[] = [];
  
  MODULE_BUNDLES.forEach((bundle) => {
    if (bundle.key === moduleKey) { // Check against key
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
    // If the bundle's key (module_key) is enabled, select the bundle
    if (enabledModules.includes(bundle.key)) {
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
  
  // Get all unique module_keys from bundles
  const allModules = new Set<string>(MODULE_BUNDLES.map(b => b.key));
  
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