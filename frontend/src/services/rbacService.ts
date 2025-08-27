// frontend/src/services/rbacService.ts

/**
 * Service CRM RBAC Service
 * 
 * Client-side service for managing Service CRM role-based access control.
 * Provides methods for managing roles, permissions, and user assignments.
 */

import api from '../lib/api';
import {
  ServicePermission,
  ServicePermissionCreate,
  ServiceRole,
  ServiceRoleWithPermissions,
  ServiceRoleCreate,
  ServiceRoleUpdate,
  UserServiceRole,
  UserWithServiceRoles,
  RoleAssignmentRequest,
  RoleAssignmentResponse,
  BulkRoleAssignmentRequest,
  BulkRoleAssignmentResponse,
  PermissionCheckRequest,
  PermissionCheckResponse,
  UserPermissions,
  ServiceModule,
  ServiceAction
} from '../types/rbac.types';

export const rbacService = {
  // Permission Management
  getPermissions: async (params?: { 
    module?: ServiceModule; 
    action?: ServiceAction; 
  }): Promise<ServicePermission[]> => {
    try {
      const response = await api.get('/rbac/permissions', { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch service permissions');
    }
  },

  initializeDefaultPermissions: async (): Promise<{ message: string; permissions: ServicePermission[] }> => {
    try {
      const response = await api.post('/rbac/permissions/initialize');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to initialize default permissions');
    }
  },

  // Role Management
  getOrganizationRoles: async (
    organizationId: number, 
    isActive?: boolean
  ): Promise<ServiceRole[]> => {
    try {
      const params = isActive !== undefined ? { is_active: isActive } : {};
      const response = await api.get(`/rbac/organizations/${organizationId}/roles`, { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch organization roles');
    }
  },

  createRole: async (
    organizationId: number, 
    roleData: ServiceRoleCreate
  ): Promise<ServiceRole> => {
    try {
      const response = await api.post(`/rbac/organizations/${organizationId}/roles`, {
        ...roleData,
        organization_id: organizationId
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to create service role');
    }
  },

  getRole: async (roleId: number): Promise<ServiceRoleWithPermissions> => {
    try {
      const response = await api.get(`/rbac/roles/${roleId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch service role');
    }
  },

  updateRole: async (roleId: number, updates: ServiceRoleUpdate): Promise<ServiceRole> => {
    try {
      const response = await api.put(`/rbac/roles/${roleId}`, updates);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to update service role');
    }
  },

  deleteRole: async (roleId: number): Promise<{ message: string }> => {
    try {
      const response = await api.delete(`/rbac/roles/${roleId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to delete service role');
    }
  },

  initializeDefaultRoles: async (organizationId: number): Promise<{ message: string; roles: ServiceRole[] }> => {
    try {
      const response = await api.post(`/rbac/organizations/${organizationId}/roles/initialize`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to initialize default roles');
    }
  },

  // User Role Assignment
  assignRolesToUser: async (
    userId: number, 
    assignment: RoleAssignmentRequest
  ): Promise<RoleAssignmentResponse> => {
    try {
      const response = await api.post(`/rbac/users/${userId}/roles`, {
        ...assignment,
        user_id: userId
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to assign roles to user');
    }
  },

  removeRoleFromUser: async (userId: number, roleId: number): Promise<{ message: string }> => {
    try {
      const response = await api.delete(`/rbac/users/${userId}/roles/${roleId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to remove role from user');
    }
  },

  removeAllRolesFromUser: async (userId: number): Promise<{ message: string }> => {
    try {
      const response = await api.delete(`/rbac/users/${userId}/roles`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to remove all roles from user');
    }
  },

  getUserServiceRoles: async (userId: number): Promise<ServiceRole[]> => {
    try {
      const response = await api.get(`/rbac/users/${userId}/roles`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch user service roles');
    }
  },

  getUsersWithRole: async (roleId: number): Promise<UserWithServiceRoles[]> => {
    try {
      const response = await api.get(`/rbac/roles/${roleId}/users`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch users with role');
    }
  },

  // Permission Checking
  checkUserPermission: async (
    request: PermissionCheckRequest
  ): Promise<PermissionCheckResponse> => {
    try {
      const response = await api.post('/rbac/permissions/check', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to check user permission');
    }
  },

  getUserPermissions: async (userId: number): Promise<UserPermissions> => {
    try {
      const response = await api.get(`/rbac/users/${userId}/permissions`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch user permissions');
    }
  },

  // Bulk Operations
  bulkAssignRoles: async (
    request: BulkRoleAssignmentRequest
  ): Promise<BulkRoleAssignmentResponse> => {
    try {
      const response = await api.post('/rbac/roles/assign/bulk', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to bulk assign roles');
    }
  },

  // Utility Functions
  getCurrentUserPermissions: async (): Promise<string[]> => {
    try {
      // Get current user first to get user ID
      const userResponse = await api.get('/users/me');
      const userId = userResponse.data.id;
      
      // Get user's service permissions
      const permissions = await rbacService.getUserPermissions(userId);
      return permissions.permissions;
    } catch (error: any) {
      console.warn('Failed to fetch current user permissions:', error);
      return [];
    }
  },

  getCurrentUserServiceRoles: async (): Promise<ServiceRole[]> => {
    try {
      // Get current user first to get user ID
      const userResponse = await api.get('/users/me');
      const userId = userResponse.data.id;
      
      // Get user's service roles
      return await rbacService.getUserServiceRoles(userId);
    } catch (error: any) {
      console.warn('Failed to fetch current user service roles:', error);
      return [];
    }
  },

  // Check if current user has specific service permission
  hasCurrentUserPermission: async (permission: string): Promise<boolean> => {
    try {
      const permissions = await rbacService.getCurrentUserPermissions();
      return permissions.includes(permission);
    } catch (error: any) {
      console.warn('Failed to check current user permission:', error);
      return false;
    }
  },

  // Get roles available for assignment in organization
  getAvailableRoles: async (organizationId: number): Promise<ServiceRole[]> => {
    try {
      return await rbacService.getOrganizationRoles(organizationId, true); // Only active roles
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch available roles');
    }
  },

  // Get comprehensive role data with permissions
  getRolesWithPermissions: async (organizationId: number): Promise<ServiceRoleWithPermissions[]> => {
    try {
      const roles = await rbacService.getOrganizationRoles(organizationId);
      
      // Fetch permissions for each role
      const rolesWithPermissions = await Promise.all(
        roles.map(async (role) => {
          try {
            return await rbacService.getRole(role.id);
          } catch (error) {
            console.warn(`Failed to fetch permissions for role ${role.id}:`, error);
            return { ...role, permissions: [] } as ServiceRoleWithPermissions;
          }
        })
      );
      
      return rolesWithPermissions;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch roles with permissions');
    }
  },

  // Get permissions grouped by module
  getPermissionsByModule: async (): Promise<Record<string, ServicePermission[]>> => {
    try {
      const permissions = await rbacService.getPermissions();
      const grouped: Record<string, ServicePermission[]> = {};
      
      permissions.forEach(permission => {
        if (!grouped[permission.module]) {
          grouped[permission.module] = [];
        }
        grouped[permission.module].push(permission);
      });
      
      return grouped;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to fetch permissions by module');
    }
  },

  // Validate role assignment (client-side checks)
  validateRoleAssignment: (
    userOrgId: number, 
    roleOrgId: number, 
    currentUserRole: string,
    isCurrentUserSuperAdmin: boolean
  ): { valid: boolean; error?: string } => {
    // Super admins can assign any role
    if (isCurrentUserSuperAdmin) {
      return { valid: true };
    }

    // Regular users can only assign roles within their organization
    if (userOrgId !== roleOrgId) {
      return { 
        valid: false, 
        error: 'Cannot assign roles across different organizations' 
      };
    }

    // Check if current user has permission to manage roles
    const canManageRoles = ['org_admin', 'admin'].includes(currentUserRole);
    if (!canManageRoles) {
      return { 
        valid: false, 
        error: 'Insufficient permissions to assign roles' 
      };
    }

    return { valid: true };
  }
};

// Export permission constants for easy import
export * from '../types/rbac.types';

export default rbacService;