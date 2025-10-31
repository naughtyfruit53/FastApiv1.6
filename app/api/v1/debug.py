# app/api/v1/debug.py

"""
Debug endpoints for troubleshooting RBAC and organization state
Protected by authentication - useful for diagnosing permission issues
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User, Organization
from app.services.rbac import RBACService
from app.core.rbac_dependencies import get_rbac_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rbac_state")
async def get_rbac_state(
    current_user: User = Depends(get_current_active_user),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive RBAC state for the current user.
    Useful for debugging permission and organization issues.
    
    Returns:
        - User info (id, email, role, is_super_admin)
        - Organization info (if applicable)
        - Service roles assigned
        - Effective permissions
        - Organization modules (if applicable)
    """
    try:
        # Get user basic info
        user_info = {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "is_super_admin": getattr(current_user, 'is_super_admin', False),
            "is_active": current_user.is_active,
            "organization_id": current_user.organization_id
        }
        
        # Get organization info if user has one
        org_info = None
        org_modules = None
        if current_user.organization_id:
            result = await db.execute(
                select(Organization).filter(Organization.id == current_user.organization_id)
            )
            org = result.scalars().first()
            if org:
                org_info = {
                    "id": org.id,
                    "name": org.name,
                    "is_active": org.is_active,
                    "max_users": org.max_users
                }
                org_modules = org.enabled_modules or {}
        
        # Get service roles
        try:
            service_roles = await rbac_service.get_user_roles(current_user.id)
            roles_info = [
                {
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "is_active": role.is_active
                }
                for role in service_roles
            ]
        except Exception as e:
            logger.error(f"Error fetching service roles: {e}")
            roles_info = []
        
        # Get effective permissions
        try:
            permissions = await rbac_service.get_user_permissions(current_user.id)
            permissions_list = list(permissions)
        except Exception as e:
            logger.error(f"Error fetching permissions: {e}")
            permissions_list = []
        
        return {
            "user": user_info,
            "organization": org_info,
            "organization_modules": org_modules,
            "service_roles": roles_info,
            "effective_permissions": permissions_list,
            "total_permissions": len(permissions_list),
            "summary": {
                "has_organization": current_user.organization_id is not None,
                "is_super_admin": getattr(current_user, 'is_super_admin', False),
                "has_service_roles": len(roles_info) > 0,
                "has_permissions": len(permissions_list) > 0
            }
        }
    except Exception as e:
        logger.error(f"Error fetching RBAC state: {e}", exc_info=True)
        return {
            "error": "Failed to fetch RBAC state",
            "detail": str(e),
            "user": {
                "id": current_user.id,
                "email": current_user.email
            }
        }
