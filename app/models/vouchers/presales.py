# app/models/vouchers/presales.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase

# Quotation
class Quotation(BaseVoucher):
    __tablename__ = "quotations"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    valid_until = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    line_discount_type = Column(String)  # 'percentage' or 'amount'
    total_discount_type = Column(String)  # 'percentage' or 'amount'
    total_discount = Column(Float, default=0.0)
    round_off = Column(Float, default=0.0)  # Added to match schema and PDF calculations
    
    customer = relationship("Customer")
    items = relationship("app.models.vouchers.presales.QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_quotation_org_voucher_number'),
        Index('idx_quotation_org_customer', 'organization_id', 'customer_id'),
        Index('idx_quotation_org_date', 'organization_id', 'date'),
    )

class QuotationItem(SimpleVoucherItemBase):
    __tablename__ = "quotation_items"
    
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Added foreign key for product
    discount_percentage = Column(Float, default=0.0)
    gst_rate = Column(Float, default=18.0)
    discount_amount = Column(Float, default=0.0, nullable=False)
    taxable_amount = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    description = Column(Text)
    
    quotation = relationship("app.models.vouchers.presales.Quotation", back_populates="items")
    product = relationship("app.models.product_models.Product")  # Qualified Product path; adjust if location differs

# Proforma Invoice
class ProformaInvoice(BaseVoucher):
    __tablename__ = "proforma_invoices"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    valid_until = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    customer = relationship("Customer")
    items = relationship("app.models.vouchers.presales.ProformaInvoiceItem", back_populates="proforma_invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pi_org_voucher_number'),
        Index('idx_pi_org_customer', 'organization_id', 'customer_id'),
        Index('idx_pi_org_date', 'organization_id', 'date'),
    )

class ProformaInvoiceItem(VoucherItemBase):
    __tablename__ = "proforma_invoice_items"
    
    proforma_invoice_id = Column(Integer, ForeignKey("proforma_invoices.id"), nullable=False)
    proforma_invoice = relationship("app.models.vouchers.presales.ProformaInvoice", back_populates="items")

# Sales Order
class SalesOrder(BaseVoucher):
    __tablename__ = "sales_orders"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    delivery_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    customer = relationship("Customer")
    items = relationship("app.models.vouchers.presales.SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_so_org_voucher_number'),
        Index('idx_so_org_customer', 'organization_id', 'customer_id'),
        Index('idx_so_org_date', 'organization_id', 'date'),
        Index('idx_so_org_status', 'organization_id', 'status'),
    )

class SalesOrderItem(SimpleVoucherItemBase):
    __tablename__ = "sales_order_items"
    
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    sales_order = relationship("app.models.vouchers.presales.SalesOrder", back_populates="items")