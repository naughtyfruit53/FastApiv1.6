"""
ERP Core Models - Chart of Accounts, AP/AR, GST, and Financial Management
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum, and_
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class AccountType(enum.Enum):
    """Account types for Chart of Accounts"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"
    BANK = "bank"
    CASH = "cash"


class TaxType(enum.Enum):
    """Tax types for GST compliance"""
    CGST = "cgst"
    SGST = "sgst"
    IGST = "igst"
    CESS = "cess"
    TCS = "tcs"
    TDS = "tds"


class ChartOfAccounts(Base):
    """Chart of Accounts model for financial management"""
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Account identification
    account_code = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False, index=True)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    
    # Hierarchy
    parent_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True)
    level = Column(Integer, default=0, nullable=False)
    is_group = Column(Boolean, default=False, nullable=False)
    
    # Financial details
    opening_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    can_post = Column(Boolean, default=True, nullable=False)  # Can post transactions to this account
    is_reconcilable = Column(Boolean, default=False, nullable=False)  # Bank/Cash accounts
    
    # Metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="chart_of_accounts")
    parent_account = relationship("ChartOfAccounts", remote_side=[id], back_populates="sub_accounts")
    sub_accounts = relationship("ChartOfAccounts", back_populates="parent_account")
    journal_entries = relationship("JournalEntry", back_populates="account")
    general_ledger_entries = relationship("GeneralLedger", back_populates="account")
    bank_account = relationship("BankAccount", back_populates="chart_account", uselist=False)
    
    # Master Data relationships (back references)
    categories_income = relationship("app.models.master_data_models.Category", 
                                   foreign_keys="app.models.master_data_models.Category.default_income_account_id",
                                   back_populates="default_income_account")
    categories_expense = relationship("app.models.master_data_models.Category", 
                                    foreign_keys="app.models.master_data_models.Category.default_expense_account_id",
                                    back_populates="default_expense_account")
    categories_asset = relationship("app.models.master_data_models.Category", 
                                  foreign_keys="app.models.master_data_models.Category.default_asset_account_id",
                                  back_populates="default_asset_account")
    tax_codes = relationship("app.models.master_data_models.TaxCode", back_populates="tax_account")
    payment_terms_discount = relationship("app.models.master_data_models.PaymentTermsExtended", 
                                         foreign_keys="app.models.master_data_models.PaymentTermsExtended.discount_account_id",
                                         back_populates="discount_account")
    payment_terms_penalty = relationship("app.models.master_data_models.PaymentTermsExtended", 
                                       foreign_keys="app.models.master_data_models.PaymentTermsExtended.penalty_account_id",
                                       back_populates="penalty_account")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'account_code', name='uq_org_account_code'),
        Index('idx_coa_org_type', 'organization_id', 'account_type'),
        Index('idx_coa_parent', 'parent_account_id'),
    )


class GSTConfiguration(Base):
    """GST Configuration for tax compliance"""
    __tablename__ = "gst_configuration"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # GST Registration
    gstin = Column(String(15), nullable=False, unique=True, index=True)
    trade_name = Column(String(200), nullable=False)
    legal_name = Column(String(200), nullable=False)
    
    # Registration details
    registration_date = Column(Date, nullable=False)
    constitution = Column(String(100), nullable=False)  # Private Limited, Partnership, etc.
    business_type = Column(String(100), nullable=False)  # Regular, Composition, etc.
    
    # Address
    address_line1 = Column(String(200), nullable=False)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    
    # Configuration
    is_composition_scheme = Column(Boolean, default=False, nullable=False)
    composition_tax_rate = Column(Numeric(5, 2), nullable=True)  # For composition dealers
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="gst_configuration")
    tax_codes = relationship("ERPTaxCode", back_populates="gst_configuration")


class ERPTaxCode(Base):
    """Tax codes for GST and other tax types"""
    __tablename__ = "erp_tax_codes"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    gst_configuration_id = Column(Integer, ForeignKey("gst_configuration.id"), nullable=True, index=True)
    
    # Tax code identification
    tax_code = Column(String(50), nullable=False, index=True)
    tax_name = Column(String(200), nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False, index=True)
    
    # Tax rates
    tax_rate = Column(Numeric(5, 2), nullable=False)  # Percentage
    is_inclusive = Column(Boolean, default=False, nullable=False)  # Tax inclusive/exclusive
    
    # HSN/SAC mapping
    hsn_sac_code = Column(String(20), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Accounts mapping
    tax_payable_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    tax_input_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="erp_tax_codes")
    gst_configuration = relationship("GSTConfiguration", back_populates="tax_codes")
    tax_payable_account = relationship("ChartOfAccounts", foreign_keys=[tax_payable_account_id])
    tax_input_account = relationship("ChartOfAccounts", foreign_keys=[tax_input_account_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'tax_code', name='uq_org_tax_code'),
        Index('idx_tax_org_type', 'organization_id', 'tax_type'),
    )


class JournalEntry(Base):
    """Journal entries for double-entry bookkeeping"""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Entry details
    entry_number = Column(String(50), nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)
    debit_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    credit_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # voucher_type like purchase, sale, payment
    transaction_id = Column(Integer, nullable=False, index=True)  # Reference to voucher ID
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    reference_number = Column(String(50), nullable=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="journal_entries")
    account = relationship("ChartOfAccounts", back_populates="journal_entries")
    cost_center = relationship("CostCenter")
    
    # Constraints
    __table_args__ = (
        Index('idx_je_org_date', 'organization_id', 'entry_date'),
        Index('idx_je_transaction', 'transaction_type', 'transaction_id'),
    )


class AccountsPayable(Base):
    """Accounts Payable for vendor management"""
    __tablename__ = "accounts_payable"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Vendor details
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    
    # Financial details
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    # Due dates
    due_date = Column(Date, nullable=False)
    payment_terms = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="unpaid", nullable=False)  # unpaid, partial, paid, overdue
    is_overdue = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="accounts_payable")
    vendor = relationship("Vendor", back_populates="accounts_payable")
    payment_records = relationship(
        "PaymentRecord",
        primaryjoin=lambda: and_(PaymentRecord.reference_type == 'payable', foreign(PaymentRecord.reference_id) == AccountsPayable.id),
        back_populates="accounts_payable"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'invoice_number', name='uq_org_invoice_number'),
        Index('idx_ap_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_ap_status', 'status'),
    )


class AccountsReceivable(Base):
    """Accounts Receivable for customer management"""
    __tablename__ = "accounts_receivable"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer details
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    
    # Financial details
    total_amount = Column(Numeric(15, 2), nullable=False)
    received_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    # Due dates
    due_date = Column(Date, nullable=False)
    payment_terms = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="unpaid", nullable=False)  # unpaid, partial, paid, overdue
    is_overdue = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="accounts_receivable")
    customer = relationship("Customer", back_populates="accounts_receivable")
    payment_records = relationship(
        "PaymentRecord",
        primaryjoin=lambda: and_(PaymentRecord.reference_type == 'receivable', foreign(PaymentRecord.reference_id) == AccountsReceivable.id),
        back_populates="accounts_receivable",
        overlaps="payment_records"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'invoice_number', name='uq_org_ar_invoice_number'),
        Index('idx_ar_org_customer', 'organization_id', 'customer_id'),
        Index('idx_ar_status', 'status'),
    )


class PaymentRecord(Base):
    """Payment records for both AP and AR"""
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Payment details
    payment_number = Column(String(50), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, bank_transfer, credit_card, etc.
    
    # Reference
    reference_type = Column(String(20), nullable=False)  # payable, receivable
    reference_id = Column(Integer, nullable=False, index=True)  # AP or AR ID
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=True)
    
    # Status
    status = Column(String(20), default="processed", nullable=False)  # pending, processed, failed
    transaction_fee = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="payment_records")
    bank_account = relationship("BankAccount")
    accounts_payable = relationship(
        "AccountsPayable",
        primaryjoin=lambda: and_(PaymentRecord.reference_type == 'payable', foreign(PaymentRecord.reference_id) == AccountsPayable.id),
        back_populates="payment_records",
        overlaps="payment_records"
    )
    accounts_receivable = relationship(
        "AccountsReceivable",
        primaryjoin=lambda: and_(PaymentRecord.reference_type == 'receivable', foreign(PaymentRecord.reference_id) == AccountsReceivable.id),
        back_populates="payment_records",
        overlaps="accounts_payable,payment_records"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'payment_number', name='uq_org_payment_number'),
        Index('idx_pr_org_date', 'organization_id', 'payment_date'),
        Index('idx_pr_reference', 'reference_type', 'reference_id'),
    )


class GeneralLedger(Base):
    """General Ledger for all transactions"""
    __tablename__ = "general_ledger"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Transaction details
    transaction_number = Column(String(50), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    debit_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    credit_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Account and reference
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    reference_type = Column(String(50), nullable=False)  # voucher_type
    reference_id = Column(Integer, nullable=False, index=True)  # voucher_id
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="general_ledger")
    account = relationship("ChartOfAccounts", back_populates="general_ledger_entries")
    cost_center = relationship("CostCenter", back_populates="general_ledger_entries")
    
    # Constraints
    __table_args__ = (
        Index('idx_gl_org_account_date', 'organization_id', 'account_id', 'transaction_date'),
        Index('idx_gl_reference', 'reference_type', 'reference_id'),
        Index('idx_gl_transaction_number', 'transaction_number'),
    )


class CostCenter(Base):
    """Cost Center for departmental accounting"""
    __tablename__ = "cost_centers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Cost center identification
    cost_center_code = Column(String(50), nullable=False, index=True)
    cost_center_name = Column(String(200), nullable=False)
    
    # Hierarchy
    parent_cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True, index=True)
    level = Column(Integer, default=0, nullable=False)
    
    # Financial details
    budget_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    department = Column(String(100), nullable=True)
    manager_id = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="cost_centers")
    parent_cost_center = relationship("CostCenter", remote_side=[id], back_populates="sub_cost_centers")
    sub_cost_centers = relationship("CostCenter", back_populates="parent_cost_center")
    general_ledger_entries = relationship("GeneralLedger", back_populates="cost_center")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'cost_center_code', name='uq_org_cost_center_code'),
        Index('idx_cc_org_active', 'organization_id', 'is_active'),
    )


class BankAccount(Base):
    """Bank accounts for cash management"""
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Bank details
    bank_name = Column(String(200), nullable=False)
    branch_name = Column(String(200), nullable=True)
    account_number = Column(String(50), nullable=False, index=True)
    ifsc_code = Column(String(20), nullable=True)
    swift_code = Column(String(20), nullable=True)
    
    # Account details
    account_type = Column(String(50), nullable=False)  # Savings, Current, etc.
    currency = Column(String(3), default="INR", nullable=False)
    opening_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    auto_reconcile = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="bank_accounts")
    chart_account = relationship("ChartOfAccounts", back_populates="bank_account")
    bank_reconciliations = relationship("BankReconciliation", back_populates="bank_account")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'account_number', name='uq_org_account_number'),
        Index('idx_bank_org_active', 'organization_id', 'is_active'),
    )


class BankReconciliation(Base):
    """Bank reconciliation records"""
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    
    # Reconciliation details
    reconciliation_date = Column(Date, nullable=False, index=True)
    statement_date = Column(Date, nullable=False)
    bank_balance = Column(Numeric(15, 2), nullable=False)
    book_balance = Column(Numeric(15, 2), nullable=False)
    
    # Reconciliation amounts
    outstanding_deposits = Column(Numeric(15, 2), default=0.00, nullable=False)
    outstanding_checks = Column(Numeric(15, 2), default=0.00, nullable=False)
    bank_charges = Column(Numeric(15, 2), default=0.00, nullable=False)
    interest_earned = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Status
    status = Column(String(20), default="pending", nullable=False)  # pending, reconciled, discrepancy
    difference_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="bank_reconciliations")
    bank_account = relationship("BankAccount", back_populates="bank_reconciliations")
    
    # Constraints
    __table_args__ = (
        Index('idx_recon_org_date', 'organization_id', 'reconciliation_date'),
        Index('idx_recon_status', 'status'),
    )


class FinancialStatement(Base):
    """Financial statements (P&L, Balance Sheet, etc.)"""
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Statement details
    statement_type = Column(String(50), nullable=False, index=True)  # profit_loss, balance_sheet, trial_balance, cash_flow
    statement_name = Column(String(200), nullable=False)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Statement data (JSON format for flexibility)
    statement_data = Column(JSON, nullable=False)  # Contains the complete statement structure
    summary_data = Column(JSON, nullable=True)  # Contains key metrics and totals
    
    # Configuration
    is_final = Column(Boolean, default=False, nullable=False)
    is_audited = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="financial_statements")
    
    # Constraints
    __table_args__ = (
        Index('idx_fs_org_type_period', 'organization_id', 'statement_type', 'period_end'),
        Index('idx_fs_period', 'period_start', 'period_end'),
    )


class FinancialKPI(Base):
    """Financial KPIs and metrics tracking"""
    __tablename__ = "financial_kpis"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # KPI details
    kpi_code = Column(String(50), nullable=False, index=True)
    kpi_name = Column(String(200), nullable=False)
    kpi_category = Column(String(100), nullable=False, index=True)  # profitability, liquidity, efficiency, etc.
    
    # Value and calculation
    kpi_value = Column(Numeric(15, 4), nullable=False)
    calculation_method = Column(Text, nullable=True)  # Formula or method used
    
    # Period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Target and variance
    target_value = Column(Numeric(15, 4), nullable=True)
    variance_percentage = Column(Numeric(8, 2), nullable=True)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculated_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="financial_kpis")
    
    # Constraints
    __table_args__ = (
        Index('idx_kpi_org_category_period', 'organization_id', 'kpi_category', 'period_end'),
        Index('idx_kpi_code_period', 'kpi_code', 'period_end'),
    )