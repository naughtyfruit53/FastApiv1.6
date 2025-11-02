# app/api/v1/organizations/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Any, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import PermissionChecker, Permission, require_platform_permission
from app.core.enforcement import require_access
from app.models.user_models import User, Organization
from app.schemas.user import UserRole, UserInDB
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationInDB,
    OrganizationLicenseCreate, OrganizationLicenseResponse
)
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.core.logging import log_license_creation, log_email_operation
from .services import OrganizationService
from .user_routes import user_router
from .invitation_routes import invitation_router
from .module_routes import module_router
from .license_routes import license_router
from .settings_routes import router as settings_router
from app.services.otp_service import OTPService
from app.schemas.reset import OTPRequest, OTPVerify
from app.scripts.seed_default_coa_accounts import create_default_accounts  # Fixed import

# Import RBACService lazily to avoid circular import
def get_rbac(db: AsyncSession = Depends(get_db)):
    from app.services.rbac import RBACService
    return RBACService(db)

# Import RBAC models from rbac_models
from app.models.rbac_models import UserServiceRole, ServiceRolePermission, ServiceRole
from app.core.modules_registry import get_default_enabled_modules

# Import for entitlements endpoint
from app.services.entitlement_service import EntitlementService
from app.schemas.entitlement_schemas import AppEntitlementsResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["organizations"])

router.include_router(user_router)
router.include_router(invitation_router)
router.include_router(module_router)
router.include_router(license_router)
router.include_router(settings_router)

@router.get("/", response_model=List[OrganizationInDB])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(require_platform_permission(Permission.VIEW_ORGANIZATIONS)),
    request: Request = None
):
    """List all organizations (super admin only)"""
  
    result = await db.execute(select(Organization).offset(skip).limit(limit))
    organizations = result.scalars().all()
    return organizations

@router.get("/current", response_model=OrganizationInDB)
async def get_current_organization(
    ts: Optional[str] = Query(None, description="Timestamp for cache busting"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's organization"""
    if current_user.organization_id is None:
        # For super admins (post-reset), return a placeholder empty organization
        return OrganizationInDB(
            id=0,
            name="Global Super Admin",
            subdomain="superadmin",
            primary_email="superadmin@example.com",
            primary_phone="0000000000",
            address1="Super Admin Address",
            city="Global",
            state="Global",
            pin_code="123456",
            gst_number=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            enabled_modules={}
        )
  
    result = await db.execute(select(Organization).filter_by(id=current_user.organization_id))
    organization = result.scalars().first()
  
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Ensure enabled_modules is always populated with defaults if None/empty
    if not organization.enabled_modules or len(organization.enabled_modules) == 0:
        organization.enabled_modules = get_default_enabled_modules()
        await db.commit()
        await db.refresh(organization)
        logger.info(f"Populated default enabled_modules for organization {organization.id}")
  
    logger.info(f"Returning enabled_modules for org {organization.id}: {organization.enabled_modules}")  # Debug log
    return organization

@router.put("/current", response_model=OrganizationInDB)
async def update_current_organization(
    org_update: OrganizationUpdate,
    auth: tuple = Depends(require_access("organization", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's organization (org admin permission required)"""
    current_user, org_id = auth
    
    result = await db.execute(select(Organization).filter_by(id=org_id))
    organization = result.scalars().first()
  
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    update_data = org_update.dict(exclude_unset=True)
    logger.info(f"Updating organization {organization.id} with fields: {list(update_data.keys())}")
    
    for field, value in update_data.items():
        if hasattr(organization, field):
            setattr(organization, field, value)
            logger.debug(f"Set {field} = {value}")
        else:
            logger.warning(f"Field {field} not found on Organization model")
  
    try:
        await db.commit()
        await db.refresh(organization)
        logger.info(f"Successfully updated organization {organization.id}. GST: {organization.gst_number}, State Code: {organization.state_code}")
        return organization
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update organization {organization.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get app-level statistics (admin permission required)"""
    if current_user.organization_id is None and current_user.is_super_admin:
        # Super admin with no organization: proceed with global statistics
        return await OrganizationService.get_app_statistics(db)
    
    # For non-super admins, restrict access
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can access app-level statistics"
        )
    
    return await OrganizationService.get_app_statistics(db)

@router.get("/org-statistics")
async def get_org_level_statistics(
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization-level statistics (org permission required)"""
    current_user, org_id = auth
    return await OrganizationService.get_org_statistics(db, org_id)

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = 10,
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activities for the organization"""
    current_user, org_id = auth
    return await OrganizationService.get_recent_activities(db, org_id, limit)

@router.post("/factory-default")
async def factory_default_system(
    auth: tuple = Depends(require_access("organization", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Factory Default - Requires organization delete permission (complete system reset)"""
    current_user, org_id = auth
    # Extra check for super admin for this critical operation
    if not getattr(current_user, 'is_super_admin', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    try:
        from app.services.reset_service import ResetService
        result = await ResetService.factory_default_system(db, current_user)
        return {
            "message": "System has been reset to factory defaults successfully",
            "warning": "All organizations, users, and data have been permanently deleted",
            "details": result.get("deleted", {}),
            "system_state": "restored_to_initial_configuration"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform factory default reset. Please try again."
        )

@router.post("/", response_model=OrganizationInDB)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(require_platform_permission(Permission.CREATE_ORGANIZATIONS))
):
    """Create new organization (Super admin only)"""
  
    try:
        result = await db.execute(select(Organization).where(
            or_(Organization.name == org_data.name, Organization.subdomain == org_data.subdomain)
        ))
        existing_org = result.scalars().first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name or subdomain already exists"
            )
      
        new_org = Organization(**org_data.dict())
        db.add(new_org)
        await db.commit()
        await db.refresh(new_org)
        
        # Seed standard chart of accounts for the new organization
        create_default_accounts(db, new_org.id)
        
        return new_org
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )

@router.post("/{organization_id}/join")
async def join_organization(
    organization_id: int,
    auth: tuple = Depends(require_access("organization", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Join an organization (requires organization update permission)"""
    current_user, org_id = auth
    
    result = await db.execute(select(Organization).filter_by(id=organization_id))
    org = result.scalars().first()
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
  
    # Extra check for super admin for cross-org operations
    if not getattr(current_user, 'is_super_admin', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    try:
        current_user.organization_id = organization_id
        await db.commit()
        await db.refresh(current_user)
        return {"message": f"Successfully joined organization {org.name}"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join organization"
        )

@router.get("/{organization_id}/members", response_model=List[UserInDB])
async def get_organization_members(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization members (org admin permission required)"""
    current_user, org_id = auth
    
    # Enforce tenant isolation - can only view members of own organization
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    result = await db.execute(
        select(User).filter_by(organization_id=organization_id, is_active=True).offset(skip).limit(limit)
    )
    members = result.scalars().all()
  
    return members

@router.post("/license/create", response_model=OrganizationLicenseResponse)
async def create_organization_license(
    license_data: OrganizationLicenseCreate,
    auth: tuple = Depends(require_access("organization", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new organization license (organization create permission required)"""
    current_user, org_id = auth
    
    result = await OrganizationService.create_license(db, license_data, current_user)

    return result

@router.post("/reset-data/request-otp")
async def request_reset_otp(
    request: OTPRequest,
    auth: tuple = Depends(require_access("organization", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Request OTP for organization data reset (requires organization delete permission)"""
    current_user, org_id = auth
  
    try:
        otp_service = OTPService(db)
        otp = otp_service.generate_and_send_otp(current_user.email, "reset_data", organization_id=org_id)
        return {"message": "OTP sent to your email. Please verify to proceed with data reset."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )

@router.post("/reset-data/verify-otp")
async def verify_reset_otp_and_reset(
    verify_data: OTPVerify,
    auth: tuple = Depends(require_access("organization", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Verify OTP and perform organization data reset (requires organization delete permission)"""
    current_user, org_id = auth
  
    try:
        otp_service = OTPService(db)
        if not otp_service.verify_otp(current_user.email, verify_data.otp, "reset_data"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        from app.services.org_reset_service import OrgResetService
        result = await OrgResetService.reset_organization_business_data(db, org_id)
        return {
            "message": "Organization data has been reset successfully",
            "details": result.get("deleted", {}),
            "organization_state": "business_data_cleared"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset organization data. Please try again."
        )

@router.post("/reset-data")
async def reset_organization_data(
    auth: tuple = Depends(require_access("organization", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Reset organization business data (requires organization delete permission)"""
    current_user, org_id = auth
  
    try:
        from app.services.org_reset_service import OrgResetService
        result = await OrgResetService.reset_organization_business_data(db, org_id)
        return {
            "message": "Organization data has been reset successfully",
            "details": result.get("deleted", {}),
            "organization_state": "business_data_cleared"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset organization data. Please try again."
        )

# NEW: Non-admin endpoint to fetch current org entitlements
@router.get("/entitlements", response_model=AppEntitlementsResponse)
async def get_entitlements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get entitlements for the current organization (org admin or super admin)"""
    if current_user.organization_id is None:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # For super admin with null org_id, return all enabled as placeholder
        from app.core.modules_registry import get_default_enabled_modules
        return AppEntitlementsResponse(
            org_id=0,
            entitlements={
                k.lower(): AppModuleEntitlement(
                    module_key=k.lower(),
                    status='enabled',
                    submodules={}
                ) for k in get_default_enabled_modules()
            }
        )

    service = EntitlementService(db)
    return await service.get_app_entitlements(current_user.organization_id)