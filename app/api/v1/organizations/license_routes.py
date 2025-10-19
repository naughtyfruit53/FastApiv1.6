# app/api/v1/organizations/license_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models import Organization, User
from app.schemas.user import UserRole
from app.schemas import OrganizationLicenseCreate, OrganizationLicenseResponse
from .services import OrganizationService

logger = logging.getLogger(__name__)

router = APIRouter()
license_router = router  # Alias for backward compatibility

@router.put("/{organization_id:int}/license")
async def update_organization_license(
    organization_id: int,
    license_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization license duration and expiry (super admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can update organization licenses"
        )
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    license_type = license_data.get("license_type")
    if license_type not in ["trial", "month", "year", "perpetual"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="license_type must be one of: trial, month, year, perpetual"
        )
    
    org.license_type = license_type
    org.license_issued_date = datetime.utcnow()
    
    if license_type == "perpetual":
        org.license_duration_months = None
        org.license_expiry_date = None
    elif license_type == "month":
        org.license_duration_months = 1
        org.license_expiry_date = datetime.utcnow() + timedelta(days=30)
    elif license_type == "year":
        org.license_duration_months = 12
        org.license_expiry_date = datetime.utcnow() + timedelta(days=365)
    elif license_type == "trial":
        org.license_duration_months = 1
        org.license_expiry_date = datetime.utcnow() + timedelta(days=7)  # Changed to 7 days for trial
    
    if license_type != "trial":
        org.plan_type = "premium"
    
    db.commit()
    db.refresh(org)
    
    license_status = "active" if license_type != "trial" else "trial"
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization license information"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    is_expired = False
    if org.license_expiry_date and datetime.utcnow() > org.license_expiry_date:
        is_expired = True
    
    license_status = "trial" if org.license_type == "trial" else "active"
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new organization license (super admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can create organization licenses"
        )
    
    result = await OrganizationService.create_license(db, license_data, current_user)
    
    return result