# app/api/v1/vouchers/debit_note.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import timezone, datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import DebitNote
from app.schemas.vouchers import DebitNoteCreate, DebitNoteInDB, DebitNoteUpdate
from app.services.voucher_service import VoucherNumberService
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/debit-notes", tags=["debit-notes"])

@router.get("/", response_model=List[DebitNoteInDB])
async def get_debit_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all debit notes with enhanced sorting and pagination"""
    current_user, org_id = auth
    
    stmt = select(DebitNote).where(
        DebitNote.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(DebitNote.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(DebitNote, sortBy):
        sort_attr = getattr(DebitNote, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(DebitNote.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    notes = result.scalars().all()
    return notes

@router.get("/next-number", response_model=str)
async def get_next_debit_note_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available debit note number for a given date"""
    current_user, org_id = auth
    
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "DN", org_id, DebitNote, voucher_date=date_to_use
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
            db, "DN", org_id, DebitNote, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.post("/", response_model=DebitNoteInDB)
async def create_debit_note(
    note: DebitNoteCreate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    current_user, org_id = auth
    
    try:
        note_data = note.dict(exclude={'items'})
        note_data['created_by'] = current_user.id
        note_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in note_data and note_data['date']:
            note_data['date'] = note_data['date'].replace(tzinfo=timezone.utc)
            voucher_date = note_data['date']
        
        # Generate unique voucher number if not provided or blank
        if not note_data.get('voucher_number') or note_data['voucher_number'] == '':
            note_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "DN", org_id, DebitNote, voucher_date=voucher_date
            )
        else:
            stmt = select(DebitNote).where(
                DebitNote.organization_id == org_id,
                DebitNote.voucher_number == note_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                note_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "DN", org_id, DebitNote, voucher_date=voucher_date
                )
        
        db_note = DebitNote(**note_data)
        db.add(db_note)
        await db.flush()
        
        for item_data in note.items:
            from app.models.vouchers.financial import DebitNoteItem  # Assuming DebitNoteItem is in financial.py
            item = DebitNoteItem(
                debit_note_id=db_note.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(db_note)  # Refresh for fresh data post-commit

        # Calculate search_pattern for the period
        current_year = db_note.date.year
        current_month = db_note.date.month
        
        stmt_settings = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == org_id
        )
        result_settings = await db.execute(stmt_settings)
        org_settings = result_settings.scalars().first()
        
        full_prefix = "DN"
        if org_settings and org_settings.voucher_prefix_enabled and org_settings.voucher_prefix:
            full_prefix = f"{org_settings.voucher_prefix}-{full_prefix}"
        
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        reset_period = org_settings.voucher_counter_reset_period if org_settings else VoucherCounterResetPeriod.ANNUALLY
        
        period_segment = ""
        if reset_period == VoucherCounterResetPeriod.MONTHLY:
            month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            period_segment = month_names[current_month - 1]
        elif reset_period == VoucherCounterResetPeriod.QUARTERLY:
            quarter = ((current_month - 1) // 3) + 1
            period_segment = f"Q{quarter}"
        
        if period_segment:
            search_pattern = f"{full_prefix}/{fiscal_year}/{period_segment}/%"
        else:
            search_pattern = f"{full_prefix}/{fiscal_year}/%"
        
        # Check if backdated: if new date < max date in period (excluding this)
        max_date_stmt = select(func.max(DebitNote.date)).where(
            DebitNote.organization_id == org_id,
            DebitNote.voucher_number.like(search_pattern),
            DebitNote.id != db_note.id,
            DebitNote.is_deleted == False
        )
        result = await db.execute(max_date_stmt)
        max_date = result.scalar()
        
        if max_date and db_note.date < max_date:
            logger.info(f"Detected backdated insert for DN {db_note.voucher_number} - triggering reindex")
            reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                db, "DN", org_id, DebitNote, db_note.date, db_note.id
            )
            if not reindex_result["success"]:
                logger.error(f"Reindex failed after backdated insert: {reindex_result['error']}")
                # Don't raise - continue with high number
            else:
                await db.refresh(db_note)
                logger.info(f"Reindex successful - new number: {db_note.voucher_number}")
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(DebitNote).where(
            DebitNote.id == db_note.id
        )
        result = await db.execute(stmt)
        db_note = result.unique().scalars().first()
        
        # Async-safe model_validate (with error handling)
        try:
            validated_note = DebitNoteInDB.model_validate(db_note)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_note = DebitNoteInDB.model_validate(db_note.__dict__)
        
        logger.info(f"Debit note {db_note.voucher_number} created by {current_user.email}")
        
        # Convert to Pydantic model before returning (ensures data access while session is open)
        return validated_note
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating debit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create debit note"
        )

@router.get("/{note_id}", response_model=DebitNoteInDB)
async def get_debit_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(DebitNote).where(
        DebitNote.id == note_id,
        DebitNote.organization_id == org_id
    )
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debit note not found"
        )
    return note

@router.put("/{note_id}", response_model=DebitNoteInDB)
async def update_debit_note(
    note_id: int,
    note_update: DebitNoteUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(DebitNote).where(
            DebitNote.id == note_id,
            DebitNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debit note not found"
            )
        
        update_data = note_update.dict(exclude_unset=True, exclude={'items'})
        
        if 'date' in update_data and update_data['date']:
            update_data['date'] = update_data['date'].replace(tzinfo=timezone.utc)
        
        # If date is being updated, check if it's crossing periods
        if 'date' in update_data:
            old_date = note.date
            new_date = update_data['date']
            stmt_settings = select(OrganizationSettings).where(
                OrganizationSettings.organization_id == org_id
            )
            result_settings = await db.execute(stmt_settings)
            org_settings = result_settings.scalars().first()
            reset_period = org_settings.voucher_counter_reset_period if org_settings else VoucherCounterResetPeriod.ANNUALLY

            def get_period(dt: datetime) -> str:
                year = dt.year
                month = dt.month
                fiscal_year = f"{str(year)[-2:]}{str(year + 1 if month > 3 else year)[-2:]}"
                if reset_period == VoucherCounterResetPeriod.MONTHLY:
                    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    return f"{fiscal_year}/{month_names[month - 1]}"
                elif reset_period == VoucherCounterResetPeriod.QUARTERLY:
                    quarter = ((month - 1) // 3) + 1
                    return f"{fiscal_year}/Q{quarter}"
                else:
                    return fiscal_year

            old_period = get_period(old_date)
            new_period = get_period(new_date)
            if old_period != new_period:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot change voucher date across numbering periods"
                )
            
            # DO NOT regenerate voucher number on date change within same period!
            # Keep the original number — that's the whole point
            # Only regenerate if crossing fiscal periods (which is blocked above)
            pass
        
        for field, value in update_data.items():
            setattr(note, field, value)
        
        if note_update.items is not None:
            from app.models.vouchers.financial import DebitNoteItem  # Assuming DebitNoteItem is in financial.py
            stmt_items = select(DebitNoteItem).where(
                DebitNoteItem.debit_note_id == note_id
            )
            result_items = await db.execute(stmt_items)
            existing_items = result_items.scalars().all()
            for existing in existing_items:
                await db.delete(existing)
            
            for item_data in note_update.items:
                item = DebitNoteItem(
                    debit_note_id=note_id,
                    **item_data.dict()
                )
                db.add(item)
        
        logger.debug(f"Before commit for debit note {note_id}")
        await db.commit()
        logger.debug(f"After commit for debit note {note_id}")
        await db.refresh(note)  # Refresh for fresh data post-commit

        # Check for backdated conflict and reindex if necessary
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "DN", org_id, DebitNote, note.date
        )
        if conflict_info["has_conflict"] and conflict_info["later_voucher_count"] > 0:  # Skip if no vouchers to reindex
            try:
                reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                    db, "DN", org_id, DebitNote, note.date, note.id
                )
                if not reindex_result["success"]:
                    logger.error(f"Reindex failed: {reindex_result['error']}")
                    # Continue but log - don't rollback update
                else:
                    await db.refresh(note)
            except Exception as e:
                logger.error(f"Error during reindex: {str(e)}")
                # Don't rollback update; log only
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(DebitNote).where(
            DebitNote.id == note_id,
            DebitNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        note = result.unique().scalars().first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debit note not found"
            )
        
        # Async-safe model_validate (with error handling)
        try:
            validated_note = DebitNoteInDB.model_validate(note)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_note = DebitNoteInDB.model_validate(note.__dict__)
        
        logger.info(f"Debit note {note.voucher_number} updated by {current_user.email}")
        
        # Convert to Pydantic model before returning
        return validated_note
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating debit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update debit note"
        )

@router.delete("/{note_id}")
async def delete_debit_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(DebitNote).where(
            DebitNote.id == note_id,
            DebitNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debit note not found"
            )
        
        from app.models.vouchers.financial import DebitNoteItem  # Assuming DebitNoteItem is in financial.py
        stmt_items = select(DebitNoteItem).where(
            DebitNoteItem.debit_note_id == note_id
        )
        result_items = await db.execute(stmt_items)
        items = result_items.scalars().all()
        for item in items:
            await db.delete(item)
        
        await db.delete(note)
        await db.commit()
        
        logger.info(f"Debit note {note.voucher_number} deleted by {current_user.email}")
        return {"message": "Debit note deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting debit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete debit note"
        )
    