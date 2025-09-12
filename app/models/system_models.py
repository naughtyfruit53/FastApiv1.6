# app/models/system_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_company_organization_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with qualified string to avoid multiple class error
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization", 
        back_populates="companies"
    )
    
    # User assignments for multi-company support
    user_assignments: Mapped[List["app.models.user_models.UserCompany"]] = relationship(
        "app.models.user_models.UserCompany",
        back_populates="company"
    )
    
    # Task Management relationships for multi-company support
    tasks: Mapped[List["app.models.task_management.Task"]] = relationship(
        "app.models.task_management.Task",
        back_populates="company"
    )
    task_projects: Mapped[List["app.models.task_management.TaskProject"]] = relationship(
        "app.models.task_management.TaskProject",
        back_populates="company"
    )
    
    # Business entity relationships for multi-company support
    vendors: Mapped[List["app.models.customer_models.Vendor"]] = relationship(
        "app.models.customer_models.Vendor",
        back_populates="company"
    )
    customers: Mapped[List["app.models.customer_models.Customer"]] = relationship(
        "app.models.customer_models.Customer",
        back_populates="company"
    )
    products: Mapped[List["app.models.product_models.Product"]] = relationship(
        "app.models.product_models.Product",
        back_populates="company"
    )
    
    # Project Management relationships
    projects: Mapped[List["app.models.project_models.Project"]] = relationship(
        "app.models.project_models.Project",
        back_populates="company"
    )
    
    # Workflow relationships
    workflow_templates: Mapped[List["app.models.workflow_models.WorkflowTemplate"]] = relationship(
        "app.models.workflow_models.WorkflowTemplate",
        back_populates="company"
    )
    approval_requests: Mapped[List["app.models.workflow_models.ApprovalRequest"]] = relationship(
        "app.models.workflow_models.ApprovalRequest",
        back_populates="company"
    )
    
    # API Gateway relationships
    api_keys: Mapped[List["app.models.api_gateway_models.APIKey"]] = relationship(
        "app.models.api_gateway_models.APIKey",
        back_populates="company"
    )
    webhooks: Mapped[List["app.models.api_gateway_models.Webhook"]] = relationship(
        "app.models.api_gateway_models.Webhook",
        back_populates="company"
    )
    
    # Integration relationships
    external_integrations: Mapped[List["app.models.integration_models.ExternalIntegration"]] = relationship(
        "app.models.integration_models.ExternalIntegration",
        back_populates="company"
    )
    
    # Master Data relationships
    categories: Mapped[List["app.models.master_data_models.Category"]] = relationship(
        "app.models.master_data_models.Category",
        back_populates="company"
    )
    units: Mapped[List["app.models.master_data_models.Unit"]] = relationship(
        "app.models.master_data_models.Unit",
        back_populates="company"
    )
    tax_codes: Mapped[List["app.models.master_data_models.TaxCode"]] = relationship(
        "app.models.master_data_models.TaxCode",
        back_populates="company"
    )
    payment_terms_extended: Mapped[List["app.models.master_data_models.PaymentTermsExtended"]] = relationship(
        "app.models.master_data_models.PaymentTermsExtended",
        back_populates="company"
    )
    
    # Advanced Workflow Automation relationships
    business_rules: Mapped[List["app.models.workflow_automation_models.BusinessRule"]] = relationship(
        "app.models.workflow_automation_models.BusinessRule",
        back_populates="company"
    )
    workflow_templates_advanced: Mapped[List["app.models.workflow_automation_models.WorkflowTemplateAdvanced"]] = relationship(
        "app.models.workflow_automation_models.WorkflowTemplateAdvanced",
        back_populates="company"
    )

    __table_args__ = (
        Index('idx_company_org_name', 'organization_id', 'name'),
        UniqueConstraint('organization_id', 'name', name='uq_company_org_name'),  # Allow multiple companies, but unique names per org
        {'extend_existing': True}
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_audit_log_organization_id"), nullable=True, index=True)
 
    # Audit details
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Made nullable
    action: Mapped[str] = mapped_column(String, nullable=False) # CREATE, UPDATE, DELETE
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_audit_log_user_id"), nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Store the changes made
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
 
    user: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
 
    __table_args__ = (
        Index('idx_audit_org_table_action', 'organization_id', 'table_name', 'action'),
        Index('idx_audit_org_timestamp', 'organization_id', 'timestamp'),
        {'extend_existing': True}
    )

class EmailNotification(Base):
    __tablename__ = "email_notifications"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_email_notification_organization_id"), nullable=False, index=True)
 
    # Email details
    to_email: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    voucher_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    voucher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending") # pending, sent, failed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
 
    __table_args__ = (
        Index('idx_email_org_status', 'organization_id', 'status'),
        {'extend_existing': True}
    )

class NotificationTemplate(Base):
    """
    Model for notification templates supporting multi-channel messaging.
    Supports email, SMS, and push notifications with variable substitution.
    """
    __tablename__ = "notification_templates"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_notification_template_organization_id"), nullable=False, index=True)
 
    # Template details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_type: Mapped[str] = mapped_column(String, nullable=False) # appointment_reminder, service_completion, follow_up, marketing
 
    # Channel support
    channel: Mapped[str] = mapped_column(String, nullable=False) # email, sms, push, in_app
 
    # Message content
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True) # For email/push notifications
    body: Mapped[str] = mapped_column(Text, nullable=False) # Main message content
    html_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # HTML version for emails
 
    # Trigger configuration
    trigger_event: Mapped[Optional[str]] = mapped_column(String, nullable=True) # customer_interaction, low_engagement, appointment_scheduled
    trigger_conditions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True) # JSON conditions for automated triggers
 
    # Template variables (JSON array of variable names that can be substituted)
    variables: Mapped[Optional[str]] = mapped_column(JSON, nullable=True) # ["customer_name", "appointment_date", "service_type"]
 
    # Status and metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_notification_template_created_by"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    __table_args__ = (
        Index('idx_notification_template_org_type', 'organization_id', 'template_type'),
        Index('idx_notification_template_org_channel', 'organization_id', 'channel'),
        UniqueConstraint('organization_id', 'name', name='uq_notification_template_org_name'),
        {'extend_existing': True}
    )

class NotificationLog(Base):
    """
    Model for tracking all sent notifications with delivery status and metadata.
    """
    __tablename__ = "notification_logs"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_notification_log_organization_id"), nullable=False, index=True)
 
    # Template reference (optional - can send without template)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notification_templates.id", name="fk_notification_log_template_id"), nullable=True)
 
    # Recipient information
    recipient_type: Mapped[str] = mapped_column(String, nullable=False) # customer, user, segment
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # customer_id or user_id
    recipient_identifier: Mapped[str] = mapped_column(String, nullable=False) # email, phone, device_token
 
    # Notification details
    channel: Mapped[str] = mapped_column(String, nullable=False) # email, sms, push, in_app
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
 
    # Delivery tracking
    status: Mapped[str] = mapped_column(String, default="pending") # pending, sent, delivered, failed, bounced
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # For email tracking
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # For link tracking
 
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
 
    # Context information
    trigger_event: Mapped[Optional[str]] = mapped_column(String, nullable=True) # What triggered this notification
    context_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True) # Additional context data
 
    # Metadata
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_notification_log_created_by"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
 
    __table_args__ = (
        Index('idx_notification_log_org_status', 'organization_id', 'status'),
        Index('idx_notification_log_org_channel', 'organization_id', 'channel'),
        Index('idx_notification_log_recipient', 'recipient_type', 'recipient_id'),
        Index('idx_notification_log_sent_at', 'sent_at'),
        {'extend_existing': True}
    )

class NotificationPreference(Base):
    """
    Model for managing notification preferences for users and customers.
    """
    __tablename__ = "notification_preferences"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_notification_preference_organization_id"), nullable=False, index=True)
 
    # Subject (user or customer)
    subject_type: Mapped[str] = mapped_column(String, nullable=False) # user, customer
    subject_id: Mapped[int] = mapped_column(Integer, nullable=False) # user_id or customer_id
 
    # Preference details
    notification_type: Mapped[str] = mapped_column(String, nullable=False) # appointment_reminder, service_completion, marketing, etc.
    channel: Mapped[str] = mapped_column(String, nullable=False) # email, sms, push, in_app
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
 
    # Channel-specific settings
    settings: Mapped[Optional[str]] = mapped_column(JSON, nullable=True) # Channel-specific preferences
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    __table_args__ = (
        Index('idx_notification_pref_org_subject', 'organization_id', 'subject_type', 'subject_id'),
        UniqueConstraint('organization_id', 'subject_type', 'subject_id', 'notification_type', 'channel',
                         name='uq_notification_pref_subject_type_channel'),
        {'extend_existing': True}
    )
 
# Payment Terms
class PaymentTerm(Base):
    __tablename__ = "payment_terms"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_payment_term_organization_id"), nullable=False, index=True)
 
    # Payment term details
    name: Mapped[str] = mapped_column(String, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
 
    __table_args__ = (
        Index('idx_payment_term_org_name', 'organization_id', 'name'),
        {'extend_existing': True}
    )

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field added
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_otp_organization_id"), nullable=True, index=True)
    
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String, nullable=False) # Store hashed OTP for security
    purpose: Mapped[str] = mapped_column(String, nullable=False, default="login") # login, password_reset, registration
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
 
    __table_args__ = (
        Index('idx_otp_email_purpose', 'email', 'purpose'),
        Index('idx_otp_expires', 'expires_at'),
        {'extend_existing': True}
    )