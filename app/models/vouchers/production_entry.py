# app/models/vouchers/production_entry.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase

class ProductionEntry(BaseVoucher):
    __tablename__ = "production_entries"
    
    production_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    shift = Column(String)
    machine = Column(String)
    operator = Column(String)
    batch_number = Column(String, nullable=False)
    actual_quantity = Column(Float, nullable=False)
    rejected_quantity = Column(Float, default=0.0)
    time_taken = Column(Float, nullable=False)
    labor_hours = Column(Float, nullable=False)
    machine_hours = Column(Float, nullable=False)
    power_consumption = Column(Float, default=0.0)
    downtime_events = Column(JSON)  # Store as JSON
    
    # Relationships
    production_order = relationship("ManufacturingOrder", back_populates="production_entries")
    bom_consumption = relationship("ProductionEntryConsumption", back_populates="production_entry", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pe_org_voucher_number'),
        Index('idx_pe_org_po', 'organization_id', 'production_order_id'),
        Index('idx_pe_org_date', 'organization_id', 'date'),
        {'extend_existing': True}
    )

class ProductionEntryConsumption(Base):
    __tablename__ = "production_entry_consumption"
    
    id = Column(Integer, primary_key=True, index=True)
    production_entry_id = Column(Integer, ForeignKey("production_entries.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    actual_qty = Column(Float, nullable=False)
    wastage_qty = Column(Float, default=0.0)
    
    component = relationship("Product")
    production_entry = relationship("ProductionEntry", back_populates="bom_consumption")
    __table_args__ = {'extend_existing': True}