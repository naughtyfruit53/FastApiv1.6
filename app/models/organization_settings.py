# app/models/organization_settings.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional
from datetime import datetime

class OrganizationSettings(Base):
    """Organization-wide settings including email preferences"""
    __tablename__ = "organization_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field (one record per organization)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_organization_settings_organization_id"), nullable=False, unique=True, index=True)
    
    # Email Settings
    mail_1_level_up_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Future extensibility for other organization-wide settings
    auto_send_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Custom settings (JSON for flexibility)
    custom_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization",
        back_populates="settings"
    )

    __table_args__ = (
        Index('idx_organization_settings_organization_id', 'organization_id'),
        Index('idx_organization_settings_mail_1_level_up', 'mail_1_level_up_enabled'),
        {'extend_existing': True}
    )