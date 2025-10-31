/**
 * Permission Normalization Utility
 * 
 * Handles permission key aliasing and normalization between backend and frontend.
 * Backend returns permissions like "*.read" or service-namespaced permissions,
 * while frontend menuConfig expects "*.view" keys.
 */

/**
 * Permission alias mapping
 * Maps backend permission keys to frontend canonical keys
 */
const PERMISSION_ALIASES: Record<string, string[]> = {
  // Master Data
  'master_data.view': ['master_data.read', 'master_data.manage'],
  
  // Inventory
  'inventory.view': ['inventory.read', 'inventory.manage'],
  
  // Vouchers
  'vouchers.view': ['vouchers.read', 'vouchers.manage'],
  
  // Settings
  'settings.view': ['settings.read', 'settings.manage', 'admin.manage'],
  
  // Admin/User Management
  'admin.view': ['admin.manage', 'admin.read', 'user.manage', 'user.read'],
  
  // CRM
  'crm.view': ['crm.read', 'crm.manage', 'service_crm.read', 'service_crm.manage'],
  
  // Sales
  'sales.view': ['sales.read', 'sales.manage'],
  
  // Purchase
  'purchase.view': ['purchase.read', 'purchase.manage'],
  
  // Manufacturing
  'manufacturing.view': ['manufacturing.read', 'manufacturing.manage'],
  
  // Reports
  'reports.view': ['reports.read', 'reports.manage'],
  
  // Email
  'email.view': ['email.read', 'email.manage'],
  
  // HR/Payroll
  'hr.view': ['hr.read', 'hr.manage', 'payroll.read', 'payroll.manage'],
  
  // Finance/Accounting
  'accounting.view': ['accounting.read', 'accounting.manage', 'finance.read', 'finance.manage'],
  
  // Analytics
  'analytics.view': ['analytics.read', 'analytics.manage'],
  
  // Projects
  'projects.view': ['projects.read', 'projects.manage'],
  
  // Website Agent
  'website_agent.view': ['website_agent.read', 'website_agent.manage'],
  
  // Marketing
  'marketing.view': ['marketing.read', 'marketing.manage'],
  
  // Organization Management
  'organization.view': ['organization.read', 'organization.manage'],
  
  // RBAC
  'rbac.view': ['rbac.read', 'rbac.manage'],
  
  // Company
  'company.view': ['company.read', 'company.manage'],
  
  // Stock
  'stock.view': ['stock.read', 'stock.manage'],
  
  // Products
  'products.view': ['products.read', 'products.manage', 'product.read', 'product.manage'],
  
  // Customers
  'customers.view': ['customers.read', 'customers.manage', 'customer.read', 'customer.manage'],
  
  // Vendors
  'vendors.view': ['vendors.read', 'vendors.manage', 'vendor.read', 'vendor.manage'],
  
  // Orders
  'orders.view': ['orders.read', 'orders.manage', 'order.read', 'order.manage'],
};

/**
 * Normalizes backend permissions to frontend canonical keys
 * @param backendPermissions - Array of permission strings from backend
 * @returns Set of normalized permission keys
 */
export function normalizePermissions(backendPermissions: string[]): Set<string> {
  const normalized = new Set<string>();
  
  // Add all original permissions
  backendPermissions.forEach(perm => normalized.add(perm));
  
  // Add canonical keys for aliased permissions
  Object.entries(PERMISSION_ALIASES).forEach(([canonical, aliases]) => {
    const hasAnyAlias = aliases.some(alias => backendPermissions.includes(alias));
    if (hasAnyAlias) {
      normalized.add(canonical);
    }
  });
  
  // Module-level base access: if user has any permission in a module namespace,
  // grant the base *.view permission for that module
  // Note: This list should match the module registry in the backend
  // TODO: Consider deriving this from PERMISSION_ALIASES keys or fetching from backend config
  const moduleNamespaces = [
    'master_data',
    'inventory',
    'vouchers',
    'settings',
    'admin',
    'crm',
    'service_crm',
    'sales',
    'purchase',
    'manufacturing',
    'reports',
    'email',
    'hr',
    'payroll',
    'accounting',
    'finance',
    'analytics',
    'projects',
    'website_agent',
    'marketing',
    'organization',
    'rbac',
    'company',
    'stock',
    'products',
    'product',
    'customers',
    'customer',
    'vendors',
    'vendor',
    'orders',
    'order',
  ];
  
  moduleNamespaces.forEach(module => {
    const hasModulePermission = backendPermissions.some(perm => 
      perm.startsWith(`${module}.`)
    );
    
    if (hasModulePermission) {
      normalized.add(`${module}.view`);
    }
  });
  
  return normalized;
}

/**
 * Checks if user has a specific permission (considering aliases)
 * @param userPermissions - Normalized user permissions
 * @param requiredPermission - Required permission key
 * @returns true if user has the permission or any of its aliases
 */
export function hasPermission(
  userPermissions: Set<string> | string[],
  requiredPermission: string
): boolean {
  const permSet = Array.isArray(userPermissions) ? new Set(userPermissions) : userPermissions;
  
  // Check direct match
  if (permSet.has(requiredPermission)) {
    return true;
  }
  
  // Check if any alias matches
  const aliases = PERMISSION_ALIASES[requiredPermission] || [];
  return aliases.some(alias => permSet.has(alias));
}

/**
 * Log permission comparison for debugging
 * Compares normalized keys vs required keys
 */
export function debugPermissions(
  backendPermissions: string[],
  requiredPermissions: string[]
): void {
  if (process.env.NODE_ENV !== 'development') return;
  
  const normalized = normalizePermissions(backendPermissions);
  
  console.group('🔑 Permission Debug');
  console.log('Backend Permissions:', backendPermissions);
  console.log('Normalized Permissions:', Array.from(normalized));
  console.log('Required Permissions:', requiredPermissions);
  
  const missingPermissions = requiredPermissions.filter(
    req => !hasPermission(normalized, req)
  );
  
  if (missingPermissions.length > 0) {
    console.warn('Missing Permissions:', missingPermissions);
  } else {
    console.log('✅ All required permissions satisfied');
  }
  
  console.groupEnd();
}
