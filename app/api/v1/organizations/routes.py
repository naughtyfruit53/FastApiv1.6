# app/api/v1/organizations/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Any, Optional
from datetime import datetime, timezone
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
from app.services.org_cache_service import (
    get_cached_organization, set_cached_organization, 
    get_cached_etag, invalidate_organization_cache
)

# Import RBACService lazily to avoid circular import
def get_rbac(db: AsyncSession = Depends(get_db)):
    from app.services.rbac import RBACService
    return RBACService(db)

# Import RBAC models from rbac_models
from app.models.rbac_models import UserServiceRole, ServiceRolePermission, ServiceRole
from app.core.modules_registry import get_default_enabled_modules

# Import for entitlements endpoint
from app.services.entitlement_service import EntitlementService
from app.schemas.entitlement_schemas import AppEntitlementsResponse, AppModuleEntitlement  # NEW: Added AppModuleEntitlement import to fix "name 'AppModuleEntitlement' is not defined" error

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
    response: Response,
    ts: Optional[str] = Query(None, description="Timestamp for cache busting"),
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's organization.
    
    Supports caching with ETag headers:
    - Returns ETag header with response
    - Supports If-None-Match header for conditional requests (returns 304 if unchanged)
    - Cache TTL: 60 seconds (server-side)
    """
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
            country="India",
            state_code="00",
            gst_number=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            enabled_modules={}
        )
    
    org_id = current_user.organization_id
    user_id = current_user.id
    
    # Check if client has valid cached version (ETag match)
    if if_none_match and not ts:  # ts=timestamp means force refresh
        cached_etag = get_cached_etag(org_id, user_id)
        if cached_etag and if_none_match == cached_etag:
            logger.debug(f"ETag match for org {org_id}, returning 304")
            response.status_code = status.HTTP_304_NOT_MODIFIED
            response.headers["ETag"] = cached_etag
            response.headers["Cache-Control"] = "private, max-age=30"
            return Response(status_code=304, headers={"ETag": cached_etag})
    
    # Try to get from cache (unless cache busting with ts parameter)
    if not ts:
        cached_data = get_cached_organization(org_id, user_id)
        if cached_data:
            etag = get_cached_etag(org_id, user_id)
            if etag:
                response.headers["ETag"] = etag
                response.headers["Cache-Control"] = "private, max-age=30"
            return OrganizationInDB(**cached_data)
  
    result = await db.execute(select(Organization).filter_by(id=current_user.organization_id))
    organization = result.scalars().first()
  
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # NEW: Check for missing required fields and raise 400 if incomplete (for non-super-admins)
    if not organization.state_code and not organization.gst_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company state code or GST number is missing. Please update in settings."
        )

    # Ensure enabled_modules is always populated with defaults if None/empty
    if not organization.enabled_modules or len(organization.enabled_modules) == 0:
        organization.enabled_modules = get_default_enabled_modules()
        await db.commit()
        await db.refresh(organization)
        logger.info(f"Populated default enabled_modules for organization {organization.id}")
    
    # Convert to dict for caching
    org_data = {
        'id': organization.id,
        'name': organization.name,
        'subdomain': organization.subdomain,
        'primary_email': organization.primary_email,
        'primary_phone': organization.primary_phone,
        'address1': organization.address1,
        'address2': getattr(organization, 'address2', None),
        'city': organization.city,
        'state': organization.state,
        'pin_code': organization.pin_code,
        'country': organization.country,
        'state_code': organization.state_code,
        'gst_number': organization.gst_number,
        'pan_number': getattr(organization, 'pan_number', None),
        'tan_number': getattr(organization, 'tan_number', None),
        'cin_number': getattr(organization, 'cin_number', None),
        'website': getattr(organization, 'website', None),
        'logo_url': getattr(organization, 'logo_url', None),
        'industry': getattr(organization, 'industry', None),
        'fiscal_year_start': str(getattr(organization, 'fiscal_year_start', '')) if getattr(organization, 'fiscal_year_start', None) else None,
        'fiscal_year_end': str(getattr(organization, 'fiscal_year_end', '')) if getattr(organization, 'fiscal_year_end', None) else None,
        'currency': getattr(organization, 'currency', 'INR'),
        'enabled_modules': organization.enabled_modules,
        'created_at': organization.created_at.isoformat() if organization.created_at else None,
        'updated_at': organization.updated_at.isoformat() if organization.updated_at else None,
    }
    
    # Cache the organization data and get ETag
    etag = set_cached_organization(org_id, user_id, org_data)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=30"
    
    logger.debug(f"Returning organization {organization.id} with ETag {etag}")
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


# NEW: Get current organization license info (normalized endpoint)
@router.get("/current/license")
async def get_current_organization_license(
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get license information for the current organization.
    
    Normalizes license data:
    - Removes duplicate trial entries if a paid plan exists
    - Shows start date (license_issued_date)
    - Shows 'Perpetual' if perpetual license, else shows renewal date
    """
    current_user, org_id = auth
    
    result = await db.execute(select(Organization).filter_by(id=org_id))
    org = result.scalars().first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Determine license status - if plan_type is not "basic" or "trial", consider it a paid plan
    is_perpetual = org.license_type == "perpetual"
    is_trial = org.license_type == "trial" or org.status == "trial"
    has_paid_plan = org.plan_type not in ["basic", "trial", None, ""]
    
    # If both trial status and paid plan exist, show only the paid plan (remove trial duplication)
    display_status = "active" if has_paid_plan else ("trial" if is_trial else "active")
    display_plan_type = org.plan_type if has_paid_plan else org.license_type
    
    # Calculate days remaining
    days_remaining = None
    if not is_perpetual and org.license_expiry_date:
        delta = org.license_expiry_date.date() - datetime.now(timezone.utc).date()
        days_remaining = delta.days
    
    # Determine renewal info
    renewal_date = None
    if is_perpetual:
        renewal_info = "Perpetual"
    elif org.license_expiry_date:
        renewal_info = org.license_expiry_date.isoformat()
        renewal_date = org.license_expiry_date
    else:
        renewal_info = None
    
    return {
        "organization_id": org_id,
        "organization_name": org.name,
        "license_type": display_plan_type,
        "license_status": display_status,
        "is_perpetual": is_perpetual,
        "is_trial": is_trial and not has_paid_plan,  # Only show trial if no paid plan
        "start_date": org.license_issued_date.isoformat() if org.license_issued_date else None,
        "renewal_date": renewal_date.isoformat() if renewal_date else None,
        "renewal_info": renewal_info,
        "days_remaining": days_remaining,
        "license_duration_months": org.license_duration_months,
        "max_users": org.max_users,
        "plan_type": org.plan_type
    }


# NEW: Get current organization overview stats (Total Users, Users Logged In Today, etc.)
@router.get("/current/overview")
async def get_current_organization_overview(
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization overview stats:
    - Total Users
    - Users Logged In Today
    - User Activity Rate
    - Inactive Users Today
    
    All stats are organization-scoped, not global.
    """
    current_user, org_id = auth
    
    # Get total users in organization
    total_users_result = await db.execute(
        select(func.count(User.id)).where(
            User.organization_id == org_id,
            User.is_active == True
        )
    )
    total_users = total_users_result.scalar_one() or 0
    
    # Get users logged in today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    logged_in_today_result = await db.execute(
        select(func.count(User.id)).where(
            User.organization_id == org_id,
            User.is_active == True,
            User.last_login >= today_start
        )
    )
    users_logged_in_today = logged_in_today_result.scalar_one() or 0
    
    # Calculate inactive users today (total - logged in today)
    inactive_users_today = total_users - users_logged_in_today
    
    # Calculate activity rate
    activity_rate = (users_logged_in_today / total_users * 100) if total_users > 0 else 0
    
    return {
        "organization_id": org_id,
        "total_users": total_users,
        "users_logged_in_today": users_logged_in_today,
        "inactive_users_today": inactive_users_today,
        "user_activity_rate": round(activity_rate, 2),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }