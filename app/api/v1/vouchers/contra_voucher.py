# app/api/v1/vouchers/contra_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import ContraVoucher
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import ContraVoucherCreate, ContraVoucherInDB, ContraVoucherUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contra-vouchers", tags=["contra-vouchers"])

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

@router.get("/", response_model=List[ContraVoucherInDB])
async def get_contra_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all contra vouchers with enhanced sorting and pagination"""
    query = db.query(ContraVoucher).filter(
        ContraVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ContraVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ContraVoucher, sortBy):
        sort_attr = getattr(ContraVoucher, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(ContraVoucher.created_at.desc())
    
    vouchers = query.offset(skip).limit(limit).all()
    
    # Load chart account details for each voucher
    for voucher in vouchers:
        chart_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == voucher.chart_account_id
        ).first()
        voucher.chart_account = chart_account
    
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_contra_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "CTR", current_user.organization_id, ContraVoucher
    )

@router.post("/", response_model=ContraVoucherInDB)
async def create_contra_voucher(
    voucher: ContraVoucherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Validate chart account
        chart_account = validate_chart_account(db, voucher.chart_account_id, current_user.organization_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "CTR", current_user.organization_id, ContraVoucher
            )
        else:
            existing = db.query(ContraVoucher).filter(
                ContraVoucher.organization_id == current_user.organization_id,
                ContraVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "CTR", current_user.organization_id, ContraVoucher
                )
        
        db_voucher = ContraVoucher(**voucher_data)
        db.add(db_voucher)
        db.commit()
        db.refresh(db_voucher)
        
        # Add chart account details
        db_voucher.chart_account = chart_account
        
        logger.info(f"Contra voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create contra voucher")

@router.get("/{voucher_id}", response_model=ContraVoucherInDB)
async def get_contra_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(ContraVoucher).filter(
        ContraVoucher.id == voucher_id,
        ContraVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Contra voucher not found")
    
    # Load chart account details
    chart_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == voucher.chart_account_id
    ).first()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=ContraVoucherInDB)
async def update_contra_voucher(
    voucher_id: int,
    voucher_update: ContraVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(ContraVoucher).filter(
            ContraVoucher.id == voucher_id,
            ContraVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Contra voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            validate_chart_account(db, update_data['chart_account_id'], current_user.organization_id)
        
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        db.commit()
        db.refresh(voucher)
        
        # Load chart account details
        chart_account = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == voucher.chart_account_id
        ).first()
        voucher.chart_account = chart_account
        
        logger.info(f"Contra voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contra voucher")

@router.delete("/{voucher_id}")
async def delete_contra_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(ContraVoucher).filter(
            ContraVoucher.id == voucher_id,
            ContraVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(status_code=404, detail="Contra voucher not found")
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Contra voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Contra voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contra voucher")