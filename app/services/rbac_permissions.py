# app/services/rbac_permissions.py
"""
Comprehensive RBAC Permissions Definition
Defines all permissions for all modules and submodules
"""

from typing import List, Tuple
from app.core.modules_registry import MODULE_SUBMODULES, ModuleName


def get_comprehensive_permissions() -> List[Tuple[str, str, str, str, str]]:
    """
    Get comprehensive list of all permissions across all modules
    Returns: List of tuples (permission_name, display_name, description, module, action)
    """
    permissions = []
    
    # Legacy/Backward Compatible Permissions
    legacy_permissions = [
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
        ("mail:dashboard:read", "Read Mail Dashboard", "View mail dashboard statistics", "mail_dashboard", "read"),
        ("mail:accounts:read", "Read Mail Accounts", "View email accounts", "mail_accounts", "read"),
        ("mail:accounts:create", "Create Mail Accounts", "Add new email accounts", "mail_accounts", "create"),
        ("mail:accounts:update", "Update Mail Accounts", "Modify email accounts", "mail_accounts", "update"),
        ("mail:accounts:delete", "Delete Mail Accounts", "Remove email accounts", "mail_accounts", "delete"),
        ("mail:emails:read", "Read Emails", "View emails", "mail_emails", "read"),
        ("mail:emails:compose", "Compose Emails", "Send new emails", "mail_emails", "create"),
        ("mail:emails:update", "Update Emails", "Modify emails", "mail_emails", "update"),
        ("mail:emails:sync", "Sync Emails", "Synchronize email accounts", "mail_emails", "update"),
        ("mail:templates:read", "Read Templates", "View email templates", "mail_templates", "read"),
        ("mail:templates:create", "Create Templates", "Add new email templates", "mail_templates", "create"),
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
    permissions.extend(legacy_permissions)
    
    # Comprehensive permissions for all modules and submodules
    # Define basic CRUD actions for all submodules
    basic_actions = [
        ("create", "Create"),
        ("read", "Read"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]
    
    # Define extended actions for specific submodules
    extended_actions = {
        "export": "Export",
        "import": "Import",
        "approve": "Approve",
        "reject": "Reject",
        "close": "Close",
        "sync": "Sync",
        "admin": "Admin",
    }
    
    # Generate permissions for each module and submodule
    for module_name, submodules in MODULE_SUBMODULES.items():
        module_key = module_name.lower().replace(" ", "_").replace("-", "_")
        
        for submodule in submodules:
            submodule_key = submodule.lower().replace(" ", "_").replace("-", "_")
            
            # CRUD permissions for each submodule
            for action_key, action_name in basic_actions:
                perm_name = f"{module_key}_{submodule_key}_{action_key}"
                display_name = f"{action_name} {submodule.replace('_', ' ').title()}"
                description = f"{action_name} {submodule.replace('_', ' ')} in {module_name}"
                permissions.append((perm_name, display_name, description, f"{module_key}_{submodule_key}", action_key))
            
            # Extended permissions for analytics, reports, and data operations
            if any(keyword in submodule for keyword in ["analytics", "reports", "import_export"]):
                for action_key, action_name in extended_actions.items():
                    if action_key in ["export", "import"]:
                        perm_name = f"{module_key}_{submodule_key}_{action_key}"
                        display_name = f"{action_name} {submodule.replace('_', ' ').title()}"
                        description = f"{action_name} data from {submodule.replace('_', ' ')} in {module_name}"
                        permissions.append((perm_name, display_name, description, f"{module_key}_{submodule_key}", action_key))
    
    return permissions


def get_default_role_permissions() -> dict:
    """
    Define default role permissions for comprehensive RBAC
    Returns: Dictionary mapping role types to their permissions
    """
    all_permissions = get_comprehensive_permissions()
    all_permission_names = [p[0] for p in all_permissions]
    
    # Admin gets all permissions
    admin_permissions = all_permission_names.copy()
    
    # Manager gets most permissions except delete and admin
    manager_permissions = [
        p[0] for p in all_permissions 
        if not any(keyword in p[0] for keyword in ["delete", "admin"]) 
        or "crm" in p[0] or "service" in p[0]  # Give full CRM and Service access to managers
    ]
    
    # Support/Executive gets read, create, update (no delete, admin)
    support_permissions = [
        p[0] for p in all_permissions 
        if any(keyword in p[0] for keyword in ["read", "create", "update", "view"])
        and not any(keyword in p[0] for keyword in ["delete", "admin"])
    ]
    
    # Viewer gets only read permissions
    viewer_permissions = [
        p[0] for p in all_permissions 
        if "read" in p[0] or "view" in p[0]
    ]
    
    return {
        "admin": admin_permissions,
        "manager": manager_permissions,
        "support": support_permissions,
        "viewer": viewer_permissions,
    }


def get_module_permissions(module_name: str) -> List[Tuple[str, str, str, str, str]]:
    """
    Get all permissions for a specific module
    Args:
        module_name: Name of the module (e.g., "CRM", "ERP")
    Returns: List of permission tuples for the module
    """
    all_permissions = get_comprehensive_permissions()
    module_key = module_name.lower().replace(" ", "_").replace("-", "_")
    
    return [
        p for p in all_permissions 
        if p[3].startswith(module_key)
    ]


def get_submodule_permissions(module_name: str, submodule_name: str) -> List[Tuple[str, str, str, str, str]]:
    """
    Get all permissions for a specific submodule
    Args:
        module_name: Name of the module (e.g., "CRM")
        submodule_name: Name of the submodule (e.g., "leads")
    Returns: List of permission tuples for the submodule
    """
    all_permissions = get_comprehensive_permissions()
    module_key = module_name.lower().replace(" ", "_").replace("-", "_")
    submodule_key = submodule_name.lower().replace(" ", "_").replace("-", "_")
    search_key = f"{module_key}_{submodule_key}"
    
    return [
        p for p in all_permissions 
        if p[3] == search_key
    ]