# app/services/user_rbac_service.py
"""
User RBAC Service
Handles hierarchical role logic and user creation with proper RBAC assignment
"""

from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import logging

from app.models.user_models import User, Organization
from app.services.rbac import RBACService
from app.core.modules_registry import get_all_modules, get_module_submodules, validate_module, validate_submodule

logger = logging.getLogger(__name__)


class UserRBACService:
    """Service for handling user RBAC logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rbac_service = RBACService(db)
    
    async def assign_modules_to_user(
        self,
        user_id: int,
        assigned_modules: Dict[str, bool],
        validate_org_modules: bool = True
    ) -> User:
        """
        Assign modules to a user
        
        Args:
            user_id: User ID
            assigned_modules: Dict of module names to enabled status
            validate_org_modules: Whether to validate against org enabled modules
        """
        # Get user
        result = await self.db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate modules
        all_modules = get_all_modules()
        for module in assigned_modules:
            if module not in all_modules:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid module: {module}. Valid modules: {', '.join(all_modules)}"
                )
        
        # If validating against org modules, check that assigned modules are subset of org modules
        if validate_org_modules and user.organization_id:
            result = await self.db.execute(
                select(Organization).filter_by(id=user.organization_id)
            )
            org = result.scalars().first()
            if org:
                org_modules = org.enabled_modules or {}
                for module, enabled in assigned_modules.items():
                    if enabled and not org_modules.get(module, False):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Module '{module}' is not enabled for this organization"
                        )
        
        # Assign modules
        user.assigned_modules = assigned_modules
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Assigned modules to user {user_id}: {assigned_modules}")
        return user
    
    async def assign_submodule_permissions_to_executive(
        self,
        user_id: int,
        submodule_permissions: Dict[str, Dict[str, List[str]]]
    ) -> User:
        """
        Assign submodule permissions to an executive
        Format: {module: {submodule: [actions]}}
        
        Args:
            user_id: User ID
            submodule_permissions: Dict of module -> submodule -> actions
        """
        # Get user
        result = await self.db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate user role
        if user.role not in ["executive"]:
            raise HTTPException(
                status_code=400,
                detail=f"Submodule permissions can only be assigned to executives, not {user.role}"
            )
        
        # Validate structure and modules/submodules
        for module, submodules_dict in submodule_permissions.items():
            if not validate_module(module):
                raise HTTPException(status_code=400, detail=f"Invalid module: {module}")
            
            for submodule, actions in submodules_dict.items():
                if not validate_submodule(module, submodule):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid submodule '{submodule}' for module '{module}'"
                    )
                
                # Validate actions
                valid_actions = ["create", "read", "update", "delete", "export", "import", "approve"]
                for action in actions:
                    if action not in valid_actions:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid action '{action}'. Valid actions: {', '.join(valid_actions)}"
                        )
        
        # Assign submodule permissions
        user.sub_module_permissions = submodule_permissions
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Assigned submodule permissions to executive {user_id}")
        return user
    
    async def inherit_manager_permissions_for_executive(
        self,
        executive_id: int,
        manager_id: int
    ) -> User:
        """
        Have an executive inherit a subset of their manager's module permissions
        
        Args:
            executive_id: Executive user ID
            manager_id: Manager user ID
        """
        # Get users
        exec_result = await self.db.execute(select(User).filter_by(id=executive_id))
        executive = exec_result.scalars().first()
        if not executive:
            raise HTTPException(status_code=404, detail="Executive not found")
        
        mgr_result = await self.db.execute(select(User).filter_by(id=manager_id))
        manager = mgr_result.scalars().first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Validate roles
        if executive.role != "executive":
            raise HTTPException(status_code=400, detail="First user must be an executive")
        if manager.role not in ["manager", "management"]:
            raise HTTPException(status_code=400, detail="Second user must be a manager")
        
        # Set reporting relationship
        executive.reporting_manager_id = manager_id
        
        # Inherit assigned modules from manager
        if manager.assigned_modules:
            executive.assigned_modules = manager.assigned_modules.copy()
        
        # Initialize empty submodule permissions (to be assigned separately)
        if not executive.sub_module_permissions:
            executive.sub_module_permissions = {}
        
        await self.db.commit()
        await self.db.refresh(executive)
        
        logger.info(f"Executive {executive_id} now reports to manager {manager_id} and inherited modules")
        return executive
    
    async def setup_user_rbac_by_role(
        self,
        user_id: int,
        role: str,
        reporting_manager_id: Optional[int] = None,
        assigned_modules: Optional[Dict[str, bool]] = None,
        submodule_permissions: Optional[Dict[str, Dict[str, List[str]]]] = None
    ) -> User:
        """
        Setup RBAC for a user based on their role
        
        Hierarchy:
        - org_admin/management: Full access to all modules
        - manager: Requires assigned_modules, gets module-level access
        - executive: Inherits from manager, gets submodule-level permissions
        
        Args:
            user_id: User ID
            role: User role (org_admin, management, manager, executive)
            reporting_manager_id: Manager ID for executives
            assigned_modules: Modules to assign (required for managers)
            submodule_permissions: Submodule permissions (for executives)
        """
        # Get user
        result = await self.db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get organization
        if user.organization_id:
            org_result = await self.db.execute(
                select(Organization).filter_by(id=user.organization_id)
            )
            org = org_result.scalars().first()
        else:
            org = None
        
        # Handle based on role
        if role in ["org_admin", "super_admin"]:
            # Full access to all enabled modules
            if org and org.enabled_modules:
                user.assigned_modules = org.enabled_modules.copy()
            else:
                from app.core.modules_registry import get_default_enabled_modules
                user.assigned_modules = get_default_enabled_modules()
            
            # Clear submodule permissions (they have full access)
            user.sub_module_permissions = None
            user.reporting_manager_id = None
            
            logger.info(f"Granted full module access to {role} user {user_id}")
        
        elif role == "management":
            # Use org.enabled_modules (respect entitlements)
            if org and org.enabled_modules:
                user.assigned_modules = org.enabled_modules.copy()
            else:
                from app.core.modules_registry import get_default_enabled_modules
                user.assigned_modules = get_default_enabled_modules()
            
            # Clear submodule permissions (full access)
            user.sub_module_permissions = None
            user.reporting_manager_id = None
            
            logger.info(f"Granted entitled module access to management user {user_id}")
        
        elif role == "manager":
            # Require assigned modules
            if not assigned_modules:
                raise HTTPException(
                    status_code=400,
                    detail="Managers must have assigned_modules specified"
                )
            
            # Validate and assign modules
            await self.assign_modules_to_user(user_id, assigned_modules, validate_org_modules=True)
            
            # Clear submodule permissions (managers have full access to assigned modules)
            user.sub_module_permissions = None
            user.reporting_manager_id = None
            
            logger.info(f"Assigned modules to manager {user_id}")
        
        elif role == "executive":
            # Require reporting manager
            if not reporting_manager_id:
                raise HTTPException(
                    status_code=400,
                    detail="Executives must have a reporting_manager_id"
                )
            
            # Inherit from manager
            await self.inherit_manager_permissions_for_executive(user_id, reporting_manager_id)
            
            # Assign submodule permissions if provided
            if submodule_permissions:
                await self.assign_submodule_permissions_to_executive(user_id, submodule_permissions)
            
            logger.info(f"Setup executive {user_id} under manager {reporting_manager_id}")
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {role}. Valid roles: org_admin, management, manager, executive"
            )
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_effective_permissions(self, user_id: int) -> Dict[str, any]:
        """
        Get effective permissions for a user based on their role and assignments
        
        Returns:
            Dict with modules, submodules, and permission details
        """
        result = await self.db.execute(select(User).filter_by(id=user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        permissions = {
            "user_id": user_id,
            "role": user.role,
            "assigned_modules": user.assigned_modules or {},
            "sub_module_permissions": user.sub_module_permissions or {},
            "has_full_access": user.role in ["org_admin", "management", "super_admin"],
            "reporting_manager_id": user.reporting_manager_id,
        }
        
        # Get RBAC role permissions
        user_permissions = await self.rbac_service.get_user_permissions(user_id)
        permissions["rbac_permissions"] = list(user_permissions)
        
        return permissions
    
    async def migrate_management_modules(self, org_id: int) -> int:
        """
        Migrate existing management users in an organization to have assigned_modules
        matching the organization's enabled_modules.
        
        Args:
            org_id: Organization ID to migrate
        
        Returns:
            Number of users updated
        """
        # Get organization
        org_result = await self.db.execute(
            select(Organization).filter_by(id=org_id)
        )
        org = org_result.scalars().first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Get enabled modules
        enabled_modules = org.enabled_modules or {}
        
        # Get all management users in org
        users_result = await self.db.execute(
            select(User).filter_by(organization_id=org_id, role="management")
        )
        management_users = users_result.scalars().all()
        
        updated_count = 0
        for user in management_users:
            # Only update if assigned_modules is None or empty
            if not user.assigned_modules:
                user.assigned_modules = enabled_modules.copy()
                updated_count += 1
                logger.info(f"Updated modules for management user {user.id} in org {org_id}")
        
        if updated_count > 0:
            await self.db.commit()
        
        logger.info(f"Migrated {updated_count} management users in org {org_id}")
        return updated_count