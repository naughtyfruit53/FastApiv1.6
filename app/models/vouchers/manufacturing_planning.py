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

class BOMAlternateComponent(Base):
    """Alternate components that can be used in place of primary component"""
    __tablename__ = "bom_alternate_components"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Reference to primary BOM component
    primary_component_id = Column(Integer, ForeignKey("bom_components.id"), nullable=False)
    
    # Alternate component details
    alternate_item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_required = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    
    # Costing
    unit_cost = Column(Float, default=0.0)
    cost_difference = Column(Float, default=0.0)  # Cost difference vs primary
    
    # Preferences
    preference_rank = Column(Integer, default=1)  # Lower number = higher preference
    is_preferred = Column(Boolean, default=False)
    
    # Conditions
    min_order_quantity = Column(Float, default=0.0)
    lead_time_days = Column(Integer, default=0)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    primary_component = relationship("BOMComponent", foreign_keys=[primary_component_id])
    alternate_item = relationship("Product", foreign_keys=[alternate_item_id])
    
    __table_args__ = (
        Index('idx_bom_alt_org_primary', 'organization_id', 'primary_component_id'),
        Index('idx_bom_alt_org_item', 'organization_id', 'alternate_item_id'),
    )

class BOMRevision(Base):
    """Track BOM revision history and engineering changes"""
    __tablename__ = "bom_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # BOM reference
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    
    # Revision details
    revision_number = Column(String, nullable=False)
    revision_date = Column(DateTime(timezone=True), server_default=func.now())
    previous_version = Column(String)
    new_version = Column(String, nullable=False)
    
    # Change details
    change_type = Column(String, nullable=False)  # 'component_add', 'component_remove', 'quantity_change', 'cost_change', 'other'
    change_description = Column(Text, nullable=False)
    change_reason = Column(Text)
    
    # Approval workflow
    change_requested_by = Column(Integer, ForeignKey("users.id"))
    change_approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    approval_status = Column(String, default="pending")  # 'pending', 'approved', 'rejected'
    
    # Impact assessment
    cost_impact = Column(Float, default=0.0)
    affected_orders_count = Column(Integer, default=0)
    implementation_date = Column(DateTime(timezone=True))
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bom = relationship("BillOfMaterials")
    requested_by_user = relationship("User", foreign_keys=[change_requested_by])
    approved_by_user = relationship("User", foreign_keys=[change_approved_by])
    
    __table_args__ = (
        Index('idx_bom_rev_org_bom', 'organization_id', 'bom_id'),
        Index('idx_bom_rev_org_date', 'organization_id', 'revision_date'),
        Index('idx_bom_rev_status', 'approval_status'),
    )

# Manufacturing Order - Enhanced with new fields for Production Entry
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
    
    # Priority
    priority = Column(String, default="medium")  # low, medium, high, urgent
    
    # Department/Location
    production_department = Column(String)
    production_location = Column(String)
    
    # Resource Allocation - NEW fields
    assigned_operator = Column(String)
    assigned_supervisor = Column(String)
    machine_id = Column(String)
    workstation_id = Column(String)
    estimated_labor_hours = Column(Float, default=0.0)
    actual_labor_hours = Column(Float, default=0.0)
    
    # Capacity Management
    estimated_setup_time = Column(Float, default=0.0)  # in hours
    estimated_run_time = Column(Float, default=0.0)  # in hours
    actual_setup_time = Column(Float, default=0.0)
    actual_run_time = Column(Float, default=0.0)
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # NEW: For Production Entry
    shift = Column(String)
    wastage_percentage = Column(Float, default=0.0)
    time_taken = Column(Float, default=0.0)  # Total time
    power_consumption = Column(Float, default=0.0)
    downtime_events = Column(Text)  # JSON string of events
    
    # NEW: Link to sales order
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    
    # NEW: Soft delete fields
    is_deleted = Column(Boolean, default=False, nullable=False)
    deletion_remark = Column(Text, nullable=True)
    
    # Relationships
    bom = relationship("BillOfMaterials")
    material_issues = relationship("MaterialIssue", back_populates="manufacturing_order", cascade="all, delete-orphan")
    production_entries = relationship("ProductionEntry", back_populates="manufacturing_order", cascade="all, delete-orphan")
    sales_order = relationship("SalesOrder")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mo_org_voucher_number'),
        Index('idx_mo_org_bom', 'organization_id', 'bom_id'),
        Index('idx_mo_org_status', 'organization_id', 'production_status'),
        Index('idx_mo_org_date', 'organization_id', 'date'),
        Index('idx_mo_deleted', 'is_deleted')  # NEW: Index for deleted
    )

# NEW: ProductionEntry Model
class ProductionEntry(Base):
    __tablename__ = "production_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    production_order_no = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    shift = Column(String)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    operator_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)  # Planned / In-progress / Completed / Rework
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    planned_quantity = Column(Float, nullable=False)
    actual_quantity = Column(Float, nullable=False)
    wastage_percentage = Column(Float, default=0.0)
    batch_number = Column(String, nullable=False)
    rejected_quantity = Column(Float, default=0.0)
    time_taken = Column(Float, nullable=False)
    labor_hours = Column(Float, nullable=False)
    machine_hours = Column(Float, nullable=False)
    power_consumption = Column(Float, default=0.0)
    downtime_events = Column(Text)  # JSON
    notes = Column(Text)
    attachments = Column(Text)  # JSON of file paths
    qc_approval = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="production_entries")
    machine = relationship("Machine")
    operator = relationship("User")
    product = relationship("Product")

    __table_args__ = {'extend_existing': True}

# NEW: Machine Model for Maintenance
class Machine(Base):
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_no = Column(String)
    supplier = Column(String)
    amc_details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    spare_parts = relationship("SparePart", back_populates="machine")
    preventive_schedules = relationship("PreventiveMaintenanceSchedule", back_populates="machine")
    breakdowns = relationship("BreakdownMaintenance", back_populates="machine")
    performance_logs = relationship("MachinePerformanceLog", back_populates="machine")

    __table_args__ = {'extend_existing': True}

# NEW: Preventive Maintenance Schedule
class PreventiveMaintenanceSchedule(Base):
    __tablename__ = "preventive_maintenance_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    frequency = Column(String, nullable=False)  # daily, weekly, etc.
    tasks = Column(Text, nullable=False)  # JSON checklist
    assigned_technician = Column(String)
    next_due_date = Column(DateTime(timezone=True))
    overdue = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="preventive_schedules")

    __table_args__ = {'extend_existing': True}

# NEW: Breakdown Maintenance
class BreakdownMaintenance(Base):
    __tablename__ = "breakdown_maintenances"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    breakdown_type = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    reported_by = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    time_to_fix = Column(Float)
    spare_parts_used = Column(Text)  # JSON list
    cost = Column(Float, default=0.0)
    downtime_hours = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="breakdowns")

    __table_args__ = {'extend_existing': True}

# NEW: Machine Performance Log
class MachinePerformanceLog(Base):
    __tablename__ = "machine_performance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    runtime_hours = Column(Float, default=0.0)
    idle_hours = Column(Float, default=0.0)
    efficiency_percentage = Column(Float, default=0.0)
    error_codes = Column(Text)  # JSON list
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="performance_logs")

    __table_args__ = {'extend_existing': True}

# NEW: Spare Part
class SparePart(Base):
    __tablename__ = "spare_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    quantity = Column(Float, nullable=False)
    min_level = Column(Float, default=0.0)
    reorder_level = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="spare_parts")

    __table_args__ = {'extend_existing': True}

# NEW: QC Template
class QCTemplate(Base):
    __tablename__ = "qc_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    test_name = Column(String, nullable=False)
    tolerance_min = Column(Float)
    tolerance_max = Column(Float)
    unit = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product")

    __table_args__ = {'extend_existing': True}

# NEW: QC Inspection
class QCInspection(Base):
    __tablename__ = "qc_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    batch_id = Column(Integer, nullable=False)  # Link to batch
    inspector = Column(String, nullable=False)
    test_results = Column(Text, nullable=False)  # JSON of tests
    overall_status = Column(String, nullable=False)  # pass/fail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = {'extend_existing': True}

# NEW: Rejection
class Rejection(Base):
    __tablename__ = "rejections"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    qc_inspection_id = Column(Integer, ForeignKey("qc_inspections.id"), nullable=False)
    reason = Column(Text, nullable=False)
    rework_required = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    qc_inspection = relationship("QCInspection")

    __table_args__ = {'extend_existing': True}

# NEW: Inventory Adjustment
class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # increase, decrease, etc.
    item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_number = Column(String)
    old_quantity = Column(Float, nullable=False)
    new_quantity = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    documents = Column(Text)  # JSON paths
    approved_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    item = relationship("Product")

    __table_args__ = {'extend_existing': True}