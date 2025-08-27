# app/models/procurement_models.py
"""
Procurement Models - RFQ, Purchase Workflows, Vendor Management
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class RFQStatus(enum.Enum):
    """RFQ Status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    RESPONDED = "responded"
    EVALUATED = "evaluated"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class VendorStatus(enum.Enum):
    """Vendor status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    UNDER_REVIEW = "under_review"


class RequestForQuotation(Base):
    """Request for Quotation model"""
    __tablename__ = "request_for_quotations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # RFQ identification
    rfq_number = Column(String(50), nullable=False, unique=True, index=True)
    rfq_title = Column(String(200), nullable=False)
    rfq_description = Column(Text, nullable=True)
    
    # Dates
    issue_date = Column(Date, nullable=False, index=True)
    submission_deadline = Column(Date, nullable=False, index=True)
    validity_period = Column(Integer, nullable=True)  # Days
    
    # Requirements
    terms_and_conditions = Column(Text, nullable=True)
    delivery_requirements = Column(Text, nullable=True)
    payment_terms = Column(String(100), nullable=True)
    
    # Status and workflow
    status = Column(Enum(RFQStatus), default=RFQStatus.DRAFT, nullable=False, index=True)
    
    # Configuration
    is_public = Column(Boolean, default=False, nullable=False)
    requires_samples = Column(Boolean, default=False, nullable=False)
    allow_partial_quotes = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="rfqs")
    rfq_items = relationship("RFQItem", back_populates="rfq", cascade="all, delete-orphan")
    vendor_rfqs = relationship("VendorRFQ", back_populates="rfq", cascade="all, delete-orphan")
    quotations = relationship("VendorQuotation", back_populates="rfq")
    
    # Constraints
    __table_args__ = (
        Index('idx_rfq_org_status', 'organization_id', 'status'),
        Index('idx_rfq_deadline', 'submission_deadline'),
    )


class RFQItem(Base):
    """RFQ Item details"""
    __tablename__ = "rfq_items"

    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("request_for_quotations.id"), nullable=False, index=True)
    
    # Item details
    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    
    # Specifications
    quantity = Column(Numeric(12, 3), nullable=False)
    unit = Column(String(20), nullable=False)
    specifications = Column(JSON, nullable=True)
    
    # Delivery
    required_delivery_date = Column(Date, nullable=True)
    delivery_location = Column(String(200), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    rfq = relationship("RequestForQuotation", back_populates="rfq_items")
    quotation_items = relationship("QuotationItem", back_populates="rfq_item")


class VendorRFQ(Base):
    """Vendor-RFQ mapping for invitation"""
    __tablename__ = "vendor_rfqs"

    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("request_for_quotations.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Invitation details
    invited_date = Column(Date, nullable=False, index=True)
    invitation_sent = Column(Boolean, default=False, nullable=False)
    
    # Response tracking
    has_responded = Column(Boolean, default=False, nullable=False)
    response_date = Column(Date, nullable=True)
    decline_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    rfq = relationship("RequestForQuotation", back_populates="vendor_rfqs")
    vendor = relationship("Vendor", back_populates="vendor_rfqs")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('rfq_id', 'vendor_id', name='uq_rfq_vendor'),
        Index('idx_vendor_rfq_response', 'has_responded'),
    )


class VendorQuotation(Base):
    """Vendor quotations in response to RFQ"""
    __tablename__ = "vendor_quotations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    rfq_id = Column(Integer, ForeignKey("request_for_quotations.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Quotation details
    quotation_number = Column(String(50), nullable=False, index=True)
    quotation_date = Column(Date, nullable=False, index=True)
    validity_date = Column(Date, nullable=False)
    
    # Financial summary
    total_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    grand_total = Column(Numeric(15, 2), nullable=False)
    
    # Terms
    payment_terms = Column(String(100), nullable=True)
    delivery_terms = Column(String(100), nullable=True)
    warranty_terms = Column(Text, nullable=True)
    
    # Status
    is_selected = Column(Boolean, default=False, nullable=False)
    selection_rank = Column(Integer, nullable=True)
    
    # Evaluation
    technical_score = Column(Numeric(5, 2), nullable=True)  # Out of 100
    commercial_score = Column(Numeric(5, 2), nullable=True)  # Out of 100
    overall_score = Column(Numeric(5, 2), nullable=True)  # Out of 100
    evaluation_notes = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="vendor_quotations")
    rfq = relationship("RequestForQuotation", back_populates="quotations")
    vendor = relationship("Vendor", back_populates="quotations")
    quotation_items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'quotation_number', name='uq_org_quotation_number'),
        Index('idx_quotation_rfq_vendor', 'rfq_id', 'vendor_id'),
        Index('idx_quotation_selected', 'is_selected'),
    )


class QuotationItem(Base):
    """Quotation item details"""
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("vendor_quotations.id"), nullable=False, index=True)
    rfq_item_id = Column(Integer, ForeignKey("rfq_items.id"), nullable=False, index=True)
    
    # Item details from vendor
    vendor_item_code = Column(String(100), nullable=True)
    vendor_item_name = Column(String(200), nullable=True)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Quantity and pricing
    quoted_quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Additional details
    delivery_period = Column(String(50), nullable=True)  # e.g., "15 days"
    remarks = Column(Text, nullable=True)
    
    # Technical compliance
    meets_specifications = Column(Boolean, default=True, nullable=False)
    deviation_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    quotation = relationship("VendorQuotation", back_populates="quotation_items")
    rfq_item = relationship("RFQItem", back_populates="quotation_items")


class VendorEvaluation(Base):
    """Vendor evaluation and rating"""
    __tablename__ = "vendor_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Evaluation details
    evaluation_date = Column(Date, nullable=False, index=True)
    evaluation_type = Column(String(50), nullable=False)  # Annual, Project-based, etc.
    
    # Ratings (out of 10)
    quality_rating = Column(Numeric(3, 1), nullable=True)
    delivery_rating = Column(Numeric(3, 1), nullable=True)
    service_rating = Column(Numeric(3, 1), nullable=True)
    price_rating = Column(Numeric(3, 1), nullable=True)
    communication_rating = Column(Numeric(3, 1), nullable=True)
    
    # Overall
    overall_rating = Column(Numeric(3, 1), nullable=False)
    
    # Feedback
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    
    # Performance metrics
    on_time_delivery_percentage = Column(Numeric(5, 2), nullable=True)
    quality_rejection_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Status
    vendor_status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE, nullable=False)
    
    # Metadata
    evaluated_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="vendor_evaluations")
    vendor = relationship("Vendor", back_populates="evaluations")
    
    # Constraints
    __table_args__ = (
        Index('idx_vendor_eval_org_date', 'organization_id', 'evaluation_date'),
        Index('idx_vendor_eval_rating', 'overall_rating'),
    )


class PurchaseRequisition(Base):
    """Purchase requisition for internal approval workflow"""
    __tablename__ = "purchase_requisitions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Requisition details
    requisition_number = Column(String(50), nullable=False, unique=True, index=True)
    requisition_date = Column(Date, nullable=False, index=True)
    required_date = Column(Date, nullable=False, index=True)
    
    # Requesting details
    department = Column(String(100), nullable=True)
    cost_center = Column(String(100), nullable=True)
    project_code = Column(String(100), nullable=True)
    
    # Justification
    purpose = Column(Text, nullable=False)
    justification = Column(Text, nullable=True)
    
    # Financial
    estimated_budget = Column(Numeric(15, 2), nullable=True)
    
    # Approval workflow
    approval_status = Column(String(20), default="pending", nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Purchase order reference
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)
    
    # Metadata
    requested_by = Column(Integer, ForeignKey("platform_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="purchase_requisitions")
    requisition_items = relationship("PurchaseRequisitionItem", back_populates="requisition", cascade="all, delete-orphan")
    purchase_order = relationship("PurchaseOrder", back_populates="purchase_requisition")
    
    # Constraints
    __table_args__ = (
        Index('idx_pr_org_status', 'organization_id', 'approval_status'),
        Index('idx_pr_required_date', 'required_date'),
    )


class PurchaseRequisitionItem(Base):
    """Purchase requisition item details"""
    __tablename__ = "purchase_requisition_items"

    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("purchase_requisitions.id"), nullable=False, index=True)
    
    # Item details
    item_code = Column(String(100), nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    
    # Quantity
    required_quantity = Column(Numeric(12, 3), nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Pricing
    estimated_unit_price = Column(Numeric(15, 2), nullable=True)
    estimated_total_price = Column(Numeric(15, 2), nullable=True)
    
    # Specifications
    specifications = Column(JSON, nullable=True)
    preferred_vendor = Column(String(200), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    requisition = relationship("PurchaseRequisition", back_populates="requisition_items")