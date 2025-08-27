# app/api/v1/vouchers/inter_department_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers import InterDepartmentVoucher
from app.schemas.vouchers import InterDepartmentVoucherCreate, InterDepartmentVoucherInDB, InterDepartmentVoucherUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inter-department-vouchers", tags=["inter-department-vouchers"])

@router.get("/", response_model=List[InterDepartmentVoucherInDB])
async def get_inter_department_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inter department vouchers with enhanced sorting and pagination"""
    query = db.query(InterDepartmentVoucher).filter(
        InterDepartmentVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(InterDepartmentVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(InterDepartmentVoucher, sortBy):
        sort_attr = getattr(InterDepartmentVoucher, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(InterDepartmentVoucher.created_at.desc())
    
    vouchers = query.offset(skip).limit(limit).all()
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_inter_department_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "IDV", current_user.organization_id, InterDepartmentVoucher
    )

@router.post("/", response_model=InterDepartmentVoucherInDB)
async def create_inter_department_voucher(
    voucher: InterDepartmentVoucherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher_data = voucher.dict(exclude={'items'})
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "IDV", current_user.organization_id, InterDepartmentVoucher
            )
        else:
            existing = db.query(InterDepartmentVoucher).filter(
                InterDepartmentVoucher.organization_id == current_user.organization_id,
                InterDepartmentVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "IDV", current_user.organization_id, InterDepartmentVoucher
                )
        
        db_voucher = InterDepartmentVoucher(**voucher_data)
        db.add(db_voucher)
        db.flush()
        
        for item_data in voucher.items:
            from app.models.vouchers import InterDepartmentVoucherItem
            item = InterDepartmentVoucherItem(
                inter_department_voucher_id=db_voucher.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_voucher)
        
        logger.info(f"Inter department voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating inter department voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create inter department voucher")

@router.get("/{voucher_id}", response_model=InterDepartmentVoucherInDB)
async def get_inter_department_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(InterDepartmentVoucher).filter(
        InterDepartmentVoucher.id == voucher_id,
        InterDepartmentVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Inter department voucher not found")
    return voucher

@router.put("/{voucher_id}", response_model=InterDepartmentVoucherInDB)
async def update_inter_department_voucher(
    voucher_id: int,
    voucher_update: InterDepartmentVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(InterDepartmentVoucher).filter(
            InterDepartmentVoucher.id == voucher_id,
            InterDepartmentVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Inter department voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        if voucher_update.items is not None:
            from app.models.vouchers import InterDepartmentVoucherItem
            db.query(InterDepartmentVoucherItem).filter(
                InterDepartmentVoucherItem.inter_department_voucher_id == voucher_id
            ).delete()
            
            for item_data in voucher_update.items:
                item = InterDepartmentVoucherItem(
                    inter_department_voucher_id=voucher_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Inter department voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating inter department voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update inter department voucher")

@router.delete("/{voucher_id}")
async def delete_inter_department_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(InterDepartmentVoucher).filter(
            InterDepartmentVoucher.id == voucher_id,
            InterDepartmentVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Inter department voucher not found")
        
        from app.models.vouchers import InterDepartmentVoucherItem
        db.query(InterDepartmentVoucherItem).filter(
            InterDepartmentVoucherItem.inter_department_voucher_id == voucher_id
        ).delete()
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Inter department voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Inter department voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting inter department voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete inter department voucher")