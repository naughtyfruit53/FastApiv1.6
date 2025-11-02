# app/core/modules_registry.py
"""
Comprehensive Module and Submodule Registry for RBAC System
Defines all modules, submodules, and their hierarchical structure
"""

from typing import Dict, List
from enum import Enum


class ModuleName(str, Enum):
    """All available modules in the system"""
    # Core Business Modules
    CRM = "crm"
    ERP = "erp"
    HR = "hr"
    INVENTORY = "inventory"
    SERVICE = "service"
    ANALYTICS = "analytics"
    FINANCE = "finance"
    
    # Extended Modules
    MANUFACTURING = "manufacturing"
    PROCUREMENT = "procurement"
    PROJECT = "project"
    ASSET = "asset"
    TRANSPORT = "transport"
    SEO = "seo"
    MARKETING = "marketing"
    PAYROLL = "payroll"
    TALENT = "talent"
    
    # Advanced Modules
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
    
    # New from menuConfig - to match frontend
    MASTER_DATA = "master_data"
    VOUCHERS = "vouchers"
    ACCOUNTING = "accounting"
    REPORTS_ANALYTICS = "reports_analytics"
    SALES = "sales"
    PROJECTS = "projects"
    HR_MANAGEMENT = "hr_management"
    TASKS_CALENDAR = "tasks_calendar"
    
    # Additional modules for menu items
    SETTINGS = "settings"
    ADMIN = "admin"
    ORGANIZATION = "organization"


# Submodule definitions for each module (expanded to match menuConfig.tsx)
MODULE_SUBMODULES: Dict[str, List[str]] = {
    # CRM Module
    ModuleName.CRM.value: [
        "leads",
        "opportunities",
        "contacts",
        "accounts",
        "activities",
        "campaigns",
        "commission",
        "analytics",
        "settings",
        "import_export",
    ],
    
    # ERP Module
    ModuleName.ERP.value: [
        "general_ledger",
        "accounts_payable",
        "accounts_receivable",
        "journal_entries",
        "bank_reconciliation",
        "cost_centers",
        "chart_of_accounts",
        "gst_configuration",
        "tax_codes",
        "financial_statements",
        "kpis",
    ],
    
    # HR Module
    ModuleName.HR.value: [
        "employees",
        "attendance",
        "leave_management",
        "performance",
        "recruitment",
        "training",
        "documents",
        "org_structure",
    ],
    
    # Inventory Module
    ModuleName.INVENTORY.value: [
        "products",
        "stock",
        "warehouses",
        "stock_transfers",
        "stock_adjustments",
        "stock_reports",
        "categories",
        "units",
        "brands",
    ],
    
    # Service Module
    ModuleName.SERVICE.value: [
        "service_requests",
        "technicians",
        "appointments",
        "work_orders",
        "service_reports",
        "customer_feedback",
        "service_closure",
        "sla_management",
        "service_analytics",
    ],
    
    # Analytics Module
    ModuleName.ANALYTICS.value: [
        "dashboards",
        "reports",
        "custom_reports",
        "data_visualization",
        "kpi_tracking",
        "forecasting",
        "export",
    ],
    
    # Finance Module
    ModuleName.FINANCE.value: [
        "vouchers",
        "purchase_vouchers",
        "sales_vouchers",
        "payment_vouchers",
        "receipt_vouchers",
        "journal_vouchers",
        "contra_vouchers",
        "financial_modeling",
        "budgeting",
    ],
    
    # Manufacturing Module
    ModuleName.MANUFACTURING.value: [
        "production_planning",
        "work_orders",
        "bom",
        "quality_control",
        "job_work",
        "material_requisition",
        "production_reports",
        "capacity_planning",
        "shop_floor",
    ],
    
    # Procurement Module
    ModuleName.PROCUREMENT.value: [
        "purchase_orders",
        "purchase_requisitions",
        "rfq",
        "vendor_quotations",
        "vendor_evaluation",
        "grn",
        "purchase_returns",
        "vendor_management",
    ],
    
    # Project Module
    ModuleName.PROJECT.value: [
        "projects",
        "tasks",
        "milestones",
        "time_tracking",
        "resource_allocation",
        "project_reports",
        "gantt_charts",
        "collaboration",
    ],
    
    # Asset Module
    ModuleName.ASSET.value: [
        "asset_register",
        "asset_tracking",
        "depreciation",
        "maintenance",
        "allocation",
        "disposal",
        "asset_reports",
    ],
    
    # Transport Module
    ModuleName.TRANSPORT.value: [
        "vehicles",
        "drivers",
        "routes",
        "trips",
        "fuel_management",
        "maintenance",
        "gps_tracking",
        "transport_reports",
    ],
    
    # SEO Module
    ModuleName.SEO.value: [
        "keywords",
        "content_optimization",
        "backlinks",
        "site_audit",
        "rank_tracking",
        "competitor_analysis",
        "seo_reports",
    ],
    
    # Marketing Module
    ModuleName.MARKETING.value: [
        "campaigns",
        "email_marketing",
        "social_media",
        "content_marketing",
        "marketing_automation",
        "lead_generation",
        "analytics",
        "roi_tracking",
    ],
    
    # Payroll Module
    ModuleName.PAYROLL.value: [
        "salary_structure",
        "payslips",
        "deductions",
        "bonuses",
        "tax_calculation",
        "statutory_compliance",
        "payroll_reports",
        "bank_transfer",
    ],
    
    # Talent Module
    ModuleName.TALENT.value: [
        "recruitment",
        "candidate_tracking",
        "interviews",
        "offer_management",
        "onboarding",
        "talent_pool",
        "recruitment_analytics",
    ],
    
    # Workflow Module
    ModuleName.WORKFLOW.value: [
        "templates",
        "approval_requests",
        "instances",
        "automation_rules",
        "analytics",
    ],
    
    # Integration Module
    ModuleName.INTEGRATION.value: [
        "api_keys",
        "webhooks",
        "external",
        "data_sync",
        "tally_sync",
        "oauth_clients",
        "logs",
    ],
    
    # AI Analytics Module
    ModuleName.AI_ANALYTICS.value: [
        "ml_models",
        "predictions",
        "anomaly_detection",
        "recommendations",
        "automl",
        "explainability",
        "reports",
    ],
    
    # Email Module
    ModuleName.EMAIL.value: [
        "inbox",
        "compose",
        "templates",
        "accounts",
        "sync",
        "filters",
        "analytics",
    ],
    
    # Calendar Module
    ModuleName.CALENDAR.value: [
        "events",
        "meetings",
        "reminders",
        "sharing",
        "event_types",
    ],
    
    # Task Management Module
    ModuleName.TASK_MANAGEMENT.value: [
        "tasks",
        "projects",
        "boards",
        "sprints",
        "time_logs",
        "reports",
    ],
    
    # Order Book Module
    ModuleName.ORDER_BOOK.value: [
        "sales_orders",
        "purchase_orders",
        "tracking",
        "fulfillment",
        "analytics",
    ],
    
    # Exhibition Module
    ModuleName.EXHIBITION.value: [
        "events",
        "booths",
        "attendees",
        "leads",
        "analytics",
    ],
    
    # Settings Module (added)
    ModuleName.SETTINGS.value: [
        "general",
        "company",
        "voucher",
        "role_management",
        "service",
        "audit_logs",
        "notification",
        "user_management",
        "system_reports",
        "migration",
        "ui_testing",
        "notification_demo",
        "transport",
        "assets",
        "bank_accounts",
    ],
    
    # Admin Module (added)
    ModuleName.ADMIN.value: [
        "dashboard",
        "user_management",
        "role_management",
        "audit_logs",
        "system_settings",
        "notifications",
        "license_management",
        "organizations",
        "app_statistics",
    ],
    
    # Organization Module (added for dashboard)
    ModuleName.ORGANIZATION.value: [
        "dashboard",
        "settings",
        "users",
        "statistics",
        "activities",
        "reports",
    ],
}


# Permission actions available across modules
class PermissionAction(str, Enum):
    """Granular permission actions"""
    # Basic CRUD
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # Advanced actions
    APPROVE = "approve"
    REJECT = "reject"
    SUBMIT = "submit"
    REVIEW = "review"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    
    # Data operations
    EXPORT = "export"
    IMPORT = "import"
    SYNC = "sync"
    BACKUP = "backup"
    RESTORE = "restore"
    
    # Special permissions
    ADMIN = "admin"
    MANAGE = "manage"
    VIEW_ALL = "view_all"
    EDIT_ALL = "edit_all"
    
    # Communication
    SEND = "send"
    COMPOSE = "compose"
    REPLY = "reply"
    FORWARD = "forward"
    
    # Conversion and transformation
    CONVERT = "convert"
    TRANSFORM = "transform"
    
    # Closure and finalization
    CLOSE = "close"
    FINALIZE = "finalize"
    REOPEN = "reopen"
    
    # Assignment
    ASSIGN = "assign"
    REASSIGN = "reassign"


def get_all_modules() -> List[str]:
    """Get list of all available modules"""
    return [module.value for module in ModuleName]


def get_module_submodules(module: str) -> List[str]:
    """Get submodules for a specific module"""
    return MODULE_SUBMODULES.get(module, [])


def get_default_enabled_modules() -> Dict[str, bool]:
    """Get default enabled modules for new organizations"""
    return {module.upper(): True for module in get_all_modules()}


def validate_module(module: str) -> bool:
    """Validate if a module exists"""
    return module in get_all_modules()


def validate_submodule(module: str, submodule: str) -> bool:
    """Validate if a submodule exists for a module"""
    return submodule in get_module_submodules(module)


def get_module_hierarchy() -> Dict[str, Dict[str, List[str]]]:
    """Get complete module hierarchy"""
    return {
        "modules": {
            module: {
                "submodules": MODULE_SUBMODULES.get(module, [])
            }
            for module in get_all_modules()
        }
    }