# app/core/constants.py

"""
Consolidated constants for tenant, entitlement, and RBAC system.
This file centralizes all constants used across the application for easier maintenance.
"""

from enum import Enum
from typing import Dict, List, Set

# ============================================================================
# TENANT CONSTANTS
# ============================================================================

class TenantHeaders:
    """HTTP headers for tenant identification"""
    ORGANIZATION_ID = "X-Organization-ID"
    USER_ID = "X-User-ID"


class TenantPaths:
    """URL path patterns for tenant identification"""
    ORG_PREFIX = "/api/v1/org"
    EXCLUDED_AUTH_PATHS = [
        "/api/v1/auth/",
        "/api/users/me",
    ]
    EXCLUDED_ORG_PATHS = [
        "/organizations/app-statistics",
        "/api/v1/organizations/app-statistics",
        "/organizations/org-statistics",
        "/api/v1/organizations/org-statistics",
        "/organizations/license/create",
        "/api/v1/organizations/license/create",
        "/organizations/factory-default",
        "/api/v1/organizations/factory-default",
        "/organizations/reset-data",
        "/api/v1/organizations/reset-data",
    ]


# ============================================================================
# ENTITLEMENT CONSTANTS
# ============================================================================

class ModuleStatusEnum(str, Enum):
    """Module entitlement status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    TRIAL = "trial"


class EntitlementSource(str, Enum):
    """Source of entitlement"""
    LICENSE = "license"
    ADMIN = "admin"
    DEFAULT = "default"
    SYSTEM = "system"


# Always-on modules (not controlled by entitlements)
ALWAYS_ON_MODULES: Set[str] = {"email", "dashboard"}

# RBAC-only modules (controlled by role permissions, not entitlements)
RBAC_ONLY_MODULES: Set[str] = {"settings", "admin", "organization", "user"}


# ============================================================================
# RBAC CONSTANTS
# ============================================================================

class UserRole(str, Enum):
    """User role types in the system"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGEMENT = "management"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    USER = "user"


class ServiceAction(str, Enum):
    """Standard CRUD actions for permissions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    MANAGE = "manage"


class PermissionScope(str, Enum):
    """Permission scope levels"""
    GLOBAL = "global"  # Super admin level
    ORG = "org"  # Organization level
    MODULE = "module"  # Module level
    SUBMODULE = "submodule"  # Submodule level
    RECORD = "record"  # Record/row level


# Default super admin permissions (bypass all checks)
SUPER_ADMIN_BYPASS_ROLES: Set[str] = {"super_admin"}

# Organization admin roles (full access to org resources)
ORG_ADMIN_ROLES: Set[str] = {"admin", "management"}

# Hierarchical role levels (higher number = more privileges)
ROLE_HIERARCHY: Dict[str, int] = {
    UserRole.SUPER_ADMIN: 100,
    UserRole.ADMIN: 80,
    UserRole.MANAGEMENT: 70,
    UserRole.MANAGER: 50,
    UserRole.EXECUTIVE: 30,
    UserRole.USER: 10,
}


# ============================================================================
# MODULE AND SUBMODULE CONSTANTS
# ============================================================================

class CoreModule(str, Enum):
    """Core business modules"""
    DASHBOARD = "dashboard"
    CRM = "crm"
    ERP = "erp"
    SALES = "sales"
    INVENTORY = "inventory"
    MANUFACTURING = "manufacturing"
    FINANCE = "finance"
    ACCOUNTING = "accounting"
    HR = "hr"
    SERVICE = "service"
    ANALYTICS = "analytics"
    REPORTS_ANALYTICS = "reports_analytics"


class ExtendedModule(str, Enum):
    """Extended modules"""
    MASTER_DATA = "master_data"
    VOUCHERS = "vouchers"
    PROCUREMENT = "procurement"
    PROJECT = "project"
    PROJECTS = "projects"
    ASSET = "asset"
    TRANSPORT = "transport"
    SEO = "seo"
    MARKETING = "marketing"
    PAYROLL = "payroll"
    TALENT = "talent"
    HR_MANAGEMENT = "hr_management"
    TASKS_CALENDAR = "tasks_calendar"


class AdvancedModule(str, Enum):
    """Advanced modules"""
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    AI_ANALYTICS = "ai_analytics"
    STREAMING_ANALYTICS = "streaming_analytics"
    AB_TESTING = "ab_testing"
    WEBSITE_AGENT = "website_agent"
    EMAIL = "email"
    CALENDAR = "calendar"
    TASK_MANAGEMENT = "task_management"
    ORDER_BOOK = "order_book"
    EXHIBITION = "exhibition"


class SystemModule(str, Enum):
    """System/admin modules"""
    SETTINGS = "settings"
    ADMIN = "admin"
    ORGANIZATION = "organization"
    USER = "user"


# Modules that require org_id in all queries
TENANT_AWARE_MODULES: Set[str] = {
    CoreModule.CRM,
    CoreModule.ERP,
    CoreModule.SALES,
    CoreModule.INVENTORY,
    CoreModule.MANUFACTURING,
    CoreModule.FINANCE,
    CoreModule.ACCOUNTING,
    CoreModule.HR,
    CoreModule.SERVICE,
    ExtendedModule.MASTER_DATA,
    ExtendedModule.VOUCHERS,
    ExtendedModule.PROCUREMENT,
    ExtendedModule.PROJECT,
    ExtendedModule.PROJECTS,
    ExtendedModule.ASSET,
    ExtendedModule.TRANSPORT,
    ExtendedModule.MARKETING,
    ExtendedModule.PAYROLL,
    ExtendedModule.TALENT,
}


# ============================================================================
# PRODUCT CATEGORY CONSTANTS
# ============================================================================

class ProductCategory(str, Enum):
    """Product categories for bundled entitlement activation"""
    CRM = "crm_suite"
    ERP = "erp_suite"
    MANUFACTURING = "manufacturing_suite"
    FINANCE = "finance_suite"
    SERVICE = "service_suite"
    HR = "hr_suite"
    ANALYTICS = "analytics_suite"
    AI = "ai_suite"
    PROJECT_MANAGEMENT = "project_management_suite"
    OPERATIONS_ASSETS = "operations_assets_suite"


# ============================================================================
# PERMISSION PATTERNS
# ============================================================================

# Common permission patterns for consistency
PERMISSION_PATTERNS = {
    "module_read": "{module}.read",
    "module_write": "{module}.write",
    "module_create": "{module}.create",
    "module_update": "{module}.update",
    "module_delete": "{module}.delete",
    "module_manage": "{module}.manage",
    "module_admin": "{module}_admin",
    "submodule_access": "{module}_{submodule}_access",
    "submodule_manage": "{module}_{submodule}_manage",
}


# ============================================================================
# ENFORCEMENT CONSTANTS
# ============================================================================

class EnforcementLevel(str, Enum):
    """3-Layer security enforcement levels"""
    TENANT = "tenant"  # Layer 1: Organization isolation
    ENTITLEMENT = "entitlement"  # Layer 2: Module/feature access
    RBAC = "rbac"  # Layer 3: User permissions


class EnforcementAction(str, Enum):
    """Actions during enforcement"""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"


# Error messages for enforcement failures
ENFORCEMENT_ERRORS = {
    "tenant_mismatch": "Access denied: Resource does not belong to your organization",
    "tenant_required": "Organization context is required for this operation",
    "entitlement_disabled": "Module '{module}' is not enabled for your organization",
    "entitlement_trial_expired": "Trial period for module '{module}' has expired",
    "rbac_permission_denied": "You do not have '{permission}' permission for this action",
    "rbac_role_insufficient": "Your role does not have sufficient privileges for this action",
    "invalid_org_id": "Invalid or missing organization identifier",
}


# ============================================================================
# AUDIT AND LOGGING CONSTANTS
# ============================================================================

class AuditEventType(str, Enum):
    """Audit event types for security logging"""
    TENANT_ACCESS = "tenant_access"
    TENANT_VIOLATION = "tenant_violation"
    ENTITLEMENT_CHECK = "entitlement_check"
    ENTITLEMENT_VIOLATION = "entitlement_violation"
    RBAC_CHECK = "rbac_check"
    RBAC_VIOLATION = "rbac_violation"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"
    ROLE_ASSIGNMENT = "role_assignment"
    ROLE_REMOVAL = "role_removal"


# Sensitive operations that require audit logging
AUDIT_REQUIRED_OPERATIONS: Set[str] = {
    "user_create",
    "user_delete",
    "role_assignment",
    "permission_grant",
    "entitlement_update",
    "organization_create",
    "organization_delete",
}


# ============================================================================
# CACHE CONSTANTS
# ============================================================================

class CacheKey:
    """Cache key patterns"""
    USER_PERMISSIONS = "user_permissions:{user_id}"
    USER_ROLES = "user_roles:{user_id}"
    ORG_ENTITLEMENTS = "org_entitlements:{org_id}"
    MODULE_STATUS = "module_status:{org_id}:{module}"


CACHE_TTL = {
    "user_permissions": 300,  # 5 minutes
    "user_roles": 300,  # 5 minutes
    "org_entitlements": 600,  # 10 minutes
    "module_status": 600,  # 10 minutes
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_super_admin_role(role: str) -> bool:
    """Check if role is super admin"""
    return role in SUPER_ADMIN_BYPASS_ROLES


def is_org_admin_role(role: str) -> bool:
    """Check if role is organization admin"""
    return role in ORG_ADMIN_ROLES


def is_rbac_only_module(module: str) -> bool:
    """Check if module is RBAC-only (not controlled by entitlements)"""
    return module.lower() in RBAC_ONLY_MODULES


def is_always_on_module(module: str) -> bool:
    """Check if module is always-on"""
    return module.lower() in ALWAYS_ON_MODULES


def get_role_level(role: str) -> int:
    """Get numeric level for role comparison"""
    return ROLE_HIERARCHY.get(role, 0)


def can_role_manage_role(manager_role: str, target_role: str) -> bool:
    """Check if manager_role can manage target_role"""
    return get_role_level(manager_role) > get_role_level(target_role)


def format_permission(pattern: str, **kwargs) -> str:
    """Format permission string from pattern"""
    return pattern.format(**kwargs)
