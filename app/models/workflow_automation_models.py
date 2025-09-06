# app/models/workflow_automation_models.py
"""
Advanced Workflow Automation Models
These models provide comprehensive workflow automation capabilities for business processes
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class WorkflowStatus(enum.Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepType(enum.Enum):
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


class WorkflowTriggerType(enum.Enum):
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

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Rule identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # approval, validation, calculation, etc.
    
    # Rule definition
    description = Column(Text, nullable=True)
    rule_expression = Column(Text, nullable=False)  # Business rule expression
    rule_type = Column(String(50), nullable=False, default="condition")  # condition, calculation, validation
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    execution_order = Column(Integer, default=0, nullable=False)
    
    # Context and scope
    applicable_entities = Column(JSON, nullable=True)  # Entity types this rule applies to
    conditions = Column(JSON, nullable=True)  # Conditions for rule execution
    actions = Column(JSON, nullable=True)  # Actions to take when rule is triggered
    
    # Error handling
    error_action = Column(String(50), default="stop", nullable=False)  # stop, continue, notify
    error_message_template = Column(Text, nullable=True)
    
    # Performance and monitoring
    execution_count = Column(Integer, default=0, nullable=False)
    last_executed_at = Column(DateTime, nullable=True)
    average_execution_time = Column(Float, default=0.0, nullable=False)  # in milliseconds
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="business_rules")
    company = relationship("Company", back_populates="business_rules")
    workflow_steps = relationship("WorkflowStep", back_populates="business_rule")
    rule_executions = relationship("BusinessRuleExecution", back_populates="business_rule")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_business_rule_org_code'),
        Index('idx_business_rule_org_category', 'organization_id', 'category'),
        Index('idx_business_rule_active', 'is_active'),
    )


class WorkflowTemplateAdvanced(Base):
    """Advanced workflow templates with comprehensive automation capabilities"""
    __tablename__ = "workflow_templates_advanced"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Template identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # procurement, hr, finance, etc.
    version = Column(String(20), nullable=False, default="1.0")
    
    # Template definition
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_template = Column(Boolean, default=True, nullable=False)
    
    # Trigger configuration
    trigger_type = Column(String(50), nullable=False, default="manual")
    trigger_config = Column(JSON, nullable=True)  # Configuration for triggers
    trigger_events = Column(JSON, nullable=True)  # Events that trigger this workflow
    
    # Workflow configuration
    parallel_execution = Column(Boolean, default=False, nullable=False)
    timeout_minutes = Column(Integer, nullable=True)  # Workflow timeout
    retry_attempts = Column(Integer, default=0, nullable=False)
    escalation_enabled = Column(Boolean, default=False, nullable=False)
    
    # Variables and parameters
    input_schema = Column(JSON, nullable=True)  # Expected input variables
    output_schema = Column(JSON, nullable=True)  # Expected output variables
    default_values = Column(JSON, nullable=True)  # Default variable values
    
    # Business rules integration
    pre_execution_rules = Column(JSON, nullable=True)  # Rules to run before workflow
    post_execution_rules = Column(JSON, nullable=True)  # Rules to run after workflow
    
    # Performance and monitoring
    execution_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    average_execution_time = Column(Float, default=0.0, nullable=False)  # in minutes
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="workflow_templates_advanced")
    company = relationship("Company", back_populates="workflow_templates_advanced")
    workflow_steps = relationship("WorkflowStep", back_populates="workflow_template", cascade="all, delete-orphan")
    workflow_instances = relationship("WorkflowInstance", back_populates="workflow_template")
    workflow_schedules = relationship("WorkflowSchedule", back_populates="workflow_template")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_workflow_template_org_code'),
        Index('idx_workflow_template_org_category', 'organization_id', 'category'),
        Index('idx_workflow_template_active', 'is_active'),
    )


class WorkflowStep(Base):
    """Individual steps within a workflow"""
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Step identification
    step_name = Column(String(200), nullable=False, index=True)
    step_code = Column(String(50), nullable=True, index=True)
    step_type = Column(String(50), nullable=False, index=True)
    step_order = Column(Integer, nullable=False, index=True)
    
    # Step configuration
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=True, nullable=False)
    is_parallel = Column(Boolean, default=False, nullable=False)
    timeout_minutes = Column(Integer, nullable=True)
    
    # Conditions for step execution
    execution_condition = Column(Text, nullable=True)  # Condition expression
    skip_condition = Column(Text, nullable=True)  # Condition to skip this step
    
    # Step configuration
    step_config = Column(JSON, nullable=True)  # Step-specific configuration
    input_mapping = Column(JSON, nullable=True)  # How to map inputs to this step
    output_mapping = Column(JSON, nullable=True)  # How to map outputs from this step
    
    # Approval configuration (if step_type is approval)
    approval_required = Column(Boolean, default=False, nullable=False)
    approver_roles = Column(JSON, nullable=True)  # Roles that can approve
    approver_users = Column(JSON, nullable=True)  # Specific users that can approve
    approval_method = Column(String(50), nullable=True)  # any, all, majority
    
    # Business rule integration
    business_rule_id = Column(Integer, ForeignKey("business_rules.id"), nullable=True, index=True)
    
    # Error handling
    on_error_action = Column(String(50), default="stop", nullable=False)  # stop, continue, retry
    retry_attempts = Column(Integer, default=0, nullable=False)
    retry_delay_minutes = Column(Integer, default=5, nullable=False)
    
    # Next step configuration
    next_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=True, index=True)
    conditional_next_steps = Column(JSON, nullable=True)  # Conditional next steps
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workflow_template = relationship("WorkflowTemplateAdvanced", back_populates="workflow_steps")
    business_rule = relationship("BusinessRule", back_populates="workflow_steps")
    next_step = relationship("WorkflowStep", remote_side=[id], back_populates="previous_steps")
    previous_steps = relationship("WorkflowStep", back_populates="next_step")
    step_executions = relationship("WorkflowStepExecution", back_populates="workflow_step")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('workflow_template_id', 'step_order', name='uq_workflow_step_order'),
        UniqueConstraint('workflow_template_id', 'step_code', name='uq_workflow_step_code'),
        Index('idx_workflow_step_type', 'step_type'),
    )


class WorkflowInstance(Base):
    """Running instances of workflows"""
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Instance identification
    instance_name = Column(String(200), nullable=True, index=True)
    reference_type = Column(String(100), nullable=True, index=True)  # invoice, purchase_order, etc.
    reference_id = Column(Integer, nullable=True, index=True)
    
    # Instance status
    status = Column(String(50), nullable=False, default="draft", index=True)
    current_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=True, index=True)
    
    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Data and variables
    input_data = Column(JSON, nullable=True)  # Input data for the workflow
    current_data = Column(JSON, nullable=True)  # Current state of workflow data
    output_data = Column(JSON, nullable=True)  # Output data from completed workflow
    
    # Progress tracking
    total_steps = Column(Integer, default=0, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    failed_steps = Column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # User tracking
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="workflow_instances")
    workflow_template = relationship("WorkflowTemplateAdvanced", back_populates="workflow_instances")
    current_step = relationship("WorkflowStep", foreign_keys=[current_step_id])
    step_executions = relationship("WorkflowStepExecution", back_populates="workflow_instance", cascade="all, delete-orphan")
    initiator = relationship("User", foreign_keys=[initiated_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    
    # Constraints
    __table_args__ = (
        Index('idx_workflow_instance_org_status', 'organization_id', 'status'),
        Index('idx_workflow_instance_reference', 'reference_type', 'reference_id'),
        Index('idx_workflow_instance_template', 'workflow_template_id'),
    )


class WorkflowStepExecution(Base):
    """Execution details for individual workflow steps"""
    __tablename__ = "workflow_step_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False, index=True)
    
    # Execution tracking
    status = Column(String(50), nullable=False, default="pending", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_data = Column(JSON, nullable=True)
    
    # Approval tracking
    approval_status = Column(String(50), nullable=True, index=True)  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    
    # Execution details
    execution_time_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # User tracking
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="step_executions")
    workflow_step = relationship("WorkflowStep", back_populates="step_executions")
    approver = relationship("User", foreign_keys=[approved_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    completer = relationship("User", foreign_keys=[completed_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('workflow_instance_id', 'workflow_step_id', name='uq_workflow_step_execution'),
        Index('idx_workflow_step_execution_status', 'status'),
        Index('idx_workflow_step_execution_assignee', 'assigned_to'),
    )


class BusinessRuleExecution(Base):
    """Execution log for business rules"""
    __tablename__ = "business_rule_executions"

    id = Column(Integer, primary_key=True, index=True)
    business_rule_id = Column(Integer, ForeignKey("business_rules.id"), nullable=False, index=True)
    
    # Execution context
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    execution_context = Column(JSON, nullable=True)
    
    # Execution details
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Results
    success = Column(Boolean, nullable=False, default=False)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Triggered by
    triggered_by_user = Column(Integer, ForeignKey("users.id"), nullable=True)
    triggered_by_system = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business_rule = relationship("BusinessRule", back_populates="rule_executions")
    triggering_user = relationship("User", foreign_keys=[triggered_by_user])
    
    # Constraints
    __table_args__ = (
        Index('idx_business_rule_execution_rule', 'business_rule_id'),
        Index('idx_business_rule_execution_entity', 'entity_type', 'entity_id'),
        Index('idx_business_rule_execution_date', 'started_at'),
    )


class WorkflowSchedule(Base):
    """Scheduled execution of workflows"""
    __tablename__ = "workflow_schedules"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates_advanced.id"), nullable=False, index=True)
    
    # Schedule identification
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Schedule configuration
    is_active = Column(Boolean, default=True, nullable=False)
    schedule_type = Column(String(50), nullable=False, index=True)  # once, recurring, cron
    schedule_expression = Column(String(200), nullable=False)  # Cron expression or datetime
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Execution window
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Execution tracking
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0, nullable=False)
    successful_runs = Column(Integer, default=0, nullable=False)
    failed_runs = Column(Integer, default=0, nullable=False)
    
    # Data
    default_input_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="workflow_schedules")
    workflow_template = relationship("WorkflowTemplateAdvanced", back_populates="workflow_schedules")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_workflow_schedule_org_name'),
        Index('idx_workflow_schedule_active', 'is_active'),
        Index('idx_workflow_schedule_next_run', 'next_run_at'),
    )