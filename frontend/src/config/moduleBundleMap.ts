// frontend/src/config/moduleBundleMap.ts

/**
 * Module bundle mapping for ModuleSelectionModal
 * Maps high-level bundles (categories) to specific module entitlements.
 * Updated to support 10-category structure - categories are now fetched from API.
 */

export interface BundleModule {
  key: string;
  displayName: string;
  description?: string;
  modules: string[]; // Module keys in this category
  module_count?: number;
}

/**
 * Legacy static bundle mapping (kept for backward compatibility during migration)
 * New code should fetch categories dynamically from /admin/categories API
 * 
 * 10-Category Structure:
 * 1. CRM Suite
 * 2. ERP Suite
 * 3. Manufacturing Suite
 * 4. Finance & Accounting Suite
 * 5. Service Management Suite
 * 6. Human Resources Suite
 * 7. Analytics & BI Suite
 * 8. AI & Machine Learning Suite
 * 9. Project Management Suite
 * 10. Operations & Assets Management Suite
 */
export const MODULE_BUNDLES: BundleModule[] = [
  {
    key: 'crm_suite',
    displayName: 'CRM Suite',
    modules: ['crm', 'sales', 'marketing', 'seo'],
  },
  {
    key: 'erp_suite',
    displayName: 'ERP Suite',
    modules: ['erp', 'inventory', 'procurement', 'order_book', 'master_data', 'product', 'vouchers'],
  },
  {
    key: 'manufacturing_suite',
    displayName: 'Manufacturing Suite',
    modules: ['manufacturing', 'bom'],
  },
  {
    key: 'finance_suite',
    displayName: 'Finance & Accounting Suite',
    modules: ['finance', 'accounting', 'reports_analytics', 'payroll'],
  },
  {
    key: 'service_suite',
    displayName: 'Service Management Suite',
    modules: ['service'],
  },
  {
    key: 'hr_suite',
    displayName: 'Human Resources Suite',
    modules: ['hr', 'hr_management', 'talent'],
  },
  {
    key: 'analytics_suite',
    displayName: 'Analytics & BI Suite',
    modules: ['analytics', 'streaming_analytics', 'ab_testing'],
  },
  {
    key: 'ai_suite',
    displayName: 'AI & Machine Learning Suite',
    modules: ['ai_analytics', 'website_agent'],
  },
  {
    key: 'project_management_suite',
    displayName: 'Project Management Suite',
    modules: ['project', 'projects', 'task_management', 'tasks_calendar'],
  },
  {
    key: 'operations_assets_suite',
    displayName: 'Operations & Assets Management Suite',
    modules: ['asset', 'transport', 'workflow', 'integration', 'email', 'calendar', 'exhibition', 'customer', 'vendor', 'voucher', 'stock', 'settings', 'admin', 'organization'],
  },
];

/**
 * Get all module_keys for a set of selected bundles (categories)
 */
export function getBundleModules(selectedBundles: string[]): string[] {
  const allModules: string[] = [];
  
  selectedBundles.forEach((bundleKey) => {
    const bundle = MODULE_BUNDLES.find(b => b.key === bundleKey);
    if (bundle) {
      allModules.push(...bundle.modules);
    }
  });
  
  return allModules;
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
 * Get selected bundles (categories) from current module entitlements
 * A category is considered selected if ANY of its modules are enabled
 */
export function getSelectedBundlesFromModules(enabledModules: string[]): string[] {
  const selectedBundles = new Set<string>();
  
  MODULE_BUNDLES.forEach((bundle) => {
    // Check if any module in this bundle is enabled
    const hasEnabledModule = bundle.modules.some(moduleKey => 
      enabledModules.includes(moduleKey)
    );
    
    if (hasEnabledModule) {
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
  
  // Get all unique module_keys from all bundles
  const allModules = new Set<string>();
  MODULE_BUNDLES.forEach(bundle => {
    bundle.modules.forEach(moduleKey => allModules.add(moduleKey));
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