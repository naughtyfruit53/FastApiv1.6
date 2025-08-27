// Frontend service for customer feedback and service closure workflow API

import api from '../lib/api';

export interface CustomerFeedback {
  id: number;
  organization_id: number;
  installation_job_id: number;
  customer_id: number;
  completion_record_id?: number;
  overall_rating: number;
  service_quality_rating?: number;
  technician_rating?: number;
  timeliness_rating?: number;
  communication_rating?: number;
  feedback_comments?: string;
  improvement_suggestions?: string;
  survey_responses?: any;
  would_recommend?: boolean;
  satisfaction_level?: string;
  follow_up_preferred: boolean;
  preferred_contact_method?: string;
  feedback_status: string;
  reviewed_by_id?: number;
  reviewed_at?: string;
  response_notes?: string;
  submitted_at: string;
  updated_at?: string;
}

export interface ServiceClosure {
  id: number;
  organization_id: number;
  installation_job_id: number;
  completion_record_id?: number;
  customer_feedback_id?: number;
  closure_status: string;
  closure_reason?: string;
  closure_notes?: string;
  requires_manager_approval: boolean;
  approved_by_id?: number;
  approved_at?: string;
  approval_notes?: string;
  closed_by_id?: number;
  closed_at?: string;
  final_closure_notes?: string;
  feedback_received: boolean;
  minimum_rating_met: boolean;
  escalation_required: boolean;
  escalation_reason?: string;
  reopened_count: number;
  last_reopened_at?: string;
  last_reopened_by_id?: number;
  reopening_reason?: string;
  created_at: string;
  updated_at?: string;
}

export interface CustomerFeedbackCreate {
  installation_job_id: number;
  customer_id: number;
  completion_record_id?: number;
  overall_rating: number;
  service_quality_rating?: number;
  technician_rating?: number;
  timeliness_rating?: number;
  communication_rating?: number;
  feedback_comments?: string;
  improvement_suggestions?: string;
  survey_responses?: any;
  would_recommend?: boolean;
  satisfaction_level?: string;
  follow_up_preferred?: boolean;
  preferred_contact_method?: string;
}

export interface ServiceClosureCreate {
  installation_job_id: number;
  completion_record_id?: number;
  customer_feedback_id?: number;
  closure_reason?: string;
  closure_notes?: string;
  requires_manager_approval?: boolean;
  approval_notes?: string;
  final_closure_notes?: string;
  escalation_required?: boolean;
  escalation_reason?: string;
  reopening_reason?: string;
}

export interface FeedbackFilters {
  feedback_status?: string;
  overall_rating?: number;
  customer_id?: number;
  installation_job_id?: number;
  from_date?: string;
  to_date?: string;
  satisfaction_level?: string;
}

export interface ClosureFilters {
  closure_status?: string;
  closure_reason?: string;
  requires_manager_approval?: boolean;
  feedback_received?: boolean;
  escalation_required?: boolean;
  approved_by_id?: number;
  closed_by_id?: number;
  from_date?: string;
  to_date?: string;
}

export interface FeedbackAnalytics {
  period_days: number;
  total_feedback: number;
  average_rating: number;
  positive_feedback: number;
  negative_feedback: number;
  satisfaction_rate: number;
}

export interface ClosureAnalytics {
  period_days: number;
  total_closures: number;
  completed_closures: number;
  escalated_closures: number;
  average_reopens: number;
  completion_rate: number;
}

class FeedbackService {
  private readonly baseUrl = '/api/v1/feedback';

  // Customer Feedback Methods
  async submitFeedback(feedbackData: CustomerFeedbackCreate): Promise<CustomerFeedback> {
    const response = await api.post(`${this.baseUrl}/feedback`, feedbackData);
    return response.data;
  }

  async getFeedbackList(
    filters: FeedbackFilters = {},
    skip: number = 0,
    limit: number = 100
  ): Promise<CustomerFeedback[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...Object.entries(filters).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== '') {
          acc[key] = value.toString();
        }
        return acc;
      }, {} as Record<string, string>)
    });

    const response = await api.get(`${this.baseUrl}/feedback?${params}`);
    return response.data;
  }

  async getFeedbackById(feedbackId: number): Promise<CustomerFeedback> {
    const response = await api.get(`${this.baseUrl}/feedback/${feedbackId}`);
    return response.data;
  }

  async updateFeedback(
    feedbackId: number,
    updateData: Partial<CustomerFeedbackCreate>
  ): Promise<CustomerFeedback> {
    const response = await api.put(`${this.baseUrl}/feedback/${feedbackId}`, updateData);
    return response.data;
  }

  async reviewFeedback(
    feedbackId: number,
    responseNotes: string
  ): Promise<CustomerFeedback> {
    const response = await api.post(`${this.baseUrl}/feedback/${feedbackId}/review`, {
      response_notes: responseNotes
    });
    return response.data;
  }

  // Service Closure Methods
  async createServiceClosure(closureData: ServiceClosureCreate): Promise<ServiceClosure> {
    const response = await api.post(`${this.baseUrl}/service-closure`, closureData);
    return response.data;
  }

  async getServiceClosures(
    filters: ClosureFilters = {},
    skip: number = 0,
    limit: number = 100
  ): Promise<ServiceClosure[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      ...Object.entries(filters).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== '') {
          acc[key] = value.toString();
        }
        return acc;
      }, {} as Record<string, string>)
    });

    const response = await api.get(`${this.baseUrl}/service-closure?${params}`);
    return response.data;
  }

  async getServiceClosureById(closureId: number): Promise<ServiceClosure> {
    const response = await api.get(`${this.baseUrl}/service-closure/${closureId}`);
    return response.data;
  }

  async approveServiceClosure(
    closureId: number,
    approvalNotes?: string
  ): Promise<ServiceClosure> {
    const response = await api.post(`${this.baseUrl}/service-closure/${closureId}/approve`, {
      approval_notes: approvalNotes
    });
    return response.data;
  }

  async closeServiceTicket(
    closureId: number,
    finalClosureNotes?: string
  ): Promise<ServiceClosure> {
    const response = await api.post(`${this.baseUrl}/service-closure/${closureId}/close`, {
      final_closure_notes: finalClosureNotes
    });
    return response.data;
  }

  async reopenServiceTicket(
    closureId: number,
    reopeningReason: string
  ): Promise<ServiceClosure> {
    const response = await api.post(`${this.baseUrl}/service-closure/${closureId}/reopen`, {
      reopening_reason: reopeningReason
    });
    return response.data;
  }

  // Analytics Methods
  async getFeedbackAnalytics(days: number = 30): Promise<FeedbackAnalytics> {
    const response = await api.get(`${this.baseUrl}/feedback/analytics/summary?days=${days}`);
    return response.data;
  }

  async getClosureAnalytics(days: number = 30): Promise<ClosureAnalytics> {
    const response = await api.get(`${this.baseUrl}/service-closure/analytics/summary?days=${days}`);
    return response.data;
  }

  // Utility Methods
  async getFeedbackByJobId(jobId: number): Promise<CustomerFeedback | null> {
    try {
      const feedbackList = await this.getFeedbackList({ installation_job_id: jobId });
      return feedbackList.length > 0 ? feedbackList[0] : null;
    } catch (error) {
      console.error('Error fetching feedback by job ID:', error);
      return null;
    }
  }

  async getClosureByJobId(jobId: number): Promise<ServiceClosure | null> {
    try {
      const closureList = await this.getServiceClosures({ installation_job_id: jobId });
      return closureList.length > 0 ? closureList[0] : null;
    } catch (error) {
      console.error('Error fetching closure by job ID:', error);
      return null;
    }
  }

  // Workflow Integration Methods
  async triggerFeedbackRequest(jobId: number): Promise<void> {
    // This would trigger an automated feedback request
    // Could be called from the dispatch management system
    const response = await api.post(`${this.baseUrl}/feedback/trigger-request`, {
      installation_job_id: jobId
    });
    return response.data;
  }

  async canClosureBeCreated(jobId: number): Promise<boolean> {
    // Check if a service can be closed based on business rules
    try {
      const feedback = await this.getFeedbackByJobId(jobId);
      const existingClosure = await this.getClosureByJobId(jobId);
      
      // Business rules: feedback received and no existing closure
      return feedback !== null && existingClosure === null;
    } catch (error) {
      console.error('Error checking closure eligibility:', error);
      return false;
    }
  }
}

// Create singleton instance
export const feedbackService = new FeedbackService();

// Export types and service
export {
  FeedbackService,
  feedbackService as default
};