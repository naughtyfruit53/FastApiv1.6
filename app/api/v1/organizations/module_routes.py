# app/api/v1/organizations/module_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.enforcement import require_access
from app.api.v1.auth import get_current_active_user
from app.models import Organization, User, Product, Customer, Vendor, Stock
from app.schemas.user import UserRole
from app.schemas import OrganizationUpdate, OrganizationInDB
import logging
from app.utils.supabase_auth import supabase_auth_service
from app.models.rbac_models import UserServiceRole, ServiceRolePermission, ServiceRole  # Changed to absolute from rbac_models

from sqlalchemy import select, delete, func  # Added imports for async queries
from app.core.tenant import TenantContext  # Added import for TenantContext

logger = logging.getLogger(__name__)

router = APIRouter()
module_router = router  # Alias for backward compatibility

# Cache sorted valid modules at module level to avoid repeated sorting
_VALID_MODULES_SORTED = None

def get_sorted_valid_modules():
    """Get cached sorted list of valid modules"""
    global _VALID_MODULES_SORTED
    if _VALID_MODULES_SORTED is None:
        from app.core.modules_registry import get_all_modules
        _VALID_MODULES_SORTED = sorted(get_all_modules())
    return _VALID_MODULES_SORTED

@router.get("/{organization_id:int}/modules")
async def get_organization_modules(
    organization_id: int,
    auth: tuple = Depends(require_access("organization_module", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization's enabled modules.
    Returns both enabled modules and list of all available modules in the system.
    """
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can access any organization by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    organization = result.scalars().first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    from app.core.modules_registry import get_default_enabled_modules, get_all_modules
    
    enabled_modules = organization.enabled_modules or get_default_enabled_modules()
    available_modules = get_all_modules()
  
    return {
        "enabled_modules": enabled_modules,
        "available_modules": available_modules,
        "organization_id": organization_id,
        "organization_name": organization.name
    }

@router.put("/{organization_id:int}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    auth: tuple = Depends(require_access("organization_module", "update")),
    db: AsyncSession = Depends(get_db)
):
    """
    Update organization's enabled modules (requires organization_module update permission).
    Idempotent - can be called multiple times with same data.
    
    Request body format:
    {
        "enabled_modules": {
            "CRM": true,
            "ERP": false,
            "Finance": true,
            ...
        }
    }
    """
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can update any organization's modules by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    organization = result.scalars().first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    try:
        from app.core.modules_registry import get_all_modules
        
        # Validate request body structure
        if "enabled_modules" not in modules_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing 'enabled_modules' in request body. Expected format: {'enabled_modules': {'ModuleName': true/false}}"
            )
        
        enabled_modules = modules_data.get("enabled_modules", {})
        
        # Validate that enabled_modules is a dict
        if not isinstance(enabled_modules, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="'enabled_modules' must be a dictionary mapping module names to boolean values"
            )
        
        valid_modules = get_all_modules()
        invalid_modules = []
        
        # Validate each module key
        for module, enabled in enabled_modules.items():
            if module not in valid_modules:
                invalid_modules.append(module)
            
            # Validate that values are booleans
            if not isinstance(enabled, bool):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module '{module}' has invalid value. Expected boolean (true/false), got: {type(enabled).__name__}"
                )
        
        if invalid_modules:
            # Use cached sorted modules list
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid module(s): {', '.join(invalid_modules)}. Valid modules are: {', '.join(get_sorted_valid_modules())}"
            )
      
        # Idempotent update - only commit if there are actual changes
        if organization.enabled_modules != enabled_modules:
            organization.enabled_modules = enabled_modules
            await db.commit()
            logger.info(f"Organization {organization_id} modules updated by {current_user.email}: {len(enabled_modules)} modules configured")
            message = "Organization modules updated successfully"
        else:
            logger.debug(f"Organization {organization_id} modules unchanged - idempotent update")
            message = "Organization modules unchanged (already up to date)"
      
        return {
            "message": message,
            "enabled_modules": organization.enabled_modules,
            "available_modules": valid_modules
        }
      
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        # Log exception with stack trace only in development for debugging
        from app.core.config import settings
        logger.error(
            f"Error updating organization modules for org {organization_id}: {type(e).__name__}", 
            exc_info=(settings.ENVIRONMENT == "development")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization modules due to an internal error. Please contact support if the issue persists."
        )

@router.get("/{organization_id:int}", response_model=OrganizationInDB)
async def get_organization(
    organization_id: int,
    auth: tuple = Depends(require_access("organization", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization by ID"""
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can access any organization by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    return org

@router.put("/{organization_id:int}", response_model=OrganizationInDB)
async def update_organization(
    organization_id: int,
    org_update: OrganizationUpdate,
    auth: tuple = Depends(require_access("organization", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update organization"""
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can update any organization by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    try:
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
      
        if 'max_users' in update_data:
            current_date = datetime.now()
            yy = current_date.strftime('%y')
            mm = current_date.strftime('%m')
            result = await db.execute(select(func.count(User.id)))
            yy = result.scalar() or 0
            seq_num = yy + 1
            tqnnnn = f"tq{seq_num:04d}"
            org.org_code = f"{yy}/{mm}-({org.max_users})- {tqnnnn}"
      
        await db.commit()
        await db.refresh(org)
      
        logger.info(f"Updated organization {org.name} by user {current_user.email}")
        return org
      
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating organization"
        )

@router.delete("/{organization_id:int}")
async def delete_organization(
    organization_id: int,
    auth: tuple = Depends(require_access("organization", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete organization (requires organization delete permission)"""
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    
    # Critical operation - extra super admin check for safety
    if not getattr(current_user, 'is_super_admin', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Can delete any organization with proper permission (super admin only in practice)
    result = await db.execute(select(Organization).filter(Organization.id == organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    try:
        # Start transaction - wrap all deletions in a single transaction
        logger.info(f"Starting organization deletion for org_id={organization_id}, org_name={org.name}")
        
        # Delete all related data in proper order to respect foreign key constraints
        
        # 1. Delete user_service_roles (via user relationship)
        # UserServiceRole doesn't have organization_id, so we need to join through User
        user_service_role_delete = await db.execute(
            delete(UserServiceRole)
            .where(UserServiceRole.user_id.in_(
                select(User.id).where(User.organization_id == organization_id)
            ))
        )
        logger.info(f"Deleted {user_service_role_delete.rowcount} user_service_roles")
        
        # 2. Delete service_role_permissions
        role_perm_delete = await db.execute(
            delete(ServiceRolePermission).where(ServiceRolePermission.organization_id == organization_id)
        )
        logger.info(f"Deleted {role_perm_delete.rowcount} service_role_permissions")
        
        # 3. Delete service_roles
        service_role_delete = await db.execute(
            delete(ServiceRole).where(ServiceRole.organization_id == organization_id)
        )
        logger.info(f"Deleted {service_role_delete.rowcount} service_roles")
        
        # 4. Delete stock
        stock_delete = await db.execute(
            delete(Stock).where(Stock.organization_id == organization_id)
        )
        logger.info(f"Deleted {stock_delete.rowcount} stock records")
        
        # 5. Delete products
        product_delete = await db.execute(
            delete(Product).where(Product.organization_id == organization_id)
        )
        logger.info(f"Deleted {product_delete.rowcount} products")
        
        # 6. Delete customers
        customer_delete = await db.execute(
            delete(Customer).where(Customer.organization_id == organization_id)
        )
        logger.info(f"Deleted {customer_delete.rowcount} customers")
        
        # 7. Delete vendors
        vendor_delete = await db.execute(
            delete(Vendor).where(Vendor.organization_id == organization_id)
        )
        logger.info(f"Deleted {vendor_delete.rowcount} vendors")
        
        # 8. Delete users (including auth users) - must be done last as other tables reference users
        result = await db.execute(select(User).where(User.organization_id == organization_id))
        users = result.scalars().all()
        user_count = len(users)
        
        for user in users:
            if user.supabase_uuid:
                try:
                    supabase_auth_service.delete_user(user.supabase_uuid)
                    logger.info(f"Deleted Supabase user {user.supabase_uuid} for {user.email}")
                except Exception as supabase_error:
                    logger.error(f"Failed to delete Supabase user {user.supabase_uuid}: {supabase_error}")
                    # Continue deletion even if Supabase fails
            await db.delete(user)
        
        logger.info(f"Deleted {user_count} users")
        
        # Commit all deletions before deleting the organization itself
        await db.commit()
        
        # 9. Finally delete the organization
        await db.delete(org)
        await db.commit()
        
        logger.info(f"Successfully deleted organization {org.name} (id={organization_id}) and all related data by user {current_user.email}")
        return {
            "message": "Organization and all related data deleted successfully",
            "deleted": {
                "user_service_roles": user_service_role_delete.rowcount if user_service_role_delete else 0,
                "service_role_permissions": role_perm_delete.rowcount if role_perm_delete else 0,
                "service_roles": service_role_delete.rowcount if service_role_delete else 0,
                "stock": stock_delete.rowcount if stock_delete else 0,
                "products": product_delete.rowcount if product_delete else 0,
                "customers": customer_delete.rowcount if customer_delete else 0,
                "vendors": vendor_delete.rowcount if vendor_delete else 0,
                "users": user_count,
                "organization": org.name
            }
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting organization {organization_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting organization and related data: {str(e)}"
        )

@router.get("/{organization_id:int}/users/{user_id:int}/modules")
async def get_user_modules(
    organization_id: int,
    user_id: int,
    auth: tuple = Depends(require_access("user", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get user's assigned modules"""
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can access any organization's user modules by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN] and current_user.role != "HR":
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view user modules"
            )
  
    result = await db.execute(select(User).where(
        User.id == user_id,
        User.organization_id == organization_id
    ))
    user = result.scalars().first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
  
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

@router.put("/{organization_id:int}/users/{user_id:int}/modules")
async def update_user_modules(
    organization_id: int,
    user_id: int,
    modules_data: dict,
    auth: tuple = Depends(require_access("user", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update user's assigned modules (requires user update permission)"""
    current_user, org_id = auth
    
    if current_user.is_super_admin:
        # Super admin can update any organization's user modules by explicit org_id
        org_id = organization_id
        TenantContext.set_organization_id(org_id)
    else:
        # Enforce tenant isolation for non-super_admin users
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN] and current_user.role != "HR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR personnel and organization administrators can manage user modules"
        )
  
    result = await db.execute(select(User).where(
        User.id == user_id,
        User.organization_id == organization_id
    ))
    user = result.scalars().first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
  
    try:
        result = await db.execute(select(Organization).where(Organization.id == organization_id))
        organization = result.scalars().first()
        org_enabled_modules = organization.enabled_modules or {}
      
        valid_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance"]
        assigned_modules = modules_data.get("assigned_modules", {})
      
        for module, enabled in assigned_modules.items():
            if module not in valid_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid module: {module}"
                )
            if enabled and not org_enabled_modules.get(module, False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module {module} is not enabled for this organization"
                )
      
        user.assigned_modules = assigned_modules
        await db.commit()
      
        logger.info(f"User {user_id} modules updated by {current_user.email}")
        return {"message": "User modules updated successfully", "assigned_modules": user.assigned_modules}
      
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user modules"
        )