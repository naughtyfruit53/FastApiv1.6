# app/models/workflow_automation_models.py
"""
Advanced Workflow Automation Models
These models provide comprehensive workflow automation capabilities for business processes
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime
from enum import Enum as PyEnum

class WorkflowStatus(PyEnum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepType(PyEnum):
    """Types of workflow steps"""
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    DATA_VALIDATION = "data_validation"
    CALCULATION = "calculation"
    API_CALL = "api_call"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    CONDITION = "condition"
    TIMER = "timer"
    HUMAN_TASK = "human_task"
    AUTO_TASK = "auto_task"


class WorkflowTriggerType(PyEnum):
    """Types of workflow triggers"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    API_TRIGGER = "api_trigger"
    EMAIL_TRIGGER = "email_trigger"
    WEBHOOK_TRIGGER = "webhook_trigger"


class BusinessRule(Base):
    """Business rules for workflow automation and validation"""
    __tablename__ = "business_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Rule identification
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # approval, validation, calculation, etc.
    
    # Rule definition
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_expression: Mapped[str] = mapped_column(Text, nullable=False)  # Business rule expression
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, default="condition")  # condition, calculation, validation
    
    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Context and scope
    applicable_entities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Entity types this rule applies to
    conditions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Conditions for rule execution
    actions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Actions to take when rule is triggered
    
    # Error handling
    error_action: Mapped[str] = mapped_column(String(50), default="stop", nullable=False)  # stop, continue, notify
    error_message_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Performance and monitoring
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    average_execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # in milliseconds
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="business_rules"
    )
    company: Mapped[Optional["Company"]] = relationship(
        "Company", back_populates="business_rules"
    )
    workflow_steps: Mapped[List["AutomationWorkflowStep"]] = relationship(
        "AutomationWorkflowStep", back_populates="business_rule"
    )
    rule_executions: Mapped[List["BusinessRuleExecution"]] = relationship(
        "BusinessRuleExecution", back_populates="business_rule"
    )
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_business_rule_org_code'),
        Index('idx_business_rule_org_category', 'organization_id', 'category'),
        Index('idx_business_rule_active', 'is_active'),
        {'extend_existing': True}
    )


class WorkflowTemplateAdvanced(Base):
    """Advanced workflow templates with comprehensive automation capabilities"""
    __tablename__ = "workflow_templates_advanced"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Template identification
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # procurement, hr, finance, etc.
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    
    # Template definition
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Trigger configuration
    trigger_type: Mapped[WorkflowTriggerType] = mapped_column(SQLEnum(WorkflowTriggerType), nullable=False, default=WorkflowTriggerType.MANUAL)
    trigger_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Configuration for triggers
    trigger_events: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Events that trigger this workflow
    
    # Workflow configuration
    parallel_execution: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timeout_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    retry_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    escalation_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Variables and parameters
    input_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Expected input variables
    output_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Expected output variables
    default_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Default variable values
    
    # Business rules integration
    pre_execution_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Rules to run before workflow
    post_execution_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Rules to run after workflow
    
    # Performance and monitoring
    execution_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # in minutes
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="workflow_templates_advanced"
    )
    company: Mapped[Optional["Company"]] = relationship(
        "Company", back_populates="workflow_templates_advanced"
    )
    workflow_steps: Mapped[List["AutomationWorkflowStep"]] = relationship(
        "AutomationWorkflowStep", back_populates="workflow_template", cascade="all, delete-orphan"
    )
    workflow_instances: Mapped[List["AutomationWorkflowInstance"]] = relationship(
        "AutomationWorkflowInstance", back_populates="workflow_template"
    )
    workflow_schedules: Mapped[List["WorkflowSchedule"]] = relationship(
        "WorkflowSchedule", back_populates="workflow_template"
    )
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_workflow_template_org_code'),
        Index('idx_workflow_template_org_category', 'organization_id', 'category'),
        Index('idx_workflow_template_active', 'is_active'),
        {'extend_existing': True}
    )


class AutomationWorkflowStep(Base):
    """Individual steps within a workflow"""
    __tablename__ = "workflow_steps_automation"  # Renamed to avoid conflict with workflow_models.py

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workflow_template_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Step identification
    step_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    step_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    step_type: Mapped[WorkflowStepType] = mapped_column(SQLEnum(WorkflowStepType), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Step configuration
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_parallel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timeout_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Conditions for step execution
    execution_condition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Condition expression
    skip_condition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Condition to skip this step
    
    # Step configuration
    step_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Step-specific configuration
    input_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # How to map inputs to this step
    output_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # How to map outputs from this step
    
    # Approval configuration (if step_type is approval)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approver_roles: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Roles that can approve
    approver_users: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Specific users that can approve
    approval_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # any, all, majority
    
    # Business rule integration
    business_rule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("business_rules.id"), nullable=True, index=True)
    
    # Error handling
    on_error_action: Mapped[str] = mapped_column(String(50), default="stop", nullable=False)  # stop, continue, retry
    retry_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_delay_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Next step configuration
    next_step_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("workflow_steps_automation.id"), nullable=True, index=True)
    conditional_next_steps: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Conditional next steps
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)

    # Relationships
    workflow_template: Mapped["WorkflowTemplateAdvanced"] = relationship(
        "WorkflowTemplateAdvanced", back_populates="workflow_steps"
    )
    business_rule: Mapped[Optional["BusinessRule"]] = relationship(
        "BusinessRule", back_populates="workflow_steps"
    )
    next_step: Mapped[Optional["AutomationWorkflowStep"]] = relationship(
        "AutomationWorkflowStep", remote_side=[id], back_populates="previous_steps"
    )
    previous_steps: Mapped[List["AutomationWorkflowStep"]] = relationship(
        "AutomationWorkflowStep", back_populates="next_step"
    )
    step_executions: Mapped[List["AutomationWorkflowStepExecution"]] = relationship(
        "AutomationWorkflowStepExecution", back_populates="workflow_step"
    )
    
    __table_args__ = (
        UniqueConstraint('workflow_template_id', 'step_order', name='uq_workflow_step_order'),
        UniqueConstraint('workflow_template_id', 'step_code', name='uq_workflow_step_code'),
        Index('idx_workflow_step_type', 'step_type'),
        {'extend_existing': True}
    )


class AutomationWorkflowInstance(Base):
    """Running instances of workflows"""
    __tablename__ = "workflow_instances_automation"  # Renamed to avoid conflict with workflow_models.py

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_template_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Instance identification
    instance_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    reference_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # invoice, purchase_order, etc.
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Instance status
    status: Mapped[WorkflowStatus] = mapped_column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.DRAFT, index=True)
    current_step_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("workflow_steps_automation.id"), nullable=True, index=True)
    
    # Execution tracking
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Data and variables
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Input data for the workflow
    current_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Current state of workflow data
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Output data from completed workflow
    
    # Progress tracking
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # User tracking
    initiated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="workflow_instances"
    )
    workflow_template: Mapped["WorkflowTemplateAdvanced"] = relationship(
        "WorkflowTemplateAdvanced", back_populates="workflow_instances"
    )
    current_step: Mapped[Optional["AutomationWorkflowStep"]] = relationship(
        "AutomationWorkflowStep", foreign_keys=[current_step_id]
    )
    step_executions: Mapped[List["AutomationWorkflowStepExecution"]] = relationship(
        "AutomationWorkflowStepExecution", back_populates="workflow_instance", cascade="all, delete-orphan"
    )
    initiator: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[initiated_by]
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to]
    )
    
    __table_args__ = (
        Index('idx_workflow_instance_org_status', 'organization_id', 'status'),
        Index('idx_workflow_instance_reference', 'reference_type', 'reference_id'),
        Index('idx_workflow_instance_template', 'workflow_template_id'),
        {'extend_existing': True}
    )


class AutomationWorkflowStepExecution(Base):
    """Execution details for individual workflow steps"""
    __tablename__ = "workflow_step_executions_automation"  # Renamed to avoid potential conflicts

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workflow_instance_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_instances_automation.id"), nullable=False, index=True)
    workflow_step_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_steps_automation.id"), nullable=False, index=True)
    
    # Execution tracking
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Data
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Approval tracking
    approval_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # pending, approved, rejected
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Execution details
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # User tracking
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    completed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)

    # Relationships
    workflow_instance: Mapped["AutomationWorkflowInstance"] = relationship(
        "AutomationWorkflowInstance", back_populates="step_executions"
    )
    workflow_step: Mapped["AutomationWorkflowStep"] = relationship(
        "AutomationWorkflowStep", back_populates="step_executions"
    )
    approver: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[approved_by]
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to]
    )
    completer: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[completed_by]
    )
    
    __table_args__ = (
        UniqueConstraint('workflow_instance_id', 'workflow_step_id', name='uq_workflow_step_execution'),
        Index('idx_workflow_step_execution_status', 'status'),
        Index('idx_workflow_step_execution_assignee', 'assigned_to'),
        {'extend_existing': True}
    )


class BusinessRuleExecution(Base):
    """Execution log for business rules"""
    __tablename__ = "business_rule_executions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("business_rules.id"), nullable=False, index=True)
    
    # Execution context
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    execution_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Execution details
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Results
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    result_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Triggered by
    triggered_by_user: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    triggered_by_system: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    business_rule: Mapped["BusinessRule"] = relationship(
        "BusinessRule", back_populates="rule_executions"
    )
    triggering_user: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[triggered_by_user]
    )
    
    __table_args__ = (
        Index('idx_business_rule_execution_rule', 'business_rule_id'),
        Index('idx_business_rule_execution_entity', 'entity_type', 'entity_id'),
        Index('idx_business_rule_execution_date', 'started_at'),
        {'extend_existing': True}
    )


class WorkflowSchedule(Base):
    """Scheduled execution of workflows"""
    __tablename__ = "workflow_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_template_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Schedule identification
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Schedule configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # once, recurring, cron
    schedule_expression: Mapped[str] = mapped_column(String(200), nullable=False)  # Cron expression or datetime
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="UTC")
    
    # Execution window
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Execution tracking
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Data
    default_input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="workflow_schedules"
    )
    workflow_template: Mapped["WorkflowTemplateAdvanced"] = relationship(
        "WorkflowTemplateAdvanced", back_populates="workflow_schedules"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[created_by]
    )
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_workflow_schedule_org_name'),
        Index('idx_workflow_schedule_active', 'is_active'),
        Index('idx_workflow_schedule_next_run', 'next_run_at'),
        {'extend_existing': True}
    )