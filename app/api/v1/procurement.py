# app/api/v1/procurement.py
"""
Procurement API endpoints - RFQ, Purchase Workflows, Vendor Management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin, validate_company_setup_for_operations
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import (
    User, Organization, Vendor,
    RequestForQuotation, RFQItem, VendorRFQ, VendorQuotation, QuotationItem,
    VendorEvaluation, PurchaseRequisition, PurchaseRequisitionItem
)
from app.schemas.procurement import (
    RequestForQuotationCreate, RequestForQuotationUpdate, RequestForQuotationResponse,
    RFQItemCreate, RFQItemUpdate, RFQItemResponse,
    VendorRFQCreate, VendorRFQUpdate, VendorRFQResponse,
    VendorQuotationCreate, VendorQuotationUpdate, VendorQuotationResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    VendorEvaluationCreate, VendorEvaluationUpdate, VendorEvaluationResponse,
    PurchaseRequisitionCreate, PurchaseRequisitionUpdate, PurchaseRequisitionResponse,
    PurchaseRequisitionItemCreate, PurchaseRequisitionItemUpdate, PurchaseRequisitionItemResponse,
    RFQAnalytics, VendorPerformanceMetrics, ProcurementDashboard
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ProcurementService:
    """Service class for procurement operations"""
    
    @staticmethod
    def generate_rfq_number(db: Session, organization_id: int) -> str:
        """Generate next RFQ number"""
        current_year = datetime.now().year
        prefix = f"RFQ-{current_year}-"
        
        # Get the highest existing RFQ number for this year
        last_rfq = db.query(RequestForQuotation).filter(
            RequestForQuotation.organization_id == organization_id,
            RequestForQuotation.rfq_number.like(f"{prefix}%")
        ).order_by(desc(RequestForQuotation.rfq_number)).first()
        
        if last_rfq:
            try:
                last_num = int(last_rfq.rfq_number.split('-')[-1])
                return f"{prefix}{str(last_num + 1).zfill(4)}"
            except (ValueError, IndexError):
                pass
        
        return f"{prefix}0001"
    
    @staticmethod
    def generate_quotation_number(db: Session, organization_id: int) -> str:
        """Generate next quotation number"""
        current_year = datetime.now().year
        prefix = f"QT-{current_year}-"
        
        last_quotation = db.query(VendorQuotation).filter(
            VendorQuotation.organization_id == organization_id,
            VendorQuotation.quotation_number.like(f"{prefix}%")
        ).order_by(desc(VendorQuotation.quotation_number)).first()
        
        if last_quotation:
            try:
                last_num = int(last_quotation.quotation_number.split('-')[-1])
                return f"{prefix}{str(last_num + 1).zfill(4)}"
            except (ValueError, IndexError):
                pass
        
        return f"{prefix}0001"


# RFQ Endpoints
@router.get("/rfqs", response_model=List[RequestForQuotationResponse])
async def get_rfqs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get RFQs with filtering options"""
    query = db.query(RequestForQuotation).filter(
        RequestForQuotation.organization_id == organization_id
    ).options(joinedload(RequestForQuotation.rfq_items))
    
    if status:
        query = query.filter(RequestForQuotation.status == status)
    
    if search:
        query = query.filter(or_(
            RequestForQuotation.rfq_title.ilike(f"%{search}%"),
            RequestForQuotation.rfq_number.ilike(f"%{search}%")
        ))
    
    query = query.order_by(desc(RequestForQuotation.created_at))
    rfqs = query.offset(skip).limit(limit).all()
    return rfqs


@router.post("/rfqs", response_model=RequestForQuotationResponse)
async def create_rfq(
    rfq_data: RequestForQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new RFQ"""
    # Generate RFQ number
    rfq_number = ProcurementService.generate_rfq_number(db, organization_id)
    
    # Create RFQ
    rfq = RequestForQuotation(
        organization_id=organization_id,
        rfq_number=rfq_number,
        rfq_title=rfq_data.rfq_title,
        rfq_description=rfq_data.rfq_description,
        issue_date=rfq_data.issue_date,
        submission_deadline=rfq_data.submission_deadline,
        validity_period=rfq_data.validity_period,
        terms_and_conditions=rfq_data.terms_and_conditions,
        delivery_requirements=rfq_data.delivery_requirements,
        payment_terms=rfq_data.payment_terms,
        is_public=rfq_data.is_public,
        requires_samples=rfq_data.requires_samples,
        allow_partial_quotes=rfq_data.allow_partial_quotes,
        created_by=current_user.id
    )
    
    db.add(rfq)
    db.flush()  # To get the RFQ ID
    
    # Create RFQ items
    for item_data in rfq_data.rfq_items:
        rfq_item = RFQItem(
            rfq_id=rfq.id,
            item_code=item_data.item_code,
            item_name=item_data.item_name,
            item_description=item_data.item_description,
            quantity=item_data.quantity,
            unit=item_data.unit,
            specifications=item_data.specifications,
            required_delivery_date=item_data.required_delivery_date,
            delivery_location=item_data.delivery_location
        )
        db.add(rfq_item)
    
    # Invite vendors
    for vendor_id in rfq_data.vendor_ids:
        vendor_rfq = VendorRFQ(
            rfq_id=rfq.id,
            vendor_id=vendor_id,
            invited_date=datetime.now().date()
        )
        db.add(vendor_rfq)
    
    db.commit()
    db.refresh(rfq)
    
    return rfq


@router.get("/rfqs/{rfq_id}", response_model=RequestForQuotationResponse)
async def get_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific RFQ"""
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.organization_id == organization_id
    ).options(joinedload(RequestForQuotation.rfq_items)).first()
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    
    return rfq


@router.put("/rfqs/{rfq_id}", response_model=RequestForQuotationResponse)
async def update_rfq(
    rfq_id: int,
    rfq_data: RequestForQuotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update an RFQ"""
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.organization_id == organization_id
    ).first()
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    
    # Check if RFQ can be updated
    if rfq.status in ['AWARDED', 'CANCELLED']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update RFQ in current status"
        )
    
    update_data = rfq_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(rfq, field, value)
    
    rfq.updated_by = current_user.id
    rfq.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rfq)
    
    return rfq


# Vendor Quotation Endpoints
@router.get("/quotations", response_model=List[VendorQuotationResponse])
async def get_quotations(
    skip: int = 0,
    limit: int = 100,
    rfq_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    is_selected: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get vendor quotations with filtering options"""
    query = db.query(VendorQuotation).filter(
        VendorQuotation.organization_id == organization_id
    ).options(joinedload(VendorQuotation.quotation_items))
    
    if rfq_id:
        query = query.filter(VendorQuotation.rfq_id == rfq_id)
    
    if vendor_id:
        query = query.filter(VendorQuotation.vendor_id == vendor_id)
    
    if is_selected is not None:
        query = query.filter(VendorQuotation.is_selected == is_selected)
    
    query = query.order_by(desc(VendorQuotation.created_at))
    quotations = query.offset(skip).limit(limit).all()
    return quotations


@router.post("/quotations", response_model=VendorQuotationResponse)
async def create_quotation(
    quotation_data: VendorQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new vendor quotation"""
    # Verify RFQ exists and is open for responses
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == quotation_data.rfq_id,
        RequestForQuotation.organization_id == organization_id
    ).first()
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    
    if rfq.status not in ['SENT', 'RESPONDED']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RFQ is not open for responses"
        )
    
    # Generate quotation number
    quotation_number = ProcurementService.generate_quotation_number(db, organization_id)
    
    # Create quotation
    quotation = VendorQuotation(
        organization_id=organization_id,
        quotation_number=quotation_number,
        rfq_id=quotation_data.rfq_id,
        vendor_id=quotation_data.vendor_id,
        quotation_date=quotation_data.quotation_date,
        validity_date=quotation_data.validity_date,
        total_amount=quotation_data.total_amount,
        tax_amount=quotation_data.tax_amount,
        grand_total=quotation_data.grand_total,
        payment_terms=quotation_data.payment_terms,
        delivery_terms=quotation_data.delivery_terms,
        warranty_terms=quotation_data.warranty_terms,
        notes=quotation_data.notes
    )
    
    db.add(quotation)
    db.flush()
    
    # Create quotation items
    for item_data in quotation_data.quotation_items:
        quotation_item = QuotationItem(
            quotation_id=quotation.id,
            rfq_item_id=item_data.rfq_item_id,
            vendor_item_code=item_data.vendor_item_code,
            vendor_item_name=item_data.vendor_item_name,
            brand=item_data.brand,
            model=item_data.model,
            quoted_quantity=item_data.quoted_quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.total_price,
            delivery_period=item_data.delivery_period,
            remarks=item_data.remarks,
            meets_specifications=item_data.meets_specifications,
            deviation_notes=item_data.deviation_notes
        )
        db.add(quotation_item)
    
    # Update vendor RFQ response status
    vendor_rfq = db.query(VendorRFQ).filter(
        VendorRFQ.rfq_id == quotation_data.rfq_id,
        VendorRFQ.vendor_id == quotation_data.vendor_id
    ).first()
    
    if vendor_rfq:
        vendor_rfq.has_responded = True
        vendor_rfq.response_date = datetime.now().date()
    
    # Update RFQ status if this is the first response
    if rfq.status == 'SENT':
        rfq.status = 'RESPONDED'
    
    db.commit()
    db.refresh(quotation)
    
    return quotation


# Vendor Evaluation Endpoints
@router.get("/vendor-evaluations", response_model=List[VendorEvaluationResponse])
async def get_vendor_evaluations(
    skip: int = 0,
    limit: int = 100,
    vendor_id: Optional[int] = None,
    evaluation_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get vendor evaluations with filtering options"""
    query = db.query(VendorEvaluation).filter(
        VendorEvaluation.organization_id == organization_id
    )
    
    if vendor_id:
        query = query.filter(VendorEvaluation.vendor_id == vendor_id)
    
    if evaluation_type:
        query = query.filter(VendorEvaluation.evaluation_type == evaluation_type)
    
    query = query.order_by(desc(VendorEvaluation.evaluation_date))
    evaluations = query.offset(skip).limit(limit).all()
    return evaluations


@router.post("/vendor-evaluations", response_model=VendorEvaluationResponse)
async def create_vendor_evaluation(
    evaluation_data: VendorEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new vendor evaluation"""
    evaluation = VendorEvaluation(
        organization_id=organization_id,
        evaluated_by=current_user.id,
        **evaluation_data.dict()
    )
    
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return evaluation


# Purchase Requisition Endpoints
@router.get("/purchase-requisitions", response_model=List[PurchaseRequisitionResponse])
async def get_purchase_requisitions(
    skip: int = 0,
    limit: int = 100,
    approval_status: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get purchase requisitions with filtering options"""
    query = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.organization_id == organization_id
    ).options(joinedload(PurchaseRequisition.requisition_items))
    
    if approval_status:
        query = query.filter(PurchaseRequisition.approval_status == approval_status)
    
    if department:
        query = query.filter(PurchaseRequisition.department == department)
    
    query = query.order_by(desc(PurchaseRequisition.created_at))
    requisitions = query.offset(skip).limit(limit).all()
    return requisitions


# Analytics Endpoints
@router.get("/analytics/dashboard", response_model=ProcurementDashboard)
async def get_procurement_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get procurement dashboard analytics"""
    # RFQ Analytics
    total_rfqs = db.query(RequestForQuotation).filter(
        RequestForQuotation.organization_id == organization_id
    ).count()
    
    active_rfqs = db.query(RequestForQuotation).filter(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status.in_(['SENT', 'RESPONDED'])
    ).count()
    
    completed_rfqs = db.query(RequestForQuotation).filter(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status == 'AWARDED'
    ).count()
    
    cancelled_rfqs = db.query(RequestForQuotation).filter(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status == 'CANCELLED'
    ).count()
    
    rfq_analytics = RFQAnalytics(
        total_rfqs=total_rfqs,
        active_rfqs=active_rfqs,
        completed_rfqs=completed_rfqs,
        cancelled_rfqs=cancelled_rfqs
    )
    
    # Vendor Performance Metrics
    vendor_performance = db.query(
        VendorEvaluation.vendor_id,
        func.count(VendorQuotation.id).label('total_quotations'),
        func.count(func.nullif(VendorQuotation.is_selected, False)).label('selected_quotations'),
        func.avg(VendorEvaluation.overall_rating).label('avg_rating')
    ).join(
        VendorQuotation, VendorEvaluation.vendor_id == VendorQuotation.vendor_id
    ).filter(
        VendorEvaluation.organization_id == organization_id
    ).group_by(VendorEvaluation.vendor_id).limit(10).all()
    
    top_vendors = []
    for perf in vendor_performance:
        vendor = db.query(Vendor).filter(Vendor.id == perf.vendor_id).first()
        if vendor:
            selection_rate = (perf.selected_quotations / perf.total_quotations * 100) if perf.total_quotations > 0 else 0
            top_vendors.append(VendorPerformanceMetrics(
                vendor_id=perf.vendor_id,
                vendor_name=vendor.name,
                total_quotations=perf.total_quotations,
                selected_quotations=perf.selected_quotations,
                selection_rate=selection_rate,
                average_overall_rating=perf.avg_rating
            ))
    
    # Pending approvals
    pending_approvals = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.organization_id == organization_id,
        PurchaseRequisition.approval_status == 'pending'
    ).count()
    
    # Total purchase value (simplified calculation)
    total_purchase_value = db.query(func.sum(VendorQuotation.grand_total)).filter(
        VendorQuotation.organization_id == organization_id,
        VendorQuotation.is_selected == True
    ).scalar() or Decimal(0)
    
    return ProcurementDashboard(
        rfq_analytics=rfq_analytics,
        top_vendors=top_vendors,
        pending_approvals=pending_approvals,
        total_purchase_value=total_purchase_value,
        organization_id=organization_id,
        as_of_date=datetime.now().date()
    )