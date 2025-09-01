# app/models/sticky_notes.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime

class StickyNote(Base):
    """User-specific sticky notes for dashboard"""
    __tablename__ = "sticky_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant fields
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_sticky_note_user_id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_sticky_note_organization_id"), nullable=False, index=True)
    
    # Note content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Visual properties
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="yellow")  # yellow, blue, green, pink, purple
    position: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # For future drag-and-drop positioning
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sticky_notes"
    )
    organization: Mapped["Organization"] = relationship(
        "Organization"
    )

    def __repr__(self):
        return f"<StickyNote(id={self.id}, title='{self.title}', user_id={self.user_id})>"