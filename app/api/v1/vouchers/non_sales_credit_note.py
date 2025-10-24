from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import NonSalesCreditNote
from app.schemas.vouchers import NonSalesCreditNoteCreate, NonSalesCreditNoteInDB, NonSalesCreditNoteUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/non-sales-credit-notes", tags=["non-sales-credit-notes"])

@router.get("/", response_model=List[NonSalesCreditNoteInDB])
async def get_non_sales_credit_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all non-sales credit notes with enhanced sorting and pagination"""
    stmt = select(NonSalesCreditNote).where(
        NonSalesCreditNote.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(NonSalesCreditNote.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(NonSalesCreditNote, sortBy):
        sort_attr = getattr(NonSalesCreditNote, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(NonSalesCreditNote.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    notes = result.scalars().all()
    return notes

@router.get("/next-number", response_model=str)
async def get_next_non_sales_credit_note_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available non-sales credit note number for a given date"""
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "NSCN", current_user.organization_id, NonSalesCreditNote, voucher_date=date_to_use
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
            db, "NSCN", current_user.organization_id, NonSalesCreditNote, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.post("/", response_model=NonSalesCreditNoteInDB)
async def create_non_sales_credit_note(
    note: NonSalesCreditNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        note_data = note.dict(exclude={'items'})
        note_data['created_by'] = current_user.id
        note_data['organization_id'] = current_user.organization_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in note_data and note_data['date']:
            voucher_date = note_data['date'] if hasattr(note_data['date'], 'year') else None
        
        # Generate unique voucher number if not provided or blank
        if not note_data.get('voucher_number') or note_data['voucher_number'] == '':
            note_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "NSCN", current_user.organization_id, NonSalesCreditNote, voucher_date=voucher_date
            )
        else:
            stmt = select(NonSalesCreditNote).where(
                NonSalesCreditNote.organization_id == current_user.organization_id,
                NonSalesCreditNote.voucher_number == note_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                note_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "NSCN", current_user.organization_id, NonSalesCreditNote, voucher_date=voucher_date
                )
        
        db_note = NonSalesCreditNote(**note_data)
        db.add(db_note)
        await db.flush()
        
        for item_data in note.items:
            from app.models.vouchers import NonSalesCreditNoteItem
            item = NonSalesCreditNoteItem(
                non_sales_credit_note_id=db_note.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(db_note)
        
        logger.info(f"Non-sales credit note {db_note.voucher_number} created by {current_user.email}")
        return db_note
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating non-sales credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create non-sales credit note"
        )

@router.get("/{note_id}", response_model=NonSalesCreditNoteInDB)
async def get_non_sales_credit_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(NonSalesCreditNote).where(
        NonSalesCreditNote.id == note_id,
        NonSalesCreditNote.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-sales credit note not found"
        )
    return note

@router.put("/{note_id}", response_model=NonSalesCreditNoteInDB)
async def update_non_sales_credit_note(
    note_id: int,
    note_update: NonSalesCreditNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(NonSalesCreditNote).where(
            NonSalesCreditNote.id == note_id,
            NonSalesCreditNote.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-sales credit note not found"
            )
        
        update_data = note_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(note, field, value)
        
        if note_update.items is not None:
            from app.models.vouchers import NonSalesCreditNoteItem
            stmt_items = select(NonSalesCreditNoteItem).where(
                NonSalesCreditNoteItem.non_sales_credit_note_id == note_id
            )
            result_items = await db.execute(stmt_items)
            existing_items = result_items.scalars().all()
            for existing in existing_items:
                await db.delete(existing)
            
            for item_data in note_update.items:
                item = NonSalesCreditNoteItem(
                    non_sales_credit_note_id=note_id,
                    **item_data.dict()
                )
                db.add(item)
        
        await db.commit()
        await db.refresh(note)
        
        logger.info(f"Non-sales credit note {note.voucher_number} updated by {current_user.email}")
        return note
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating non-sales credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update non-sales credit note"
        )

@router.delete("/{note_id}")
async def delete_non_sales_credit_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(NonSalesCreditNote).where(
            NonSalesCreditNote.id == note_id,
            NonSalesCreditNote.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-sales credit note not found"
            )
        
        from app.models.vouchers import NonSalesCreditNoteItem
        stmt_items = select(NonSalesCreditNoteItem).where(
            NonSalesCreditNoteItem.non_sales_credit_note_id == note_id
        )
        result_items = await db.execute(stmt_items)
        items = result_items.scalars().all()
        for item in items:
            await db.delete(item)
        
        await db.delete(note)
        await db.commit()
        
        logger.info(f"Non-sales credit note {note.voucher_number} deleted by {current_user.email}")
        return {"message": "Non-sales credit note deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting non-sales credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete non-sales credit note"
        )