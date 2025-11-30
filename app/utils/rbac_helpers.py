# app/utils/rbac_helpers.py

"""
Standardized RBAC utility functions for permission checking (Layer 3)
Provides helpers for role and permission validation
"""

from typing import List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging

from app.core.constants import (
    SUPER_ADMIN_BYPASS_ROLES,
    ORG_ADMIN_ROLES,
    ROLE_HIERARCHY,
    ENFORCEMENT_ERRORS,
    UserRole,
    PermissionScope,
)
from app.models.user_models import User
from app.services.rbac import RBACService

logger = logging.getLogger(__name__)


class RBACHelper:
    """Helper class for RBAC operations"""

    @staticmethod
    def is_super_admin(user: User) -> bool:
        """
        Check if user is super admin
        
        Args:
            user: User object
            
        Returns:
            bool: True if super admin
        """
        return user.is_super_admin or user.role in SUPER_ADMIN_BYPASS_ROLES

    @staticmethod
    def is_org_admin(user: User) -> bool:
        """
        Check if user is organization admin
        
        Args:
            user: User object
            
        Returns:
            bool: True if org admin
        """
        return user.role in ORG_ADMIN_ROLES or user.is_company_admin

    @staticmethod
    def get_role_level(role: str) -> int:
        """
        Get numeric level for role
        
        Args:
            role: Role name
            
        Returns:
            int: Role level (higher = more privileges)
        """
        return ROLE_HIERARCHY.get(role, 0)

    @staticmethod
    def can_manage_role(manager_role: str, target_role: str) -> bool:
        """
        Check if manager role can manage target role
        
        Args:
            manager_role: Role of the manager
            target_role: Role being managed
            
        Returns:
            bool: True if can manage
        """
        manager_level = RBACHelper.get_role_level(manager_role)
        target_level = RBACHelper.get_role_level(target_role)
        return manager_level > target_level

    @staticmethod
    def enforce_can_manage_role(manager_role: str, target_role: str) -> None:
        """
        Enforce manager can manage target role
        
        Args:
            manager_role: Role of the manager
            target_role: Role being managed
            
        Raises:
            HTTPException: If cannot manage role
        """
        if not RBACHelper.can_manage_role(manager_role, target_role):
            logger.warning(
                f"Role {manager_role} attempted to manage role {target_role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ENFORCEMENT_ERRORS["rbac_role_insufficient"]
            )

    @staticmethod
    async def get_user_permissions(
        db: AsyncSession,
        user_id: int
    ) -> List[str]:
        """
        Get all permissions for user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List[str]: List of permission names
        """
        rbac_service = RBACService(db)
        permissions = await rbac_service.get_user_permissions(user_id)
        return list(permissions)

    @staticmethod
    async def has_permission(
        db: AsyncSession,
        user: User,
        permission: str
    ) -> bool:
        """
        Check if user has specific permission
        
        Args:
            db: Database session
            user: User object
            permission: Permission name to check
            
        Returns:
            bool: True if user has permission
        """
        # Super admins bypass permission checks
        if RBACHelper.is_super_admin(user):
            logger.debug(f"Super admin {user.email} bypassed permission check for {permission}")
            return True
        
        # Get user permissions
        user_permissions = await RBACHelper.get_user_permissions(db, user.id)
        
        # Check exact match
        if permission in user_permissions:
            return True
        
        # Check wildcard match (e.g., "crm.*" matches "crm.read")
        for user_perm in user_permissions:
            if user_perm.endswith('.*'):
                module = user_perm[:-2]
                if permission.startswith(f"{module}."):
                    return True
        
        return False

    @staticmethod
    async def enforce_permission(
        db: AsyncSession,
        user: User,
        permission: str
    ) -> None:
        """
        Enforce user has permission, raise exception if not
        
        Args:
            db: Database session
            user: User object
            permission: Permission name to check
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        has_perm = await RBACHelper.has_permission(db, user, permission)
        
        if not has_perm:
            logger.warning(
                f"User {user.email} denied permission {permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ENFORCEMENT_ERRORS["rbac_permission_denied"].format(
                    permission=permission
                )
            )

    @staticmethod
    async def has_any_permission(
        db: AsyncSession,
        user: User,
        permissions: List[str]
    ) -> bool:
        """
        Check if user has any of the specified permissions
        
        Args:
            db: Database session
            user: User object
            permissions: List of permission names
            
        Returns:
            bool: True if user has at least one permission
        """
        for permission in permissions:
            if await RBACHelper.has_permission(db, user, permission):
                return True
        return False

    @staticmethod
    async def has_all_permissions(
        db: AsyncSession,
        user: User,
        permissions: List[str]
    ) -> bool:
        """
        Check if user has all specified permissions
        
        Args:
            db: Database session
            user: User object
            permissions: List of permission names
            
        Returns:
            bool: True if user has all permissions
        """
        for permission in permissions:
            if not await RBACHelper.has_permission(db, user, permission):
                return False
        return True

    @staticmethod
    async def get_user_modules(
        db: AsyncSession,
        user_id: int
    ) -> Set[str]:
        """
        Get all modules user has access to
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Set[str]: Set of module names
        """
        permissions = await RBACHelper.get_user_permissions(db, user_id)
        
        modules = set()
        for perm in permissions:
            # Extract module from permission (e.g., "crm.read" -> "crm")
            if '.' in perm:
                module = perm.split('.')[0]
                modules.add(module)
            elif '_' in perm:
                # Handle format like "crm_admin"
                module = perm.split('_')[0]
                modules.add(module)
        
        return modules

    @staticmethod
    async def can_access_module(
        db: AsyncSession,
        user: User,
        module: str,
        action: str = "read"
    ) -> bool:
        """
        Check if user can access module with specific action
        
        Args:
            db: Database session
            user: User object
            module: Module name
            action: Action (read, write, create, etc.)
            
        Returns:
            bool: True if can access
        """
        # Super admins have access to all modules
        if RBACHelper.is_super_admin(user):
            return True
        
        # Check specific permission
        permission = f"{module}.{action}"
        if await RBACHelper.has_permission(db, user, permission):
            return True
        
        # Check wildcard permission
        wildcard = f"{module}.*"
        if await RBACHelper.has_permission(db, user, wildcard):
            return True
        
        return False

    @staticmethod
    async def filter_accessible_records(
        db: AsyncSession,
        user: User,
        records: List,
        check_ownership: bool = True,
        owner_field: str = "created_by_id"
    ) -> List:
        """
        Filter records based on user access rights
        
        Args:
            db: Database session
            user: User object
            records: List of records to filter
            check_ownership: If True, check record ownership
            owner_field: Field name for owner ID
            
        Returns:
            List: Filtered records
        """
        # Super admins and org admins see all records
        if RBACHelper.is_super_admin(user) or RBACHelper.is_org_admin(user):
            return records
        
        if not check_ownership:
            return records
        
        # Filter to user's own records
        filtered = []
        for record in records:
            if hasattr(record, owner_field):
                owner_id = getattr(record, owner_field)
                if owner_id == user.id:
                    filtered.append(record)
            else:
                # If no owner field, include record
                filtered.append(record)
        
        return filtered


# Convenience functions for common operations

def is_super_admin(user: User) -> bool:
    """Check if user is super admin"""
    return RBACHelper.is_super_admin(user)


def is_org_admin(user: User) -> bool:
    """Check if user is organization admin"""
    return RBACHelper.is_org_admin(user)


def can_manage_role(manager_role: str, target_role: str) -> bool:
    """Check if manager role can manage target role"""
    return RBACHelper.can_manage_role(manager_role, target_role)


async def has_permission(db: AsyncSession, user: User, permission: str) -> bool:
    """Check if user has permission"""
    return await RBACHelper.has_permission(db, user, permission)


async def enforce_permission(db: AsyncSession, user: User, permission: str) -> None:
    """Enforce user has permission"""
    await RBACHelper.enforce_permission(db, user, permission)


async def can_access_module(
    db: AsyncSession,
    user: User,
    module: str,
    action: str = "read"
) -> bool:
    """Check if user can access module"""
    return await RBACHelper.can_access_module(db, user, module, action)
