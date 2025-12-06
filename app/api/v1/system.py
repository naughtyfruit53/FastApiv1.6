"""
System information endpoints for feature detection and configuration.

Provides endpoints for frontend to detect backend capabilities and configuration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.core.permissions import LEGACY_PERMISSION_MAP, PERMISSION_HIERARCHY
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/permission-format")
async def get_permission_format(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get permission format configuration for frontend feature detection.
    
    This endpoint allows the frontend to detect:
    - Primary permission format (dotted)
    - Whether backward compatibility mode is enabled
    - Legacy formats supported
    - Whether permission hierarchy is enabled
    
    Returns:
        {
            "primary_format": "dotted",
            "compatibility": true,
            "legacy_formats": ["underscore", "colon"],
            "hierarchy_enabled": true,
            "version": "1.0",
            "migration_status": "in_progress"
        }
    """
    # Check if compatibility mode is enabled (always true for now, will be disabled after migration)
    compatibility_enabled = True  # TODO: Make this configurable via env var
    
    # Determine legacy formats supported
    legacy_formats = []
    if compatibility_enabled:
        # Check which legacy format types exist in the mapping
        has_underscore = any('_' in key for key in LEGACY_PERMISSION_MAP.keys())
        has_colon = any(':' in key for key in LEGACY_PERMISSION_MAP.keys())
        
        if has_underscore:
            legacy_formats.append("underscore")
        if has_colon:
            legacy_formats.append("colon")
    
    # Check if hierarchy is enabled
    hierarchy_enabled = len(PERMISSION_HIERARCHY) > 0
    
    response = {
        "primary_format": "dotted",
        "compatibility": compatibility_enabled,
        "legacy_formats": legacy_formats,
        "hierarchy_enabled": hierarchy_enabled,
        "version": "1.0",
        "migration_status": "in_progress",  # TODO: Update when migration is complete
        "total_legacy_mappings": len(LEGACY_PERMISSION_MAP),
        "total_hierarchy_rules": len(PERMISSION_HIERARCHY),
    }
    
    logger.info(
        f"Permission format check by user {current_user.id}: "
        f"primary={response['primary_format']}, "
        f"compatibility={response['compatibility']}, "
        f"hierarchy={response['hierarchy_enabled']}"
    )
    
    return response


@router.get("/permission-format/mappings")
async def get_permission_mappings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get legacy permission mappings (for development/debugging).
    
    Returns the complete mapping of legacy permission formats to new dotted format.
    Useful for frontend developers during migration.
    
    Note: This endpoint may be removed after migration is complete.
    """
    # Only allow super admins and org admins to access mappings
    if not (current_user.is_super_admin or current_user.role.lower() in ['super_admin', 'org_admin']):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access permission mappings"
        )
    
    logger.info(f"Permission mappings requested by admin user {current_user.id}")
    
    return {
        "legacy_to_dotted": LEGACY_PERMISSION_MAP,
        "total_mappings": len(LEGACY_PERMISSION_MAP)
    }


@router.get("/permission-format/hierarchy")
async def get_permission_hierarchy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get permission hierarchy configuration (for development/debugging).
    
    Returns the permission hierarchy showing which parent permissions grant child permissions.
    Useful for frontend developers to understand permission implications.
    
    Note: This endpoint may be removed after migration is complete.
    """
    # Only allow super admins and org admins to access hierarchy
    if not (current_user.is_super_admin or current_user.role.lower() in ['super_admin', 'org_admin']):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access permission hierarchy"
        )
    
    logger.info(f"Permission hierarchy requested by admin user {current_user.id}")
    
    return {
        "hierarchy": PERMISSION_HIERARCHY,
        "total_parent_permissions": len(PERMISSION_HIERARCHY),
        "total_child_permissions": sum(len(children) for children in PERMISSION_HIERARCHY.values())
    }
