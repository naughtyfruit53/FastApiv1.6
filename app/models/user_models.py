# app/models/user_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
from typing import TYPE_CHECKING

# Import entitlement models to resolve relationships (moved outside TYPE_CHECKING for runtime)
from app.models.entitlement_models import OrgEntitlement, OrgSubentitlement, EntitlementEvent

# Platform User Model - For SaaS platform-level users (kept here, removed from base.py)
class PlatformUser(Base):
    __tablename__ = "platform_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User credentials
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # User details
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="super_admin") # super_admin, platform_admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Temporary master password support
    temp_password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Temporary password hash
    temp_password_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # Expiry for temp password
    force_password_reset: Mapped[bool] = mapped_column(Boolean, default=False) # Force password reset on next login

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_platform_user_email', 'email'),
        Index('idx_platform_user_active', 'is_active'),
        {'extend_existing': True}
    )

# Organization/Tenant Model - Core of Multi-tenancy (kept here, removed from base.py)
class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    subdomain: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True) # For subdomain-based tenancy
    status: Mapped[str] = mapped_column(String, nullable=False, default="active") # active, suspended, trial

    # Business details
    business_type: Mapped[Optional[str]] = mapped_column(String, nullable=True) # manufacturing, trading, service, etc.
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Contact information
    primary_email: Mapped[str] = mapped_column(String, nullable=False)
    primary_phone: Mapped[str] = mapped_column(String, nullable=False)

    # Address
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False, default="India")
    state_code: Mapped[str] = mapped_column(String, nullable=False)  # Required for GST calculation

    # Legal details
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Corporate Identification Number

    # Subscription details
    plan_type: Mapped[str] = mapped_column(String, default="trial") # trial, basic, premium, enterprise
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_companies: Mapped[int] = mapped_column(Integer, default=1) # Maximum companies allowed for this organization
    storage_limit_gb: Mapped[int] = mapped_column(Integer, default=1)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Feature flags
    
    # License management
    license_type: Mapped[str] = mapped_column(String, default="trial") # trial, month, year, perpetual
    license_issued_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    license_expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    license_duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # null for perpetual

    # Settings
    timezone: Mapped[str] = mapped_column(String, default="Asia/Kolkata")
    currency: Mapped[str] = mapped_column(String, default="INR")
    date_format: Mapped[str] = mapped_column(String, default="DD/MM/YYYY")
    financial_year_start: Mapped[str] = mapped_column(String, default="04/01") # April 1st

    # Module Access Control - Organization level module enable/disable
    enabled_modules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        # Core Business Modules
        "CRM": True,
        "ERP": True, 
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True,
        
        # Extended Modules
        "Manufacturing": True,
        "Procurement": True,
        "Project": True,
        "Asset": True,
        "Transport": True,
        "SEO": True,
        "Marketing": True,
        "Payroll": True,
        "Talent": True,
        
        # Advanced Modules
        "Workflow": True,
        "Integration": True,
        "AI_Analytics": True,
        "Streaming_Analytics": True,
        "AB_Testing": True,
        "Website_Agent": True,
        "Email": True,
        "Calendar": True,
        "Task_Management": True,
        "Order_Book": True,
        "Exhibition": True,
    }) # Modules enabled for this organization

    # Onboarding status
    company_details_completed: Mapped[bool] = mapped_column(Boolean, default=False) # Track if company details have been filled

    # Custom org code
    org_code: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True, index=True, default=None) # Custom format: yy/mm-(total user)-tqnnnn

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with forward refs (class names only)
    users: Mapped[List["User"]] = relationship(
        "User", 
        back_populates="organization"
    )
    companies: Mapped[List["Company"]] = relationship(
        "Company", 
        back_populates="organization"
    )
    vendors: Mapped[List["Vendor"]] = relationship(
        "Vendor", 
        back_populates="organization"
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", 
        back_populates="organization"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product", 
        back_populates="organization"
    )
    stock_entries: Mapped[List["Stock"]] = relationship(
        "Stock", 
        back_populates="organization"
    )
    
    # ERP Core relationships
    chart_of_accounts: Mapped[List["ChartOfAccounts"]] = relationship(
        "ChartOfAccounts",
        back_populates="organization"
    )
    gst_configuration: Mapped[List["GSTConfiguration"]] = relationship(
        "GSTConfiguration",
        back_populates="organization"
    )
    erp_tax_codes: Mapped[List["ERPTaxCode"]] = relationship(
        "ERPTaxCode",
        back_populates="organization"
    )
    
    # Project Management relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="organization"
    )
    
    # Workflow relationships
    workflow_templates: Mapped[List["WorkflowTemplate"]] = relationship(
        "WorkflowTemplate",
        back_populates="organization"
    )
    approval_requests: Mapped[List["ApprovalRequest"]] = relationship(
        "ApprovalRequest",
        back_populates="organization"
    )
    
    # API Gateway relationships
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey",
        back_populates="organization"
    )
    webhooks: Mapped[List["Webhook"]] = relationship(
        "Webhook",
        back_populates="organization"
    )
    
    # Integration relationships
    external_integrations: Mapped[List["ExternalIntegration"]] = relationship(
        "ExternalIntegration",
        back_populates="organization"
    )
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="organization"
    )
    accounts_payable: Mapped[List["AccountsPayable"]] = relationship(
        "AccountsPayable",
        back_populates="organization"
    )
    accounts_receivable: Mapped[List["AccountsReceivable"]] = relationship(
        "AccountsReceivable",
        back_populates="organization"
    )
    payment_records: Mapped[List["PaymentRecord"]] = relationship(
        "PaymentRecord",
        back_populates="organization"
    )
    general_ledger: Mapped[List["GeneralLedger"]] = relationship(
        "GeneralLedger",
        back_populates="organization"
    )
    cost_centers: Mapped[List["CostCenter"]] = relationship(
        "CostCenter",
        back_populates="organization"
    )
    bank_accounts: Mapped[List["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="organization"
    )
    bank_reconciliations: Mapped[List["BankReconciliation"]] = relationship(
        "BankReconciliation",
        back_populates="organization"
    )
    financial_statements: Mapped[List["FinancialStatement"]] = relationship(
        "FinancialStatement",
        back_populates="organization"
    )
    financial_kpis: Mapped[List["FinancialKPI"]] = relationship(
        "FinancialKPI",
        back_populates="organization"
    )
    
    # Procurement relationships
    rfqs: Mapped[List["RequestForQuotation"]] = relationship(
        "RequestForQuotation",
        back_populates="organization"
    )
    vendor_quotations: Mapped[List["VendorQuotation"]] = relationship(
        "VendorQuotation",
        back_populates="organization"
    )
    vendor_evaluations: Mapped[List["VendorEvaluation"]] = relationship(
        "VendorEvaluation",
        back_populates="organization"
    )
    purchase_requisitions: Mapped[List["PurchaseRequisition"]] = relationship(
        "PurchaseRequisition",
        back_populates="organization"
    )
    
    # Master Data relationships
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="organization"
    )
    units: Mapped[List["Unit"]] = relationship(
        "Unit",
        back_populates="organization"
    )
    tax_codes: Mapped[List["TaxCode"]] = relationship(
        "TaxCode",
        back_populates="organization"
    )
    payment_terms_extended: Mapped[List["PaymentTermsExtended"]] = relationship(
        "PaymentTermsExtended",
        back_populates="organization"
    )
    
    # Advanced Workflow Automation relationships
    business_rules: Mapped[List["BusinessRule"]] = relationship(
        "BusinessRule",
        back_populates="organization"
    )
    workflow_templates_advanced: Mapped[List["WorkflowTemplateAdvanced"]] = relationship(
        "WorkflowTemplateAdvanced",
        back_populates="organization"
    )
    workflow_instances: Mapped[List["AutomationWorkflowInstance"]] = relationship(
        "AutomationWorkflowInstance",
        back_populates="organization"
    )
    workflow_schedules: Mapped[List["WorkflowSchedule"]] = relationship(
        "WorkflowSchedule",
        back_populates="organization"
    )
    
    # Tally integration relationships
    tally_configuration: Mapped[List["TallyConfiguration"]] = relationship(
        "TallyConfiguration",
        back_populates="organization"
    )
    tally_data_cache: Mapped[List["TallyDataCache"]] = relationship(
        "TallyDataCache",
        back_populates="organization"
    )
    tally_error_logs: Mapped[List["TallyErrorLog"]] = relationship(
        "TallyErrorLog",
        back_populates="organization"
    )
    
    # Migration relationships
    migration_jobs: Mapped[List["MigrationJob"]] = relationship(
        "MigrationJob",
        back_populates="organization"
    )
    
    # Enhanced inventory relationships
    warehouses: Mapped[List["Warehouse"]] = relationship(
        "Warehouse",
        back_populates="organization"
    )
    warehouse_stock: Mapped[List["WarehouseStock"]] = relationship(
        "WarehouseStock",
        back_populates="organization"
    )
    product_batches: Mapped[List["ProductBatch"]] = relationship(
        "ProductBatch",
        back_populates="organization"
    )
    product_serials: Mapped[List["ProductSerial"]] = relationship(
        "ProductSerial",
        back_populates="organization"
    )
    stock_movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="organization"
    )
    stock_adjustments: Mapped[List["StockAdjustment"]] = relationship(
        "StockAdjustment",
        back_populates="organization"
    )
    
    # Exhibition mode relationships
    exhibition_events: Mapped[List["ExhibitionEvent"]] = relationship(
        "ExhibitionEvent",
        back_populates="organization"
    )
    
    # Task Management Relationships
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="organization"
    )
    task_projects: Mapped[List["TaskProject"]] = relationship(
        "TaskProject",
        back_populates="organization"
    )
    
    # Calendar Management Relationships
    calendar_events: Mapped[List["CalendarEvent"]] = relationship(
        "CalendarEvent",
        back_populates="organization"
    )
    calendars: Mapped[List["Calendar"]] = relationship(
        "Calendar",
        back_populates="organization"
    )
    google_calendar_integrations: Mapped[List["GoogleCalendarIntegration"]] = relationship(
        "GoogleCalendarIntegration",
        back_populates="organization"
    )
    
    # OAuth2 Email Token relationships
    email_tokens: Mapped[List["UserEmailToken"]] = relationship(
        "UserEmailToken",
        back_populates="organization"
    )
    
    # New organization role assignments
    organization_roles: Mapped[List["OrganizationRole"]] = relationship(
        "OrganizationRole",
        back_populates="organization"
    )
    approval_settings: Mapped[Optional["OrganizationApprovalSettings"]] = relationship(
        "OrganizationApprovalSettings",
        back_populates="organization",
        uselist=False
    )
    voucher_approvals: Mapped[List["VoucherApproval"]] = relationship(
        "VoucherApproval",
        back_populates="organization"
    )
    settings: Mapped[Optional["OrganizationSettings"]] = relationship(
        "OrganizationSettings",
        back_populates="organization",
        uselist=False
    )
    
    # Expense Account relationships
    expense_accounts: Mapped[List["ExpenseAccount"]] = relationship(
        "ExpenseAccount",
        back_populates="organization"
    )

    # RBAC relationships
    service_roles: Mapped[List["ServiceRole"]] = relationship(
        "ServiceRole",
        back_populates="organization"
    )

    # Entitlement relationships
    org_entitlements: Mapped[List[OrgEntitlement]] = relationship(
        OrgEntitlement,
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    org_subentitlements: Mapped[List[OrgSubentitlement]] = relationship(
        OrgSubentitlement,
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    entitlement_events: Mapped[List[EntitlementEvent]] = relationship(
        EntitlementEvent,
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_org_status_subdomain', 'status', 'subdomain'),
        {'extend_existing': True}
    )

# Merged User model (took the more complete version from base.py, with fields from user_models.py like permissions, is_sso_user added)
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Multi-tenant fields - REQUIRED for all organization users
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_user_organization_id"), nullable=True, index=True)

    # User credentials
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Supabase Auth integration
    supabase_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True) # Supabase user UUID for auth integration

    # User details
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # NEW ROLE SYSTEM: Only 4 org-wide roles: org_admin, management, manager, executive
    # org_admin: Full access based on entitlement only (no RBAC)
    # management: Full owner-like access via RBAC (except Org Admin creation)
    # manager: Module-level access assigned at creation/management
    # executive: Submodule-level access based on reporting manager's modules
    role: Mapped[str] = mapped_column(String, nullable=False, default="executive") # org_admin, management, manager, executive (super_admin for platform-level only)
    department: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Permissions and status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    has_stock_access: Mapped[bool] = mapped_column(Boolean, default=True) # Module access for stock functionality

    # Module Access Control - User level module enablement
    assigned_modules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        # Core Business Modules
        "CRM": True,
        "ERP": True, 
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True,
        
        # Extended Modules
        "Manufacturing": True,
        "Procurement": True,
        "Project": True,
        "Asset": True,
        "Transport": True,
        "SEO": True,
        "Marketing": True,
        "Payroll": True,
        "Talent": True,
        
        # Advanced Modules
        "Workflow": True,
        "Integration": True,
        "AI_Analytics": True,
        "Streaming_Analytics": True,
        "AB_Test": True,
        "Website_Agent": True,
        "Email": True,
        "Calendar": True,
        "Task_Management": True,
        "Order_Book": True,
        "Exhibition": True,
    }) # Modules assigned to this user (subset of org enabled modules)

    # Executive-specific fields
    reporting_manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_reporting_manager_id"), nullable=True, index=True)
    sub_module_permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {module: {submodule: [actions]}} for executives - inherited from manager

    # Temporary master password support
    temp_password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Temporary password hash
    temp_password_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # Expiry for temp password
    force_password_reset: Mapped[bool] = mapped_column(Boolean, default=False) # Force password reset on next login

    # Profile
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Added from user_models.py
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # JSON field for flexible permissions
    is_sso_user: Mapped[bool] = mapped_column(Boolean, default=False) # Flag to identify SSO users
    sso_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True) # SSO provider name
    sso_id: Mapped[Optional[str]] = mapped_column(String, nullable=True) # SSO provider user ID
    
    # User preferences and settings
    user_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {}) # User-specific settings

    # Relationships with forward refs (class names only)
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", 
        back_populates="users"
    )
    
    # Executive reporting relationship
    reporting_manager: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[reporting_manager_id]
    )
    
    # Executives reporting to this manager
    executives: Mapped[List["User"]] = relationship(
        "User",
        back_populates="reporting_manager",
        foreign_keys=[reporting_manager_id]
    )
    
    # Task Management Relationships
    created_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        foreign_keys="Task.created_by",
        back_populates="creator"
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        back_populates="assignee"
    )
    created_projects: Mapped[List["TaskProject"]] = relationship(
        "TaskProject",
        back_populates="creator"
    )
    project_memberships: Mapped[List["TaskProjectMember"]] = relationship(
        "TaskProjectMember",
        back_populates="user"
    )
    task_comments: Mapped[List["TaskComment"]] = relationship(
        "TaskComment",
        back_populates="user"
    )
    task_attachments: Mapped[List["TaskAttachment"]] = relationship(
        "TaskAttachment",
        back_populates="user"
    )
    time_logs: Mapped[List["TaskTimeLog"]] = relationship(
        "TaskTimeLog",
        back_populates="user"
    )
    task_reminders: Mapped[List["TaskReminder"]] = relationship(
        "TaskReminder",
        back_populates="user"
    )
    
    # Calendar Management Relationships
    created_events: Mapped[List["CalendarEvent"]] = relationship(
        "CalendarEvent",
        foreign_keys="CalendarEvent.created_by",
        back_populates="creator"
    )
    event_attendances: Mapped[List["EventAttendee"]] = relationship(
        "EventAttendee",
        back_populates="user"
    )
    event_reminders: Mapped[List["EventReminder"]] = relationship(
        "EventReminder",
        back_populates="user"
    )
    owned_calendars: Mapped[List["Calendar"]] = relationship(
        "Calendar",
        back_populates="owner"
    )
    calendar_shares: Mapped[List["CalendarShare"]] = relationship(
        "CalendarShare",
        foreign_keys="CalendarShare.user_id",
        back_populates="user"
    )
    google_calendar_integration: Mapped[List["GoogleCalendarIntegration"]] = relationship(
        "GoogleCalendarIntegration",
        back_populates="user"
    )
    
    # OAuth2 Email Token relationship
    email_tokens: Mapped[List["UserEmailToken"]] = relationship(
        "UserEmailToken",
        back_populates="user"
    )
    # Company assignments for multi-company support
    company_assignments: Mapped[List["UserCompany"]] = relationship(
        "UserCompany",
        foreign_keys="UserCompany.user_id",
        back_populates="user"
    )
    
    # New organization role assignments
    organization_role_assignments: Mapped[List["UserOrganizationRole"]] = relationship(
        "UserOrganizationRole",
        foreign_keys="UserOrganizationRole.user_id",
        back_populates="user"
    )

    # SnappyMail relationship removed - integration discontinued

    # RBAC relationships
    service_roles: Mapped[List["UserServiceRole"]] = relationship(
        "UserServiceRole",
        foreign_keys="UserServiceRole.user_id",
        back_populates="user"
    )

    __table_args__ = (
        # Unique email per organization
        UniqueConstraint('organization_id', 'email', name='uq_user_org_email'),
        Index('idx_user_org_email', 'organization_id', 'email'),
        Index('idx_user_org_active', 'organization_id', 'is_active'),
        Index('idx_user_reporting_manager', 'reporting_manager_id'),
        {'extend_existing': True}
    )

# UserCompany many-to-many relationship for multi-company support
class UserCompany(Base):
    """Many-to-many relationship between Users and Companies"""
    __tablename__ = "user_companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_company_user_id"), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", name="fk_user_company_company_id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_user_company_organization_id"), nullable=False, index=True)
    
    # Assignment details
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_company_assigned_by_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_company_admin: Mapped[bool] = mapped_column(Boolean, default=False)  # True if user is admin of this company
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with forward refs (class names only)
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id],
        back_populates="company_assignments"
    )
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="user_assignments"
    )
    organization: Mapped["Organization"] = relationship(
        "Organization"
    )
    assigned_by: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[assigned_by_id]
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='uq_user_company'),
        Index('idx_user_company_user', 'user_id'),
        Index('idx_user_company_company', 'company_id'),
        Index('idx_user_company_org', 'organization_id'),
        Index('idx_user_company_active', 'is_active'),
        Index('idx_user_company_admin', 'is_company_admin'),
        {'extend_existing': True}
    )


# New Organization Role Hierarchy Models

class OrganizationRole(Base):
    """Organization-wide roles (management, manager, executive) with module-based permissions"""
    __tablename__ = "organization_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_org_role_organization_id"), nullable=False, index=True)
    
    # Role details
    name: Mapped[str] = mapped_column(String, nullable=False) # management, manager, executive
    display_name: Mapped[str] = mapped_column(String, nullable=False) # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hierarchy_level: Mapped[int] = mapped_column(Integer, nullable=False) # 1=Management, 2=Manager, 3=Executive
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_org_role_created_by_id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="organization_roles")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    user_assignments: Mapped[List["UserOrganizationRole"]] = relationship("UserOrganizationRole", back_populates="role")
    module_assignments: Mapped[List["RoleModuleAssignment"]] = relationship("RoleModuleAssignment", back_populates="role")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_org_role_org_name'),
        Index('idx_org_role_org_active', 'organization_id', 'is_active'),
        Index('idx_org_role_hierarchy', 'hierarchy_level'),
        {'extend_existing': True}
    )


class RoleModuleAssignment(Base):
    """Module assignments for organization roles - which modules each role can access"""
    __tablename__ = "role_module_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_role_module_organization_id"), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("organization_roles.id", name="fk_role_module_role_id"), nullable=False)
    
    # Module assignment details
    module_name: Mapped[str] = mapped_column(String, nullable=False) # CRM, ERP, HR, etc.
    access_level: Mapped[str] = mapped_column(String, nullable=False, default="full") # full, limited, view_only
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Specific permissions for the module
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_role_module_assigned_by_id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    role: Mapped["OrganizationRole"] = relationship("OrganizationRole", back_populates="module_assignments")
    assigned_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_by_id])
    
    __table_args__ = (
        UniqueConstraint('role_id', 'module_name', name='uq_role_module'),
        Index('idx_role_module_org', 'organization_id'),
        Index('idx_role_module_active', 'is_active'),
        {'extend_existing': True}
    )


class UserOrganizationRole(Base):
    """User assignments to organization roles"""
    __tablename__ = "user_organization_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_user_org_role_organization_id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_org_role_user_id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("organization_roles.id", name="fk_user_org_role_role_id"), nullable=False)
    
    # Assignment details
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_org_role_assigned_by_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Manager assignment for executives - executives report to managers per module
    manager_assignments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {"CRM": manager_user_id, "ERP": manager_user_id}
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="organization_role_assignments")
    role: Mapped["OrganizationRole"] = relationship("OrganizationRole", back_populates="user_assignments")
    assigned_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_by_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_org_role'),
        Index('idx_user_org_role_user', 'user_id'),
        Index('idx_user_org_role_role', 'role_id'),
        Index('idx_user_org_role_active', 'is_active'),
        {'extend_existing': True}
    )


# Voucher Approval Workflow Models

class OrganizationApprovalSettings(Base):
    """Organization-wide approval workflow settings"""
    __tablename__ = "organization_approval_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_approval_settings_organization_id"), nullable=False, unique=True, index=True)
    
    # Approval model settings
    approval_model: Mapped[str] = mapped_column(String, nullable=False, default="no_approval") # no_approval, level_1, level_2
    
    # Level 2 approval settings - which Management users can provide final approval
    level_2_approvers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {"user_ids": [1, 2, 3]} - Management users who can approve
    
    # Additional workflow settings
    auto_approve_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Auto-approve vouchers below this amount
    escalation_timeout_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=72) # Auto-escalate after X hours
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_approval_settings_updated_by_id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="approval_settings")
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])
    voucher_approvals: Mapped[List["VoucherApproval"]] = relationship("VoucherApproval", back_populates="approval_settings")
    
    __table_args__ = (
        Index('idx_approval_settings_model', 'approval_model'),
        {'extend_existing': True}
    )


class VoucherApproval(Base):
    """Individual voucher approval records"""
    __tablename__ = "voucher_approvals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_voucher_approval_organization_id"), nullable=False, index=True)
    approval_settings_id: Mapped[int] = mapped_column(Integer, ForeignKey("organization_approval_settings.id", name="fk_voucher_approval_settings_id"), nullable=False)
    
    # Voucher identification - generic to support all voucher types
    voucher_type: Mapped[str] = mapped_column(String, nullable=False) # sales_voucher, purchase_voucher, etc.
    voucher_id: Mapped[int] = mapped_column(Integer, nullable=False) # ID of the specific voucher
    voucher_number: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Human-readable voucher number
    voucher_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # Amount for threshold checking
    
    # Submitter information
    submitted_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_voucher_approval_submitted_by_id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Current approval status
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # pending, level_1_approved, approved, rejected
    current_approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_voucher_approval_current_approver_id"), nullable=True)
    
    # Level 1 approval (Manager)
    level_1_approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_voucher_approval_level_1_approver_id"), nullable=True)
    level_1_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    level_1_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Level 2 approval (Management)
    level_2_approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_voucher_approval_level_2_approver_id"), nullable=True)
    level_2_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    level_2_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Final decision
    final_decision: Mapped[Optional[str]] = mapped_column(String, nullable=True) # approved, rejected
    final_decision_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    final_decision_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_voucher_approval_final_decision_by_id"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="voucher_approvals")
    approval_settings: Mapped["OrganizationApprovalSettings"] = relationship("OrganizationApprovalSettings", back_populates="voucher_approvals")
    submitted_by: Mapped["User"] = relationship("User", foreign_keys=[submitted_by_id])
    current_approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[current_approver_id])
    level_1_approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[level_1_approver_id])
    level_2_approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[level_2_approver_id])
    final_decision_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[final_decision_by_id])
    
    __table_args__ = (
        UniqueConstraint('voucher_type', 'voucher_id', name='uq_voucher_approval'),
        Index('idx_voucher_approval_org', 'organization_id'),
        Index('idx_voucher_approval_status', 'status'),
        Index('idx_voucher_approval_submitted', 'submitted_by_id'),
        Index('idx_voucher_approval_current', 'current_approver_id'),
        {'extend_existing': True}
    )