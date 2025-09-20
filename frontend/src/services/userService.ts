// frontend/src/services/userService.ts

/**
 * User Service
 *
 * Client-side service for managing users within organizations.
 * Provides methods for creating, updating, deleting, and listing users.
 */
import api from "../lib/api";

export const userService = {
  // Create a new user in an organization
  // Password is optional; if not provided, backend generates OTP for initial login
  createUser: async (organizationId: number, userData: any): Promise<any> => {
    try {
      const response = await api.post(`/organizations/${organizationId}/users`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create user");
    }
  },

  // Get list of users in an organization
  getOrganizationUsers: async (organizationId: number, params?: any): Promise<any> => {
    try {
      const response = await api.get(`/organizations/${organizationId}/users`, { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization users");
    }
  },

  // Update a user in an organization
  updateUser: async (organizationId: number, userId: number, userData: any): Promise<any> => {
    try {
      const response = await api.put(`/organizations/${organizationId}/users/${userId}`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user");
    }
  },

  // Delete a user from an organization
  deleteUser: async (organizationId: number, userId: number): Promise<any> => {
    try {
      const response = await api.delete(`/organizations/${organizationId}/users/${userId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete user");
    }
  },

  // Reset a user's password (admin only)
  resetUserPassword: async (organizationId: number, userId: number): Promise<any> => {
    try {
      const response = await api.post(`/organizations/${organizationId}/users/${userId}/reset-password`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset user password");
    }
  },

  // NEW: Validate role before creation
  validateRole: (role: string): boolean => {
    const validRoles = ["super_admin", "org_admin", "management", "manager", "executive"];
    return validRoles.includes(role);
  },
};

export default userService;