// frontend/src/services/marketingService.ts

import api from '../lib/api';

export interface Campaign {
  id: number;
  campaign_number: string;
  name: string;
  campaign_type: string;
  status: string;
  start_date: string;
  end_date: string;
  budget: number;
  spent_amount?: number;
  target_audience?: string;
  description?: string;
  success_metrics?: any;
  performance_data?: any;
  created_at: string;
  updated_at?: string;
}

export interface Promotion {
  id: number;
  promotion_code: string;
  name: string;
  promotion_type: string;
  status: string;
  discount_type: string;
  discount_value: number;
  min_order_value?: number;
  max_discount_amount?: number;
  start_date: string;
  end_date: string;
  usage_limit?: number;
  current_usage?: number;
  applicable_products?: any;
  conditions?: any;
  created_at: string;
  updated_at?: string;
}

export interface MarketingAnalytics {
  total_campaigns: number;
  active_campaigns: number;
  total_promotions: number;
  active_promotions: number;
  campaign_roi: number;
  promotion_redemption_rate: number;
  email_open_rate: number;
  click_through_rate: number;
  conversion_rate: number;
  customer_acquisition_cost: number;
  lifetime_value: number;
  revenue_from_campaigns: number;
}

class MarketingService {
  private endpoint = '/marketing';

  /**
   * Get marketing analytics dashboard data
   */
  async getAnalytics(): Promise<MarketingAnalytics> {
    try {
      const response = await api.get(`${this.endpoint}/analytics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching marketing analytics:', error);
      throw error;
    }
  }

  /**
   * Get all campaigns
   */
  async getCampaigns(skip: number = 0, limit: number = 100): Promise<Campaign[]> {
    try {
      const response = await api.get(`${this.endpoint}/campaigns`, {
        params: { skip, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      throw error;
    }
  }

  /**
   * Get campaign by ID
   */
  async getCampaign(id: number): Promise<Campaign> {
    try {
      const response = await api.get(`${this.endpoint}/campaigns/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching campaign ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new campaign
   */
  async createCampaign(campaignData: any): Promise<Campaign> {
    try {
      const response = await api.post(`${this.endpoint}/campaigns`, campaignData);
      return response.data;
    } catch (error) {
      console.error('Error creating campaign:', error);
      throw error;
    }
  }

  /**
   * Update campaign
   */
  async updateCampaign(id: number, campaignData: any): Promise<Campaign> {
    try {
      const response = await api.put(`${this.endpoint}/campaigns/${id}`, campaignData);
      return response.data;
    } catch (error) {
      console.error(`Error updating campaign ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete campaign
   */
  async deleteCampaign(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/campaigns/${id}`);
    } catch (error) {
      console.error(`Error deleting campaign ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get all promotions
   */
  async getPromotions(skip: number = 0, limit: number = 100): Promise<Promotion[]> {
    try {
      const response = await api.get(`${this.endpoint}/promotions`, {
        params: { skip, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching promotions:', error);
      throw error;
    }
  }

  /**
   * Get promotion by ID
   */
  async getPromotion(id: number): Promise<Promotion> {
    try {
      const response = await api.get(`${this.endpoint}/promotions/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching promotion ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new promotion
   */
  async createPromotion(promotionData: any): Promise<Promotion> {
    try {
      const response = await api.post(`${this.endpoint}/promotions`, promotionData);
      return response.data;
    } catch (error) {
      console.error('Error creating promotion:', error);
      throw error;
    }
  }

  /**
   * Update promotion
   */
  async updatePromotion(id: number, promotionData: any): Promise<Promotion> {
    try {
      const response = await api.put(`${this.endpoint}/promotions/${id}`, promotionData);
      return response.data;
    } catch (error) {
      console.error(`Error updating promotion ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete promotion
   */
  async deletePromotion(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/promotions/${id}`);
    } catch (error) {
      console.error(`Error deleting promotion ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get campaign performance report
   */
  async getCampaignPerformance(id: number): Promise<any> {
    try {
      const response = await api.get(`${this.endpoint}/campaigns/${id}/performance`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching campaign performance for ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get promotion analytics
   */
  async getPromotionAnalytics(id: number): Promise<any> {
    try {
      const response = await api.get(`${this.endpoint}/promotions/${id}/analytics`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching promotion analytics for ${id}:`, error);
      throw error;
    }
  }
}

export const marketingService = new MarketingService();