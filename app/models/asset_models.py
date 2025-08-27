# app/models/asset_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AssetStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    DISPOSED = "disposed"

class AssetCondition(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class MaintenanceType(enum.Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"

class MaintenanceStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class DepreciationMethod(enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"
    SUM_OF_YEARS = "sum_of_years"

# Asset Master Data
class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Asset Identification
    asset_code = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)  # Equipment, Vehicle, Building, IT, etc.
    subcategory = Column(String)
    
    # Physical Details
    manufacturer = Column(String)
    model = Column(String)
    serial_number = Column(String)
    year_of_manufacture = Column(Integer)
    
    # Financial Information
    purchase_cost = Column(Float, default=0.0)
    purchase_date = Column(DateTime(timezone=True))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    warranty_start_date = Column(DateTime(timezone=True))
    warranty_end_date = Column(DateTime(timezone=True))
    
    # Location and Assignment
    location = Column(String)
    department = Column(String)
    assigned_to_employee = Column(String)
    
    # Status and Condition
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False)
    condition = Column(Enum(AssetCondition), default=AssetCondition.GOOD, nullable=False)
    last_inspection_date = Column(DateTime(timezone=True))
    next_inspection_date = Column(DateTime(timezone=True))
    
    # Specifications
    specifications = Column(Text)  # JSON or structured data
    operating_capacity = Column(String)
    power_rating = Column(String)
    
    # Depreciation
    depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    useful_life_years = Column(Integer)
    salvage_value = Column(Float, default=0.0)
    depreciation_rate = Column(Float)  # Percentage
    
    # Insurance
    insurance_provider = Column(String)
    insurance_policy_number = Column(String)
    insurance_expiry_date = Column(DateTime(timezone=True))
    
    # Notes and attachments
    notes = Column(Text)
    photo_path = Column(String)
    document_path = Column(String)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    vendor = relationship("Vendor")
    created_by_user = relationship("User")
    maintenance_schedules = relationship("MaintenanceSchedule", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset", cascade="all, delete-orphan")
    depreciation_records = relationship("DepreciationRecord", back_populates="asset", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'asset_code', name='uq_asset_org_code'),
        Index('idx_asset_org_category', 'organization_id', 'category'),
        Index('idx_asset_org_status', 'organization_id', 'status'),
        Index('idx_asset_org_location', 'organization_id', 'location'),
        Index('idx_asset_org_created', 'organization_id', 'created_at'),
    )

# Maintenance Scheduling
class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Asset Reference
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Schedule Details
    schedule_name = Column(String, nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(Text)
    
    # Frequency and Timing
    frequency_type = Column(String, nullable=False)  # daily, weekly, monthly, quarterly, yearly, mileage, hours
    frequency_value = Column(Integer)  # Every X units
    estimated_duration_hours = Column(Float)
    
    # Next due calculation
    last_maintenance_date = Column(DateTime(timezone=True))
    next_due_date = Column(DateTime(timezone=True))
    
    # Meter-based scheduling
    meter_type = Column(String)  # hours, kilometers, cycles, etc.
    meter_frequency = Column(Float)  # Every X meter units
    last_meter_reading = Column(Float)
    next_meter_due = Column(Float)
    
    # Cost and Resources
    estimated_cost = Column(Float, default=0.0)
    required_skills = Column(Text)
    required_parts = Column(Text)  # JSON list
    
    # Assignment
    assigned_technician = Column(String)
    assigned_department = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    
    # Notifications
    advance_notice_days = Column(Integer, default=7)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_schedules")
    created_by_user = relationship("User")
    maintenance_records = relationship("MaintenanceRecord", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_maint_sched_org_asset', 'organization_id', 'asset_id'),
        Index('idx_maint_sched_org_due', 'organization_id', 'next_due_date'),
        Index('idx_maint_sched_org_type', 'organization_id', 'maintenance_type'),
        Index('idx_maint_sched_org_active', 'organization_id', 'is_active'),
    )

# Maintenance Records
class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Asset and Schedule References
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("maintenance_schedules.id"))
    
    # Work Order Details
    work_order_number = Column(String, nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    priority = Column(String, default="medium")
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    
    # Work Description
    description = Column(Text, nullable=False)
    work_performed = Column(Text)
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Personnel
    assigned_technician = Column(String)
    performed_by = Column(String)
    supervised_by = Column(String)
    
    # Status
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, nullable=False)
    
    # Costs
    labor_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    external_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Meter Readings
    meter_reading_before = Column(Float)
    meter_reading_after = Column(Float)
    
    # Quality and Safety
    safety_incidents = Column(Text)
    quality_check_passed = Column(Boolean, default=True)
    quality_remarks = Column(Text)
    
    # Asset Condition Update
    condition_before = Column(Enum(AssetCondition))
    condition_after = Column(Enum(AssetCondition))
    
    # Documentation
    photos_path = Column(String)
    documents_path = Column(String)
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    schedule = relationship("MaintenanceSchedule", back_populates="maintenance_records")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    created_by_user = relationship("User", foreign_keys=[created_by])
    parts_used = relationship("MaintenancePartUsed", back_populates="maintenance_record", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'work_order_number', name='uq_maint_rec_org_wo'),
        Index('idx_maint_rec_org_asset', 'organization_id', 'asset_id'),
        Index('idx_maint_rec_org_status', 'organization_id', 'status'),
        Index('idx_maint_rec_org_date', 'organization_id', 'scheduled_date'),
        Index('idx_maint_rec_org_type', 'organization_id', 'maintenance_type'),
    )

# Parts Used in Maintenance
class MaintenancePartUsed(Base):
    __tablename__ = "maintenance_parts_used"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # References
    maintenance_record_id = Column(Integer, ForeignKey("maintenance_records.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Usage Details
    quantity_used = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Tracking
    batch_number = Column(String)
    serial_number = Column(String)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    maintenance_record = relationship("MaintenanceRecord", back_populates="parts_used")
    product = relationship("Product")
    
    __table_args__ = (
        Index('idx_maint_parts_org_record', 'organization_id', 'maintenance_record_id'),
        Index('idx_maint_parts_org_product', 'organization_id', 'product_id'),
    )

# Asset Depreciation
class DepreciationRecord(Base):
    __tablename__ = "depreciation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Asset Reference
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Period
    depreciation_year = Column(Integer, nullable=False)
    depreciation_month = Column(Integer)  # Optional for monthly depreciation
    period_start_date = Column(DateTime(timezone=True), nullable=False)
    period_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Depreciation Calculation
    opening_book_value = Column(Float, nullable=False)
    depreciation_amount = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    closing_book_value = Column(Float, nullable=False)
    
    # Method Details
    depreciation_method = Column(Enum(DepreciationMethod), nullable=False)
    depreciation_rate = Column(Float)  # Percentage
    
    # Usage-based depreciation
    usage_units = Column(Float)  # For units of production method
    
    # Status
    is_finalized = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("Asset", back_populates="depreciation_records")
    created_by_user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('asset_id', 'depreciation_year', 'depreciation_month', 
                        name='uq_depr_asset_year_month'),
        Index('idx_depr_org_asset', 'organization_id', 'asset_id'),
        Index('idx_depr_org_period', 'organization_id', 'period_start_date'),
        Index('idx_depr_org_year', 'organization_id', 'depreciation_year'),
    )