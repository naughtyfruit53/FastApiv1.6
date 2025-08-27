# app/models/erp_models.py
"""
ERP Core Models - Chart of Accounts, AP/AR, GST, and Financial Management
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship
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
    tax_codes = relationship("TaxCode", back_populates="gst_configuration")


class TaxCode(Base):
    """Tax codes for GST and other tax types"""
    __tablename__ = "tax_codes"

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
    organization = relationship("Organization", back_populates="tax_codes")
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
    reference_type = Column(String(50), nullable=True, index=True)  # voucher type
    reference_id = Column(Integer, nullable=True, index=True)  # voucher id
    reference_number = Column(String(50), nullable=True, index=True)  # voucher number
    
    # Financial amounts
    debit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    credit_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Description
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status
    is_reconciled = Column(Boolean, default=False, nullable=False)
    reconciled_date = Column(Date, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="journal_entries")
    account = relationship("ChartOfAccounts", back_populates="journal_entries")
    
    # Constraints
    __table_args__ = (
        Index('idx_journal_org_date', 'organization_id', 'entry_date'),
        Index('idx_journal_reference', 'reference_type', 'reference_id'),
    )


class AccountsPayable(Base):
    """Accounts Payable tracking"""
    __tablename__ = "accounts_payable"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Bill details
    bill_number = Column(String(100), nullable=False, index=True)
    bill_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    
    # Financial amounts
    bill_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax details
    tax_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Reference
    reference_type = Column(String(50), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)
    
    # Status
    payment_status = Column(String(20), default="pending", nullable=False, index=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="accounts_payable")
    vendor = relationship("Vendor", back_populates="accounts_payable")
    payment_records = relationship("PaymentRecord", back_populates="accounts_payable")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'vendor_id', 'bill_number', name='uq_org_vendor_bill'),
        Index('idx_ap_org_status', 'organization_id', 'payment_status'),
        Index('idx_ap_due_date', 'due_date'),
    )


class AccountsReceivable(Base):
    """Accounts Receivable tracking"""
    __tablename__ = "accounts_receivable"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(100), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    
    # Financial amounts
    invoice_amount = Column(Numeric(15, 2), nullable=False)
    received_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax details
    tax_amount = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Reference
    reference_type = Column(String(50), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)
    
    # Status
    payment_status = Column(String(20), default="pending", nullable=False, index=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="accounts_receivable")
    customer = relationship("Customer", back_populates="accounts_receivable")
    payment_records = relationship("PaymentRecord", back_populates="accounts_receivable")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'customer_id', 'invoice_number', name='uq_org_customer_invoice'),
        Index('idx_ar_org_status', 'organization_id', 'payment_status'),
        Index('idx_ar_due_date', 'due_date'),
    )


class PaymentRecord(Base):
    """Payment records for AP/AR"""
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Payment details
    payment_number = Column(String(100), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # Cash, Bank, Cheque, etc.
    
    # References
    accounts_payable_id = Column(Integer, ForeignKey("accounts_payable.id"), nullable=True, index=True)
    accounts_receivable_id = Column(Integer, ForeignKey("accounts_receivable.id"), nullable=True, index=True)
    
    # Bank details (if applicable)
    bank_account = Column(String(100), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="payment_records")
    accounts_payable = relationship("AccountsPayable", back_populates="payment_records")
    accounts_receivable = relationship("AccountsReceivable", back_populates="payment_records")
    
    # Constraints
    __table_args__ = (
        Index('idx_payment_org_date', 'organization_id', 'payment_date'),
        Index('idx_payment_method', 'payment_method'),
    )