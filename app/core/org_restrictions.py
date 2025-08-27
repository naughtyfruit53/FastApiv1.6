# app/core/org_restrictions.py

"""
Organization data access restrictions for app-level super admins
"""

from fastapi import HTTPException, status
from app.models import User
from app.schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)


def require_organization_access(current_user: User) -> None:
    """
    Ensure that app super admins cannot access organization-specific data.
    App super admins should only have access to app-level features like license management.
    
    Args:
        current_user: The current authenticated user
        
    Raises:
        HTTPException: If user is an app super admin trying to access org data
    """
    is_app_super_admin = getattr(current_user, 'is_super_admin', False) and current_user.organization_id is None
    
    if is_app_super_admin:
        logger.warning(f"[require_organization_access] App super admin {current_user.email} attempted to access organization data")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App super administrators cannot access organization-specific data. Use license management features instead."
        )
    
    logger.debug(f"[require_organization_access] Organization access allowed for user {current_user.id} (org_id: {current_user.organization_id})")


def ensure_organization_context(current_user: User) -> int:
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


def require_current_organization_id(current_user: User) -> int:
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
    
    # Platform users and super admins never require organization context
    if hasattr(current_user, 'role') and current_user.role in ['super_admin', 'platform_admin']:
        logger.info(f"[require_current_organization_id] Platform user {current_user.email} doesn't require org context")
        return None
        
    if getattr(current_user, 'is_super_admin', False):
        logger.info(f"[require_current_organization_id] Super admin {current_user.email} doesn't require org context")
        return None
    
    # Organization users require organization_id
    if not current_user.organization_id:
        logger.error(f"[require_current_organization_id] Organization user {current_user.id} has no organization_id")
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Company setup required before importing inventory."
        )
    
    logger.info(f"[require_current_organization_id] Organization context required and found: org_id={current_user.organization_id}")
    return current_user.organization_id


def can_access_organization_data(user: User) -> bool:
    """
    Check if user can access organization-specific business data.
    
    Args:
        user: User to check
        
    Returns:
        bool: True if user can access organization data, False otherwise
    """
    # App super admins (no organization_id) cannot access organization data
    if getattr(user, 'is_super_admin', False) and user.organization_id is None:
        return False
    
    # Organization users can access their organization's data
    return user.organization_id is not None