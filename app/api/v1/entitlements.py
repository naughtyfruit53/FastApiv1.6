# app/api/v1/entitlements.py

"""
App-level API endpoints for accessing organization entitlements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.database import get_async_db
from app.api.v1.auth import get_current_active_user
from app.services.entitlement_service import EntitlementService
from app.schemas.entitlement_schemas import AppEntitlementsResponse
from app.models.user_models import User
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orgs", tags=["entitlements"])


@router.get("/{org_id}/entitlements", response_model=AppEntitlementsResponse)
async def get_app_entitlements(
    org_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get effective entitlements for an organization (app use, cached).
    
    **Requires:** Authenticated user with access to the organization
    
    Returns a map of module_key to entitlement status and submodules.
    This endpoint is optimized for frontend use and cached with TTL.
    """
    # Verify user has access to the organization
    if current_user.organization_id != org_id and current_user.role != "super_admin":
        logger.warning(
            f"User {current_user.email} (org_id: {current_user.organization_id}) "
            f"attempted to access entitlements for org {org_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization's entitlements"
        )
    
    # Check cache first
    cache_key = f"entitlements:org:{org_id}"
    cached_result = await cache_manager.get(cache_key) if hasattr(cache_manager, 'get') else None
    
    if cached_result:
        logger.debug(f"Returning cached entitlements for org {org_id}")
        return cached_result
    
    try:
        service = EntitlementService(db)
        entitlements = await service.get_app_entitlements(org_id)
        
        # Cache the result (TTL: 5 minutes)
        if hasattr(cache_manager, 'set'):
            await cache_manager.set(cache_key, entitlements, ttl=300)
        
        return entitlements
    except Exception as e:
        logger.error(f"Error fetching app entitlements for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch organization entitlements"
        )


async def invalidate_entitlements_cache(org_id: int):
    """Helper function to invalidate entitlements cache for an organization"""
    cache_key = f"entitlements:org:{org_id}"
    if hasattr(cache_manager, 'delete'):
        await cache_manager.delete(cache_key)
        logger.info(f"Invalidated entitlements cache for org {org_id}")
