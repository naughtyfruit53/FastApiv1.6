# app/api/v1/rbac.py

"""
Service CRM RBAC API endpoints for role and permission management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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

# Permission Management Endpoints
@router.get("/permissions", response_model=List[ServicePermissionInDB])
async def get_service_permissions(
    module: Optional[str] = Query(None, description="Filter by module"),
    action: Optional[str] = Query(None, description="Filter by action"),
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Get all service permissions with optional filtering"""
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
    current_user: User = Depends(require_role_management_permission)
):
    """Initialize default service permissions (admin only)"""
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
    current_user: User = Depends(require_role_management_permission),
    _: int = Depends(require_same_organization)
):
    """Get all service roles for an organization, excluding super_admin for non-super admins"""
    try:
        # Validate organization_id is positive
        if organization_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization_id. Must be a positive integer."
            )
        
        logger.info(f"User {current_user.id} requesting roles for organization {organization_id}")
        roles = await rbac_service.get_roles(organization_id, is_active=is_active, exclude_super_admin=not current_user.is_super_admin)
        return roles
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching roles for organization {organization_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization roles: {str(e)}"
        )

@router.post("/organizations/{organization_id}/roles", response_model=ServiceRoleInDB)
async def create_service_role(
    organization_id: int,
    role: ServiceRoleCreate,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission),
    _: int = Depends(require_same_organization)
):
    """Create a new service role, preventing org admins from creating super_admin role"""
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
            detail=f"Failed to create role: {str(e)}"
        )

@router.get("/roles/{role_id}", response_model=ServiceRoleWithPermissions)
async def get_service_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Get a specific service role with its permissions"""
    try:
        logger.info(f"User {current_user.id} requesting role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else current_user.organization_id
        
        role = await rbac_service.get_role_with_permissions(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if organization_id and role.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to role from different organization"
            )
        
        role_dict = role.__dict__.copy()
        role_dict['permissions'] = [rp.permission for rp in role.role_permissions]
        
        return role_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch role: {str(e)}"
        )

@router.put("/roles/{role_id}", response_model=ServiceRoleInDB)
async def update_service_role(
    role_id: int,
    updates: ServiceRoleUpdate,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Update a service role"""
    try:
        logger.info(f"User {current_user.id} updating role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else current_user.organization_id
        
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
            detail=f"Failed to update role: {str(e)}"
        )

@router.delete("/roles/{role_id}")
async def delete_service_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Delete a service role"""
    try:
        logger.info(f"User {current_user.id} deleting role {role_id}")
        
        organization_id = None if getattr(current_user, 'is_super_admin', False) else current_user.organization_id
        
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
            detail=f"Failed to delete role: {str(e)}"
        )

@router.post("/organizations/{organization_id}/roles/initialize")
async def initialize_default_roles(
    organization_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission),
    _: int = Depends(require_same_organization)
):
    """Initialize default service roles for an organization"""
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
            detail=f"Failed to initialize default roles: {str(e)}"
        )

# User Role Assignment Endpoints
@router.post("/users/{user_id}/roles", response_model=RoleAssignmentResponse)
async def assign_roles_to_user(
    user_id: int,
    assignment: RoleAssignmentRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Assign service roles to a user"""
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
    current_user: User = Depends(require_role_management_permission)
):
    """Remove a specific role from a user"""
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
            detail=f"Failed to remove role: {str(e)}"
        )

@router.delete("/users/{user_id}/roles")
async def remove_all_roles_from_user(
    user_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Remove all service roles from a user"""
    logger.info(f"User {current_user.id} removing all roles from user {user_id}")
    
    count = await rbac_service.remove_all_service_roles_from_user(user_id)
    return {"message": f"Removed {count} role assignments"}

@router.get("/users/{user_id}/roles", response_model=List[ServiceRoleInDB])
async def get_user_service_roles(
    user_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all service roles assigned to a user, including self"""
    logger.info(f"User {current_user.id} requesting roles for user {user_id}")
    
    # Allow users to view their own roles
    if current_user.id != user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view other users' roles"
        )
    
    roles = await rbac_service.get_user_service_roles(user_id)
    return roles

@router.get("/roles/{role_id}/users", response_model=List[UserWithServiceRoles])
async def get_users_with_role(
    role_id: int,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Get all users assigned to a specific role"""
    logger.info(f"User {current_user.id} requesting users with role {role_id}")
    
    users = await rbac_service.get_users_with_role(role_id)
    
    result = []
    for user in users:
        user_roles = await rbac_service.get_user_service_roles(user.id)
        result.append(UserWithServiceRoles(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            service_roles=user_roles
        ))
    
    return result

# Permission Checking Endpoints
@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_user_permission(
    request: PermissionCheckRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(get_current_active_user)
):
    """Check if a user has a specific permission, including self"""
    logger.info(f"User {current_user.id} checking permission '{request.permission}' for user {request.user_id}")
    
    # Allow users to check their own permissions
    if current_user.id != request.user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to check other users' permissions"
        )
    
    has_permission = await rbac_service.user_has_service_permission(request.user_id, request.permission)
    
    source = "none"
    if has_permission:
        user_roles = await rbac_service.get_user_service_roles(request.user_id)
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
    current_user: User = Depends(get_current_active_user)
):
    """Get all permissions for a user, including self"""
    logger.info(f"User {current_user.id} requesting permissions for user {user_id}")
    
    # Allow users to view their own permissions
    if current_user.id != user_id and current_user.role not in ["admin", "org_admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view other users' permissions"
        )
    
    permissions = await rbac_service.get_user_service_permissions(user_id)
    roles = await rbac_service.get_user_service_roles(user_id)
    
    return {
        "user_id": user_id,
        "permissions": list(permissions),
        "service_roles": roles,
        "total_permissions": len(permissions)
    }

# Bulk Operations
@router.post("/roles/assign/bulk", response_model=BulkRoleAssignmentResponse)
async def bulk_assign_roles(
    request: BulkRoleAssignmentRequest,
    rbac_service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(require_role_management_permission)
):
    """Bulk assign roles to multiple users"""
    logger.info(f"User {current_user.id} performing bulk role assignment")
    
    successful = 0
    failed = 0
    details = []
    
    for user_id in request.user_ids:
        try:
            if request.replace_existing:
                await rbac_service.remove_all_service_roles_from_user(user_id)
            
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