# app/services/org_role_service.py

"""
Organization Role Service for the new 4-role system.

NEW ROLE SYSTEM:
- Org Admin: Full access based on entitlement only (no RBAC)
- Management: Full owner-like access via RBAC (except Org Admin creation)
- Manager: Module-level access assigned at creation/management
- Executive: Submodule-level access based on reporting manager's modules
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user_models import User, Organization
from app.models.entitlement_models import Module, Submodule, OrgEntitlement, OrgSubentitlement
from app.schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)


class OrgRoleService:
    """Service for managing organization-level roles and permissions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_role_transition(
        self, 
        current_role: str, 
        new_role: str,
        requester_role: str,
        org_id: int
    ) -> bool:
        """
        Validate if a role transition is allowed.
        
        Rules:
        - Only Org Admin can create other Org Admins
        - Management can create/manage Managers and Executives
        - Org Admin and Management can upgrade users
        - Managers can only manage their own Executives
        """
        valid_roles = {UserRole.ORG_ADMIN.value, UserRole.MANAGEMENT.value, 
                      UserRole.MANAGER.value, UserRole.EXECUTIVE.value}
        
        if new_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {new_role}. Must be one of: org_admin, management, manager, executive"
            )
        
        # Only Org Admin can create Org Admin
        if new_role == UserRole.ORG_ADMIN.value and requester_role != UserRole.ORG_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Org Admin can create or assign Org Admin role"
            )
        
        # Management cannot create Org Admin
        if new_role == UserRole.ORG_ADMIN.value and requester_role == UserRole.MANAGEMENT.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Management cannot create Org Admin users"
            )
        
        # Manager can only manage Executives
        if requester_role == UserRole.MANAGER.value:
            if new_role not in [UserRole.EXECUTIVE.value]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only create and manage Executives"
                )
        
        return True
    
    async def get_available_modules_for_role(
        self,
        role: str,
        org_id: int,
        manager_id: Optional[int] = None
    ) -> Dict[str, List[str]]:
        """
        Get available modules and submodules for a role.
        
        For Org Admin: All entitled modules
        For Management: All entitled modules (RBAC-based)
        For Manager: Modules assigned by Org Admin or Management
        For Executive: Submodules from reporting manager's modules
        """
        # Get organization entitlements
        stmt = select(OrgEntitlement).where(
            and_(
                OrgEntitlement.org_id == org_id,
                OrgEntitlement.status == "enabled"
            )
        ).options(joinedload(OrgEntitlement.module))
        
        result = await self.db.execute(stmt)
        entitlements = result.scalars().all()
        
        available = {}
        
        if role == UserRole.ORG_ADMIN.value:
            # Org Admin gets all entitled modules with all submodules
            for ent in entitlements:
                module_key = ent.module.module_key
                # Get all submodules for this module
                sub_stmt = select(Submodule).where(
                    and_(
                        Submodule.module_id == ent.module_id,
                        Submodule.is_active == True
                    )
                )
                sub_result = await self.db.execute(sub_stmt)
                submodules = sub_result.scalars().all()
                available[module_key] = [s.submodule_key for s in submodules]
        
        elif role == UserRole.MANAGEMENT.value:
            # Management gets all entitled modules with all submodules (via RBAC)
            for ent in entitlements:
                module_key = ent.module.module_key
                sub_stmt = select(Submodule).where(
                    and_(
                        Submodule.module_id == ent.module_id,
                        Submodule.is_active == True
                    )
                )
                sub_result = await self.db.execute(sub_stmt)
                submodules = sub_result.scalars().all()
                available[module_key] = [s.submodule_key for s in submodules]
        
        elif role == UserRole.MANAGER.value:
            # Manager gets modules assigned by admin/management
            # This will be populated during user creation
            for ent in entitlements:
                module_key = ent.module.module_key
                sub_stmt = select(Submodule).where(
                    and_(
                        Submodule.module_id == ent.module_id,
                        Submodule.is_active == True
                    )
                )
                sub_result = await self.db.execute(sub_stmt)
                submodules = sub_result.scalars().all()
                available[module_key] = [s.submodule_key for s in submodules]
        
        elif role == UserRole.EXECUTIVE.value:
            # Executive gets submodules based on manager's assigned modules
            if manager_id:
                manager_stmt = select(User).where(User.id == manager_id)
                manager_result = await self.db.execute(manager_stmt)
                manager = manager_result.scalars().first()
                
                if manager and manager.assigned_modules:
                    # Get manager's modules
                    for module_key, enabled in manager.assigned_modules.items():
                        if enabled:
                            # Find module ID
                            mod_stmt = select(Module).where(Module.module_key == module_key)
                            mod_result = await self.db.execute(mod_stmt)
                            module = mod_result.scalars().first()
                            
                            if module:
                                sub_stmt = select(Submodule).where(
                                    and_(
                                        Submodule.module_id == module.id,
                                        Submodule.is_active == True
                                    )
                                )
                                sub_result = await self.db.execute(sub_stmt)
                                submodules = sub_result.scalars().all()
                                available[module_key] = [s.submodule_key for s in submodules]
        
        return available
    
    async def assign_modules_to_user(
        self,
        user_id: int,
        modules: Dict[str, bool],
        org_id: int,
        assigned_by_id: int
    ) -> None:
        """
        Assign modules to a Manager or Executive.
        For Managers: modules dict with True/False
        For Executives: submodules dict with module->submodule list
        """
        user_stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(user_stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate modules are entitled for the organization
        entitled_modules = await self.get_available_modules_for_role(
            UserRole.ORG_ADMIN.value,  # Get all entitled modules
            org_id
        )
        
        for module_key in modules.keys():
            if module_key not in entitled_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module '{module_key}' is not entitled for this organization"
                )
        
        # Update user's assigned modules
        user.assigned_modules = modules
        await self.db.commit()
        
        logger.info(f"Assigned modules to user {user_id}: {modules}")
    
    async def assign_submodules_to_executive(
        self,
        user_id: int,
        submodule_permissions: Dict[str, List[str]],
        org_id: int,
        manager_id: int,
        assigned_by_id: int
    ) -> None:
        """
        Assign submodules to an Executive based on manager's modules.
        
        submodule_permissions format: {"CRM": ["leads", "contacts"], "ERP": ["sales"]}
        """
        # Validate executive and manager
        user_stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(user_stmt)
        user = result.scalars().first()
        
        if not user or user.role != UserRole.EXECUTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Executive user not found"
            )
        
        manager_stmt = select(User).where(User.id == manager_id)
        manager_result = await self.db.execute(manager_stmt)
        manager = manager_result.scalars().first()
        
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )
        
        # Validate submodules are within manager's assigned modules
        manager_modules = await self.get_available_modules_for_role(
            UserRole.EXECUTIVE.value,  # Gets manager's modules
            org_id,
            manager_id=manager_id
        )
        
        for module_key, submodules in submodule_permissions.items():
            if module_key not in manager_modules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module '{module_key}' is not assigned to the manager"
                )
            
            for submodule in submodules:
                if submodule not in manager_modules[module_key]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Submodule '{submodule}' is not available in module '{module_key}'"
                    )
        
        # Update executive's submodule permissions
        user.sub_module_permissions = submodule_permissions
        user.reporting_manager_id = manager_id
        await self.db.commit()
        
        logger.info(f"Assigned submodules to executive {user_id}: {submodule_permissions}")
    
    async def get_user_effective_permissions(
        self,
        user_id: int,
        org_id: int
    ) -> Dict[str, Any]:
        """
        Get effective permissions for a user based on their role.
        
        Returns a dict with:
        - role: User's role
        - modules: Available modules
        - submodules: Available submodules (for executives)
        - full_access: Boolean indicating if user has full access to modules
        """
        user_stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(user_stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        permissions = {
            "role": user.role,
            "modules": {},
            "submodules": {},
            "full_access": False
        }
        
        if user.role == UserRole.ORG_ADMIN.value:
            # Org Admin: Full access to all entitled modules
            modules = await self.get_available_modules_for_role(
                UserRole.ORG_ADMIN.value,
                org_id
            )
            permissions["modules"] = modules
            permissions["full_access"] = True
        
        elif user.role == UserRole.MANAGEMENT.value:
            # Management: Full RBAC access to all modules
            modules = await self.get_available_modules_for_role(
                UserRole.MANAGEMENT.value,
                org_id
            )
            permissions["modules"] = modules
            permissions["full_access"] = True
        
        elif user.role == UserRole.MANAGER.value:
            # Manager: Module-level access
            if user.assigned_modules:
                for module_key, enabled in user.assigned_modules.items():
                    if enabled:
                        # Get all submodules for this module
                        mod_stmt = select(Module).where(Module.module_key == module_key)
                        mod_result = await self.db.execute(mod_stmt)
                        module = mod_result.scalars().first()
                        
                        if module:
                            sub_stmt = select(Submodule).where(
                                Submodule.module_id == module.id
                            )
                            sub_result = await self.db.execute(sub_stmt)
                            submodules = sub_result.scalars().all()
                            permissions["modules"][module_key] = [s.submodule_key for s in submodules]
        
        elif user.role == UserRole.EXECUTIVE.value:
            # Executive: Submodule-level access
            if user.sub_module_permissions:
                permissions["submodules"] = user.sub_module_permissions
        
        return permissions
