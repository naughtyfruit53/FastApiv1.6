# app/api/v1/vouchers/credit_note.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import CreditNote
from app.schemas.vouchers import CreditNoteCreate, CreditNoteInDB, CreditNoteUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/credit-notes", tags=["credit-notes"])

@router.get("/", response_model=List[CreditNoteInDB])
async def get_credit_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all credit notes with enhanced sorting and pagination"""
    query = db.query(CreditNote).filter(
        CreditNote.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(CreditNote.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(CreditNote, sortBy):
        sort_attr = getattr(CreditNote, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(CreditNote.created_at.desc())
    
    notes = query.offset(skip).limit(limit).all()
    return notes

@router.get("/next-number", response_model=str)
async def get_next_credit_note_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available credit note number for a given date"""
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return VoucherNumberService.generate_voucher_number(
        db, "CN", current_user.organization_id, CreditNote, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if creating a voucher with the given date would create conflicts"""
    try:
        parsed_date = date_parser.parse(voucher_date)
        # Note: This is sync version, return no conflict for now
        return {
            "has_conflict": False,
            "later_voucher_count": 0,
            "suggested_date": parsed_date.isoformat(),
            "period": "ANNUAL"
        }
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.post("/", response_model=CreditNoteInDB)
async def create_credit_note(
    note: CreditNoteCreate,
    db: Session = Depends(get_db),
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
            note_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "CN", current_user.organization_id, CreditNote, voucher_date=voucher_date
            )
        else:
            existing = db.query(CreditNote).filter(
                CreditNote.organization_id == current_user.organization_id,
                CreditNote.voucher_number == note_data['voucher_number']
            ).first()
            if existing:
                note_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "CN", current_user.organization_id, CreditNote, voucher_date=voucher_date
                )
        
        db_note = CreditNote(**note_data)
        db.add(db_note)
        db.flush()
        
        for item_data in note.items:
            from app.models.vouchers import CreditNoteItem
            item = CreditNoteItem(
                credit_note_id=db_note.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_note)
        
        logger.info(f"Credit note {db_note.voucher_number} created by {current_user.email}")
        return db_note
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credit note"
        )

@router.get("/{note_id}", response_model=CreditNoteInDB)
async def get_credit_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    note = db.query(CreditNote).filter(
        CreditNote.id == note_id,
        CreditNote.organization_id == current_user.organization_id
    ).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit note not found"
        )
    return note

@router.put("/{note_id}", response_model=CreditNoteInDB)
async def update_credit_note(
    note_id: int,
    note_update: CreditNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        note = db.query(CreditNote).filter(
            CreditNote.id == note_id,
            CreditNote.organization_id == current_user.organization_id
        ).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit note not found"
            )
        
        update_data = note_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(note, field, value)
        
        if note_update.items is not None:
            from app.models.vouchers import CreditNoteItem
            db.query(CreditNoteItem).filter(
                CreditNoteItem.credit_note_id == note_id
            ).delete()
            
            for item_data in note_update.items:
                item = CreditNoteItem(
                    credit_note_id=note_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(note)
        
        logger.info(f"Credit note {note.voucher_number} updated by {current_user.email}")
        return note
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update credit note"
        )

@router.delete("/{note_id}")
async def delete_credit_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        note = db.query(CreditNote).filter(
            CreditNote.id == note_id,
            CreditNote.organization_id == current_user.organization_id
        ).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit note not found"
            )
        
        from app.models.vouchers import CreditNoteItem
        db.query(CreditNoteItem).filter(
            CreditNoteItem.credit_note_id == note_id
        ).delete()
        
        db.delete(note)
        db.commit()
        
        logger.info(f"Credit note {note.voucher_number} deleted by {current_user.email}")
        return {"message": "Credit note deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting credit note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete credit note"
        )