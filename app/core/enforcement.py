# app/core/enforcement.py

"""
Centralized RBAC and tenant isolation enforcement utilities.
This module provides unified enforcement of organization scoping and permission checks.
"""

from typing import Optional, Callable, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantContext, require_current_organization_id
from app.services.rbac import RBACService
import logging

# Import entitlement checking at module level to avoid circular dependencies
try:
    from app.api.deps.entitlements import check_entitlement_access, EntitlementDeniedError
except ImportError:
    # Fallback if entitlements module not available
    check_entitlement_access = None
    EntitlementDeniedError = None

logger = logging.getLogger(__name__)


class EnforcementError(HTTPException):
    """Custom exception for enforcement failures"""
    pass


class TenantEnforcement:
    """Tenant isolation enforcement utilities"""
    
    @staticmethod
    def get_organization_id(current_user: User = Depends(get_current_active_user)) -> int:
        """
        Get and enforce organization ID for the current user.
        
        Args:
            current_user: The authenticated user
            
        Returns:
            int: The organization ID
            
        Raises:
            HTTPException: If organization context is missing or invalid
        """
        return require_current_organization_id(current_user)
    
    @staticmethod
    def enforce_organization_access(
        obj,
        organization_id: int,
        resource_name: str = "Resource"
    ) -> None:
        """
        Enforce that an object belongs to the specified organization.
        
        Args:
            obj: The database object to check
            organization_id: The required organization ID
            resource_name: Name of the resource for error messages
            
        Raises:
            HTTPException: If object doesn't belong to the organization
        """
        if not hasattr(obj, 'organization_id'):
            logger.warning(f"{resource_name} model lacks organization_id field")
            return
        
        if obj.organization_id != organization_id:
            logger.warning(
                f"Organization mismatch: {resource_name} belongs to org {obj.organization_id}, "
                f"user attempted access from org {organization_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{resource_name} not found"
            )
    
    @staticmethod
    def filter_by_organization(
        stmt: select,
        model_class,
        organization_id: int
    ) -> select:
        """
        Add organization filter to a SQLAlchemy query.
        
        Args:
            stmt: The SQLAlchemy select statement
            model_class: The model class being queried
            organization_id: The organization ID to filter by
            
        Returns:
            The modified select statement
        """
        if not hasattr(model_class, 'organization_id'):
            logger.warning(f"Model {model_class.__name__} lacks organization_id field")
            return stmt
        
        return stmt.where(model_class.organization_id == organization_id)


class RBACEnforcement:
    """RBAC permission enforcement utilities"""
    
    @staticmethod
    def check_permission(
        user: User,
        module: str,
        action: str,
        db: Session
    ) -> bool:
        """
        Check if user has permission for a module action.
        
        Args:
            user: The user to check
            module: The module name (e.g., 'inventory', 'voucher')
            action: The action (e.g., 'create', 'read', 'update', 'delete')
            db: Database session
            
        Returns:
            True if user has permission
            
        Raises:
            HTTPException: If user lacks permission
        """
        # Super admins bypass checks
        if getattr(user, 'is_super_admin', False):
            return True
        
        # Build permission string
        permission = f"{module}_{action}"
        
        # Check service permission through RBAC
        rbac_service = RBACService(db)
        
        if rbac_service.user_has_permission(user.id, permission):
            logger.debug(f"User {user.id} has permission: {permission}")
            return True
        
        logger.warning(
            f"User {user.id} denied access - missing permission: {permission}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {permission}"
        )
    
    @staticmethod
    def require_module_permission(module: str, action: str):
        """
        Create a dependency that requires a specific module permission.
        
        Args:
            module: The module name
            action: The action to check
            
        Returns:
            A FastAPI dependency function
        """
        def dependency(
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db)
        ) -> User:
            RBACEnforcement.check_permission(current_user, module, action, db)
            return current_user
        
        return dependency


def enforce_tenant_and_permission(
    module: str,
    action: str
):
    """
    Combined dependency that enforces both tenant isolation and RBAC.
    
    Args:
        module: The module name
        action: The action to check
        
    Returns:
        A tuple of (user, organization_id) dependencies
        
    Example:
        @router.get("/items")
        async def get_items(
            user: User = Depends(enforce_tenant_and_permission("inventory", "read")[0]),
            org_id: int = Depends(enforce_tenant_and_permission("inventory", "read")[1]),
            db: Session = Depends(get_db)
        ):
            ...
    """
    user_dep = RBACEnforcement.require_module_permission(module, action)
    org_dep = TenantEnforcement.get_organization_id
    
    return (user_dep, org_dep)


class CombinedEnforcement:
    """
    Combined enforcement for convenience with entitlement-first, RBAC-second pattern.
    
    This class implements a three-tier access control hierarchy:
    1. Entitlement check (org-level): Does the organization have access to this module?
    2. RBAC check (user-level): Does the user have permission for this action?
    3. Tenant isolation: Ensure data access is scoped to the correct organization
    
    Example usage:
        @router.get("/sales/leads")
        async def get_leads(
            auth: tuple = Depends(require_access("crm", "read")),
            db: Session = Depends(get_db)
        ):
            current_user, org_id = auth
            # Business logic here
            
        @router.get("/sales/reports")
        async def get_reports(
            auth: tuple = Depends(require_access("crm", "read", "advanced_analytics")),
            db: Session = Depends(get_db)
        ):
            current_user, org_id = auth
            # Business logic with submodule check
    """
    
    def __init__(self, module: str, action: str, submodule: Optional[str] = None):
        self.module = module
        self.action = action
        self.submodule = submodule
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> tuple[User, Optional[int]]:
        """
        Enforce entitlements first, then RBAC, then tenant isolation.
        
        Order of checks:
        1. Entitlement check (org-level access)
        2. RBAC permission check (user-level access)
        3. Tenant isolation enforcement
        
        Returns:
            Tuple of (user, organization_id or None for super_admin)
        """
        # Get organization ID (None for super_admin without context)
        org_id = require_current_organization_id(current_user)
        
        # Step 1: Check entitlement (org-level access)
        if check_entitlement_access is None or EntitlementDeniedError is None:
            # Entitlements not available, skip check
            logger.warning("Entitlements module not available, skipping entitlement check")
        else:
            is_entitled, entitlement_status, reason = await check_entitlement_access(
                module_key=self.module,
                submodule_key=self.submodule,
                org_id=org_id,
                db=db,
                user=current_user,
                allow_super_admin_bypass=True
            )
            
            if not is_entitled:
                logger.warning(
                    f"User ID {current_user.id} (org_id: {org_id}) "
                    f"denied access to {self.module}/{self.submodule or 'all'} due to entitlement. "
                    f"Status: {entitlement_status}, Reason: {reason}"
                )
                raise EntitlementDeniedError(
                    module_key=self.module,
                    submodule_key=self.submodule,
                    entitlement_status=entitlement_status or "disabled",
                    reason=reason or "Access denied"
                )
        
        # Step 2: Check RBAC permission (user-level access)
        RBACEnforcement.check_permission(current_user, self.module, self.action, db)
        
        # Step 3: Return user and org_id for tenant isolation
        return current_user, org_id


def require_access(module: str, action: str, submodule: Optional[str] = None):
    """
    Convenience function to create a combined enforcement dependency.
    
    Implements entitlement-first, RBAC-second pattern with tenant isolation.
    
    Args:
        module: The module name (e.g., "crm", "manufacturing")
        action: The RBAC action to check (e.g., "read", "write")
        submodule: Optional submodule name for fine-grained entitlement control
        
    Returns:
        A CombinedEnforcement instance
        
    Example:
        @router.get("/items")
        async def get_items(
            auth: tuple = Depends(require_access("inventory", "read")),
            db: Session = Depends(get_db)
        ):
            user, org_id = auth
            ...
        
        @router.get("/sales/leads")
        async def get_leads(
            auth: tuple = Depends(require_access("crm", "read", "lead_management")),
            db: Session = Depends(get_db)
        ):
            user, org_id = auth
            ...
    """
    return CombinedEnforcement(module, action, submodule)


# Query helper for common pattern
async def get_organization_scoped_query(
    model_class,
    organization_id: int,
    db: AsyncSession,
    filters: Optional[dict] = None
):
    """
    Create an organization-scoped query.
    
    Args:
        model_class: The SQLAlchemy model class
        organization_id: The organization ID to scope to
        db: Async database session
        filters: Optional additional filters as dict
        
    Returns:
        SQLAlchemy select statement
    """
    stmt = select(model_class)
    
    # Add organization filter
    if hasattr(model_class, 'organization_id'):
        stmt = stmt.where(model_class.organization_id == organization_id)
    else:
        logger.warning(f"Model {model_class.__name__} lacks organization_id field")
    
    # Add additional filters
    if filters:
        for field, value in filters.items():
            if hasattr(model_class, field):
                stmt = stmt.where(getattr(model_class, field) == value)
    
    return stmt