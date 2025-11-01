# app/api/v1/admin_entitlements.py

"""
Admin API endpoints for managing organization entitlements (super_admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_async_db
from app.api.v1.auth import get_current_super_admin
from app.services.entitlement_service import EntitlementService
from app.schemas.entitlement_schemas import (
    ModulesListResponse, ModuleResponse, OrgEntitlementsResponse,
    UpdateEntitlementsRequest, UpdateEntitlementsResponse
)
from app.models.user_models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin-entitlements"])


@router.get("/modules", response_model=ModulesListResponse)
async def get_modules(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Get all modules and submodules in the taxonomy.
    
    **Requires:** super_admin role
    
    Returns the complete module taxonomy with all submodules.
    """
    try:
        service = EntitlementService(db)
        modules = await service.get_all_modules()
        return ModulesListResponse(modules=modules)
    except Exception as e:
        logger.error(f"Error fetching modules: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch modules"
        )


@router.get("/orgs/{org_id}/entitlements", response_model=OrgEntitlementsResponse)
async def get_org_entitlements(
    org_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Get effective entitlements for an organization.
    
    **Requires:** super_admin role
    
    Returns all module and submodule entitlements for the specified organization,
    including status (enabled/disabled/trial), trial expiration dates, and source.
    """
    try:
        service = EntitlementService(db)
        entitlements = await service.get_org_entitlements(org_id)
        return entitlements
    except ValueError as e:
        logger.warning(f"Organization {org_id} not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching entitlements for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch organization entitlements"
        )


@router.put("/orgs/{org_id}/entitlements", response_model=UpdateEntitlementsResponse)
async def update_org_entitlements(
    org_id: int,
    request_body: UpdateEntitlementsRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Update organization entitlements (diff-only changes).
    
    **Requires:** super_admin role
    
    Apply module and submodule entitlement changes for an organization.
    Creates an audit event with the diff and reason.
    
    **Request Body:**
    - `reason`: Explanation for the change (required, 10-500 chars)
    - `changes.modules`: List of module-level changes (status, trial_expires_at)
    - `changes.submodules`: List of submodule-level changes (enabled/disabled)
    
    **Response:**
    Returns the updated entitlements along with the event ID for audit purposes.
    """
    try:
        service = EntitlementService(db)
        result = await service.update_org_entitlements(
            org_id=org_id,
            request=request_body,
            actor_user_id=current_user.id
        )
        
        logger.info(
            f"Super admin {current_user.email} (ID: {current_user.id}) updated entitlements "
            f"for org {org_id}. Event ID: {result.event_id}. Reason: {request_body.reason}"
        )
        
        return result
    except ValueError as e:
        logger.warning(f"Validation error updating entitlements for org {org_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating entitlements for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization entitlements"
        )
