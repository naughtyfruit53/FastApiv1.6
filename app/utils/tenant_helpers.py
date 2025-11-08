# app/utils/tenant_helpers.py

"""
Standardized tenant utility functions for organization isolation (Layer 1)
Provides helpers for tenant context management, validation, and filtering
"""

from typing import Optional, Type, TypeVar, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging

from app.core.tenant import TenantContext
from app.core.constants import ENFORCEMENT_ERRORS
from app.models.user_models import User, Organization

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


class TenantHelper:
    """Helper class for tenant operations"""

    @staticmethod
    def get_current_org_id() -> Optional[int]:
        """
        Get current organization ID from context
        
        Returns:
            int or None: Organization ID if set, None otherwise
        """
        return TenantContext.get_organization_id()

    @staticmethod
    def ensure_org_context() -> int:
        """
        Ensure organization context is set and return it
        
        Returns:
            int: Organization ID
            
        Raises:
            HTTPException: If organization context is not set
        """
        org_id = TenantContext.get_organization_id()
        if org_id is None:
            logger.error("Organization context not set when required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ENFORCEMENT_ERRORS["tenant_required"]
            )
        return org_id

    @staticmethod
    def validate_user_org_access(user: User, org_id: int) -> bool:
        """
        Validate user has access to organization
        
        Args:
            user: User object
            org_id: Organization ID to check
            
        Returns:
            bool: True if user has access, False otherwise
        """
        # Super admins have access to all orgs
        if user.is_super_admin or user.organization_id is None:
            return True
        
        # Regular users can only access their own org
        return user.organization_id == org_id

    @staticmethod
    def enforce_user_org_access(user: User, org_id: int) -> None:
        """
        Enforce user has access to organization, raise exception if not
        
        Args:
            user: User object
            org_id: Organization ID to check
            
        Raises:
            HTTPException: If user doesn't have access
        """
        if not TenantHelper.validate_user_org_access(user, org_id):
            logger.warning(
                f"User {user.email} (org={user.organization_id}) "
                f"attempted to access org {org_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ENFORCEMENT_ERRORS["tenant_mismatch"]
            )

    @staticmethod
    def apply_org_filter(
        stmt: select,
        model: Type[ModelType],
        org_id: Optional[int] = None,
        user: Optional[User] = None
    ) -> select:
        """
        Apply organization filter to SQLAlchemy statement
        
        Args:
            stmt: SQLAlchemy select statement
            model: Model class to filter
            org_id: Organization ID (uses context if not provided)
            user: User object for access validation
            
        Returns:
            select: Filtered statement
            
        Raises:
            HTTPException: If org_id required but not available or access denied
        """
        # Get org_id from context if not provided
        org_id = org_id or TenantContext.get_organization_id()
        
        # Check if model has organization_id field
        if not hasattr(model, 'organization_id'):
            logger.warning(f"Model {model.__name__} does not have organization_id field")
            return stmt
        
        # Super admin with explicit org_id can query that org
        if user and user.is_super_admin and org_id is not None:
            return stmt.where(model.organization_id == org_id)
        
        # Require org_id
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ENFORCEMENT_ERRORS["tenant_required"]
            )
        
        # Validate user access to org
        if user:
            TenantHelper.enforce_user_org_access(user, org_id)
        
        return stmt.where(model.organization_id == org_id)

    @staticmethod
    def validate_data_org_id(data: dict, user: User) -> dict:
        """
        Validate and set organization_id in data dictionary
        
        Args:
            data: Data dictionary to validate
            user: User performing the operation
            
        Returns:
            dict: Data with validated organization_id
            
        Raises:
            HTTPException: If validation fails
        """
        current_org_id = TenantContext.get_organization_id()
        
        # Super admins must specify org_id
        if user.is_super_admin:
            if 'organization_id' not in data or data['organization_id'] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Super admins must specify organization_id"
                )
            return data
        
        # Regular users cannot specify different org_id
        if 'organization_id' in data and data['organization_id'] is not None:
            if data['organization_id'] != user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ENFORCEMENT_ERRORS["tenant_mismatch"]
                )
        
        # Set org_id from user
        data['organization_id'] = user.organization_id
        return data

    @staticmethod
    def validate_record_org_access(
        obj: Any,
        org_id: Optional[int] = None,
        raise_404: bool = True
    ) -> None:
        """
        Validate a record belongs to the organization
        
        Args:
            obj: Object to validate
            org_id: Organization ID to check against (uses context if not provided)
            raise_404: If True, raise 404 instead of 403 for security
            
        Raises:
            HTTPException: If record doesn't belong to org
        """
        org_id = org_id or TenantContext.get_organization_id()
        
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ENFORCEMENT_ERRORS["tenant_required"]
            )
        
        if hasattr(obj, 'organization_id') and obj.organization_id != org_id:
            logger.warning(
                f"Attempted to access record with org_id={obj.organization_id} "
                f"from context org_id={org_id}"
            )
            status_code = status.HTTP_404_NOT_FOUND if raise_404 else status.HTTP_403_FORBIDDEN
            detail = "Resource not found" if raise_404 else ENFORCEMENT_ERRORS["tenant_mismatch"]
            raise HTTPException(status_code=status_code, detail=detail)

    @staticmethod
    async def get_org_or_404(
        db: AsyncSession,
        org_id: int
    ) -> Organization:
        """
        Get organization by ID or raise 404
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            Organization: Organization object
            
        Raises:
            HTTPException: If organization not found
        """
        result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return org

    @staticmethod
    def set_org_context(org_id: int, user_id: Optional[int] = None) -> None:
        """
        Set organization context (and optionally user context)
        
        Args:
            org_id: Organization ID to set
            user_id: Optional user ID to set
        """
        TenantContext.set_organization_id(org_id)
        logger.debug(f"Set organization context: org_id={org_id}")
        
        if user_id is not None:
            TenantContext.set_user_id(user_id)
            logger.debug(f"Set user context: user_id={user_id}")

    @staticmethod
    def clear_context() -> None:
        """Clear tenant context"""
        TenantContext.clear()
        logger.debug("Cleared tenant context")


# Convenience functions for common operations

def get_current_org_id() -> Optional[int]:
    """Get current organization ID from context"""
    return TenantHelper.get_current_org_id()


def ensure_org_context() -> int:
    """Ensure organization context is set"""
    return TenantHelper.ensure_org_context()


def validate_user_org_access(user: User, org_id: int) -> bool:
    """Validate user has access to organization"""
    return TenantHelper.validate_user_org_access(user, org_id)


def enforce_user_org_access(user: User, org_id: int) -> None:
    """Enforce user has access to organization"""
    TenantHelper.enforce_user_org_access(user, org_id)


def apply_org_filter(
    stmt: select,
    model: Type[ModelType],
    org_id: Optional[int] = None,
    user: Optional[User] = None
) -> select:
    """Apply organization filter to statement"""
    return TenantHelper.apply_org_filter(stmt, model, org_id, user)


def validate_data_org_id(data: dict, user: User) -> dict:
    """Validate and set organization_id in data"""
    return TenantHelper.validate_data_org_id(data, user)


def validate_record_org_access(
    obj: Any,
    org_id: Optional[int] = None,
    raise_404: bool = True
) -> None:
    """Validate record belongs to organization"""
    TenantHelper.validate_record_org_access(obj, org_id, raise_404)
