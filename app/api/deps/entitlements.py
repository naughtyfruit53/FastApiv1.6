# app/api/deps/entitlements.py

"""
Unified dependency for entitlement checking.
Implements entitlement-first, RBAC-second approach with exceptions.
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Callable
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.services.entitlement_service import EntitlementService
from app.models.user_models import User

logger = logging.getLogger(__name__)

# Always-on modules (skip entitlement check)
ALWAYS_ON_MODULES = {'email'}

# RBAC-only modules (non-billable, skip entitlement check)
RBAC_ONLY_MODULES = {'settings', 'admin', 'administration'}

# Feature flag for entitlements gating (set to True to enable enforcement)
ENABLE_ENTITLEMENTS_GATING = True


class EntitlementDeniedError(HTTPException):
    """Custom exception for entitlement violations with standardized error body"""
    
    def __init__(
        self,
        module_key: str,
        submodule_key: Optional[str] = None,
        entitlement_status: str = "disabled",
        reason: str = "Access denied"
    ):
        detail = {
            "error_type": "entitlement_denied",
            "module_key": module_key,
            "submodule_key": submodule_key,
            "status": entitlement_status,
            "reason": reason,
            "message": f"Organization does not have access to module '{module_key}'. {reason}"
        }
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class PermissionDeniedError(HTTPException):
    """Custom exception for RBAC permission violations with standardized error body"""
    
    def __init__(
        self,
        permission: str,
        reason: str = "Insufficient permissions"
    ):
        detail = {
            "error_type": "permission_denied",
            "permission": permission,
            "reason": reason,
            "message": f"User does not have required permission '{permission}'. {reason}"
        }
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def require_entitlement(
    module_key: str,
    submodule_key: Optional[str] = None,
    allow_super_admin_bypass: bool = True,
    audit_bypass: bool = True
):
    """
    Unified dependency/decorator for entitlement checking.
    
    Implements entitlement-first, RBAC-second enforcement with exceptions:
    - Email: always-on (skip entitlement check)
    - Settings/Admin: RBAC-only (skip entitlement check)
    - Super Admin: bypass entitlement checks (with optional audit logging)
    
    Usage:
        @router.get("/sales/dashboard")
        async def get_sales_dashboard(
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(get_current_active_user),
            _: None = Depends(require_entitlement("sales"))
        ):
            # ... endpoint logic
    
        @router.get("/sales/leads")
        async def get_leads(
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(get_current_active_user),
            _: None = Depends(require_entitlement("sales", "lead_management"))
        ):
            # ... endpoint logic
    
    Args:
        module_key: Module key to check (e.g., "sales", "manufacturing")
        submodule_key: Optional submodule key (e.g., "lead_management")
        allow_super_admin_bypass: If True, super admins bypass entitlement checks
        audit_bypass: If True, log when super admin bypasses disabled module
    
    Returns:
        FastAPI dependency that checks entitlements
    
    Raises:
        EntitlementDeniedError: If organization lacks the required entitlement
    """
    
    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
    ) -> None:
        """Dependency that performs the entitlement check"""
        
        # Feature flag check
        if not ENABLE_ENTITLEMENTS_GATING:
            logger.debug(f"Entitlements gating disabled by feature flag for {module_key}")
            return
        
        # Exception 1: Email is always-on
        if module_key in ALWAYS_ON_MODULES:
            logger.debug(f"Module '{module_key}' is always-on, skipping entitlement check")
            return
        
        # Exception 2: Settings/Admin are RBAC-only (non-billable)
        if module_key in RBAC_ONLY_MODULES:
            logger.debug(f"Module '{module_key}' is RBAC-only, skipping entitlement check")
            return
        
        # Exception 3: Super Admin bypass
        if allow_super_admin_bypass and current_user.role == "super_admin":
            if audit_bypass:
                logger.info(
                    f"Super admin {current_user.email} (ID: {current_user.id}) "
                    f"bypassed entitlement check for {module_key}"
                    + (f"/{submodule_key}" if submodule_key else "")
                )
            return
        
        # Check entitlement
        service = EntitlementService(db)
        is_entitled, entitlement_status, reason = await service.check_entitlement(
            org_id=current_user.organization_id,
            module_key=module_key,
            submodule_key=submodule_key
        )
        
        if not is_entitled:
            logger.warning(
                f"User {current_user.email} (org_id: {current_user.organization_id}) "
                f"denied access to {module_key}"
                + (f"/{submodule_key}" if submodule_key else "")
                + f". Status: {entitlement_status}, Reason: {reason}"
            )
            raise EntitlementDeniedError(
                module_key=module_key,
                submodule_key=submodule_key,
                entitlement_status=entitlement_status or "disabled",
                reason=reason or "Access denied"
            )
        
        logger.debug(
            f"User {current_user.email} granted access to {module_key}"
            + (f"/{submodule_key}" if submodule_key else "")
            + f". Status: {entitlement_status}"
        )
    
    return dependency


async def check_entitlement_access(
    module_key: str,
    submodule_key: Optional[str],
    org_id: int,
    db: AsyncSession,
    user: Optional[User] = None,
    allow_super_admin_bypass: bool = True
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Helper function to check entitlement access without using as a dependency.
    Returns: (is_entitled, status, reason)
    
    Args:
        module_key: Module key to check
        submodule_key: Optional submodule key
        org_id: Organization ID
        db: Database session
        user: Optional user (for super admin bypass check)
        allow_super_admin_bypass: If True, super admins bypass entitlement checks
    
    Returns:
        Tuple of (is_entitled, status, reason)
    """
    
    # Feature flag check
    if not ENABLE_ENTITLEMENTS_GATING:
        return True, 'enabled', 'Feature flag disabled'
    
    # Exception 1: Email is always-on
    if module_key in ALWAYS_ON_MODULES:
        return True, 'enabled', 'Always-on module'
    
    # Exception 2: Settings/Admin are RBAC-only
    if module_key in RBAC_ONLY_MODULES:
        return True, 'enabled', 'RBAC-only module'
    
    # Exception 3: Super Admin bypass
    if user and allow_super_admin_bypass and user.role == "super_admin":
        return True, 'enabled', 'Super admin bypass'
    
    # Check entitlement
    service = EntitlementService(db)
    return await service.check_entitlement(
        org_id=org_id,
        module_key=module_key,
        submodule_key=submodule_key
    )


def require_permission_with_entitlement(
    module_key: str,
    permission: str,
    submodule_key: Optional[str] = None
):
    """
    Composed dependency that checks both entitlements and RBAC permissions.
    Enforces entitlement-first, then RBAC-second pattern.
    
    Usage:
        @router.post("/sales/leads")
        async def create_lead(
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(get_current_active_user),
            _: None = Depends(require_permission_with_entitlement("sales", "crm.create"))
        ):
            # ... endpoint logic
    
    Args:
        module_key: Module key to check
        permission: RBAC permission to check
        submodule_key: Optional submodule key
    
    Returns:
        FastAPI dependency that checks both entitlements and permissions
    """
    
    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
        _entitlement: None = Depends(require_entitlement(module_key, submodule_key))
    ) -> None:
        """Dependency that performs both entitlement and permission checks"""
        
        # Check RBAC permission
        from app.core.rbac import check_permission
        
        has_permission = await check_permission(
            db=db,
            user=current_user,
            permission=permission
        )
        
        if not has_permission:
            logger.warning(
                f"User {current_user.email} (org_id: {current_user.organization_id}) "
                f"denied access due to insufficient permissions. Required: {permission}"
            )
            raise PermissionDeniedError(
                permission=permission,
                reason=f"User lacks required permission '{permission}'"
            )
        
        logger.debug(
            f"User {current_user.email} granted access with permission {permission}"
        )
    
    return dependency
