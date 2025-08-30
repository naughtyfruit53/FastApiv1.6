from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date

class CustomerAnalytics(Base):
    """
    Model for storing customer analytics data.
    Tracks customer-related metrics for reporting.
    """
    __tablename__ = "customer_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_analytics_organization_id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_customer_analytics_customer_id"), nullable=False, index=True)
    total_purchases: Mapped[float] = mapped_column(Float, default=0.0)
    average_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    purchase_frequency: Mapped[float] = mapped_column(Float, default=0.0)
    last_purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped["Customer"] = relationship("Customer")

    __table_args__ = (
        UniqueConstraint('organization_id', 'customer_id', name='uq_customer_analytics_org_customer'),
        Index('idx_customer_analytics_org', 'organization_id'),
    )

class SalesAnalytics(Base):
    """
    Model for storing sales analytics data.
    Tracks sales-related metrics for reporting.
    """
    __tablename__ = "sales_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sales_analytics_organization_id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'daily', 'weekly', 'monthly'
    total_sales: Mapped[float] = mapped_column(Float, default=0.0)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    average_sale_value: Mapped[float] = mapped_column(Float, default=0.0)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    __table_args__ = (
        UniqueConstraint('organization_id', 'period', 'summary_date', name='uq_sales_analytics_org_period_date'),
        Index('idx_sales_analytics_org_date', 'organization_id', 'summary_date'),
    )

class PurchaseAnalytics(Base):
    """
    Model for storing purchase analytics data.
    Tracks purchase-related metrics for reporting.
    """
    __tablename__ = "purchase_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_purchase_analytics_organization_id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'daily', 'weekly', 'monthly'
    total_purchases: Mapped[float] = mapped_column(Float, default=0.0)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    average_purchase_value: Mapped[float] = mapped_column(Float, default=0.0)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    __table_args__ = (
        UniqueConstraint('organization_id', 'period', 'summary_date', name='uq_purchase_analytics_org_period_date'),
        Index('idx_purchase_analytics_org_date', 'organization_id', 'summary_date'),
    )

class ServiceAnalytics(Base):
    """
    Model for storing service analytics data.
    Tracks service-related metrics for reporting.
    """
    __tablename__ = "service_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_service_analytics_organization_id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'daily', 'weekly', 'monthly'
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    average_completion_time: Mapped[float] = mapped_column(Float, default=0.0)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    __table_args__ = (
        UniqueConstraint('organization_id', 'period', 'summary_date', name='uq_service_analytics_org_period_date'),
        Index('idx_service_analytics_org_date', 'organization_id', 'summary_date'),
    )

class ServiceAnalyticsEvent(Base):
    """
    Model for storing individual analytics events for Service CRM.
    Used to track key events that contribute to analytics calculations.
    """
    __tablename__ = "service_analytics_events"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_service_analytics_event_organization_id"), nullable=False, index=True)
  
    # Event details
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True) # 'job_completed', 'job_started', 'feedback_received', 'sla_breach', etc.
    event_category: Mapped[str] = mapped_column(String, nullable=False, index=True) # 'completion', 'performance', 'satisfaction', 'volume', 'sla'
  
    # Related entities
    installation_job_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_service_analytics_event_installation_job_id"), nullable=True)
    technician_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_service_analytics_event_technician_id"), nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_service_analytics_event_customer_id"), nullable=True)
    completion_record_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("completion_records.id", name="fk_service_analytics_event_completion_record_id"), nullable=True)
    feedback_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customer_feedback.id", name="fk_service_analytics_event_feedback_id"), nullable=True)
  
    # Event data
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Flexible JSON field for event-specific data
    metric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Numeric metric value
  
    # Timing
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    installation_job: Mapped[Optional["InstallationJob"]] = relationship("InstallationJob")
    technician: Mapped[Optional["User"]] = relationship("User", foreign_keys=[technician_id])
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    completion_record: Mapped[Optional["CompletionRecord"]] = relationship("CompletionRecord")
    feedback: Mapped[Optional["CustomerFeedback"]] = relationship("CustomerFeedback")
  
    __table_args__ = (
        Index('idx_service_analytics_event_org_type', 'organization_id', 'event_type'),
        Index('idx_service_analytics_event_org_category', 'organization_id', 'event_category'),
        Index('idx_service_analytics_event_org_timestamp', 'organization_id', 'event_timestamp'),
        Index('idx_service_analytics_event_technician', 'technician_id'),
        Index('idx_service_analytics_event_customer', 'customer_id'),
        Index('idx_service_analytics_event_job', 'installation_job_id'),
    )

class ReportConfiguration(Base):
    """
    Model for storing user-defined report configurations.
    Allows users to save and schedule custom analytics reports.
    """
    __tablename__ = "report_configurations"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_report_configuration_organization_id"), nullable=False, index=True)
  
    # Configuration details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  
    # Report settings
    metric_types: Mapped[List[str]] = mapped_column(JSON, nullable=False) # List of metric types to include
    default_filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Default filter settings
  
    # Scheduling
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule_frequency: Mapped[Optional[str]] = mapped_column(String, nullable=True) # 'daily', 'weekly', 'monthly'
    schedule_time: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Time of day to run (HH:MM format)
    schedule_day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 0-6 for weekly schedules
    schedule_day_of_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 1-31 for monthly schedules
  
    # Email settings
    email_recipients: Mapped[List[str]] = mapped_column(JSON, nullable=True) # List of email addresses
    email_subject_template: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_generation_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_report_configuration_created_by_id"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_report_configuration_updated_by_id"), nullable=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
  
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_report_configuration_org_name'),
        Index('idx_report_configuration_org_active', 'organization_id', 'is_active'),
        Index('idx_report_configuration_schedule', 'schedule_enabled', 'next_generation_at'),
    )

class AnalyticsSummary(Base):
    """
    Model for storing pre-calculated analytics summaries.
    Used to cache frequently accessed metrics for better performance.
    """
    __tablename__ = "analytics_summaries"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_analytics_summary_organization_id"), nullable=False, index=True)
  
    # Summary details
    summary_type: Mapped[str] = mapped_column(String, nullable=False, index=True) # 'daily', 'weekly', 'monthly', 'technician', 'customer'
    summary_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
  
    # Aggregated metrics
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    pending_jobs: Mapped[int] = mapped_column(Integer, default=0)
    cancelled_jobs: Mapped[int] = mapped_column(Integer, default=0)
  
    # Performance metrics
    total_completion_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_completion_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # Customer satisfaction
    total_feedback_received: Mapped[int] = mapped_column(Integer, default=0)
    average_overall_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_service_quality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_technician_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # SLA metrics
    sla_met_count: Mapped[int] = mapped_column(Integer, default=0)
    sla_breached_count: Mapped[int] = mapped_column(Integer, default=0)
    sla_compliance_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # Entity-specific data
    technician_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_analytics_summary_technician_id"), nullable=True) # For technician-specific summaries
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_analytics_summary_customer_id"), nullable=True) # For customer-specific summaries
  
    # Additional summary data
    summary_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Extended metrics and flexible data
  
    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    technician: Mapped[Optional["User"]] = relationship("User", foreign_keys=[technician_id])
    customer: Mapped[Optional["Customer"]] = relationship("Customer", foreign_keys=[customer_id])
  
    __table_args__ = (
        UniqueConstraint('organization_id', 'summary_type', 'summary_date', 'technician_id', 'customer_id',
                        name='uq_analytics_summary_org_type_date_entities'),
        Index('idx_analytics_summary_org_type_date', 'organization_id', 'summary_type', 'summary_date'),
        Index('idx_analytics_summary_technician', 'technician_id'),
        Index('idx_analytics_summary_customer', 'customer_id'),
    )