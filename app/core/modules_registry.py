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

    # Added to match route usage from logs (to fix "not found" errors)
    CUSTOMER = "customer"
    PRODUCT = "product"
    VENDOR = "vendor"
    VOUCHER = "voucher"
    STOCK = "stock"
    BOM = "bom"


# Submodule definitions for each module (expanded to match menuConfig.tsx)
MODULE_SUBMODULES: Dict[str, List[str]] = {
    # CRM Module
    ModuleName.CRM.value: [
        "keywords",
        "contacts",
        "leads",
        "opportunities",
        "customers",
        "accounts",
        "pipeline",
        "reports",
        "analytics"
    ],
    'ERP': [
        "inventory",
        "products",
        "stock",
        "warehouse",
        "procurement",
        "dispatch",
        "tasks_calendar",
        "appointments",
        "meeting_rooms",
        "event_reminders",
        "recurring_events",
        "vendors",  # Added to fix "Submodule 'vendors' not found in module 'erp'"
        "customers"  # Added for consistency with vendors
    ],
    'MANUFACTURING': [
        "bom",
        "mrp",
        "production_planning",
        "job_cards",
        "material_issue",
        "material_receipt",
        "shop_floor",
        "quality",
        "reports"
    ],
    'FINANCE': [
        "salary_structure",
        "salary_components",
        "payslips",
        "deductions",
        "bonuses",
        "tax_calculation",
        "statutory_compliance",
        "payroll_reports",
        "bank_transfer"
    ],
    'SERVICE': [
        "tickets",
        "sla",
        "service_desk",
        "technicians",
        "feedback",
        "dispatch",
        "service_analytics"
    ],
    'HR': [
        "salary",
        "salary_structure",
        "payslips",
        "deductions",
        "bonuses",
        "tax_calculation",
        "statutory_compliance",
        "payroll_reports",
        "bank_transfer"
    ],
    'ANALYTICS': [
        "customer",
        "sales",
        "purchase",
        "service",
        "financial",
        "ab_testing",
        "streaming_dashboard"
    ],
    # Add new modules for missing ones
    'INVENTORY': [  # Make inventory a top-level module
        "stock",
        "locations",
        "bins",
        "movements",
        "cycle_count",
        "low_stock",
        "pending_orders"
    ],
    'PRODUCT': [  # Add product as top-level module
        "categories",
        "units",
        "details",
        "pricing",
        "images"
    ],
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
    ModuleName.ASSET.value: [
        "asset_register",
        "asset_tracking",
        "depreciation",
        "maintenance",
        "allocation",
        "disposal",
        "asset_reports",
    ],
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
    ModuleName.SEO.value: [
        "keywords",
        "content_optimization",
        "backlinks",
        "site_audit",
        "rank_tracking",
        "competitor_analysis",
        "seo_reports",
    ],
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
    ModuleName.PAYROLL.value: [
        "salary_structure",
        "salary_components",
        "payslips",
        "deductions",
        "bonuses",
        "tax_calculation",
        "statutory_compliance",
        "payroll_reports",
        "bank_transfer"
    ],
    ModuleName.TALENT.value: [
        "recruitment",
        "candidate_tracking",
        "interviews",
        "offer_management",
        "onboarding",
        "talent_pool",
        "recruitment_analytics",
    ],
    ModuleName.WORKFLOW.value: [
        "templates",
        "approval_requests",
        "instances",
        "automation_rules",
        "analytics",
    ],
    ModuleName.INTEGRATION.value: [
        "api_keys",
        "webhooks",
        "external",
        "data_sync",
        "tally_sync",
        "oauth_clients",
        "logs",
    ],
    ModuleName.AI_ANALYTICS.value: [
        "ml_models",
        "predictions",
        "anomaly_detection",
        "recommendations",
        "automl",
        "explainability",
        "reports",
    ],
    ModuleName.EMAIL.value: [
        "inbox",
        "compose",
        "templates",
        "accounts",
        "sync",
        "filters",
        "analytics",
    ],
    ModuleName.CALENDAR.value: [
        "events",
        "meetings",
        "reminders",
        "sharing",
        "event_types",
    ],
    ModuleName.TASK_MANAGEMENT.value: [
        "tasks",
        "projects",
        "boards",
        "sprints",
        "time_logs",
        "reports",
    ],
    ModuleName.ORDER_BOOK.value: [
        "sales_orders",
        "purchase_orders",
        "tracking",
        "fulfillment",
        "analytics",
    ],
    ModuleName.EXHIBITION.value: [
        "events",
        "booths",
        "attendees",
        "leads",
        "analytics",
    ],
    
    # Master Data Module
    ModuleName.MASTER_DATA.value: [
        "customers",
        "vendors",
        "products",
        "bom",
        "employees",
        "chart_of_accounts",
        "expense_accounts",
        "payment_terms",
        "tax_codes",
        "units",
        "company_details",
        "multi_company",
    ],
    
    # Vouchers Module
    ModuleName.VOUCHERS.value: [
        "sales_vouchers",
        "purchase_vouchers",
        "payment_vouchers",
        "receipt_vouchers",
        "journal_vouchers",
        "contra_vouchers",
        "debit_note",
        "credit_note",
        "delivery_challan",
        "goods_receipt_note",
        "quotation",
        "proforma_invoice",
        "purchase_order",
        "sales_order",
        "purchase_return",
        "sales_return",
        "inter_department_voucher",
    ],
    
    # Accounting Module
    ModuleName.ACCOUNTING.value: [
        "ledger",
        "trial_balance",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "customer_aging",
        "vendor_aging",
    ],
    
    # Reports Analytics Module
    ModuleName.REPORTS_ANALYTICS.value: [
        "balance_sheet",
        "cash_flow",
        "ledgers",
        "profit_loss",
        "trial_balance",
    ],
    
    # Sales Module
    ModuleName.SALES.value: [
        "customers",
        "leads",
        "opportunities",
        "contacts",
        "commissions",
        "pipeline",
        "reports",
        "customer_analytics",
        "dashboard",
        "accounts",
    ],
    
    # Projects Module
    ModuleName.PROJECTS.value: [
        "planning",
        "documents",
        "resources",
        "analytics",
    ],
    
    # HR Management Module
    ModuleName.HR_MANAGEMENT.value: [
        "employees_directory",
        "employees",
        "dashboard",
    ],
    
    # Tasks Calendar Module
    ModuleName.TASKS_CALENDAR.value: [
        "dashboard",
        "create",
        "assignments",
        "events",
    ],
    
    # Settings Module
    ModuleName.SETTINGS.value: [
        "general_settings",
        "company",
        "user_management",
        "voucher_settings",
        "data_management",
        "factory_reset",
    ],
    
    # Admin Module
    ModuleName.ADMIN.value: [
        "app_user_management",
        "audit_logs",
        "notifications",
        "license_management",
        "manage_organizations",
    ],
    
    # Organization Module
    ModuleName.ORGANIZATION.value: [
        "create",
        "users",
    ],

    # Added empty submodules for new modules to fix "not found" errors
    ModuleName.CUSTOMER.value: [],
    ModuleName.PRODUCT.value: [],
    ModuleName.VENDOR.value: [],
    ModuleName.VOUCHER.value: [],
    ModuleName.STOCK.value: [],
    ModuleName.BOM.value: [],
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