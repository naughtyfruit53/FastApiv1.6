# app/api/v1/organizations/settings_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.permissions import require_organization_permission, Permission
from app.models.organization_settings import OrganizationSettings
from app.schemas.organization_settings import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    OrganizationSettingsCreate
)
from app.core.security import get_current_user

router = APIRouter(prefix="/settings", tags=["organization-settings"])

@router.get("/", response_model=OrganizationSettingsResponse)
async def get_organization_settings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.ACCESS_ORG_SETTINGS))
):
    """Get organization settings for the current user's organization"""
    
    # Get or create organization settings
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == current_user.organization_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings if they don't exist
        settings = OrganizationSettings(
            organization_id=current_user.organization_id,
            mail_1_level_up_enabled=False,
            auto_send_notifications=True,
            voucher_prefix='',  # Default for voucher settings
            voucher_prefix_enabled=False,
            voucher_counter_reset_period='annually',
            voucher_format_template_id=None
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings

@router.put("/", response_model=OrganizationSettingsResponse)
async def update_organization_settings(
    settings_update: OrganizationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.ACCESS_ORG_SETTINGS))
):
    """Update organization settings (requires org admin or super admin role)"""
    
    # Get existing settings
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == current_user.organization_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create new settings if they don't exist
        settings_data = settings_update.dict(exclude_unset=True)
        settings_data['organization_id'] = current_user.organization_id
        settings = OrganizationSettings(**settings_data)
        db.add(settings)
    else:
        # Update existing settings
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return settings

@router.post("/", response_model=OrganizationSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_settings(
    settings_create: OrganizationSettingsCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.ACCESS_ORG_SETTINGS))
):
    """Create organization settings (org admin or super admin only)"""
    
    # Check if settings already exist
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == settings_create.organization_id
    ))
    existing_settings = result.scalar_one_or_none()
    
    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization settings already exist. Use PUT to update."
        )
    
    # Create new settings
    settings = OrganizationSettings(**settings_create.dict())
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    
    return settings