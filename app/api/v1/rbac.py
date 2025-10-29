# app/api/v1/rbac.py

"""
Service CRM RBAC API endpoints for role and permission management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User
from app.services.rbac import RBACService
from app.schemas.rbac import (
    ServiceRoleCreate, ServiceRoleUpdate, ServiceRoleInDB, ServiceRoleWithPermissions,
    ServicePermissionInDB, UserServiceRoleCreate, UserServiceRoleInDB,
    UserWithServiceRoles, RoleAssignmentRequest, RoleAssignmentResponse,
    BulkRoleAssignmentRequest, BulkRoleAssignmentResponse,
    PermissionCheckRequest, PermissionCheckResponse
)
from app.api.v1.user import get_current_active_user
from app.core.rbac_dependencies import (
    require_role_management_permission, require_same_organization,
    get_rbac_service
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Permission Assignment Request Schema
class PermissionAssignmentRequest(BaseModel):
    permission_names: List[str]

# Permission Assignment Response Schema
class PermissionAssignmentResponse(BaseModel):
    success: bool
    message: str
    assigned_permissions: List[str]
    failed_permissions: List[str]

# Permission Management Endpoints
@router.get("/permissions", response_model=List[ServicePermissionInDB])
async def get_service_permissions(
    module: Optional[str] = Query(None, description="Filter by module"),
    action: Optional[str] = Query(None, description="Filter by action"),
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read"))
):
    """Get all service permissions with optional filtering"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} requesting service permissions")
    
    # Validate module if provided
    if module:
        from app.schemas.rbac import ServiceModule
        if not ServiceModule.is_valid(module):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid module '{module}'. Must be one of: {', '.join([m.value for m in ServiceModule])}"
            )
    
    # Validate action if provided
    if action:
        from app.schemas.rbac import ServiceAction
        try:
            ServiceAction(action)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action '{action}'. Must be one of: {', '.join([a.value for a in ServiceAction])}"
            )
    
    permissions = await rbac_service.get_permissions(module=module, action=action)
    return permissions

@router.post("/permissions/initialize")
async def initialize_default_permissions(
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create"))
):
    """Initialize default service permissions (admin only)"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} initializing default permissions")
    
    if not getattr(current_user, 'is_super_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can initialize permissions"
        )
    
    permissions = await rbac_service.initialize_default_permissions()
    return {
        "message": f"Initialized {len(permissions)} default permissions",
        "permissions": permissions
    }

# Role Management Endpoints
@router.get("/organizations/{organization_id}/roles", response_model=List[ServiceRoleInDB])
async def get_organization_roles(
    organization_id: int,
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read")),
    _: int = Depends(require_same_organization)
):
    """Get all service roles for an organization, excluding super_admin for non-super admins"""
    current_user, organization_id = auth

    try:
        # Validate organization_id is positive
        if organization_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization_id. Must be a positive integer."
            )
        
        logger.info(f"User {current_user.id} requesting roles for organization {organization_id}")
        roles = await rbac_service.get_roles(organization_id, is_active=is_active)
        return roles
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching roles for organization {organization_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch organization roles"
        )

@router.post("/organizations/{organization_id}/roles", response_model=ServiceRoleInDB)
async def create_service_role(
    organization_id: int,
    role: ServiceRoleCreate,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create")),
    _: int = Depends(require_same_organization)
):
    """Create a new service role, preventing org admins from creating super_admin role"""
    current_user, organization_id = auth

    try:
        # Validate organization_id is positive
        if organization_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization_id. Must be a positive integer."
            )
        
        logger.info(f"User {current_user.id} creating role '{role.name}' for organization {organization_id}")
        
        # Prevent org admins from creating super_admin role
        if not current_user.is_super_admin and role.name == "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only app super admins can create super_admin roles"
            )
        
        # Validate role name is a valid ServiceRoleType enum value
        try:
            from app.schemas.rbac import ServiceRoleType
            ServiceRoleType(role.name)
        except ValueError:
            logger.error(f"Invalid role type: {role.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role type '{role.name}'. Must be one of: {', '.join([r.value for r in ServiceRoleType])}"
            )
        
        # Ensure organization_id matches between path and body
        role.organization_id = organization_id
        
        db_role = await rbac_service.create_role(role, created_by_user_id=current_user.id)
        return db_role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service role: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )

@router.get("/roles/{role_id}", response_model=ServiceRoleWithPermissions)
async def get_service_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read"))
):
    """Get a specific service role with its permissions"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} requesting role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else organization_id
        
        role = await rbac_service.get_role_with_permissions(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if organization_id and role.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to role from different organization"
            )
        
        role_dict = role.__dict__.copy()
        role_dict['permissions'] = [rp.permission for rp in role.permissions]
        
        return role_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch role"
        )

@router.put("/roles/{role_id}", response_model=ServiceRoleInDB)
async def update_service_role(
    role_id: int,
    updates: ServiceRoleUpdate,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "update"))
):
    """Update a service role"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} updating role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else organization_id
        
        db_role = await rbac_service.update_role(role_id, updates, organization_id=organization_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return db_role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )

@router.delete("/roles/{role_id}")
async def delete_service_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "delete"))
):
    """Delete a service role"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} deleting role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else organization_id
        
        success = await rbac_service.delete_role(role_id, organization_id=organization_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        
        return {"message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role"
        )

@router.post("/organizations/{organization_id}/roles/initialize")
async def initialize_default_roles(
    organization_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create")),
    _: int = Depends(require_same_organization)
):
    """Initialize default service roles for an organization"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} initializing default roles for organization {organization_id}")
        
        roles = await rbac_service.initialize_default_roles(organization_id)
        return {
            "message": f"Initialized {len(roles)} default roles",
            "roles": roles
        }
    except Exception as e:
        logger.error(f"Error initializing default roles for organization {organization_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize default roles"
        )

# User Role Assignment Endpoints
@router.post("/users/{user_id}/roles", response_model=RoleAssignmentResponse)
async def assign_roles_to_user(
    user_id: int,
    assignment: RoleAssignmentRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create"))
):
    """Assign service roles to a user"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} assigning roles to user {user_id}")
        
        assignment.user_id = user_id
        
        assignments = await rbac_service.assign_multiple_roles_to_user(
            user_id, assignment.role_ids, assigned_by_id=current_user.id
        )
        
        return RoleAssignmentResponse(
            success=True,
            message=f"Successfully assigned {len(assignments)} roles",
            assignments=assignments
        )
    except HTTPException as e:
        logger.error(f"HTTP error assigning roles to user {user_id}: {e.detail}")
        return RoleAssignmentResponse(
            success=False,
            message=f"Failed to assign roles: {e.detail}",
            assignments=[]
        )
    except Exception as e:
        logger.error(f"Error assigning roles to user {user_id}: {str(e)}", exc_info=True)
        return RoleAssignmentResponse(
            success=False,
            message=f"Failed to assign roles: {str(e)}",
            assignments=[]
        )

@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "delete"))
):
    """Remove a specific role from a user"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} removing role {role_id} from user {user_id}")
        
        success = await rbac_service.remove_role_from_user(user_id, role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role assignment not found")
        
        return {"message": "Role removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing role {role_id} from user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove role"
        )

@router.delete("/users/{user_id}/roles")
async def remove_all_roles_from_user(
    user_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "delete"))
):
    """Remove all service roles from a user"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} removing all roles from user {user_id}")
    
    count = await rbac_service.remove_all_service_roles_from_user(user_id)
    return {"message": f"Removed {count} role assignments"}

@router.get("/users/{user_id}/roles", response_model=List[ServiceRoleInDB])
async def get_user_service_roles(
    user_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read"))
):
    """Get all service roles assigned to a user, including self"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} requesting roles for user {user_id}")
    
    # Allow users to view their own roles
    if current_user.id != user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view other users' roles"
        )
    
    roles = await rbac_service.get_user_roles(user_id)
    return roles

@router.get("/roles/{role_id}/users", response_model=List[UserWithServiceRoles])
async def get_users_with_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read"))
):
    """Get all users assigned to a specific role"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} requesting users with role {role_id}")
    
    users = await rbac_service.get_users_with_role(role_id)
    
    result = []
    for user in users:
        user_roles = await rbac_service.get_user_roles(user.id)
        result.append(UserWithServiceRoles(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            service_roles=user_roles
        ))
    
    return result

@router.post("/users/{user_id}/permissions", response_model=PermissionAssignmentResponse)
async def assign_permissions_to_user(
    user_id: int,
    assignment: PermissionAssignmentRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Assign specific permissions to a user by creating a custom role"""
    current_user, organization_id = auth

    try:
        logger.info(f"User {current_user.id} assigning permissions to user {user_id}")
        
        # Validate user exists
        user_result = await db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create or find a custom role for the user
        custom_role_name = f"custom_{user_id}_{current_user.id}"
        role_result = await db.execute(
            select(Role).filter_by(organization_id=user.organization_id, name=custom_role_name)
        )
        custom_role = role_result.scalars().first()
        
        if not custom_role:
            role_create = ServiceRoleCreate(
                name=custom_role_name,
                display_name=f"Custom Role for User {user_id}",
                description="Auto-generated custom role for direct permission assignments",
                organization_id=user.organization_id,
                permission_ids=[]
            )
            custom_role = await rbac_service.create_role(role_create, created_by_user_id=current_user.id)
        
        # Validate and assign permissions
        permission_ids = []
        failed_permissions = []
        for perm_name in assignment.permission_names:
            perm_result = await db.execute(
                select(Permission).filter_by(name=perm_name, is_active=True)
            )
            permission = perm_result.scalars().first()
            if permission:
                permission_ids.append(permission.id)
            else:
                failed_permissions.append(perm_name)
        
        if permission_ids:
            # Update role with new permissions
            role_update = ServiceRoleUpdate(
                name=custom_role.name,
                display_name=custom_role.display_name,
                description=custom_role.description,
                permission_ids=permission_ids
            )
            await rbac_service.update_role(custom_role.id, role_update, organization_id=user.organization_id)
        
        # Assign the custom role to the user if not already assigned
        existing_assignment = await db.execute(
            select(UserRole).filter_by(user_id=user_id, role_id=custom_role.id)
        )
        assignment_record = existing_assignment.scalars().first()
        
        if not assignment_record:
            await rbac_service.assign_role_to_user(user_id, custom_role.id, assigned_by_id=current_user.id)
        elif not assignment_record.is_active:
            assignment_record.is_active = True
            await db.commit()
        
        return PermissionAssignmentResponse(
            success=len(failed_permissions) == 0,
            message=f"Assigned {len(permission_ids)} permissions to user {user_id}",
            assigned_permissions=[perm_name for perm_name in assignment.permission_names if perm_name not in failed_permissions],
            failed_permissions=failed_permissions
        )
    except HTTPException as e:
        logger.error(f"HTTP error assigning permissions to user {user_id}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error assigning permissions to user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign permissions"
        )

# Permission Checking Endpoints
@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_user_permission(
    request: PermissionCheckRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create"))
):
    """Check if a user has a specific permission, including self"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} checking permission '{request.permission}' for user {request.user_id}")
    
    # Allow users to check their own permissions
    if current_user.id != request.user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to check other users' permissions"
        )
    
    has_permission = await rbac_service.user_has_permission(request.user_id, request.permission)
    
    source = "none"
    if has_permission:
        user_roles = await rbac_service.get_user_roles(request.user_id)
        source = "service_role" if user_roles else "none"
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        user_id=request.user_id,
        permission=request.permission,
        source=source
    )

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "read"))
):
    """Get all permissions for a user, including self"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} requesting permissions for user {user_id}")
    
    # Allow users to view their own permissions
    if current_user.id != user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view other users' permissions"
        )
    
    try:
        permissions = await rbac_service.get_user_permissions(user_id)
        roles = await rbac_service.get_user_roles(user_id)
    
        return {
            "user_id": user_id,
            "permissions": list(permissions),
            "service_roles": roles,
            "total_permissions": len(permissions)
        }
    except Exception as e:
        logger.error(f"Error fetching user permissions for {user_id}: {str(e)}", exc_info=True)
        # Return empty permissions to avoid frontend crash
        return {
            "user_id": user_id,
            "permissions": [],
            "service_roles": [],
            "total_permissions": 0,
            "error": "Failed to fetch permissions"
        }

# Bulk Operations
@router.post("/roles/assign/bulk", response_model=BulkRoleAssignmentResponse)
async def bulk_assign_roles(
    request: BulkRoleAssignmentRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    auth: tuple = Depends(require_access("rbac", "create"))
):
    """Bulk assign roles to multiple users"""
    current_user, organization_id = auth

    logger.info(f"User {current_user.id} performing bulk role assignment")
    
    successful = 0
    failed = 0
    details = []
    
    for user_id in request.user_ids:
        try:
            if request.replace_existing:
                await rbac_service.remove_all_roles_from_user(user_id)
            
            assignments = await rbac_service.assign_multiple_roles_to_user(
                user_id, request.role_ids, assigned_by_id=current_user.id
            )
            successful += len(assignments)
            details.append(f"User {user_id}: assigned {len(assignments)} roles")
            
        except Exception as e:
            failed += 1
            details.append(f"User {user_id}: failed - {str(e)}")
    
    return BulkRoleAssignmentResponse(
        success=failed == 0,
        message=f"Bulk assignment completed. {successful} successful, {failed} failed.",
        successful_assignments=successful,
        failed_assignments=failed,
        details=details
    )