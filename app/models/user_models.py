# app/models/user_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date

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
    state_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Legal details
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Corporate Identification Number

    # Subscription details
    plan_type: Mapped[str] = mapped_column(String, default="trial") # trial, basic, premium, enterprise
    max_users: Mapped[int] = mapped_column(Integer, default=5)
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

    # Module Access Control - Organization level module enablement
    enabled_modules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        "CRM": True,
        "ERP": True, 
        "HR": True,
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }) # Modules enabled for this organization

    # Onboarding status
    company_details_completed: Mapped[bool] = mapped_column(Boolean, default=False) # Track if company details have been filled

    # Custom org code
    org_code: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True, index=True) # Custom format: yy/mm-(total user)-tqnnnn

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with fully qualified paths
    users: Mapped[List["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User", 
        back_populates="organization"
    )
    companies: Mapped[List["app.models.system_models.Company"]] = relationship(
        "app.models.system_models.Company", 
        back_populates="organization"
    )
    vendors: Mapped[List["app.models.customer_models.Vendor"]] = relationship(
        "app.models.customer_models.Vendor", 
        back_populates="organization"
    )
    customers: Mapped[List["app.models.customer_models.Customer"]] = relationship(
        "app.models.customer_models.Customer", 
        back_populates="organization"
    )
    products: Mapped[List["app.models.product_models.Product"]] = relationship(
        "app.models.product_models.Product", 
        back_populates="organization"
    )
    stock_entries: Mapped[List["app.models.product_models.Stock"]] = relationship(
        "app.models.product_models.Stock", 
        back_populates="organization"
    )
    
    # ERP Core relationships
    chart_of_accounts: Mapped[List["app.models.erp_models.ChartOfAccounts"]] = relationship(
        "app.models.erp_models.ChartOfAccounts",
        back_populates="organization"
    )
    gst_configuration: Mapped[List["app.models.erp_models.GSTConfiguration"]] = relationship(
        "app.models.erp_models.GSTConfiguration",
        back_populates="organization"
    )
    tax_codes: Mapped[List["app.models.erp_models.TaxCode"]] = relationship(
        "app.models.erp_models.TaxCode",
        back_populates="organization"
    )
    journal_entries: Mapped[List["app.models.erp_models.JournalEntry"]] = relationship(
        "app.models.erp_models.JournalEntry",
        back_populates="organization"
    )
    accounts_payable: Mapped[List["app.models.erp_models.AccountsPayable"]] = relationship(
        "app.models.erp_models.AccountsPayable",
        back_populates="organization"
    )
    accounts_receivable: Mapped[List["app.models.erp_models.AccountsReceivable"]] = relationship(
        "app.models.erp_models.AccountsReceivable",
        back_populates="organization"
    )
    payment_records: Mapped[List["app.models.erp_models.PaymentRecord"]] = relationship(
        "app.models.erp_models.PaymentRecord",
        back_populates="organization"
    )
    general_ledger: Mapped[List["app.models.erp_models.GeneralLedger"]] = relationship(
        "app.models.erp_models.GeneralLedger",
        back_populates="organization"
    )
    cost_centers: Mapped[List["app.models.erp_models.CostCenter"]] = relationship(
        "app.models.erp_models.CostCenter",
        back_populates="organization"
    )
    bank_accounts: Mapped[List["app.models.erp_models.BankAccount"]] = relationship(
        "app.models.erp_models.BankAccount",
        back_populates="organization"
    )
    bank_reconciliations: Mapped[List["app.models.erp_models.BankReconciliation"]] = relationship(
        "app.models.erp_models.BankReconciliation",
        back_populates="organization"
    )
    financial_statements: Mapped[List["app.models.erp_models.FinancialStatement"]] = relationship(
        "app.models.erp_models.FinancialStatement",
        back_populates="organization"
    )
    financial_kpis: Mapped[List["app.models.erp_models.FinancialKPI"]] = relationship(
        "app.models.erp_models.FinancialKPI",
        back_populates="organization"
    )
    
    # Procurement relationships
    rfqs: Mapped[List["app.models.procurement_models.RequestForQuotation"]] = relationship(
        "app.models.procurement_models.RequestForQuotation",
        back_populates="organization"
    )
    vendor_quotations: Mapped[List["app.models.procurement_models.VendorQuotation"]] = relationship(
        "app.models.procurement_models.VendorQuotation",
        back_populates="organization"
    )
    vendor_evaluations: Mapped[List["app.models.procurement_models.VendorEvaluation"]] = relationship(
        "app.models.procurement_models.VendorEvaluation",
        back_populates="organization"
    )
    purchase_requisitions: Mapped[List["app.models.procurement_models.PurchaseRequisition"]] = relationship(
        "app.models.procurement_models.PurchaseRequisition",
        back_populates="organization"
    )
    
    # Tally integration relationships
    tally_configuration: Mapped[List["app.models.tally_models.TallyConfiguration"]] = relationship(
        "app.models.tally_models.TallyConfiguration",
        back_populates="organization"
    )
    tally_data_cache: Mapped[List["app.models.tally_models.TallyDataCache"]] = relationship(
        "app.models.tally_models.TallyDataCache",
        back_populates="organization"
    )
    tally_error_logs: Mapped[List["app.models.tally_models.TallyErrorLog"]] = relationship(
        "app.models.tally_models.TallyErrorLog",
        back_populates="organization"
    )
    
    # Migration relationships
    migration_jobs: Mapped[List["app.models.migration_models.MigrationJob"]] = relationship(
        "app.models.migration_models.MigrationJob",
        back_populates="organization"
    )
    
    # Enhanced inventory relationships
    warehouses: Mapped[List["app.models.enhanced_inventory_models.Warehouse"]] = relationship(
        "app.models.enhanced_inventory_models.Warehouse",
        back_populates="organization"
    )
    warehouse_stock: Mapped[List["app.models.enhanced_inventory_models.WarehouseStock"]] = relationship(
        "app.models.enhanced_inventory_models.WarehouseStock",
        back_populates="organization"
    )
    product_batches: Mapped[List["app.models.enhanced_inventory_models.ProductBatch"]] = relationship(
        "app.models.enhanced_inventory_models.ProductBatch",
        back_populates="organization"
    )
    product_serials: Mapped[List["app.models.enhanced_inventory_models.ProductSerial"]] = relationship(
        "app.models.enhanced_inventory_models.ProductSerial",
        back_populates="organization"
    )
    stock_movements: Mapped[List["app.models.enhanced_inventory_models.StockMovement"]] = relationship(
        "app.models.enhanced_inventory_models.StockMovement",
        back_populates="organization"
    )
    stock_adjustments: Mapped[List["app.models.enhanced_inventory_models.StockAdjustment"]] = relationship(
        "app.models.enhanced_inventory_models.StockAdjustment",
        back_populates="organization"
    )
    
    # Exhibition mode relationships
    exhibition_events: Mapped[List["app.models.exhibition_models.ExhibitionEvent"]] = relationship(
        "app.models.exhibition_models.ExhibitionEvent",
        back_populates="organization"
    )
    
    # Task Management relationships
    tasks: Mapped[List["app.models.task_management.Task"]] = relationship(
        "app.models.task_management.Task",
        back_populates="organization"
    )
    task_projects: Mapped[List["app.models.task_management.TaskProject"]] = relationship(
        "app.models.task_management.TaskProject",
        back_populates="organization"
    )
    
    # Calendar Management relationships
    calendar_events: Mapped[List["app.models.calendar_management.CalendarEvent"]] = relationship(
        "app.models.calendar_management.CalendarEvent",
        back_populates="organization"
    )
    calendars: Mapped[List["app.models.calendar_management.Calendar"]] = relationship(
        "app.models.calendar_management.Calendar",
        back_populates="organization"
    )
    google_calendar_integrations: Mapped[List["app.models.calendar_management.GoogleCalendarIntegration"]] = relationship(
        "app.models.calendar_management.GoogleCalendarIntegration",
        back_populates="organization"
    )
    
    # Email Management relationships
    email_accounts: Mapped[List["app.models.mail_management.EmailAccount"]] = relationship(
        "app.models.mail_management.EmailAccount",
        back_populates="organization"
    )
    emails: Mapped[List["app.models.mail_management.Email"]] = relationship(
        "app.models.mail_management.Email",
        back_populates="organization"
    )
    sent_emails: Mapped[List["app.models.mail_management.SentEmail"]] = relationship(
        "app.models.mail_management.SentEmail",
        back_populates="organization"
    )
    email_templates: Mapped[List["app.models.mail_management.EmailTemplate"]] = relationship(
        "app.models.mail_management.EmailTemplate",
        back_populates="organization"
    )
    email_rules: Mapped[List["app.models.mail_management.EmailRule"]] = relationship(
        "app.models.mail_management.EmailRule",
        back_populates="organization"
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
    username: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Supabase Auth integration
    supabase_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True) # Supabase user UUID for auth integration

    # User details
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="standard_user") # org_admin, admin, standard_user
    department: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Permissions and status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    has_stock_access: Mapped[bool] = mapped_column(Boolean, default=True) # Module access for stock functionality

    # Module Access Control - User level module assignments
    assigned_modules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        "CRM": True,
        "ERP": True,
        "HR": True, 
        "Inventory": True,
        "Service": True,
        "Analytics": True,
        "Finance": True
    }) # Modules assigned to this user (subset of org enabled modules)

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
    user_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=lambda: {
        "sticky_notes_enabled": True
    }) # User-specific settings including sticky notes preference

    # Relationships with fully qualified paths
    organization: Mapped[Optional["app.models.user_models.Organization"]] = relationship(
        "app.models.user_models.Organization", 
        back_populates="users"
    )
    
    # Task Management Relationships
    created_tasks: Mapped[List["app.models.task_management.Task"]] = relationship(
        "app.models.task_management.Task",
        foreign_keys="app.models.task_management.Task.created_by",
        back_populates="creator"
    )
    assigned_tasks: Mapped[List["app.models.task_management.Task"]] = relationship(
        "app.models.task_management.Task",
        foreign_keys="app.models.task_management.Task.assigned_to",
        back_populates="assignee"
    )
    created_projects: Mapped[List["app.models.task_management.TaskProject"]] = relationship(
        "app.models.task_management.TaskProject",
        back_populates="creator"
    )
    project_memberships: Mapped[List["app.models.task_management.TaskProjectMember"]] = relationship(
        "app.models.task_management.TaskProjectMember",
        back_populates="user"
    )
    task_comments: Mapped[List["app.models.task_management.TaskComment"]] = relationship(
        "app.models.task_management.TaskComment",
        back_populates="user"
    )
    task_attachments: Mapped[List["app.models.task_management.TaskAttachment"]] = relationship(
        "app.models.task_management.TaskAttachment",
        back_populates="user"
    )
    time_logs: Mapped[List["app.models.task_management.TaskTimeLog"]] = relationship(
        "app.models.task_management.TaskTimeLog",
        back_populates="user"
    )
    task_reminders: Mapped[List["app.models.task_management.TaskReminder"]] = relationship(
        "app.models.task_management.TaskReminder",
        back_populates="user"
    )
    
    # Calendar Management Relationships
    created_events: Mapped[List["app.models.calendar_management.CalendarEvent"]] = relationship(
        "app.models.calendar_management.CalendarEvent",
        foreign_keys="app.models.calendar_management.CalendarEvent.created_by",
        back_populates="creator"
    )
    event_attendances: Mapped[List["app.models.calendar_management.EventAttendee"]] = relationship(
        "app.models.calendar_management.EventAttendee",
        back_populates="user"
    )
    event_reminders: Mapped[List["app.models.calendar_management.EventReminder"]] = relationship(
        "app.models.calendar_management.EventReminder",
        back_populates="user"
    )
    owned_calendars: Mapped[List["app.models.calendar_management.Calendar"]] = relationship(
        "app.models.calendar_management.Calendar",
        back_populates="owner"
    )
    calendar_shares: Mapped[List["app.models.calendar_management.CalendarShare"]] = relationship(
        "app.models.calendar_management.CalendarShare",
        foreign_keys="app.models.calendar_management.CalendarShare.user_id",
        back_populates="user"
    )
    google_calendar_integration: Mapped[List["app.models.calendar_management.GoogleCalendarIntegration"]] = relationship(
        "app.models.calendar_management.GoogleCalendarIntegration",
        back_populates="user"
    )
    
    # Email Management Relationships
    email_accounts: Mapped[List["app.models.mail_management.EmailAccount"]] = relationship(
        "app.models.mail_management.EmailAccount",
        back_populates="user"
    )
    sent_emails: Mapped[List["app.models.mail_management.SentEmail"]] = relationship(
        "app.models.mail_management.SentEmail",
        back_populates="sender"
    )
    email_actions: Mapped[List["app.models.mail_management.EmailAction"]] = relationship(
        "app.models.mail_management.EmailAction",
        back_populates="user"
    )
    created_email_templates: Mapped[List["app.models.mail_management.EmailTemplate"]] = relationship(
        "app.models.mail_management.EmailTemplate",
        back_populates="creator"
    )
    email_rules: Mapped[List["app.models.mail_management.EmailRule"]] = relationship(
        "app.models.mail_management.EmailRule",
        back_populates="user"
    )
    
    # Sticky Notes relationship
    sticky_notes: Mapped[List["app.models.sticky_notes.StickyNote"]] = relationship(
        "app.models.sticky_notes.StickyNote",
        back_populates="user"
    )

    __table_args__ = (
        # Unique email per organization
        UniqueConstraint('organization_id', 'email', name='uq_user_org_email'),
        # Unique username per organization
        UniqueConstraint('organization_id', 'username', name='uq_user_org_username'),
        Index('idx_user_org_email', 'organization_id', 'email'),
        Index('idx_user_org_username', 'organization_id', 'username'),
        Index('idx_user_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

# Merged ServiceRole (took version from base.py with display_name, removed from base.py)
class ServiceRole(Base):
    """Service CRM roles (admin, manager, support, viewer)"""
    __tablename__ = "service_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_service_role_organization_id"), nullable=False, index=True)

    # Role details
    name: Mapped[str] = mapped_column(String, nullable=False) # admin, manager, support, viewer
    display_name: Mapped[str] = mapped_column(String, nullable=False) # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with fully qualified paths
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    user_assignments: Mapped[List["app.models.user_models.UserServiceRole"]] = relationship(
        "app.models.user_models.UserServiceRole", 
        back_populates="role"
    )
    role_permissions: Mapped[List["app.models.user_models.ServiceRolePermission"]] = relationship(
        "app.models.user_models.ServiceRolePermission", 
        back_populates="role"
    )

    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_service_role_org_name'),
        Index('idx_service_role_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )

# Merged ServicePermission (took version from base.py with module, action, removed from base.py)
class ServicePermission(Base):
    """Service CRM permissions for granular access control"""
    __tablename__ = "service_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Permission details
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True) # e.g., service_create, technician_read
    display_name: Mapped[str] = mapped_column(String, nullable=False) # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String, nullable=False, index=True) # service, technician, appointment, etc.
    action: Mapped[str] = mapped_column(String, nullable=False, index=True) # create, read, update, delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with fully qualified paths
    role_permissions: Mapped[List["app.models.user_models.ServiceRolePermission"]] = relationship(
        "app.models.user_models.ServiceRolePermission", 
        back_populates="permission"
    )

    __table_args__ = (
        Index('idx_service_permission_module_action', 'module', 'action'),
        {'extend_existing': True}
    )

# Merged ServiceRolePermission (took version from base.py, added organization_id from user_models.py)
class ServiceRolePermission(Base):
    """Many-to-many relationship between Service roles and permissions"""
    __tablename__ = "service_role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Added organization_id for consistency with multi-tenancy
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_service_role_permission_organization_id"), nullable=False, index=True)

    # Foreign keys
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_roles.id", name="fk_service_role_permission_role_id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_permissions.id", name="fk_service_role_permission_permission_id"), nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships with fully qualified paths
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    role: Mapped["app.models.user_models.ServiceRole"] = relationship(
        "app.models.user_models.ServiceRole", 
        back_populates="role_permissions"
    )
    permission: Mapped["app.models.user_models.ServicePermission"] = relationship(
        "app.models.user_models.ServicePermission", 
        back_populates="role_permissions"
    )

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_service_role_permission'),
        Index('idx_service_role_permission_role', 'role_id'),
        Index('idx_service_role_permission_permission', 'permission_id'),
        {'extend_existing': True}
    )

# Merged UserServiceRole (took version from base.py, added organization_id and assigned_at from user_models.py)
class UserServiceRole(Base):
    """Many-to-many relationship between Users and Service roles"""
    __tablename__ = "user_service_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Added organization_id for consistency with multi-tenancy
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_user_service_role_organization_id"), nullable=False, index=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_service_role_user_id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_roles.id", name="fk_user_service_role_role_id"), nullable=False)

    # Assignment details
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_user_service_role_assigned_by_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Added from user_models.py

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with fully qualified paths
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    user: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User", 
        foreign_keys=[user_id]
    )
    role: Mapped["app.models.user_models.ServiceRole"] = relationship(
        "app.models.user_models.ServiceRole", 
        back_populates="user_assignments"
    )
    assigned_by: Mapped[Optional["app.models.user_models.User"]] = relationship(
        "app.models.user_models.User", 
        foreign_keys=[assigned_by_id]
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_service_role'),
        Index('idx_user_service_role_user', 'user_id'),
        Index('idx_user_service_role_role', 'role_id'),
        Index('idx_user_service_role_active', 'is_active'),
        {'extend_existing': True}
    )