# app/api/v1/role_delegation.py

"""
Role Delegation API endpoints

Allows org_admin and management to delegate module/submodule access to manager and executive roles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User, ServiceRole, ServicePermission, ServiceRolePermission, UserServiceRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants for role names
DELEGATOR_ROLES = ['org_admin', 'management']  # Roles that can delegate permissions
DELEGATEE_ROLES = ['manager', 'executive']  # Roles that can receive delegated permissions


# Request/Response Schemas
class DelegatePermissionsRequest(BaseModel):
    """Request to delegate permissions to a role"""
    target_role_name: str  # 'manager' or 'executive'
    permission_names: List[str]  # List of permission names to delegate


class DelegatePermissionsResponse(BaseModel):
    """Response from permission delegation"""
    success: bool
    message: str
    granted_permissions: List[str]
    failed_permissions: List[str]


class RevokePermissionsRequest(BaseModel):
    """Request to revoke permissions from a role"""
    target_role_name: str  # 'manager' or 'executive'
    permission_names: List[str]  # List of permission names to revoke


class RevokePermissionsResponse(BaseModel):
    """Response from permission revocation"""
    success: bool
    message: str
    revoked_permissions: List[str]
    failed_permissions: List[str]


class RolePermissionsResponse(BaseModel):
    """Response with role's current permissions"""
    role_name: str
    role_id: int
    organization_id: int
    permissions: List[dict]


# Helper function to check if user can delegate
async def check_delegation_permission(
    current_user: User,
    organization_id: int,
    db: AsyncSession
) -> bool:
    """Check if user has org_admin or management role"""
    result = await db.execute(
        select(UserServiceRole).join(ServiceRole).where(
            and_(
                UserServiceRole.user_id == current_user.id,
                ServiceRole.organization_id == organization_id,
                ServiceRole.name.in_(DELEGATOR_ROLES),
                UserServiceRole.is_active == True,
                ServiceRole.is_active == True
            )
        )
    )
    return result.first() is not None


# Endpoints
@router.post("/delegate", response_model=DelegatePermissionsResponse)
async def delegate_permissions(
    request: DelegatePermissionsRequest,
    auth: tuple = Depends(require_access("admin", "create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Delegate module/submodule permissions to manager or executive roles.
    
    Only org_admin and management can delegate permissions.
    Can only delegate to 'manager' or 'executive' roles.
    """
    current_user, organization_id = auth
    
    # Check if user can delegate
    can_delegate = await check_delegation_permission(current_user, organization_id, db)
    if not can_delegate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {', '.join(DELEGATOR_ROLES)} roles can delegate permissions"
        )
    
    # Validate target role
    if request.target_role_name not in DELEGATEE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only delegate to {', '.join(DELEGATEE_ROLES)} roles"
        )
    
    # Get target role
    result = await db.execute(
        select(ServiceRole).where(
            and_(
                ServiceRole.organization_id == organization_id,
                ServiceRole.name == request.target_role_name,
                ServiceRole.is_active == True
            )
        )
    )
    target_role = result.scalar_one_or_none()
    
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{request.target_role_name}' not found in organization"
        )
    
    granted_permissions = []
    failed_permissions = []
    
    # Process each permission
    for perm_name in request.permission_names:
        # Get permission
        perm_result = await db.execute(
            select(ServicePermission).where(
                and_(
                    ServicePermission.name == perm_name,
                    ServicePermission.is_active == True
                )
            )
        )
        permission = perm_result.scalar_one_or_none()
        
        if not permission:
            logger.warning(f"Permission '{perm_name}' not found")
            failed_permissions.append(perm_name)
            continue
        
        # Check if permission is already granted
        existing_result = await db.execute(
            select(ServiceRolePermission).where(
                and_(
                    ServiceRolePermission.role_id == target_role.id,
                    ServiceRolePermission.permission_id == permission.id
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            logger.info(f"Permission '{perm_name}' already granted to '{request.target_role_name}'")
            granted_permissions.append(perm_name)
            continue
        
        # Grant permission
        role_permission = ServiceRolePermission(
            role_id=target_role.id,
            permission_id=permission.id
        )
        db.add(role_permission)
        granted_permissions.append(perm_name)
        logger.info(f"Granted permission '{perm_name}' to role '{request.target_role_name}'")
    
    await db.commit()
    
    return DelegatePermissionsResponse(
        success=len(failed_permissions) == 0,
        message=f"Delegated {len(granted_permissions)} permissions to {request.target_role_name}",
        granted_permissions=granted_permissions,
        failed_permissions=failed_permissions
    )


@router.post("/revoke", response_model=RevokePermissionsResponse)
async def revoke_permissions(
    request: RevokePermissionsRequest,
    auth: tuple = Depends(require_access("admin", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke delegated permissions from manager or executive roles.
    
    Only org_admin and management can revoke permissions.
    Can only revoke from 'manager' or 'executive' roles.
    """
    current_user, organization_id = auth
    
    # Check if user can revoke
    can_delegate = await check_delegation_permission(current_user, organization_id, db)
    if not can_delegate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {', '.join(DELEGATOR_ROLES)} roles can revoke permissions"
        )
    
    # Validate target role
    if request.target_role_name not in DELEGATEE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only revoke from {', '.join(DELEGATEE_ROLES)} roles"
        )
    
    # Get target role
    result = await db.execute(
        select(ServiceRole).where(
            and_(
                ServiceRole.organization_id == organization_id,
                ServiceRole.name == request.target_role_name,
                ServiceRole.is_active == True
            )
        )
    )
    target_role = result.scalar_one_or_none()
    
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{request.target_role_name}' not found in organization"
        )
    
    revoked_permissions = []
    failed_permissions = []
    
    # Process each permission
    for perm_name in request.permission_names:
        # Get permission
        perm_result = await db.execute(
            select(ServicePermission).where(
                and_(
                    ServicePermission.name == perm_name,
                    ServicePermission.is_active == True
                )
            )
        )
        permission = perm_result.scalar_one_or_none()
        
        if not permission:
            logger.warning(f"Permission '{perm_name}' not found")
            failed_permissions.append(perm_name)
            continue
        
        # Check if permission is granted
        existing_result = await db.execute(
            select(ServiceRolePermission).where(
                and_(
                    ServiceRolePermission.role_id == target_role.id,
                    ServiceRolePermission.permission_id == permission.id
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if not existing:
            logger.warning(f"Permission '{perm_name}' not granted to '{request.target_role_name}'")
            failed_permissions.append(perm_name)
            continue
        
        # Revoke permission
        await db.delete(existing)
        revoked_permissions.append(perm_name)
        logger.info(f"Revoked permission '{perm_name}' from role '{request.target_role_name}'")
    
    await db.commit()
    
    return RevokePermissionsResponse(
        success=len(failed_permissions) == 0,
        message=f"Revoked {len(revoked_permissions)} permissions from {request.target_role_name}",
        revoked_permissions=revoked_permissions,
        failed_permissions=failed_permissions
    )


@router.get("/role/{role_name}/permissions", response_model=RolePermissionsResponse)
async def get_role_permissions(
    role_name: str,
    auth: tuple = Depends(require_access("admin", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all permissions granted to a specific role.
    
    Returns the list of permissions for manager or executive roles.
    """
    current_user, organization_id = auth
    
    # Check if user can view role permissions
    can_view = await check_delegation_permission(current_user, organization_id, db)
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {', '.join(DELEGATOR_ROLES)} roles can view role permissions"
        )
    
    # Get role
    result = await db.execute(
        select(ServiceRole).where(
            and_(
                ServiceRole.organization_id == organization_id,
                ServiceRole.name == role_name,
                ServiceRole.is_active == True
            )
        )
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found in organization"
        )
    
    # Get all permissions for this role
    perms_result = await db.execute(
        select(ServicePermission).join(ServiceRolePermission).where(
            and_(
                ServiceRolePermission.role_id == role.id,
                ServicePermission.is_active == True
            )
        )
    )
    permissions = perms_result.scalars().all()
    
    return RolePermissionsResponse(
        role_name=role.name,
        role_id=role.id,
        organization_id=role.organization_id,
        permissions=[
            {
                "id": p.id,
                "name": p.name,
                "display_name": p.display_name,
                "description": p.description if hasattr(p, 'description') else None,
                "module": p.module if hasattr(p, 'module') else None,
                "action": p.action if hasattr(p, 'action') else None
            }
            for p in permissions
        ]
    )
