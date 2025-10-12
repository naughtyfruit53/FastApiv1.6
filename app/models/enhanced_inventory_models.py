# app/models/enhanced_inventory_models.py
"""
Enhanced Inventory Models - Batch/Serial tracking, Warehouse management
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class TrackingType(enum.Enum):
    """Inventory tracking type"""
    NONE = "none"
    BATCH = "batch"
    SERIAL = "serial"
    BATCH_AND_SERIAL = "batch_and_serial"


class InventoryValuationMethod(enum.Enum):
    """Inventory valuation methods"""
    FIFO = "fifo"
    LIFO = "lifo"
    WEIGHTED_AVERAGE = "weighted_average"
    STANDARD_COST = "standard_cost"


class StockMovementType(enum.Enum):
    """Stock movement types"""
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    OBSOLETE = "obsolete"


class WarehouseType(enum.Enum):
    """Warehouse types"""
    MAIN = "main"
    BRANCH = "branch"
    VIRTUAL = "virtual"
    TRANSIT = "transit"
    QUARANTINE = "quarantine"


class AlertType(enum.Enum):
    """Inventory alert types"""
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    SHORTAGE_FOR_MO = "shortage_for_mo"
    OVERSTOCK = "overstock"
    EXPIRY_ALERT = "expiry_alert"


class AlertStatus(enum.Enum):
    """Inventory alert statuses"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertPriority(enum.Enum):
    """Inventory alert priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Warehouse(Base):
    """Warehouse/Location management"""
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Warehouse identification
    warehouse_code = Column(String(50), nullable=False, index=True)
    warehouse_name = Column(String(200), nullable=False)
    warehouse_type = Column(Enum(WarehouseType), default=WarehouseType.MAIN, nullable=False)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India", nullable=False)
    
    # Contact details
    contact_person = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    allow_negative_stock = Column(Boolean, default=False, nullable=False)
    is_main_warehouse = Column(Boolean, default=False, nullable=False)
    
    # Capacity
    total_area_sqft = Column(Numeric(10, 2), nullable=True)
    storage_capacity_units = Column(Numeric(15, 3), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="warehouses")
    stock_locations = relationship("StockLocation", back_populates="warehouse", cascade="all, delete-orphan")
    warehouse_stock = relationship("WarehouseStock", back_populates="warehouse")
    stock_movements = relationship("StockMovement", back_populates="warehouse")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'warehouse_code', name='uq_org_warehouse_code'),
        Index('idx_warehouse_type', 'warehouse_type'),
        {'extend_existing': True}
    )


class StockLocation(Base):
    """Stock locations within warehouses (bins, racks, etc.)"""
    __tablename__ = "stock_locations"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    
    # Location identification
    location_code = Column(String(50), nullable=False, index=True)
    location_name = Column(String(200), nullable=False)
    location_type = Column(String(50), nullable=True)  # Rack, Bin, Floor, etc.
    
    # Hierarchy (for nested locations)
    parent_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True, index=True)
    
    # Physical attributes
    row_number = Column(String(10), nullable=True)
    column_number = Column(String(10), nullable=True)
    level_number = Column(String(10), nullable=True)
    
    # Capacity
    max_capacity_units = Column(Numeric(12, 3), nullable=True)
    max_weight_kg = Column(Numeric(10, 2), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_pickable = Column(Boolean, default=True, nullable=False)
    is_receivable = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="stock_locations")
    parent_location = relationship("StockLocation", remote_side=[id], back_populates="sub_locations")
    sub_locations = relationship("StockLocation", back_populates="parent_location")
    batch_locations = relationship("BatchLocation", back_populates="stock_location")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'location_code', name='uq_warehouse_location_code'),
        {'extend_existing': True}
    )


class ProductTracking(Base):
    """Product tracking configuration"""
    __tablename__ = "product_tracking"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True, index=True)
    
    # Tracking configuration
    tracking_type = Column(Enum(TrackingType), default=TrackingType.NONE, nullable=False)
    valuation_method = Column(Enum(InventoryValuationMethod), default=InventoryValuationMethod.WEIGHTED_AVERAGE, nullable=False)
    
    # Batch configuration
    batch_naming_series = Column(String(50), nullable=True)  # e.g., "BATCH-.YYYY.-.####"
    auto_create_batch = Column(Boolean, default=False, nullable=False)
    batch_expiry_required = Column(Boolean, default=False, nullable=False)
    
    # Serial configuration
    serial_naming_series = Column(String(50), nullable=True)  # e.g., "SRL-.YYYY.-.#####"
    auto_create_serial = Column(Boolean, default=False, nullable=False)
    
    # Reorder configuration
    enable_reorder_alert = Column(Boolean, default=True, nullable=False)
    reorder_level = Column(Numeric(12, 3), nullable=True)
    reorder_quantity = Column(Numeric(12, 3), nullable=True)
    max_stock_level = Column(Numeric(12, 3), nullable=True)
    
    # Lead time
    procurement_lead_time_days = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="tracking_config")
    batches = relationship("ProductBatch", back_populates="product_tracking")
    serials = relationship("ProductSerial", back_populates="product_tracking")

    # Constraints
    __table_args__ = {'extend_existing': True}


class WarehouseStock(Base):
    """Warehouse-wise stock levels"""
    __tablename__ = "warehouse_stock"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Stock quantities
    available_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)
    committed_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)  # Reserved for orders
    on_order_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)  # Purchase orders
    
    # Calculated fields
    free_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)  # Available - Committed
    total_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)  # Available + On Order
    
    # Valuation
    average_cost = Column(Numeric(15, 2), default=0.00, nullable=False)
    total_value = Column(Numeric(15, 2), default=0.00, nullable=False)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_movement_date = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="warehouse_stock")
    warehouse = relationship("Warehouse", back_populates="warehouse_stock")
    product = relationship("Product", back_populates="warehouse_stock")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'product_id', name='uq_warehouse_product_stock'),
        Index('idx_warehouse_stock_org_warehouse', 'organization_id', 'warehouse_id'),
        {'extend_existing': True}
    )


class ProductBatch(Base):
    """Product batch information"""
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    product_tracking_id = Column(Integer, ForeignKey("product_tracking.id"), nullable=False, index=True)
    
    # Batch identification
    batch_number = Column(String(100), nullable=False, index=True)
    batch_name = Column(String(200), nullable=True)
    
    # Manufacturing details
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    
    # Supplier details
    supplier_batch_number = Column(String(100), nullable=True)
    supplier_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    
    # Quality attributes
    quality_grade = Column(String(50), nullable=True)
    quality_notes = Column(Text, nullable=True)
    
    # Stock quantity for this batch
    batch_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)
    available_quantity = Column(Numeric(12, 3), default=0.000, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="product_batches")
    product_tracking = relationship("ProductTracking", back_populates="batches")
    supplier = relationship("Vendor", back_populates="product_batches")
    batch_locations = relationship("BatchLocation", back_populates="batch")
    serial_numbers = relationship("ProductSerial", back_populates="batch")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'batch_number', name='uq_org_batch_number'),
        Index('idx_batch_expiry', 'expiry_date'),
        Index('idx_batch_active', 'is_active'),
        {'extend_existing': True}
    )


class ProductSerial(Base):
    """Product serial number tracking"""
    __tablename__ = "product_serials"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    product_tracking_id = Column(Integer, ForeignKey("product_tracking.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True, index=True)
    
    # Serial identification
    serial_number = Column(String(100), nullable=False, index=True)
    
    # Manufacturing details
    manufacturing_date = Column(Date, nullable=True)
    warranty_expiry_date = Column(Date, nullable=True)
    
    # Supplier details
    supplier_serial_number = Column(String(100), nullable=True)
    supplier_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    
    # Current status
    current_status = Column(String(20), default="available", nullable=False, index=True)  # available, sold, defective, returned
    current_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True, index=True)
    current_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True, index=True)
    
    # Customer assignment (if sold)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    sale_date = Column(Date, nullable=True)
    sale_invoice_number = Column(String(100), nullable=True)
    
    # Quality attributes
    quality_grade = Column(String(50), nullable=True)
    quality_notes = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="product_serials")
    product_tracking = relationship("ProductTracking", back_populates="serials")
    batch = relationship("ProductBatch", back_populates="serial_numbers")
    supplier = relationship("Vendor", back_populates="product_serials")
    current_warehouse = relationship("Warehouse", foreign_keys=[current_warehouse_id])
    current_location = relationship("StockLocation", foreign_keys=[current_location_id])
    customer = relationship("Customer", back_populates="product_serials")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'serial_number', name='uq_org_serial_number'),
        Index('idx_serial_status', 'current_status'),
        Index('idx_serial_warranty', 'warranty_expiry_date'),
        {'extend_existing': True}
    )


class BatchLocation(Base):
    """Batch-wise location tracking"""
    __tablename__ = "batch_locations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=False, index=True)
    stock_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False, index=True)
    
    # Quantity at this location
    quantity = Column(Numeric(12, 3), nullable=False)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    batch = relationship("ProductBatch", back_populates="batch_locations")
    stock_location = relationship("StockLocation", back_populates="batch_locations")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('batch_id', 'stock_location_id', name='uq_batch_location'),
        {'extend_existing': True}
    )


class StockMovement(Base):
    """Enhanced stock movement tracking"""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Movement details
    movement_type = Column(Enum(StockMovementType), nullable=False, index=True)
    movement_date = Column(DateTime, nullable=False, index=True)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Quantities
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_cost = Column(Numeric(15, 2), nullable=True)
    total_value = Column(Numeric(15, 2), nullable=True)
    
    # Batch/Serial details
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True, index=True)
    serial_numbers = Column(JSON, nullable=True)  # Array of serial numbers for this movement
    
    # Location details
    from_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True, index=True)
    to_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True, index=True)
    
    # Reference to source document
    source_document_type = Column(String(50), nullable=True, index=True)
    source_document_id = Column(Integer, nullable=True, index=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="stock_movements")
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")
    batch = relationship("ProductBatch")
    from_location = relationship("StockLocation", foreign_keys=[from_location_id])
    to_location = relationship("StockLocation", foreign_keys=[to_location_id])
    
    # Constraints
    __table_args__ = (
        Index('idx_stock_movement_org_date', 'organization_id', 'movement_date'),
        Index('idx_stock_movement_type', 'movement_type'),
        {'extend_existing': True}
    )


class StockAdjustment(Base):
    """Stock adjustment entries"""
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Adjustment details
    adjustment_number = Column(String(50), nullable=False, unique=True, index=True)
    adjustment_date = Column(Date, nullable=False, index=True)
    adjustment_type = Column(String(50), nullable=False, index=True)  # physical_count, damage, obsolete, etc.
    
    # Approval workflow
    status = Column(String(20), default="draft", nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Reason
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("platform_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="stock_adjustments")
    adjustment_items = relationship("StockAdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index('idx_stock_adj_org_status', 'organization_id', 'status'),
        {'extend_existing': True}
    )


class StockAdjustmentItem(Base):
    """Stock adjustment item details"""
    __tablename__ = "stock_adjustment_items"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_id = Column(Integer, ForeignKey("stock_adjustments.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Quantities
    book_quantity = Column(Numeric(12, 3), nullable=False)  # System quantity
    physical_quantity = Column(Numeric(12, 3), nullable=False)  # Actual quantity
    adjustment_quantity = Column(Numeric(12, 3), nullable=False)  # Difference
    
    # Valuation
    unit_cost = Column(Numeric(15, 2), nullable=False)
    adjustment_value = Column(Numeric(15, 2), nullable=False)
    
    # Batch/Serial details
    batch_id = Column(Integer, ForeignKey("product_batches.id"), nullable=True, index=True)
    serial_numbers = Column(JSON, nullable=True)  # Array of affected serial numbers
    
    # Metadata
    notes = Column(Text, nullable=True)

    # Relationships
    adjustment = relationship("StockAdjustment", back_populates="adjustment_items")
    warehouse = relationship("Warehouse")
    product = relationship("Product")
    batch = relationship("ProductBatch")

    # Constraints
    __table_args__ = {'extend_existing': True}


class InventoryAlert(Base):
    """Inventory alerts for shortages, low stock, etc."""
    __tablename__ = "inventory_alerts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    current_stock = Column(Numeric(12, 3), nullable=False)
    reorder_level = Column(Numeric(12, 3), nullable=False)
    priority = Column(Enum(AlertPriority), nullable=False)
    message = Column(Text, nullable=False)
    suggested_order_quantity = Column(Numeric(12, 3), nullable=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships with overlaps to silence warnings
    organization = relationship("Organization", overlaps="organization")
    product = relationship("Product", overlaps="product")

    # Constraints
    __table_args__ = (
        Index('idx_alert_org_type_status', 'organization_id', 'alert_type', 'status'),
        {'extend_existing': True}
    )