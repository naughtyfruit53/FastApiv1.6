# app/api/v1/vouchers/receipt_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import ReceiptVoucher
from app.schemas.vouchers import ReceiptVoucherCreate, ReceiptVoucherInDB, ReceiptVoucherUpdate
from app.services.email_service import send_voucher_email
import logging
import re
from sqlalchemy.sql import text  # Added import for text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["receipt-vouchers"])

def add_entity_name(voucher, db: Session):
    if voucher.entity_type == 'Customer':
        result = db.execute(text("SELECT name, email FROM customers WHERE id = :id"), {'id': voucher.entity_id}).first()
        if result:
            name, email = result
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    elif voucher.entity_type == 'Vendor':
        result = db.execute(text("SELECT name, email FROM vendors WHERE id = :id"), {'id': voucher.entity_id}).first()
        if result:
            name, email = result
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    elif voucher.entity_type == 'Employee':
        result = db.execute(text("SELECT full_name, email FROM employees WHERE id = :id"), {'id': voucher.entity_id}).first()
        if result:
            name, email = result
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    else:
        voucher.entity = {'name': 'N/A', 'email': None}
    return voucher

@router.get("", response_model=List[ReceiptVoucherInDB])
async def get_receipt_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all receipt vouchers with enhanced sorting and pagination"""
    query = db.query(ReceiptVoucher).filter(
        ReceiptVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ReceiptVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ReceiptVoucher, sortBy):
        sort_attr = getattr(ReceiptVoucher, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(ReceiptVoucher.created_at.desc())
    
    vouchers = query.offset(skip).limit(limit).all()
    for voucher in vouchers:
        add_entity_name(voucher, db)
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_receipt_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    org_id = current_user.organization_id
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization")
    
    last_voucher = db.query(func.max(ReceiptVoucher.voucher_number)).filter(
        ReceiptVoucher.organization_id == org_id
    ).scalar()
    
    if last_voucher:
        match = re.match(r"RCT-(\d+)", last_voucher)
        if match:
            next_number = int(match.group(1)) + 1
        else:
            next_number = 1
    else:
        next_number = 1
    
    return f"RCT-{next_number:06d}"

@router.post("", response_model=ReceiptVoucherInDB)
async def create_receipt_voucher(
    voucher: ReceiptVoucherCreate,
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
            voucher_data['voucher_number'] = await get_next_receipt_voucher_number(db=db, current_user=current_user)
        else:
            existing = db.query(ReceiptVoucher).filter(
                ReceiptVoucher.organization_id == current_user.organization_id,
                ReceiptVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = await get_next_receipt_voucher_number(db=db, current_user=current_user)
        
        db_voucher = ReceiptVoucher(**voucher_data)
        db.add(db_voucher)
        db.commit()
        db.refresh(db_voucher)
        
        if send_email and db_voucher.entity and db_voucher.entity.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="receipt_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.entity.email,
                recipient_name=db_voucher.entity.name
            )
        
        logger.info(f"Receipt voucher {db_voucher.voucher_number} created by {current_user.email}")
        add_entity_name(db_voucher, db)
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create receipt voucher")

@router.get("/{voucher_id}", response_model=ReceiptVoucherInDB)
async def get_receipt_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(ReceiptVoucher).filter(
        ReceiptVoucher.id == voucher_id,
        ReceiptVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Receipt voucher not found")
    add_entity_name(voucher, db)
    return voucher

@router.put("/{voucher_id}", response_model=ReceiptVoucherInDB)
async def update_receipt_voucher(
    voucher_id: int,
    voucher_update: ReceiptVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(ReceiptVoucher).filter(
            ReceiptVoucher.id == voucher_id,
            ReceiptVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Receipt voucher {voucher.voucher_number} updated by {current_user.email}")
        add_entity_name(voucher, db)
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update receipt voucher")

@router.delete("/{voucher_id}")
async def delete_receipt_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(ReceiptVoucher).filter(
            ReceiptVoucher.id == voucher_id,
            ReceiptVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt voucher not found")
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Receipt voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Receipt voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete receipt voucher")