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
    CRM = "CRM"
    ERP = "ERP"
    HR = "HR"
    INVENTORY = "Inventory"
    SERVICE = "Service"
    ANALYTICS = "Analytics"
    FINANCE = "Finance"
    
    # Extended Modules
    MANUFACTURING = "Manufacturing"
    PROCUREMENT = "Procurement"
    PROJECT = "Project"
    ASSET = "Asset"
    TRANSPORT = "Transport"
    SEO = "SEO"
    MARKETING = "Marketing"
    PAYROLL = "Payroll"
    TALENT = "Talent"
    
    # Advanced Modules
    WORKFLOW = "Workflow"
    INTEGRATION = "Integration"
    AI_ANALYTICS = "AI_Analytics"
    STREAMING_ANALYTICS = "Streaming_Analytics"
    AB_TESTING = "AB_Testing"
    WEBSITE_AGENT = "Website_Agent"
    EMAIL = "Email"
    CALENDAR = "Calendar"
    TASK_MANAGEMENT = "Task_Management"
    ORDER_BOOK = "Order_Book"
    EXHIBITION = "Exhibition"
    
    # New from menuConfig - to match frontend
    MASTER_DATA = "Master_Data"
    VOUCHERS = "Vouchers"
    ACCOUNTING = "Accounting"
    REPORTS_ANALYTICS = "Reports_Analytics"
    SALES = "Sales"
    PROJECTS = "Projects"
    HR_MANAGEMENT = "HR_Management"
    TASKS_CALENDAR = "Tasks_Calendar"


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
        "workflow_templates",
        "approval_requests",
        "workflow_instances",
        "automation_rules",
        "workflow_analytics",
    ],
    
    # Integration Module
    ModuleName.INTEGRATION.value: [
        "api_keys",
        "webhooks",
        "external_integrations",
        "data_sync",
        "tally_sync",
        "oauth_clients",
        "integration_logs",
    ],
    
    # AI Analytics Module
    ModuleName.AI_ANALYTICS.value: [
        "ml_models",
        "predictions",
        "anomaly_detection",
        "recommendations",
        "automl",
        "model_explainability",
        "ai_reports",
    ],
    
    # Streaming Analytics Module
    ModuleName.STREAMING_ANALYTICS.value: [
        "real_time_dashboards",
        "event_streaming",
        "alerts",
        "monitoring",
        "streaming_reports",
    ],
    
    # AB Testing Module
    ModuleName.AB_TESTING.value: [
        "experiments",
        "variants",
        "metrics",
        "results_analysis",
        "ab_reports",
    ],
    
    # Website Agent Module
    ModuleName.WEBSITE_AGENT.value: [
        "chatbot_config",
        "conversations",
        "knowledge_base",
        "analytics",
        "customization",
    ],
    
    # Email Module
    ModuleName.EMAIL.value: [
        "inbox",
        "compose",
        "templates",
        "accounts",
        "sync",
        "filters",
        "email_analytics",
    ],
    
    # Calendar Module
    ModuleName.CALENDAR.value: [
        "events",
        "meetings",
        "reminders",
        "calendar_sharing",
        "event_types",
    ],
    
    # Task Management Module
    ModuleName.TASK_MANAGEMENT.value: [
        "tasks",
        "projects",
        "boards",
        "sprints",
        "time_logs",
        "task_reports",
    ],
    
    # Order Book Module
    ModuleName.ORDER_BOOK.value: [
        "sales_orders",
        "purchase_orders",
        "order_tracking",
        "fulfillment",
        "order_analytics",
    ],
    
    # Exhibition Module
    ModuleName.EXHIBITION.value: [
        "exhibitions",
        "booths",
        "attendees",
        "leads",
        "exhibition_analytics",
    ],
    
    # New from menuConfig
    ModuleName.MASTER_DATA.value: [
        "vendors",
        "customers",
        "employees",
        "company_details",
        "products",
        "categories",
        "units",
        "bom",
        "chart_of_accounts",
        "tax_codes",
        "payment_terms",
        "bank_account",
    ],
    ModuleName.VOUCHERS.value: [
        "purchase_order",
        "grn",
        "purchase_voucher",
        "purchase_return",
        "quotation",
        "proforma_invoice",
        "sales_order",
        "sales_voucher",
        "delivery_challan",
        "sales_return",
        "payment_voucher",
        "receipt_voucher",
        "journal_voucher",
        "contra_voucher",
        "credit_note",
        "debit_note",
        "non_sales_credit_note",
        "rfq",
        "dispatch_details",
        "inter_department_voucher",
    ],
    ModuleName.ACCOUNTING.value: [
        "chart_of_accounts",
        "account_groups",
        "opening_balances",
        "general_ledger",
        "journal_entries",
        "bank_reconciliation",
        "trial_balance",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
    ],
    ModuleName.REPORTS_ANALYTICS.value: [
        "ledgers",
        "trial_balance",
        "profit_loss",
        "balance_sheet",
        "stock_report",
        "valuation_report",
        "movement_report",
        "sales_analysis",
        "purchase_analysis",
        "vendor_analysis",
        "customer_analytics",
        "sales_analytics",
        "purchase_analytics",
        "project_analytics",
        "hr_analytics",
        "service_dashboard",
        "job_completion",
        "technician_performance",
        "customer_satisfaction",
        "sla_compliance",
    ],
    ModuleName.SALES.value: [
        "sales_dashboard",
        "lead_management",
        "opportunity_tracking",
        "sales_pipeline",
        "exhibition_mode",
        "customer_database",
        "contact_management",
        "account_management",
        "customer_analytics",
        "quotations",
        "sales_orders",
        "commission_tracking",
        "sales_reports",
    ],
    ModuleName.PROJECTS.value: [
        "all_projects",
        "project_planning",
        "resource_management",
        "document_management",
        "create_project",
        "project_analytics",
        "performance_reports",
        "resource_utilization",
        "budget_analysis",
        "team_dashboard",
        "time_tracking",
        "team_documents",
        "project_chat",
    ],
    ModuleName.HR_MANAGEMENT.value: [
        "employee_directory",
        "employee_records",
        "employee_onboarding",
        "performance_management",
        "employee_records_archive",
        "payroll_management",
        "salary_processing",
        "benefits_administration",
        "tax_management",
        "time_tracking",
        "leave_management",
        "attendance_reports",
        "shift_management",
        "job_postings",
        "candidate_management",
        "interview_scheduling",
        "hiring_pipeline",
        "hr_analytics_dashboard",
    ],
    ModuleName.TASKS_CALENDAR.value: [
        "task_dashboard",
        "my_tasks",
        "create_task",
        "task_assignment",
        "task_templates",
        "task_reminders",
        "task_comments",
        "calendar_dashboard",
        "calendar_view",
        "my_events",
        "create_event",
        "appointments",
        "meeting_rooms",
        "event_reminders",
        "recurring_events",
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
    return {module: True for module in get_all_modules()}


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