# app/schemas/rbac.py

"""
RBAC schemas for Service CRM role-based access control
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ServiceRoleType(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"
    VIEWER = "viewer"


class ServiceModule(str, Enum):
    # Legacy service-specific modules (keep for backward compatibility)
    SERVICE = "service"
    TECHNICIAN = "technician"
    APPOINTMENT = "appointment"
    CUSTOMER_SERVICE = "customer_service"
    WORK_ORDER = "work_order"
    SERVICE_REPORTS = "service_reports"
    CRM_ADMIN = "crm_admin"
    CUSTOMER_FEEDBACK = "customer_feedback"
    SERVICE_CLOSURE = "service_closure"
    MAIL = "mail"
    CRM_LEAD = "crm_lead"
    CRM_OPPORTUNITY = "crm_opportunity"
    CRM_ACTIVITY = "crm_activity"
    CRM_ANALYTICS = "crm_analytics"
    CRM_SETTINGS = "crm_settings"
    CRM = "crm"
    CRM_COMMISSION = "crm_commission"
    
    # Comprehensive module structure - Submodules
    # CRM Submodules
    CRM_LEADS = "crm_leads"
    CRM_OPPORTUNITIES = "crm_opportunities"
    CRM_CONTACTS = "crm_contacts"
    CRM_ACCOUNTS = "crm_accounts"
    CRM_ACTIVITIES = "crm_activities"
    CRM_CAMPAIGNS = "crm_campaigns"
    CRM_IMPORT_EXPORT = "crm_import_export"
    
    # ERP Submodules
    ERP_GENERAL_LEDGER = "erp_general_ledger"
    ERP_ACCOUNTS_PAYABLE = "erp_accounts_payable"
    ERP_ACCOUNTS_RECEIVABLE = "erp_accounts_receivable"
    ERP_JOURNAL_ENTRIES = "erp_journal_entries"
    ERP_BANK_RECONCILIATION = "erp_bank_reconciliation"
    ERP_COST_CENTERS = "erp_cost_centers"
    ERP_CHART_OF_ACCOUNTS = "erp_chart_of_accounts"
    ERP_GST_CONFIGURATION = "erp_gst_configuration"
    ERP_TAX_CODES = "erp_tax_codes"
    ERP_FINANCIAL_STATEMENTS = "erp_financial_statements"
    ERP_KPIS = "erp_kpis"
    
    # HR Submodules
    HR_EMPLOYEES = "hr_employees"
    HR_ATTENDANCE = "hr_attendance"
    HR_LEAVE_MANAGEMENT = "hr_leave_management"
    HR_PERFORMANCE = "hr_performance"
    HR_RECRUITMENT = "hr_recruitment"
    HR_TRAINING = "hr_training"
    HR_DOCUMENTS = "hr_documents"
    HR_ORG_STRUCTURE = "hr_org_structure"
    
    # Inventory Submodules
    INVENTORY_PRODUCTS = "inventory_products"
    INVENTORY_STOCK = "inventory_stock"
    INVENTORY_WAREHOUSES = "inventory_warehouses"
    INVENTORY_STOCK_TRANSFERS = "inventory_stock_transfers"
    INVENTORY_STOCK_ADJUSTMENTS = "inventory_stock_adjustments"
    INVENTORY_STOCK_REPORTS = "inventory_stock_reports"
    INVENTORY_CATEGORIES = "inventory_categories"
    INVENTORY_UNITS = "inventory_units"
    INVENTORY_BRANDS = "inventory_brands"
    
    # Service Submodules
    SERVICE_REQUESTS = "service_requests"
    SERVICE_TECHNICIANS = "service_technicians"
    SERVICE_APPOINTMENTS = "service_appointments"
    SERVICE_WORK_ORDERS = "service_work_orders"
    SERVICE_SERVICE_REPORTS = "service_reports"
    SERVICE_CUSTOMER_FEEDBACK = "service_customer_feedback"
    SERVICE_SLA_MANAGEMENT = "service_sla_management"
    SERVICE_ANALYTICS = "service_analytics"
    
    # Analytics Submodules
    ANALYTICS_DASHBOARDS = "analytics_dashboards"
    ANALYTICS_REPORTS = "analytics_reports"
    ANALYTICS_CUSTOM_REPORTS = "analytics_custom_reports"
    ANALYTICS_DATA_VISUALIZATION = "analytics_data_visualization"
    ANALYTICS_KPI_TRACKING = "analytics_kpi_tracking"
    ANALYTICS_FORECASTING = "analytics_forecasting"
    ANALYTICS_EXPORT = "analytics_export"
    
    # Finance Submodules
    FINANCE_VOUCHERS = "finance_vouchers"
    FINANCE_PURCHASE_VOUCHERS = "finance_purchase_vouchers"
    FINANCE_SALES_VOUCHERS = "finance_sales_vouchers"
    FINANCE_PAYMENT_VOUCHERS = "finance_payment_vouchers"
    FINANCE_RECEIPT_VOUCHERS = "finance_receipt_vouchers"
    FINANCE_JOURNAL_VOUCHERS = "finance_journal_vouchers"
    FINANCE_CONTRA_VOUCHERS = "finance_contra_vouchers"
    FINANCE_FINANCIAL_MODELING = "finance_financial_modeling"
    FINANCE_BUDGETING = "finance_budgeting"
    
    # Manufacturing Submodules
    MANUFACTURING_PRODUCTION_PLANNING = "manufacturing_production_planning"
    MANUFACTURING_WORK_ORDERS = "manufacturing_work_orders"
    MANUFACTURING_BOM = "manufacturing_bom"
    MANUFACTURING_QUALITY_CONTROL = "manufacturing_quality_control"
    MANUFACTURING_JOB_WORK = "manufacturing_job_work"
    MANUFACTURING_MATERIAL_REQUISITION = "manufacturing_material_requisition"
    MANUFACTURING_PRODUCTION_REPORTS = "manufacturing_production_reports"
    MANUFACTURING_CAPACITY_PLANNING = "manufacturing_capacity_planning"
    MANUFACTURING_SHOP_FLOOR = "manufacturing_shop_floor"
    
    # Procurement Submodules
    PROCUREMENT_PURCHASE_ORDERS = "procurement_purchase_orders"
    PROCUREMENT_PURCHASE_REQUISITIONS = "procurement_purchase_requisitions"
    PROCUREMENT_RFQ = "procurement_rfq"
    PROCUREMENT_VENDOR_QUOTATIONS = "procurement_vendor_quotations"
    PROCUREMENT_VENDOR_EVALUATION = "procurement_vendor_evaluation"
    PROCUREMENT_GRN = "procurement_grn"
    PROCUREMENT_PURCHASE_RETURNS = "procurement_purchase_returns"
    PROCUREMENT_VENDOR_MANAGEMENT = "procurement_vendor_management"
    
    # Project Submodules
    PROJECT_PROJECTS = "project_projects"
    PROJECT_TASKS = "project_tasks"
    PROJECT_MILESTONES = "project_milestones"
    PROJECT_TIME_TRACKING = "project_time_tracking"
    PROJECT_RESOURCE_ALLOCATION = "project_resource_allocation"
    PROJECT_PROJECT_REPORTS = "project_project_reports"
    PROJECT_GANTT_CHARTS = "project_gantt_charts"
    PROJECT_COLLABORATION = "project_collaboration"
    
    # Asset Submodules
    ASSET_REGISTER = "asset_register"
    ASSET_TRACKING = "asset_tracking"
    ASSET_DEPRECIATION = "asset_depreciation"
    ASSET_MAINTENANCE = "asset_maintenance"
    ASSET_ALLOCATION = "asset_allocation"
    ASSET_DISPOSAL = "asset_disposal"
    ASSET_REPORTS = "asset_reports"
    
    # Transport Submodules
    TRANSPORT_VEHICLES = "transport_vehicles"
    TRANSPORT_DRIVERS = "transport_drivers"
    TRANSPORT_ROUTES = "transport_routes"
    TRANSPORT_TRIPS = "transport_trips"
    TRANSPORT_FUEL_MANAGEMENT = "transport_fuel_management"
    TRANSPORT_MAINTENANCE = "transport_maintenance"
    TRANSPORT_GPS_TRACKING = "transport_gps_tracking"
    TRANSPORT_REPORTS = "transport_reports"
    
    # SEO Submodules
    SEO_KEYWORDS = "seo_keywords"
    SEO_CONTENT_OPTIMIZATION = "seo_content_optimization"
    SEO_BACKLINKS = "seo_backlinks"
    SEO_SITE_AUDIT = "seo_site_audit"
    SEO_RANK_TRACKING = "seo_rank_tracking"
    SEO_COMPETITOR_ANALYSIS = "seo_competitor_analysis"
    SEO_REPORTS = "seo_reports"
    
    # Marketing Submodules
    MARKETING_CAMPAIGNS = "marketing_campaigns"
    MARKETING_EMAIL_MARKETING = "marketing_email_marketing"
    MARKETING_SOCIAL_MEDIA = "marketing_social_media"
    MARKETING_CONTENT_MARKETING = "marketing_content_marketing"
    MARKETING_AUTOMATION = "marketing_automation"
    MARKETING_LEAD_GENERATION = "marketing_lead_generation"
    MARKETING_ANALYTICS = "marketing_analytics"
    MARKETING_ROI_TRACKING = "marketing_roi_tracking"
    
    # Payroll Submodules
    PAYROLL_SALARY_STRUCTURE = "payroll_salary_structure"
    PAYROLL_PAYSLIPS = "payroll_payslips"
    PAYROLL_DEDUCTIONS = "payroll_deductions"
    PAYROLL_BONUSES = "payroll_bonuses"
    PAYROLL_TAX_CALCULATION = "payroll_tax_calculation"
    PAYROLL_STATUTORY_COMPLIANCE = "payroll_statutory_compliance"
    PAYROLL_REPORTS = "payroll_reports"
    PAYROLL_BANK_TRANSFER = "payroll_bank_transfer"
    
    # Talent Submodules
    TALENT_RECRUITMENT = "talent_recruitment"
    TALENT_CANDIDATE_TRACKING = "talent_candidate_tracking"
    TALENT_INTERVIEWS = "talent_interviews"
    TALENT_OFFER_MANAGEMENT = "talent_offer_management"
    TALENT_ONBOARDING = "talent_onboarding"
    TALENT_TALENT_POOL = "talent_talent_pool"
    TALENT_RECRUITMENT_ANALYTICS = "talent_recruitment_analytics"
    
    # Workflow Submodules
    WORKFLOW_TEMPLATES = "workflow_templates"
    WORKFLOW_APPROVAL_REQUESTS = "workflow_approval_requests"
    WORKFLOW_INSTANCES = "workflow_instances"
    WORKFLOW_AUTOMATION_RULES = "workflow_automation_rules"
    WORKFLOW_ANALYTICS = "workflow_analytics"
    
    # Integration Submodules
    INTEGRATION_API_KEYS = "integration_api_keys"
    INTEGRATION_WEBHOOKS = "integration_webhooks"
    INTEGRATION_EXTERNAL = "integration_external"
    INTEGRATION_DATA_SYNC = "integration_data_sync"
    INTEGRATION_TALLY_SYNC = "integration_tally_sync"
    INTEGRATION_OAUTH_CLIENTS = "integration_oauth_clients"
    INTEGRATION_LOGS = "integration_logs"
    
    # AI Analytics Submodules
    AI_ANALYTICS_ML_MODELS = "ai_analytics_ml_models"
    AI_ANALYTICS_PREDICTIONS = "ai_analytics_predictions"
    AI_ANALYTICS_ANOMALY_DETECTION = "ai_analytics_anomaly_detection"
    AI_ANALYTICS_RECOMMENDATIONS = "ai_analytics_recommendations"
    AI_ANALYTICS_AUTOML = "ai_analytics_automl"
    AI_ANALYTICS_EXPLAINABILITY = "ai_analytics_explainability"
    AI_ANALYTICS_REPORTS = "ai_analytics_reports"
    
    # Email Submodules
    EMAIL_INBOX = "email_inbox"
    EMAIL_COMPOSE = "email_compose"
    EMAIL_TEMPLATES = "email_templates"
    EMAIL_ACCOUNTS = "email_accounts"
    EMAIL_SYNC = "email_sync"
    EMAIL_FILTERS = "email_filters"
    EMAIL_ANALYTICS = "email_analytics"
    
    # Calendar Submodules
    CALENDAR_EVENTS = "calendar_events"
    CALENDAR_MEETINGS = "calendar_meetings"
    CALENDAR_REMINDERS = "calendar_reminders"
    CALENDAR_SHARING = "calendar_sharing"
    CALENDAR_EVENT_TYPES = "calendar_event_types"
    
    # Task Management Submodules
    TASK_TASKS = "task_tasks"
    TASK_PROJECTS = "task_projects"
    TASK_BOARDS = "task_boards"
    TASK_SPRINTS = "task_sprints"
    TASK_TIME_LOGS = "task_time_logs"
    TASK_REPORTS = "task_reports"
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid module"""
        try:
            cls(value)
            return True
        except ValueError:
            return False


class ServiceAction(str, Enum):
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
    
    # View action for menu visibility
    VIEW = "view"  # Added for view-specific permissions


# Service Permission Schemas
class ServicePermissionBase(BaseModel):
    name: str = Field(..., description="Permission name (e.g., service_create)")
    display_name: str = Field(..., description="Human-readable permission name")
    description: Optional[str] = Field(None, description="Permission description")
    module: ServiceModule = Field(..., description="Module this permission applies to")
    action: ServiceAction = Field(..., description="Action this permission allows")
    is_active: bool = Field(True, description="Whether permission is active")
    
    model_config = ConfigDict(use_enum_values=False)  # Keep enum objects, not just values


class ServicePermissionCreate(ServicePermissionBase):
    pass


class ServicePermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServicePermissionInDB(ServicePermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Service Role Schemas
class ServiceRoleBase(BaseModel):
    name: ServiceRoleType = Field(..., description="Role name")
    display_name: str = Field(..., description="Human-readable role name")
    description: Optional[str] = Field(None, description="Role description")
    is_active: bool = Field(True, description="Whether role is active")


class ServiceRoleCreate(ServiceRoleBase):
    organization_id: int = Field(..., description="Organization ID", gt=0)
    permission_ids: List[int] = Field(default_factory=list, description="List of permission IDs to assign")


class ServiceRoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class ServiceRoleInDB(ServiceRoleBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ServiceRoleWithPermissions(ServiceRoleInDB):
    permissions: List[ServicePermissionInDB] = Field(default_factory=list)


# User Service Role Assignment Schemas
class UserServiceRoleBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Service role ID")
    is_active: bool = Field(True, description="Whether assignment is active")


class UserServiceRoleCreate(UserServiceRoleBase):
    assigned_by_id: Optional[int] = Field(None, description="User ID who made the assignment")


class UserServiceRoleUpdate(BaseModel):
    is_active: Optional[bool] = None


class UserServiceRoleInDB(UserServiceRoleBase):
    id: int
    assigned_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# User with Service Roles
class UserWithServiceRoles(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str  # Regular user role
    is_active: bool
    service_roles: List[ServiceRoleInDB] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# Service Role Assignment Request
class RoleAssignmentRequest(BaseModel):
    user_id: int = Field(..., description="User ID to assign role to")
    role_ids: List[int] = Field(..., description="List of service role IDs to assign")


class RoleAssignmentResponse(BaseModel):
    success: bool
    message: str
    assignments: List[UserServiceRoleInDB] = Field(default_factory=list)


# Permission Check Schemas
class PermissionCheckRequest(BaseModel):
    user_id: int = Field(..., description="User ID to check")
    permission: str = Field(..., description="Permission to check")
    organization_id: Optional[int] = Field(None, description="Organization context")


class PermissionCheckResponse(BaseModel):
    has_permission: bool
    user_id: int
    permission: str
    source: str = Field(..., description="Source of permission (role_name or 'system')")


# Bulk Operations
class BulkRoleAssignmentRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs")
    role_ids: List[int] = Field(..., description="List of role IDs to assign")
    replace_existing: bool = Field(False, description="Whether to replace existing role assignments")


class BulkRoleAssignmentResponse(BaseModel):
    success: bool
    message: str
    successful_assignments: int
    failed_assignments: int
    details: List[str] = Field(default_factory=list)