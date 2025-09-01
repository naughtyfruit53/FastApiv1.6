# app/api/v1/sticky_notes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user_models import User  # Use db model
from app.models.sticky_notes import StickyNote
from app.schemas.sticky_notes import (
    StickyNoteCreate, StickyNoteUpdate, StickyNote as StickyNoteSchema,
    UserSettingsUpdate, UserSettings
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[StickyNoteSchema])
async def get_sticky_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's sticky notes"""
    try:
        notes = db.query(StickyNote).filter(
            StickyNote.user_id == current_user.id,
            StickyNote.organization_id == current_user.organization_id,
            StickyNote.is_active == True
        ).offset(skip).limit(limit).all()
        
        return notes
    except Exception as e:
        logger.error(f"Error fetching sticky notes for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching sticky notes")

@router.post("", response_model=StickyNoteSchema)
async def create_sticky_note(
    note: StickyNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sticky note"""
    try:
        # Validate color
        valid_colors = ["yellow", "blue", "green", "pink", "purple", "orange"]
        if note.color not in valid_colors:
            note.color = "yellow"
        
        db_note = StickyNote(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            title=note.title,
            content=note.content,
            color=note.color,
            position=note.position
        )
        
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        logger.info(f"Created sticky note {db_note.id} for user {current_user.id}")
        return db_note
        
    except Exception as e:
        logger.error(f"Error creating sticky note for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating sticky note")

@router.get("/{note_id}", response_model=StickyNoteSchema)
async def get_sticky_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific sticky note"""
    note = db.query(StickyNote).filter(
        StickyNote.id == note_id,
        StickyNote.user_id == current_user.id,
        StickyNote.organization_id == current_user.organization_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sticky note not found")
    
    return note

@router.put("/{note_id}", response_model=StickyNoteSchema)
async def update_sticky_note(
    note_id: int,
    note_update: StickyNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a sticky note"""
    try:
        db_note = db.query(StickyNote).filter(
            StickyNote.id == note_id,
            StickyNote.user_id == current_user.id,
            StickyNote.organization_id == current_user.organization_id
        ).first()
        
        if not db_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sticky note not found")
        
        update_data = note_update.model_dump(exclude_unset=True)
        
        # Validate color if provided
        if "color" in update_data:
            valid_colors = ["yellow", "blue", "green", "pink", "purple", "orange"]
            if update_data["color"] not in valid_colors:
                update_data["color"] = "yellow"
        
        for field, value in update_data.items():
            setattr(db_note, field, value)
        
        db.commit()
        db.refresh(db_note)
        
        logger.info(f"Updated sticky note {note_id} for user {current_user.id}")
        return db_note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sticky note {note_id} for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating sticky note")

@router.delete("/{note_id}")
async def delete_sticky_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sticky note"""
    try:
        db_note = db.query(StickyNote).filter(
            StickyNote.id == note_id,
            StickyNote.user_id == current_user.id,
            StickyNote.organization_id == current_user.organization_id
        ).first()
        
        if not db_note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sticky note not found")
        
        # Soft delete by setting is_active to False
        db_note.is_active = False
        db.commit()
        
        logger.info(f"Deleted sticky note {note_id} for user {current_user.id}")
        return {"message": "Sticky note deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sticky note {note_id} for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting sticky note")

@router.get("/settings/user-settings", response_model=UserSettings)
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user settings"""
    if current_user.user_settings is None:
        # Return default settings
        return UserSettings(sticky_notes_enabled=True)
    
    return UserSettings(**current_user.user_settings)

@router.put("/settings/user-settings", response_model=UserSettings)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user settings"""
    try:
        # Get current settings or initialize with defaults
        current_settings = current_user.user_settings or {"sticky_notes_enabled": True}
        
        # Update only provided fields
        update_data = settings_update.model_dump(exclude_unset=True)
        current_settings.update(update_data)
        
        # Update user settings
        current_user.user_settings = current_settings
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Updated user settings for user {current_user.id}")
        return UserSettings(**current_settings)
        
    except Exception as e:
        logger.error(f"Error updating user settings for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating user settings")