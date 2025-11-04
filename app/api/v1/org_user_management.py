# app/api/v1/org_user_management.py

"""
Organization User Management API for the new 4-role system.

This API provides endpoints for creating and managing users with the new role system:
- Org Admin: Full access based on entitlement
- Management: Full owner-like access via RBAC  
- Manager: Module-level access
- Executive: Submodule-level access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user_models import User
from app.schemas.user import UserRole, UserInDB, UserCreate
from app.services.org_role_service import OrgRoleService
from app.core.security import get_password_hash
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response schemas
class OrgUserCreateRequest(BaseModel):
    """Request schema for creating organization users"""
    email: EmailStr
    full_name: str
    password: str
    role: UserRole
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    
    # Role-specific fields
    assigned_modules: Optional[Dict[str, bool]] = None  # For Manager
    reporting_manager_id: Optional[int] = None  # For Executive
    sub_module_permissions: Optional[Dict[str, List[str]]] = None  # For Executive


class ModuleSubmoduleResponse(BaseModel):
    """Response schema for available modules and submodules"""
    modules: Dict[str, List[str]]  # module_key -> [submodule_keys]


class UserPermissionsResponse(BaseModel):
    """Response schema for user effective permissions"""
    role: str
    modules: Dict[str, List[str]]
    submodules: Dict[str, List[str]]
    full_access: bool


# Endpoints
@router.post("/users", response_model=UserInDB)
async def create_org_user(
    user_data: OrgUserCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new organization user with role-based access control.
    
    Rules:
    - Only Org Admin can create Org Admin users
    - Management can create Managers and Executives
    - Managers can create Executives under their management
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    org_id = current_user.organization_id
    role_service = OrgRoleService(db)
    
    # Validate role transition
    await role_service.validate_role_transition(
        current_role=None,  # New user
        new_role=user_data.role.value,
        requester_role=current_user.role,
        org_id=org_id
    )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(
            User.email == user_data.email,
            User.organization_id == org_id
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization"
        )
    
    # Validate and process role-specific data
    if user_data.role == UserRole.MANAGER:
        if not user_data.assigned_modules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Managers must have assigned modules"
            )
        # Validate modules are entitled
        available = await role_service.get_available_modules_for_role(
            UserRole.ORG_ADMIN.value,
            org_id
        )
        for module in user_data.assigned_modules.keys():
            if module not in available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module '{module}' is not available for this organization"
                )
    
    elif user_data.role == UserRole.EXECUTIVE:
        if not user_data.reporting_manager_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Executives must have a reporting manager"
            )
        # Validate reporting manager exists and is a Manager
        manager_result = await db.execute(
            select(User).where(User.id == user_data.reporting_manager_id)
        )
        manager = manager_result.scalars().first()
        if not manager or manager.role != UserRole.MANAGER.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reporting manager"
            )
    
    # Create user in Supabase Auth
    try:
        supabase_user = supabase_auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            user_metadata={
                "full_name": user_data.full_name,
                "role": user_data.role.value,
                "organization_id": org_id,
                "department": user_data.department,
                "designation": user_data.designation
            }
        )
        supabase_uuid = supabase_user["supabase_uuid"]
        logger.info(f"Created user {user_data.email} in Supabase with UUID {supabase_uuid}")
    except SupabaseAuthError as e:
        logger.error(f"Failed to create user in Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user in authentication system: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user in Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in authentication system"
        )
    
    # Create user in database
    try:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            organization_id=org_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role.value,
            department=user_data.department,
            designation=user_data.designation,
            employee_id=user_data.employee_id,
            phone=user_data.phone,
            supabase_uuid=supabase_uuid,
            assigned_modules=user_data.assigned_modules or {},
            reporting_manager_id=user_data.reporting_manager_id,
            sub_module_permissions=user_data.sub_module_permissions or {}
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Assign modules/submodules based on role
        if user_data.role == UserRole.MANAGER and user_data.assigned_modules:
            await role_service.assign_modules_to_user(
                user_id=db_user.id,
                modules=user_data.assigned_modules,
                org_id=org_id,
                assigned_by_id=current_user.id
            )
        
        elif user_data.role == UserRole.EXECUTIVE and user_data.sub_module_permissions:
            await role_service.assign_submodules_to_executive(
                user_id=db_user.id,
                submodule_permissions=user_data.sub_module_permissions,
                org_id=org_id,
                manager_id=user_data.reporting_manager_id,
                assigned_by_id=current_user.id
            )
        
        logger.info(f"User {user_data.email} created with role {user_data.role.value}")
        return db_user
    
    except Exception as e:
        # Cleanup Supabase user if database creation fails
        try:
            supabase_auth_service.delete_user(supabase_uuid)
            logger.info(f"Cleaned up Supabase user {supabase_uuid}")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup Supabase user: {cleanup_error}")
        
        await db.rollback()
        logger.error(f"Failed to create user in database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in database"
        )


@router.get("/available-modules/{role}", response_model=ModuleSubmoduleResponse)
async def get_available_modules(
    role: UserRole,
    manager_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available modules and submodules for a specific role.
    
    For Executive role, manager_id must be provided to get manager's modules.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    role_service = OrgRoleService(db)
    
    modules = await role_service.get_available_modules_for_role(
        role=role.value,
        org_id=current_user.organization_id,
        manager_id=manager_id
    )
    
    return {"modules": modules}


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get effective permissions for a user based on their role.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    # Verify user belongs to same organization
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role_service = OrgRoleService(db)
    permissions = await role_service.get_user_effective_permissions(
        user_id=user_id,
        org_id=current_user.organization_id
    )
    
    return permissions


@router.put("/users/{user_id}/modules")
async def update_user_modules(
    user_id: int,
    modules: Dict[str, bool] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update module assignments for a Manager.
    
    Only Org Admin and Management can update module assignments.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    # Check permission
    if current_user.role not in [UserRole.ORG_ADMIN.value, UserRole.MANAGEMENT.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Org Admin and Management can update module assignments"
        )
    
    # Verify user exists and is a Manager
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != UserRole.MANAGER.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update modules for Manager role"
        )
    
    role_service = OrgRoleService(db)
    await role_service.assign_modules_to_user(
        user_id=user_id,
        modules=modules,
        org_id=current_user.organization_id,
        assigned_by_id=current_user.id
    )
    
    return {"message": "Modules updated successfully"}


@router.put("/users/{user_id}/submodules")
async def update_executive_submodules(
    user_id: int,
    submodules: Dict[str, List[str]] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update submodule permissions for an Executive.
    
    Can be done by Org Admin, Management, or the Executive's reporting Manager.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    # Verify user exists and is an Executive
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id
        )
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role != UserRole.EXECUTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update submodules for Executive role"
        )
    
    # Check permission
    allowed = (
        current_user.role in [UserRole.ORG_ADMIN.value, UserRole.MANAGEMENT.value] or
        (current_user.role == UserRole.MANAGER.value and user.reporting_manager_id == current_user.id)
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this executive's submodules"
        )
    
    if not user.reporting_manager_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Executive must have a reporting manager"
        )
    
    role_service = OrgRoleService(db)
    await role_service.assign_submodules_to_executive(
        user_id=user_id,
        submodule_permissions=submodules,
        org_id=current_user.organization_id,
        manager_id=user.reporting_manager_id,
        assigned_by_id=current_user.id
    )
    
    return {"message": "Submodules updated successfully"}


@router.get("/managers", response_model=List[UserInDB])
async def get_managers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all managers in the organization.
    Used for selecting reporting manager when creating Executives.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.role == UserRole.MANAGER.value,
            User.is_active == True
        )
    )
    
    return result.scalars().all()


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user from the organization.
    
    Rules:
    - org_admin can delete any user except themselves
    - management can delete managers and executives
    - managers can delete executives under their management
    - Cannot delete super_admin users
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user must belong to an organization"
        )
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Get user to delete
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.organization_id == current_user.organization_id
        )
    )
    user_to_delete = result.scalar_one_or_none()
    
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deletion of super_admin
    if user_to_delete.is_super_admin or user_to_delete.role == 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete super admin users"
        )
    
    # Check permissions based on current user role
    requester_role = current_user.role.lower()
    target_role = user_to_delete.role.lower()
    
    if requester_role == 'org_admin':
        # org_admin can delete anyone except themselves and super_admin (already checked)
        pass
    elif requester_role == 'management':
        # management can delete managers and executives
        if target_role not in ['manager', 'executive']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Management users cannot delete {target_role} users"
            )
    elif requester_role == 'manager':
        # managers can only delete executives under their management
        if target_role != 'executive':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only delete executives"
            )
        if user_to_delete.reporting_manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete executives reporting to you"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete users"
        )
    
    # Delete user from Supabase Auth if exists
    if user_to_delete.supabase_uuid:
        try:
            supabase_auth_service.delete_user(user_to_delete.supabase_uuid)
            logger.info(f"Deleted user {user_to_delete.email} from Supabase")
        except Exception as e:
            logger.warning(f"Failed to delete user from Supabase: {e}")
            # Continue with database deletion even if Supabase fails
    
    # Soft delete or hard delete - using soft delete by setting is_active = False
    user_to_delete.is_active = False
    await db.commit()
    
    logger.info(f"User {user_to_delete.email} (id={user_id}) deleted by {current_user.email}")
    
    return {
        "message": f"User {user_to_delete.email} deleted successfully",
        "deleted_user_id": user_id,
        "deleted_user_email": user_to_delete.email
    }
