# app/api/v1/vouchers/quotation.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.presales import Quotation, QuotationItem
from app.schemas.vouchers import QuotationCreate, QuotationInDB, QuotationUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["quotations"])

@router.get("", response_model=List[QuotationInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[QuotationInDB])
async def get_quotations(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all quotations"""
    stmt = select(Quotation).options(joinedload(Quotation.customer)).where(
        Quotation.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(Quotation.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(Quotation, sortBy):
        sort_attr = getattr(Quotation, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(asc(sort_attr))
        else:
            stmt = stmt.order_by(desc(sort_attr))
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(desc(Quotation.created_at))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_quotation_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available quotation number"""
    return await VoucherNumberService.generate_voucher_number(
        db, "QT", current_user.organization_id, Quotation
    )

# Register both "" and "/" for POST to support both /api/v1/quotations and /api/v1/quotations/
@router.post("", response_model=QuotationInDB, include_in_schema=False)
@router.post("/", response_model=QuotationInDB)
async def create_quotation(
    quotation: QuotationCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new quotation"""
    try:
        quotation_data = quotation.dict(exclude={'items'})
        quotation_data['created_by'] = current_user.id
        quotation_data['organization_id'] = current_user.organization_id
        
        # Handle revisions: If parent_id provided, generate revised number
        if quotation.parent_id:
            stmt = select(Quotation).where(Quotation.id == quotation.parent_id)
            result = await db.execute(stmt)
            parent = result.scalar_one_or_none()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent quotation not found")
            
            # Get latest revision number
            stmt = select(func.max(Quotation.revision_number)).where(
                Quotation.organization_id == current_user.organization_id,
                Quotation.voucher_number.like(f"{parent.voucher_number}%")
            )
            result = await db.execute(stmt)
            latest_revision = result.scalar() or 0
            
            quotation_data['revision_number'] = latest_revision + 1
            quotation_data['voucher_number'] = f"{parent.voucher_number} Rev {quotation_data['revision_number']}"
            quotation_data['parent_id'] = quotation.parent_id
        else:
            # Generate unique voucher number if not provided or blank
            if not quotation_data.get('voucher_number') or quotation_data['voucher_number'] == '':
                quotation_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                    db, "QT", current_user.organization_id, Quotation
                )
            else:
                stmt = select(Quotation).where(
                    Quotation.organization_id == current_user.organization_id,
                    Quotation.voucher_number == quotation_data['voucher_number']
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    quotation_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                        db, "QT", current_user.organization_id, Quotation
                    )
        
        db_quotation = Quotation(**quotation_data)
        db.add(db_quotation)
        await db.flush()
        
        for item_data in quotation.items:
            item = QuotationItem(
                quotation_id=db_quotation.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(db_quotation)
        
        if send_email and db_quotation.customer and db_quotation.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="quotation",
                voucher_id=db_quotation.id,
                recipient_email=db_quotation.customer.email,
                recipient_name=db_quotation.customer.name
            )
        
        logger.info(f"Quotation {db_quotation.voucher_number} created by {current_user.email}")
        return db_quotation
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating quotation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quotation"
        )

@router.get("/{quotation_id}", response_model=QuotationInDB)
async def get_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(Quotation).options(
        joinedload(Quotation.customer),
        joinedload(Quotation.items).joinedload(QuotationItem.product)
    ).where(
        Quotation.id == quotation_id,
        Quotation.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    quotation = result.unique().scalar_one_or_none()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    return quotation

@router.put("/{quotation_id}", response_model=QuotationInDB)
async def update_quotation(
    quotation_id: int,
    quotation_update: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        logger.debug(f"Starting update for quotation {quotation_id} by {current_user.email}")
        stmt = select(Quotation).where(
            Quotation.id == quotation_id,
            Quotation.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        update_data = quotation_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(quotation, field, value)
        
        if quotation_update.items is not None:
            from sqlalchemy import delete
            stmt_delete = delete(QuotationItem).where(QuotationItem.quotation_id == quotation_id)
            await db.execute(stmt_delete)
            await db.flush()  # Flush deletes before adding new items to avoid potential locks
            for item_data in quotation_update.items:
                item = QuotationItem(
                    quotation_id=quotation_id,
                    **item_data.dict()
                )
                db.add(item)
            await db.flush()  # Flush adds before commit
        
        logger.debug(f"Before commit for quotation {quotation_id}")
        await db.commit()
        logger.debug(f"After commit for quotation {quotation_id}")
        await db.refresh(quotation)
        
        logger.info(f"Quotation {quotation.voucher_number} updated by {current_user.email}")
        return quotation
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating quotation {quotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quotation"
        )

@router.delete("/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(Quotation).where(
            Quotation.id == quotation_id,
            Quotation.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(QuotationItem).where(QuotationItem.quotation_id == quotation_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(quotation)
        await db.commit()
        
        logger.info(f"Quotation {quotation.voucher_number} deleted by {current_user.email}")
        return {"message": "Quotation deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting quotation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quotation"
        )