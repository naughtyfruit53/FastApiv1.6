# app/api/v1/vouchers/payment_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import PaymentVoucher
from app.models.customer_models import Vendor, Customer  # Vendor and Customer are in customer_models.py
from app.models.hr_models import EmployeeProfile as Employee  # Employee is EmployeeProfile in hr_models.py
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import PaymentVoucherCreate, PaymentVoucherInDB, PaymentVoucherUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payment-vouchers"])

def load_entity(db: Session, entity_id: int, entity_type: str) -> Optional[Dict[str, Any]]:
    if entity_type == 'Vendor':
        entity = db.query(Vendor).filter(Vendor.id == entity_id).first()
        return {'id': entity.id, 'name': entity.name, 'type': 'Vendor'} if entity else None
    elif entity_type == 'Customer':
        entity = db.query(Customer).filter(Customer.id == entity_id).first()
        return {'id': entity.id, 'name': entity.name, 'type': 'Customer'} if entity else None
    elif entity_type == 'Employee':
        entity = db.query(Employee).filter(Employee.id == entity_id).first()
        return {'id': entity.id, 'name': entity.name, 'type': 'Employee'} if entity else None
    return None

def validate_chart_account(db: Session, chart_account_id: int, organization_id: int) -> ChartOfAccounts:
    """Validate that chart_account_id exists and belongs to organization"""
    chart_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == chart_account_id,
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_active == True
    ).first()
    
    if not chart_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chart account ID or account not found for this organization"
        )
    
    return chart_account

@router.get("", response_model=List[PaymentVoucherInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PaymentVoucherInDB])
async def get_payment_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all payment vouchers with enhanced sorting and pagination"""
    query = db.query(PaymentVoucher).filter(
        PaymentVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PaymentVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PaymentVoucher, sortBy):
        sort_attr = getattr(PaymentVoucher, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(PaymentVoucher.created_at.desc())
    
    vouchers = query.offset(skip).limit(limit).all()
    for voucher in vouchers:
        voucher.entity = load_entity(db, voucher.entity_id, voucher.entity_type)
        # Load chart account details
        chart_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == voucher.chart_account_id
        ).first()
        voucher.chart_account = chart_account
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_payment_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available payment voucher number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PMT", current_user.organization_id, PaymentVoucher
    )

# Register both "" and "/" for POST to support both /api/v1/payment-vouchers and /api/v1/payment-vouchers/
@router.post("", response_model=PaymentVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PaymentVoucherInDB)
async def create_payment_voucher(
    voucher: PaymentVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new payment voucher"""
    try:
        if voucher.entity_type not in ['Vendor', 'Customer', 'Employee']:
            raise HTTPException(status_code=400, detail="Invalid entity_type")
        
        # Validate chart account
        chart_account = validate_chart_account(db, voucher.chart_account_id, current_user.organization_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PMT", current_user.organization_id, PaymentVoucher
            )
        else:
            existing = db.query(PaymentVoucher).filter(
                PaymentVoucher.organization_id == current_user.organization_id,
                PaymentVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PMT", current_user.organization_id, PaymentVoucher
                )
        
        db_voucher = PaymentVoucher(**voucher_data)
        db.add(db_voucher)
        db.commit()
        db.refresh(db_voucher)
        
        # Load entity and chart account details
        db_voucher.entity = load_entity(db, db_voucher.entity_id, db_voucher.entity_type)
        db_voucher.chart_account = chart_account
        
        if send_email and db_voucher.entity and 'email' in db_voucher.entity:  # Assuming entity has email, but for simplicity
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="payment_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.entity.get('email', ''),
                recipient_name=db_voucher.entity['name']
            )
        
        logger.info(f"Payment voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment voucher"
        )

@router.get("/{voucher_id}", response_model=PaymentVoucherInDB)
async def get_payment_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(PaymentVoucher).options(
        db.query(PaymentVoucher).join(ChartOfAccounts)
    ).filter(
        PaymentVoucher.id == voucher_id,
        PaymentVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment voucher not found"
        )
    voucher.entity = load_entity(db, voucher.entity_id, voucher.entity_type)
    
    # Load chart account details
    chart_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == voucher.chart_account_id
    ).first()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=PaymentVoucherInDB)
async def update_payment_voucher(
    voucher_id: int,
    voucher_update: PaymentVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(PaymentVoucher).filter(
            PaymentVoucher.id == voucher_id,
            PaymentVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment voucher not found"
            )
        
        update_data = voucher_update.dict(exclude_unset=True)
        if 'entity_type' in update_data and update_data['entity_type'] not in ['Vendor', 'Customer', 'Employee']:
            raise HTTPException(status_code=400, detail="Invalid entity_type")
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            validate_chart_account(db, update_data['chart_account_id'], current_user.organization_id)
        
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        db.commit()
        db.refresh(voucher)
        
        voucher.entity = load_entity(db, voucher.entity_id, voucher.entity_type)
        
        # Load chart account details
        chart_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == voucher.chart_account_id
        ).first()
        voucher.chart_account = chart_account
        
        logger.info(f"Payment voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payment voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment voucher"
        )

@router.delete("/{voucher_id}")
async def delete_payment_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(PaymentVoucher).filter(
            PaymentVoucher.id == voucher_id,
            PaymentVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment voucher not found"
            )
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Payment voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Payment voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payment voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment voucher"
        )