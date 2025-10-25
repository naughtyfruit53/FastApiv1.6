"""
RBAC service layer for Service CRM role-based access control
"""

from typing import List, Optional, Dict, Set
from sqlalchemy import select, and_, or_, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

from app.models import (
    User, ServiceRole, ServicePermission, ServiceRolePermission, 
    UserServiceRole, Organization
)
from app.schemas.rbac import (
    ServiceRoleCreate, ServiceRoleUpdate, ServicePermissionCreate,
    UserServiceRoleCreate, ServiceRoleType, ServiceModule, ServiceAction
)
from app.core.permissions import Permission
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

class RBACService:
    """Service class for Role-Based Access Control operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Permission Management
    async def create_permission(self, permission: ServicePermissionCreate) -> ServicePermission:
        """Create a new service permission"""
        db_permission = ServicePermission(**permission.model_dump())
        self.db.add(db_permission)
        await self.db.commit()
        await self.db.refresh(db_permission)
        logger.info(f"Created service permission: {db_permission.name}")
        return db_permission
    
    async def get_permissions(self, 
                             module: Optional[str] = None,
                             action: Optional[str] = None,
                             is_active: bool = True) -> List[ServicePermission]:
        """Get service permissions with optional filtering"""
        from app.schemas.rbac import ServiceModule, ServiceAction
        
        stmt = select(ServicePermission)
        
        if is_active is not None:
            stmt = stmt.where(ServicePermission.is_active == is_active)
        if module:
            stmt = stmt.where(ServicePermission.module == module)
        if action:
            stmt = stmt.where(ServicePermission.action == action)
            
        result = await self.db.execute(stmt.order_by(ServicePermission.module, ServicePermission.action))
        permissions = result.scalars().all()
        
        valid_permissions = []
        valid_modules = {m.value for m in ServiceModule}
        valid_actions = {a.value for a in ServiceAction}
        
        for perm in permissions:
            if perm.module in valid_modules and perm.action in valid_actions:
                valid_permissions.append(perm)
            else:
                logger.warning(f"Filtering out permission with invalid module/action: {perm.name} (module={perm.module}, action={perm.action})")
        
        return valid_permissions
    
    async def get_permission_by_name(self, name: str) -> Optional[ServicePermission]:
        """Get permission by name"""
        result = await self.db.execute(
            select(ServicePermission).filter_by(name=name, is_active=True)
        )
        return result.scalars().first()
    
    # Role Management
    async def create_role(self, role: ServiceRoleCreate, created_by_user_id: Optional[int] = None) -> ServiceRole:
        """Create a new service role with permissions"""
        result = await self.db.execute(
            select(ServiceRole).filter_by(organization_id=role.organization_id, name=role.name)
        )
        existing = result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role.name}' already exists in this organization"
            )
        
        role_data = role.model_dump(exclude={'permission_ids'})
        db_role = ServiceRole(**role_data)
        self.db.add(db_role)
        await self.db.flush()
        
        if role.permission_ids:
            for permission_id in role.permission_ids:
                result = await self.db.execute(
                    select(ServicePermission).filter_by(id=permission_id, is_active=True)
                )
                permission = result.scalars().first()
                
                if permission:
                    role_permission = ServiceRolePermission(
                        organization_id=role.organization_id,
                        role_id=db_role.id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Created service role: {db_role.name} for organization {db_role.organization_id}")
        return db_role
    
    async def get_roles(self, organization_id: int, is_active: bool = True) -> List[ServiceRole]:
        """Get service roles for an organization"""
        stmt = select(ServiceRole).filter_by(organization_id=organization_id)
        
        if is_active is not None:
            stmt = stmt.where(ServiceRole.is_active == is_active)
            
        result = await self.db.execute(stmt.order_by(ServiceRole.name))
        return result.scalars().all()
    
    async def get_role_by_id(self, role_id: int, organization_id: Optional[int] = None) -> Optional[ServiceRole]:
        """Get role by ID with optional organization filtering"""
        stmt = select(ServiceRole).filter_by(id=role_id)
        
        if organization_id:
            stmt = stmt.where(ServiceRole.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_role_with_permissions(self, role_id: int) -> Optional[ServiceRole]:
        """Get role with its permissions loaded"""
        result = await self.db.execute(
            select(ServiceRole).options(
                joinedload(ServiceRole.permissions).joinedload(ServiceRolePermission.permission)
            ).filter_by(id=role_id)
        )
        return result.scalars().first()
    
    async def update_role(self, role_id: int, updates: ServiceRoleUpdate, organization_id: Optional[int] = None) -> ServiceRole:
        """Update a service role"""
        stmt = select(ServiceRole).filter_by(id=role_id)
        if organization_id:
            stmt = stmt.where(ServiceRole.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        db_role = result.scalars().first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        update_data = updates.model_dump(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        if updates.permission_ids is not None:
            await self.db.execute(
                ServiceRolePermission.__table__.delete().where(
                    ServiceRolePermission.role_id == role_id
                )
            )
            
            for permission_id in updates.permission_ids:
                perm_result = await self.db.execute(
                    select(ServicePermission).filter_by(id=permission_id, is_active=True)
                )
                permission = perm_result.scalars().first()
                
                if permission:
                    role_permission = ServiceRolePermission(
                        organization_id=db_role.organization_id,
                        role_id=role_id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        await self.db.commit()
        await self.db.refresh(db_role)
        logger.info(f"Updated service role: {db_role.name}")
        return db_role
    
    async def delete_role(self, role_id: int, organization_id: Optional[int] = None) -> bool:
        """Delete a service role (soft delete by setting is_active=False)"""
        stmt = select(ServiceRole).filter_by(id=role_id)
        if organization_id:
            stmt = stmt.where(ServiceRole.organization_id == organization_id)
            
        result = await self.db.execute(stmt)
        db_role = result.scalars().first()
        if not db_role:
            return False
        
        count_stmt = select(func.count('*')).select_from(UserServiceRole).where(
            UserServiceRole.role_id == role_id, UserServiceRole.is_active == True
        )
        count_result = await self.db.execute(count_stmt)
        active_assignments = count_result.scalar()
        
        if active_assignments > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role '{db_role.name}' as it is assigned to {active_assignments} users"
            )
        
        db_role.is_active = False
        await self.db.commit()
        logger.info(f"Deleted service role: {db_role.name}")
        return True
    
    # User Role Assignment
    async def assign_role_to_user(self, user_id: int, role_id: int, assigned_by_id: Optional[int] = None) -> UserServiceRole:
        """Assign a service role to a user"""
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        role_result = await self.db.execute(
            select(ServiceRole).filter_by(id=role_id, is_active=True)
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
            select(UserServiceRole).filter_by(user_id=user_id, role_id=role_id)
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
        
        assignment = UserServiceRole(
            organization_id=user.organization_id,
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
        """Remove a service role from a user"""
        result = await self.db.execute(
            select(UserServiceRole).filter_by(
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
    
    async def get_user_service_roles(self, user_id: int) -> List[ServiceRole]:
        """Get all active service roles for a user"""
        result = await self.db.execute(
            select(ServiceRole)
            .join(UserServiceRole)
            .where(
                UserServiceRole.user_id == user_id,
                UserServiceRole.is_active == True,
                ServiceRole.is_active == True
            )
        )
        return result.scalars().all()
    
    async def get_users_with_role(self, role_id: int) -> List[User]:
        """Get all users assigned to a specific role"""
        result = await self.db.execute(
            select(User)
            .join(UserServiceRole)
            .where(
                UserServiceRole.role_id == role_id,
                UserServiceRole.is_active == True,
                User.is_active == True
            )
        )
        return result.scalars().all()
    
    async def user_has_service_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific service permission through their roles"""
        await self.initialize_default_permissions()
        logger.debug(f"Checking permission '{permission_name}' for user_id {user_id}")
        
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        if user:
            logger.debug(f"User {user_id} role: {user.role}, is_super_admin: {user.is_super_admin}")
            if user.is_super_admin or user.role == 'super_admin':
                logger.debug(f"Granted permission '{permission_name}' to super_admin user {user_id}")
                return True
            if user.role == 'org_admin':
                # Extended fallback permissions for org_admin
                if (permission_name.startswith('crm_') or 
                    permission_name == 'crm_admin' or 
                    permission_name.startswith('mail:') or 
                    permission_name in ['crm_commission_read', 'crm_commission_create', 
                                      'crm_commission_update', 'crm_commission_delete']):
                    logger.debug(f"Granted permission '{permission_name}' to org_admin user {user_id} via fallback")
                    return True
        
        user_roles = await self.get_user_service_roles(user_id)
        logger.debug(f"User {user_id} active roles: {[role.name for role in user_roles]}")
        
        for role in user_roles:
            result = await self.db.execute(
                select(ServicePermission)
                .join(ServiceRolePermission)
                .where(
                    ServiceRolePermission.role_id == role.id,
                    ServicePermission.name == permission_name,
                    ServicePermission.is_active == True
                )
            )
            if result.scalars().first():
                logger.debug(f"Granted permission '{permission_name}' to user {user_id} via role {role.name}")
                return True
        
        logger.debug(f"Denied permission '{permission_name}' for user {user_id}")
        return False
    
    async def get_user_service_permissions(self, user_id: int) -> Set[str]:
        """Get all service permissions for a user"""
        await self.initialize_default_permissions()
        logger.debug(f"Fetching permissions for user_id {user_id}")
        
        user_result = await self.db.execute(select(User).filter_by(id=user_id))
        user = user_result.scalars().first()
        
        permissions = set()
        if user and user.role == 'org_admin':
            logger.debug(f"Adding org_admin fallback permissions for user {user_id}")
            fallback_result = await self.db.execute(
                select(ServicePermission.name).where(
                    or_(
                        ServicePermission.name.like('crm_%'),
                        ServicePermission.name == 'crm_admin',
                        ServicePermission.name.like('mail:%'),
                        ServicePermission.name.in_(['crm_commission_read', 'crm_commission_create', 
                                                  'crm_commission_update', 'crm_commission_delete'])
                    ),
                    ServicePermission.is_active == True
                )
            )
            permissions.update({row[0] for row in fallback_result.fetchall()})
            logger.debug(f"Fallback permissions for org_admin: {permissions}")
        
        result = await self.db.execute(
            select(ServicePermission.name)
            .select_from(UserServiceRole)
            .join(UserServiceRole.role)
            .join(ServiceRole.permissions)
            .join(ServiceRolePermission.permission)
            .where(
                UserServiceRole.user_id == user_id,
                UserServiceRole.is_active == True,
                ServicePermission.is_active == True
            )
        )
        role_permissions = {row[0] for row in result.fetchall()}
        logger.debug(f"Permissions from roles for user {user_id}: {role_permissions}")
        
        permissions.update(role_permissions)
        logger.debug(f"Final permissions for user {user_id}: {permissions}")
        
        return permissions
    
    # Bulk Operations
    async def assign_multiple_roles_to_user(self, user_id: int, role_ids: List[int], assigned_by_id: Optional[int] = None) -> List[UserServiceRole]:
        """Assign multiple roles to a user"""
        assignments = []
        for role_id in role_ids:
            try:
                assignment = await self.assign_role_to_user(user_id, role_id, assigned_by_id)
                assignments.append(assignment)
            except HTTPException as e:
                logger.warning(f"Failed to assign role {role_id} to user {user_id}: {e.detail}")
        
        return assignments
    
    async def remove_all_service_roles_from_user(self, user_id: int) -> int:
        """Remove all service roles from a user"""
        result = await self.db.execute(
            select(UserServiceRole).filter_by(user_id=user_id, is_active=True)
        )
        assignments = result.scalars().all()
        
        count = len(assignments)
        for assignment in assignments:
            assignment.is_active = False
        
        await self.db.commit()
        logger.info(f"Removed {count} role assignments from user {user_id}")
        return count
    
    # Initialization
    async def initialize_default_permissions(self) -> List[ServicePermission]:
        """Initialize default service permissions"""
        default_permissions = [
            ("service_create", "Create Services", "Create new services", "service", "create"),
            ("service_read", "View Services", "View service information", "service", "read"),
            ("service_update", "Update Services", "Modify service information", "service", "update"),
            ("service_delete", "Delete Services", "Delete services", "service", "delete"),
            ("technician_create", "Create Technicians", "Add new technicians", "technician", "create"),
            ("technician_read", "View Technicians", "View technician information", "technician", "read"),
            ("technician_update", "Update Technicians", "Modify technician information", "technician", "update"),
            ("technician_delete", "Delete Technicians", "Remove technicians", "technician", "delete"),
            ("appointment_create", "Create Appointments", "Schedule new appointments", "appointment", "create"),
            ("appointment_read", "View Appointments", "View appointment information", "appointment", "read"),
            ("appointment_update", "Update Appointments", "Modify appointments", "appointment", "update"),
            ("appointment_delete", "Cancel Appointments", "Cancel appointments", "appointment", "delete"),
            ("customer_service_create", "Create Customer Records", "Create customer service records", "customer_service", "create"),
            ("customer_service_read", "View Customer Records", "View customer service information", "customer_service", "read"),
            ("customer_service_update", "Update Customer Records", "Modify customer service records", "customer_service", "update"),
            ("customer_service_delete", "Delete Customer Records", "Remove customer service records", "customer_service", "delete"),
            ("work_order_create", "Create Work Orders", "Create new work orders", "work_order", "create"),
            ("work_order_read", "View Work Orders", "View work order information", "work_order", "read"),
            ("work_order_update", "Update Work Orders", "Modify work orders", "work_order", "update"),
            ("work_order_delete", "Delete Work Orders", "Remove work orders", "work_order", "delete"),
            ("service_reports_read", "View Service Reports", "Access service reports", "service_reports", "read"),
            ("service_reports_export", "Export Service Reports", "Export service reports", "service_reports", "export"),
            ("crm_admin", "CRM Administration", "Full CRM administration access", "crm_admin", "admin"),
            ("crm_settings", "CRM Settings", "Manage CRM settings", "crm_admin", "update"),
            ("mail:dashboard:read", "Read Mail Dashboard", "View mail dashboard statistics", "mail", "read"),
            ("mail:accounts:read", "Read Mail Accounts", "View email accounts", "mail", "read"),
            ("mail:accounts:create", "Create Mail Accounts", "Add new email accounts", "mail", "create"),
            ("mail:accounts:update", "Update Mail Accounts", "Modify email accounts", "mail", "update"),
            ("mail:accounts:delete", "Delete Mail Accounts", "Remove email accounts", "mail", "delete"),
            ("mail:emails:read", "Read Emails", "View emails", "mail", "read"),
            ("mail:emails:compose", "Compose Emails", "Send new emails", "mail", "create"),
            ("mail:emails:update", "Update Emails", "Modify emails", "mail", "update"),
            ("mail:emails:sync", "Sync Emails", "Synchronize email accounts", "mail", "update"),
            ("mail:templates:read", "Read Templates", "View email templates", "mail", "read"),
            ("mail:templates:create", "Create Templates", "Add new email templates", "mail", "create"),
            ("crm_lead_read", "Read Leads", "View leads", "crm_lead", "read"),
            ("crm_lead_create", "Create Leads", "Create new leads", "crm_lead", "create"),
            ("crm_lead_update", "Update Leads", "Modify leads", "crm_lead", "update"),
            ("crm_lead_delete", "Delete Leads", "Delete leads", "crm_lead", "delete"),
            ("crm_lead_convert", "Convert Leads", "Convert leads to opportunities/customers", "crm_lead", "convert"),
            ("crm_opportunity_read", "Read Opportunities", "View opportunities", "crm_opportunity", "read"),
            ("crm_opportunity_create", "Create Opportunities", "Create new opportunities", "crm_opportunity", "create"),
            ("crm_opportunity_update", "Update Opportunities", "Modify opportunities", "crm_opportunity", "update"),
            ("crm_opportunity_delete", "Delete Opportunities", "Delete opportunities", "crm_opportunity", "delete"),
            ("crm_activity_read", "Read Activities", "View activities", "crm_activity", "read"),
            ("crm_activity_create", "Create Activities", "Create new activities", "crm_activity", "create"),
            ("crm_activity_update", "Update Activities", "Modify activities", "crm_activity", "update"),
            ("crm_activity_delete", "Delete Activities", "Delete activities", "crm_activity", "delete"),
            ("crm_analytics_read", "Read Analytics", "View CRM analytics", "crm_analytics", "read"),
            ("crm_analytics_export", "Export Analytics", "Export CRM analytics", "crm_analytics", "export"),
            ("crm_settings_read", "Read Settings", "View CRM settings", "crm_settings", "read"),
            ("crm_settings_update", "Update Settings", "Modify CRM settings", "crm_settings", "update"),
            ("crm_import", "Import Data", "Import CRM data", "crm", "import"),
            ("crm_export", "Export Data", "Export CRM data", "crm", "export"),
            ("crm_commission_read", "Read Commissions", "View commissions", "crm_commission", "read"),
            ("crm_commission_create", "Create Commissions", "Create new commissions", "crm_commission", "create"),
            ("crm_commission_update", "Update Commissions", "Modify commissions", "crm_commission", "update"),
            ("crm_commission_delete", "Delete Commissions", "Delete commissions", "crm_commission", "delete"),
        ]
        
        # Batch check existing permissions
        stmt = select(ServicePermission.name).where(
            ServicePermission.name.in_([name for name, _, _, _, _ in default_permissions]),
            ServicePermission.is_active == True
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
            insert_stmt = insert(ServicePermission).values(to_create)
            result = await self.db.execute(insert_stmt.returning(ServicePermission))
            created_permissions = result.scalars().all()
            await self.db.commit()
            
            for perm in created_permissions:
                logger.info(f"Created service permission: {perm.name}")
        
        return created_permissions
    
    async def initialize_default_roles(self, organization_id: int) -> List[ServiceRole]:
        """Initialize default service roles for an organization"""
        await self.initialize_default_permissions()
        
        all_permissions = await self.get_permissions()
        permission_map = {p.name: p.id for p in all_permissions}
        
        default_roles = [
            {
                "name": ServiceRoleType.ADMIN.value,
                "display_name": "Service Admin",
                "description": "Full access to all service CRM functionality",
                "permissions": list(permission_map.keys())
            },
            {
                "name": ServiceRoleType.MANAGER.value,
                "display_name": "Service Manager",
                "description": "Manage services, technicians, and appointments",
                "permissions": [
                    "service_read", "service_update", "service_create",
                    "technician_read", "technician_update", "technician_create",
                    "appointment_read", "appointment_update", "appointment_create",
                    "customer_service_read", "customer_service_update",
                    "work_order_read", "work_order_update", "work_order_create",
                    "service_reports_read", "service_reports_export",
                    "mail:dashboard:read", "mail:accounts:read", "mail:accounts:update", "mail:emails:read", "mail:emails:compose", "mail:emails:update", "mail:emails:sync",
                    "crm_lead_read", "crm_lead_create", "crm_lead_update", "crm_lead_convert",
                    "crm_opportunity_read", "crm_opportunity_create", "crm_opportunity_update",
                    "crm_activity_read", "crm_activity_create", "crm_activity_update",
                    "crm_analytics_read", "crm_analytics_export",
                    "crm_settings_read", "crm_settings_update",
                    "crm_import", "crm_export",
                    "crm_commission_read", "crm_commission_create", "crm_commission_update",
                ]
            },
            {
                "name": ServiceRoleType.SUPPORT.value,
                "display_name": "Support Agent",
                "description": "Handle customer service and basic operations",
                "permissions": [
                    "service_read",
                    "technician_read",
                    "appointment_read", "appointment_update", "appointment_create",
                    "customer_service_read", "customer_service_update", "customer_service_create",
                    "work_order_read", "work_order_update",
                    "service_reports_read",
                    "mail:dashboard:read", "mail:emails:read", "mail:emails:compose",
                    "crm_lead_read", "crm_lead_create", "crm_lead_update",
                    "crm_opportunity_read", "crm_opportunity_update",
                    "crm_activity_read", "crm_activity_create",
                    "crm_analytics_read",
                    "crm_commission_read",
                ]
            },
            {
                "name": ServiceRoleType.VIEWER.value,
                "display_name": "Viewer",
                "description": "Read-only access to service information",
                "permissions": [
                    "service_read",
                    "technician_read",
                    "appointment_read",
                    "customer_service_read",
                    "work_order_read",
                    "service_reports_read",
                    "mail:dashboard:read", "mail:emails:read",
                    "crm_lead_read",
                    "crm_opportunity_read",
                    "crm_activity_read",
                    "crm_analytics_read",
                    "crm_commission_read",
                ]
            }
        ]
        
        # Batch check existing roles
        stmt = select(ServiceRole.name).filter_by(
            organization_id=organization_id
        ).where(ServiceRole.name.in_([r["name"] for r in default_roles]))
        result = await self.db.execute(stmt)
        existing_names = set(result.scalars().all())
        
        created_roles = []
        
        for role_data in default_roles:
            if role_data["name"] not in existing_names:
                permission_ids = [permission_map[p] for p in role_data["permissions"] if p in permission_map]
                
                role_create = ServiceRoleCreate(
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
        
        if user.role in ["org_admin", "super_admin"] or user.is_super_admin:
            logger.debug(f"Granted company permission '{permission_name}' to user {user_id} due to role {user.role}")
            return True
        
        if await self.user_is_company_admin(user_id, company_id):
            org_only_permissions = ["create_organization", "delete_organization", "manage_organization_settings"]
            if permission_name not in org_only_permissions:
                logger.debug(f"Granted company permission '{permission_name}' to user {user_id} as company admin")
                return True
        
        has_permission = await self.user_has_service_permission(user_id, permission_name)
        logger.debug(f"Service permission check for '{permission_name}': {'granted' if has_permission else 'denied'}")
        return has_permission
    
    async def enforce_company_access(self, user_id: int, company_id: int, permission_name: Optional[str] = None):
        """Enforce company access and optionally permission - raises HTTPException if denied"""
        logger.debug(f"Enforcing company access for user_id {user_id}, company_id {company_id}, permission {permission_name}")
        
        if not await self.user_has_company_access(user_id, company_id):
            logger.debug(f"Access denied: User {user_id} has no access to company {company_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to this company"
            )
        
        if permission_name and not await self.user_has_company_permission(user_id, company_id, permission_name):
            logger.debug(f"Access denied: User {user_id} lacks permission '{permission_name}' for company {company_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing permission '{permission_name}' for this company"
            )