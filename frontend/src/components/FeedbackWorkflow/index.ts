// Export all feedback workflow components
export { default as CustomerFeedbackModal } from './CustomerFeedbackModal';
export { default as ServiceClosureDialog } from './ServiceClosureDialog';
export { default as FeedbackStatusList } from './FeedbackStatusList';
export { default as FeedbackWorkflowIntegration } from './FeedbackWorkflowIntegration';
export { default as FeedbackWorkflowDemo } from './FeedbackWorkflowDemo';

// Export types
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