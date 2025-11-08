// frontend/src/services/organizationService.ts
import api from "../lib/api";
export const organizationService = {
  createLicense: async (data: any): Promise<any> => {
    try {
      const response = await api.post("/organizations/license/create", data, {
        timeout: 60000  // Increased to 60 seconds for long processing
      });
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to create organization license",
      );
    }
  },
  getCurrentOrganization: async (): Promise<any> => {
    try {
      const ts = new Date().getTime(); // Timestamp to bust cache
      const response = await api.get(`/organizations/current?ts=${ts}`, {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      console.log('Fetched organization data:', response.data); // Debug log
      console.log('Enabled modules:', response.data.enabled_modules); // Specific debug for enabled_modules
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch current organization:', error);
      throw new Error(
        error.userMessage || "Failed to get current organization",
      );
    }
  },
  updateOrganization: async (data: any): Promise<any> => {
    try {
      const response = await api.put("/organizations/current", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
  // Admin-only endpoints
  getAllOrganizations: async (): Promise<any> => {
    try {
      const response = await api.get("/organizations/");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organizations");
    }
  },
  getOrganization: async (id: number): Promise<any> => {
    try {
      const response = await api.get(`/organizations/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization");
    }
  },
  updateOrganizationById: async (id: number, data: any, config?: any): Promise<any> => {
    try {
      const response = await api.put(`/organizations/${id}`, data, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
  // New organization management endpoints
  createOrganization: async (data: any): Promise<any> => {
    try {
      const response = await api.post("/organizations/", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create organization");
    }
  },
  joinOrganization: async (organizationId: number): Promise<any> => {
    try {
      const response = await api.post(`/organizations/${organizationId}/join`);
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to join organization");
    }
  },
  getOrganizationMembers: async (organizationId: number): Promise<any> => {
    try {
      const response = await api.get(
        `/organizations/${organizationId}/members`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to get organization members",
      );
    }
  },
  inviteUserToOrganization: async (organizationId: number, userData: any): Promise<any> => {
    try {
      const response = await api.post(
        `/organizations/${organizationId}/invite`,
        userData,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to invite user to organization",
      );
    }
  },
  // User organization management
  getUserOrganizations: async (): Promise<any> => {
    try {
      const response = await api.get("/users/me/organizations");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get user organizations");
    }
  },
  switchOrganization: async (organizationId: number): Promise<any> => {
    try {
      const response = await api.put("/users/me/organization", {
        organization_id: organizationId,
      });
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to switch organization");
    }
  },
  deleteOrganization: async (organizationId: number): Promise<any> => {
    try {
      const response = await api.delete(`/organizations/${organizationId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete organization");
    }
  },
  // Organization-scoped user management
  getOrganizationUsers: async (organizationId: number, params?: any): Promise<any> => {
    try {
      const response = await api.get(`/organizations/${organizationId}/users`, {
        params,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization users");
    }
  },
  createUserInOrganization: async (organizationId: number, userData: any): Promise<any> => {
    try {
      const response = await api.post(
        `/organizations/${organizationId}/users`,
        userData,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to create user in organization",
      );
    }
  },
  updateUserInOrganization: async (
    organizationId: number,
    userId: number,
    userData: any,
  ): Promise<any> => {
    try {
      const response = await api.put(
        `/organizations/${organizationId}/users/${userId}`,
        userData,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to update user in organization",
      );
    }
  },
  deleteUserFromOrganization: async (
    organizationId: number,
    userId: number,
  ): Promise<any> => {
    try {
      const response = await api.delete(
        `/organizations/${organizationId}/users/${userId}`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to delete user from organization",
      );
    }
  },
  // Invitation management
  getOrganizationInvitations: async (organizationId: number, params?: any): Promise<any> => {
    try {
      const response = await api.get(
        `/organizations/${organizationId}/invitations`,
        { params },
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to get organization invitations",
      );
    }
  },
  resendInvitation: async (organizationId: number, invitationId: number): Promise<any> => {
    try {
      const response = await api.post(
        `/organizations/${organizationId}/invitations/${invitationId}/resend`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to resend invitation");
    }
  },
  cancelInvitation: async (organizationId: number, invitationId: number): Promise<any> => {
    try {
      const response = await api.delete(
        `/organizations/${organizationId}/invitations/${invitationId}`,
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to cancel invitation");
    }
  },
  resetUserPassword: async (organizationId: number, userId: number): Promise<any> => {
    try {
      const response = await api.post(`/organizations/${organizationId}/users/${userId}/reset-password`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset user password");
    }
  },

  // Organization settings management
  getOrganizationSettings: async (): Promise<any> => {
    try {
      const response = await api.get("/organizations/settings/");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization settings");
    }
  },

  updateOrganizationSettings: async (settings: any): Promise<any> => {
    try {
      const response = await api.put("/organizations/settings/", settings);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization settings");
    }
  },

  // New methods for module management
  getAvailableModules: async (): Promise<any> => {
    try {
      const response = await api.get("/organizations/available-modules");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get available modules");
    }
  },

  getOrganizationModules: async (id: number, config?: any): Promise<any> => {
    try {
      const response = await api.get(`/organizations/${id}/modules`, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization modules");
    }
  },

  updateOrganizationModules: async (id: number, data: any, config?: any): Promise<any> => {
    try {
      const response = await api.put(`/organizations/${id}/modules`, data, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization modules");
    }
  },

  // New method for reset
  resetOrganizationData: async (config?: any): Promise<any> => {
    try {
      const response = await api.post("/organizations/reset-data", {}, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset organization data");
    }
  },
};