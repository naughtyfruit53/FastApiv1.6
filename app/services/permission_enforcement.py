# app/services/permission_enforcement.py

"""
Permission Enforcement Service for the new 4-role system.

This service implements the permission logic for:
- Org Admin: Full access based on entitlement only (no RBAC checks)
- Management: Full owner-like access via RBAC (except Org Admin creation)
- Manager: Module-level access assigned at creation
- Executive: Submodule-level access based on reporting manager
"""

from typing import Optional, Dict, Any, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user_models import User
from app.models.entitlement_models import Module, Submodule, OrgEntitlement
from app.schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)


class PermissionEnforcer:
    """Enforces permissions based on the new 4-role system"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_module_access(
        self,
        user: User,
        module_key: str,
        action: str = "read"
    ) -> bool:
        """
        Check if user has access to a specific module.
        
        Args:
            user: User object
            module_key: Module identifier (e.g., "CRM", "ERP")
            action: Action type (read, create, update, delete)
        
        Returns:
            bool: True if user has access, False otherwise
        """
        if not user.organization_id:
            return False
        
        # Org Admin: Full access to all entitled modules
        if user.role == UserRole.ORG_ADMIN.value:
            return await self._check_entitlement(user.organization_id, module_key)
        
        # Management: Full RBAC access to all entitled modules
        elif user.role == UserRole.MANAGEMENT.value:
            return await self._check_entitlement(user.organization_id, module_key)
        
        # Manager: Check assigned modules
        elif user.role == UserRole.MANAGER.value:
            if user.assigned_modules and module_key in user.assigned_modules:
                return user.assigned_modules[module_key]
            return False
        
        # Executive: Check if any submodule of this module is assigned
        elif user.role == UserRole.EXECUTIVE.value:
            if user.sub_module_permissions and module_key in user.sub_module_permissions:
                return len(user.sub_module_permissions[module_key]) > 0
            return False
        
        return False
    
    async def check_submodule_access(
        self,
        user: User,
        module_key: str,
        submodule_key: str,
        action: str = "read"
    ) -> bool:
        """
        Check if user has access to a specific submodule.
        
        Args:
            user: User object
            module_key: Module identifier
            submodule_key: Submodule identifier
            action: Action type (read, create, update, delete)
        
        Returns:
            bool: True if user has access, False otherwise
        """
        if not user.organization_id:
            return False
        
        # Org Admin: Full access to all entitled submodules
        if user.role == UserRole.ORG_ADMIN.value:
            return await self._check_entitlement(user.organization_id, module_key)
        
        # Management: Full RBAC access to all entitled submodules
        elif user.role == UserRole.MANAGEMENT.value:
            return await self._check_entitlement(user.organization_id, module_key)
        
        # Manager: Full access to all submodules of assigned modules
        elif user.role == UserRole.MANAGER.value:
            return await self.check_module_access(user, module_key, action)
        
        # Executive: Check specific submodule permissions
        elif user.role == UserRole.EXECUTIVE.value:
            if user.sub_module_permissions:
                if module_key in user.sub_module_permissions:
                    return submodule_key in user.sub_module_permissions[module_key]
            return False
        
        return False
    
    async def check_settings_menu_access(
        self,
        user: User,
        setting_module: str
    ) -> bool:
        """
        Check if user should see a settings menu item.
        
        Rules:
        - Org Admin: Sees all settings based on entitlement
        - Management: Sees settings for modules with RBAC access
        - Manager: Sees settings for assigned modules only
        - Executive: No settings access
        
        Args:
            user: User object
            setting_module: Module related to the setting
        
        Returns:
            bool: True if user can see the setting, False otherwise
        """
        if not user.organization_id:
            return False
        
        # Executives don't see settings menus
        if user.role == UserRole.EXECUTIVE.value:
            return False
        
        # For others, check module access
        return await self.check_module_access(user, setting_module)
    
    async def get_accessible_modules(self, user: User) -> List[str]:
        """
        Get list of modules the user can access.
        
        Returns:
            List of module keys
        """
        if not user.organization_id:
            return []
        
        # Org Admin and Management: All entitled modules
        if user.role in [UserRole.ORG_ADMIN.value, UserRole.MANAGEMENT.value]:
            stmt = select(OrgEntitlement).where(
                and_(
                    OrgEntitlement.org_id == user.organization_id,
                    OrgEntitlement.status == "enabled"
                )
            ).options(lambda q: q.joinedload(OrgEntitlement.module))
            
            result = await self.db.execute(stmt)
            entitlements = result.scalars().all()
            return [ent.module.module_key for ent in entitlements]
        
        # Manager: Assigned modules
        elif user.role == UserRole.MANAGER.value:
            if user.assigned_modules:
                return [k for k, v in user.assigned_modules.items() if v]
            return []
        
        # Executive: Modules with assigned submodules
        elif user.role == UserRole.EXECUTIVE.value:
            if user.sub_module_permissions:
                return list(user.sub_module_permissions.keys())
            return []
        
        return []
    
    async def get_accessible_submodules(
        self,
        user: User,
        module_key: str
    ) -> List[str]:
        """
        Get list of submodules the user can access for a specific module.
        
        Args:
            user: User object
            module_key: Module identifier
        
        Returns:
            List of submodule keys
        """
        if not user.organization_id:
            return []
        
        # Org Admin and Management: All submodules of entitled modules
        if user.role in [UserRole.ORG_ADMIN.value, UserRole.MANAGEMENT.value]:
            # Check module entitlement first
            if not await self._check_entitlement(user.organization_id, module_key):
                return []
            
            # Get module ID
            mod_stmt = select(Module).where(Module.module_key == module_key)
            mod_result = await self.db.execute(mod_stmt)
            module = mod_result.scalars().first()
            
            if not module:
                return []
            
            # Get all submodules
            sub_stmt = select(Submodule).where(
                and_(
                    Submodule.module_id == module.id,
                    Submodule.is_active == True
                )
            )
            sub_result = await self.db.execute(sub_stmt)
            submodules = sub_result.scalars().all()
            return [s.submodule_key for s in submodules]
        
        # Manager: All submodules if module is assigned
        elif user.role == UserRole.MANAGER.value:
            if user.assigned_modules and user.assigned_modules.get(module_key):
                # Get module ID
                mod_stmt = select(Module).where(Module.module_key == module_key)
                mod_result = await self.db.execute(mod_stmt)
                module = mod_result.scalars().first()
                
                if not module:
                    return []
                
                # Get all submodules
                sub_stmt = select(Submodule).where(
                    and_(
                        Submodule.module_id == module.id,
                        Submodule.is_active == True
                    )
                )
                sub_result = await self.db.execute(sub_stmt)
                submodules = sub_result.scalars().all()
                return [s.submodule_key for s in submodules]
            return []
        
        # Executive: Assigned submodules only
        elif user.role == UserRole.EXECUTIVE.value:
            if user.sub_module_permissions and module_key in user.sub_module_permissions:
                return user.sub_module_permissions[module_key]
            return []
        
        return []
    
    async def can_manage_user(
        self,
        manager_user: User,
        target_user: User
    ) -> bool:
        """
        Check if manager_user can manage target_user.
        
        Rules:
        - Org Admin: Can manage all users except other Org Admins
        - Management: Can manage Managers and Executives, not Org Admin
        - Manager: Can manage only their reporting Executives
        - Executive: Cannot manage any users
        
        Args:
            manager_user: User attempting to manage
            target_user: User to be managed
        
        Returns:
            bool: True if management is allowed
        """
        if manager_user.organization_id != target_user.organization_id:
            return False
        
        # Org Admin can manage everyone except other Org Admins
        if manager_user.role == UserRole.ORG_ADMIN.value:
            return target_user.role != UserRole.ORG_ADMIN.value
        
        # Management can manage Managers and Executives
        elif manager_user.role == UserRole.MANAGEMENT.value:
            return target_user.role in [UserRole.MANAGER.value, UserRole.EXECUTIVE.value]
        
        # Manager can manage only their reporting Executives
        elif manager_user.role == UserRole.MANAGER.value:
            return (
                target_user.role == UserRole.EXECUTIVE.value and
                target_user.reporting_manager_id == manager_user.id
            )
        
        # Executives cannot manage users
        return False
    
    async def _check_entitlement(self, org_id: int, module_key: str) -> bool:
        """
        Check if organization has entitlement for a module.
        
        Args:
            org_id: Organization ID
            module_key: Module identifier
        
        Returns:
            bool: True if entitled
        """
        # Get module
        mod_stmt = select(Module).where(Module.module_key == module_key)
        mod_result = await self.db.execute(mod_stmt)
        module = mod_result.scalars().first()
        
        if not module:
            return False
        
        # Check entitlement
        ent_stmt = select(OrgEntitlement).where(
            and_(
                OrgEntitlement.org_id == org_id,
                OrgEntitlement.module_id == module.id,
                OrgEntitlement.status == "enabled"
            )
        )
        ent_result = await self.db.execute(ent_stmt)
        entitlement = ent_result.scalars().first()
        
        return entitlement is not None
