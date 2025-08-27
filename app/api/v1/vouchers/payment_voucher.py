# app/api/v1/vouchers/payment_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import PaymentVoucher
from app.schemas.vouchers import PaymentVoucherCreate, PaymentVoucherInDB, PaymentVoucherUpdate
from app.services.email_service import send_voucher_email
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payment-vouchers"])  # Removed prefix="/payment-vouchers" to avoid double prefixing

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
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_payment_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    org_id = current_user.organization_id
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization")
    
    last_voucher = db.query(func.max(PaymentVoucher.voucher_number)).filter(
        PaymentVoucher.organization_id == org_id
    ).scalar()
    
    if last_voucher:
        match = re.match(r"PMT-(\d+)", last_voucher)
        if match:
            next_number = int(match.group(1)) + 1
        else:
            next_number = 1
    else:
        next_number = 1
    
    return f"PMT-{next_number:06d}"

@router.post("/", response_model=PaymentVoucherInDB)
async def create_payment_voucher(
    voucher: PaymentVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await get_next_payment_voucher_number(db=db, current_user=current_user)
        else:
            existing = db.query(PaymentVoucher).filter(
                PaymentVoucher.organization_id == current_user.organization_id,
                PaymentVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = await get_next_payment_voucher_number(db=db, current_user=current_user)
        
        db_voucher = PaymentVoucher(**voucher_data)
        db.add(db_voucher)
        db.commit()
        db.refresh(db_voucher)
        
        if send_email and db_voucher.vendor and db_voucher.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="payment_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.vendor.email,
                recipient_name=db_voucher.vendor.name
            )
        
        logger.info(f"Payment voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment voucher")

@router.get("/{voucher_id}", response_model=PaymentVoucherInDB)
async def get_payment_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(PaymentVoucher).filter(
        PaymentVoucher.id == voucher_id,
        PaymentVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Payment voucher not found")
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
            raise HTTPException(status_code=404, detail="Payment voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Payment voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payment voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update payment voucher")

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
            raise HTTPException(status_code=404, detail="Payment voucher not found")
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Payment voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Payment voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payment voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete payment voucher")