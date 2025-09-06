# app/models/workflow_models.py

"""
Workflow and Approval Engine Models for comprehensive business process automation
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base


class WorkflowStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class WorkflowTriggerType(PyEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"


class ApprovalStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class StepType(PyEnum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    CONDITION = "condition"
    ACTION = "action"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class InstanceStatus(PyEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class EscalationAction(PyEnum):
    EMAIL = "email"
    NOTIFICATION = "notification"
    REASSIGN = "reassign"
    AUTO_APPROVE = "auto_approve"
    ESCALATE_TO_MANAGER = "escalate_to_manager"


class WorkflowTemplate(Base):
    """Workflow template definitions for reusable business processes"""
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Template identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # HR, Finance, Procurement, etc.
    
    # Workflow configuration
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False)
    trigger_type = Column(Enum(WorkflowTriggerType), default=WorkflowTriggerType.MANUAL, nullable=False)
    
    # Template settings
    version = Column(String(20), default="1.0")
    is_default = Column(Boolean, default=False)
    allow_parallel_execution = Column(Boolean, default=False)
    auto_complete = Column(Boolean, default=True)
    
    # Entity association
    entity_type = Column(String(100), nullable=True)  # purchase_order, expense_claim, etc.
    entity_conditions = Column(JSON, nullable=True)  # Conditions for auto-triggering
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="workflow_templates")
    company = relationship("Company", back_populates="workflow_templates")
    creator = relationship("User")
    
    steps = relationship("WorkflowStep", back_populates="template", cascade="all, delete-orphan", order_by="WorkflowStep.step_order")
    instances = relationship("WorkflowInstance", back_populates="template", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', 'version', name='uq_workflow_template_org_name_version'),
        Index('idx_workflow_template_org_category', 'organization_id', 'category'),
        Index('idx_workflow_template_org_status', 'organization_id', 'status'),
        Index('idx_workflow_template_org_entity', 'organization_id', 'entity_type'),
    )


class WorkflowStep(Base):
    """Individual steps within a workflow template"""
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    
    # Step configuration
    step_name = Column(String(255), nullable=False)
    step_type = Column(Enum(StepType), nullable=False)
    step_order = Column(Integer, nullable=False)
    
    # Step behavior
    is_required = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=True)
    allow_rejection = Column(Boolean, default=True)
    
    # Assignment
    assigned_role = Column(String(100), nullable=True)  # Role-based assignment
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Direct assignment
    assignment_rules = Column(JSON, nullable=True)  # Complex assignment logic
    
    # Conditions
    condition_rules = Column(JSON, nullable=True)  # When this step should execute
    parallel_group = Column(String(50), nullable=True)  # For parallel steps
    
    # Escalation
    escalation_enabled = Column(Boolean, default=False)
    escalation_hours = Column(Integer, nullable=True)
    escalation_action = Column(Enum(EscalationAction), nullable=True)
    escalation_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notifications
    notification_template = Column(Text, nullable=True)
    send_email = Column(Boolean, default=True)
    send_in_app = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="steps")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    escalation_user = relationship("User", foreign_keys=[escalation_to_user_id])
    
    step_instances = relationship("WorkflowStepInstance", back_populates="step", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_workflow_step_org_template', 'organization_id', 'template_id'),
        Index('idx_workflow_step_org_order', 'organization_id', 'template_id', 'step_order'),
        Index('idx_workflow_step_org_type', 'organization_id', 'step_type'),
    )


class WorkflowInstance(Base):
    """Active workflow instances for specific entities"""
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    
    # Instance identification
    instance_name = Column(String(255), nullable=False)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Entity association
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_data = Column(JSON, nullable=True)  # Snapshot of entity data at workflow start
    
    # Instance status
    status = Column(Enum(InstanceStatus), default=InstanceStatus.CREATED, nullable=False)
    current_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=True)
    
    # Progress tracking
    total_steps = Column(Integer, nullable=False, default=0)
    completed_steps = Column(Integer, nullable=False, default=0)
    
    # Timeline
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Triggers
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    trigger_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="instances")
    triggered_by_user = relationship("User")
    current_step = relationship("WorkflowStep")
    
    step_instances = relationship("WorkflowStepInstance", back_populates="instance", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRequest", back_populates="workflow_instance", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_workflow_instance_org_template', 'organization_id', 'template_id'),
        Index('idx_workflow_instance_org_entity', 'organization_id', 'entity_type', 'entity_id'),
        Index('idx_workflow_instance_org_status', 'organization_id', 'status'),
        Index('idx_workflow_instance_org_triggered', 'organization_id', 'triggered_by'),
    )


class WorkflowStepInstance(Base):
    """Individual step executions within a workflow instance"""
    __tablename__ = "workflow_step_instances"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False)
    
    # Step execution
    status = Column(Enum(InstanceStatus), default=InstanceStatus.CREATED, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timeline
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Results
    result_data = Column(JSON, nullable=True)
    comments = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="step_instances")
    step = relationship("WorkflowStep", back_populates="step_instances")
    assignee = relationship("User")
    
    __table_args__ = (
        Index('idx_workflow_step_instance_org_instance', 'organization_id', 'instance_id'),
        Index('idx_workflow_step_instance_org_step', 'organization_id', 'step_id'),
        Index('idx_workflow_step_instance_org_status', 'organization_id', 'status'),
        Index('idx_workflow_step_instance_org_assigned', 'organization_id', 'assigned_to'),
    )


class ApprovalRequest(Base):
    """Approval requests for various business entities"""
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Approval identification
    approval_code = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Entity association
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    entity_data = Column(JSON, nullable=True)
    
    # Approval details
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Assignment
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Workflow association
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=True)
    step_instance_id = Column(Integer, ForeignKey("workflow_step_instances.id"), nullable=True)
    
    # Timeline
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deadline = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    
    # Decision
    decision = Column(Enum(ApprovalStatus), nullable=True)
    decision_comments = Column(Text, nullable=True)
    decision_data = Column(JSON, nullable=True)
    
    # Delegation
    delegated_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    delegation_reason = Column(Text, nullable=True)
    
    # Escalation
    escalated_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_reason = Column(Text, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="approval_requests")
    company = relationship("Company", back_populates="approval_requests")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[assigned_to])
    delegate = relationship("User", foreign_keys=[delegated_to])
    escalated_user = relationship("User", foreign_keys=[escalated_to])
    
    workflow_instance = relationship("WorkflowInstance", back_populates="approvals")
    step_instance = relationship("WorkflowStepInstance")
    
    attachments = relationship("ApprovalAttachment", back_populates="approval", cascade="all, delete-orphan")
    history = relationship("ApprovalHistory", back_populates="approval", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'approval_code', name='uq_approval_org_code'),
        Index('idx_approval_org_entity', 'organization_id', 'entity_type', 'entity_id'),
        Index('idx_approval_org_status', 'organization_id', 'status'),
        Index('idx_approval_org_assigned', 'organization_id', 'assigned_to'),
        Index('idx_approval_org_requested', 'organization_id', 'requested_by'),
    )


class ApprovalHistory(Base):
    """Audit trail for approval decisions and changes"""
    __tablename__ = "approval_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    
    # Action details
    action = Column(String(100), nullable=False)  # submitted, approved, rejected, delegated, etc.
    previous_status = Column(Enum(ApprovalStatus), nullable=True)
    new_status = Column(Enum(ApprovalStatus), nullable=False)
    
    # Actor information
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    comments = Column(Text, nullable=True)
    
    # Change data
    changes = Column(JSON, nullable=True)  # What changed
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    approval = relationship("ApprovalRequest", back_populates="history")
    performer = relationship("User")
    
    __table_args__ = (
        Index('idx_approval_history_org_approval', 'organization_id', 'approval_id'),
        Index('idx_approval_history_org_performer', 'organization_id', 'performed_by'),
        Index('idx_approval_history_org_action', 'organization_id', 'action'),
    )


class ApprovalAttachment(Base):
    """File attachments for approval requests"""
    __tablename__ = "approval_attachments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    
    # File details
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    approval = relationship("ApprovalRequest", back_populates="attachments")
    uploader = relationship("User")
    
    __table_args__ = (
        Index('idx_approval_attachment_org_approval', 'organization_id', 'approval_id'),
        Index('idx_approval_attachment_org_uploader', 'organization_id', 'uploaded_by'),
    )