// frontend/src/services/procurementService.ts
import api from '../lib/api';

export interface RFQItem {
  item_code: string;
  item_name: string;
  item_description?: string;
  quantity: number;
  unit: string;
  specifications?: any;
  expected_price?: number;
}

export interface CreateRFQRequest {
  rfq_title: string;
  rfq_description?: string;
  issue_date: string;
  submission_deadline: string;
  validity_period?: number;
  terms_and_conditions?: string;
  delivery_requirements?: string;
  payment_terms?: string;
  is_public?: boolean;
  requires_samples?: boolean;
  allow_partial_quotes?: boolean;
  rfq_items: RFQItem[];
}

export interface UpdateRFQRequest {
  rfq_title?: string;
  rfq_description?: string;
  issue_date?: string;
  submission_deadline?: string;
  validity_period?: number;
  terms_and_conditions?: string;
  delivery_requirements?: string;
  payment_terms?: string;
  is_public?: boolean;
  requires_samples?: boolean;
  allow_partial_quotes?: boolean;
}

export interface RFQ {
  id: number;
  rfq_number: string;
  rfq_title: string;
  rfq_description?: string;
  issue_date: string;
  submission_deadline: string;
  validity_period?: number;
  terms_and_conditions?: string;
  delivery_requirements?: string;
  payment_terms?: string;
  status: string;
  is_public: boolean;
  requires_samples: boolean;
  allow_partial_quotes: boolean;
  created_at: string;
  updated_at: string;
  rfq_items: RFQItem[];
}

export interface GetRFQsParams {
  skip?: number;
  limit?: number;
  status?: string;
  search?: string;
}

export const procurementService = {
  // RFQ Management
  async getRFQs(params: GetRFQsParams = {}): Promise<RFQ[]> {
    const queryParams = new URLSearchParams();
    
    if (params.skip !== undefined) {queryParams.append('skip', params.skip.toString());}
    if (params.limit !== undefined) {queryParams.append('limit', params.limit.toString());}
    if (params.status) {queryParams.append('status', params.status);}
    if (params.search) {queryParams.append('search', params.search);}

    const response = await api.get(`/api/v1/procurement/rfqs?${queryParams.toString()}`);
    return response.data;
  },

  async getRFQ(id: number): Promise<RFQ> {
    const response = await api.get(`/api/v1/procurement/rfqs/${id}`);
    return response.data;
  },

  async createRFQ(data: CreateRFQRequest): Promise<RFQ> {
    const response = await api.post('/api/v1/procurement/rfqs', data);
    return response.data;
  },

  async updateRFQ(id: number, data: UpdateRFQRequest): Promise<RFQ> {
    const response = await api.put(`/api/v1/procurement/rfqs/${id}`, data);
    return response.data;
  },

  async deleteRFQ(id: number): Promise<void> {
    await api.delete(`/api/v1/procurement/rfqs/${id}`);
  },

  // RFQ Status Management
  async sendRFQ(id: number, vendorIds: number[]): Promise<RFQ> {
    const response = await api.post(`/api/v1/procurement/rfqs/${id}/send`, {
      vendor_ids: vendorIds
    });
    return response.data;
  },

  async cancelRFQ(id: number, reason?: string): Promise<RFQ> {
    const response = await api.post(`/api/v1/procurement/rfqs/${id}/cancel`, {
      reason
    });
    return response.data;
  },

  // Vendor Quotations
  async getQuotations(rfqId?: number, vendorId?: number): Promise<any[]> {
    const queryParams = new URLSearchParams();
    
    if (rfqId !== undefined) {queryParams.append('rfq_id', rfqId.toString());}
    if (vendorId !== undefined) {queryParams.append('vendor_id', vendorId.toString());}

    const response = await api.get(`/api/v1/procurement/quotations?${queryParams.toString()}`);
    return response.data;
  },

  async getQuotation(id: number): Promise<any> {
    const response = await api.get(`/api/v1/procurement/quotations/${id}`);
    return response.data;
  },

  async selectQuotation(id: number): Promise<any> {
    const response = await api.post(`/api/v1/procurement/quotations/${id}/select`);
    return response.data;
  },

  // Analytics
  async getDashboard(): Promise<any> {
    const response = await api.get('/api/v1/procurement/dashboard');
    return response.data;
  }
};

export default procurementService;