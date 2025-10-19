// frontend/src/services/tallyService.ts

import api from "../lib/api";

interface TallyConfig {
  enabled: boolean;
  host: string;
  port: number;
  company_name: string;
  sync_frequency: string;
  last_sync?: string;
}

interface TallyConnectionTest {
  host: string;
  port: number;
  company_name: string;
}

interface TallyConnectionTestResponse {
  success: boolean;
  message: string;
  connection_time_ms?: number;
  server_info?: {
    version: string;
    company_count: number;
  };
  available_companies?: string[];
}

interface TallySyncResponse {
  success: boolean;
  items_synced: number;
  message: string;
}

const tallyService = {
  getTallyConfig: async (organizationId: number): Promise<TallyConfig> => {
    try {
      const response = await api.get(`/settings/tally/configuration`, {
        params: { organization_id: organizationId },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || "Failed to fetch Tally configuration");
    }
  },

  updateTallyConfig: async (organizationId: number, config: TallyConfig): Promise<TallyConfig> => {
    try {
      const response = await api.post(`/settings/tally/configuration`, config, {
        params: { organization_id: organizationId },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || "Failed to update Tally configuration");
    }
  },

  testTallyConnection: async (config: TallyConnectionTest): Promise<TallyConnectionTestResponse> => {
    try {
      const response = await api.post(`/settings/tally/test-connection`, config);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || "Failed to test Tally connection");
    }
  },

  syncWithTally: async (organizationId: number, syncType: string): Promise<TallySyncResponse> => {
    try {
      const response = await api.post(`/settings/tally/sync`, { sync_type: syncType }, {
        params: { organization_id: organizationId },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || "Failed to sync with Tally");
    }
  },
};

export default tallyService;