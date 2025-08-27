# app/api/v1/organizations/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import PermissionChecker, Permission
from app.models import Organization, User, Product, Customer, Vendor, Stock
from app.schemas.user import UserRole
from app.schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationInDB,
    OrganizationLicenseCreate, OrganizationLicenseResponse,
    UserCreate, UserInDB
)
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.core.logging import log_license_creation, log_email_operation
from app.services.rbac import RBACService
from .services import OrganizationService
from .user_routes import user_router
from .invitation_routes import invitation_router
from .module_routes import module_router
from .license_routes import license_router

router = APIRouter(prefix="/organizations", tags=["organizations"])

router.include_router(user_router)
router.include_router(invitation_router)
router.include_router(module_router)
router.include_router(license_router)

@router.get("/", response_model=List[OrganizationInDB])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """List all organizations (super admin only)"""
    PermissionChecker.require_permission(Permission.VIEW_ORGANIZATIONS, current_user, db, request)
  
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations

@router.get("/current", response_model=OrganizationInDB)
async def get_current_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's organization"""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
  
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
  
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    return organization

@router.put("/current", response_model=OrganizationInDB)
async def update_current_organization(
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's organization (org admin only)"""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
  
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can update organization details"
        )
  
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
  
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    for field, value in org_update.dict(exclude_unset=True).items():
        if hasattr(organization, field):
            setattr(organization, field, value)
  
    try:
        db.commit()
        db.refresh(organization)
        return organization
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization"
        )

@router.get("/available-modules")
async def get_available_modules(
    current_user: User = Depends(get_current_user)
):
    """Get available modules in the application"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return OrganizationService.get_available_modules()

@router.get("/app-statistics")
async def get_app_level_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app-level statistics for super admins"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can access app-level statistics"
        )
    return OrganizationService.get_app_statistics(db)

@router.get("/org-statistics")
async def get_org_level_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get organization-level statistics for org admins/users"""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization context required for statistics"
        )
    return OrganizationService.get_org_statistics(db, current_user.organization_id)

@router.post("/factory-default")
async def factory_default_system(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Factory Default - App Super Admin only (complete system reset)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only app super administrators can perform factory default reset"
        )
    try:
        from app.services.reset_service import ResetService
        result = ResetService.factory_default_system(db)
        return {
            "message": "System has been reset to factory defaults successfully",
            "warning": "All organizations, users, and data have been permanently deleted",
            "details": result.get("deleted", {}),
            "system_state": "restored_to_initial_configuration"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform factory default reset. Please try again."
        )

@router.post("/", response_model=OrganizationInDB)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create new organization (Super admin only)"""
    PermissionChecker.require_permission(Permission.CREATE_ORGANIZATIONS, current_user, db, request)
  
    try:
        existing_org = db.query(Organization).filter(
            (Organization.name == org_data.name) |
            (Organization.subdomain == org_data.subdomain)
        ).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name or subdomain already exists"
            )
      
        new_org = Organization(**org_data.dict())
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        return new_org
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )

@router.post("/{organization_id}/join")
async def join_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Join an organization (must have permission)"""
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    if current_user.organization_id == organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )
  
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can join organizations without invitation"
        )
  
    try:
        current_user.organization_id = organization_id
        db.commit()
        db.refresh(current_user)
        return {"message": f"Successfully joined organization {org.name}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join organization"
        )

@router.get("/{organization_id}/members", response_model=List[UserInDB])
async def get_organization_members(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get organization members (org admin or super admin only)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view organization members"
        )
  
    members = db.query(User).filter(
        User.organization_id == organization_id,
        User.is_active == True
    ).offset(skip).limit(limit).all()
  
    return members

@router.post("/license/create", response_model=OrganizationLicenseResponse)
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
    
    result = OrganizationService.create_license(db, license_data, current_user)

    return result