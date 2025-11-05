// frontend/src/constants/rbac.ts

/**
 * Consolidated constants for RBAC, Entitlement, and Tenant system
 * This file centralizes all constants for the 3-layer security model
 */

// ============================================================================
// ROLE CONSTANTS
// ============================================================================

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  ADMIN = 'admin',
  MANAGEMENT = 'management',
  MANAGER = 'manager',
  EXECUTIVE = 'executive',
  USER = 'user',
}

export const ROLE_DISPLAY_NAMES: Record<UserRole, string> = {
  [UserRole.SUPER_ADMIN]: 'Super Admin',
  [UserRole.ADMIN]: 'Admin',
  [UserRole.MANAGEMENT]: 'Management',
  [UserRole.MANAGER]: 'Manager',
  [UserRole.EXECUTIVE]: 'Executive',
  [UserRole.USER]: 'User',
};

export const ROLE_HIERARCHY: Record<UserRole, number> = {
  [UserRole.SUPER_ADMIN]: 100,
  [UserRole.ADMIN]: 80,
  [UserRole.MANAGEMENT]: 70,
  [UserRole.MANAGER]: 50,
  [UserRole.EXECUTIVE]: 30,
  [UserRole.USER]: 10,
};

export const SUPER_ADMIN_ROLES: Set<string> = new Set([UserRole.SUPER_ADMIN]);

export const ORG_ADMIN_ROLES: Set<string> = new Set([
  UserRole.ADMIN,
  UserRole.MANAGEMENT,
]);

// ============================================================================
// MODULE CONSTANTS
// ============================================================================

export enum CoreModule {
  DASHBOARD = 'dashboard',
  CRM = 'crm',
  ERP = 'erp',
  SALES = 'sales',
  INVENTORY = 'inventory',
  MANUFACTURING = 'manufacturing',
  FINANCE = 'finance',
  ACCOUNTING = 'accounting',
  HR = 'hr',
  SERVICE = 'service',
  ANALYTICS = 'analytics',
  REPORTS_ANALYTICS = 'reports_analytics',
}

export enum ExtendedModule {
  MASTER_DATA = 'master_data',
  VOUCHERS = 'vouchers',
  PROCUREMENT = 'procurement',
  PROJECT = 'project',
  PROJECTS = 'projects',
  ASSET = 'asset',
  TRANSPORT = 'transport',
  SEO = 'seo',
  MARKETING = 'marketing',
  PAYROLL = 'payroll',
  TALENT = 'talent',
  HR_MANAGEMENT = 'hr_management',
  TASKS_CALENDAR = 'tasks_calendar',
}

export enum AdvancedModule {
  WORKFLOW = 'workflow',
  INTEGRATION = 'integration',
  AI_ANALYTICS = 'ai_analytics',
  STREAMING_ANALYTICS = 'streaming_analytics',
  AB_TESTING = 'ab_testing',
  WEBSITE_AGENT = 'website_agent',
  EMAIL = 'email',
  CALENDAR = 'calendar',
  TASK_MANAGEMENT = 'task_management',
  ORDER_BOOK = 'order_book',
  EXHIBITION = 'exhibition',
}

export enum SystemModule {
  SETTINGS = 'settings',
  ADMIN = 'admin',
  ORGANIZATION = 'organization',
  USER = 'user',
}

// ============================================================================
// ENTITLEMENT CONSTANTS
// ============================================================================

export enum ModuleStatus {
  ENABLED = 'enabled',
  DISABLED = 'disabled',
  TRIAL = 'trial',
  UNKNOWN = 'unknown',
}

export const ALWAYS_ON_MODULES: Set<string> = new Set(['email', 'dashboard']);

export const RBAC_ONLY_MODULES: Set<string> = new Set([
  'settings',
  'admin',
  'organization',
  'user',
]);

// ============================================================================
// PERMISSION CONSTANTS
// ============================================================================

export enum PermissionAction {
  CREATE = 'create',
  READ = 'read',
  UPDATE = 'update',
  DELETE = 'delete',
  APPROVE = 'approve',
  EXPORT = 'export',
  IMPORT = 'import',
  MANAGE = 'manage',
}

export enum PermissionScope {
  GLOBAL = 'global',
  ORG = 'org',
  MODULE = 'module',
  SUBMODULE = 'submodule',
  RECORD = 'record',
}

// Permission pattern builders
export const PERMISSION_PATTERNS = {
  moduleRead: (module: string) => `${module}.read`,
  moduleWrite: (module: string) => `${module}.write`,
  moduleCreate: (module: string) => `${module}.create`,
  moduleUpdate: (module: string) => `${module}.update`,
  moduleDelete: (module: string) => `${module}.delete`,
  moduleManage: (module: string) => `${module}.manage`,
  moduleAdmin: (module: string) => `${module}_admin`,
  submoduleAccess: (module: string, submodule: string) =>
    `${module}_${submodule}_access`,
  submoduleManage: (module: string, submodule: string) =>
    `${module}_${submodule}_manage`,
};

// ============================================================================
// PRODUCT CATEGORY CONSTANTS
// ============================================================================

export enum ProductCategory {
  CRM = 'crm_suite',
  ERP = 'erp_suite',
  MANUFACTURING = 'manufacturing_suite',
  FINANCE = 'finance_suite',
  SERVICE = 'service_suite',
  HR = 'hr_suite',
  ANALYTICS = 'analytics_suite',
  AI = 'ai_suite',
  PROJECT_MANAGEMENT = 'project_management_suite',
  OPERATIONS_ASSETS = 'operations_assets_suite',
}

export const CATEGORY_DISPLAY_NAMES: Record<ProductCategory, string> = {
  [ProductCategory.CRM]: 'CRM Suite',
  [ProductCategory.ERP]: 'ERP Suite',
  [ProductCategory.MANUFACTURING]: 'Manufacturing Suite',
  [ProductCategory.FINANCE]: 'Finance & Accounting Suite',
  [ProductCategory.SERVICE]: 'Service Management Suite',
  [ProductCategory.HR]: 'Human Resources Suite',
  [ProductCategory.ANALYTICS]: 'Analytics & BI Suite',
  [ProductCategory.AI]: 'AI & Machine Learning Suite',
  [ProductCategory.PROJECT_MANAGEMENT]: 'Project Management Suite',
  [ProductCategory.OPERATIONS_ASSETS]: 'Operations & Assets Management Suite',
};

// ============================================================================
// ENFORCEMENT CONSTANTS
// ============================================================================

export enum EnforcementLevel {
  TENANT = 'tenant',
  ENTITLEMENT = 'entitlement',
  RBAC = 'rbac',
}

export const ENFORCEMENT_ERROR_MESSAGES = {
  tenantMismatch: 'Access denied: Resource does not belong to your organization',
  tenantRequired: 'Organization context is required for this operation',
  entitlementDisabled: (module: string) =>
    `Module '${module}' is not enabled for your organization`,
  entitlementTrialExpired: (module: string) =>
    `Trial period for module '${module}' has expired`,
  rbacPermissionDenied: (permission: string) =>
    `You do not have '${permission}' permission for this action`,
  rbacRoleInsufficient:
    'Your role does not have sufficient privileges for this action',
  invalidOrgId: 'Invalid or missing organization identifier',
};

// ============================================================================
// API CONSTANTS
// ============================================================================

export const API_HEADERS = {
  ORGANIZATION_ID: 'X-Organization-ID',
  USER_ID: 'X-User-ID',
  AUTHORIZATION: 'Authorization',
};

// ============================================================================
// CACHE CONSTANTS
// ============================================================================

export const CACHE_KEYS = {
  userPermissions: (userId: number) => `user_permissions_${userId}`,
  userRoles: (userId: number) => `user_roles_${userId}`,
  orgEntitlements: (orgId: number) => `org_entitlements_${orgId}`,
  moduleStatus: (orgId: number, module: string) =>
    `module_status_${orgId}_${module}`,
};

export const CACHE_TTL_MS = {
  userPermissions: 5 * 60 * 1000, // 5 minutes
  userRoles: 5 * 60 * 1000, // 5 minutes
  orgEntitlements: 10 * 60 * 1000, // 10 minutes
  moduleStatus: 10 * 60 * 1000, // 10 minutes
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function isSuperAdminRole(role: string): boolean {
  return SUPER_ADMIN_ROLES.has(role);
}

export function isOrgAdminRole(role: string): boolean {
  return ORG_ADMIN_ROLES.has(role);
}

export function isRBACOnlyModule(module: string): boolean {
  return RBAC_ONLY_MODULES.has(module.toLowerCase());
}

export function isAlwaysOnModule(module: string): boolean {
  return ALWAYS_ON_MODULES.has(module.toLowerCase());
}

export function getRoleLevel(role: string): number {
  return ROLE_HIERARCHY[role as UserRole] || 0;
}

export function canRoleManageRole(managerRole: string, targetRole: string): boolean {
  return getRoleLevel(managerRole) > getRoleLevel(targetRole);
}

export function formatPermission(
  pattern: keyof typeof PERMISSION_PATTERNS,
  ...args: string[]
): string {
  const fn = PERMISSION_PATTERNS[pattern];
  return typeof fn === 'function' ? fn(...args) : '';
}

export function isModuleEnabled(
  status: ModuleStatus | string,
  trialExpiry?: Date | string | null
): boolean {
  if (status === ModuleStatus.ENABLED) return true;
  if (status === ModuleStatus.TRIAL) {
    if (!trialExpiry) return true;
    const expiryDate = typeof trialExpiry === 'string' ? new Date(trialExpiry) : trialExpiry;
    return expiryDate > new Date();
  }
  return false;
}

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface UserPermissions {
  role: string;
  roles: Array<{
    id: number;
    name: string;
    role_type: string;
  }>;
  permissions: string[];
  modules: string[];
  submodules: Record<string, string[]>;
}

export interface ModuleEntitlement {
  module_key: string;
  status: ModuleStatus;
  trial_expires_at?: string | null;
  submodules?: Record<string, boolean>;
}

export interface OrgEntitlements {
  entitlements: Record<string, ModuleEntitlement>;
}

export interface PermissionCheck {
  hasPermission: boolean;
  reason?: string;
  enforcementLevel: EnforcementLevel;
}
