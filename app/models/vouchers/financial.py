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
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_payment_org_voucher_number'),
        Index('idx_pv_payment_org_entity', 'organization_id', 'entity_id'),
        Index('idx_pv_payment_org_date', 'organization_id', 'date'),
    )

# Receipt Voucher
class ReceiptVoucher(BaseVoucher):
    __tablename__ = "receipt_vouchers"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    receipt_method = Column(String)
    reference = Column(String)
    bank_account = Column(String)
    
    customer = relationship("Customer")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_rv_org_voucher_number'),
        Index('idx_rv_org_customer', 'organization_id', 'customer_id'),
        Index('idx_rv_org_date', 'organization_id', 'date'),
    )

# Contra Voucher
class ContraVoucher(BaseVoucher):
    __tablename__ = "contra_vouchers"
    
    from_account = Column(String, nullable=False)
    to_account = Column(String, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_contra_org_voucher_number'),
        Index('idx_contra_org_from_account', 'organization_id', 'from_account'),
        Index('idx_contra_org_to_account', 'organization_id', 'to_account'),
        Index('idx_contra_org_date', 'organization_id', 'date'),
    )

# Journal Voucher
class JournalVoucher(BaseVoucher):
    __tablename__ = "journal_vouchers"
    
    entries = Column(Text, nullable=False)  # JSON string for entries
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_journal_org_voucher_number'),
        Index('idx_journal_org_date', 'organization_id', 'date'),
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