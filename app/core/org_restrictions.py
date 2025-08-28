# app/core/org_restrictions.py

"""
Organization data access restrictions for app-level super admins
"""

from fastapi import HTTPException, status
from typing import Union, Optional
from app.schemas.user import UserInDB, PlatformUserInDB, CurrentUser
import logging

logger = logging.getLogger(__name__)


def require_organization_access(current_user: CurrentUser) -> None:
    """
    Ensure that app super admins cannot access organization-specific data.
    App super admins should only have access to app-level features like license management.
    
    Args:
        current_user: The current authenticated user
        
    Raises:
        HTTPException: If user is an app super admin trying to access org data
    """
    organization_id = getattr(current_user, 'organization_id', None)
    
    if organization_id is None:
        logger.warning(f"[require_organization_access] App super admin {current_user.email} attempted to access organization data")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App super administrators cannot access organization-specific data. Use license management features instead."
        )
    
    logger.debug(f"[require_organization_access] Organization access allowed for user {current_user.id} (org_id: {organization_id})")


def ensure_organization_context(current_user: CurrentUser) -> Optional[int]:
    """
    Ensure user has an organization context and is not an app super admin.
    
    This function is deprecated - use require_current_organization_id instead
    for clearer logic about platform vs organization users.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        int: The organization ID
        
    Raises:
        HTTPException: If user doesn't have organization context or is app super admin
    """
    logger.warning(f"[ensure_organization_context] DEPRECATED - use require_current_organization_id instead")
    return require_current_organization_id(current_user)


def require_current_organization_id(current_user: CurrentUser) -> int:
    """
    Require organization ID for users who need organization context.
    
    Platform users (super_admin/platform_admin) never require organization context.
    Only organization users (non-super_admin) require valid organization_id.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        int: The organization ID for users who need it
        
    Raises:
        HTTPException: If user requires but lacks organization context
    """
    logger.info(f"[require_current_organization_id] Checking requirement for user {current_user.id} ({current_user.email})")
    
    organization_id = getattr(current_user, 'organization_id', None)
    if organization_id is None:
        logger.error(f"[require_current_organization_id] User {current_user.id} has no organization_id")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires an organization context"
        )
    
    logger.info(f"[require_current_organization_id] Organization context required and found: org_id={organization_id}")
    return organization_id


def can_access_organization_data(user: CurrentUser) -> bool:
    """
    Check if user can access organization-specific business data.
    
    Args:
        user: User to check
        
    Returns:
        bool: True if user can access organization data, False otherwise
    """
    organization_id = getattr(user, 'organization_id', None)
    return organization_id is not None