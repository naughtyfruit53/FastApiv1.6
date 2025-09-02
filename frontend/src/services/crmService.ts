// frontend/src/services/crmService.ts

import api from "../lib/api";

export interface Lead {
  id: number;
  lead_number: string;
  company_name: string;
  contact_person: string;
  contact_email: string;
  contact_phone?: string;
  lead_source: string;
  lead_status: string;
  industry?: string;
  estimated_value?: number;
  expected_close_date?: string;
  last_activity_date?: string;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
}

export interface Opportunity {
  id: number;
  opportunity_number: string;
  lead_id: number;
  title: string;
  description?: string;
  stage: string;
  probability: number;
  estimated_value: number;
  expected_close_date: string;
  actual_close_date?: string;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
}

export interface CRMAnalytics {
  total_leads: number;
  qualified_leads: number;
  total_opportunities: number;
  won_opportunities: number;
  total_pipeline_value: number;
  avg_deal_size: number;
  lead_conversion_rate: number;
  sales_cycle_length: number;
  monthly_sales_target: number;
  monthly_sales_actual: number;
}

export interface Customer {
  id: number;
  customer_number: string;
  company_name: string;
  contact_person: string;
  contact_email: string;
  contact_phone?: string;
  billing_address?: string;
  shipping_address?: string;
  customer_type: string;
  credit_limit?: number;
  payment_terms?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

class CRMService {
  private endpoint = "/crm";

  /**
   * Get CRM analytics dashboard data
   */
  async getAnalytics(): Promise<CRMAnalytics> {
    try {
      const response = await api.get(`${this.endpoint}/analytics`);
      return response.data;
    } catch (error) {
      console.error("Error fetching CRM analytics:", error);
      throw error;
    }
  }

  /**
   * Get all leads
   */
  async getLeads(skip: number = 0, limit: number = 100): Promise<Lead[]> {
    try {
      const response = await api.get(`${this.endpoint}/leads`, {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching leads:", error);
      throw error;
    }
  }

  /**
   * Get lead by ID
   */
  async getLead(id: number): Promise<Lead> {
    try {
      const response = await api.get(`${this.endpoint}/leads/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching lead ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new lead
   */
  async createLead(leadData: any): Promise<Lead> {
    try {
      const response = await api.post(`${this.endpoint}/leads`, leadData);
      return response.data;
    } catch (error) {
      console.error("Error creating lead:", error);
      throw error;
    }
  }

  /**
   * Update lead
   */
  async updateLead(id: number, leadData: any): Promise<Lead> {
    try {
      const response = await api.put(`${this.endpoint}/leads/${id}`, leadData);
      return response.data;
    } catch (error) {
      console.error(`Error updating lead ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete lead
   */
  async deleteLead(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/leads/${id}`);
    } catch (error) {
      console.error(`Error deleting lead ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get all opportunities
   */
  async getOpportunities(
    skip: number = 0,
    limit: number = 100,
  ): Promise<Opportunity[]> {
    try {
      const response = await api.get(`${this.endpoint}/opportunities`, {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching opportunities:", error);
      throw error;
    }
  }

  /**
   * Get opportunity by ID
   */
  async getOpportunity(id: number): Promise<Opportunity> {
    try {
      const response = await api.get(`${this.endpoint}/opportunities/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching opportunity ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new opportunity
   */
  async createOpportunity(opportunityData: any): Promise<Opportunity> {
    try {
      const response = await api.post(
        `${this.endpoint}/opportunities`,
        opportunityData,
      );
      return response.data;
    } catch (error) {
      console.error("Error creating opportunity:", error);
      throw error;
    }
  }

  /**
   * Update opportunity
   */
  async updateOpportunity(
    id: number,
    opportunityData: any,
  ): Promise<Opportunity> {
    try {
      const response = await api.put(
        `${this.endpoint}/opportunities/${id}`,
        opportunityData,
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating opportunity ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete opportunity
   */
  async deleteOpportunity(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/opportunities/${id}`);
    } catch (error) {
      console.error(`Error deleting opportunity ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get all customers
   */
  async getCustomers(
    skip: number = 0,
    limit: number = 100,
  ): Promise<Customer[]> {
    try {
      const response = await api.get("/customers", {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching customers:", error);
      throw error;
    }
  }

  /**
   * Convert lead to opportunity
   */
  async convertLeadToOpportunity(
    leadId: number,
    opportunityData: any,
  ): Promise<Opportunity> {
    try {
      const response = await api.post(
        `${this.endpoint}/leads/${leadId}/convert`,
        opportunityData,
      );
      return response.data;
    } catch (error) {
      console.error(`Error converting lead ${leadId} to opportunity:`, error);
      throw error;
    }
  }
}

export const crmService = new CRMService();
