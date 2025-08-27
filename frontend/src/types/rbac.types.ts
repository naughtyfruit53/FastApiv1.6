// frontend/src/types/rbac.types.ts

/**
 * Service CRM RBAC Types
 * 
 * TypeScript type definitions for Role-Based Access Control
 * in the Service CRM module.
 */

// Enums matching backend
export enum ServiceRoleType {
  ADMIN = 'admin',
  MANAGER = 'manager',
  SUPPORT = 'support',
  VIEWER = 'viewer'
}

export enum ServiceModule {
  SERVICE = 'service',
  TECHNICIAN = 'technician',
  APPOINTMENT = 'appointment',
  CUSTOMER_SERVICE = 'customer_service',
  WORK_ORDER = 'work_order',
  SERVICE_REPORTS = 'service_reports',
  CRM_ADMIN = 'crm_admin'
}

export enum ServiceAction {
  CREATE = 'create',
  READ = 'read',
  UPDATE = 'update',
  DELETE = 'delete',
  EXPORT = 'export',
  ADMIN = 'admin'
}

// Service Permission Types
export interface ServicePermission {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  module: ServiceModule;
  action: ServiceAction;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ServicePermissionCreate {
  name: string;
  display_name: string;
  description?: string;
  module: ServiceModule;
  action: ServiceAction;
  is_active?: boolean;
}

export interface ServicePermissionUpdate {
  display_name?: string;
  description?: string;
  is_active?: boolean;
}

// Service Role Types
export interface ServiceRole {
  id: number;
  organization_id: number;
  name: ServiceRoleType;
  display_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ServiceRoleWithPermissions extends ServiceRole {
  permissions: ServicePermission[];
}

export interface ServiceRoleCreate {
  name: ServiceRoleType;
  display_name: string;
  description?: string;
  organization_id: number;
  permission_ids?: number[];
  is_active?: boolean;
}

export interface ServiceRoleUpdate {
  display_name?: string;
  description?: string;
  is_active?: boolean;
  permission_ids?: number[];
}

// User Role Assignment Types
export interface UserServiceRole {
  id: number;
  user_id: number;
  role_id: number;
  assigned_by_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserServiceRoleCreate {
  user_id: number;
  role_id: number;
  assigned_by_id?: number;
  is_active?: boolean;
}

export interface UserWithServiceRoles {
  id: number;
  email: string;
  full_name?: string;
  role: string; // Regular user role
  is_active: boolean;
  service_roles: ServiceRole[];
}

// Role Assignment Request/Response Types
export interface RoleAssignmentRequest {
  user_id: number;
  role_ids: number[];
}

export interface RoleAssignmentResponse {
  success: boolean;
  message: string;
  assignments: UserServiceRole[];
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
  service_roles: ServiceRole[];
  total_permissions: number;
}

// UI Component Props Types
export interface RoleManagementProps {
  organizationId: number;
}

export interface RoleFormProps {
  role?: ServiceRoleWithPermissions;
  permissions: ServicePermission[];
  organizationId: number;
  onSubmit: (data: ServiceRoleCreate | ServiceRoleUpdate) => void;
  onCancel: () => void;
  loading?: boolean;
}

export interface UserRoleAssignmentProps {
  userId: number;
  userEmail: string;
  userFullName?: string;
  currentRoles: ServiceRole[];
  availableRoles: ServiceRole[];
  onAssign: (roleIds: number[]) => void;
  onRemove: (roleId: number) => void;
  loading?: boolean;
}

export interface RolePermissionMatrixProps {
  roles: ServiceRoleWithPermissions[];
  permissions: ServicePermission[];
  onPermissionToggle: (roleId: number, permissionId: number, granted: boolean) => void;
  loading?: boolean;
}

// Service Role Defaults
export const SERVICE_ROLE_DEFAULTS: Record<ServiceRoleType, Partial<ServiceRoleCreate>> = {
  [ServiceRoleType.ADMIN]: {
    name: ServiceRoleType.ADMIN,
    display_name: 'Service Admin',
    description: 'Full access to all service CRM functionality'
  },
  [ServiceRoleType.MANAGER]: {
    name: ServiceRoleType.MANAGER,
    display_name: 'Service Manager',
    description: 'Manage services, technicians, and appointments'
  },
  [ServiceRoleType.SUPPORT]: {
    name: ServiceRoleType.SUPPORT,
    display_name: 'Support Agent',
    description: 'Handle customer service and basic operations'
  },
  [ServiceRoleType.VIEWER]: {
    name: ServiceRoleType.VIEWER,
    display_name: 'Viewer',
    description: 'Read-only access to service information'
  }
};

// Permission Display Names
export const PERMISSION_DISPLAY_NAMES: Record<string, string> = {
  // Service Management
  'service_create': 'Create Services',
  'service_read': 'View Services',
  'service_update': 'Update Services',
  'service_delete': 'Delete Services',
  
  // Technician Management
  'technician_create': 'Create Technicians',
  'technician_read': 'View Technicians',
  'technician_update': 'Update Technicians',
  'technician_delete': 'Delete Technicians',
  
  // Appointment Management
  'appointment_create': 'Create Appointments',
  'appointment_read': 'View Appointments',
  'appointment_update': 'Update Appointments',
  'appointment_delete': 'Cancel Appointments',
  
  // Customer Service
  'customer_service_create': 'Create Customer Records',
  'customer_service_read': 'View Customer Records',
  'customer_service_update': 'Update Customer Records',
  'customer_service_delete': 'Delete Customer Records',
  
  // Work Orders
  'work_order_create': 'Create Work Orders',
  'work_order_read': 'View Work Orders',
  'work_order_update': 'Update Work Orders',
  'work_order_delete': 'Delete Work Orders',
  
  // Reports
  'service_reports_read': 'View Service Reports',
  'service_reports_export': 'Export Service Reports',
  
  // CRM Admin
  'crm_admin': 'CRM Administration',
  'crm_settings': 'CRM Settings'
};

// Module Display Names
export const MODULE_DISPLAY_NAMES: Record<ServiceModule, string> = {
  [ServiceModule.SERVICE]: 'Service Management',
  [ServiceModule.TECHNICIAN]: 'Technician Management',
  [ServiceModule.APPOINTMENT]: 'Appointment Management',
  [ServiceModule.CUSTOMER_SERVICE]: 'Customer Service',
  [ServiceModule.WORK_ORDER]: 'Work Orders',
  [ServiceModule.SERVICE_REPORTS]: 'Service Reports',
  [ServiceModule.CRM_ADMIN]: 'CRM Administration'
};

// Role Badge Colors (for UI display)
export const ROLE_BADGE_COLORS: Record<ServiceRoleType, string> = {
  [ServiceRoleType.ADMIN]: 'error', // Red
  [ServiceRoleType.MANAGER]: 'warning', // Orange
  [ServiceRoleType.SUPPORT]: 'info', // Blue
  [ServiceRoleType.VIEWER]: 'success' // Green
};

// Permission checking helper functions
export const hasServicePermission = (
  userRoles: ServiceRole[],
  requiredPermission: string,
  allRoles: ServiceRoleWithPermissions[]
): boolean => {
  for (const userRole of userRoles) {
    const roleWithPermissions = allRoles.find(r => r.id === userRole.id);
    if (roleWithPermissions) {
      const hasPermission = roleWithPermissions.permissions.some(
        p => p.name === requiredPermission && p.is_active
      );
      if (hasPermission) return true;
    }
  }
  return false;
};

export const getUserServicePermissions = (
  userRoles: ServiceRole[],
  allRoles: ServiceRoleWithPermissions[]
): string[] => {
  const permissions = new Set<string>();
  
  for (const userRole of userRoles) {
    const roleWithPermissions = allRoles.find(r => r.id === userRole.id);
    if (roleWithPermissions) {
      roleWithPermissions.permissions
        .filter(p => p.is_active)
        .forEach(p => permissions.add(p.name));
    }
  }
  
  return Array.from(permissions);
};

// Service permission constants (matching backend)
export const SERVICE_PERMISSIONS = {
  // Service Management
  SERVICE_CREATE: 'service_create',
  SERVICE_READ: 'service_read',
  SERVICE_UPDATE: 'service_update',
  SERVICE_DELETE: 'service_delete',
  
  // Technician Management
  TECHNICIAN_CREATE: 'technician_create',
  TECHNICIAN_READ: 'technician_read',
  TECHNICIAN_UPDATE: 'technician_update',
  TECHNICIAN_DELETE: 'technician_delete',
  
  // Appointment Management
  APPOINTMENT_CREATE: 'appointment_create',
  APPOINTMENT_READ: 'appointment_read',
  APPOINTMENT_UPDATE: 'appointment_update',
  APPOINTMENT_DELETE: 'appointment_delete',
  
  // Customer Service
  CUSTOMER_SERVICE_CREATE: 'customer_service_create',
  CUSTOMER_SERVICE_READ: 'customer_service_read',
  CUSTOMER_SERVICE_UPDATE: 'customer_service_update',
  CUSTOMER_SERVICE_DELETE: 'customer_service_delete',
  
  // Work Orders
  WORK_ORDER_CREATE: 'work_order_create',
  WORK_ORDER_READ: 'work_order_read',
  WORK_ORDER_UPDATE: 'work_order_update',
  WORK_ORDER_DELETE: 'work_order_delete',
  
  // Reports
  SERVICE_REPORTS_READ: 'service_reports_read',
  SERVICE_REPORTS_EXPORT: 'service_reports_export',
  
  // CRM Admin
  CRM_ADMIN: 'crm_admin',
  CRM_SETTINGS: 'crm_settings'
} as const;

export type ServicePermissionType = typeof SERVICE_PERMISSIONS[keyof typeof SERVICE_PERMISSIONS];