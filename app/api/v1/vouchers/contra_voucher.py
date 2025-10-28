# app/api/v1/vouchers/contra_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import ContraVoucher
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import ContraVoucherCreate, ContraVoucherInDB, ContraVoucherUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contra-vouchers", tags=["contra-vouchers"])

async def validate_chart_account(db: AsyncSession, chart_account_id: int, organization_id: int) -> ChartOfAccounts:
    """Validate that chart_account_id exists and belongs to organization"""
    stmt = select(ChartOfAccounts).where(
        ChartOfAccounts.id == chart_account_id,
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_active == True
    )
    result = await db.execute(stmt)
    chart_account = result.scalar_one_or_none()
    
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
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all contra vouchers with enhanced sorting and pagination"""
    current_user, org_id = auth
    
    stmt = select(ContraVoucher).where(
        ContraVoucher.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(ContraVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ContraVoucher, sortBy):
        sort_attr = getattr(ContraVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(ContraVoucher.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    vouchers = result.scalars().all()
    
    # Load chart account details for each voucher
    for voucher in vouchers:
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        voucher.chart_account = chart_account
    
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_contra_voucher_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available contra voucher number for a given date"""
    current_user, org_id = auth
    
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "CTR", org_id, ContraVoucher, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Check if creating a voucher with the given date would create conflicts"""
    current_user, org_id = auth
    
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "CTR", org_id, ContraVoucher, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.post("/", response_model=ContraVoucherInDB)
async def create_contra_voucher(
    voucher: ContraVoucherCreate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    current_user, org_id = auth
    
    try:
        # Validate chart account
        chart_account = await validate_chart_account(db, voucher.chart_account_id, org_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in voucher_data and voucher_data['date']:
            voucher_date = voucher_data['date'] if hasattr(voucher_data['date'], 'year') else None
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "CTR", org_id, ContraVoucher, voucher_date=voucher_date
            )
        else:
            stmt = select(ContraVoucher).where(
                ContraVoucher.organization_id == org_id,
                ContraVoucher.voucher_number == voucher_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "CTR", org_id, ContraVoucher, voucher_date=voucher_date
                )
        
        db_voucher = ContraVoucher(**voucher_data)
        db.add(db_voucher)
        await db.commit()
        await db.refresh(db_voucher)
        
        # Add chart account details
        db_voucher.chart_account = chart_account
        
        logger.info(f"Contra voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create contra voucher")

@router.get("/{voucher_id}", response_model=ContraVoucherInDB)
async def get_contra_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(ContraVoucher).where(
        ContraVoucher.id == voucher_id,
        ContraVoucher.organization_id == org_id
    )
    result = await db.execute(stmt)
    voucher = result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(status_code=404, detail="Contra voucher not found")
    
    # Load chart account details
    stmt_chart = select(ChartOfAccounts).where(
        ChartOfAccounts.id == voucher.chart_account_id
    )
    result_chart = await db.execute(stmt_chart)
    chart_account = result_chart.scalar_one_or_none()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=ContraVoucherInDB)
async def update_contra_voucher(
    voucher_id: int,
    voucher_update: ContraVoucherUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(ContraVoucher).where(
            ContraVoucher.id == voucher_id,
            ContraVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Contra voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            await validate_chart_account(db, update_data['chart_account_id'], org_id)
        
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        await db.commit()
        await db.refresh(voucher)
        
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        voucher.chart_account = chart_account
        
        logger.info(f"Contra voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contra voucher")

@router.delete("/{voucher_id}")
async def delete_contra_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(ContraVoucher).where(
            ContraVoucher.id == voucher_id,
            ContraVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Contra voucher not found")
        
        await db.delete(voucher)
        await db.commit()
        
        logger.info(f"Contra voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Contra voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting contra voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contra voucher")