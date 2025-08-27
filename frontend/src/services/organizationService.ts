// frontend/src/services/organizationService.ts

import api from '../lib/api';

export const organizationService = {
  createLicense: async (data: any) => {
    try {
      const response = await api.post('/organizations/license/create', data);
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to create organization license');
    }
  },
  getCurrentOrganization: async () => {
    try {
      const response = await api.get('/organizations/current');
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get current organization');
    }
  },
  updateOrganization: async (data: any) => {
    try {
      const response = await api.put('/organizations/current', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to update organization');
    }
  },
  // Admin-only endpoints
  getAllOrganizations: async () => {
    try {
      const response = await api.get('/organizations/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organizations');
    }
  },
  getOrganization: async (id: number) => {
    try {
      const response = await api.get(`/organizations/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organization');
    }
  },
  updateOrganizationById: async (id: number, data: any) => {
    try {
      const response = await api.put(`/organizations/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to update organization');
    }
  },
  // New organization management endpoints
  createOrganization: async (data: any) => {
    try {
      const response = await api.post('/organizations/', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to create organization');
    }
  },
  joinOrganization: async (organizationId: number) => {
    try {
      const response = await api.post(`/organizations/${organizationId}/join`);
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to join organization');
    }
  },
  getOrganizationMembers: async (organizationId: number) => {
    try {
      const response = await api.get(`/organizations/${organizationId}/members`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organization members');
    }
  },
  inviteUserToOrganization: async (organizationId: number, userData: any) => {
    try {
      const response = await api.post(`/organizations/${organizationId}/invite`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to invite user to organization');
    }
  },
  // User organization management
  getUserOrganizations: async () => {
    try {
      const response = await api.get('/users/me/organizations');
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get user organizations');
    }
  },
  switchOrganization: async (organizationId: number) => {
    try {
      const response = await api.put('/users/me/organization', { organization_id: organizationId });
      // Organization context is managed by backend session only
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to switch organization');
    }
  },
  deleteOrganization: async (organizationId: number) => {
    try {
      const response = await api.delete(`/organizations/${organizationId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to delete organization');
    }
  },

  // Organization-scoped user management
  getOrganizationUsers: async (organizationId: number, params?: any) => {
    try {
      const response = await api.get(`/organizations/${organizationId}/users`, { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organization users');
    }
  },

  createUserInOrganization: async (organizationId: number, userData: any) => {
    try {
      const response = await api.post(`/organizations/${organizationId}/users`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to create user in organization');
    }
  },

  updateUserInOrganization: async (organizationId: number, userId: number, userData: any) => {
    try {
      const response = await api.put(`/organizations/${organizationId}/users/${userId}`, userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to update user in organization');
    }
  },

  deleteUserFromOrganization: async (organizationId: number, userId: number) => {
    try {
      const response = await api.delete(`/organizations/${organizationId}/users/${userId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to delete user from organization');
    }
  },

  // Invitation management
  getOrganizationInvitations: async (organizationId: number, params?: any) => {
    try {
      const response = await api.get(`/organizations/${organizationId}/invitations`, { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to get organization invitations');
    }
  },

  resendInvitation: async (organizationId: number, invitationId: number) => {
    try {
      const response = await api.post(`/organizations/${organizationId}/invitations/${invitationId}/resend`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to resend invitation');
    }
  },

  cancelInvitation: async (organizationId: number, invitationId: number) => {
    try {
      const response = await api.delete(`/organizations/${organizationId}/invitations/${invitationId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || 'Failed to cancel invitation');
    }
  },
};