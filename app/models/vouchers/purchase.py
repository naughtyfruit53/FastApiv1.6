# app/models/vouchers/purchase.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
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
    total_discount = Column(Float, default=0.0)
    round_off = Column(Float, default=0.0)  # Added to match schema and PDF calculations
    
    vendor = relationship("Vendor")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    purchase_requisition = relationship("app.models.procurement_models.PurchaseRequisition", back_populates="purchase_order", uselist=False)
    
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
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    gst_rate = Column(Float, default=18.0)
    discount_amount = Column(Float, default=0.0, nullable=False)
    taxable_amount = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    description = Column(Text)
    
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")  # Added relationship to Product

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
    
    purchase_order = relationship("PurchaseOrder")
    vendor = relationship("Vendor")
    items = relationship("GoodsReceiptNoteItem", back_populates="grn", cascade="all, delete-orphan")
    
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
    ordered_quantity = Column(Float, nullable=False)
    received_quantity = Column(Float, nullable=False)
    accepted_quantity = Column(Float, nullable=False)
    rejected_quantity = Column(Float, default=0.0)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    remarks = Column(Text)
    # Quality control fields
    batch_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    quality_status = Column(String, default="pending")  # pending, passed, failed
    
    grn = relationship("GoodsReceiptNote", back_populates="items")
    product = relationship("Product")
    po_item = relationship("PurchaseOrderItem")

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
    
    vendor = relationship("Vendor")
    purchase_order = relationship("PurchaseOrder")
    grn = relationship("GoodsReceiptNote")
    items = relationship("PurchaseVoucherItem", back_populates="purchase_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_org_voucher_number'),
        Index('idx_pv_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pv_org_po', 'organization_id', 'purchase_order_id'),
        Index('idx_pv_org_grn', 'organization_id', 'grn_id'),
        Index('idx_pv_org_date', 'organization_id', 'date'),
    )

class PurchaseVoucherItem(VoucherItemBase):
    __tablename__ = "purchase_voucher_items"
    
    purchase_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"), nullable=False)
    grn_item_id = Column(Integer, ForeignKey("goods_receipt_note_items.id"))  # Link to GRN item
    
    purchase_voucher = relationship("PurchaseVoucher", back_populates="items")
    grn_item = relationship("GoodsReceiptNoteItem")
    product = relationship("Product")  # Added relationship to Product

# Purchase Return (Rejection In)
class PurchaseReturn(BaseVoucher):
    __tablename__ = "purchase_returns"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    reference_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"))
    reason = Column(Text)
    
    vendor = relationship("Vendor")
    reference_voucher = relationship("PurchaseVoucher")
    items = relationship("PurchaseReturnItem", back_populates="purchase_return", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pr_org_voucher_number'),
        Index('idx_pr_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pr_org_date', 'organization_id', 'date'),
    )

class PurchaseReturnItem(VoucherItemBase):
    __tablename__ = "purchase_return_items"
    
    purchase_return_id = Column(Integer, ForeignKey("purchase_returns.id"), nullable=False)
    purchase_return = relationship("PurchaseReturn", back_populates="items")
    product = relationship("Product")  # Added relationship to Product