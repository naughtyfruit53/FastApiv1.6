# app/schemas/sticky_notes.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class StickyNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the sticky note")
    content: str = Field(..., min_length=1, description="Content of the sticky note")
    color: str = Field(default="yellow", description="Color theme of the sticky note")
    position: Optional[Dict[str, Any]] = Field(default=None, description="Position data for the note")

class StickyNoteCreate(StickyNoteBase):
    pass

class StickyNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    color: Optional[str] = None
    position: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class StickyNoteInDB(StickyNoteBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class StickyNote(StickyNoteInDB):
    pass

class UserSettingsUpdate(BaseModel):
    sticky_notes_enabled: Optional[bool] = None
    # Can be extended with other user preferences in the future

class UserSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    sticky_notes_enabled: bool = True
    # Can be extended with other user preferences in the future