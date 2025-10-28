# app/api/v1/procurement.py
"""
Procurement API endpoints - RFQ, Purchase Workflows, Vendor Management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
from app.core.tenant import TenantQueryMixin
from app.core.org_restrictions import validate_company_setup
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
    async def generate_rfq_number(db: AsyncSession, organization_id: int) -> str:
        """Generate next RFQ number"""
        current_year = datetime.now().year
        prefix = f"RFQ-{current_year}-"
        
        # Get the highest existing RFQ number for this year
        stmt = select(RequestForQuotation).where(
            RequestForQuotation.organization_id == organization_id,
            RequestForQuotation.rfq_number.like(f"{prefix}%")
        ).order_by(desc(RequestForQuotation.rfq_number))
        result = await db.execute(stmt)
        last_rfq = result.scalar_one_or_none()
        
        if last_rfq:
            try:
                last_num = int(last_rfq.rfq_number.split('-')[-1])
                return f"{prefix}{str(last_num + 1).zfill(4)}"
            except (ValueError, IndexError):
                pass
        
        return f"{prefix}0001"
    
    @staticmethod
    async def generate_quotation_number(db: AsyncSession, organization_id: int) -> str:
        """Generate next quotation number"""
        current_year = datetime.now().year
        prefix = f"QT-{current_year}-"
        
        stmt = select(VendorQuotation).where(
            VendorQuotation.organization_id == organization_id,
            VendorQuotation.quotation_number.like(f"{prefix}%")
        ).order_by(desc(VendorQuotation.quotation_number))
        result = await db.execute(stmt)
        last_quotation = result.scalar_one_or_none()
        
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get RFQs with filtering options"""
    stmt = select(RequestForQuotation).where(
        RequestForQuotation.organization_id == organization_id
    ).options(joinedload(RequestForQuotation.rfq_items))
    
    if status:
        stmt = stmt.where(RequestForQuotation.status == status)
    
    if search:
        stmt = stmt.where(or_(
            RequestForQuotation.rfq_title.ilike(f"%{search}%"),
            RequestForQuotation.rfq_number.ilike(f"%{search}%")
        ))
    
    stmt = stmt.order_by(desc(RequestForQuotation.created_at))
    result = await db.execute(stmt.offset(skip).limit(limit))
    rfqs = result.scalars().all()
    return rfqs


@router.post("/rfqs", response_model=RequestForQuotationResponse)
async def create_rfq(
    rfq_data: RequestForQuotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new RFQ"""
    # Generate RFQ number
    rfq_number = await ProcurementService.generate_rfq_number(db, organization_id)
    
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
    await db.flush()  # To get the RFQ ID
    
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
    
    await db.commit()
    await db.refresh(rfq)
    
    return rfq


@router.get("/rfqs/{rfq_id}", response_model=RequestForQuotationResponse)
async def get_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific RFQ"""
    stmt = select(RequestForQuotation).where(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.organization_id == organization_id
    ).options(joinedload(RequestForQuotation.rfq_items))
    result = await db.execute(stmt)
    rfq = result.scalar_one_or_none()
    
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update an RFQ"""
    stmt = select(RequestForQuotation).where(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.organization_id == organization_id
    )
    result = await db.execute(stmt)
    rfq = result.scalar_one_or_none()
    
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
    
    await db.commit()
    await db.refresh(rfq)
    
    return rfq


# Vendor Quotation Endpoints
@router.get("/quotations", response_model=List[VendorQuotationResponse])
async def get_quotations(
    skip: int = 0,
    limit: int = 100,
    rfq_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    is_selected: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get vendor quotations with filtering options"""
    stmt = select(VendorQuotation).where(
        VendorQuotation.organization_id == organization_id
    ).options(joinedload(VendorQuotation.quotation_items))
    
    if rfq_id:
        stmt = stmt.where(VendorQuotation.rfq_id == rfq_id)
    
    if vendor_id:
        stmt = stmt.where(VendorQuotation.vendor_id == vendor_id)
    
    if is_selected is not None:
        stmt = stmt.where(VendorQuotation.is_selected == is_selected)
    
    stmt = stmt.order_by(desc(VendorQuotation.created_at))
    result = await db.execute(stmt.offset(skip).limit(limit))
    quotations = result.scalars().all()
    return quotations


@router.post("/quotations", response_model=VendorQuotationResponse)
async def create_quotation(
    quotation_data: VendorQuotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new vendor quotation"""
    # Verify RFQ exists and is open for responses
    stmt = select(RequestForQuotation).where(
        RequestForQuotation.id == quotation_data.rfq_id,
        RequestForQuotation.organization_id == organization_id
    )
    result = await db.execute(stmt)
    rfq = result.scalar_one_or_none()
    
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
    quotation_number = await ProcurementService.generate_quotation_number(db, organization_id)
    
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
    await db.flush()
    
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
    stmt = select(VendorRFQ).where(
        VendorRFQ.rfq_id == quotation_data.rfq_id,
        VendorRFQ.vendor_id == quotation_data.vendor_id
    )
    result = await db.execute(stmt)
    vendor_rfq = result.scalar_one_or_none()
    
    if vendor_rfq:
        vendor_rfq.has_responded = True
        vendor_rfq.response_date = datetime.now().date()
    
    # Update RFQ status if this is the first response
    if rfq.status == 'SENT':
        rfq.status = 'RESPONDED'
    
    await db.commit()
    await db.refresh(quotation)
    
    return quotation


# Vendor Evaluation Endpoints
@router.get("/vendor-evaluations", response_model=List[VendorEvaluationResponse])
async def get_vendor_evaluations(
    skip: int = 0,
    limit: int = 100,
    vendor_id: Optional[int] = None,
    evaluation_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get vendor evaluations with filtering options"""
    stmt = select(VendorEvaluation).where(
        VendorEvaluation.organization_id == organization_id
    )
    
    if vendor_id:
        stmt = stmt.where(VendorEvaluation.vendor_id == vendor_id)
    
    if evaluation_type:
        stmt = stmt.where(VendorEvaluation.evaluation_type == evaluation_type)
    
    stmt = stmt.order_by(desc(VendorEvaluation.evaluation_date))
    result = await db.execute(stmt.offset(skip).limit(limit))
    evaluations = result.scalars().all()
    return evaluations


@router.post("/vendor-evaluations", response_model=VendorEvaluationResponse)
async def create_vendor_evaluation(
    evaluation_data: VendorEvaluationCreate,
    db: AsyncSession = Depends(get_db),
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
    await db.commit()
    await db.refresh(evaluation)
    
    return evaluation


# Purchase Requisition Endpoints
@router.get("/purchase-requisitions", response_model=List[PurchaseRequisitionResponse])
async def get_purchase_requisitions(
    skip: int = 0,
    limit: int = 100,
    approval_status: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get purchase requisitions with filtering options"""
    stmt = select(PurchaseRequisition).where(
        PurchaseRequisition.organization_id == organization_id
    ).options(joinedload(PurchaseRequisition.requisition_items))
    
    if approval_status:
        stmt = stmt.where(PurchaseRequisition.approval_status == approval_status)
    
    if department:
        stmt = stmt.where(PurchaseRequisition.department == department)
    
    stmt = stmt.order_by(desc(PurchaseRequisition.created_at))
    result = await db.execute(stmt.offset(skip).limit(limit))
    requisitions = result.scalars().all()
    return requisitions


# Analytics Endpoints
@router.get("/analytics/dashboard", response_model=ProcurementDashboard)
async def get_procurement_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get procurement dashboard analytics"""
    # RFQ Analytics
    stmt_total = select(func.count(RequestForQuotation.id)).where(
        RequestForQuotation.organization_id == organization_id
    )
    result_total = await db.execute(stmt_total)
    total_rfqs = result_total.scalar()
    
    stmt_active = select(func.count(RequestForQuotation.id)).where(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status.in_(['SENT', 'RESPONDED'])
    )
    result_active = await db.execute(stmt_active)
    active_rfqs = result_active.scalar()
    
    stmt_completed = select(func.count(RequestForQuotation.id)).where(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status == 'AWARDED'
    )
    result_completed = await db.execute(stmt_completed)
    completed_rfqs = result_completed.scalar()
    
    stmt_cancelled = select(func.count(RequestForQuotation.id)).where(
        RequestForQuotation.organization_id == organization_id,
        RequestForQuotation.status == 'CANCELLED'
    )
    result_cancelled = await db.execute(stmt_cancelled)
    cancelled_rfqs = result_cancelled.scalar()
    
    rfq_analytics = RFQAnalytics(
        total_rfqs=total_rfqs,
        active_rfqs=active_rfqs,
        completed_rfqs=completed_rfqs,
        cancelled_rfqs=cancelled_rfqs
    )
    
    # Vendor Performance Metrics
    stmt_performance = select(
        VendorEvaluation.vendor_id,
        func.count(VendorQuotation.id).label('total_quotations'),
        func.count(func.nullif(VendorQuotation.is_selected, False)).label('selected_quotations'),
        func.avg(VendorEvaluation.overall_rating).label('avg_rating')
    ).join(
        VendorQuotation, VendorEvaluation.vendor_id == VendorQuotation.vendor_id
    ).where(
        VendorEvaluation.organization_id == organization_id
    ).group_by(VendorEvaluation.vendor_id).limit(10)
    result_performance = await db.execute(stmt_performance)
    vendor_performance = result_performance.all()
    
    top_vendors = []
    for perf in vendor_performance:
        stmt_vendor = select(Vendor).where(Vendor.id == perf.vendor_id)
        result_vendor = await db.execute(stmt_vendor)
        vendor = result_vendor.scalar_one_or_none()
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
    stmt_pending = select(func.count(PurchaseRequisition.id)).where(
        PurchaseRequisition.organization_id == organization_id,
        PurchaseRequisition.approval_status == 'pending'
    )
    result_pending = await db.execute(stmt_pending)
    pending_approvals = result_pending.scalar()
    
    # Total purchase value (simplified calculation)
    stmt_purchase = select(func.sum(VendorQuotation.grand_total)).where(
        VendorQuotation.organization_id == organization_id,
        VendorQuotation.is_selected == True
    )
    result_purchase = await db.execute(stmt_purchase)
    total_purchase_value = result_purchase.scalar() or Decimal(0)
    
    return ProcurementDashboard(
        rfq_analytics=rfq_analytics,
        top_vendors=top_vendors,
        pending_approvals=pending_approvals,
        total_purchase_value=total_purchase_value,
        organization_id=organization_id,
        as_of_date=datetime.now().date()
    )