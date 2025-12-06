# Revised: v1/app/core/permissions.py

from typing import Optional, List, Any, Union
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.models import User, Organization, PlatformUser
from app.schemas.user import UserRole, PlatformUserRole, UserInDB, PlatformUserInDB
from app.core.database import get_db
from app.core.audit import AuditLogger, get_client_ip, get_user_agent
from app.core.security import get_current_user
import logging

logger = logging.getLogger(__name__)


class Permission:
    """Permission constants - standardized to dotted format (module.action)"""
    
    # User management permissions (dotted format)
    MANAGE_USERS = "users.manage"
    VIEW_USERS = "users.view"
    CREATE_USERS = "users.create"
    DELETE_USERS = "users.delete"
    
    # Password management permissions
    RESET_OWN_PASSWORD = "password.reset_own"
    RESET_ORG_PASSWORDS = "password.reset_org"
    RESET_ANY_PASSWORD = "password.reset_any"
    
    # Data management permissions
    RESET_OWN_DATA = "data.reset_own"
    RESET_ORG_DATA = "data.reset_org"
    RESET_ANY_DATA = "data.reset_any"
    
    # Organization management permissions
    MANAGE_ORGANIZATIONS = "organizations.manage"
    VIEW_ORGANIZATIONS = "organizations.view"
    CREATE_ORGANIZATIONS = "organizations.create"
    DELETE_ORGANIZATIONS = "organizations.delete"
    
    # Platform administration permissions
    PLATFORM_ADMIN = "platform.admin"
    SUPER_ADMIN = "platform.super_admin"
    
    # Audit permissions
    VIEW_AUDIT_LOGS = "audit.view"
    VIEW_ALL_AUDIT_LOGS = "audit.view_all"
    
    # Factory reset permission (App Super Admin only)
    FACTORY_RESET = "platform.factory_reset"
    
    # Organization settings access
    ACCESS_ORG_SETTINGS = "settings.access"
    
    # Service CRM Module Permissions - CRUD operations per module
    # Service Management Permissions
    SERVICE_CREATE = "service.create"
    SERVICE_READ = "service.read"
    SERVICE_UPDATE = "service.update"
    SERVICE_DELETE = "service.delete"
    
    # Technician Management Permissions
    TECHNICIAN_CREATE = "technician.create"
    TECHNICIAN_READ = "technician.read"
    TECHNICIAN_UPDATE = "technician.update"
    TECHNICIAN_DELETE = "technician.delete"
    
    # Appointment Management Permissions
    APPOINTMENT_CREATE = "appointment.create"
    APPOINTMENT_READ = "appointment.read"
    APPOINTMENT_UPDATE = "appointment.update"
    APPOINTMENT_DELETE = "appointment.delete"
    
    # Customer Service Permissions
    CUSTOMER_SERVICE_CREATE = "customer_service.create"
    CUSTOMER_SERVICE_READ = "customer_service.read"
    CUSTOMER_SERVICE_UPDATE = "customer_service.update"
    CUSTOMER_SERVICE_DELETE = "customer_service.delete"
    
    # Work Order Permissions
    WORK_ORDER_CREATE = "work_order.create"
    WORK_ORDER_READ = "work_order.read"
    WORK_ORDER_UPDATE = "work_order.update"
    WORK_ORDER_DELETE = "work_order.delete"
    
    # Service Reports Permissions
    SERVICE_REPORTS_READ = "service_reports.read"
    SERVICE_REPORTS_EXPORT = "service_reports.export"
    
    # CRM Admin Permissions
    CRM_ADMIN = "crm.admin"
    CRM_SETTINGS = "crm.settings"
    
    # Voucher management permissions
    VIEW_VOUCHERS = "vouchers.view"
    MANAGE_VOUCHERS = "vouchers.manage"
    
    # Commission Permissions
    CRM_COMMISSION_READ = "crm.commission.read"
    CRM_COMMISSION_CREATE = "crm.commission.create"
    CRM_COMMISSION_UPDATE = "crm.commission.update"
    CRM_COMMISSION_DELETE = "crm.commission.delete"

    # Inventory permissions
    INVENTORY_READ = "inventory.read"
    INVENTORY_WRITE = "inventory.write"
    INVENTORY_UPDATE = "inventory.update"
    INVENTORY_DELETE = "inventory.delete"

    # Products permissions
    PRODUCTS_READ = "products.read"
    PRODUCTS_WRITE = "products.write"
    PRODUCTS_UPDATE = "products.update"
    PRODUCTS_DELETE = "products.delete"

    # Master Data permissions
    MASTER_DATA_READ = "master_data.read"
    MASTER_DATA_WRITE = "master_data.write"
    MASTER_DATA_UPDATE = "master_data.update"
    MASTER_DATA_DELETE = "master_data.delete"

    # Manufacturing permissions
    MANUFACTURING_READ = "manufacturing.read"
    MANUFACTURING_WRITE = "manufacturing.write"
    MANUFACTURING_UPDATE = "manufacturing.update"
    MANUFACTURING_DELETE = "manufacturing.delete"

    # Vendors permissions (specific for ERP master data)
    VENDORS_READ = "vendors.read"
    VENDORS_CREATE = "vendors.create"
    VENDORS_UPDATE = "vendors.update"
    VENDORS_DELETE = "vendors.delete"

    # Voucher permissions (specific for ERP vouchers)
    VOUCHER_READ = "voucher.read"
    VOUCHER_CREATE = "voucher.create"
    VOUCHER_UPDATE = "voucher.update"
    VOUCHER_DELETE = "voucher.delete"


# TODO: Remove after full migration (target: Q1 2026)
# Backward compatibility mapping for legacy permission formats
LEGACY_PERMISSION_MAP = {
    # Underscore format -> Dotted format
    "manage_users": "users.manage",
    "view_users": "users.view",
    "create_users": "users.create",
    "delete_users": "users.delete",
    "reset_own_password": "password.reset_own",
    "reset_org_passwords": "password.reset_org",
    "reset_any_password": "password.reset_any",
    "reset_own_data": "data.reset_own",
    "reset_org_data": "data.reset_org",
    "reset_any_data": "data.reset_any",
    "manage_organizations": "organizations.manage",
    "view_organizations": "organizations.view",
    "create_organizations": "organizations.create",
    "delete_organizations": "organizations.delete",
    "platform_admin": "platform.admin",
    "super_admin": "platform.super_admin",
    "view_audit_logs": "audit.view",
    "view_all_audit_logs": "audit.view_all",
    "factory_reset": "platform.factory_reset",
    "access_org_settings": "settings.access",
    "service_create": "service.create",
    "service_read": "service.read",
    "service_update": "service.update",
    "service_delete": "service.delete",
    "technician_create": "technician.create",
    "technician_read": "technician.read",
    "technician_update": "technician.update",
    "technician_delete": "technician.delete",
    "appointment_create": "appointment.create",
    "appointment_read": "appointment.read",
    "appointment_update": "appointment.update",
    "appointment_delete": "appointment.delete",
    "customer_service_create": "customer_service.create",
    "customer_service_read": "customer_service.read",
    "customer_service_update": "customer_service.update",
    "customer_service_delete": "customer_service.delete",
    "work_order_create": "work_order.create",
    "work_order_read": "work_order.read",
    "work_order_update": "work_order.update",
    "work_order_delete": "work_order.delete",
    "service_reports_read": "service_reports.read",
    "service_reports_export": "service_reports.export",
    "crm_admin": "crm.admin",
    "crm_settings": "crm.settings",
    "view_vouchers": "vouchers.view",
    "manage_vouchers": "vouchers.manage",
    "crm_commission_read": "crm.commission.read",
    "crm_commission_create": "crm.commission.create",
    "crm_commission_update": "crm.commission.update",
    "crm_commission_delete": "crm.commission.delete",
    # Colon format -> Dotted format
    "mail:dashboard:read": "mail.dashboard.read",
    "mail:accounts:read": "mail.accounts.read",
    "mail:accounts:create": "mail.accounts.create",
    "mail:accounts:update": "mail.accounts.update",
    "mail:accounts:delete": "mail.accounts.delete",
    "mail:emails:read": "mail.emails.read",
    "mail:emails:compose": "mail.emails.compose",
    "mail:emails:update": "mail.emails.update",
    "mail:emails:sync": "mail.emails.sync",
    "mail:templates:read": "mail.templates.read",
    "mail:templates:create": "mail.templates.create",
}

# Permission hierarchy: parent -> children
# Parent permissions grant all child permissions
PERMISSION_HIERARCHY = {
    "master_data.read": [
        "vendors.read",
        "products.read",
        "inventory.read",
    ],
    "master_data.write": [
        "vendors.create",
        "vendors.update",
        "products.write",
        "products.update",
        "inventory.write",
        "inventory.update",
    ],
    "master_data.delete": [
        "vendors.delete",
        "products.delete",
        "inventory.delete",
    ],
    "crm.admin": [
        "crm.settings",
        "crm.commission.read",
        "crm.commission.create",
        "crm.commission.update",
        "crm.commission.delete",
    ],
    "platform.super_admin": [
        "platform.admin",
        "platform.factory_reset",
    ],
    "platform.admin": [
        "organizations.manage",
        "organizations.view",
        "organizations.create",
        "organizations.delete",
        "audit.view_all",
    ],
}


class PermissionChecker:
    """Service for checking user permissions"""
    
    # Role-based permission mapping for regular users
    ROLE_PERMISSIONS = {
        'super_admin': [
            Permission.MANAGE_USERS,
            Permission.VIEW_USERS,
            Permission.CREATE_USERS,
            Permission.DELETE_USERS,
            Permission.RESET_OWN_PASSWORD,
            Permission.RESET_ORG_PASSWORDS,
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_OWN_DATA,
            Permission.RESET_ORG_DATA,
            Permission.RESET_ANY_DATA,
            Permission.MANAGE_ORGANIZATIONS,
            Permission.VIEW_ORGANIZATIONS,
            Permission.CREATE_ORGANIZATIONS,
            Permission.DELETE_ORGANIZATIONS,
            Permission.PLATFORM_ADMIN,
            Permission.SUPER_ADMIN,
            Permission.VIEW_AUDIT_LOGS,
            Permission.VIEW_ALL_AUDIT_LOGS,
            Permission.FACTORY_RESET,
            Permission.VIEW_VOUCHERS,
            Permission.MANAGE_VOUCHERS,
            # NEW: Add inventory/products/master_data for super_admin
            Permission.INVENTORY_READ,
            Permission.INVENTORY_WRITE,
            Permission.INVENTORY_UPDATE,
            Permission.INVENTORY_DELETE,
            Permission.PRODUCTS_READ,
            Permission.PRODUCTS_WRITE,
            Permission.PRODUCTS_UPDATE,
            Permission.PRODUCTS_DELETE,
            Permission.MASTER_DATA_READ,
            Permission.MASTER_DATA_WRITE,
            Permission.MASTER_DATA_UPDATE,
            Permission.MASTER_DATA_DELETE,
            # NEW: Add manufacturing for super_admin
            Permission.MANUFACTURING_READ,
            Permission.MANUFACTURING_WRITE,
            Permission.MANUFACTURING_UPDATE,
            Permission.MANUFACTURING_DELETE,
            # NEW: Add vendors and voucher permissions for super_admin
            Permission.VENDORS_READ,
            Permission.VENDORS_CREATE,
            Permission.VENDORS_UPDATE,
            Permission.VENDORS_DELETE,
            Permission.VOUCHER_READ,
            Permission.VOUCHER_CREATE,
            Permission.VOUCHER_UPDATE,
            Permission.VOUCHER_DELETE,
            # Note: App Super Admins don't have ACCESS_ORG_SETTINGS (per requirements)
        ],
        'org_admin': [
            Permission.MANAGE_USERS,
            Permission.VIEW_USERS,
            Permission.CREATE_USERS,
            Permission.DELETE_USERS,
            Permission.RESET_OWN_PASSWORD,
            Permission.RESET_ORG_PASSWORDS,
            Permission.RESET_OWN_DATA,
            Permission.RESET_ORG_DATA,  # Org admins can reset their org data
            Permission.VIEW_AUDIT_LOGS,
            Permission.ACCESS_ORG_SETTINGS,  # Org admins have access to org settings
            Permission.VIEW_VOUCHERS,
            Permission.MANAGE_VOUCHERS,
            # NEW: Add inventory/products/master_data for org_admin
            Permission.INVENTORY_READ,
            Permission.INVENTORY_WRITE,
            Permission.INVENTORY_UPDATE,
            Permission.INVENTORY_DELETE,
            Permission.PRODUCTS_READ,
            Permission.PRODUCTS_WRITE,
            Permission.PRODUCTS_UPDATE,
            Permission.PRODUCTS_DELETE,
            Permission.MASTER_DATA_READ,
            Permission.MASTER_DATA_WRITE,
            Permission.MASTER_DATA_UPDATE,
            Permission.MASTER_DATA_DELETE,
            # NEW: Add manufacturing for org_admin
            Permission.MANUFACTURING_READ,
            Permission.MANUFACTURING_WRITE,
            Permission.MANUFACTURING_UPDATE,
            Permission.MANUFACTURING_DELETE,
            # NEW: Add vendors and voucher permissions for org_admin
            Permission.VENDORS_READ,
            Permission.VENDORS_CREATE,
            Permission.VENDORS_UPDATE,
            Permission.VENDORS_DELETE,
            Permission.VOUCHER_READ,
            Permission.VOUCHER_CREATE,
            Permission.VOUCHER_UPDATE,
            Permission.VOUCHER_DELETE,
        ],
        'management': [
            Permission.MANAGE_USERS,
            Permission.VIEW_USERS,
            Permission.CREATE_USERS,
            Permission.DELETE_USERS,
            Permission.RESET_OWN_PASSWORD,
            Permission.RESET_ORG_PASSWORDS,
            Permission.RESET_OWN_DATA,
            Permission.RESET_ORG_DATA,
            Permission.VIEW_AUDIT_LOGS,
            Permission.ACCESS_ORG_SETTINGS,
            Permission.VIEW_VOUCHERS,
            Permission.MANAGE_VOUCHERS,
            # NEW: Add inventory/products/master_data for management
            Permission.INVENTORY_READ,
            Permission.INVENTORY_WRITE,
            Permission.INVENTORY_UPDATE,
            Permission.INVENTORY_DELETE,
            Permission.PRODUCTS_READ,
            Permission.PRODUCTS_WRITE,
            Permission.PRODUCTS_UPDATE,
            Permission.PRODUCTS_DELETE,
            Permission.MASTER_DATA_READ,
            Permission.MASTER_DATA_WRITE,
            Permission.MASTER_DATA_UPDATE,
            Permission.MASTER_DATA_DELETE,
            # NEW: Add manufacturing for management
            Permission.MANUFACTURING_READ,
            Permission.MANUFACTURING_WRITE,
            Permission.MANUFACTURING_UPDATE,
            Permission.MANUFACTURING_DELETE,
            # NEW: Add vendors and voucher permissions for management
            Permission.VENDORS_READ,
            Permission.VENDORS_CREATE,
            Permission.VENDORS_UPDATE,
            Permission.VENDORS_DELETE,
            Permission.VOUCHER_READ,
            Permission.VOUCHER_CREATE,
            Permission.VOUCHER_UPDATE,
            Permission.VOUCHER_DELETE,
        ],
        'manager': [
            Permission.VIEW_USERS,  # Can view users (their executives)
            Permission.CREATE_USERS,  # Can create executives under them
            Permission.RESET_OWN_PASSWORD,
            Permission.VIEW_AUDIT_LOGS,
            Permission.ACCESS_ORG_SETTINGS,  # Limited access
            Permission.VIEW_VOUCHERS,
            # NEW: Add read-only for inventory/products/master_data
            Permission.INVENTORY_READ,
            Permission.PRODUCTS_READ,
            Permission.MASTER_DATA_READ,
            # NEW: Add read-only for manufacturing
            Permission.MANUFACTURING_READ,
            # NEW: Add vendors and voucher read permissions for manager
            Permission.VENDORS_READ,
            Permission.VOUCHER_READ,
        ],
        'executive': [
            Permission.RESET_OWN_PASSWORD,
            Permission.ACCESS_ORG_SETTINGS,  # Basic access
            Permission.VIEW_VOUCHERS,
            # NEW: Add read-only for inventory/products/master_data
            Permission.INVENTORY_READ,
            Permission.PRODUCTS_READ,
            Permission.MASTER_DATA_READ,
            # NEW: Add read-only for manufacturing
            Permission.MANUFACTURING_READ,
        ],
    }
    
    # Platform role permissions
    PLATFORM_ROLE_PERMISSIONS = {
        'super_admin': [
            Permission.SUPER_ADMIN,
            Permission.PLATFORM_ADMIN,
            Permission.MANAGE_USERS,  # For platform users
            Permission.CREATE_USERS,  # For creating app_admins and super_admins
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_ANY_DATA,
            Permission.MANAGE_ORGANIZATIONS,
            Permission.VIEW_ORGANIZATIONS,
            Permission.CREATE_ORGANIZATIONS,
            Permission.DELETE_ORGANIZATIONS,
            Permission.VIEW_ALL_AUDIT_LOGS,
            Permission.FACTORY_RESET,  # Only super_admin can factory reset
        ],
        'app_admin': [
            Permission.PLATFORM_ADMIN,
            Permission.MANAGE_ORGANIZATIONS,
            Permission.CREATE_ORGANIZATIONS,
            Permission.VIEW_ORGANIZATIONS,
            Permission.VIEW_AUDIT_LOGS,
            # Note: app_admin CANNOT: manage platform admins, reset app/org data, factory reset
        ],
    }
    
    @staticmethod
    def normalize_permission(permission: str) -> str:
        """
        Normalize permission to dotted format with backward compatibility.
        
        Args:
            permission: Permission string in any format (underscore, colon, or dotted)
            
        Returns:
            Normalized permission string in dotted format
        """
        # Return as-is if already in dotted format or unknown
        if permission in LEGACY_PERMISSION_MAP:
            normalized = LEGACY_PERMISSION_MAP[permission]
            logger.debug(f"Normalized legacy permission '{permission}' to '{normalized}'")
            return normalized
        return permission
    
    @staticmethod
    def get_implied_permissions(permission: str) -> List[str]:
        """
        Get all permissions implied by a parent permission through hierarchy.
        
        Args:
            permission: Parent permission
            
        Returns:
            List of child permissions granted by the parent
        """
        return PERMISSION_HIERARCHY.get(permission, [])
    
    @staticmethod
    def has_permission(user: Union[User, UserInDB], permission: str) -> bool:
        """
        Check if user has permission with backward compatibility and hierarchy support.
        
        Args:
            user: User to check
            permission: Permission to check (accepts legacy and dotted formats)
            
        Returns:
            True if user has permission (directly or through hierarchy)
        """
        role = user.role.lower() if hasattr(user, 'role') else None
        is_super_admin = getattr(user, 'is_super_admin', False)
        user_id = getattr(user, 'id', 'unknown')
        
        # Super admins have all permissions
        if is_super_admin or role == 'super_admin':
            logger.info(f"Permission '{permission}' granted to super_admin user {user_id}")
            return True
        
        # Normalize permission to dotted format
        normalized_permission = PermissionChecker.normalize_permission(permission)
        
        # Get user's role permissions
        user_permissions = PermissionChecker.ROLE_PERMISSIONS.get(role, [])
        
        # Check direct permission
        if normalized_permission in user_permissions:
            logger.info(f"Permission '{normalized_permission}' granted to user {user_id} (role: {role})")
            return True
        
        # Check if user has a parent permission that grants this one
        for user_perm in user_permissions:
            implied = PermissionChecker.get_implied_permissions(user_perm)
            if normalized_permission in implied:
                logger.info(f"Permission '{normalized_permission}' granted to user {user_id} via parent permission '{user_perm}'")
                return True
        
        logger.warning(f"Permission '{normalized_permission}' denied for user {user_id} (role: {role})")
        return False
    
    @staticmethod
    def has_platform_permission(platform_user: Union[User, PlatformUser, UserInDB, PlatformUserInDB], permission: str) -> bool:
        """Check platform-specific permissions with backward compatibility, handling both ORM and Pydantic models"""
        # Extract attributes consistently for both ORM and Pydantic
        role = platform_user.role.lower() if hasattr(platform_user, 'role') else ''
        is_super_admin = getattr(platform_user, 'is_super_admin', False)
        user_id = getattr(platform_user, 'id', 'None')
        email = getattr(platform_user, 'email', 'None')
        organization_id = getattr(platform_user, 'organization_id', 'None')
        
        # Normalize permission
        normalized_permission = PermissionChecker.normalize_permission(permission)
        
        logger.info(f"Permission check for {normalized_permission}: id={user_id}, email={email}, role={role}, is_super_admin={is_super_admin}, organization_id={organization_id}")

        # Use attribute check instead of type name for robustness
        if hasattr(platform_user, 'organization_id') and platform_user.organization_id is not None:
            # Organization user (User or UserInDB)
            if is_super_admin or role == 'super_admin':
                logger.info("Permission granted: Organization user is super admin")
                return True
            # Fallback to regular permission check
            granted = PermissionChecker.has_permission(platform_user, normalized_permission)
            logger.info(f"Regular permission check result: {granted}")
            return granted
        
        else:
            # Platform user (PlatformUser or PlatformUserInDB)
            if role == 'super_admin':
                logger.info("Permission granted: Platform user is super admin")
                return True
            platform_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get(role, [])
            
            # Check direct permission
            if normalized_permission in platform_permissions:
                logger.info(f"Platform permission check result: True")
                return True
            
            # Check hierarchy
            for user_perm in platform_permissions:
                implied = PermissionChecker.get_implied_permissions(user_perm)
                if normalized_permission in implied:
                    logger.info(f"Platform permission granted via parent permission '{user_perm}'")
                    return True
            
            logger.info(f"Platform permission check result: False, permissions: {platform_permissions}")
            return False
    
    @staticmethod
    def require_permission(
        permission: str,
        user: Union[User, UserInDB],
        db: Session,
        request: Optional[Request] = None,
        organization_id: Optional[int] = None
    ) -> bool:
        """Require user to have specific permission, raise exception if not"""
        if not PermissionChecker.has_permission(user, permission):
            # Log permission denied event
            if db and request:
                AuditLogger.log_permission_denied(
                    db=db,
                    user_email=user.email,
                    attempted_action=permission,
                    user_id=user.id,
                    user_role=user.role,
                    organization_id=organization_id or user.organization_id,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    details={"required_permission": permission}
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return True
    
    @staticmethod
    def can_access_organization(user: Union[User, UserInDB], organization_id: int) -> bool:
        """Check if user can access specific organization data"""
        # Super admin always can access any organization
        if getattr(user, 'is_super_admin', False) or user.role.lower() == 'super_admin':
            return True
        
        # Regular users can only access their own organization
        return user.organization_id == organization_id
    
    @staticmethod
    def require_organization_access(
        user: Union[User, UserInDB],
        organization_id: int,
        db: Session,
        request: Optional[Request] = None
    ) -> bool:
        """Require user to have access to specific organization"""
        if not PermissionChecker.can_access_organization(user, organization_id):
            # Log permission denied event
            if db and request:
                AuditLogger.log_permission_denied(
                    db=db,
                    user_email=user.email,
                    attempted_action=f"access_organization_{organization_id}",
                    user_id=user.id,
                    user_role=user.role,
                    organization_id=user.organization_id,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    details={"requested_organization_id": organization_id}
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to organization {organization_id}"
            )
        return True
    
    @staticmethod
    def can_reset_user_password(current_user: Union[User, UserInDB], target_user: Union[User, UserInDB]) -> bool:
        """Check if current user can reset target user's password"""
        # Super admin can reset any password
        if getattr(current_user, 'is_super_admin', False) or current_user.role.lower() == 'super_admin':
            return True
        
        # Org admin can reset passwords within their organization
        if current_user.role.lower() == 'org_admin':
            return current_user.organization_id == target_user.organization_id
        
        # Users can only reset their own password
        return current_user.id == target_user.id
    
    @staticmethod
    def can_reset_organization_data(current_user: Union[User, UserInDB], organization_id: int) -> bool:
        """Check if current user can reset organization data"""
        # Super admin can reset any organization data
        if getattr(current_user, 'is_super_admin', False) or current_user.role.lower() == 'super_admin':
            return True
        
        # Org admin can reset data for their own organization
        if current_user.role.lower() == 'org_admin':
            return current_user.organization_id == organization_id
        
        return False
    
    @staticmethod
    def get_accessible_organizations(user: Union[User, UserInDB], db: Session) -> List[int]:
        """Get list of organization IDs user can access"""
        # Super admin can access all organizations
        if getattr(user, 'is_super_admin', False) or user.role.lower() == 'super_admin':
            organizations = db.query(Organization.id).all()
            return [org.id for org in organizations]
        
        # Regular users can only access their own organization
        if user.organization_id:
            return [user.organization_id]
        
        return []
    
    @staticmethod
    def can_access_organization_settings(user: Union[User, UserInDB]) -> bool:
        """Check if user can access organization settings (hidden from App Super Admins)"""
        if not user or not user.role:
            return False
        
        # App Super Admins should NOT have access to organization settings per requirements
        if getattr(user, 'is_super_admin', False) or user.role.lower() == 'super_admin':
            return False
        
        # All other users (including org admins) can access org settings
        return PermissionChecker.has_permission(user, Permission.ACCESS_ORG_SETTINGS)  # Org admins have access to org settings
    
    @staticmethod
    def can_factory_reset(user: Union[User, UserInDB]) -> bool:
        """Check if user can perform factory reset (App Super Admin only)"""
        if not user or not user.role:
            return False
        
        # Only App Super Admins can perform factory reset
        return getattr(user, 'is_super_admin', False) or user.role.lower() == 'super_admin'
    
    @staticmethod
    def can_show_user_management_in_menu(user: Union[User, UserInDB]) -> bool:
        """Check if user management should be shown in mega menu (App Super Admin only)"""
        if not user or not user.role:
            return False
        
        # Only App Super Admins should see user management in mega menu
        # Org admins should access it through Organization Settings
        return getattr(user, 'is_super_admin', False) or user.role.lower() == 'super_admin'

    @staticmethod
    def can_edit_user(current_user: Union[User, UserInDB], target_user: Union[User, UserInDB]) -> bool:
        """Check if current user can edit target user based on hierarchy"""
        if not current_user or not target_user:
            return False
        
        # Super admins and org admins can edit anyone in their org
        if current_user.is_super_admin or current_user.role in ['super_admin', 'org_admin']:
            return current_user.organization_id == target_user.organization_id
        
        # Management can edit managers and executives
        if current_user.role == 'management':
            return target_user.role in ['manager', 'executive'] and current_user.organization_id == target_user.organization_id
        
        # Managers can edit their executives
        if current_user.role == 'manager' and target_user.role == 'executive':
            return target_user.reporting_manager_id == current_user.id
        
        # Users can only reset their own password
        return current_user.id == target_user.id
    
    @staticmethod
    def can_create_user(current_user: Union[User, UserInDB], new_user_role: str) -> bool:
        """Check if current user can create a user of specific role"""
        if current_user.is_super_admin or current_user.role == 'super_admin':
            return True
        
        if current_user.role == 'org_admin':
            # Org admin can create all org-level roles
            return new_user_role in ['org_admin', 'management', 'manager', 'executive']
        
        if current_user.role == 'manager':
            # Managers can only create executives under them
            return new_user_role == 'executive'
        
        return False


# FastAPI dependencies for permission checking
def require_organization_permission(permission: str):
    """FastAPI dependency to require organization-level permissions"""
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> User:
        if not PermissionChecker.has_permission(current_user, permission):
            # Log permission denied event
            if db and request:
                AuditLogger.log_permission_denied(
                    db=db,
                    user_email=current_user.email,
                    attempted_action=permission,
                    user_id=current_user.id,
                    user_role=current_user.role,
                    organization_id=current_user.organization_id,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    details={"required_permission": permission}
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user
    return dependency

def require_platform_permission(permission: str):
    """FastAPI dependency to require platform-level permissions"""
    def dependency(
        current_user: Union[User, PlatformUser] = Depends(get_current_user),
        db: Session = Depends(get_db),
        request: Request = None
    ) -> Union[User, PlatformUser]:
        if not PermissionChecker.has_platform_permission(current_user, permission):
            # Log permission denied event
            if db and request:
                AuditLogger.log_permission_denied(
                    db=db,
                    user_email=getattr(current_user, 'email', 'unknown'),
                    attempted_action=permission,
                    user_id=getattr(current_user, 'id', None),
                    user_role=getattr(current_user, 'role', 'unknown'),
                    organization_id=getattr(current_user, 'organization_id', None),
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    details={"required_permission": permission}
                )
            
            # Create more descriptive error message based on permission
            permission_messages = {
                Permission.MANAGE_ORGANIZATIONS: "manage organizations",
                Permission.VIEW_ORGANIZATIONS: "view organizations",
                Permission.CREATE_ORGANIZATIONS: "create organizations",
                Permission.DELETE_ORGANIZATIONS: "delete organizations",
            }
            action = permission_messages.get(permission, permission.replace('_', ' '))
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions to {action}. This action requires platform administrator access. "
                       f"Please contact your system administrator to request '{permission}' permission or upgrade to platform administrator role."
            )
        return current_user
    return dependency

def require_super_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
) -> User:
    """FastAPI dependency to require super admin access"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    PermissionChecker.require_permission(
        Permission.SUPER_ADMIN,
        current_user,
        db,
        request
    )
    return current_user


def require_org_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
) -> User:
    """FastAPI dependency to require org admin access"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not PermissionChecker.has_permission(current_user, Permission.RESET_ORG_PASSWORDS):
        PermissionChecker.require_permission(
            Permission.SUPER_ADMIN,
            current_user,
            db,
            request
        )
    
    return current_user


def require_password_reset_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
) -> User:
    """FastAPI dependency to require password reset permissions"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Check if any password reset permission
    if not (
        PermissionChecker.has_permission(current_user, Permission.RESET_ORG_PASSWORDS) or
        PermissionChecker.has_permission(current_user, Permission.RESET_ANY_PASSWORD)
    ):
        PermissionChecker.require_permission(
            Permission.RESET_ORG_PASSWORDS,
            current_user,
            db,
            request
        )
    
    return current_user


def require_data_reset_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
) -> User:
    """FastAPI dependency to require data reset permissions"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Check if any data reset permission
    if not (
        PermissionChecker.has_permission(current_user, Permission.RESET_ORG_DATA) or
        PermissionChecker.has_permission(current_user, Permission.RESET_ANY_DATA)
    ):
        PermissionChecker.require_permission(
            Permission.RESET_ORG_DATA,
            current_user,
            db,
            request
        )
    
    return current_user
