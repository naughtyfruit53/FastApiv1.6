# app/services/rbac_permissions.py
"""
Comprehensive Permission Definitions for RBAC System
Defines all default permissions for modules and submodules
"""

from typing import List, Tuple, Dict  # ADDED Dict
from app.core.modules_registry import get_all_modules, get_module_submodules
from app.schemas.rbac import ServiceModule as Module, ServiceAction as Action

def get_comprehensive_permissions() -> List[Tuple[str, str, str, str, str]]:
    """
    Generate comprehensive list of permissions
    Returns list of (name, display_name, description, module, action)
    """
    permissions = []
    
    # Add core permissions for all modules and submodules
    basic_actions = [
        ("create", "Create"),
        ("read", "Read"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),  # Added view action for menu visibility
    ]
    
    for module in get_all_modules():
        # Module-level permissions
        for action_key, action_name in basic_actions:
            name = f"{module.lower()}_{action_key}"
            display_name = f"{action_name} {module.capitalize()}"
            description = f"{action_name} access in {module.capitalize()} module"
            permissions.append((name, display_name, description, module.lower(), action_key))
        
        # Submodule permissions
        submodules = get_module_submodules(module)
        for sub in submodules:
            for action_key, action_name in basic_actions:
                name = f"{module.lower()}_{sub}_{action_key}"
                display_name = f"{action_name} {sub.capitalize()} in {module.capitalize()}"
                description = f"{action_name} access to {sub.capitalize()} in {module.capitalize()}"
                permissions.append((name, display_name, description, f"{module.lower()}_{sub}", action_key))
    
    # Add specific permissions not covered by the loop
    # Settings module
    permissions.append((
        "settings_view",
        "View Settings",
        "View organization settings",
        "settings",
        "view"
    ))
    permissions.append((
        "settings_update",
        "Update Settings",
        "Update organization settings",
        "settings",
        "update"
    ))
    
    # Admin module
    permissions.append((
        "admin_view",
        "View Admin Panel",
        "Access to admin dashboard",
        "admin",
        "view"
    ))
    permissions.append((
        "admin_manage",
        "Manage Admin",
        "Full admin management access",
        "admin",
        "manage"
    ))
    
    # Email module
    permissions.append((
        "email_view",
        "View Email",
        "Access to email inbox and views",
        "email",
        "view"
    ))
    permissions.append((
        "email_compose",
        "Compose Email",
        "Create and send emails",
        "email",
        "create"
    ))
    
    # Add more specific permissions as needed from menu requirements
    permissions.append((
        "crm_admin",
        "CRM Admin Access",
        "Administrative access to CRM module",
        "crm",
        "admin"
    ))
    
    return permissions


def get_default_role_permissions() -> dict[str, list[str]]:  # CHANGED Dict[str, List[str]] to dict[str, list[str]]
    """
    Get default permissions for each role
    Returns dict of role_name -> list of permission names
    """
    all_permissions = [p[0] for p in get_comprehensive_permissions()]
    
    return {
        "admin": all_permissions,  # Full access
        "manager": [
            p for p in all_permissions 
            if not p.startswith("admin_") 
            and not p.startswith("settings_") 
            and "delete" not in p  # No delete for managers
        ],
        "support": [
            p for p in all_permissions 
            if any(keyword in p for keyword in ["read", "create", "update", "view"])
            and not any(keyword in p for keyword in ["delete", "admin"])
        ],
        "viewer": [
            p for p in all_permissions 
            if "read" in p or "view" in p
        ]
    }