# app/api/v1/vouchers/receipt_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import ReceiptVoucher
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import ReceiptVoucherCreate, ReceiptVoucherInDB, ReceiptVoucherUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging
from sqlalchemy.sql import text  # Added import for text

logger = logging.getLogger(__name__)
router = APIRouter(tags=["receipt-vouchers"])

async def add_entity_name(voucher, db: AsyncSession):
    if voucher.entity_type == 'Customer':
        stmt = text("SELECT name, email FROM customers WHERE id = :id")
        result = await db.execute(stmt, {'id': voucher.entity_id})
        row = result.first()
        if row:
            name, email = row
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    elif voucher.entity_type == 'Vendor':
        stmt = text("SELECT name, email FROM vendors WHERE id = :id")
        result = await db.execute(stmt, {'id': voucher.entity_id})
        row = result.first()
        if row:
            name, email = row
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    elif voucher.entity_type == 'Employee':
        stmt = text("SELECT full_name, email FROM employees WHERE id = :id")
        result = await db.execute(stmt, {'id': voucher.entity_id})
        row = result.first()
        if row:
            name, email = row
            voucher.entity = {'name': name, 'email': email}
        else:
            voucher.entity = {'name': 'N/A', 'email': None}
    else:
        voucher.entity = {'name': 'N/A', 'email': None}
    return voucher

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

@router.get("", response_model=List[ReceiptVoucherInDB])
async def get_receipt_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all receipt vouchers with enhanced sorting and pagination"""
    stmt = select(ReceiptVoucher).where(
        ReceiptVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(ReceiptVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ReceiptVoucher, sortBy):
        sort_attr = getattr(ReceiptVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(ReceiptVoucher.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    vouchers = result.scalars().all()
    for voucher in vouchers:
        await add_entity_name(voucher, db)
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        voucher.chart_account = chart_account
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_receipt_voucher_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available receipt voucher number for a given date"""
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "RCT", current_user.organization_id, ReceiptVoucher, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if creating a voucher with the given date would create conflicts"""
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "RCT", current_user.organization_id, ReceiptVoucher, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.post("", response_model=ReceiptVoucherInDB)
async def create_receipt_voucher(
    voucher: ReceiptVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Validate chart account
        chart_account = await validate_chart_account(db, voucher.chart_account_id, current_user.organization_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in voucher_data and voucher_data['date']:
            voucher_date = voucher_data['date'] if hasattr(voucher_data['date'], 'year') else None
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "RCT", current_user.organization_id, ReceiptVoucher, voucher_date=voucher_date
            )
        else:
            stmt = select(ReceiptVoucher).where(
                ReceiptVoucher.organization_id == current_user.organization_id,
                ReceiptVoucher.voucher_number == voucher_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "RCT", current_user.organization_id, ReceiptVoucher, voucher_date=voucher_date
                )
        
        db_voucher = ReceiptVoucher(**voucher_data)
        db.add(db_voucher)
        await db.commit()
        await db.refresh(db_voucher)
        
        if send_email and db_voucher.entity and db_voucher.entity.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="receipt_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.entity.email,
                recipient_name=db_voucher.entity.name
            )
        
        logger.info(f"Receipt voucher {db_voucher.voucher_number} created by {current_user.email}")
        await add_entity_name(db_voucher, db)
        
        # Add chart account details
        db_voucher.chart_account = chart_account
        
        return db_voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create receipt voucher")

@router.get("/{voucher_id}", response_model=ReceiptVoucherInDB)
async def get_receipt_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(ReceiptVoucher).where(
        ReceiptVoucher.id == voucher_id,
        ReceiptVoucher.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    voucher = result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(status_code=404, detail="Receipt voucher not found")
    await add_entity_name(voucher, db)
    
    # Load chart account details
    stmt_chart = select(ChartOfAccounts).where(
        ChartOfAccounts.id == voucher.chart_account_id
    )
    result_chart = await db.execute(stmt_chart)
    chart_account = result_chart.scalar_one_or_none()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=ReceiptVoucherInDB)
async def update_receipt_voucher(
    voucher_id: int,
    voucher_update: ReceiptVoucherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(ReceiptVoucher).where(
            ReceiptVoucher.id == voucher_id,
            ReceiptVoucher.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt voucher not found")
        
        update_data = voucher_update.dict(exclude_unset=True)
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            await validate_chart_account(db, update_data['chart_account_id'], current_user.organization_id)
        
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        await db.commit()
        await db.refresh(voucher)
        
        logger.info(f"Receipt voucher {voucher.voucher_number} updated by {current_user.email}")
        await add_entity_name(voucher, db)
        
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        voucher.chart_account = chart_account
        
        return voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to update receipt voucher")

@router.delete("/{voucher_id}")
async def delete_receipt_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(ReceiptVoucher).where(
            ReceiptVoucher.id == voucher_id,
            ReceiptVoucher.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Receipt voucher not found")
        
        await db.delete(voucher)
        await db.commit()
        
        logger.info(f"Receipt voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Receipt voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting receipt voucher: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete receipt voucher")