// frontend/src/types/rbac.types.ts
  // Disable no-unused-vars for enum members, as they are exported types used elsewhere

/**
 * RBAC Types
 *
 * TypeScript type definitions for Role-Based Access Control
 * across all app modules.
 */
// Enums matching backend
export enum RoleType {
  ADMIN = "admin",
  MANAGER = "manager",
  SUPPORT = "support",
  VIEWER = "viewer",
}
export enum Module {
  MASTER_DATA = "master_data",
  INVENTORY = "inventory",
  MANUFACTURING = "manufacturing",
  VOUCHERS = "vouchers",
  FINANCE = "finance",
  ACCOUNTING = "accounting",
  REPORTS = "reports",
  AI_ANALYTICS = "ai_analytics",
  SALES = "sales",
  MARKETING = "marketing",
  SERVICE = "service",
  PROJECTS = "projects",
  HR = "hr",
  TASKS_CALENDAR = "tasks_calendar",
  EMAIL = "email",
  SETTINGS = "settings",
  CRM_ADMIN = "crm_admin",
}
export enum Action {
  CREATE = "create",
  READ = "read",
  UPDATE = "update",
  DELETE = "delete",
  EXPORT = "export",
  ADMIN = "admin",
}
// Permission Types
export interface Permission {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  module: Module;
  action: Action;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}
export interface PermissionCreate {
  name: string;
  display_name: string;
  description?: string;
  module: Module;
  action: Action;
  is_active?: boolean;
}
export interface PermissionUpdate {
  display_name?: string;
  description?: string;
  is_active?: boolean;
}
// Role Types
export interface Role {
  id: number;
  organization_id: number;
  name: RoleType;
  display_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}
export interface RoleWithPermissions extends Role {
  permissions: Permission[];
}
export interface RoleCreate {
  name: RoleType;
  display_name: string;
  description?: string;
  organization_id: number;
  permission_ids?: number[];
  is_active?: boolean;
}
export interface RoleUpdate {
  display_name?: string;
  description?: string;
  is_active?: boolean;
  permission_ids?: number[];
}
// User Role Assignment Types
export interface UserRole {
  id: number;
  user_id: number;
  role_id: number;
  assigned_by_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}
export interface UserRoleCreate {
  user_id: number;
  role_id: number;
  assigned_by_id?: number;
  is_active?: boolean;
}
export interface UserWithRoles {
  id: number;
  email: string;
  full_name?: string;
  role: string; // Regular user role
  is_active: boolean;
  roles: Role[];
}
// Role Assignment Request/Response Types
export interface RoleAssignmentRequest {
  user_id: number;
  role_ids: number[];
}
export interface RoleAssignmentResponse {
  success: boolean;
  message: string;
  assignments: UserRole[];
}
export interface BulkRoleAssignmentRequest {
  user_ids: number[];
  role_ids: number[];
  replace_existing?: boolean;
}
export interface BulkRoleAssignmentResponse {
  success: boolean;
  message: string;
  successful_assignments: number;
  failed_assignments: number;
  details: string[];
}
// Permission Checking Types
export interface PermissionCheckRequest {
  user_id: number;
  permission: string;
  organization_id?: number;
}
export interface PermissionCheckResponse {
  has_permission: boolean;
  user_id: number;
  permission: string;
  source: string;
}
export interface UserPermissions {
  user_id: number;
  permissions: string[];
  roles: Role[];
  total_permissions: number;
}
// UI Component Props Types
export interface RoleManagementProps {
  organizationId: number;
}
export interface RoleFormProps {
  role?: RoleWithPermissions;
  permissions: Permission[];
  organizationId: number;
  onSubmit: (data: RoleCreate | RoleUpdate) => void;
  onCancel: () => void;
  loading?: boolean;
}
export interface UserRoleAssignmentProps {
  userId: number;
  userEmail: string;
  userFullName?: string;
  currentRoles: Role[];
  availableRoles: Role[];
  onAssign: (roleIds: number[]) => void;
  onRemove: (roleId: number) => void;
  loading?: boolean;
}
export interface RolePermissionMatrixProps {
  roles: RoleWithPermissions[];
  permissions: Permission[];
  onPermissionToggle: (
    roleId: number,
    permissionId: number,
    granted: boolean,
  ) => void;
  loading?: boolean;
}
// Role Defaults
export const ROLE_DEFAULTS: Record<
  RoleType,
  Partial<RoleCreate>
> = {
  [RoleType.ADMIN]: {
    name: RoleType.ADMIN,
    display_name: "Admin",
    description: "Full access to all functionality",
  },
  [RoleType.MANAGER]: {
    name: RoleType.MANAGER,
    display_name: "Manager",
    description: "Management access",
  },
  [RoleType.SUPPORT]: {
    name: RoleType.SUPPORT,
    display_name: "Support Staff",
    description: "Operational access to tickets and tasks",
  },
  [RoleType.VIEWER]: {
    name: RoleType.VIEWER,
    display_name: "Viewer",
    description: "Read-only access to data",
  },
};
// Module Display Names (for UI)
export const MODULE_DISPLAY_NAMES: Record<Module, string> = {
  [Module.MASTER_DATA]: "Master Data",
  [Module.INVENTORY]: "Inventory",
  [Module.MANUFACTURING]: "Manufacturing",
  [Module.VOUCHERS]: "Vouchers",
  [Module.FINANCE]: "Finance",
  [Module.ACCOUNTING]: "Accounting",
  [Module.REPORTS]: "Reports & Analytics",
  [Module.AI_ANALYTICS]: "AI & Analytics",
  [Module.SALES]: "Sales",
  [Module.MARKETING]: "Marketing",
  [Module.SERVICE]: "Service",
  [Module.PROJECTS]: "Projects",
  [Module.HR]: "HR Management",
  [Module.TASKS_CALENDAR]: "Tasks & Calendar",
  [Module.EMAIL]: "Email",
  [Module.SETTINGS]: "Settings",
  [Module.CRM_ADMIN]: "CRM Administration",
};
// Role Badge Colors (for UI display)
export const ROLE_BADGE_COLORS: Record<RoleType, string> = {
  [RoleType.ADMIN]: "error", // Red
  [RoleType.MANAGER]: "warning", // Orange
  [RoleType.SUPPORT]: "info", // Blue
  [RoleType.VIEWER]: "success", // Green
};
// Permission checking helper functions
export const hasPermission = (
  userRoles: Role[],
  requiredPermission: string,
  allRoles: RoleWithPermissions[],
): boolean => {
  for (const userRole of userRoles) {
    const roleWithPermissions = allRoles.find((r) => r.id === userRole.id);
    if (roleWithPermissions) {
      const hasPermission = roleWithPermissions.permissions.some(
        (p) => p.name === requiredPermission && p.is_active,
      );
      if (hasPermission) {
        return true;
      }
    }
  }
  return false;
};
export const getUserPermissions = (
  userRoles: Role[],
  allRoles: RoleWithPermissions[],
): string[] => {
  const permissions = new Set<string>();
  for (const userRole of userRoles) {
    const roleWithPermissions = allRoles.find((r) => r.id === userRole.id);
    if (roleWithPermissions) {
      roleWithPermissions.permissions
        .filter((p) => p.is_active)
        .forEach((p) => permissions.add(p.name));
    }
  }
  return Array.from(permissions);
};
// Permission constants (matching backend)
export const PERMISSIONS = {
  // Master Data
  MASTER_DATA_CREATE: "master_data_create",
  MASTER_DATA_READ: "master_data_read",
  MASTER_DATA_UPDATE: "master_data_update",
  MASTER_DATA_DELETE: "master_data_delete",
  // Inventory
  INVENTORY_CREATE: "inventory_create",
  INVENTORY_READ: "inventory_read",
  INVENTORY_UPDATE: "inventory_update",
  INVENTORY_DELETE: "inventory_delete",
  // Manufacturing
  MANUFACTURING_CREATE: "manufacturing_create",
  MANUFACTURING_READ: "manufacturing_read",
  MANUFACTURING_UPDATE: "manufacturing_update",
  MANUFACTURING_DELETE: "manufacturing_delete",
  // Vouchers
  VOUCHERS_CREATE: "vouchers_create",
  VOUCHERS_READ: "vouchers_read",
  VOUCHERS_UPDATE: "vouchers_update",
  VOUCHERS_DELETE: "vouchers_delete",
  // Finance
  FINANCE_CREATE: "finance_create",
  FINANCE_READ: "finance_read",
  FINANCE_UPDATE: "finance_update",
  FINANCE_DELETE: "finance_delete",
  // Accounting
  ACCOUNTING_CREATE: "accounting_create",
  ACCOUNTING_READ: "accounting_read",
  ACCOUNTING_UPDATE: "accounting_update",
  ACCOUNTING_DELETE: "accounting_delete",
  // Reports
  REPORTS_READ: "reports_read",
  REPORTS_EXPORT: "reports_export",
  // AI Analytics
  AI_ANALYTICS_READ: "ai_analytics_read",
  AI_ANALYTICS_CREATE: "ai_analytics_create",
  // Sales
  SALES_CREATE: "sales_create",
  SALES_READ: "sales_read",
  SALES_UPDATE: "sales_update",
  SALES_DELETE: "sales_delete",
  // Marketing
  MARKETING_CREATE: "marketing_create",
  MARKETING_READ: "marketing_read",
  MARKETING_UPDATE: "marketing_update",
  MARKETING_DELETE: "marketing_delete",
  // Service
  SERVICE_CREATE: "service_create",
  SERVICE_READ: "service_read",
  SERVICE_UPDATE: "service_update",
  SERVICE_DELETE: "service_delete",
  // Projects
  PROJECTS_CREATE: "projects_create",
  PROJECTS_READ: "projects_read",
  PROJECTS_UPDATE: "projects_update",
  PROJECTS_DELETE: "projects_delete",
  // HR
  HR_CREATE: "hr_create",
  HR_READ: "hr_read",
  HR_UPDATE: "hr_update",
  HR_DELETE: "hr_delete",
  // Tasks Calendar
  TASKS_CALENDAR_CREATE: "tasks_calendar_create",
  TASKS_CALENDAR_READ: "tasks_calendar_read",
  TASKS_CALENDAR_UPDATE: "tasks_calendar_update",
  TASKS_CALENDAR_DELETE: "tasks_calendar_delete",
  // Email
  EMAIL_CREATE: "email_create",
  EMAIL_READ: "email_read",
  EMAIL_UPDATE: "email_update",
  EMAIL_DELETE: "email_delete",
  // Settings
  SETTINGS_READ: "settings_read",
  SETTINGS_UPDATE: "settings_update",
  // Admin
  ADMIN: "admin",
  CRM_ADMIN: "crm_admin",
} as const;
export type PermissionType =
  (typeof PERMISSIONS)[keyof typeof PERMISSIONS];