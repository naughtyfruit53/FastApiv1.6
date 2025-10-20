// frontend/src/services/crmService.ts

import api from "@lib/api";

export interface Lead {
  id: number;
  lead_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source: string;
  status: string;
  score: number;
  estimated_value?: number;
  expected_close_date?: string;
  created_at: string;
  updated_at?: string;
  last_contacted?: string;
}

export interface Opportunity {
  id: number;
  opportunity_number: string;
  lead_id: number;
  name: string;
  description?: string;
  stage: string;
  probability: number;
  amount: number;
  expected_close_date: string;
  actual_close_date?: string;
  assigned_to_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface CRMAnalytics {
  leads_total: number;
  leads_by_status: { [key: string]: number };
  leads_by_source: { [key: string]: number };
  opportunities_total: number;
  opportunities_by_stage: { [key: string]: number };
  pipeline_value: number;
  weighted_pipeline_value: number;
  conversion_rate: number;
  average_deal_size: number;
  sales_cycle_days: number;
  win_rate: number;
  period_start: string;
  period_end: string;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  contact_number?: string;
  contact_person?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  pin_code?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

class CRMService {
  private endpoint = "/crm";

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("No authentication token found");
    }
    return {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
  }

  async getAnalytics(params: { period_start: string; period_end: string }): Promise<CRMAnalytics> {
    try {
      const response = await api.get(`${this.endpoint}/analytics`, {
        headers: this.getAuthHeaders(),
        params,
      });
      return response.data;
    } catch (error: any) {
      console.error("Error fetching CRM analytics:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to fetch analytics data");
    }
  }

  async getLeads(skip: number = 0, limit: number = 100): Promise<Lead[]> {
    try {
      const response = await api.get(`${this.endpoint}/leads`, {
        headers: this.getAuthHeaders(),
        params: { skip, limit },
      });
      return response.data;
    } catch (error: any) {
      console.error("Error fetching leads:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to fetch leads");
    }
  }

  async getLead(id: number): Promise<Lead> {
    try {
      const response = await api.get(`${this.endpoint}/leads/${id}`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error fetching lead ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to fetch lead ${id}`);
    }
  }

  async createLead(leadData: any): Promise<Lead> {
    try {
      const response = await api.post(`${this.endpoint}/leads`, leadData, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error("Error creating lead:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to create lead");
    }
  }

  async updateLead(id: number, leadData: any): Promise<Lead> {
    try {
      const response = await api.put(`${this.endpoint}/leads/${id}`, leadData, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error updating lead ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to update lead ${id}`);
    }
  }

  async deleteLead(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/leads/${id}`, {
        headers: this.getAuthHeaders(),
      });
    } catch (error: any) {
      console.error(`Error deleting lead ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to delete lead ${id}`);
    }
  }

  async getOpportunities(skip: number = 0, limit: number = 100): Promise<Opportunity[]> {
    try {
      const response = await api.get(`${this.endpoint}/opportunities`, {
        headers: this.getAuthHeaders(),
        params: { skip, limit },
      });
      return response.data;
    } catch (error: any) {
      console.error("Error fetching opportunities:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to fetch opportunities");
    }
  }

  async getOpportunity(id: number): Promise<Opportunity> {
    try {
      const response = await api.get(`${this.endpoint}/opportunities/${id}`, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error fetching opportunity ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to fetch opportunity ${id}`);
    }
  }

  async createOpportunity(opportunityData: any): Promise<Opportunity> {
    try {
      const response = await api.post(`${this.endpoint}/opportunities`, opportunityData, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error("Error creating opportunity:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to create opportunity");
    }
  }

  async updateOpportunity(id: number, opportunityData: any): Promise<Opportunity> {
    try {
      const response = await api.put(`${this.endpoint}/opportunities/${id}`, opportunityData, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error updating opportunity ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to update opportunity ${id}`);
    }
  }

  async deleteOpportunity(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/opportunities/${id}`, {
        headers: this.getAuthHeaders(),
      });
    } catch (error: any) {
      console.error(`Error deleting opportunity ${id}:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to delete opportunity ${id}`);
    }
  }

  async getCustomers(skip: number = 0, limit: number = 100): Promise<Customer[]> {
    try {
      const response = await api.get("/customers", {
        headers: this.getAuthHeaders(),
        params: { skip, limit },
      });
      return response.data;
    } catch (error: any) {
      console.error("Error fetching customers:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Failed to fetch customers");
    }
  }

  async convertLeadToOpportunity(leadId: number, opportunityData: any): Promise<Opportunity> {
    try {
      const response = await api.post(`${this.endpoint}/leads/${leadId}/convert`, opportunityData, {
        headers: this.getAuthHeaders(),
      });
      return response.data;
    } catch (error: any) {
      console.error(`Error converting lead ${leadId} to opportunity:`, error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || `Failed to convert lead ${leadId} to opportunity`);
    }
  }
}

export const crmService = new CRMService();