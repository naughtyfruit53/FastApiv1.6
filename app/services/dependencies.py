# app/services/dependencies.py

from typing import List
from fastapi import Depends, HTTPException

from app.models.user_models import User
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from .rbac import RBACService

def require_permission(permission: str):
    """Dependency to check if current user has a specific permission"""
    async def dependency(current_user: User = Depends(get_current_active_user), db = Depends(get_db)):
        rbac = RBACService(db)
        if not await rbac.user_has_service_permission(current_user.id, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {permission} required"
            )
        return current_user
    return dependency

def check_permissions(user: User, required_permissions: List[str]) -> bool:
    """
    Check if user has all required permissions
    """
    user_permissions = user.permissions or []
    return all(perm in user_permissions for perm in required_permissions)

class PermissionChecker:
    def __init__(self, allowed_permissions: List[str]):
        self.allowed_permissions = allowed_permissions

    async def __call__(self, current_user: User = Depends(get_current_active_user), db = Depends(get_db)):
        rbac = RBACService(db)
        for perm in self.allowed_permissions:
            if await rbac.user_has_service_permission(current_user.id, perm):
                return current_user
        raise HTTPException(status_code=403, detail="Insufficient permissions")