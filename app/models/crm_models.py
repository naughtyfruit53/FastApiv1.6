# app/models/crm_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import enum

class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified" 
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"
    NURTURING = "nurturing"

class LeadSource(enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_MEDIA = "social_media"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    PARTNER = "partner"
    ADVERTISEMENT = "advertisement"
    OTHER = "other"

class OpportunityStage(enum.Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class Lead(Base):
    """
    Model for lead management in CRM.
    Leads are potential customers before they become opportunities.
    """
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_lead_organization_id"), nullable=False, index=True)
    
    # Lead identification
    lead_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    
    # Contact information
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    job_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Address information
    address1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pin_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Lead details
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    source: Mapped[LeadSource] = mapped_column(Enum(LeadSource), default=LeadSource.OTHER, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Lead scoring and qualification
    score: Mapped[int] = mapped_column(Integer, default=0) # Lead score from 0-100
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    qualification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Business potential
    estimated_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Assignment and ownership
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_lead_assigned_to_id"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_lead_created_by_id"), nullable=True)
    
    # Conversion tracking
    converted_to_customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_lead_converted_customer_id"), nullable=True)
    converted_to_opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", name="fk_lead_converted_opportunity_id"), nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Custom fields (JSON for flexibility)
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_contacted: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    converted_customer: Mapped[Optional["Customer"]] = relationship("Customer")
    converted_opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity")
    activities: Mapped[List["LeadActivity"]] = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_lead_org_status', 'organization_id', 'status'),
        Index('idx_lead_org_source', 'organization_id', 'source'),
        Index('idx_lead_org_assigned', 'organization_id', 'assigned_to_id'),
        Index('idx_lead_score', 'score'),
        Index('idx_lead_qualified', 'is_qualified'),
        Index('idx_lead_company', 'company'),
        UniqueConstraint('organization_id', 'lead_number', name='uq_lead_org_number'),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Opportunity(Base):
    """
    Model for sales opportunities in CRM.
    Opportunities are qualified leads with defined sales potential.
    """
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_opportunity_organization_id"), nullable=False, index=True)
    
    # Opportunity identification
    opportunity_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Sales pipeline
    stage: Mapped[OpportunityStage] = mapped_column(Enum(OpportunityStage), default=OpportunityStage.PROSPECTING, index=True)
    probability: Mapped[float] = mapped_column(Float, default=0.0) # Probability of closing (0-100%)
    
    # Financial details
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expected_revenue: Mapped[float] = mapped_column(Float, nullable=False) # amount * probability / 100
    
    # Timeline
    expected_close_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Customer and assignment
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_opportunity_customer_id"), nullable=True)
    lead_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("leads.id", name="fk_opportunity_lead_id"), nullable=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_opportunity_assigned_to_id"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_opportunity_created_by_id"), nullable=True)
    
    # Competition and context
    competitors: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of competitor names
    win_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    loss_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source tracking
    source: Mapped[LeadSource] = mapped_column(Enum(LeadSource), default=LeadSource.OTHER, index=True)
    
    # Custom fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    lead: Mapped[Optional["Lead"]] = relationship("Lead")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    activities: Mapped[List["OpportunityActivity"]] = relationship("OpportunityActivity", back_populates="opportunity", cascade="all, delete-orphan")
    products: Mapped[List["OpportunityProduct"]] = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_opportunity_org_stage', 'organization_id', 'stage'),
        Index('idx_opportunity_org_assigned', 'organization_id', 'assigned_to_id'),
        Index('idx_opportunity_close_date', 'expected_close_date'),
        Index('idx_opportunity_amount', 'amount'),
        Index('idx_opportunity_probability', 'probability'),
        UniqueConstraint('organization_id', 'opportunity_number', name='uq_opportunity_org_number'),
    )

class OpportunityProduct(Base):
    """
    Products/services associated with an opportunity.
    """
    __tablename__ = "opportunity_products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_opportunity_product_organization_id"), nullable=False, index=True)
    
    # References
    opportunity_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunities.id", name="fk_opportunity_product_opportunity_id"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id", name="fk_opportunity_product_product_id"), nullable=True)
    
    # Product details (can be custom product not in master)
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    product_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pricing and quantity
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    final_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="products")
    product: Mapped[Optional["Product"]] = relationship("Product")
    
    __table_args__ = (
        Index('idx_opportunity_product_org_opp', 'organization_id', 'opportunity_id'),
    )

class LeadActivity(Base):
    """
    Activity tracking for leads (calls, emails, meetings, etc.)
    """
    __tablename__ = "lead_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_lead_activity_organization_id"), nullable=False, index=True)
    
    # References
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id", name="fk_lead_activity_lead_id"), nullable=False)
    
    # Activity details
    activity_type: Mapped[str] = mapped_column(String, nullable=False) # call, email, meeting, note, task
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String, nullable=True) # completed, no_answer, follow_up_required, etc.
    
    # Scheduling
    activity_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Assignment
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_lead_activity_created_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_lead_activity_org_lead', 'organization_id', 'lead_id'),
        Index('idx_lead_activity_type', 'activity_type'),
        Index('idx_lead_activity_date', 'activity_date'),
    )

class OpportunityActivity(Base):
    """
    Activity tracking for opportunities
    """
    __tablename__ = "opportunity_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_opportunity_activity_organization_id"), nullable=False, index=True)
    
    # References
    opportunity_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunities.id", name="fk_opportunity_activity_opportunity_id"), nullable=False)
    
    # Activity details
    activity_type: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Scheduling
    activity_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Assignment
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_opportunity_activity_created_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="activities")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_opportunity_activity_org_opp', 'organization_id', 'opportunity_id'),
        Index('idx_opportunity_activity_type', 'activity_type'),
        Index('idx_opportunity_activity_date', 'activity_date'),
    )

class SalesPipeline(Base):
    """
    Sales pipeline configuration for opportunities
    """
    __tablename__ = "sales_pipelines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sales_pipeline_organization_id"), nullable=False, index=True)
    
    # Pipeline configuration
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Pipeline stages (JSON configuration)
    stages: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False) # Stage configurations with probabilities
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_sales_pipeline_created_by_id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_sales_pipeline_org_name'),
        Index('idx_sales_pipeline_org_default', 'organization_id', 'is_default'),
    )

class SalesForecast(Base):
    """
    Sales forecasting data and predictions
    """
    __tablename__ = "sales_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sales_forecast_organization_id"), nullable=False, index=True)
    
    # Forecast period
    forecast_period: Mapped[str] = mapped_column(String, nullable=False) # monthly, quarterly, yearly
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Forecast metrics
    predicted_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_revenue: Mapped[float] = mapped_column(Float, nullable=False) # Based on probabilities
    committed_revenue: Mapped[float] = mapped_column(Float, nullable=False) # High-probability deals
    best_case_revenue: Mapped[float] = mapped_column(Float, nullable=False) # All deals if won
    worst_case_revenue: Mapped[float] = mapped_column(Float, nullable=False) # Conservative estimate
    
    # Opportunity counts
    total_opportunities: Mapped[int] = mapped_column(Integer, nullable=False)
    opportunities_by_stage: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)
    
    # Model information
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False) # 0-100%
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_sales_forecast_created_by_id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_sales_forecast_org_period', 'organization_id', 'forecast_period', 'period_start'),
        UniqueConstraint('organization_id', 'forecast_period', 'period_start', 'period_end', name='uq_sales_forecast_period'),
    )