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
            # Sort valid modules once for display
            valid_modules_sorted = sorted(valid_modules)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid module(s): {', '.join(invalid_modules)}. Valid modules are: {', '.join(valid_modules_sorted)}"
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
        # Delete all related data
        # Delete user_service_roles
        await db.execute(delete(UserServiceRole).where(UserServiceRole.organization_id == organization_id))
        
        # Delete service_role_permissions
        await db.execute(delete(ServiceRolePermission).where(ServiceRolePermission.organization_id == organization_id))
        
        # Delete stock
        await db.execute(delete(Stock).where(Stock.organization_id == organization_id))
        
        # Delete products
        await db.execute(delete(Product).where(Product.organization_id == organization_id))
        
        # Delete customers
        await db.execute(delete(Customer).where(Customer.organization_id == organization_id))
        
        # Delete vendors
        await db.execute(delete(Vendor).where(Vendor.organization_id == organization_id))
        
        # Delete users (including auth users)
        result = await db.execute(select(User).where(User.organization_id == organization_id))
        users = result.scalars().all()
        for user in users:
            if user.supabase_uuid:
                try:
                    supabase_auth_service.delete_user(user.supabase_uuid)
                    logger.info(f"Deleted Supabase user {user.supabase_uuid} for {user.email}")
                except Exception as supabase_error:
                    logger.error(f"Failed to delete Supabase user {user.supabase_uuid}: {supabase_error}")
                    # Continue deletion even if Supabase fails
            await db.delete(user)
        
        # Delete service_roles
        await db.execute(delete(ServiceRole).where(ServiceRole.organization_id == organization_id))
        
        # Commit deletions
        await db.commit()
        
        # Now delete the organization
        await db.delete(org)
        await db.commit()
        
        logger.info(f"Deleted organization {org.name} and all related data by user {current_user.email}")
        return {"message": "Organization and all related data deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting organization and related data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting organization and related data"
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