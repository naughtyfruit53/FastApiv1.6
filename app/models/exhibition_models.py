# app/models/exhibition_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime
import uuid


class ExhibitionEvent(Base):
    """Model for managing exhibition events where business cards are scanned"""
    __tablename__ = "exhibition_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Event details
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Event timing
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Event status
    status: Mapped[str] = mapped_column(String, default="planned")  # planned, active, completed, cancelled
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Exhibition settings
    auto_send_intro_email: Mapped[bool] = mapped_column(Boolean, default=True)
    intro_email_template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("notification_templates.id"), nullable=True
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization", back_populates="exhibition_events"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User", foreign_keys=[created_by_id]
    )
    card_scans: Mapped[List["BusinessCardScan"]] = relationship(
        "BusinessCardScan", back_populates="exhibition_event", cascade="all, delete-orphan"
    )
    prospects: Mapped[List["ExhibitionProspect"]] = relationship(
        "ExhibitionProspect", back_populates="exhibition_event", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_exhibition_event_org_status', 'organization_id', 'status'),
        Index('idx_exhibition_event_active', 'is_active'),
        {'extend_existing': True}
    )


class BusinessCardScan(Base):
    """Model for storing scanned business card data and OCR results"""
    __tablename__ = "business_card_scans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    exhibition_event_id: Mapped[int] = mapped_column(ForeignKey("exhibition_events.id"), nullable=False)
    
    # Scan metadata
    scan_id: Mapped[str] = mapped_column(String, unique=True, default=lambda: str(uuid.uuid4()))
    image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Path to uploaded card image
    scan_method: Mapped[str] = mapped_column(String, default="upload")  # upload, camera, scanner
    
    # OCR extracted data
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Raw OCR text
    extracted_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Structured extracted data
    
    # Extracted contact information
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Quality and validation
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # OCR confidence (0-1)
    validation_status: Mapped[str] = mapped_column(String, default="pending")  # pending, validated, rejected
    validated_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    validation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Processing status
    processing_status: Mapped[str] = mapped_column(String, default="scanned")  # scanned, processed, converted, failed
    prospect_created: Mapped[bool] = mapped_column(Boolean, default=False)
    intro_email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    scanned_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    exhibition_event: Mapped["ExhibitionEvent"] = relationship(
        "ExhibitionEvent", back_populates="card_scans"
    )
    scanned_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User", foreign_keys=[scanned_by_id]
    )
    validated_by: Mapped[Optional["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User", foreign_keys=[validated_by_id]
    )
    prospect: Mapped[Optional["ExhibitionProspect"]] = relationship(
        "ExhibitionProspect", back_populates="card_scan", uselist=False
    )
    
    __table_args__ = (
        Index('idx_card_scan_event', 'exhibition_event_id'),
        Index('idx_card_scan_status', 'processing_status'),
        Index('idx_card_scan_validation', 'validation_status'),
        {'extend_existing': True}
    )


class ExhibitionProspect(Base):
    """Model for prospects created from exhibition card scans"""
    __tablename__ = "exhibition_prospects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    exhibition_event_id: Mapped[int] = mapped_column(ForeignKey("exhibition_events.id"), nullable=False)
    card_scan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("business_card_scans.id"), nullable=True)
    
    # Contact information (refined from card scan)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Lead scoring and qualification
    lead_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    qualification_status: Mapped[str] = mapped_column(String, default="unqualified")  # unqualified, qualified, hot, cold
    interest_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # high, medium, low
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # CRM integration
    crm_customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Communication tracking
    intro_email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status and workflow
    status: Mapped[str] = mapped_column(String, default="new")  # new, contacted, qualified, converted, lost
    conversion_status: Mapped[str] = mapped_column(String, default="prospect")  # prospect, lead, customer
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    exhibition_event: Mapped["ExhibitionEvent"] = relationship(
        "ExhibitionEvent", back_populates="prospects"
    )
    card_scan: Mapped[Optional["BusinessCardScan"]] = relationship(
        "BusinessCardScan", back_populates="prospect"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User", foreign_keys=[created_by_id]
    )
    assigned_to: Mapped[Optional["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User", foreign_keys=[assigned_to_id]
    )
    crm_customer: Mapped[Optional["app.models.customer_models.Customer"]] = relationship(
        "app.models.customer_models.Customer"
    )
    
    __table_args__ = (
        Index('idx_exhibition_prospect_event', 'exhibition_event_id'),
        Index('idx_exhibition_prospect_status', 'status'),
        Index('idx_exhibition_prospect_assigned', 'assigned_to_id'),
        Index('idx_exhibition_prospect_company', 'company_name'),
        {'extend_existing': True}
    )