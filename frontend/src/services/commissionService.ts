import api from "../lib/api";

export interface Commission {
  id: number;
  organization_id: number;
  sales_person_id: number;
  sales_person_name: string;
  person_type: "internal" | "external";
  opportunity_id?: number;
  lead_id?: number;
  commission_type: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount: number;
  commission_date: string;
  payment_status: string;
  payment_date?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  created_by_id?: number;
}

export interface CommissionCreate {
  sales_person_id: number;
  sales_person_name: string;
  person_type: "internal" | "external";
  opportunity_id?: number;
  lead_id?: number;
  commission_type: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount: number;
  commission_date: string;
  payment_status: string;
  payment_date?: string;
  notes?: string;
}

export interface CommissionUpdate {
  sales_person_name?: string;
  person_type?: "internal" | "external";
  opportunity_id?: number;
  lead_id?: number;
  commission_type?: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount?: number;
  commission_date?: string;
  payment_status?: string;
  payment_date?: string;
  notes?: string;
}

const commissionService = {
  // Get all commissions with filtering
  getCommissions: async (params?: {
    skip?: number;
    limit?: number;
    person_type?: string;
    payment_status?: string;
  }): Promise<Commission[]> => {
    const response = await api.get("/crm/commissions", { params });
    return response.data;
  },

  // Get single commission
  getCommission: async (commissionId: number): Promise<Commission> => {
    const response = await api.get(`/crm/commissions/${commissionId}`);
    return response.data;
  },

  // Create commission
  createCommission: async (data: CommissionCreate): Promise<Commission> => {
    const response = await api.post("/crm/commissions", data);
    return response.data;
  },

  // Update commission
  updateCommission: async (
    commissionId: number,
    data: CommissionUpdate
  ): Promise<Commission> => {
    const response = await api.put(`/crm/commissions/${commissionId}`, data);
    return response.data;
  },

  // Delete commission
  deleteCommission: async (commissionId: number): Promise<void> => {
    await api.delete(`/crm/commissions/${commissionId}`);
  },
};

export default commissionService;