// New: v1/frontend/src/services/adminService.ts

import api from '../lib/api';  // Changed import to use the correct api instance with /api/v1 baseURL

interface AppStatistics {
  total_licenses_issued: number;
  active_organizations: number;
  trial_organizations: number;
  total_active_users: number;
  super_admins_count: number;
  new_licenses_this_month: number;
  plan_breakdown: { [key: string]: number };
  system_health: {
    status: string;
    uptime: string;
  };
  generated_at: string;
}

interface OrgStatistics {
  total_products: number;
  total_customers: number;
  total_vendors: number;
  active_users: number;
  monthly_sales: number;
  inventory_value: number;
  plan_type: string;
  storage_used_gb: number;
  generated_at: string;
}

const adminService = {
  getAppStatistics: async (): Promise<AppStatistics> => {
    try {
      const response = await api.get<AppStatistics>('/organizations/app-statistics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch app statistics:', error);
      throw error;
    }
  },

  getOrgStatistics: async (): Promise<OrgStatistics> => {
    try {
      const response = await api.get<OrgStatistics>('/organizations/org-statistics');  // Assuming this endpoint exists in backend
      return response.data;
    } catch (error) {
      console.error('Failed to fetch organization statistics:', error);
      throw error;
    }
  },

  // Add more admin-related API calls as needed, e.g., manage licenses, organizations, etc.
  createLicense: async (licenseData: any) => {
    try {
      const response = await api.post('/organizations/license/create', licenseData);
      return response.data;
    } catch (error) {
      console.error('Failed to create license:', error);
      throw error;
    }
  },

  resetOrganizationData: async () => {
    try {
      const response = await api.post('/organizations/reset-data');
      return response.data;
    } catch (error) {
      console.error('Failed to reset organization data:', error);
      throw error;
    }
  },

  resetUserPassword: async (email: string) => {
    try {
      const response = await api.post('/password/admin-reset', { user_email: email });
      return response.data;
    } catch (error) {
      console.error('Failed to reset user password:', error);
      throw error;
    }
  }
};

export default adminService;