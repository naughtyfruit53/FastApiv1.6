# app/models/vouchers/sales.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase

# Delivery Challan - Enhanced for auto-population from SO
class DeliveryChallan(BaseVoucher):
    __tablename__ = "delivery_challans"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"))
    delivery_date = Column(DateTime(timezone=True))
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    destination = Column(String)
    
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    items = relationship("DeliveryChallanItem", back_populates="delivery_challan", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_dc_org_voucher_number'),
        Index('idx_dc_org_customer', 'organization_id', 'customer_id'),
        Index('idx_dc_org_so', 'organization_id', 'sales_order_id'),
        Index('idx_dc_org_date', 'organization_id', 'delivery_date'),
    )

class DeliveryChallanItem(SimpleVoucherItemBase):
    __tablename__ = "delivery_challan_items"
    
    delivery_challan_id = Column(Integer, ForeignKey("delivery_challans.id"), nullable=False)
    so_item_id = Column(Integer, ForeignKey("sales_order_items.id"))  # Link to SO item
    
    delivery_challan = relationship("DeliveryChallan", back_populates="items")
    so_item = relationship("SalesOrderItem")

# Sales Voucher - Enhanced for auto-population from delivery challan
class SalesVoucher(BaseVoucher):
    __tablename__ = "sales_vouchers"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"))
    delivery_challan_id = Column(Integer, ForeignKey("delivery_challans.id"))  # Auto-populate from challan
    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    place_of_supply = Column(String)
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    e_way_bill_number = Column(String)
    voucher_type = Column(String, nullable=False, default="sales", index=True)
    
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    delivery_challan = relationship("DeliveryChallan")
    items = relationship("SalesVoucherItem", back_populates="sales_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_sv_org_voucher_number'),
        Index('idx_sv_org_customer', 'organization_id', 'customer_id'),
        Index('idx_sv_org_so', 'organization_id', 'sales_order_id'),
        Index('idx_sv_org_challan', 'organization_id', 'delivery_challan_id'),
        Index('idx_sv_org_date', 'organization_id', 'date'),
    )

class SalesVoucherItem(VoucherItemBase):
    __tablename__ = "sales_voucher_items"
    
    sales_voucher_id = Column(Integer, ForeignKey("sales_vouchers.id"), nullable=False)
    delivery_challan_item_id = Column(Integer, ForeignKey("delivery_challan_items.id"))  # Link to challan item
    hsn_code = Column(String)
    
    sales_voucher = relationship("SalesVoucher", back_populates="items")
    challan_item = relationship("DeliveryChallanItem")

# Sales Return (Rejection Out)
class SalesReturn(BaseVoucher):
    __tablename__ = "sales_returns"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    reference_voucher_id = Column(Integer, ForeignKey("sales_vouchers.id"))
    reason = Column(Text)
    
    customer = relationship("Customer")
    reference_voucher = relationship("SalesVoucher")
    items = relationship("SalesReturnItem", back_populates="sales_return", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_sr_org_voucher_number'),
        Index('idx_sr_org_customer', 'organization_id', 'customer_id'),
        Index('idx_sr_org_date', 'organization_id', 'date'),
    )

class SalesReturnItem(VoucherItemBase):
    __tablename__ = "sales_return_items"
    
    sales_return_id = Column(Integer, ForeignKey("sales_returns.id"), nullable=False)
    sales_return = relationship("SalesReturn", back_populates="items")