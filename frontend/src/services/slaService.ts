// frontend/src/services/slaService.ts

/**
 * SLA Management Service
 * Handles API calls for SLA policies and tracking
 */

import api from '../lib/api';

// Types for SLA Management
export interface SLAPolicy {
  id: number;
  organization_id: number;
  name: string;
  description?: string;
  priority?: string;
  ticket_type?: string;
  customer_tier?: string;
  response_time_hours: number;
  resolution_time_hours: number;
  escalation_enabled: boolean;
  escalation_threshold_percent: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at?: string;
  created_by_id?: number;
}

export interface SLATracking {
  id: number;
  organization_id: number;
  ticket_id: number;
  policy_id: number;
  response_deadline: string;
  resolution_deadline: string;
  first_response_at?: string;
  resolved_at?: string;
  response_status: 'pending' | 'met' | 'breached';
  resolution_status: 'pending' | 'met' | 'breached';
  escalation_triggered: boolean;
  escalation_triggered_at?: string;
  escalation_level: number;
  response_breach_hours?: number;
  resolution_breach_hours?: number;
  created_at: string;
  updated_at?: string;
}

export interface SLATrackingWithPolicy extends SLATracking {
  policy: SLAPolicy;
}

export interface SLAMetrics {
  total_tickets: number;
  response_sla_met: number;
  resolution_sla_met: number;
  response_sla_breached: number;
  resolution_sla_breached: number;
  escalated_tickets: number;
  avg_response_time_hours?: number;
  avg_resolution_time_hours?: number;
  response_sla_percentage: number;
  resolution_sla_percentage: number;
}

export interface SLAPolicyCreate {
  name: string;
  description?: string;
  priority?: string;
  ticket_type?: string;
  customer_tier?: string;
  response_time_hours: number;
  resolution_time_hours: number;
  escalation_enabled?: boolean;
  escalation_threshold_percent?: number;
  is_active?: boolean;
  is_default?: boolean;
}

export interface SLAPolicyUpdate extends Partial<SLAPolicyCreate> {}

export const slaService = {
  // SLA Policy Management
  getPolicies: async (organizationId: number, isActive?: boolean): Promise<SLAPolicy[]> => {
    try {
      const params = new URLSearchParams();
      if (isActive !== undefined) {
        params.append('is_active', isActive.toString());
      }
      
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/policies?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching SLA policies:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch SLA policies');
    }
  },

  getPolicy: async (organizationId: number, policyId: number): Promise<SLAPolicy> => {
    try {
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/policies/${policyId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching SLA policy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch SLA policy');
    }
  },

  createPolicy: async (organizationId: number, policy: SLAPolicyCreate): Promise<SLAPolicy> => {
    try {
      const response = await api.post(`/api/v1/sla/organizations/${organizationId}/policies`, policy);
      return response.data;
    } catch (error: any) {
      console.error('Error creating SLA policy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create SLA policy');
    }
  },

  updatePolicy: async (organizationId: number, policyId: number, policy: SLAPolicyUpdate): Promise<SLAPolicy> => {
    try {
      const response = await api.put(`/api/v1/sla/organizations/${organizationId}/policies/${policyId}`, policy);
      return response.data;
    } catch (error: any) {
      console.error('Error updating SLA policy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update SLA policy');
    }
  },

  deletePolicy: async (organizationId: number, policyId: number): Promise<void> => {
    try {
      await api.delete(`/api/v1/sla/organizations/${organizationId}/policies/${policyId}`);
    } catch (error: any) {
      console.error('Error deleting SLA policy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete SLA policy');
    }
  },

  // SLA Tracking
  assignSLAToTicket: async (organizationId: number, ticketId: number, forceRecreate?: boolean): Promise<any> => {
    try {
      const params = new URLSearchParams();
      if (forceRecreate) {
        params.append('force_recreate', 'true');
      }
      
      const response = await api.post(`/api/v1/sla/organizations/${organizationId}/tickets/${ticketId}/sla?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error assigning SLA to ticket:', error);
      throw new Error(error.response?.data?.detail || 'Failed to assign SLA to ticket');
    }
  },

  getTicketSLA: async (organizationId: number, ticketId: number): Promise<SLATrackingWithPolicy> => {
    try {
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/tickets/${ticketId}/sla`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching ticket SLA:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch ticket SLA');
    }
  },

  updateSLATracking: async (organizationId: number, trackingId: number, update: any): Promise<SLATracking> => {
    try {
      const response = await api.put(`/api/v1/sla/organizations/${organizationId}/tracking/${trackingId}`, update);
      return response.data;
    } catch (error: any) {
      console.error('Error updating SLA tracking:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update SLA tracking');
    }
  },

  // SLA Monitoring
  getBreachedSLAs: async (organizationId: number, limit?: number): Promise<SLATracking[]> => {
    try {
      const params = new URLSearchParams();
      if (limit) {
        params.append('limit', limit.toString());
      }
      
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/sla/breached?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching breached SLAs:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch breached SLAs');
    }
  },

  getEscalationCandidates: async (organizationId: number): Promise<SLATracking[]> => {
    try {
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/sla/escalation-candidates`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching escalation candidates:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch escalation candidates');
    }
  },

  triggerEscalation: async (organizationId: number, trackingId: number): Promise<any> => {
    try {
      const response = await api.post(`/api/v1/sla/organizations/${organizationId}/tracking/${trackingId}/escalate`);
      return response.data;
    } catch (error: any) {
      console.error('Error triggering escalation:', error);
      throw new Error(error.response?.data?.detail || 'Failed to trigger escalation');
    }
  },

  // SLA Analytics
  getSLAMetrics: async (
    organizationId: number, 
    startDate?: string, 
    endDate?: string, 
    days?: number
  ): Promise<SLAMetrics> => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (days) params.append('days', days.toString());
      
      const response = await api.get(`/api/v1/sla/organizations/${organizationId}/sla/metrics?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching SLA metrics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch SLA metrics');
    }
  },

  // Ticket Processing
  processTicketResponse: async (organizationId: number, ticketId: number, responseTime?: string): Promise<any> => {
    try {
      const params = new URLSearchParams();
      if (responseTime) {
        params.append('response_time', responseTime);
      }
      
      const response = await api.post(`/api/v1/sla/organizations/${organizationId}/tickets/${ticketId}/response?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error processing ticket response:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process ticket response');
    }
  },

  processTicketResolution: async (organizationId: number, ticketId: number, resolutionTime?: string): Promise<any> => {
    try {
      const params = new URLSearchParams();
      if (resolutionTime) {
        params.append('resolution_time', resolutionTime);
      }
      
      const response = await api.post(`/api/v1/sla/organizations/${organizationId}/tickets/${ticketId}/resolution?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Error processing ticket resolution:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process ticket resolution');
    }
  }
};

export default slaService;