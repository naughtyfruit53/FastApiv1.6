# app/api/v1/organizations/settings_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.organization_settings import OrganizationSettings
from app.schemas.organization_settings import (
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    OrganizationSettingsCreate
)
from app.schemas.tally import TallyConfig, TallyConnectionTest, TallyConnectionTestResponse, TallySyncResponse
from app.core.security import get_current_user
from app.services.tally_service import TallyIntegrationService

router = APIRouter(prefix="/settings", tags=["organization-settings"])

@router.get("/", response_model=OrganizationSettingsResponse)
async def get_organization_settings(
    auth: tuple = Depends(require_access("organization_settings", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization settings for the current user's organization"""
    current_user, org_id = auth
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = OrganizationSettings(
            organization_id=org_id,
            mail_1_level_up_enabled=False,
            auto_send_notifications=True,
            voucher_prefix='',
            voucher_prefix_enabled=False,
            voucher_counter_reset_period='annually',
            voucher_format_template_id=None,
            tally_enabled=False,
            tally_host='localhost',
            tally_port=9000,
            tally_company_name='',
            tally_sync_frequency='manual'
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings

@router.put("/", response_model=OrganizationSettingsResponse)
async def update_organization_settings(
    settings_update: OrganizationSettingsUpdate,
    auth: tuple = Depends(require_access("organization_settings", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update organization settings (requires organization_settings update permission)"""
    current_user, org_id = auth
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings_data = settings_update.dict(exclude_unset=True)
        settings_data['organization_id'] = org_id
        settings = OrganizationSettings(**settings_data)
        db.add(settings)
    else:
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return settings

@router.post("/", response_model=OrganizationSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_settings(
    settings_create: OrganizationSettingsCreate,
    auth: tuple = Depends(require_access("organization_settings", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create organization settings (requires organization_settings create permission)"""
    current_user, org_id = auth
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == settings_create.organization_id
    ))
    existing_settings = result.scalar_one_or_none()
    
    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization settings already exist. Use PUT to update."
        )
    
    settings = OrganizationSettings(**settings_create.dict())
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    
    return settings

@router.get("/tally/configuration", response_model=TallyConfig)
async def get_tally_config(
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("organization_settings", "read"))
):
    """Get Tally configuration for the organization"""
    current_user, org_id = auth
        )
    
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        return TallyConfig(
            enabled=False,
            host="localhost",
            port=9000,
            company_name="",
            sync_frequency="manual"
        )
    
    return TallyConfig(
        enabled=settings.tally_enabled,
        host=settings.tally_host or "localhost",
        port=settings.tally_port or 9000,
        company_name=settings.tally_company_name or "",
        sync_frequency=settings.tally_sync_frequency or "manual",
        last_sync=settings.tally_last_sync
    )

@router.post("/tally/configuration", response_model=TallyConfig)
async def update_tally_config(
    config: TallyConfig,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("organization_settings", "read"))
):
    """Update Tally configuration for the organization"""
    current_user, org_id = auth
        )
    
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = OrganizationSettings(
            organization_id=org_id,
            mail_1_level_up_enabled=False,
            auto_send_notifications=True,
            voucher_prefix='',
            voucher_prefix_enabled=False,
            voucher_counter_reset_period='annually',
            voucher_format_template_id=None
        )
        db.add(settings)
    
    settings.tally_enabled = config.enabled
    settings.tally_host = config.host
    settings.tally_port = config.port
    settings.tally_company_name = config.company_name
    settings.tally_sync_frequency = config.sync_frequency
    
    await db.commit()
    await db.refresh(settings)
    
    return TallyConfig(
        enabled=settings.tally_enabled,
        host=settings.tally_host,
        port=settings.tally_port,
        company_name=settings.tally_company_name,
        sync_frequency=settings.tally_sync_frequency,
        last_sync=settings.tally_last_sync
    )

@router.post("/tally/test-connection", response_model=TallyConnectionTestResponse)
async def test_tally_connection(
    config: TallyConnectionTest,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("organization_settings", "read"))
):
    """Test Tally connection"""
    current_user, org_id = auth
        )
    
    response = await TallyIntegrationService.test_tally_connection(config)
    return response

@router.post("/tally/sync", response_model=TallySyncResponse)
async def sync_with_tally(
    sync_type: str,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("organization_settings", "read"))
):
    """Initiate Tally sync"""
    current_user, org_id = auth
        )
    
    # Placeholder: Implement actual sync logic in TallyIntegrationService
    result = await db.execute(select(OrganizationSettings).filter(
        OrganizationSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings or not settings.tally_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tally integration is not enabled"
        )
    
    # Update last sync time (placeholder - actual sync logic would go here)
    settings.tally_last_sync = func.now()
    await db.commit()
    await db.refresh(settings)
    
    return TallySyncResponse(
        success=True,
        items_synced=0,  # Placeholder
        message="Sync completed successfully (simulated)"
    )