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
    """Permission constants"""
    
    # User management permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    DELETE_USERS = "delete_users"
    
    # Password management permissions
    RESET_OWN_PASSWORD = "reset_own_password"
    RESET_ORG_PASSWORDS = "reset_org_passwords"
    RESET_ANY_PASSWORD = "reset_any_password"
    
    # Data management permissions
    RESET_OWN_DATA = "reset_own_data"
    RESET_ORG_DATA = "reset_org_data"
    RESET_ANY_DATA = "reset_any_data"
    
    # Organization management permissions
    MANAGE_ORGANIZATIONS = "manage_organizations"
    VIEW_ORGANIZATIONS = "view_organizations"
    CREATE_ORGANIZATIONS = "create_organizations"
    DELETE_ORGANIZATIONS = "delete_organizations"
    
    # Platform administration permissions
    PLATFORM_ADMIN = "platform_admin"
    SUPER_ADMIN = "super_admin"
    
    # Audit permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    VIEW_ALL_AUDIT_LOGS = "view_all_audit_logs"
    
    # Factory reset permission (App Super Admin only)
    FACTORY_RESET = "factory_reset"
    
    # Organization settings access
    ACCESS_ORG_SETTINGS = "access_org_settings"
    
    # Service CRM Module Permissions - CRUD operations per module
    # Service Management Permissions
    SERVICE_CREATE = "service_create"
    SERVICE_READ = "service_read"
    SERVICE_UPDATE = "service_update"
    SERVICE_DELETE = "service_delete"
    
    # Technician Management Permissions
    TECHNICIAN_CREATE = "technician_create"
    TECHNICIAN_READ = "technician_read"
    TECHNICIAN_UPDATE = "technician_update"
    TECHNICIAN_DELETE = "technician_delete"
    
    # Appointment Management Permissions
    APPOINTMENT_CREATE = "appointment_create"
    APPOINTMENT_READ = "appointment_read"
    APPOINTMENT_UPDATE = "appointment_update"
    APPOINTMENT_DELETE = "appointment_delete"
    
    # Customer Service Permissions
    CUSTOMER_SERVICE_CREATE = "customer_service_create"
    CUSTOMER_SERVICE_READ = "customer_service_read"
    CUSTOMER_SERVICE_UPDATE = "customer_service_update"
    CUSTOMER_SERVICE_DELETE = "customer_service_delete"
    
    # Work Order Permissions
    WORK_ORDER_CREATE = "work_order_create"
    WORK_ORDER_READ = "work_order_read"
    WORK_ORDER_UPDATE = "work_order_update"
    WORK_ORDER_DELETE = "work_order_delete"
    
    # Service Reports Permissions
    SERVICE_REPORTS_READ = "service_reports_read"
    SERVICE_REPORTS_EXPORT = "service_reports_export"
    
    # CRM Admin Permissions
    CRM_ADMIN = "crm_admin"
    CRM_SETTINGS = "crm_settings"
    
    # Voucher management permissions
    VIEW_VOUCHERS = "view_vouchers"
    MANAGE_VOUCHERS = "manage_vouchers"
    
    # Commission Permissions
    CRM_COMMISSION_READ = "crm_commission_read"
    CRM_COMMISSION_CREATE = "crm_commission_create"
    CRM_COMMISSION_UPDATE = "crm_commission_update"
    CRM_COMMISSION_DELETE = "crm_commission_delete"

    # NEW: Inventory permissions
    INVENTORY_READ = "inventory.read"
    INVENTORY_WRITE = "inventory.write"
    INVENTORY_UPDATE = "inventory.update"
    INVENTORY_DELETE = "inventory.delete"

    # NEW: Products permissions
    PRODUCTS_READ = "products.read"
    PRODUCTS_WRITE = "products.write"
    PRODUCTS_UPDATE = "products.update"
    PRODUCTS_DELETE = "products.delete"

    # NEW: Master Data permissions
    MASTER_DATA_READ = "master_data.read"
    MASTER_DATA_WRITE = "master_data.write"
    MASTER_DATA_UPDATE = "master_data.update"
    MASTER_DATA_DELETE = "master_data.delete"

    # NEW: Manufacturing permissions
    MANUFACTURING_READ = "manufacturing.read"
    MANUFACTURING_WRITE = "manufacturing.write"
    MANUFACTURING_UPDATE = "manufacturing.update"
    MANUFACTURING_DELETE = "manufacturing.delete"

    # NEW: Vendors permissions (specific for ERP master data)
    VENDORS_READ = "vendors.read"
    VENDORS_CREATE = "vendors.create"
    VENDORS_UPDATE = "vendors.update"
    VENDORS_DELETE = "vendors.delete"

    # NEW: Voucher permissions (specific for ERP vouchers)
    VOUCHER_READ = "voucher.read"
    VOUCHER_CREATE = "voucher.create"
    VOUCHER_UPDATE = "voucher.update"
    VOUCHER_DELETE = "voucher.delete"


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
    def has_permission(user: Union[User, UserInDB], permission: str) -> bool:
        role = user.role.lower() if hasattr(user, 'role') else None
        is_super_admin = getattr(user, 'is_super_admin', False)
        if is_super_admin or role == 'super_admin':
            return True
        
        user_permissions = PermissionChecker.ROLE_PERMISSIONS.get(role, [])
        return permission in user_permissions
    
    @staticmethod
    def has_platform_permission(platform_user: Union[User, PlatformUser, UserInDB, PlatformUserInDB], permission: str) -> bool:
        """Check platform-specific permissions, handling both ORM and Pydantic models"""
        # Extract attributes consistently for both ORM and Pydantic
        role = platform_user.role.lower() if hasattr(platform_user, 'role') else ''
        is_super_admin = getattr(platform_user, 'is_super_admin', False)
        user_id = getattr(platform_user, 'id', 'None')
        email = getattr(platform_user, 'email', 'None')
        organization_id = getattr(platform_user, 'organization_id', 'None')
        
        logger.info(f"Permission check for {permission}: id={user_id}, email={email}, role={role}, is_super_admin={is_super_admin}, organization_id={organization_id}")

        # Use attribute check instead of type name for robustness
        if hasattr(platform_user, 'organization_id') and platform_user.organization_id is not None:
            # Organization user (User or UserInDB)
            if is_super_admin or role == 'super_admin':
                logger.info("Permission granted: Organization user is super admin")
                return True
            # Fallback to regular permission check
            granted = PermissionChecker.has_permission(platform_user, permission)
            logger.info(f"Regular permission check result: {granted}")
            return granted
        
        else:
            # Platform user (PlatformUser or PlatformUserInDB)
            if role == 'super_admin':
                logger.info("Permission granted: Platform user is super admin")
                return True
            platform_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get(role, [])
            granted = permission in platform_permissions
            logger.info(f"Platform permission check result: {granted}, permissions: {platform_permissions}")
            return granted
    
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
