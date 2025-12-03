# app/api/v1/organizations/license_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models.user_models import Organization, User
from app.schemas.user import UserRole
from app.schemas.organization import OrganizationLicenseCreate, OrganizationLicenseResponse, LicenseExtendUpdate
from .services import OrganizationService

logger = logging.getLogger(__name__)

router = APIRouter()
license_router = router  # Alias for backward compatibility

@router.put("/{organization_id:int}/license")
async def update_organization_license(
    organization_id: int,
    license_data: LicenseExtendUpdate,
    auth: tuple = Depends(require_access("organization_license", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update organization license duration and expiry (requires organization_license update permission)"""
    current_user, org_id = auth
    
    # License operations can be cross-organization for super admins
    # But regular users can only update their own organization
    if organization_id != org_id and not getattr(current_user, 'is_super_admin', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    org_result = await db.execute(select(Organization).filter_by(id=organization_id))
    org = org_result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    license_type = license_data.license_type
    if license_type not in ["trial_7", "trial_15", "month_1", "month_3", "year_1", "perpetual", "custom"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="license_type must be one of: trial_7, trial_15, month_1, month_3, year_1, perpetual, custom"
        )
    
    if license_data.extend:
        base_date = org.license_expiry_date or datetime.utcnow()
    else:
        base_date = datetime.utcnow()
    
    org.license_type = license_type
    org.license_issued_date = datetime.utcnow()
    
    if license_type == "perpetual":
        org.license_duration_months = None
        org.license_expiry_date = None
    elif license_type == "month_1":
        org.license_duration_months = 1
        org.license_expiry_date = base_date + timedelta(days=30)
    elif license_type == "month_3":
        org.license_duration_months = 3
        org.license_expiry_date = base_date + timedelta(days=90)
    elif license_type == "year_1":
        org.license_duration_months = 12
        org.license_expiry_date = base_date + timedelta(days=365)
    elif license_type == "trial_7":
        org.license_duration_months = None
        org.license_expiry_date = base_date + timedelta(days=7)
    elif license_type == "trial_15":
        org.license_duration_months = None
        org.license_expiry_date = base_date + timedelta(days=15)
    elif license_type == "custom":
        if not license_data.custom_number or not license_data.custom_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_number and custom_unit required for custom type"
            )
        if license_data.custom_unit == 'days':
            delta = timedelta(days=license_data.custom_number)
        elif license_data.custom_unit == 'months':
            delta = timedelta(days=30 * license_data.custom_number)
        elif license_data.custom_unit == 'years':
            delta = timedelta(days=365 * license_data.custom_number)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_unit must be days, months, or years"
            )
        org.license_duration_months = None if license_data.custom_unit != 'months' else license_data.custom_number
        org.license_expiry_date = base_date + delta
    
    if not license_type.startswith("trial"):
        org.plan_type = "premium"
        org.status = "active"
    else:
        org.status = "trial"
    
    await db.commit()
    await db.refresh(org)
    
    license_status = "active" if not license_type.startswith("trial") else "trial"
    
    return {
        "message": "Organization license updated successfully",
        "organization_id": organization_id,
        "license_type": org.license_type,
        "license_status": license_status,
        "license_issued_date": org.license_issued_date.isoformat() if org.license_issued_date else None,
        "license_expiry_date": org.license_expiry_date.isoformat() if org.license_expiry_date else None,
        "license_duration_months": org.license_duration_months
    }

@router.get("/{organization_id:int}/license")
async def get_organization_license(
    organization_id: int,
    auth: tuple = Depends(require_access("organization_license", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization license information"""
    current_user, org_id = auth
    
    # Enforce tenant isolation
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    org_result = await db.execute(select(Organization).filter_by(id=organization_id))
    org = org_result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    is_expired = False
    if org.license_expiry_date and datetime.utcnow() > org.license_expiry_date:
        is_expired = True
    
    license_status = "trial" if org.license_type.startswith("trial") else "active"
    
    return {
        "organization_id": organization_id,
        "organization_name": org.name,
        "license_type": org.license_type or "trial",
        "license_status": license_status,
        "license_issued_date": org.license_issued_date.isoformat() if org.license_issued_date else None,
        "license_expiry_date": org.license_expiry_date.isoformat() if org.license_expiry_date else None,
        "license_duration_months": org.license_duration_months,
        "is_expired": is_expired,
        "plan_type": org.plan_type
    }

@router.post("/create", response_model=OrganizationLicenseResponse)
async def create_organization_license(
    license_data: OrganizationLicenseCreate,
    auth: tuple = Depends(require_access("organization_license", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new organization license (requires organization_license create permission)"""
    current_user, org_id = auth
    
    result = await OrganizationService.create_license(db, license_data, current_user)
    
    return result
