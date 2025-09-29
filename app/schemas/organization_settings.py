# app/schemas/organization_settings.py

from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class OrganizationSettingsBase(BaseModel):
    mail_1_level_up_enabled: bool = False
    auto_send_notifications: bool = True
    custom_settings: Optional[Dict] = None

class OrganizationSettingsCreate(OrganizationSettingsBase):
    organization_id: int

class OrganizationSettingsUpdate(BaseModel):
    mail_1_level_up_enabled: Optional[bool] = None
    auto_send_notifications: Optional[bool] = None
    custom_settings: Optional[Dict] = None

class OrganizationSettingsInDB(OrganizationSettingsBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrganizationSettingsResponse(OrganizationSettingsInDB):
    """Response model for organization settings"""
    pass