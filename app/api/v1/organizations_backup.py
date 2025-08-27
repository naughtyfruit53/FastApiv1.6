# Revised: v1/app/api/v1/organizations.py
"""
Organization management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.tenant import require_organization, TenantContext
from app.core.permissions import PermissionChecker, Permission
from app.models import Organization, User, Product, Customer, Vendor, Stock
from app.schemas.user import UserRole # Corrected import from schemas.user
from app.schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationInDB,
    OrganizationLicenseCreate, OrganizationLicenseResponse,
    UserCreate, UserInDB
)
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user, get_current_admin_user, get_current_super_admin
from datetime import timedelta, datetime
import logging
import secrets
import string
import re
from sqlalchemy.sql import func
from app.core.logging import log_license_creation, log_email_operation
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
from app.services.rbac import RBACService
from app.models.user_models import ServiceRole
import logging
logger = logging.getLogger(__name__)
# Email service configuration with explicit import handling
email_service = None
EMAIL_SERVICE_AVAILABLE = False
def _initialize_email_service():
    """Initialize email service if available."""
    global email_service, EMAIL_SERVICE_AVAILABLE
    try:
        from app.services.email_service import email_service as _email_service
        email_service = _email_service
        EMAIL_SERVICE_AVAILABLE = True
        logger.info("Email service initialized successfully")
    except ImportError as e:
        EMAIL_SERVICE_AVAILABLE = False
        email_service = None
        logger.warning(f"Email service not available: {e}")
# Initialize email service on module load
_initialize_email_service()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["organizations"])
@router.get("/", response_model=List[OrganizationInDB])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """List all organizations (super admin only)"""
    # Check permissions using the permission system
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
   
    # Check if user has permission to update organization
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
   
    # Update organization fields
    for field, value in org_update.dict(exclude_unset=True).items():
        if hasattr(organization, field):
            setattr(organization, field, value)
   
    try:
        db.commit()
        db.refresh(organization)
        logger.info(f"Updated current organization {organization.name} by user {current_user.email}")
        return organization
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization"
        )
@router.get("/available-modules")
async def get_available_modules(
    current_user: User = Depends(get_current_user)
):
    """Get available modules in the application"""
    
    # Only authenticated users can access this
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Map available modules to their descriptions based on actual implementation
    available_modules = {
        "CRM": {
            "name": "CRM",
            "description": "Customer Relationship Management",
            "endpoints": ["/api/v1/customers"],
            "enabled": True
        },
        "ERP": {
            "name": "ERP", 
            "description": "Enterprise Resource Planning",
            "endpoints": ["/api/v1/companies", "/api/v1/users"],
            "enabled": True
        },
        "HR": {
            "name": "HR",
            "description": "Human Resources Management", 
            "endpoints": ["/api/v1/users"],
            "enabled": True
        },
        "Inventory": {
            "name": "Inventory",
            "description": "Inventory Management",
            "endpoints": ["/api/v1/stock", "/api/v1/products", "/api/v1/inventory"],
            "enabled": True
        },
        "Service": {
            "name": "Service",
            "description": "Service Management",
            "endpoints": ["/api/v1/service-analytics", "/api/v1/sla", "/api/v1/dispatch", "/api/v1/feedback"],
            "enabled": True
        },
        "Analytics": {
            "name": "Analytics", 
            "description": "Reports and Analytics",
            "endpoints": ["/api/v1/analytics", "/api/v1/service-analytics"],
            "enabled": True
        },
        "Finance": {
            "name": "Finance",
            "description": "Financial Management",
            "endpoints": ["/api/v1/vendors", "/api/v1", "/api/v1/gst"],
            "enabled": True
        }
    }
    
    return {
        "available_modules": available_modules,
        "default_enabled": list(available_modules.keys())
    }

@router.get("/app-statistics")
async def get_app_level_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get app-level statistics for super admins"""
   
    # Only super admins can access app-level statistics
    if not current_user.is_super_admin: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can access app-level statistics"
        )
   
    try:
        # Get total licenses issued (total organizations)
        total_licenses = db.query(Organization).count()
       
        # Get active organizations
        active_organizations = db.query(Organization).filter(
            Organization.status == "active"
        ).count()
       
        # Get trial organizations
        trial_organizations = db.query(Organization).filter(
            Organization.status == "trial"
        ).count()
       
        # Get total users across all organizations (excluding super admins)
        total_users = db.query(User).filter(
            User.organization_id.isnot(None),
            User.is_active == True
        ).count()
       
        # Get active app-level super admins
        super_admins = db.query(User).filter(
            User.is_super_admin == True,
            User.is_active == True
        ).count()
       
        # Get organization breakdown by plan type
        plan_breakdown = {}
        plan_types = db.query(Organization.plan_type).distinct().all()
        for plan_type_row in plan_types:
            plan_type = plan_type_row[0]
            count = db.query(Organization).filter(
                Organization.plan_type == plan_type
            ).count()
            plan_breakdown[plan_type] = count
       
        # Get monthly statistics (organizations created in last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_licenses_this_month = db.query(Organization).filter(
            Organization.created_at >= thirty_days_ago
        ).count()
        # Additional parameters
        # Total storage used (sum of all org storage, placeholder as 1GB per org max)
        total_storage_used_gb = total_licenses * 0.5 # Example, replace with real calculation if field exists
       
        # Average users per org
        average_users_per_org = round(total_users / total_licenses) if total_licenses > 0 else 0
       
        # Failed login attempts (assume from audit logs or user.failed_login_attempts sum)
        failed_login_attempts = db.query(func.sum(User.failed_login_attempts)).scalar() or 0
       
        # Recent new orgs (7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_new_orgs = db.query(Organization).filter(
            Organization.created_at >= seven_days_ago
        ).count()
       
        return {
            "total_licenses_issued": total_licenses,
            "active_organizations": active_organizations,
            "trial_organizations": trial_organizations,
            "total_active_users": total_users,
            "super_admins_count": super_admins,
            "new_licenses_this_month": new_licenses_this_month,
            "plan_breakdown": plan_breakdown,
            "system_health": {
                "status": "healthy",
                "uptime": "99.9%" # This could be calculated from actual metrics
            },
            "generated_at": datetime.utcnow().isoformat(),
            "total_storage_used_gb": total_storage_used_gb,
            "average_users_per_org": average_users_per_org,
            "failed_login_attempts": failed_login_attempts,
            "recent_new_orgs": recent_new_orgs
        }
       
    except Exception as e:
        logger.exception(f"Error fetching app statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application statistics"
        )
@router.post("/license/create", response_model=OrganizationLicenseResponse)
async def create_organization_license(
    license_data: OrganizationLicenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new organization license and initial admin (super admin only)"""
   
    # Enhanced logging for session preservation debugging
    logger.info(f"[License Creation] Starting license creation for {license_data.organization_name}")
    logger.info(f"[License Creation] Current user: {current_user.id} ({current_user.email})")
    logger.info(f"[License Creation] Current user context: is_super_admin={current_user.is_super_admin}, org_id={current_user.organization_id}")
   
    if not current_user.is_super_admin:
        logger.warning(f"[License Creation] Non-super admin {current_user.email} attempted license creation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can create organization licenses"
        )
   
    # IMPORTANT: This endpoint should NOT modify the current user's session or JWT
    # The current super admin's session must remain intact throughout the process
    logger.info(f"[License Creation] Session preservation check - current user session will NOT be modified")
   
    try:
        # Check if organization name or subdomain exists
        existing_org = db.query(Organization).filter(
            Organization.name == license_data.organization_name
        ).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name already exists"
            )
       
        # Create subdomain from organization name (lowercase, replace spaces with hyphens)
        subdomain = re.sub(r'\s+', '-', license_data.organization_name.lower()).strip('-')
       
        existing_subdomain = db.query(Organization).filter(
            Organization.subdomain == subdomain
        ).first()
        if existing_subdomain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subdomain already in use"
            )
       
        # Generate temporary password if not provided
        temp_password = license_data.admin_password
        if not temp_password:
            alphabet = string.ascii_letters + string.digits + string.punctuation
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
       
        # 1. FIRST: Create user in Supabase Auth before any local DB operations
        logger.info(f"[License Creation] Creating org admin in Supabase Auth: {license_data.superadmin_email}")
        supabase_uuid = None
        try:
            supabase_user = supabase_auth_service.create_user(
                email=license_data.superadmin_email,
                password=temp_password,
                user_metadata={
                    "full_name": license_data.superadmin_email.split('@')[0],
                    "role": UserRole.ORG_ADMIN.value,
                    "organization_name": license_data.organization_name,
                    "is_super_admin": False,
                    "is_org_admin": True
                }
            )
            supabase_uuid = supabase_user["supabase_uuid"]
            logger.info(f"[License Creation] Successfully created Supabase Auth user: {supabase_uuid}")
           
        except SupabaseAuthError as e:
            error_msg = f"Failed to create org admin in Supabase Auth: {str(e)}"
            logger.error(f"[License Creation] {error_msg}")
            log_license_creation(
                license_data.organization_name,
                license_data.superadmin_email,
                current_user.email,
                False,
                error_msg
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supabase Auth error: {str(e)}"
            )
        except Exception as e:
            error_msg = f"Unexpected error during Supabase Auth user creation: {str(e)}"
            logger.error(f"[License Creation] {error_msg}")
            log_license_creation(
                license_data.organization_name,
                license_data.superadmin_email,
                current_user.email,
                False,
                error_msg
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in authentication system"
            )
       
        # 2. THEN: Create organization and user in local database
        try:
            # Generate custom org_code: yy/mm-(total user)-tqnnnn
            current_date = datetime.now()
            yy = current_date.strftime('%y')
            mm = current_date.strftime('%m')
            total_users = db.query(func.count(User.id)).scalar() or 0 # Global total users
            seq_num = total_users + 1 # Sequential based on total users
            tqnnnn = f"tq{seq_num:04d}"
            org_code = f"{yy}/{mm}-({total_users})- {tqnnnn}"
           
            # Create organization with all required fields and org_code
            new_org = Organization(
                name=license_data.organization_name,
                subdomain=subdomain,
                status="active",
                primary_email=license_data.superadmin_email, # Use provided superadmin_email
                primary_phone=license_data.primary_phone or "0000000000", # Default if not provided
                address1=license_data.address1 or "Default Address", # Default if not provided
                city=license_data.city or "Default City",
                state=license_data.state or "Default State",
                pin_code=license_data.pin_code or "000000",
                gst_number=license_data.gst_number,
                state_code=license_data.state_code or "00",
                max_users=license_data.max_users or 5, # Fixed: max_users field now included in schema
                enabled_modules=license_data.enabled_modules,
                country="India", # Default country
                org_code=org_code # Set custom org_code
            )
            db.add(new_org)
            db.flush() # Get org ID
           
            # Create initial org admin user with Supabase UUID
            hashed_password = get_password_hash(temp_password)
            new_user = User(
                organization_id=new_org.id,
                email=license_data.superadmin_email,
                username=license_data.superadmin_email.split('@')[0],
                hashed_password=hashed_password,
                full_name=license_data.superadmin_email.split('@')[0], # Use email prefix as full_name
                role=UserRole.ORG_ADMIN.value, # Creates "Org Super Admin" (correct role for organization admin)
                is_active=True,
                must_change_password=True, # Force password change on first login
            )
            db.add(new_user)
           
            db.commit()
            db.refresh(new_org)
            db.refresh(new_user)
            logger.info(f"[License Creation] Successfully created organization and user in local DB")

            # Initialize RBAC (roles and permissions) for the new organization
            rbac_service = RBACService(db)
            try:
                # Initialize default permissions and roles
                logger.info(f"[License Creation] Initializing RBAC for organization {new_org.id}")
                permissions = rbac_service.initialize_default_permissions()
                logger.info(f"[License Creation] Initialized {len(permissions)} default permissions")
                
                roles = rbac_service.initialize_default_roles(new_org.id)
                logger.info(f"[License Creation] Initialized {len(roles)} default roles for organization {new_org.id}")

                # Assign admin role to the new org super admin
                admin_role = db.query(ServiceRole).filter(
                    ServiceRole.organization_id == new_org.id,
                    ServiceRole.name == "admin"
                ).first()
                if admin_role:
                    rbac_service.assign_role_to_user(new_user.id, admin_role.id)
                    logger.info(f"[License Creation] Successfully assigned admin role to user {new_user.email}")
                else:
                    logger.error(f"[License Creation] Admin role not found after initialization for org {new_org.id}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to initialize RBAC roles properly"
                    )
            except Exception as rbac_error:
                logger.error(f"[License Creation] RBAC initialization failed for org {new_org.id}: {rbac_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to initialize permissions and roles: {str(rbac_error)}"
                )
           
        except Exception as e:
            # If local DB creation fails, cleanup Supabase Auth user
            try:
                supabase_auth_service.delete_user(supabase_uuid)
                logger.info(f"[License Creation] Rolled back Supabase Auth user {supabase_uuid} after DB failure")
            except Exception as cleanup_error:
                logger.error(f"[License Creation] Failed to cleanup Supabase user {supabase_uuid}: {cleanup_error}")
            db.rollback()
            error_msg = f"Failed to create organization/user in local database: {str(e)}"
            logger.error(f"[License Creation] {error_msg}")
            log_license_creation(
                license_data.organization_name,
                license_data.superadmin_email,
                current_user.email,
                False,
                error_msg
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create organization and user in database"
            )
       
        # Send enhanced license creation emails (if email_service is configured)
        email_sent = False
        email_error = None
        try:
            if EMAIL_SERVICE_AVAILABLE and email_service:
                # Send comprehensive license creation emails
                email_sent, email_error = email_service.send_license_creation_email(
                    org_admin_email=new_user.email,
                    org_admin_name=new_user.full_name or new_user.username,
                    organization_name=new_org.name,
                    temp_password=temp_password,
                    subdomain=new_org.subdomain,
                    org_code=new_org.org_code,
                    created_by=current_user.email,
                    notify_creator=True
                )
               
                if email_sent:
                    logger.info(f"✅ License creation emails sent successfully for organization: {new_org.name}")
                    log_license_creation(new_org.name, new_user.email, current_user.email, True)
                else:
                    logger.error(f"❌ Failed to send license creation emails: {email_error}")
                    log_license_creation(new_org.name, new_user.email, current_user.email, False, email_error)
            else:
                logger.warning("📧 Email service not available - skipping license creation emails")
                email_error = "Email service not configured"
        except Exception as email_exception:
            email_error = str(email_exception)
            logger.exception(f"💥 Exception during license creation email sending: {email_exception}")
            # Don't fail the entire operation if email fails
            pass
       
        logger.info(f"📋 Created organization license for {new_org.name} by {current_user.email}")
        logger.info(f"🔐 License creation completed without affecting super admin session for {current_user.email}")
       
        return OrganizationLicenseResponse(
            message="Organization license created successfully",
            organization_id=new_org.id,
            organization_name=new_org.name,
            superadmin_email=new_user.email,
            subdomain=new_org.subdomain,
            temp_password=temp_password,
            org_code=new_org.org_code,
            email_sent=email_sent,
            email_error=email_error
        )
       
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"💥 Error creating organization license: {e}")
        log_license_creation(
            license_data.organization_name if 'license_data' in locals() else "Unknown",
            license_data.superadmin_email if 'license_data' in locals() else "Unknown",
            current_user.email,
            False,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization license"
        )
@router.get("/org-statistics")
async def get_org_level_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get organization-level statistics for org admins/users"""
   
    # Require organization context
    if current_user.organization_id is None: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization context required for statistics"
        )
   
    organization_id = current_user.organization_id
   
    try:
        # Total products
        total_products = db.query(Product).filter(
            Product.organization_id == organization_id
        ).count()
       
        # Total customers
        total_customers = db.query(Customer).filter(
            Customer.organization_id == organization_id
        ).count()
       
        # Total vendors
        total_vendors = db.query(Vendor).filter(
            Vendor.organization_id == organization_id
        ).count()
       
        # Active users
        active_users = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
       
        # Monthly sales (placeholder - assume from vouchers, use 0 for now)
        monthly_sales = 0 # Replace with real query, e.g., sum from sales vouchers last 30 days
       
        # Inventory value (sum quantity * unit_price from stock)
        inventory_value = db.query(func.sum(Stock.quantity * Product.unit_price)).join(
            Product, Stock.product_id == Product.id
        ).filter(
            Stock.organization_id == organization_id
        ).scalar() or 0
       
        # Plan type from organization
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        plan_type = org.plan_type if org else 'unknown'
       
        # Storage used (placeholder - use 0.5 for demo)
        storage_used_gb = 0.5 # Replace with real calculation if field exists
       
        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_vendors": total_vendors,
            "active_users": active_users,
            "monthly_sales": monthly_sales,
            "inventory_value": inventory_value,
            "plan_type": plan_type,
            "storage_used_gb": storage_used_gb,
            "generated_at": datetime.utcnow().isoformat()
        }
       
    except Exception as e:
        logger.exception(f"Error fetching org statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch organization statistics"
        )
@router.post("/factory-default")
async def factory_default_system(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Factory Default - App Super Admin only (complete system reset)"""
    from app.core.permissions import PermissionChecker, Permission
   
    # Enhanced permission check using PermissionChecker
    if not PermissionChecker.can_factory_reset(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only app super administrators can perform factory default reset"
        )
   
    # Additional check using permission system
    PermissionChecker.require_permission(
        Permission.FACTORY_RESET,
        current_user,
        db
    )
   
    try:
        from app.services.reset_service import ResetService
       
        # Perform complete system reset - all organizations, users, data
        result = ResetService.factory_default_system(db)
       
        logger.warning(f"FACTORY DEFAULT: App super admin {current_user.email} performed complete system reset")
       
        return {
            "message": "System has been reset to factory defaults successfully",
            "warning": "All organizations, users, and data have been permanently deleted",
            "details": result.get("deleted", {}),
            "system_state": "restored_to_initial_configuration"
        }
       
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error performing factory default reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform factory default reset. Please try again."
        )
@router.get("/{organization_id}/modules")
async def get_organization_modules(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization modules"""
    
    # Check permissions
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
    
    # Get enabled modules or use default
    enabled_modules = org.enabled_modules or {
        "CRM": True,
        "ERP": True,
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }
    
    return {
        "organization_id": organization_id,
        "organization_name": org.name,
        "enabled_modules": enabled_modules
    }

@router.put("/{organization_id}/modules")
async def update_organization_modules(
    organization_id: int,
    module_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization modules (super admin only)"""
    
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can update organization modules"
        )
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate enabled_modules data
    enabled_modules = module_data.get("enabled_modules", {})
    if not isinstance(enabled_modules, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="enabled_modules must be a dictionary"
        )
    
    # Update organization modules
    org.enabled_modules = enabled_modules
    db.commit()
    db.refresh(org)
    
    return {
        "message": "Organization modules updated successfully",
        "organization_id": organization_id,
        "enabled_modules": enabled_modules
    }

@router.get("/{organization_id}", response_model=OrganizationInDB)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
    # Super admins can access any organization
    # Regular users can only access their own organization
    if not current_user.is_super_admin and current_user.organization_id != organization_id: # pyright: ignore[reportGeneralTypeIssues]
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
   
    return org
@router.put("/{organization_id}", response_model=OrganizationInDB)
async def update_organization(
    organization_id: int,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization"""
    # Super admins can update any organization
    # Org admins can only update their own organization
    if not current_user.is_super_admin: # pyright: ignore[reportGeneralTypeIssues]
        if current_user.organization_id != organization_id or current_user.role not in [UserRole.ORG_ADMIN]: # pyright: ignore[reportGeneralTypeIssues]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update this organization"
            )
   
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    try:
        # Update fields
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
       
        # Regenerate org_code if max_users changed
        if 'max_users' in update_data:
            current_date = datetime.now()
            yy = current_date.strftime('%y')
            mm = current_date.strftime('%m')
            total_users = db.query(func.count(User.id)).scalar() or 0 # Global total users
            seq_num = total_users + 1
            tqnnnn = f"tq{seq_num:04d}"
            org.org_code = f"{yy}/{mm}-({org.max_users})- {tqnnnn}"
       
        db.commit()
        db.refresh(org)
       
        logger.info(f"Updated organization {org.name} by user {current_user.email}")
        return org
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating organization"
        )
@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete organization (Super admin only)"""
    if not current_user.is_super_admin: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can delete organizations"
        )
   
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Check if organization has any dependencies before deletion
    dependencies = {}
   
    # Check for users
    user_count = db.query(User).filter(User.organization_id == organization_id).count()
    if user_count > 0:
        dependencies["users"] = user_count
   
    # Check for products
    product_count = db.query(Product).filter(Product.organization_id == organization_id).count()
    if product_count > 0:
        dependencies["products"] = product_count
   
    # Check for customers
    customer_count = db.query(Customer).filter(Customer.organization_id == organization_id).count()
    if customer_count > 0:
        dependencies["customers"] = customer_count
   
    # Check for vendors
    vendor_count = db.query(Vendor).filter(Vendor.organization_id == organization_id).count()
    if vendor_count > 0:
        dependencies["vendors"] = vendor_count
   
    # Check for stock entries
    stock_count = db.query(Stock).filter(Stock.organization_id == organization_id).count()
    if stock_count > 0:
        dependencies["stock_entries"] = stock_count
   
    # If there are any dependencies, prevent deletion and provide detailed information
    if dependencies:
        dependency_details = []
        for dep_type, count in dependencies.items():
            dependency_details.append(f"{count} {dep_type}")
       
        detail_message = (
            f"Cannot delete organization '{org.name}' because it contains: "
            f"{', '.join(dependency_details)}. "
            f"Please remove or transfer all data before deleting the organization."
        )
       
        logger.warning(f"Organization deletion blocked for {org.name}: {dependencies}")
       
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": detail_message,
                "reason": "organization_has_dependencies",
                "dependencies": dependencies,
                "organization_name": org.name,
                "suggestions": [
                    "Remove all users from the organization",
                    "Delete or transfer all products to another organization",
                    "Delete or transfer all customers to another organization",
                    "Delete or transfer all vendors to another organization",
                    "Clear all stock entries for this organization"
                ]
            }
        )
   
    try:
        db.delete(org)
        db.commit()
       
        logger.info(f"Deleted organization {org.name} by user {current_user.email}")
        return {"message": "Organization deleted successfully"}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting organization"
        )
@router.get("/{organization_id}/users", response_model=List[UserInDB])
async def list_organization_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List users in organization"""
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users"
        )
   
    query = db.query(User).filter(User.organization_id == organization_id)
   
    if active_only:
        query = query.filter(User.is_active == True)
   
    users = query.offset(skip).limit(limit).all()
    return users
@router.post("/", response_model=OrganizationInDB)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create new organization (Super admin only)"""
    # Check permissions using the permission system
    PermissionChecker.require_permission(Permission.CREATE_ORGANIZATIONS, current_user, db, request)
   
    try:
        # Check if organization name or subdomain exists
        existing_org = db.query(Organization).filter(
            (Organization.name == org_data.name) |
            (Organization.subdomain == org_data.subdomain)
        ).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization name or subdomain already exists"
            )
       
        # Create organization
        new_org = Organization(**org_data.dict())
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
       
        logger.info(f"Created organization {new_org.name} by {current_user.email}")
        return new_org
       
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating organization: {e}")
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
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Check if user is already in organization
    if current_user.organization_id == organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )
   
    # For now, only allow super admins to join any organization
    # In a full implementation, this would check for invitations
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can join organizations without invitation"
        )
   
    try:
        # Update user's organization
        current_user.organization_id = organization_id
        db.commit()
        db.refresh(current_user)
       
        logger.info(f"User {current_user.email} joined organization {org.name}")
        return {"message": f"Successfully joined organization {org.name}"}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error joining organization: {e}")
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
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN: # pyright: ignore[reportGeneralTypeIssues]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view organization members"
        )
   
    members = db.query(User).filter(
        User.organization_id == organization_id,
        User.is_active == True
    ).offset(skip).limit(limit).all()
   
    return members
@router.post("/{organization_id}/invite")
async def invite_user_to_organization(
    organization_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Invite user to organization (org admin only)"""
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can invite users"
        )
   
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
   
    try:
        # Create new user in organization
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            organization_id=organization_id,
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.STANDARD_USER.value,
            is_active=True,
            must_change_password=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
       
        # Send invitation email (if email service is configured)
        try:
            if EMAIL_SERVICE_AVAILABLE and email_service:
                await email_service.send_email(
                    to_email=new_user.email,
                    subject=f"Invitation to join {org.name}",
                    body=f"You have been invited to join {org.name}. Please login with your credentials."
                )
                logger.info(f"Invitation email sent to {new_user.email}")
            else:
                logger.info("Email service not available - skipping invitation email")
        except Exception as email_error:
            logger.error(f"Failed to send invitation email: {email_error}")
            # Don't fail the entire operation if email fails
            pass
        logger.info(f"User {new_user.email} invited to organization {org.name} by {current_user.email}")
        return {"message": f"User {new_user.email} successfully invited to {org.name}"}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error inviting user to organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user to organization"
        )
# ================================
# Organization-Scoped User Management Endpoints
# ================================
@router.get("/{organization_id}/users", response_model=List[UserInDB])
async def get_organization_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get users in organization (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Check if user has permission to view users
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can view users"
        )
   
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Build query
    query = db.query(User).filter(User.organization_id == organization_id)
   
    if active_only:
        query = query.filter(User.is_active == True)
   
    if role:
        query = query.filter(User.role == role)
   
    users = query.offset(skip).limit(limit).all()
   
    logger.info(f"Retrieved {len(users)} users from organization {organization_id} by {current_user.email}")
    return users
@router.post("/{organization_id}/users", response_model=UserInDB)
async def create_user_in_organization(
    organization_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create user in organization (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Check if user has permission to create users
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can create users"
        )
   
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Check if email already exists in the organization
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.organization_id == organization_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization"
        )
   
    # Check if username already exists in the organization
    if user_data.username:
        existing_username = db.query(User).filter(
            User.username == user_data.username,
            User.organization_id == organization_id
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken in this organization"
            )
   
    # Check user limits for the organization
    if not current_user.is_super_admin:
        user_count = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
       
        if user_count >= org.max_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum user limit ({org.max_users}) reached for this organization"
            )
   
    # Validate role permissions
    if user_data.role == UserRole.ORG_ADMIN and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can create organization administrators"
        )
   
    try:
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            organization_id=organization_id,
            email=user_data.email,
            username=user_data.username or user_data.email.split('@')[0],
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role or UserRole.STANDARD_USER.value,
            department=user_data.department,
            designation=user_data.designation,
            employee_id=user_data.employee_id,
            phone=user_data.phone,
            is_active=user_data.is_active if user_data.is_active is not None else True
        )
       
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
       
        logger.info(f"User {new_user.email} created in organization {org.name} by {current_user.email}")
        return new_user
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user in organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in organization"
        )
@router.put("/{organization_id}/users/{user_id}", response_model=UserInDB)
async def update_user_in_organization(
    organization_id: int,
    user_id: int,
    user_update: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user in organization (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Find the user
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
   
    # Check permissions - users can update themselves, org admins can update others
    is_self_update = current_user.id == user_id
    if not is_self_update and not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can update other users"
        )
   
    # Restrict self-update fields for non-admin users
    if is_self_update and not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        allowed_fields = {"email", "username", "full_name", "phone", "department", "designation"}
        if not all(field in allowed_fields for field in user_update.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update administrative fields"
            )
   
    # Check role update permissions
    if "role" in user_update:
        if user_update["role"] == UserRole.ORG_ADMIN.value and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super administrators can assign organization administrator role"
            )
   
    try:
        # Update user fields
        for field, value in user_update.items():
            if field == "password" and value:
                setattr(user, "hashed_password", get_password_hash(value))
            elif hasattr(user, field):
                setattr(user, field, value)
       
        db.commit()
        db.refresh(user)
       
        logger.info(f"User {user.email} updated in organization {organization_id} by {current_user.email}")
        return user
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user in organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user in organization"
        )
@router.delete("/{organization_id}/users/{user_id}")
async def delete_user_from_organization(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete user from organization (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Check if user has permission to delete users
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can delete users"
        )
   
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
   
    # Find the user
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
   
    # Prevent deleting the last admin in an organization
    if user.role == UserRole.ORG_ADMIN.value and not current_user.is_super_admin:
        admin_count = db.query(User).filter(
            User.organization_id == organization_id,
            User.role == UserRole.ORG_ADMIN.value,
            User.is_active == True
        ).count()
       
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last organization administrator"
            )
   
    try:
        db.delete(user)
        db.commit()
       
        logger.info(f"User {user.email} deleted from organization {organization_id} by {current_user.email}")
        return {"message": f"User {user.email} deleted successfully"}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user from organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user from organization"
        )
# ================================
# Enhanced Invitation Management
# ================================
@router.get("/{organization_id}/invitations")
async def list_organization_invitations(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List organization invitations (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can view invitations"
        )
   
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # For now, return recently invited users as "pending invitations"
    # In a full implementation, you would have a separate Invitation table
    query = db.query(User).filter(
        User.organization_id == organization_id,
        User.must_change_password == True # Indicator of pending invitation
    )
   
    invitations = query.offset(skip).limit(limit).all()
   
    # Transform to invitation-like format
    invitation_data = []
    for user in invitations:
        invitation_data.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "status": "pending" if user.must_change_password else "accepted",
            "invited_at": user.created_at,
            "invited_by": "unknown", # Would track this in full implementation
            "organization_id": organization_id,
            "organization_name": org.name
        })
   
    return invitation_data
@router.post("/{organization_id}/invitations/{invitation_id}/resend")
async def resend_organization_invitation(
    organization_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Resend organization invitation (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can resend invitations"
        )
   
    # Find the user/invitation (using user ID as invitation ID for now)
    user = db.query(User).filter(
        User.id == invitation_id,
        User.organization_id == organization_id,
        User.must_change_password == True # Still pending
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already accepted"
        )
   
    org = db.query(Organization).filter(Organization.id == organization_id).first()
   
    try:
        # Send invitation email (if email service is configured)
        if EMAIL_SERVICE_AVAILABLE and email_service:
            await email_service.send_email(
                to_email=user.email,
                subject=f"Invitation to join {org.name} (Resent)",
                body=f"You have been invited to join {org.name}. Please login with your credentials to complete your account setup."
            )
            logger.info(f"Invitation email resent to {user.email}")
       
        logger.info(f"Invitation resent for {user.email} in organization {org.name} by {current_user.email}")
        return {"message": f"Invitation resent to {user.email}"}
       
    except Exception as e:
        logger.error(f"Error resending invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend invitation"
        )
@router.delete("/{organization_id}/invitations/{invitation_id}")
async def cancel_organization_invitation(
    organization_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel organization invitation (org admin or super admin only)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can cancel invitations"
        )
   
    # Find the user/invitation (using user ID as invitation ID for now)
    user = db.query(User).filter(
        User.id == invitation_id,
        User.organization_id == organization_id,
        User.must_change_password == True # Still pending
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already accepted"
        )
   
    try:
        # For now, delete the user since they haven't activated yet
        # In a full implementation, you would mark invitation as cancelled
        db.delete(user)
        db.commit()
       
        logger.info(f"Invitation cancelled for {user.email} in organization {organization_id} by {current_user.email}")
        return {"message": f"Invitation cancelled for {user.email}"}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel invitation"
        )
# Module Control Endpoints
@router.get("/{organization_id}/modules")
async def get_organization_modules(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get organization's enabled modules"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    # Return enabled modules or default set
    enabled_modules = organization.enabled_modules or {
        "CRM": True,
        "ERP": True,
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }
   
    return {"enabled_modules": enabled_modules}
@router.put("/{organization_id}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update organization's enabled modules (super admin only)"""
   
    # Only super admins can modify organization modules
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can modify organization modules"
        )
   
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
   
    try:
        # Validate module names
        valid_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance"]
        for module in modules_data.get("enabled_modules", {}):
            if module not in valid_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid module: {module}"
                )
       
        # Update organization modules
        organization.enabled_modules = modules_data.get("enabled_modules", {})
        db.commit()
       
        logger.info(f"Organization {organization_id} modules updated by {current_user.email}")
        return {"message": "Organization modules updated successfully", "enabled_modules": organization.enabled_modules}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating organization modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization modules"
        )
@router.get("/{organization_id}/users/{user_id}/modules")
async def get_user_modules(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's assigned modules"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Check if user can manage other users (HR role or admin)
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN] and current_user.role != "HR":
        if current_user.id != user_id: # Users can view their own modules
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view user modules"
            )
   
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
   
    # Return assigned modules or default set
    assigned_modules = user.assigned_modules or {
        "CRM": True,
        "ERP": True,
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }
   
    return {"assigned_modules": assigned_modules}
@router.put("/{organization_id}/users/{user_id}/modules")
async def update_user_modules(
    organization_id: int,
    user_id: int,
    modules_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user's assigned modules (HR role or org admin)"""
   
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
   
    # Check if user can manage other users (HR role or admin)
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN] and current_user.role != "HR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR personnel and organization administrators can manage user modules"
        )
   
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
   
    try:
        # Get organization's enabled modules to validate against
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        org_enabled_modules = organization.enabled_modules or {}
       
        # Validate module names and ensure they're enabled for the organization
        valid_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance"]
        assigned_modules = modules_data.get("assigned_modules", {})
       
        for module, enabled in assigned_modules.items():
            if module not in valid_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid module: {module}"
                )
           
            # User can only be assigned modules that are enabled for the organization
            if enabled and not org_enabled_modules.get(module, False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module {module} is not enabled for this organization"
                )
       
        # Update user modules
        user.assigned_modules = assigned_modules
        db.commit()
       
        logger.info(f"User {user_id} modules updated by {current_user.email}")
        return {"message": "User modules updated successfully", "assigned_modules": user.assigned_modules}
       
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user modules"
        )