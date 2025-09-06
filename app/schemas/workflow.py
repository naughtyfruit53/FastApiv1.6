# app/schemas/workflow.py

"""
Workflow and Approval Engine Schemas for comprehensive business process automation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class WorkflowTriggerType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    CONDITION = "condition"
    ACTION = "action"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class InstanceStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class EscalationAction(str, Enum):
    EMAIL = "email"
    NOTIFICATION = "notification"
    REASSIGN = "reassign"
    AUTO_APPROVE = "auto_approve"
    ESCALATE_TO_MANAGER = "escalate_to_manager"


# Workflow Template Schemas
class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    trigger_type: WorkflowTriggerType = WorkflowTriggerType.MANUAL
    version: str = Field(default="1.0", max_length=20)
    is_default: bool = False
    allow_parallel_execution: bool = False
    auto_complete: bool = True
    entity_type: Optional[str] = Field(None, max_length=100)
    entity_conditions: Optional[Dict[str, Any]] = None


class WorkflowTemplateCreate(WorkflowTemplateBase):
    company_id: Optional[int] = None


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    status: Optional[WorkflowStatus] = None
    trigger_type: Optional[WorkflowTriggerType] = None
    version: Optional[str] = Field(None, max_length=20)
    is_default: Optional[bool] = None
    allow_parallel_execution: Optional[bool] = None
    auto_complete: Optional[bool] = None
    entity_type: Optional[str] = Field(None, max_length=100)
    entity_conditions: Optional[Dict[str, Any]] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    status: WorkflowStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowTemplateWithDetails(WorkflowTemplateResponse):
    creator_name: Optional[str] = None
    step_count: int = 0
    instance_count: int = 0
    active_instances: int = 0


# Workflow Step Schemas
class WorkflowStepBase(BaseModel):
    step_name: str = Field(..., min_length=1, max_length=255)
    step_type: StepType
    step_order: int = Field(..., ge=1)
    is_required: bool = True
    allow_delegation: bool = True
    allow_rejection: bool = True
    assigned_role: Optional[str] = Field(None, max_length=100)
    assigned_user_id: Optional[int] = None
    assignment_rules: Optional[Dict[str, Any]] = None
    condition_rules: Optional[Dict[str, Any]] = None
    parallel_group: Optional[str] = Field(None, max_length=50)
    escalation_enabled: bool = False
    escalation_hours: Optional[int] = Field(None, gt=0)
    escalation_action: Optional[EscalationAction] = None
    escalation_to_user_id: Optional[int] = None
    notification_template: Optional[str] = None
    send_email: bool = True
    send_in_app: bool = True


class WorkflowStepCreate(WorkflowStepBase):
    template_id: int


class WorkflowStepUpdate(BaseModel):
    step_name: Optional[str] = Field(None, min_length=1, max_length=255)
    step_type: Optional[StepType] = None
    step_order: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    allow_rejection: Optional[bool] = None
    assigned_role: Optional[str] = Field(None, max_length=100)
    assigned_user_id: Optional[int] = None
    assignment_rules: Optional[Dict[str, Any]] = None
    condition_rules: Optional[Dict[str, Any]] = None
    parallel_group: Optional[str] = Field(None, max_length=50)
    escalation_enabled: Optional[bool] = None
    escalation_hours: Optional[int] = Field(None, gt=0)
    escalation_action: Optional[EscalationAction] = None
    escalation_to_user_id: Optional[int] = None
    notification_template: Optional[str] = None
    send_email: Optional[bool] = None
    send_in_app: Optional[bool] = None


class WorkflowStepResponse(WorkflowStepBase):
    id: int
    organization_id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowStepWithDetails(WorkflowStepResponse):
    assigned_user_name: Optional[str] = None
    escalation_user_name: Optional[str] = None


# Workflow Instance Schemas
class WorkflowInstanceBase(BaseModel):
    instance_name: str = Field(..., min_length=1, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=100)
    entity_type: str = Field(..., max_length=100)
    entity_id: int
    entity_data: Optional[Dict[str, Any]] = None
    trigger_reason: Optional[str] = None
    deadline: Optional[datetime] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    template_id: int


class WorkflowInstanceUpdate(BaseModel):
    instance_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[InstanceStatus] = None
    deadline: Optional[datetime] = None
    trigger_reason: Optional[str] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    id: int
    organization_id: int
    template_id: int
    status: InstanceStatus
    current_step_id: Optional[int]
    total_steps: int
    completed_steps: int
    triggered_by: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowInstanceWithDetails(WorkflowInstanceResponse):
    template_name: Optional[str] = None
    triggered_by_name: Optional[str] = None
    current_step_name: Optional[str] = None
    progress_percentage: Optional[float] = None
    pending_approvals: List["ApprovalRequestResponse"] = []


# Approval Request Schemas
class ApprovalRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    entity_type: str = Field(..., max_length=100)
    entity_id: int
    entity_data: Optional[Dict[str, Any]] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    assigned_to: int
    deadline: Optional[datetime] = None


class ApprovalRequestCreate(ApprovalRequestBase):
    company_id: Optional[int] = None
    workflow_instance_id: Optional[int] = None
    step_instance_id: Optional[int] = None


class ApprovalRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[int] = None
    deadline: Optional[datetime] = None


class ApprovalDecision(BaseModel):
    decision: ApprovalStatus = Field(..., pattern="^(approved|rejected|delegated)$")
    decision_comments: Optional[str] = None
    decision_data: Optional[Dict[str, Any]] = None
    delegated_to: Optional[int] = None
    delegation_reason: Optional[str] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    approval_code: str
    status: ApprovalStatus
    requested_by: int
    workflow_instance_id: Optional[int]
    step_instance_id: Optional[int]
    requested_at: datetime
    responded_at: Optional[datetime]
    decision: Optional[ApprovalStatus]
    decision_comments: Optional[str]
    decision_data: Optional[Dict[str, Any]]
    delegated_to: Optional[int]
    delegation_reason: Optional[str]
    escalated_to: Optional[int]
    escalation_reason: Optional[str]
    escalated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalRequestWithDetails(ApprovalRequestResponse):
    requester_name: Optional[str] = None
    approver_name: Optional[str] = None
    delegate_name: Optional[str] = None
    escalated_user_name: Optional[str] = None
    entity_description: Optional[str] = None
    time_pending_hours: Optional[float] = None
    attachment_count: int = 0


# Approval History Schemas
class ApprovalHistoryResponse(BaseModel):
    id: int
    organization_id: int
    approval_id: int
    action: str
    previous_status: Optional[ApprovalStatus]
    new_status: ApprovalStatus
    performed_by: int
    comments: Optional[str]
    changes: Optional[Dict[str, Any]]
    created_at: datetime
    performer_name: Optional[str] = None

    class Config:
        from_attributes = True


# Dashboard and Analytics Schemas
class WorkflowDashboardStats(BaseModel):
    total_active_workflows: int
    pending_approvals: int
    overdue_approvals: int
    completed_today: int
    average_processing_time_hours: float
    approvals_by_status: Dict[str, int]
    workflows_by_type: Dict[str, int]
    top_pending_approvals: List[ApprovalRequestWithDetails]
    recent_completions: List[ApprovalRequestResponse]


class ApprovalDashboardStats(BaseModel):
    my_pending_approvals: int
    my_delegated_approvals: int
    my_escalated_approvals: int
    approvals_processed_today: int
    average_response_time_hours: float
    pending_by_priority: Dict[str, int]
    overdue_approvals: List[ApprovalRequestWithDetails]
    recent_decisions: List[ApprovalRequestResponse]


# Filter Schemas
class WorkflowTemplateFilter(BaseModel):
    status: Optional[WorkflowStatus] = None
    category: Optional[str] = None
    trigger_type: Optional[WorkflowTriggerType] = None
    entity_type: Optional[str] = None
    created_by: Optional[int] = None
    search: Optional[str] = None


class WorkflowInstanceFilter(BaseModel):
    template_id: Optional[int] = None
    status: Optional[InstanceStatus] = None
    entity_type: Optional[str] = None
    triggered_by: Optional[int] = None
    started_from: Optional[datetime] = None
    started_to: Optional[datetime] = None
    search: Optional[str] = None


class ApprovalRequestFilter(BaseModel):
    status: Optional[ApprovalStatus] = None
    entity_type: Optional[str] = None
    assigned_to: Optional[int] = None
    requested_by: Optional[int] = None
    priority: Optional[str] = None
    requested_from: Optional[datetime] = None
    requested_to: Optional[datetime] = None
    deadline_from: Optional[datetime] = None
    deadline_to: Optional[datetime] = None
    search: Optional[str] = None


# List Response Schemas
class WorkflowTemplateList(BaseModel):
    templates: List[WorkflowTemplateWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class WorkflowInstanceList(BaseModel):
    instances: List[WorkflowInstanceWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class ApprovalRequestList(BaseModel):
    approvals: List[ApprovalRequestWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


# Bulk Operations
class BulkApprovalDecision(BaseModel):
    approval_ids: List[int] = Field(..., min_items=1)
    decision: ApprovalStatus = Field(..., pattern="^(approved|rejected)$")
    decision_comments: Optional[str] = None


class BulkWorkflowAction(BaseModel):
    instance_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., pattern="^(cancel|pause|resume)$")
    reason: Optional[str] = None


# Export Schemas
class WorkflowExportRequest(BaseModel):
    template_ids: Optional[List[int]] = None
    instance_ids: Optional[List[int]] = None
    approval_ids: Optional[List[int]] = None
    filters: Optional[Dict[str, Any]] = None
    include_history: bool = True
    include_attachments: bool = False
    format: str = Field(default="excel", pattern="^(excel|csv|pdf)$")


# Update forward references
WorkflowInstanceWithDetails.model_rebuild()