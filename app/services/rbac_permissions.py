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
    
    # Legacy/Backward Compatible Permissions (standardized to dot notation)
    legacy_permissions = [
        ("service.create", "Create Services", "Create new services", "service", "create"),
        ("service.read", "View Services", "View service information", "service", "read"),
        ("service.update", "Update Services", "Modify service information", "service", "update"),
        ("service.delete", "Delete Services", "Delete services", "service", "delete"),
        ("technician.create", "Create Technicians", "Add new technicians", "technician", "create"),
        ("technician.read", "View Technicians", "View technician information", "technician", "read"),
        ("technician.update", "Update Technicians", "Modify technician information", "technician", "update"),
        ("technician.delete", "Delete Technicians", "Remove technicians", "technician", "delete"),
        ("appointment.create", "Create Appointments", "Schedule new appointments", "appointment", "create"),
        ("appointment.read", "View Appointments", "View appointment information", "appointment", "read"),
        ("appointment.update", "Update Appointments", "Modify appointments", "appointment", "update"),
        ("appointment.delete", "Cancel Appointments", "Cancel appointments", "appointment", "delete"),
        ("customer_service.create", "Create Customer Records", "Create customer service records", "customer_service", "create"),
        ("customer_service.read", "View Customer Records", "View customer service information", "customer_service", "read"),
        ("customer_service.update", "Update Customer Records", "Modify customer service records", "customer_service", "update"),
        ("customer_service.delete", "Delete Customer Records", "Remove customer service records", "customer_service", "delete"),
        ("work_order.create", "Create Work Orders", "Create new work orders", "work_order", "create"),
        ("work_order.read", "View Work Orders", "View work order information", "work_order", "read"),
        ("work_order.update", "Update Work Orders", "Modify work orders", "work_order", "update"),
        ("work_order.delete", "Delete Work Orders", "Remove work orders", "work_order", "delete"),
        ("service_reports.read", "View Service Reports", "Access service reports", "service_reports", "read"),
        ("service_reports.export", "Export Service Reports", "Export service reports", "service_reports", "export"),
        ("crm.admin", "CRM Administration", "Full CRM administration access", "crm_admin", "admin"),
        ("crm.settings", "CRM Settings", "Manage CRM settings", "crm_admin", "update"),
        ("mail:dashboard.read", "Read Mail Dashboard", "View mail dashboard statistics", "mail_dashboard", "read"),
        ("mail:accounts.read", "Read Mail Accounts", "View email accounts", "mail_accounts", "read"),
        ("mail:accounts.create", "Create Mail Accounts", "Add new email accounts", "mail_accounts", "create"),
        ("mail:accounts.update", "Update Mail Accounts", "Modify email accounts", "mail_accounts", "update"),
        ("mail:accounts.delete", "Delete Mail Accounts", "Remove email accounts", "mail_accounts", "delete"),
        ("mail:emails.read", "Read Emails", "View emails", "mail_emails", "read"),
        ("mail:emails.compose", "Compose Emails", "Send new emails", "mail_emails", "create"),
        ("mail:emails.update", "Update Emails", "Modify emails", "mail_emails", "update"),
        ("mail:emails.sync", "Sync Emails", "Synchronize email accounts", "mail_emails", "update"),
        ("mail:templates.read", "Read Templates", "View email templates", "mail_templates", "read"),
        ("mail:templates.create", "Create Templates", "Add new email templates", "mail_templates", "create"),
        ("crm.lead.read", "Read Leads", "View leads", "crm_lead", "read"),
        ("crm.lead.create", "Create Leads", "Create new leads", "crm_lead", "create"),
        ("crm.lead.update", "Update Leads", "Modify leads", "crm_lead", "update"),
        ("crm.lead.delete", "Delete Leads", "Delete leads", "crm_lead", "delete"),
        ("crm.lead.convert", "Convert Leads", "Convert leads to opportunities/customers", "crm_lead", "convert"),
        ("crm.opportunity.read", "Read Opportunities", "View opportunities", "crm_opportunity", "read"),
        ("crm.opportunity.create", "Create Opportunities", "Create new opportunities", "crm_opportunity", "create"),
        ("crm.opportunity.update", "Update Opportunities", "Modify opportunities", "crm_opportunity", "update"),
        ("crm.opportunity.delete", "Delete Opportunities", "Delete opportunities", "crm_opportunity", "delete"),
        ("crm.activity.read", "Read Activities", "View activities", "crm_activity", "read"),
        ("crm.activity.create", "Create Activities", "Create new activities", "crm_activity", "create"),
        ("crm.activity.update", "Update Activities", "Modify activities", "crm_activity", "update"),
        ("crm.activity.delete", "Delete Activities", "Delete activities", "crm_activity", "delete"),
        ("crm.analytics.read", "Read Analytics", "View CRM analytics", "crm_analytics", "read"),
        ("crm.analytics.export", "Export Analytics", "Export CRM analytics", "crm_analytics", "export"),
        ("crm.settings.read", "Read Settings", "View CRM settings", "crm_settings", "read"),
        ("crm.settings.update", "Update Settings", "Modify CRM settings", "crm_settings", "update"),
        ("crm.import", "Import Data", "Import CRM data", "crm", "import"),
        ("crm.export", "Export Data", "Export CRM data", "crm", "export"),
        ("crm.commission.read", "Read Commissions", "View commissions", "crm_commission", "read"),
        ("crm.commission.create", "Create Commissions", "Create new commissions", "crm_commission", "create"),
        ("crm.commission.update", "Update Commissions", "Modify commissions", "crm_commission", "update"),
        ("crm.commission.delete", "Delete Commissions", "Delete commissions", "crm_commission", "delete"),
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
        "submit": "Submit",
        "review": "Review",
        "publish": "Publish",
        "archive": "Archive",
        "sync": "Sync",
        "backup": "Backup",
        "restore": "Restore",
        "admin": "Admin",
        "manage": "Manage",
        "view_all": "View All",
        "edit_all": "Edit All",
        "send": "Send",
        "compose": "Compose",
        "reply": "Reply",
        "forward": "Forward",
        "convert": "Convert",
        "transform": "Transform",
        "close": "Close",
        "finalize": "Finalize",
        "reopen": "Reopen",
        "assign": "Assign",
        "reassign": "Reassign",
    }
    
    # Generate module-level permissions first
    for module in ModuleName:
        module_key = module.value.lower().replace("_", ".")
        
        for action_key, action_name in basic_actions:
            perm_name = f"{module_key}.{action_key}"
            display_name = f"{action_name} {module.value.replace('_', ' ').title()}"
            description = f"{action_name} operations in {module.value.replace('_', ' ')} module"
            permissions.append((perm_name, display_name, description, module_key, action_key))
    
    # Generate submodule permissions
    for module_name, submodules in MODULE_SUBMODULES.items():
        module_key = module_name.lower().replace("_", ".")
        
        for submodule in submodules:
            submodule_key = submodule.lower().replace("_", ".")
            
            # CRUD permissions for each submodule
            for action_key, action_name in basic_actions:
                perm_name = f"{module_key}.{submodule_key}.{action_key}"
                display_name = f"{action_name} {submodule.replace('_', ' ').title()}"
                description = f"{action_name} {submodule.replace('_', ' ')} in {module_name}"
                permissions.append((perm_name, display_name, description, f"{module_key}.{submodule_key}", action_key))
            
            # Extended permissions for analytics, reports, and data operations
            if any(keyword in submodule for keyword in ["analytics", "reports", "import_export"]):
                for action_key, action_name in extended_actions.items():
                    if action_key in ["export", "import"]:
                        perm_name = f"{module_key}.{submodule_key}.{action_key}"
                        display_name = f"{action_name} {submodule.replace('_', ' ').title()}"
                        description = f"{action_name} data from {submodule.replace('_', ' ')} in {module_name}"
                        permissions.append((perm_name, display_name, description, f"{module_key}.{submodule_key}", action_key))
    
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
    module_key = module_name.lower().replace("_", ".")
    
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
    module_key = module_name.lower().replace("_", ".")
    submodule_key = submodule_name.lower().replace("_", ".")
    search_key = f"{module_key}.{submodule_key}"
    
    return [
        p for p in all_permissions 
        if p[3] == search_key
    ]