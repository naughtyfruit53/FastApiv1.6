from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date

class Ticket(Base):
    """
    Model for customer support tickets in the Service CRM.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "tickets"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ticket_organization_id"), nullable=False, index=True)
 
    # Ticket identification
    ticket_number: Mapped[str] = mapped_column(String, nullable=False, index=True) # Auto-generated unique ticket number
 
    # Customer and assignment
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_ticket_customer_id"), nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ticket_assigned_to_id"), nullable=True) # Assigned technician/user
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ticket_created_by_id"), nullable=True) # Who created the ticket
 
    # Ticket details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open") # 'open', 'in_progress', 'resolved', 'closed', 'cancelled'
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium") # 'low', 'medium', 'high', 'urgent'
    ticket_type: Mapped[str] = mapped_column(String, nullable=False, default="support") # 'support', 'maintenance', 'installation', 'complaint'
 
    # Resolution details
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # SLA and business metrics
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
 
    # Customer satisfaction
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 rating
    customer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped["Customer"] = relationship("Customer")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    history: Mapped[List["TicketHistory"]] = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")
    attachments: Mapped[List["TicketAttachment"]] = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    sla_tracking: Mapped[Optional["SLATracking"]] = relationship("SLATracking", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
 
    __table_args__ = (
        # Unique ticket number per organization
        UniqueConstraint('organization_id', 'ticket_number', name='uq_ticket_org_number'),
        Index('idx_ticket_org_status', 'organization_id', 'status'),
        Index('idx_ticket_org_priority', 'organization_id', 'priority'),
        Index('idx_ticket_org_type', 'organization_id', 'ticket_type'),
        Index('idx_ticket_org_customer', 'organization_id', 'customer_id'),
        Index('idx_ticket_org_assigned', 'organization_id', 'assigned_to_id'),
        Index('idx_ticket_created_at', 'created_at'),
        Index('idx_ticket_due_date', 'due_date'),
    )

class TicketHistory(Base):
    """
    Model for tracking ticket status changes and updates.
    Provides audit trail for all ticket modifications.
    """
    __tablename__ = "ticket_history"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ticket_history_organization_id"), nullable=False, index=True)
 
    # Ticket reference
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id", name="fk_ticket_history_ticket_id"), nullable=False)
 
    # Change details
    action: Mapped[str] = mapped_column(String, nullable=False) # 'created', 'status_changed', 'assigned', 'updated', 'commented'
    field_changed: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Which field was changed
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Previous value
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # New value
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Additional comments
 
    # User who made the change
    changed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ticket_history_changed_by_id"), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="history")
    changed_by: Mapped[Optional["User"]] = relationship("User")
 
    __table_args__ = (
        Index('idx_ticket_history_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_ticket_history_action', 'action'),
        Index('idx_ticket_history_created_at', 'created_at'),
        Index('idx_ticket_history_user', 'changed_by_id'),
    )

class TicketAttachment(Base):
    """
    Model for file attachments on tickets.
    Follows the same pattern as CustomerFile and VendorFile.
    """
    __tablename__ = "ticket_attachments"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ticket_attachment_organization_id"), nullable=False, index=True)
 
    # Ticket reference
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id", name="fk_ticket_attachment_ticket_id"), nullable=False)
 
    # File details
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general") # general, screenshot, document, etc.
 
    # Upload details
    uploaded_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ticket_attachment_uploaded_by_id"), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="attachments")
    uploaded_by: Mapped[Optional["User"]] = relationship("User")
 
    __table_args__ = (
        Index('idx_ticket_attachment_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_ticket_attachment_type', 'file_type'),
        Index('idx_ticket_attachment_uploaded_by', 'uploaded_by_id'),
    )

class SLAPolicy(Base):
    """
    Model for defining SLA policies for ticket management.
    Policies define response and resolution time requirements.
    """
    __tablename__ = "sla_policies"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sla_policy_organization_id"), nullable=False, index=True)
 
    # Policy identification and details
    name: Mapped[str] = mapped_column(String, nullable=False) # e.g., "Critical Support", "Standard Maintenance"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Applicability criteria
    priority: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'low', 'medium', 'high', 'urgent' - null means applies to all
    ticket_type: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'support', 'maintenance', etc. - null means applies to all
    customer_tier: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'premium', 'standard', etc. - null means applies to all
 
    # SLA time definitions (in hours)
    response_time_hours: Mapped[float] = mapped_column(Float, nullable=False) # Time to first response
    resolution_time_hours: Mapped[float] = mapped_column(Float, nullable=False) # Time to resolution
 
    # Escalation rules
    escalation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    escalation_threshold_percent: Mapped[float] = mapped_column(Float, default=80.0) # Escalate at 80% of SLA time
 
    # Status and configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False) # Default policy for unmatched tickets
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_sla_policy_created_by_id"), nullable=True)
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    sla_tracking: Mapped[List["SLATracking"]] = relationship("SLATracking", back_populates="policy", cascade="all, delete-orphan")
 
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_sla_policy_org_name'),
        Index('idx_sla_policy_org_active', 'organization_id', 'is_active'),
        Index('idx_sla_policy_priority', 'priority'),
        Index('idx_sla_policy_ticket_type', 'ticket_type'),
        Index('idx_sla_policy_default', 'is_default'),
    )

class SLATracking(Base):
    """
    Model for tracking SLA compliance for individual tickets.
    Tracks response times, resolution times, and escalation status.
    """
    __tablename__ = "sla_tracking"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sla_tracking_organization_id"), nullable=False, index=True)
 
    # References
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id", name="fk_sla_tracking_ticket_id"), nullable=False, unique=True) # One SLA tracking per ticket
    policy_id: Mapped[int] = mapped_column(Integer, ForeignKey("sla_policies.id", name="fk_sla_tracking_policy_id"), nullable=False)
 
    # SLA deadlines (calculated from policy and ticket creation time)
    response_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolution_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
 
    # Actual response and resolution times
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # SLA status tracking
    response_status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'met', 'breached'
    resolution_status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'met', 'breached'
 
    # Escalation tracking
    escalation_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0) # 0 = no escalation, 1+ = escalation levels
 
    # Breach calculations (in hours, negative = met SLA, positive = breached)
    response_breach_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_breach_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    ticket: Mapped["Ticket"] = relationship("Ticket")
    policy: Mapped["SLAPolicy"] = relationship("SLAPolicy", back_populates="sla_tracking")
 
    __table_args__ = (
        Index('idx_sla_tracking_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_sla_tracking_policy', 'policy_id'),
        Index('idx_sla_tracking_response_status', 'response_status'),
        Index('idx_sla_tracking_resolution_status', 'resolution_status'),
        Index('idx_sla_tracking_escalation', 'escalation_triggered'),
        Index('idx_sla_tracking_response_deadline', 'response_deadline'),
        Index('idx_sla_tracking_resolution_deadline', 'resolution_deadline'),
    )

class DispatchOrder(Base):
    """
    Model for material dispatch orders in the Service CRM.
    Links to customers and tracks dispatch status.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "dispatch_orders"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_dispatch_order_organization_id"), nullable=False, index=True)
 
    # Order identification
    order_number: Mapped[str] = mapped_column(String, nullable=False, index=True) # Auto-generated unique order number
 
    # Customer and order details
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_dispatch_order_customer_id"), nullable=False)
    ticket_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tickets.id", name="fk_dispatch_order_ticket_id"), nullable=True) # Optional link to support ticket
 
    # Dispatch details
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'in_transit', 'delivered', 'cancelled'
    dispatch_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # Address details
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_contact_person: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    delivery_contact_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
 
    # Notes and tracking
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    courier_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
 
    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_dispatch_order_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_dispatch_order_updated_by_id"), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped["Customer"] = relationship("Customer")
    ticket: Mapped[Optional["Ticket"]] = relationship("Ticket")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
    items: Mapped[List["DispatchItem"]] = relationship("DispatchItem", back_populates="dispatch_order", cascade="all, delete-orphan")
    installation_jobs: Mapped[List["InstallationJob"]] = relationship("InstallationJob", back_populates="dispatch_order", cascade="all, delete-orphan")
 
    __table_args__ = (
        # Unique order number per organization
        UniqueConstraint('organization_id', 'order_number', name='uq_dispatch_order_org_number'),
        Index('idx_dispatch_order_org_status', 'organization_id', 'status'),
        Index('idx_dispatch_order_org_customer', 'organization_id', 'customer_id'),
        Index('idx_dispatch_order_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_dispatch_order_dispatch_date', 'dispatch_date'),
        Index('idx_dispatch_order_delivery_date', 'expected_delivery_date'),
        Index('idx_dispatch_order_created_at', 'created_at'),
    )

class DispatchItem(Base):
    """
    Model for individual items in a dispatch order.
    Links to products and tracks quantities dispatched.
    """
    __tablename__ = "dispatch_items"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Dispatch order reference
    dispatch_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch_orders.id", name="fk_dispatch_item_dispatch_order_id"), nullable=False)
 
    # Product details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_dispatch_item_product_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
 
    # Item details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    serial_numbers: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of serial numbers
    batch_numbers: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of batch numbers
 
    # Status tracking
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'packed', 'dispatched', 'delivered'
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    dispatch_order: Mapped["DispatchOrder"] = relationship("DispatchOrder", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
 
    __table_args__ = (
        Index('idx_dispatch_item_order', 'dispatch_order_id'),
        Index('idx_dispatch_item_product', 'product_id'),
        Index('idx_dispatch_item_status', 'status'),
    )

class InstallationJob(Base):
    """
    Model for installation jobs created from dispatch orders.
    Tracks installation scheduling and completion.
    """
    __tablename__ = "installation_jobs"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_installation_job_organization_id"), nullable=False, index=True)
 
    # Job identification
    job_number: Mapped[str] = mapped_column(String, nullable=False, index=True) # Auto-generated unique job number
 
    # References
    dispatch_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch_orders.id", name="fk_installation_job_dispatch_order_id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_installation_job_customer_id"), nullable=False)
    ticket_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tickets.id", name="fk_installation_job_ticket_id"), nullable=True) # Optional link to support ticket
 
    # Installation details
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled") # 'scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled'
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium") # 'low', 'medium', 'high', 'urgent'
 
    # Scheduling
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # Assignment
    assigned_technician_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_job_assigned_technician_id"), nullable=True)
 
    # Installation details
    installation_address: Mapped[str] = mapped_column(Text, nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
 
    # Installation details
    installation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 rating
 
    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_job_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_job_updated_by_id"), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    dispatch_order: Mapped["DispatchOrder"] = relationship("DispatchOrder", back_populates="installation_jobs")
    customer: Mapped["Customer"] = relationship("Customer")
    ticket: Mapped[Optional["Ticket"]] = relationship("Ticket")
    assigned_technician: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_technician_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
 
    # New relationships for tasks and completion
    tasks: Mapped[List["InstallationTask"]] = relationship("InstallationTask", back_populates="installation_job", cascade="all, delete-orphan", order_by="InstallationTask.sequence_order")
    completion_record: Mapped[Optional["CompletionRecord"]] = relationship("CompletionRecord", back_populates="installation_job", uselist=False, cascade="all, delete-orphan")
    parts_used: Mapped[List["JobParts"]] = relationship("JobParts", back_populates="job", cascade="all, delete-orphan")
 
    __table_args__ = (
        # Unique job number per organization
        UniqueConstraint('organization_id', 'job_number', name='uq_installation_job_org_number'),
        Index('idx_installation_job_org_status', 'organization_id', 'status'),
        Index('idx_installation_job_org_customer', 'organization_id', 'customer_id'),
        Index('idx_installation_job_org_technician', 'organization_id', 'assigned_technician_id'),
        Index('idx_installation_job_dispatch_order', 'dispatch_order_id'),
        Index('idx_installation_job_scheduled_date', 'scheduled_date'),
        Index('idx_installation_job_priority', 'priority'),
        Index('idx_installation_job_created_at', 'created_at'),
    )

class InstallationTask(Base):
    """
    Model for individual tasks within an installation job.
    Allows breaking down installation jobs into manageable tasks.
    """
    __tablename__ = "installation_tasks"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_installation_task_organization_id"), nullable=False, index=True)
 
    # Installation job reference
    installation_job_id: Mapped[int] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_installation_task_installation_job_id"), nullable=False)
 
    # Task details
    task_number: Mapped[str] = mapped_column(String, nullable=False, index=True) # Auto-generated task number
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Task status and priority
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'in_progress', 'completed', 'cancelled', 'blocked'
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium") # 'low', 'medium', 'high', 'urgent'
 
    # Scheduling
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1) # Task order within job
 
    # Assignment
    assigned_technician_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_task_assigned_technician_id"), nullable=True)
 
    # Task timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # Task notes
    work_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Dependencies
    depends_on_task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("installation_tasks.id", name="fk_installation_task_depends_on_task_id"), nullable=True)
 
    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_task_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_installation_task_updated_by_id"), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    installation_job: Mapped["InstallationJob"] = relationship("InstallationJob", back_populates="tasks")
    assigned_technician: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_technician_id])
    depends_on_task: Mapped[Optional["InstallationTask"]] = relationship("InstallationTask", remote_side=[id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
 
    __table_args__ = (
        # Unique task number per organization
        UniqueConstraint('organization_id', 'task_number', name='uq_installation_task_org_number'),
        Index('idx_installation_task_org_job', 'organization_id', 'installation_job_id'),
        Index('idx_installation_task_status', 'status'),
        Index('idx_installation_task_technician', 'assigned_technician_id'),
        Index('idx_installation_task_sequence', 'installation_job_id', 'sequence_order'),
        Index('idx_installation_task_created_at', 'created_at'),
    )

class CompletionRecord(Base):
    """
    Model for tracking detailed completion records for installation jobs.
    Provides comprehensive tracking of completion process and customer feedback.
    """
    __tablename__ = "completion_records"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_completion_record_organization_id"), nullable=False, index=True)
 
    # Installation job reference
    installation_job_id: Mapped[int] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_completion_record_installation_job_id"), nullable=False, unique=True)
 
    # Completion details
    completion_status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'partial', 'completed', 'failed'
    completed_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_completion_record_completed_by_id"), nullable=False) # Must be assigned technician
 
    # Timing
    completion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Auto-calculated
 
    # Work performed
    work_performed: Mapped[str] = mapped_column(Text, nullable=False) # Required completion notes
    issues_encountered: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Materials and parts
    materials_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of materials
    parts_replaced: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of parts
 
    # Quality and verification
    quality_check_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photos_attached: Mapped[bool] = mapped_column(Boolean, default=False)
 
    # Customer interaction
    customer_present: Mapped[bool] = mapped_column(Boolean, default=True)
    customer_signature_received: Mapped[bool] = mapped_column(Boolean, default=False)
    customer_feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 rating
 
    # Follow-up requirements
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    follow_up_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Customer feedback workflow trigger
    feedback_request_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_request_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    installation_job: Mapped["InstallationJob"] = relationship("InstallationJob", back_populates="completion_record")
    completed_by: Mapped["User"] = relationship("User", foreign_keys=[completed_by_id])
 
    __table_args__ = (
        Index('idx_completion_record_org_job', 'organization_id', 'installation_job_id'),
        Index('idx_completion_record_status', 'completion_status'),
        Index('idx_completion_record_completed_by', 'completed_by_id'),
        Index('idx_completion_record_completion_date', 'completion_date'),
        Index('idx_completion_record_follow_up', 'follow_up_required', 'follow_up_date'),
        Index('idx_completion_record_feedback_sent', 'feedback_request_sent'),
    )

class CustomerFeedback(Base):
    """
    Model for capturing structured customer feedback and survey responses.
    Extends beyond basic completion feedback to provide detailed customer satisfaction tracking.
    """
    __tablename__ = "customer_feedback"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_feedback_organization_id"), nullable=False, index=True)
 
    # Job and customer references
    installation_job_id: Mapped[int] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_customer_feedback_installation_job_id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_customer_feedback_customer_id"), nullable=False)
    completion_record_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("completion_records.id", name="fk_customer_feedback_completion_record_id"), nullable=True)
 
    # Feedback details
    overall_rating: Mapped[int] = mapped_column(Integer, nullable=False) # 1-5 scale
    service_quality_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 scale
    technician_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 scale
    timeliness_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 scale
    communication_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-5 scale
 
    # Text feedback
    feedback_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Survey questions (JSON field for flexible survey forms)
    survey_responses: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON string
 
    # Recommendation and satisfaction
    would_recommend: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    satisfaction_level: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'very_satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very_dissatisfied'
 
    # Follow-up preferences
    follow_up_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_contact_method: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'email', 'phone', 'sms'
 
    # Status tracking
    feedback_status: Mapped[str] = mapped_column(String, nullable=False, default="submitted") # 'submitted', 'reviewed', 'responded', 'closed'
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_customer_feedback_reviewed_by_id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Metadata
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    installation_job: Mapped["InstallationJob"] = relationship("InstallationJob")
    customer: Mapped["Customer"] = relationship("Customer")
    completion_record: Mapped[Optional["CompletionRecord"]] = relationship("CompletionRecord")
    reviewed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by_id])
 
    __table_args__ = (
        Index('idx_customer_feedback_org_job', 'organization_id', 'installation_job_id'),
        Index('idx_customer_feedback_customer', 'customer_id'),
        Index('idx_customer_feedback_completion', 'completion_record_id'),
        Index('idx_customer_feedback_status', 'feedback_status'),
        Index('idx_customer_feedback_rating', 'overall_rating'),
        Index('idx_customer_feedback_submitted', 'submitted_at'),
    )

class ServiceClosure(Base):
    """
    Model for tracking service ticket closure workflow.
    Manages the formal closure process including manager approval and final status.
    """
    __tablename__ = "service_closures"
 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
 
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_service_closure_organization_id"), nullable=False, index=True)
 
    # Service references
    installation_job_id: Mapped[int] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_service_closure_installation_job_id"), nullable=False, unique=True)
    completion_record_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("completion_records.id", name="fk_service_closure_completion_record_id"), nullable=True)
    customer_feedback_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customer_feedback.id", name="fk_service_closure_customer_feedback_id"), nullable=True)
 
    # Closure workflow
    closure_status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'approved', 'closed', 'reopened'
    closure_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'completed', 'cancelled', 'customer_request', 'no_show'
    closure_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Manager approval workflow
    requires_manager_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_service_closure_approved_by_id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Final closure
    closed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_service_closure_closed_by_id"), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    final_closure_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Customer satisfaction requirements
    feedback_received: Mapped[bool] = mapped_column(Boolean, default=False)
    minimum_rating_met: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_required: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Reopening tracking
    reopened_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reopened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reopened_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_service_closure_last_reopened_by_id"), nullable=True)
    reopening_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
 
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
 
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    installation_job: Mapped["InstallationJob"] = relationship("InstallationJob")
    completion_record: Mapped[Optional["CompletionRecord"]] = relationship("CompletionRecord")
    customer_feedback: Mapped[Optional["CustomerFeedback"]] = relationship("CustomerFeedback")
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])
    closed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[closed_by_id])
    last_reopened_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[last_reopened_by_id])
 
    __table_args__ = (
        Index('idx_service_closure_org_job', 'organization_id', 'installation_job_id'),
        Index('idx_service_closure_status', 'closure_status'),
        Index('idx_service_closure_completion', 'completion_record_id'),
        Index('idx_service_closure_feedback', 'customer_feedback_id'),
        Index('idx_service_closure_approved_by', 'approved_by_id'),
        Index('idx_service_closure_closed_by', 'closed_by_id'),
        Index('idx_service_closure_approval_required', 'requires_manager_approval'),
        Index('idx_service_closure_feedback_received', 'feedback_received'),
        Index('idx_service_closure_escalation', 'escalation_required'),
    )