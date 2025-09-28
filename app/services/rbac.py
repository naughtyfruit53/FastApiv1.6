# app/services/rbac.py

"""
RBAC service layer for Service CRM role-based access control
"""

from typing import List, Optional, Dict, Set
from typing import TYPE_CHECKING
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status, Depends

from app.models import (
    User, ServiceRole, ServicePermission, ServiceRolePermission, 
    UserServiceRole, Organization
)
from app.schemas.rbac import (
    ServiceRoleCreate, ServiceRoleUpdate, ServicePermissionCreate,
    UserServiceRoleCreate, ServiceRoleType, ServiceModule, ServiceAction
)
from app.core.permissions import Permission
import logging

if TYPE_CHECKING:
    from app.api.v1.auth import get_current_active_user  # Type-only import to break circular import

logger = logging.getLogger(__name__)


class RBACService:
    """Service class for Role-Based Access Control operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Permission Management
    def create_permission(self, permission: ServicePermissionCreate) -> ServicePermission:
        """Create a new service permission"""
        db_permission = ServicePermission(**permission.model_dump())
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        logger.info(f"Created service permission: {db_permission.name}")
        return db_permission
    
    def get_permissions(self, 
                       module: Optional[str] = None,
                       action: Optional[str] = None,
                       is_active: bool = True) -> List[ServicePermission]:
        """Get service permissions with optional filtering"""
        query = self.db.query(ServicePermission)
        
        if is_active is not None:
            query = query.filter(ServicePermission.is_active == is_active)
        if module:
            query = query.filter(ServicePermission.module == module)
        if action:
            query = query.filter(ServicePermission.action == action)
            
        return query.order_by(ServicePermission.module, ServicePermission.action).all()
    
    def get_permission_by_name(self, name: str) -> Optional[ServicePermission]:
        """Get permission by name"""
        return self.db.query(ServicePermission).filter(
            ServicePermission.name == name,
            ServicePermission.is_active == True
        ).first()
    
    # Role Management
    def create_role(self, role: ServiceRoleCreate, created_by_user_id: Optional[int] = None) -> ServiceRole:
        """Create a new service role with permissions"""
        # Check if role already exists in organization
        existing = self.db.query(ServiceRole).filter(
            ServiceRole.organization_id == role.organization_id,
            ServiceRole.name == role.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role.name}' already exists in this organization"
            )
        
        # Create role
        role_data = role.model_dump(exclude={'permission_ids'})
        db_role = ServiceRole(**role_data)
        self.db.add(db_role)
        self.db.flush()  # Get the ID without committing
        
        # Assign permissions
        if role.permission_ids:
            for permission_id in role.permission_ids:
                permission = self.db.query(ServicePermission).filter(
                    ServicePermission.id == permission_id,
                    ServicePermission.is_active == True
                ).first()
                
                if permission:
                    role_permission = ServiceRolePermission(
                        organization_id=role.organization_id,  # ADD THIS LINE
                        role_id=db_role.id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        self.db.commit()
        self.db.refresh(db_role)
        logger.info(f"Created service role: {db_role.name} for organization {db_role.organization_id}")
        return db_role
    
    def get_roles(self, organization_id: int, is_active: bool = True) -> List[ServiceRole]:
        """Get service roles for an organization"""
        query = self.db.query(ServiceRole).filter(
            ServiceRole.organization_id == organization_id
        )
        
        if is_active is not None:
            query = query.filter(ServiceRole.is_active == is_active)
            
        return query.order_by(ServiceRole.name).all()
    
    def get_role_by_id(self, role_id: int, organization_id: Optional[int] = None) -> Optional[ServiceRole]:
        """Get role by ID with optional organization filtering"""
        query = self.db.query(ServiceRole).filter(ServiceRole.id == role_id)
        
        if organization_id:
            query = query.filter(ServiceRole.organization_id == organization_id)
            
        return query.first()
    
    def get_role_with_permissions(self, role_id: int) -> Optional[ServiceRole]:
        """Get role with its permissions loaded"""
        return self.db.query(ServiceRole).options(
            joinedload(ServiceRole.role_permissions).joinedload(ServiceRolePermission.permission)
        ).filter(ServiceRole.id == role_id).first()
    
    def update_role(self, role_id: int, updates: ServiceRoleUpdate, organization_id: Optional[int] = None) -> ServiceRole:
        """Update a service role"""
        query = self.db.query(ServiceRole).filter(ServiceRole.id == role_id)
        if organization_id:
            query = query.filter(ServiceRole.organization_id == organization_id)
            
        db_role = query.first()
        if not db_role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Update basic fields
        update_data = updates.model_dump(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        # Update permissions if provided
        if updates.permission_ids is not None:
            # Remove existing permissions
            self.db.query(ServiceRolePermission).filter(
                ServiceRolePermission.role_id == role_id
            ).delete()
            
            # Add new permissions
            for permission_id in updates.permission_ids:
                permission = self.db.query(ServicePermission).filter(
                    ServicePermission.id == permission_id,
                    ServicePermission.is_active == True
                ).first()
                
                if permission:
                    role_permission = ServiceRolePermission(
                        organization_id=db_role.organization_id,  # ADD THIS LINE FOR CONSISTENCY
                        role_id=role_id,
                        permission_id=permission_id
                    )
                    self.db.add(role_permission)
        
        self.db.commit()
        self.db.refresh(db_role)
        logger.info(f"Updated service role: {db_role.name}")
        return db_role
    
    def delete_role(self, role_id: int, organization_id: Optional[int] = None) -> bool:
        """Delete a service role (soft delete by setting is_active=False)"""
        query = self.db.query(ServiceRole).filter(ServiceRole.id == role_id)
        if organization_id:
            query = query.filter(ServiceRole.organization_id == organization_id)
            
        db_role = query.first()
        if not db_role:
            return False
        
        # Check if role is assigned to any users
        active_assignments = self.db.query(UserServiceRole).filter(
            UserServiceRole.role_id == role_id,
            UserServiceRole.is_active == True
        ).count()
        
        if active_assignments > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role '{db_role.name}' as it is assigned to {active_assignments} users"
            )
        
        db_role.is_active = False
        self.db.commit()
        logger.info(f"Deleted service role: {db_role.name}")
        return True
    
    # User Role Assignment
    def assign_role_to_user(self, user_id: int, role_id: int, assigned_by_id: Optional[int] = None) -> UserServiceRole:
        """Assign a service role to a user"""
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if role exists and is active
        role = self.db.query(ServiceRole).filter(
            ServiceRole.id == role_id,
            ServiceRole.is_active == True
        ).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found or inactive")
        
        # Check if user belongs to the same organization as the role
        if user.organization_id != role.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User and role must belong to the same organization"
            )
        
        # Check if assignment already exists
        existing = self.db.query(UserServiceRole).filter(
            UserServiceRole.user_id == user_id,
            UserServiceRole.role_id == role_id
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already has this role assigned"
                )
            else:
                # Reactivate existing assignment
                existing.is_active = True
                existing.assigned_by_id = assigned_by_id
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Reactivated role assignment: user {user_id} -> role {role_id}")
                return existing
        
        # Create new assignment
        assignment = UserServiceRole(
            organization_id=user.organization_id,  # ADD THIS LINE FOR CONSISTENCY
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=assigned_by_id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        logger.info(f"Assigned role: user {user_id} -> role {role_id}")
        return assignment
    
    def remove_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove a service role from a user"""
        assignment = self.db.query(UserServiceRole).filter(
            UserServiceRole.user_id == user_id,
            UserServiceRole.role_id == role_id,
            UserServiceRole.is_active == True
        ).first()
        
        if not assignment:
            return False
        
        assignment.is_active = False
        self.db.commit()
        logger.info(f"Removed role assignment: user {user_id} -> role {role_id}")
        return True
    
    def get_user_service_roles(self, user_id: int) -> List[ServiceRole]:
        """Get all active service roles for a user"""
        return self.db.query(ServiceRole).join(UserServiceRole).filter(
            UserServiceRole.user_id == user_id,
            UserServiceRole.is_active == True,
            ServiceRole.is_active == True
        ).all()
    
    def get_users_with_role(self, role_id: int) -> List[User]:
        """Get all users assigned to a specific role"""
        return self.db.query(User).join(UserServiceRole).filter(
            UserServiceRole.role_id == role_id,
            UserServiceRole.is_active == True,
            User.is_active == True
        ).all()
    
    # Permission Checking
    def user_has_service_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific service permission through their roles"""
        # Get user's active service roles
        user_roles = self.get_user_service_roles(user_id)
        
        # Check if any role has the required permission
        for role in user_roles:
            role_permissions = self.db.query(ServicePermission).join(ServiceRolePermission).filter(
                ServiceRolePermission.role_id == role.id,
                ServicePermission.name == permission_name,
                ServicePermission.is_active == True
            ).first()
            
            if role_permissions:
                return True
        
        return False
    
    def get_user_service_permissions(self, user_id: int) -> Set[str]:
        """Get all service permissions for a user"""
        query = self.db.query(ServicePermission.name) \
            .select_from(UserServiceRole) \
            .join(UserServiceRole.role) \
            .join(ServiceRole.role_permissions) \
            .join(ServiceRolePermission.permission) \
            .filter(
                UserServiceRole.user_id == user_id,
                UserServiceRole.is_active == True,
                ServicePermission.is_active == True
            )
        return set(row[0] for row in query.all())
    
    # Bulk Operations
    def assign_multiple_roles_to_user(self, user_id: int, role_ids: List[int], assigned_by_id: Optional[int] = None) -> List[UserServiceRole]:
        """Assign multiple roles to a user"""
        assignments = []
        for role_id in role_ids:
            try:
                assignment = self.assign_role_to_user(user_id, role_id, assigned_by_id)
                assignments.append(assignment)
            except HTTPException as e:
                logger.warning(f"Failed to assign role {role_id} to user {user_id}: {e.detail}")
        
        return assignments
    
    def remove_all_service_roles_from_user(self, user_id: int) -> int:
        """Remove all service roles from a user"""
        assignments = self.db.query(UserServiceRole).filter(
            UserServiceRole.user_id == user_id,
            UserServiceRole.is_active == True
        ).all()
        
        count = len(assignments)
        for assignment in assignments:
            assignment.is_active = False
        
        self.db.commit()
        logger.info(f"Removed {count} role assignments from user {user_id}")
        return count
    
    # Initialization
    def initialize_default_permissions(self) -> List[ServicePermission]:
        """Initialize default service permissions"""
        default_permissions = [
            # Service Management
            ("service_create", "Create Services", "Create new services", "service", "create"),
            ("service_read", "View Services", "View service information", "service", "read"),
            ("service_update", "Update Services", "Modify service information", "service", "update"),
            ("service_delete", "Delete Services", "Delete services", "service", "delete"),
            
            # Technician Management
            ("technician_create", "Create Technicians", "Add new technicians", "technician", "create"),
            ("technician_read", "View Technicians", "View technician information", "technician", "read"),
            ("technician_update", "Update Technicians", "Modify technician information", "technician", "update"),
            ("technician_delete", "Delete Technicians", "Remove technicians", "technician", "delete"),
            
            # Appointment Management
            ("appointment_create", "Create Appointments", "Schedule new appointments", "appointment", "create"),
            ("appointment_read", "View Appointments", "View appointment information", "appointment", "read"),
            ("appointment_update", "Update Appointments", "Modify appointments", "appointment", "update"),
            ("appointment_delete", "Cancel Appointments", "Cancel appointments", "appointment", "delete"),
            
            # Customer Service
            ("customer_service_create", "Create Customer Records", "Create customer service records", "customer_service", "create"),
            ("customer_service_read", "View Customer Records", "View customer service information", "customer_service", "read"),
            ("customer_service_update", "Update Customer Records", "Modify customer service records", "customer_service", "update"),
            ("customer_service_delete", "Delete Customer Records", "Remove customer service records", "customer_service", "delete"),
            
            # Work Orders
            ("work_order_create", "Create Work Orders", "Create new work orders", "work_order", "create"),
            ("work_order_read", "View Work Orders", "View work order information", "work_order", "read"),
            ("work_order_update", "Update Work Orders", "Modify work orders", "work_order", "update"),
            ("work_order_delete", "Delete Work Orders", "Remove work orders", "work_order", "delete"),
            
            # Service Reports
            ("service_reports_read", "View Service Reports", "Access service reports", "service_reports", "read"),
            ("service_reports_export", "Export Service Reports", "Export service reports", "service_reports", "export"),
            
            # CRM Admin
            ("crm_admin", "CRM Administration", "Full CRM administration access", "crm_admin", "admin"),
            ("crm_settings", "CRM Settings", "Manage CRM settings", "crm_admin", "update"),
            
            # Mail Module Permissions
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
        ]
        
        created_permissions = []
        for name, display_name, description, module, action in default_permissions:
            existing = self.get_permission_by_name(name)
            if not existing:
                permission = ServicePermissionCreate(
                    name=name,
                    display_name=display_name,
                    description=description,
                    module=module,
                    action=action
                )
                created_permissions.append(self.create_permission(permission))
        
        return created_permissions
    
    def initialize_default_roles(self, organization_id: int) -> List[ServiceRole]:
        """Initialize default service roles for an organization"""
        # Ensure permissions exist
        self.initialize_default_permissions()
        
        # Get all permissions
        all_permissions = self.get_permissions()
        permission_map = {p.name: p.id for p in all_permissions}
        
        # Define default roles with their permissions
        default_roles = [
            {
                "name": ServiceRoleType.ADMIN.value,
                "display_name": "Service Admin",
                "description": "Full access to all service CRM functionality",
                "permissions": list(permission_map.keys())  # All permissions
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
                    "mail:dashboard:read", "mail:accounts:read", "mail:accounts:update", "mail:emails:read", "mail:emails:compose", "mail:emails:update", "mail:emails:sync"
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
                    "mail:dashboard:read", "mail:emails:read", "mail:emails:compose"
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
                    "mail:dashboard:read", "mail:emails:read"
                ]
            }
        ]
        
        created_roles = []
        for role_data in default_roles:
            existing = self.db.query(ServiceRole).filter(
                ServiceRole.organization_id == organization_id,
                ServiceRole.name == role_data["name"]
            ).first()
            
            if not existing:
                permission_ids = [permission_map[p] for p in role_data["permissions"] if p in permission_map]
                
                role_create = ServiceRoleCreate(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data["description"],
                    organization_id=organization_id,
                    permission_ids=permission_ids
                )
                created_roles.append(self.create_role(role_create))
        
        return created_roles
    
    # Company-scoped permission methods for multi-company support
    
    def user_has_company_access(self, user_id: int, company_id: int) -> bool:
        """Check if user has access to a specific company"""
        from app.models.user_models import UserCompany
        
        # Check if user is assigned to the company
        assignment = self.db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id,
            UserCompany.is_active == True
        ).first()
        
        return assignment is not None
    
    def user_is_company_admin(self, user_id: int, company_id: int) -> bool:
        """Check if user is admin of a specific company"""
        from app.models.user_models import UserCompany
        
        assignment = self.db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id,
            UserCompany.is_active == True,
            UserCompany.is_company_admin == True
        ).first()
        
        return assignment is not None
    
    def get_user_companies(self, user_id: int) -> List[int]:
        """Get list of company IDs that user has access to"""
        from app.models.user_models import UserCompany
        
        assignments = self.db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.is_active == True
        ).all()
        
        return [assignment.company_id for assignment in assignments]
    
    def get_user_admin_companies(self, user_id: int) -> List[int]:
        """Get list of company IDs where user is admin"""
        from app.models.user_models import UserCompany
        
        assignments = self.db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.is_active == True,
            UserCompany.is_company_admin == True
        ).all()
        
        return [assignment.company_id for assignment in assignments]
    
    def user_has_company_permission(self, user_id: int, company_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission within a company scope"""
        
        # First check if user has access to the company
        if not self.user_has_company_access(user_id, company_id):
            return False
        
        # Check user's role - org admin or super admin have all permissions
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if user.role in ["org_admin", "super_admin"] or user.is_super_admin:
            return True
        
        # Check if user is company admin for this company
        if self.user_is_company_admin(user_id, company_id):
            # Company admins have most permissions except organization-level ones
            org_only_permissions = ["create_organization", "delete_organization", "manage_organization_settings"]
            if permission_name not in org_only_permissions:
                return True
        
        # Check service role permissions
        return self.user_has_service_permission(user_id, permission_name)
    
    def enforce_company_access(self, user_id: int, company_id: int, permission_name: Optional[str] = None):
        """Enforce company access and optionally permission - raises HTTPException if denied"""
        
        if not self.user_has_company_access(user_id, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to this company"
            )
        
        if permission_name and not self.user_has_company_permission(user_id, company_id, permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing permission '{permission_name}' for this company"
            )

def require_permission(permission: str):
    """Dependency to check if current user has a specific permission"""
    def dependency(current_user: User = Depends(get_current_active_user)):
        rbac = RBACService(dependency.db)  # Assuming db is available in dependency
        if not rbac.user_has_service_permission(current_user.id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        return current_user
    return dependency