# app/services/rbac.py

"""
RBAC service layer for Role-based access control
"""

from typing import List, Optional, Set
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import get_db
from app.models import (
    User, ServiceRole as Role, ServicePermission as Permission, ServiceRolePermission as RolePermission, 
    UserServiceRole as UserRole, Organization
)
from app.schemas.rbac import (
    ServiceRoleCreate as RoleCreate, ServiceRoleUpdate as RoleUpdate, ServicePermissionCreate as PermissionCreate,
    UserServiceRoleCreate as UserRoleCreate, ServiceRoleType as RoleType, ServiceModule as Module, ServiceAction as Action
)
import logging

logger = logging.getLogger(__name__)

class RBACService:
    """Service class for Role-Based Access Control operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Permission Management
    async def create_permission(self, permission: PermissionCreate) -> Permission:
        """Create a new permission"""
        db_permission = Permission(**permission.model_dump())
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        logger.info(f"Created permission: {db_permission.name}")
        return db_permission
    
    async def get_permissions(self, 
                             module: Optional[str] = None,
                             action: Optional[str] = None,
                             is_active: bool = True) -> List[Permission]:
        """Get permissions with optional filtering"""
        from app.schemas.rbac import ServiceModule as Module, ServiceAction as Action
        
        stmt = select(Permission)
        
        if is_active is not None:
            stmt = stmt.where(Permission.is_active == is_active)
        if module:
            stmt = stmt.where(Permission.module == module)
        if action:
            stmt = stmt.where(Permission.action == action)
            
        result = await self.db.execute(stmt.order_by(Permission.module, Permission.action))
        permissions = result.scalars().all()
        
        valid_permissions = []
        valid_modules = {m.value for m in Module}
        valid_actions = {a.value for a in Action}
        
        for perm in permissions:
            if perm.module in valid_modules and perm.action in valid_actions:
                valid_permissions.append(perm)
            else:
                logger.warning(f"Filtering out permission with invalid module/action: {perm.name} (module={perm.module}, action={perm.action})")
        
        return valid_permissions
    
    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        result = await self.db.execute(
            select(Permission).filter_by(name=name, is_active=True)
        )
        return result.scalars().first()
    
    # Role Management
    async def create_role(self, role: RoleCreate, created_by_user_id: Optional[int] = None) -> Role:
        """Create a new role with permissions"""
        result = await self.db.execute(
            select(Role).filter_by(organization_id=role.organization_id, name=role.name)
        )
        existing = result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role.name}' already exists in this organization"
            )
        
        role_data = role.model_dump(exclude={'permission_ids'})
        db_role = Role(**role_data)
        self.db.add(db_role)
        await self.db.flush()
        
        if role.permission_ids:
            for permission_id in role.permission_ids:
                result = await self.db.execute(
                    select(Permission).filter_by(id=permission_id, is_active=True)
                )
                permission = result.scalars().first()
                if permission:
                    role_permission = RolePermission(
                        role_id=db_role.id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Created role: {db_role.name} for organization {db_role.organization_id}")
        return db_role
    
    async def get_roles(self, organization_id: int, is_active: bool = True) -> List[Role]:
        """Get roles for an organization"""
        stmt = select(Role).filter_by(organization_id=organization_id)
        
        if is_active is not None:
            stmt = stmt.where(Role.is_active == is_active)
            
        result = await self.db.execute(stmt.order_by(Role.name))
        return result.scalars().all()
    
    async def get_role_by_id(self, role_id: int, organization_id: Optional[int] = None) -> Optional[Role]:
        """Get role by ID with optional organization filtering"""
        stmt = select(Role).filter_by(id=role_id)
        
        if organization_id:
            stmt = stmt.where(Role.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[Role]:
        """Get role with its permissions loaded"""
        result = await self.db.execute(
            select(Role).options(
                joinedload(Role.permissions).joinedload(RolePermission.permission)
            ).filter_by(id=role_id)
        )
        return result.scalars().first()
    
    async def update_role(self, role_id: int, updates: RoleUpdate, organization_id: Optional[int] = None) -> Role:
        """Update a role"""
        stmt = select(Role).filter_by(id=role_id)
        if organization_id:
            stmt = stmt.where(Role.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        db_role = result.scalars().first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        update_data = updates.model_dump(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        if updates.permission_ids is not None:
            await self.db.execute(
                RolePermission.__table__.delete().where(
                    RolePermission.role_id == role_id
                )
            )
            
            for permission_id in updates.permission_ids:
                stmt = select(Permission).filter_by(id=permission_id, is_active=True)
                result = await self.db.execute(stmt)
                permission = result.scalars().first()
                
                if permission:
                    role_permission = RolePermission(
                        role_id=role_id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Updated role: {db_role.name}")
        return db_role
    
    async def delete_role(self, role_id: int, organization_id: Optional[int] = None) -> bool:
        """Delete a role (soft delete by setting is_active=False)"""
        stmt = select(Role).filter_by(id=role_id)
        if organization_id:
            stmt = stmt.where(Role.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        db_role = result.scalars().first()
        if not db_role:
            return False
        
        count_stmt = select(func.count('*')).select_from(UserRole).where(UserRole.role_id == role_id, UserRole.is_active == True)
        count_result = await self.db.execute(count_stmt)
        active_assignments = count_result.scalar()
        
        if active_assignments > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role '{db_role.name}' as it is assigned to {active_assignments} users"
            )
        
        db_role.is_active = False
        await self.db.commit()
        logger.info(f"Deleted role: {db_role.name}")
        return True
    
    # User Role Assignment
    async def assign_role_to_user(self, user_id: int, role_id: int, assigned_by_id: Optional[int] = None) -> UserRole:
        """Assign a role to a user"""
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role_result = await self.db.execute(
            select(Role).filter_by(id=role_id, is_active=True)
        )
        role = role_result.scalars().first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found or inactive")
        
        if user.organization_id != role.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User and role must belong to the same organization"
            )
        
        existing_result = await self.db.execute(
            select(UserRole).filter_by(user_id=user_id, role_id=role_id)
        )
        existing = existing_result.scalars().first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has this role assigned"
                )
            else:
                existing.is_active = True
                existing.assigned_by_id = assigned_by_id
                await self.db.commit()
                await self.db.refresh(existing)
                logger.info(f"Reactivated role assignment: user {user_id} -> role {role_id}")
                return existing
        
        assignment = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=assigned_by_id
        )
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        logger.info(f"Assigned role: user {user_id} -> role {role_id}")
        return assignment
    
    async def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove a role from a user"""
        result = await self.db.execute(
            select(UserRole).filter_by(
                user_id=user_id,
                role_id=role_id,
                is_active=True
            )
        )
        assignment = result.scalars().first()
        
        if not assignment:
            return False
        
        assignment.is_active = False
        await self.db.commit()
        logger.info(f"Removed role assignment: user {user_id} -> role {role_id}")
        return True
    
    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all active roles for a user"""
        result = await self.db.execute(
            select(Role)
            .join(UserRole)
            .where(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                Role.is_active == True
            )
        )
        return result.scalars().all()
    
    async def get_users_with_role(self, role_id: int) -> List[User]:
        """Get all users assigned to a specific role"""
        result = await self.db.execute(
            select(User)
            .join(UserRole)
            .where(
                UserRole.role_id == role_id,
                UserRole.is_active == True,
                User.is_active == True
            )
        )
        return result.scalars().all()
    
    async def user_has_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission through their roles"""
        await self.initialize_default_permissions()
        logger.debug(f"Checking permission '{permission_name}' for user_id {user_id}")
        
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if not user:
            logger.warning(f"User {user_id} not found")
            return False
            
        logger.debug(f"User {user_id} role: {user.role}, org_id: {user.organization_id}, is_super_admin: {user.is_super_admin}")
        
        # Super admins bypass all checks
        if user.is_super_admin:
            logger.debug(f"Granted permission '{permission_name}' to super_admin user {user_id}")
            return True
        
        # First, resolve user's role through service_roles table using users.role + users.organization_id
        # This is the proper way to map the user's role string to a service_role row
        if user.organization_id and user.role:
            role_result = await self.db.execute(
                select(Role).filter_by(
                    organization_id=user.organization_id,
                    name=user.role,
                    is_active=True
                )
            )
            role_from_users_table = role_result.scalars().first()
            
            if role_from_users_table:
                logger.debug(f"Resolved user {user_id} role '{user.role}' to service_role id {role_from_users_table.id}")
                # Check if this role has the required permission
                perm_result = await self.db.execute(
                    select(Permission)
                    .join(RolePermission)
                    .where(
                        RolePermission.role_id == role_from_users_table.id,
                        Permission.name == permission_name,
                        Permission.is_active == True
                    )
                )
                if perm_result.scalars().first():
                    logger.debug(f"Granted permission '{permission_name}' to user {user_id} via service_role '{user.role}'")
                    return True
            else:
                logger.warning(f"User {user_id} has role '{user.role}' but no matching service_role found in org {user.organization_id}")
        
        # Fallback: check through UserServiceRole assignments (explicit role assignments)
        user_roles = await self.get_user_roles(user_id)
        logger.debug(f"User {user_id} explicit role assignments: {[role.name for role in user_roles]}")
        
        for role in user_roles:
            result = await self.db.execute(
                select(Permission)
                .join(RolePermission)
                .where(
                    RolePermission.role_id == role.id,
                    Permission.name == permission_name,
                    Permission.is_active == True
                )
            )
            if result.scalars().first():
                logger.debug(f"Granted permission '{permission_name}' to user {user_id} via explicit role assignment '{role.name}'")
                return True
        
        logger.debug(f"Denied permission '{permission_name}' for user {user_id} - no matching role or permission found")
        return False
    
    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user"""
        await self.initialize_default_permissions()
        logger.debug(f"Fetching permissions for user_id {user_id}")
        
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        
        permissions = set()
        if user and (user.is_super_admin or user.role in ["super_admin", "org_admin"]):
            # Grant all active permissions to super admins and org admins
            result = await self.db.execute(select(Permission.name).where(Permission.is_active == True))
            permissions.update({row[0] for row in result.fetchall()})
            logger.debug(f"Granted all permissions to user {user_id} due to role {user.role}")
        
        result = await self.db.execute(
            select(Permission.name)
            .select_from(UserRole)
            .join(UserRole.role)
            .join(Role.permissions)
            .join(RolePermission.permission)
            .where(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                Permission.is_active == True
            )
        )
        role_permissions = {row[0] for row in result.fetchall()}
        logger.debug(f"Permissions from roles: {role_permissions}")
        
        permissions.update(role_permissions)
        logger.debug(f"Final permissions for user {user_id}: {permissions}")
        
        return permissions
    
    # Bulk Operations
    async def assign_multiple_roles_to_user(self, user_id: int, role_ids: List[int], assigned_by_id: Optional[int] = None) -> List[UserRole]:
        """Assign multiple roles to a user"""
        assignments = []
        for role_id in role_ids:
            try:
                assignment = await self.assign_role_to_user(user_id, role_id, assigned_by_id)
                assignments.append(assignment)
            except HTTPException as e:
                logger.warning(f"Failed to assign role {role_id} to user {user_id}: {e.detail}")
        
        return assignments
    
    async def remove_all_roles_from_user(self, user_id: int) -> int:
        """Remove all roles from a user"""
        result = await self.db.execute(
            select(UserRole).filter_by(
                user_id=user_id, is_active=True
            )
        )
        assignments = result.scalars().all()
        
        count = len(assignments)
        for assignment in assignments:
            assignment.is_active = False
        
        await self.db.commit()
        logger.info(f"Removed {count} role assignments from user {user_id}")
        return count
    
    # Initialization
    async def initialize_default_permissions(self) -> List[Permission]:
        """Initialize default permissions"""
        from app.services.rbac_permissions import get_comprehensive_permissions
        
        # Get comprehensive permissions
        default_permissions = get_comprehensive_permissions()
        
        # Batch check existing permissions
        stmt = select(Permission.name).where(
            Permission.name.in_([name for name, _, _, _, _ in default_permissions]),
            Permission.is_active == True
        )
        result = await self.db.execute(stmt)
        existing_names = set(result.scalars().all())
        
        created_permissions = []
        to_create = []
        
        for name, display_name, description, module, action in default_permissions:
            if name not in existing_names:
                to_create.append({
                    "name": name,
                    "display_name": display_name,
                    "description": description,
                    "module": module,
                    "action": action,
                    "is_active": True
                })
        
        if to_create:
            # Insert in batches to avoid issues with very large inserts
            batch_size = 100
            for i in range(0, len(to_create), batch_size):
                batch = to_create[i:i+batch_size]
                # Use PostgreSQL-specific insert with on_conflict_do_nothing
                insert_stmt = pg_insert(Permission).values(batch).on_conflict_do_nothing(
                    index_elements=['module', 'action']  # Use the unique constraint
                )
                result = await self.db.execute(insert_stmt.returning(Permission))
                batch_created = result.scalars().all()
                created_permissions.extend(batch_created)
            
            await self.db.commit()
            
            logger.info(f"Created {len(created_permissions)} new permissions")
        else:
            logger.info("All permissions already exist")
        
        return created_permissions
    
    async def initialize_default_roles(self, organization_id: int) -> List[Role]:
        """Initialize default roles for an organization"""
        await self.initialize_default_permissions()
        
        from app.services.rbac_permissions import get_default_role_permissions
        
        all_permissions = await self.get_permissions()
        permission_map = {p.name: p.id for p in all_permissions}
        
        # Get comprehensive role permissions
        role_permissions_map = get_default_role_permissions()
        
        default_roles = [
            {
                "name": RoleType.ADMIN.value,
                "display_name": "Admin",
                "description": "Full access to all modules",
                "permissions": role_permissions_map.get("admin", [])
            },
            {
                "name": RoleType.MANAGER.value,
                "display_name": "Manager",
                "description": "Module-level access",
                "permissions": role_permissions_map.get("manager", [])
            },
            {
                "name": RoleType.SUPPORT.value,
                "display_name": "Support Agent",
                "description": "Handle operations with limited permissions",
                "permissions": role_permissions_map.get("support", [])
            },
            {
                "name": RoleType.VIEWER.value,
                "display_name": "Viewer",
                "description": "Read-only access to data",
                "permissions": role_permissions_map.get("viewer", [])
            },
            {
                "name": RoleType.ORG_ADMIN.value,
                "display_name": "Organization Admin",
                "description": "Full organization management access",
                "permissions": role_permissions_map.get("org_admin", [])  # Add if defined in rbac_permissions
            }
        ]
        
        # Batch check existing roles
        stmt = select(Role.name).filter_by(
            organization_id=organization_id
        ).where(Role.name.in_([r["name"] for r in default_roles]))
        result = await self.db.execute(stmt)
        existing_names = set(result.scalars().all())
        
        created_roles = []
        
        for role_data in default_roles:
            if role_data["name"] not in existing_names:
                # Filter permissions to only include those that exist
                permission_ids = [
                    permission_map[p] for p in role_data["permissions"] 
                    if p in permission_map
                ]
                
                logger.info(f"Creating role '{role_data['name']}' with {len(permission_ids)} permissions out of {len(role_data['permissions'])} requested")
                
                role_create = RoleCreate(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data["description"],
                    organization_id=organization_id,
                    permission_ids=permission_ids
                )
                created_roles.append(await self.create_role(role_create))
        
        return created_roles
    
    # Company-scoped RBAC
    async def user_has_company_access(self, user_id: int, company_id: int) -> bool:
        """Check if user has access to a specific company"""
        from app.models.user_models import UserCompany
        
        result = await self.db.execute(
            select(UserCompany).filter_by(user_id=user_id, company_id=company_id, is_active=True)
        )
        assignment = result.scalars().first()
        
        return assignment is not None
    
    async def user_is_company_admin(self, user_id: int, company_id: int) -> bool:
        """Check if user is admin of a specific company"""
        from app.models.user_models import UserCompany
        
        result = await self.db.execute(
            select(UserCompany).filter_by(
                user_id=user_id,
                company_id=company_id,
                is_active=True,
                is_company_admin=True
            )
        )
        assignment = result.scalars().first()
        
        return assignment is not None
    
    async def get_user_companies(self, user_id: int) -> List[int]:
        """Get list of company IDs that user has access to"""
        from app.models.user_models import UserCompany
        
        result = await self.db.execute(
            select(UserCompany).filter_by(user_id=user_id, is_active=True)
        )
        assignments = result.scalars().all()
        
        return [assignment.company_id for assignment in assignments]
    
    async def get_user_admin_companies(self, user_id: int) -> List[int]:
        """Get list of company IDs where user is admin"""
        from app.models.user_models import UserCompany
        
        result = await self.db.execute(
            select(UserCompany).filter_by(
                user_id=user_id,
                is_active=True,
                is_company_admin=True
            )
        )
        assignments = result.scalars().all()
        
        return [assignment.company_id for assignment in assignments]
    
    async def user_has_company_permission(self, user_id: int, company_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission within a company scope"""
        logger.debug(f"Checking company permission '{permission_name}' for user_id {user_id}, company_id {company_id}")
        
        if not await self.user_has_company_access(user_id, company_id):
            logger.debug(f"User {user_id} has no access to company {company_id}")
            return False
        
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if not user:
            logger.debug(f"User {user_id} not found")
            return False
        
        if user.role in ["org_admin", "super_admin", "management"] or user.is_super_admin:
            logger.debug(f"Granted company permission '{permission_name}' to user {user_id} due to role {user.role}")
            return True
        
        if await self.user_is_company_admin(user_id, company_id):
            org_only_permissions = ["create_organization", "delete_organization", "manage_organization_settings"]
            if permission_name not in org_only_permissions:
                logger.debug(f"Granted company permission '{permission_name}' to user {user_id} as company admin")
                return True
        
        has_permission = await self.user_has_permission(user_id, permission_name)
        logger.debug(f"Permission check for '{permission_name}': {'granted' if has_permission else 'denied'}")
        return has_permission