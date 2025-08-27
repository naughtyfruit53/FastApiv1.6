# app/schemas/procurement.py
"""
Procurement Schemas - RFQ, Purchase Workflows, Vendor Management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class RFQStatusEnum(str, Enum):
    """RFQ Status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    RESPONDED = "responded"
    EVALUATED = "evaluated"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class VendorStatusEnum(str, Enum):
    """Vendor status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    UNDER_REVIEW = "under_review"


# RFQ Schemas
class RFQItemBase(BaseModel):
    item_code: str = Field(..., description="Item code")
    item_name: str = Field(..., description="Item name")
    item_description: Optional[str] = Field(None, description="Item description")
    quantity: Decimal = Field(..., description="Required quantity")
    unit: str = Field(..., description="Unit of measurement")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Item specifications")
    required_delivery_date: Optional[date] = Field(None, description="Required delivery date")
    delivery_location: Optional[str] = Field(None, description="Delivery location")


class RFQItemCreate(RFQItemBase):
    pass


class RFQItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    required_delivery_date: Optional[date] = None
    delivery_location: Optional[str] = None


class RFQItemResponse(RFQItemBase):
    id: int
    rfq_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RequestForQuotationBase(BaseModel):
    rfq_title: str = Field(..., description="RFQ title")
    rfq_description: Optional[str] = Field(None, description="RFQ description")
    issue_date: date = Field(..., description="Issue date")
    submission_deadline: date = Field(..., description="Submission deadline")
    validity_period: Optional[int] = Field(None, description="Validity period in days")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    delivery_requirements: Optional[str] = Field(None, description="Delivery requirements")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    is_public: bool = Field(False, description="Is public RFQ")
    requires_samples: bool = Field(False, description="Requires samples")
    allow_partial_quotes: bool = Field(True, description="Allow partial quotes")


class RequestForQuotationCreate(RequestForQuotationBase):
    rfq_items: List[RFQItemCreate] = Field(..., description="RFQ items")
    vendor_ids: List[int] = Field(..., description="Invited vendor IDs")


class RequestForQuotationUpdate(BaseModel):
    rfq_title: Optional[str] = None
    rfq_description: Optional[str] = None
    submission_deadline: Optional[date] = None
    validity_period: Optional[int] = None
    terms_and_conditions: Optional[str] = None
    delivery_requirements: Optional[str] = None
    payment_terms: Optional[str] = None
    is_public: Optional[bool] = None
    requires_samples: Optional[bool] = None
    allow_partial_quotes: Optional[bool] = None
    status: Optional[RFQStatusEnum] = None


class RequestForQuotationResponse(RequestForQuotationBase):
    id: int
    organization_id: int
    rfq_number: str
    status: RFQStatusEnum
    created_at: datetime
    updated_at: datetime
    rfq_items: List[RFQItemResponse] = []
    
    class Config:
        from_attributes = True


# Vendor RFQ Schemas
class VendorRFQBase(BaseModel):
    rfq_id: int = Field(..., description="RFQ ID")
    vendor_id: int = Field(..., description="Vendor ID")
    invited_date: date = Field(..., description="Invitation date")
    invitation_sent: bool = Field(False, description="Invitation sent")
    has_responded: bool = Field(False, description="Has responded")
    response_date: Optional[date] = Field(None, description="Response date")
    decline_reason: Optional[str] = Field(None, description="Decline reason")


class VendorRFQCreate(VendorRFQBase):
    pass


class VendorRFQUpdate(BaseModel):
    invitation_sent: Optional[bool] = None
    has_responded: Optional[bool] = None
    response_date: Optional[date] = None
    decline_reason: Optional[str] = None


class VendorRFQResponse(VendorRFQBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Quotation Schemas
class QuotationItemBase(BaseModel):
    rfq_item_id: int = Field(..., description="RFQ item ID")
    vendor_item_code: Optional[str] = Field(None, description="Vendor item code")
    vendor_item_name: Optional[str] = Field(None, description="Vendor item name")
    brand: Optional[str] = Field(None, description="Brand")
    model: Optional[str] = Field(None, description="Model")
    quoted_quantity: Decimal = Field(..., description="Quoted quantity")
    unit_price: Decimal = Field(..., description="Unit price")
    total_price: Decimal = Field(..., description="Total price")
    delivery_period: Optional[str] = Field(None, description="Delivery period")
    remarks: Optional[str] = Field(None, description="Remarks")
    meets_specifications: bool = Field(True, description="Meets specifications")
    deviation_notes: Optional[str] = Field(None, description="Deviation notes")


class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemUpdate(BaseModel):
    vendor_item_code: Optional[str] = None
    vendor_item_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    quoted_quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    delivery_period: Optional[str] = None
    remarks: Optional[str] = None
    meets_specifications: Optional[bool] = None
    deviation_notes: Optional[str] = None


class QuotationItemResponse(QuotationItemBase):
    id: int
    quotation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class VendorQuotationBase(BaseModel):
    rfq_id: int = Field(..., description="RFQ ID")
    vendor_id: int = Field(..., description="Vendor ID")
    quotation_date: date = Field(..., description="Quotation date")
    validity_date: date = Field(..., description="Validity date")
    total_amount: Decimal = Field(..., description="Total amount")
    tax_amount: Decimal = Field(0.00, description="Tax amount")
    grand_total: Decimal = Field(..., description="Grand total")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    delivery_terms: Optional[str] = Field(None, description="Delivery terms")
    warranty_terms: Optional[str] = Field(None, description="Warranty terms")
    notes: Optional[str] = Field(None, description="Notes")


class VendorQuotationCreate(VendorQuotationBase):
    quotation_items: List[QuotationItemCreate] = Field(..., description="Quotation items")


class VendorQuotationUpdate(BaseModel):
    quotation_date: Optional[date] = None
    validity_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    notes: Optional[str] = None
    is_selected: Optional[bool] = None
    selection_rank: Optional[int] = None
    technical_score: Optional[Decimal] = None
    commercial_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    evaluation_notes: Optional[str] = None


class VendorQuotationResponse(VendorQuotationBase):
    id: int
    organization_id: int
    quotation_number: str
    is_selected: bool
    selection_rank: Optional[int]
    technical_score: Optional[Decimal]
    commercial_score: Optional[Decimal]
    overall_score: Optional[Decimal]
    evaluation_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    quotation_items: List[QuotationItemResponse] = []
    
    class Config:
        from_attributes = True


# Vendor Evaluation Schemas
class VendorEvaluationBase(BaseModel):
    vendor_id: int = Field(..., description="Vendor ID")
    evaluation_date: date = Field(..., description="Evaluation date")
    evaluation_type: str = Field(..., description="Evaluation type")
    quality_rating: Optional[Decimal] = Field(None, description="Quality rating (out of 10)")
    delivery_rating: Optional[Decimal] = Field(None, description="Delivery rating (out of 10)")
    service_rating: Optional[Decimal] = Field(None, description="Service rating (out of 10)")
    price_rating: Optional[Decimal] = Field(None, description="Price rating (out of 10)")
    communication_rating: Optional[Decimal] = Field(None, description="Communication rating (out of 10)")
    overall_rating: Decimal = Field(..., description="Overall rating (out of 10)")
    strengths: Optional[str] = Field(None, description="Strengths")
    weaknesses: Optional[str] = Field(None, description="Weaknesses")
    improvement_suggestions: Optional[str] = Field(None, description="Improvement suggestions")
    on_time_delivery_percentage: Optional[Decimal] = Field(None, description="On-time delivery percentage")
    quality_rejection_percentage: Optional[Decimal] = Field(None, description="Quality rejection percentage")
    vendor_status: VendorStatusEnum = Field(VendorStatusEnum.ACTIVE, description="Vendor status")
    notes: Optional[str] = Field(None, description="Notes")


class VendorEvaluationCreate(VendorEvaluationBase):
    pass


class VendorEvaluationUpdate(BaseModel):
    evaluation_type: Optional[str] = None
    quality_rating: Optional[Decimal] = None
    delivery_rating: Optional[Decimal] = None
    service_rating: Optional[Decimal] = None
    price_rating: Optional[Decimal] = None
    communication_rating: Optional[Decimal] = None
    overall_rating: Optional[Decimal] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    on_time_delivery_percentage: Optional[Decimal] = None
    quality_rejection_percentage: Optional[Decimal] = None
    vendor_status: Optional[VendorStatusEnum] = None
    notes: Optional[str] = None


class VendorEvaluationResponse(VendorEvaluationBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Purchase Requisition Schemas
class PurchaseRequisitionItemBase(BaseModel):
    item_code: str = Field(..., description="Item code")
    item_name: str = Field(..., description="Item name")
    item_description: Optional[str] = Field(None, description="Item description")
    required_quantity: Decimal = Field(..., description="Required quantity")
    unit: str = Field(..., description="Unit of measurement")
    estimated_unit_price: Optional[Decimal] = Field(None, description="Estimated unit price")
    estimated_total_price: Optional[Decimal] = Field(None, description="Estimated total price")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Specifications")
    preferred_vendor: Optional[str] = Field(None, description="Preferred vendor")


class PurchaseRequisitionItemCreate(PurchaseRequisitionItemBase):
    pass


class PurchaseRequisitionItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_description: Optional[str] = None
    required_quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    estimated_unit_price: Optional[Decimal] = None
    estimated_total_price: Optional[Decimal] = None
    specifications: Optional[Dict[str, Any]] = None
    preferred_vendor: Optional[str] = None


class PurchaseRequisitionItemResponse(PurchaseRequisitionItemBase):
    id: int
    requisition_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseRequisitionBase(BaseModel):
    requisition_date: date = Field(..., description="Requisition date")
    required_date: date = Field(..., description="Required date")
    department: Optional[str] = Field(None, description="Department")
    cost_center: Optional[str] = Field(None, description="Cost center")
    project_code: Optional[str] = Field(None, description="Project code")
    purpose: str = Field(..., description="Purpose")
    justification: Optional[str] = Field(None, description="Justification")
    estimated_budget: Optional[Decimal] = Field(None, description="Estimated budget")


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    requisition_items: List[PurchaseRequisitionItemCreate] = Field(..., description="Requisition items")


class PurchaseRequisitionUpdate(BaseModel):
    required_date: Optional[date] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    purpose: Optional[str] = None
    justification: Optional[str] = None
    estimated_budget: Optional[Decimal] = None
    approval_status: Optional[str] = None
    rejection_reason: Optional[str] = None


class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    id: int
    organization_id: int
    requisition_number: str
    approval_status: str
    approved_date: Optional[date]
    rejection_reason: Optional[str]
    purchase_order_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    requisition_items: List[PurchaseRequisitionItemResponse] = []
    
    class Config:
        from_attributes = True


# Procurement Analytics Schemas
class RFQAnalytics(BaseModel):
    total_rfqs: int
    active_rfqs: int
    completed_rfqs: int
    cancelled_rfqs: int
    average_response_time_days: Optional[float]
    vendor_participation_rate: Optional[float]


class VendorPerformanceMetrics(BaseModel):
    vendor_id: int
    vendor_name: str
    total_quotations: int
    selected_quotations: int
    selection_rate: Optional[float]
    average_overall_rating: Optional[Decimal]
    on_time_delivery_rate: Optional[Decimal]
    quality_rating: Optional[Decimal]


class ProcurementDashboard(BaseModel):
    rfq_analytics: RFQAnalytics
    top_vendors: List[VendorPerformanceMetrics]
    pending_approvals: int
    total_purchase_value: Decimal
    organization_id: int
    as_of_date: date