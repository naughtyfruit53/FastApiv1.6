# app/models/vouchers/base.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func
from app.core.database import Base

class BaseVoucher(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED for all vouchers
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    voucher_number = Column(String, nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    status = Column(String, default="draft")  # draft, confirmed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    @declared_attr
    def created_by(cls):
        return Column(Integer, ForeignKey("users.id"))

    @declared_attr
    def created_by_user(cls):
        return relationship("User", foreign_keys=[cls.created_by])

class VoucherItemBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    taxable_amount = Column(Float, nullable=False)
    gst_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    @declared_attr
    def product(cls):
        return relationship("Product")

class SimpleVoucherItemBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    @declared_attr
    def product(cls):
        return relationship("Product")
    