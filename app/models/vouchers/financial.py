# app/models/vouchers/financial.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase
from app.core.database import Base

# Credit Note
class CreditNote(BaseVoucher):
    __tablename__ = "credit_notes"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    reference_voucher_type = Column(String)
    reference_voucher_id = Column(Integer)
    reason = Column(String, nullable=False)
    
    customer = relationship("Customer")
    vendor = relationship("Vendor")
    items = relationship("CreditNoteItem", back_populates="credit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_cn_org_voucher_number'),
        Index('idx_cn_org_customer', 'organization_id', 'customer_id'),
        Index('idx_cn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_cn_org_date', 'organization_id', 'date'),
    )

class CreditNoteItem(SimpleVoucherItemBase):
    __tablename__ = "credit_note_items"
    
    credit_note_id = Column(Integer, ForeignKey("credit_notes.id"), nullable=False)
    credit_note = relationship("CreditNote", back_populates="items")

# Debit Note
class DebitNote(BaseVoucher):
    __tablename__ = "debit_notes"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    reference_voucher_type = Column(String)
    reference_voucher_id = Column(Integer)
    reason = Column(String, nullable=False)
    
    customer = relationship("Customer")
    vendor = relationship("Vendor")
    items = relationship("DebitNoteItem", back_populates="debit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_dn_org_voucher_number'),
        Index('idx_dn_org_customer', 'organization_id', 'customer_id'),
        Index('idx_dn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_dn_org_date', 'organization_id', 'date'),
    )

class DebitNoteItem(SimpleVoucherItemBase):
    __tablename__ = "debit_note_items"
    
    debit_note_id = Column(Integer, ForeignKey("debit_notes.id"), nullable=False)
    debit_note = relationship("DebitNote", back_populates="items")

# Payment Voucher
class PaymentVoucher(BaseVoucher):
    __tablename__ = "payment_vouchers"
    
    entity_id = Column(Integer, nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'Vendor', 'Customer', 'Employee'
    payment_method = Column(String)
    reference = Column(String)
    bank_account = Column(String)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Relationships
    chart_account = relationship("app.models.erp_models.ChartOfAccounts")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_payment_org_voucher_number'),
        Index('idx_pv_payment_org_entity', 'organization_id', 'entity_id'),
        Index('idx_pv_payment_org_date', 'organization_id', 'date'),
        Index('idx_pv_payment_chart_account', 'chart_account_id'),
    )

# Receipt Voucher
class ReceiptVoucher(BaseVoucher):
    __tablename__ = "receipt_vouchers"
    
    entity_id = Column(Integer, nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'Vendor', 'Customer', 'Employee'
    receipt_method = Column(String)
    reference = Column(String)
    bank_account = Column(String)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Relationships
    chart_account = relationship("app.models.erp_models.ChartOfAccounts")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_rv_org_voucher_number'),
        Index('idx_rv_org_entity', 'organization_id', 'entity_id'),
        Index('idx_rv_org_date', 'organization_id', 'date'),
        Index('idx_rv_chart_account', 'chart_account_id'),
    )

# Contra Voucher
class ContraVoucher(BaseVoucher):
    __tablename__ = "contra_vouchers"
    
    from_account = Column(String, nullable=False)
    to_account = Column(String, nullable=False)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Relationships
    chart_account = relationship("app.models.erp_models.ChartOfAccounts")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_contra_org_voucher_number'),
        Index('idx_contra_org_from_account', 'organization_id', 'from_account'),
        Index('idx_contra_org_to_account', 'organization_id', 'to_account'),
        Index('idx_contra_org_date', 'organization_id', 'date'),
        Index('idx_contra_chart_account', 'chart_account_id'),
    )

# Journal Voucher
class JournalVoucher(BaseVoucher):
    __tablename__ = "journal_vouchers"
    
    entries = Column(Text, nullable=False)  # JSON string for entries
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Relationships
    chart_account = relationship("app.models.erp_models.ChartOfAccounts")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_journal_org_voucher_number'),
        Index('idx_journal_org_date', 'organization_id', 'date'),
        Index('idx_journal_chart_account', 'chart_account_id'),
    )

# Inter Department Voucher
class InterDepartmentVoucher(BaseVoucher):
    __tablename__ = "inter_department_vouchers"
    
    from_department = Column(String, nullable=False)
    to_department = Column(String, nullable=False)
    
    items = relationship("InterDepartmentVoucherItem", back_populates="inter_department_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_idv_org_voucher_number'),
        Index('idx_idv_org_from_dept', 'organization_id', 'from_department'),
        Index('idx_idv_org_to_dept', 'organization_id', 'to_department'),
        Index('idx_idv_org_date', 'organization_id', 'date'),
    )

class InterDepartmentVoucherItem(SimpleVoucherItemBase):
    __tablename__ = "inter_department_voucher_items"
    
    inter_department_voucher_id = Column(Integer, ForeignKey("inter_department_vouchers.id"), nullable=False)
    inter_department_voucher = relationship("InterDepartmentVoucher", back_populates="items")

# Non-Sales Credit Note
class NonSalesCreditNote(BaseVoucher):
    __tablename__ = "non_sales_credit_notes"
    
    reason = Column(String, nullable=False)
    chart_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Relationships
    chart_account = relationship("app.models.erp_models.ChartOfAccounts")
    items = relationship("NonSalesCreditNoteItem", back_populates="non_sales_credit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_nscn_org_voucher_number'),
        Index('idx_nscn_org_date', 'organization_id', 'date'),
        Index('idx_nscn_chart_account', 'chart_account_id'),
    )

class NonSalesCreditNoteItem(SimpleVoucherItemBase):
    __tablename__ = "non_sales_credit_note_items"
    
    non_sales_credit_note_id = Column(Integer, ForeignKey("non_sales_credit_notes.id"), nullable=False)
    non_sales_credit_note = relationship("NonSalesCreditNote", back_populates="items")