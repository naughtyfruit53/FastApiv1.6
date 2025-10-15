# app/api/v1/organizations/module_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models import Organization, User, Product, Customer, Vendor, Stock
from app.schemas.user import UserRole
from app.schemas import OrganizationUpdate, OrganizationInDB
import logging
from app.utils.supabase_auth import supabase_auth_service
from app.models.rbac_models import UserServiceRole, ServiceRolePermission, ServiceRole  # Changed to absolute from rbac_models

logger = logging.getLogger(__name__)

module_router = APIRouter()

@module_router.get("/{organization_id:int}/modules")
async def get_organization_modules(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization's enabled modules"""
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

@module_router.put("/{organization_id:int}/modules")
async def update_organization_modules(
    organization_id: int,
    modules_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization's enabled modules (super admin only)"""
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
        valid_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance"]
        for module in modules_data.get("enabled_modules", {}):
            if module not in valid_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid module: {module}"
                )
      
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

@module_router.get("/{organization_id:int}", response_model=OrganizationInDB)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
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
  
    return org

@module_router.put("/{organization_id:int}", response_model=OrganizationInDB)
async def update_organization(
    organization_id: int,
    org_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization"""
    if not current_user.is_super_admin:
        if current_user.organization_id != organization_id or current_user.role not in [UserRole.ORG_ADMIN]:
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
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
      
        if 'max_users' in update_data:
            current_date = datetime.now()
            yy = current_date.strftime('%y')
            mm = current_date.strftime('%m')
            total_users = db.query(func.count(User.id)).scalar() or 0
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

@module_router.delete("/{organization_id:int}")
async def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete organization (Super admin only)"""
    if not current_user.is_super_admin:
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
  
    try:
        # Delete all related data
        # Delete user_service_roles
        db.query(UserServiceRole).filter(UserServiceRole.organization_id == organization_id).delete()
        
        # Delete service_role_permissions
        db.query(ServiceRolePermission).filter(ServiceRolePermission.organization_id == organization_id).delete()
        
        # Delete stock
        db.query(Stock).filter(Stock.organization_id == organization_id).delete()
        
        # Delete products
        db.query(Product).filter(Product.organization_id == organization_id).delete()
        
        # Delete customers
        db.query(Customer).filter(Customer.organization_id == organization_id).delete()
        
        # Delete vendors
        db.query(Vendor).filter(Vendor.organization_id == organization_id).delete()
        
        # Delete users (including auth users)
        users = db.query(User).filter(User.organization_id == organization_id).all()
        for user in users:
            if user.supabase_uuid:
                try:
                    supabase_auth_service.delete_user(user.supabase_uuid)
                    logger.info(f"Deleted Supabase user {user.supabase_uuid} for {user.email}")
                except Exception as supabase_error:
                    logger.error(f"Failed to delete Supabase user {user.supabase_uuid}: {supabase_error}")
                    # Continue deletion even if Supabase fails
            db.delete(user)
        
        # Delete service_roles
        db.query(ServiceRole).filter(ServiceRole.organization_id == organization_id).delete()
        
        # Commit deletions
        db.commit()
        
        # Now delete the organization
        db.delete(org)
        db.commit()
        
        logger.info(f"Deleted organization {org.name} and all related data by user {current_user.email}")
        return {"message": "Organization and all related data deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting organization and related data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting organization and related data"
        )

@module_router.get("/{organization_id:int}/users/{user_id:int}/modules")
async def get_user_modules(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's assigned modules"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN] and current_user.role != "HR":
        if current_user.id != user_id:
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

@module_router.put("/{organization_id:int}/users/{user_id:int}/modules")
async def update_user_modules(
    organization_id: int,
    user_id: int,
    modules_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's assigned modules (HR role or org admin)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
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
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
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