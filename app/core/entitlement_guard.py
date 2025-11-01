# app/core/entitlement_guard.py

"""
Middleware and decorators for entitlement checking
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Callable
import logging

from app.core.database import get_async_db
from app.services.entitlement_service import EntitlementService
from app.models.user_models import User

logger = logging.getLogger(__name__)


class EntitlementGuardException(HTTPException):
    """Custom exception for entitlement violations"""
    
    def __init__(
        self,
        module_key: str,
        submodule_key: Optional[str] = None,
        entitlement_status: str = "disabled",
        reason: str = "Access denied"
    ):
        detail = {
            "error": "entitlement_required",
            "module_key": module_key,
            "submodule_key": submodule_key,
            "status": entitlement_status,
            "reason": reason,
            "message": f"Module '{module_key}' access denied: {reason}"
        }
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def require_entitlement(module_key: str, submodule_key: Optional[str] = None):
    """
    Decorator to check entitlement for a module/submodule.
    
    Usage:
        @router.get("/sales/dashboard")
        @require_entitlement("sales")
        async def get_sales_dashboard(...):
            ...
        
        @router.get("/sales/leads")
        @require_entitlement("sales", "lead_management")
        async def get_leads(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract db and current_user from kwargs or dependencies
            db: Optional[AsyncSession] = kwargs.get('db')
            current_user: Optional[User] = kwargs.get('current_user')
            
            if not db or not current_user:
                # Try to get from args if they're positional
                for arg in args:
                    if isinstance(arg, AsyncSession):
                        db = arg
                    elif isinstance(arg, User):
                        current_user = arg
            
            if not db or not current_user:
                logger.error(
                    f"Entitlement guard for {module_key}/{submodule_key} failed: "
                    "Could not find db or current_user in function arguments"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Entitlement check configuration error"
                )
            
            # Super admin bypasses entitlement checks
            if current_user.role == "super_admin":
                logger.debug(f"Super admin {current_user.email} bypassed entitlement check for {module_key}")
                return await func(*args, **kwargs)
            
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
                    f"denied access to {module_key}/{submodule_key}. "
                    f"Status: {entitlement_status}, Reason: {reason}"
                )
                raise EntitlementGuardException(
                    module_key=module_key,
                    submodule_key=submodule_key,
                    entitlement_status=entitlement_status or "disabled",
                    reason=reason or "Access denied"
                )
            
            logger.debug(
                f"User {current_user.email} granted access to {module_key}/{submodule_key}. "
                f"Status: {entitlement_status}"
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def check_module_access(
    module_key: str,
    submodule_key: Optional[str],
    org_id: int,
    db: AsyncSession
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Helper function to check module access without decorator.
    Returns: (is_entitled, status, reason)
    """
    service = EntitlementService(db)
    return await service.check_entitlement(
        org_id=org_id,
        module_key=module_key,
        submodule_key=submodule_key
    )


async def require_module_access(
    module_key: str,
    submodule_key: Optional[str],
    org_id: int,
    db: AsyncSession
):
    """
    Helper function to check module access and raise exception if denied.
    """
    is_entitled, entitlement_status, reason = await check_module_access(
        module_key, submodule_key, org_id, db
    )
    
    if not is_entitled:
        raise EntitlementGuardException(
            module_key=module_key,
            submodule_key=submodule_key,
            entitlement_status=entitlement_status or "disabled",
            reason=reason or "Access denied"
        )
