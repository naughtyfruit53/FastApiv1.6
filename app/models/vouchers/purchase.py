# app/models/vouchers/purchase.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase
from app.models.product_models import Product  # Added import for Product

# Purchase Order
class PurchaseOrder(BaseVoucher):
    __tablename__ = "purchase_orders"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    delivery_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    line_discount_type = Column(String)  # 'percentage' or 'amount'
    total_discount_type = Column(String)  # 'percentage' or 'amount'
    total_discount = Column(Float, default=0.0, nullable=False)
    round_off = Column(Float, default=0.0, nullable=False)  # Added to match schema and PDF calculations
    additional_charges = Column(JSONB, default=dict)
    # Tracking fields
    transporter_name = Column(String)
    tracking_number = Column(String)
    tracking_link = Column(String)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # Soft delete flag
    deletion_remark = Column(Text)  # Delete reason
    
    vendor = relationship("Vendor", lazy='selectin')  # Async-safe lazy loading
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan", lazy='selectin')
    purchase_requisition = relationship("app.models.procurement_models.PurchaseRequisition", back_populates="purchase_order", uselist=False, lazy='selectin')
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_po_org_voucher_number'),
        Index('idx_po_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_po_org_date', 'organization_id', 'date'),
        Index('idx_po_org_status', 'organization_id', 'status'),
    )

class PurchaseOrderItem(SimpleVoucherItemBase):
    __tablename__ = "purchase_order_items"
    
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Added foreign key for product
    delivered_quantity = Column(Float, default=0.0, nullable=False)
    pending_quantity = Column(Float, default=0.0, nullable=False)
    discount_percentage = Column(Float, default=0.0, nullable=False)
    gst_rate = Column(Float, default=18.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    taxable_amount = Column(Float, default=0.0, nullable=False)
    cgst_amount = Column(Float, default=0.0, nullable=False)
    sgst_amount = Column(Float, default=0.0, nullable=False)
    igst_amount = Column(Float, default=0.0, nullable=False)
    description = Column(Text)
    discounted_price = Column(Float, default=0.0, nullable=False)
    
    purchase_order = relationship("PurchaseOrder", back_populates="items", lazy='selectin')
    product = relationship("Product", lazy='selectin')  # Added relationship to Product

# Goods Receipt Note (GRN) - Enhanced for auto-population from PO
class GoodsReceiptNote(BaseVoucher):
    __tablename__ = "goods_receipt_notes"
    
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    grn_date = Column(DateTime(timezone=True), nullable=False)
    challan_number = Column(String)
    challan_date = Column(DateTime(timezone=True))
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    inspection_status = Column(String, default="pending")  # pending, completed, rejected
    additional_charges = Column(JSONB, default=dict)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # Soft delete flag
    deletion_remark = Column(Text)  # Delete reason
    
    purchase_order = relationship("PurchaseOrder", lazy='selectin')
    vendor = relationship("Vendor", lazy='selectin')
    items = relationship("GoodsReceiptNoteItem", back_populates="grn", cascade="all, delete-orphan", lazy='selectin')
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_grn_org_voucher_number'),
        Index('idx_grn_org_po', 'organization_id', 'purchase_order_id'),
        Index('idx_grn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_grn_org_date', 'organization_id', 'grn_date'),
    )

class GoodsReceiptNoteItem(Base):
    __tablename__ = "goods_receipt_note_items"
    
    id = Column(Integer, primary_key=True, index=True)
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    po_item_id = Column(Integer, ForeignKey("purchase_order_items.id"))
    ordered_quantity = Column(Float, default=0.0, nullable=False)
    received_quantity = Column(Float, default=0.0, nullable=False)
    accepted_quantity = Column(Float, default=0.0, nullable=False)
    rejected_quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    remarks = Column(Text)
    # Quality control fields
    batch_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    quality_status = Column(String, default="pending")  # pending, passed, failed
    
    grn = relationship("GoodsReceiptNote", back_populates="items", lazy='selectin')
    product = relationship("Product", lazy='selectin')
    po_item = relationship("PurchaseOrderItem", lazy='selectin')

# Purchase Voucher - Enhanced for auto-population from GRN
class PurchaseVoucher(BaseVoucher):
    __tablename__ = "purchase_vouchers"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"))  # Auto-populate from GRN
    invoice_number = Column(String)
    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    e_way_bill_number = Column(String)
    vendor_voucher_number = Column(String)  # Vendor's own voucher/invoice reference number
    additional_charges = Column(JSONB, default=dict)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # Soft delete flag
    deletion_remark = Column(Text)  # Delete reason
    
    vendor = relationship("Vendor", lazy='selectin')
    purchase_order = relationship("PurchaseOrder", lazy='selectin')
    grn = relationship("GoodsReceiptNote", lazy='selectin')
    items = relationship("PurchaseVoucherItem", back_populates="purchase_voucher", cascade="all, delete-orphan", lazy='selectin')
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_org_voucher_number'),
        # Prevent duplicate PV per GRN (allows null grn_id)
        UniqueConstraint('organization_id', 'grn_id', name='uq_pv_org_grn'),
        Index('idx_pv_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pv_org_po', 'organization_id', 'purchase_order_id'),
        Index('idx_pv_org_grn', 'organization_id', 'grn_id'),
        Index('idx_pv_org_date', 'organization_id', 'date'),
        Index('idx_pv_vendor_voucher_number', 'organization_id', 'vendor_voucher_number'),
    )

class PurchaseVoucherItem(VoucherItemBase):
    __tablename__ = "purchase_voucher_items"
    
    purchase_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"), nullable=False)
    grn_item_id = Column(Integer, ForeignKey("goods_receipt_note_items.id"))  # Link to GRN item
    description = Column(Text)
    
    purchase_voucher = relationship("PurchaseVoucher", back_populates="items", lazy='selectin')
    grn_item = relationship("GoodsReceiptNoteItem", lazy='selectin')
    product = relationship("Product", lazy='selectin')  # Added relationship to Product

# Purchase Return (Rejection In)
class PurchaseReturn(BaseVoucher):
    __tablename__ = "purchase_returns"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    reference_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"))
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"))  
    reason = Column(Text)
    additional_charges = Column(JSONB, default=dict)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)  # Soft delete flag
    deletion_remark = Column(Text)  # Delete reason
    
    vendor = relationship("Vendor", lazy='selectin')
    reference_voucher = relationship("PurchaseVoucher", lazy='selectin')
    grn = relationship("GoodsReceiptNote", lazy='selectin')
    items = relationship("PurchaseReturnItem", back_populates="purchase_return", cascade="all, delete-orphan", lazy='selectin')
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pr_org_voucher_number'),
        # Prevent duplicate PR per GRN (allows null grn_id)
        UniqueConstraint('organization_id', 'grn_id', name='uq_pr_org_grn'),
        Index('idx_pr_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_purchase_return_org_date', 'organization_id', 'date'),  # Changed name to avoid conflict
    )

class PurchaseReturnItem(VoucherItemBase):
    __tablename__ = "purchase_return_items"
    
    purchase_return_id = Column(Integer, ForeignKey("purchase_returns.id"), nullable=False)
    purchase_return = relationship("PurchaseReturn", back_populates="items", lazy='selectin')
    product = relationship("Product", lazy='selectin')  # Added relationship to Product
    