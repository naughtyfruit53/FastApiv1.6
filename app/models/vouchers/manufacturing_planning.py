# app/models/vouchers/manufacturing_planning.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase

# Bill of Materials (BOM) Models
class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # BOM Details
    bom_name = Column(String, nullable=False)
    output_item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    output_quantity = Column(Float, nullable=False, default=1.0)
    version = Column(String, default="1.0")
    validity_start = Column(DateTime(timezone=True))
    validity_end = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Description and notes
    description = Column(Text)
    notes = Column(Text)
    
    # Costing information
    material_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    output_item = relationship("Product", foreign_keys=[output_item_id])
    components = relationship("BOMComponent", back_populates="bom", cascade="all, delete-orphan")
    created_by_user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'bom_name', 'version', name='uq_bom_org_name_version'),
        Index('idx_bom_org_output', 'organization_id', 'output_item_id'),
        Index('idx_bom_org_active', 'organization_id', 'is_active'),
        Index('idx_bom_org_created', 'organization_id', 'created_at'),
    )

class BOMComponent(Base):
    __tablename__ = "bom_components"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # BOM Reference
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    
    # Component Details
    component_item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_required = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    
    # Costing
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Production details
    wastage_percentage = Column(Float, default=0.0)  # Expected wastage
    is_optional = Column(Boolean, default=False)  # Optional component
    sequence = Column(Integer, default=0)  # Order in production
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    bom = relationship("BillOfMaterials", back_populates="components")
    component_item = relationship("Product", foreign_keys=[component_item_id])
    
    __table_args__ = (
        UniqueConstraint('bom_id', 'component_item_id', name='uq_bom_component_item'),
        Index('idx_bom_comp_org_bom', 'organization_id', 'bom_id'),
        Index('idx_bom_comp_org_item', 'organization_id', 'component_item_id'),
    )

# Manufacturing Order
class ManufacturingOrder(BaseVoucher):
    __tablename__ = "manufacturing_orders"
    
    # Production Details
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    planned_quantity = Column(Float, nullable=False)
    produced_quantity = Column(Float, default=0.0)
    scrap_quantity = Column(Float, default=0.0)
    
    # Planning
    planned_start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    
    # Status
    production_status = Column(String, default="planned")  # planned, in_progress, completed, cancelled
    priority = Column(String, default="medium")  # low, medium, high, urgent
    
    # Department/Location
    production_department = Column(String)
    production_location = Column(String)
    
    # Relationships
    bom = relationship("BillOfMaterials")
    material_issues = relationship("MaterialIssue", back_populates="manufacturing_order", cascade="all, delete-orphan")
    production_entries = relationship("ProductionEntry", back_populates="manufacturing_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mo_org_voucher_number'),
        Index('idx_mo_org_bom', 'organization_id', 'bom_id'),
        Index('idx_mo_org_status', 'organization_id', 'production_status'),
        Index('idx_mo_org_date', 'organization_id', 'date'),
    )