# app/models/customer_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date

class Vendor(Base):
    __tablename__ = "vendors"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_vendor_organization_id"), nullable=False, index=True)
  
    # Vendor details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization", 
        back_populates="vendors"
    )
    files: Mapped[List["app.models.customer_models.VendorFile"]] = relationship(
        "app.models.customer_models.VendorFile", 
        back_populates="vendor"
    )
  
    __table_args__ = (
        # Unique vendor name per organization
        UniqueConstraint('organization_id', 'name', name='uq_vendor_org_name'),
        Index('idx_vendor_org_name', 'organization_id', 'name'),
        Index('idx_vendor_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

class Customer(Base):
    __tablename__ = "customers"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_organization_id"), nullable=False, index=True)
  
    # Customer details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization", 
        back_populates="customers"
    )
    files: Mapped[List["app.models.customer_models.CustomerFile"]] = relationship(
        "app.models.customer_models.CustomerFile", 
        back_populates="customer"
    )
    interactions: Mapped[List["app.models.customer_models.CustomerInteraction"]] = relationship(
        "app.models.customer_models.CustomerInteraction", 
        back_populates="customer"
    )
    segments: Mapped[List["app.models.customer_models.CustomerSegment"]] = relationship(
        "app.models.customer_models.CustomerSegment", 
        back_populates="customer"
    )
  
    __table_args__ = (
        # Unique customer name per organization
        UniqueConstraint('organization_id', 'name', name='uq_customer_org_name'),
        Index('idx_customer_org_name', 'organization_id', 'name'),
        Index('idx_customer_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

class CustomerFile(Base):
    __tablename__ = "customer_files"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_file_organization_id"), nullable=False, index=True)
  
    # File details
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_customer_file_customer_id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general") # general, gst_certificate, pan_card, etc.
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    customer: Mapped["app.models.customer_models.Customer"] = relationship(
        "app.models.customer_models.Customer", 
        back_populates="files"
    )
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
  
    __table_args__ = (
        Index('idx_customer_file_org_customer', 'organization_id', 'customer_id'),
        {'extend_existing': True}
    )

class CustomerInteraction(Base):
    """
    Model for tracking customer interactions and communications.
    Supports multi-tenant architecture with organization-level isolation with organization-level isolation.
    """
    __tablename__ = "customer_interactions"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_interaction_organization_id"), nullable=False, index=True)
  
    # Customer reference
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_customer_interaction_customer_id"), nullable=False)
  
    # Interaction details
    interaction_type: Mapped[str] = mapped_column(String, nullable=False) # 'call', 'email', 'meeting', 'support_ticket', 'complaint', 'feedback'
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # 'pending', 'in_progress', 'completed', 'cancelled'
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
  
    # User who created this interaction record
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_customer_interaction_created_by"), nullable=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    customer: Mapped["app.models.customer_models.Customer"] = relationship(
        "app.models.customer_models.Customer", 
        back_populates="interactions"
    )
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    created_by_user: Mapped[Optional["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User"
    )
  
    __table_args__ = (
        Index('idx_customer_interaction_org_customer', 'organization_id', 'customer_id'),
        Index('idx_customer_interaction_type_status', 'interaction_type', 'status'),
        Index('idx_customer_interaction_date', 'interaction_date'),
        {'extend_existing': True}
    )

class CustomerSegment(Base):
    """
    Model for categorizing customers into segments for business and marketing purposes.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "customer_segments"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_customer_segment_organization_id"), nullable=False, index=True)
  
    # Customer reference
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id", name="fk_customer_segment_customer_id"), nullable=False)
  
    # Segment details
    segment_name: Mapped[str] = mapped_column(String, nullable=False) # 'vip', 'premium', 'regular', 'new', 'high_value', 'at_risk'
    segment_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Optional numeric value for the segment
    segment_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
  
    # User who assigned this segment
    assigned_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_customer_segment_assigned_by"), nullable=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    customer: Mapped["app.models.customer_models.Customer"] = relationship(
        "app.models.customer_models.Customer", 
        back_populates="segments"
    )
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    assigned_by_user: Mapped[Optional["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User"
    )
  
    __table_args__ = (
        Index('idx_customer_segment_org_customer', 'organization_id', 'customer_id'),
        Index('idx_customer_segment_name_active', 'segment_name', 'is_active'),
        Index('idx_customer_segment_assigned_date', 'assigned_date'),
        # Ensure a customer can only have one active segment of the same name per organization
        UniqueConstraint('organization_id', 'customer_id', 'segment_name', name='uq_customer_segment_org_customer_name'),
        {'extend_existing': True}
    )

class VendorFile(Base):
    __tablename__ = "vendor_files"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_vendor_file_organization_id"), nullable=False, index=True)
  
    # File details
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id", name="fk_vendor_file_vendor_id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general") # general, gst_certificate, pan_card, etc.
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    vendor: Mapped["app.models.customer_models.Vendor"] = relationship(
        "app.models.customer_models.Vendor", 
        back_populates="files"
    )
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
  
    __table_args__ = (
        Index('idx_vendor_file_org_vendor', 'organization_id', 'vendor_id'),
        {'extend_existing': True}
    )