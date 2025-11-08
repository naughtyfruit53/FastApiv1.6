# app/api/v1/admin_categories.py

"""
Admin API endpoints for category-based entitlement management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_super_admin
from app.services.entitlement_service import EntitlementService
from app.models.user_models import User
from app.core.module_categories import (
    get_all_category_info,
    get_category_info,
    CATEGORY_DISPLAY_NAMES,
    CATEGORY_DESCRIPTIONS
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/categories", tags=["admin-categories"])


class CategoryInfo(BaseModel):
    """Category information response"""
    key: str = Field(..., description="Category key")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Description")
    modules: List[str] = Field(..., description="List of module keys in this category")
    module_count: int = Field(..., description="Number of modules")


class CategoryListResponse(BaseModel):
    """Response for listing all categories"""
    categories: List[CategoryInfo]


class ActivateCategoryRequest(BaseModel):
    """Request to activate a category"""
    category: str = Field(..., description="Category key to activate")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for activation")


class DeactivateCategoryRequest(BaseModel):
    """Request to deactivate a category"""
    category: str = Field(..., description="Category key to deactivate")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for deactivation")


class OrgActivatedCategoriesResponse(BaseModel):
    """Response for organization's activated categories"""
    org_id: int
    activated_categories: List[str]


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    current_user: User = Depends(get_current_super_admin)
):
    """
    Get all available product categories.
    
    **Requires:** super_admin role
    
    Returns the complete list of product categories with their descriptions and module counts.
    """
    try:
        categories = get_all_category_info()
        return CategoryListResponse(categories=categories)
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get("/{category}", response_model=CategoryInfo)
async def get_category(
    category: str,
    current_user: User = Depends(get_current_super_admin)
):
    """
    Get details of a specific category.
    
    **Requires:** super_admin role
    """
    try:
        info = get_category_info(category)
        if not info or not info.get('modules'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        return CategoryInfo(**info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category {category}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category '{category}'"
        )


@router.post("/orgs/{org_id}/activate")
async def activate_category_for_org(
    org_id: int,
    request: ActivateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Activate a product category for an organization.
    This instantly enables all modules in the category.
    
    **Requires:** super_admin role
    """
    try:
        service = EntitlementService(db)
        result = await service.activate_category(
            org_id=org_id,
            category=request.category,
            actor_user_id=current_user.id,
            reason=request.reason
        )
        return result
    except ValueError as e:
        logger.warning(f"Invalid category activation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error activating category for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate category"
        )


@router.post("/orgs/{org_id}/deactivate")
async def deactivate_category_for_org(
    org_id: int,
    request: DeactivateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Deactivate a product category for an organization.
    This disables all modules in the category.
    
    **Requires:** super_admin role
    """
    try:
        service = EntitlementService(db)
        result = await service.deactivate_category(
            org_id=org_id,
            category=request.category,
            actor_user_id=current_user.id,
            reason=request.reason
        )
        return result
    except ValueError as e:
        logger.warning(f"Invalid category deactivation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deactivating category for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate category"
        )


@router.get("/orgs/{org_id}/activated", response_model=OrgActivatedCategoriesResponse)
async def get_activated_categories_for_org(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Get list of activated categories for an organization.
    
    **Requires:** super_admin role
    """
    try:
        service = EntitlementService(db)
        activated = await service.get_activated_categories(org_id)
        return OrgActivatedCategoriesResponse(
            org_id=org_id,
            activated_categories=activated
        )
    except Exception as e:
        logger.error(f"Error fetching activated categories for org {org_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch activated categories"
        )
