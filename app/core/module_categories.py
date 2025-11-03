# app/core/module_categories.py

"""
Module Categories Configuration
Maps product categories to their constituent modules for category-based entitlement activation
"""

from typing import Dict, List
from enum import Enum


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
    ASSET_TRANSPORT = "asset_transport_suite"
    WORKFLOW = "workflow_suite"
    INTEGRATION = "integration_suite"
    COMMUNICATION = "communication_suite"
    ADDITIONAL = "additional_features"


# Category to module mapping
CATEGORY_MODULE_MAP: Dict[str, List[str]] = {
    ProductCategory.CRM: [
        "crm",
        "sales",
        "marketing",
        "seo"
    ],
    
    ProductCategory.ERP: [
        "erp",
        "inventory",
        "procurement",
        "order_book",
        "master_data",
        "product",
        "vouchers"
    ],
    
    ProductCategory.MANUFACTURING: [
        "manufacturing",
        "bom"
    ],
    
    ProductCategory.FINANCE: [
        "finance",
        "accounting",
        "reports_analytics",
        "payroll"
    ],
    
    ProductCategory.SERVICE: [
        "service"
    ],
    
    ProductCategory.HR: [
        "hr",
        "hr_management",
        "talent"
    ],
    
    ProductCategory.ANALYTICS: [
        "analytics",
        "streaming_analytics",
        "ab_testing"
    ],
    
    ProductCategory.AI: [
        "ai_analytics",
        "website_agent"
    ],
    
    ProductCategory.PROJECT_MANAGEMENT: [
        "project",
        "projects",
        "task_management",
        "tasks_calendar"
    ],
    
    ProductCategory.ASSET_TRANSPORT: [
        "asset",
        "transport"
    ],
    
    ProductCategory.WORKFLOW: [
        "workflow"
    ],
    
    ProductCategory.INTEGRATION: [
        "integration"
    ],
    
    ProductCategory.COMMUNICATION: [
        "email",
        "calendar"
    ],
    
    ProductCategory.ADDITIONAL: [
        "exhibition",
        "customer",
        "vendor",
        "voucher",
        "stock"
    ]
}


# Reverse mapping: module to category
MODULE_CATEGORY_MAP: Dict[str, str] = {}
for category, modules in CATEGORY_MODULE_MAP.items():
    for module in modules:
        MODULE_CATEGORY_MAP[module] = category


# Category display names
CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    ProductCategory.CRM: "CRM Suite",
    ProductCategory.ERP: "ERP Suite",
    ProductCategory.MANUFACTURING: "Manufacturing Suite",
    ProductCategory.FINANCE: "Finance & Accounting Suite",
    ProductCategory.SERVICE: "Service Management Suite",
    ProductCategory.HR: "Human Resources Suite",
    ProductCategory.ANALYTICS: "Analytics & BI Suite",
    ProductCategory.AI: "AI & Machine Learning Suite",
    ProductCategory.PROJECT_MANAGEMENT: "Project Management Suite",
    ProductCategory.ASSET_TRANSPORT: "Asset & Transport Management Suite",
    ProductCategory.WORKFLOW: "Workflow & Automation Suite",
    ProductCategory.INTEGRATION: "Integration Platform",
    ProductCategory.COMMUNICATION: "Communication & Collaboration",
    ProductCategory.ADDITIONAL: "Additional Features"
}


# Category descriptions
CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    ProductCategory.CRM: "Complete customer relationship management, sales, and marketing tools",
    ProductCategory.ERP: "Core business operations including inventory, procurement, and order management",
    ProductCategory.MANUFACTURING: "Production planning, shop floor management, and quality control",
    ProductCategory.FINANCE: "Comprehensive financial management, accounting, and payroll processing",
    ProductCategory.SERVICE: "Service desk, ticket management, and customer support operations",
    ProductCategory.HR: "Human resource management, recruitment, and talent acquisition",
    ProductCategory.ANALYTICS: "Business intelligence, reporting, and analytics capabilities",
    ProductCategory.AI: "Artificial intelligence, machine learning, and predictive analytics",
    ProductCategory.PROJECT_MANAGEMENT: "Project planning, task management, and collaboration tools",
    ProductCategory.ASSET_TRANSPORT: "Asset lifecycle and transportation fleet management",
    ProductCategory.WORKFLOW: "Business process automation and workflow management",
    ProductCategory.INTEGRATION: "Third-party integrations, APIs, and data synchronization",
    ProductCategory.COMMUNICATION: "Email, calendar, and collaboration tools",
    ProductCategory.ADDITIONAL: "Specialized business features and emerging capabilities"
}


# Always-on modules (not controlled by entitlements)
ALWAYS_ON_MODULES = ["email"]

# RBAC-only modules (not controlled by entitlements, only by role permissions)
RBAC_ONLY_MODULES = ["settings", "admin", "organization"]


def get_modules_for_category(category: str) -> List[str]:
    """Get all modules for a given category"""
    return CATEGORY_MODULE_MAP.get(category, [])


def get_category_for_module(module: str) -> str:
    """Get the category for a given module"""
    return MODULE_CATEGORY_MAP.get(module)


def get_all_categories() -> List[str]:
    """Get all product categories"""
    return [category.value for category in ProductCategory]


def get_category_info(category: str) -> Dict[str, any]:
    """Get complete information about a category"""
    return {
        "key": category,
        "display_name": CATEGORY_DISPLAY_NAMES.get(category, category),
        "description": CATEGORY_DESCRIPTIONS.get(category, ""),
        "modules": get_modules_for_category(category),
        "module_count": len(get_modules_for_category(category))
    }


def is_always_on_module(module: str) -> bool:
    """Check if a module is always-on"""
    return module in ALWAYS_ON_MODULES


def is_rbac_only_module(module: str) -> bool:
    """Check if a module is RBAC-only"""
    return module in RBAC_ONLY_MODULES


def get_all_category_info() -> List[Dict[str, any]]:
    """Get information about all categories"""
    return [get_category_info(category) for category in get_all_categories()]
