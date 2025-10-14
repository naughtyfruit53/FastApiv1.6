# app/api/v1/vouchers/journal_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import JournalVoucher
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import JournalVoucherCreate, JournalVoucherInDB, JournalVoucherUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/journal-vouchers", tags=["journal-vouchers"])

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

@router.get("/", response_model=List[JournalVoucherInDB])
async def get_journal_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all journal vouchers with enhanced sorting and pagination"""
    stmt = select(JournalVoucher).where(
        JournalVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(JournalVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(JournalVoucher, sortBy):
        sort_attr = getattr(JournalVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(JournalVoucher.created_at.desc())
    
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
async def get_next_journal_voucher_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await VoucherNumberService.generate_voucher_number_async(
        db, "JNL", current_user.organization_id, JournalVoucher
    )

@router.post("/", response_model=JournalVoucherInDB)
async def create_journal_voucher(
    voucher: JournalVoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Validate chart account
        chart_account = await validate_chart_account(db, voucher.chart_account_id, current_user.organization_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "JNL", current_user.organization_id, JournalVoucher
            )
        else:
            stmt = select(JournalVoucher).where(
                JournalVoucher.organization_id == current_user.organization_id,
                JournalVoucher.voucher_number == voucher_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "JNL", current_user.organization_id, JournalVoucher
                )
        
        db_voucher = JournalVoucher(**voucher_data)
        db.add(db_voucher)
        await db.commit()
        await db.refresh(db_voucher)
        
        # Add chart account details
        db_voucher.chart_account = chart_account
        
        logger.info(f"Journal voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating journal voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create journal voucher")

@router.get("/{voucher_id}", response_model=JournalVoucherInDB)
async def get_journal_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(JournalVoucher).where(
        JournalVoucher.id == voucher_id,
        JournalVoucher.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    voucher = result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(status_code=404, detail="Journal voucher not found")
    
    # Load chart account details
    stmt_chart = select(ChartOfAccounts).where(
        ChartOfAccounts.id == voucher.chart_account_id
    )
    result_chart = await db.execute(stmt_chart)
    chart_account = result_chart.scalar_one_or_none()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=JournalVoucherInDB)
async def update_journal_voucher(
    voucher_id: int,
    voucher_update: JournalVoucherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(JournalVoucher).where(
            JournalVoucher.id == voucher_id,
            JournalVoucher.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Journal voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            await validate_chart_account(db, update_data['chart_account_id'], current_user.organization_id)
        
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
        
        logger.info(f"Journal voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating journal voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update journal voucher")

@router.delete("/{voucher_id}")
async def delete_journal_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(JournalVoucher).where(
            JournalVoucher.id == voucher_id,
            JournalVoucher.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Journal voucher not found")
        
        await db.delete(voucher)
        await db.commit()
        
        logger.info(f"Journal voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Journal voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting journal voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete journal voucher")