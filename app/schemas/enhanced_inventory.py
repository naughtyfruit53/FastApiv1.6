# app/schemas/enhanced_inventory.py
"""
Enhanced Inventory Schemas - Batch/Serial tracking, Warehouse management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class TrackingTypeEnum(str, Enum):
    """Inventory tracking type"""
    NONE = "none"
    BATCH = "batch"
    SERIAL = "serial"
    BATCH_AND_SERIAL = "batch_and_serial"


class InventoryValuationMethodEnum(str, Enum):
    """Inventory valuation methods"""
    FIFO = "fifo"
    LIFO = "lifo"
    WEIGHTED_AVERAGE = "weighted_average"
    STANDARD_COST = "standard_cost"


class StockMovementTypeEnum(str, Enum):
    """Stock movement types"""
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    OBSOLETE = "obsolete"


class WarehouseTypeEnum(str, Enum):
    """Warehouse types"""
    MAIN = "main"
    BRANCH = "branch"
    VIRTUAL = "virtual"
    TRANSIT = "transit"
    QUARANTINE = "quarantine"


# Warehouse Schemas
class WarehouseBase(BaseModel):
    warehouse_code: str = Field(..., description="Warehouse code")
    warehouse_name: str = Field(..., description="Warehouse name")
    warehouse_type: WarehouseTypeEnum = Field(WarehouseTypeEnum.MAIN, description="Warehouse type")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    pincode: Optional[str] = Field(None, description="Pincode")
    country: str = Field("India", description="Country")
    contact_person: Optional[str] = Field(None, description="Contact person")
    phone_number: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email")
    allow_negative_stock: bool = Field(False, description="Allow negative stock")
    is_main_warehouse: bool = Field(False, description="Is main warehouse")
    total_area_sqft: Optional[Decimal] = Field(None, description="Total area in sq ft")
    storage_capacity_units: Optional[Decimal] = Field(None, description="Storage capacity in units")
    notes: Optional[str] = Field(None, description="Notes")


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    warehouse_name: Optional[str] = None
    warehouse_type: Optional[WarehouseTypeEnum] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    allow_negative_stock: Optional[bool] = None
    is_main_warehouse: Optional[bool] = None
    total_area_sqft: Optional[Decimal] = None
    storage_capacity_units: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Stock Location Schemas
class StockLocationBase(BaseModel):
    location_code: str = Field(..., description="Location code")
    location_name: str = Field(..., description="Location name")
    location_type: Optional[str] = Field(None, description="Location type")
    parent_location_id: Optional[int] = Field(None, description="Parent location ID")
    row_number: Optional[str] = Field(None, description="Row number")
    column_number: Optional[str] = Field(None, description="Column number")
    level_number: Optional[str] = Field(None, description="Level number")
    max_capacity_units: Optional[Decimal] = Field(None, description="Max capacity in units")
    max_weight_kg: Optional[Decimal] = Field(None, description="Max weight in kg")
    is_pickable: bool = Field(True, description="Is pickable")
    is_receivable: bool = Field(True, description="Is receivable")
    notes: Optional[str] = Field(None, description="Notes")


class StockLocationCreate(StockLocationBase):
    warehouse_id: int = Field(..., description="Warehouse ID")


class StockLocationUpdate(BaseModel):
    location_name: Optional[str] = None
    location_type: Optional[str] = None
    parent_location_id: Optional[int] = None
    row_number: Optional[str] = None
    column_number: Optional[str] = None
    level_number: Optional[str] = None
    max_capacity_units: Optional[Decimal] = None
    max_weight_kg: Optional[Decimal] = None
    is_pickable: Optional[bool] = None
    is_receivable: Optional[bool] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StockLocationResponse(StockLocationBase):
    id: int
    warehouse_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Product Tracking Schemas
class ProductTrackingBase(BaseModel):
    tracking_type: TrackingTypeEnum = Field(TrackingTypeEnum.NONE, description="Tracking type")
    valuation_method: InventoryValuationMethodEnum = Field(InventoryValuationMethodEnum.WEIGHTED_AVERAGE, description="Valuation method")
    batch_naming_series: Optional[str] = Field(None, description="Batch naming series")
    auto_create_batch: bool = Field(False, description="Auto create batch")
    batch_expiry_required: bool = Field(False, description="Batch expiry required")
    serial_naming_series: Optional[str] = Field(None, description="Serial naming series")
    auto_create_serial: bool = Field(False, description="Auto create serial")
    enable_reorder_alert: bool = Field(True, description="Enable reorder alert")
    reorder_level: Optional[Decimal] = Field(None, description="Reorder level")
    reorder_quantity: Optional[Decimal] = Field(None, description="Reorder quantity")
    max_stock_level: Optional[Decimal] = Field(None, description="Max stock level")
    procurement_lead_time_days: Optional[int] = Field(None, description="Procurement lead time in days")


class ProductTrackingCreate(ProductTrackingBase):
    product_id: int = Field(..., description="Product ID")


class ProductTrackingUpdate(BaseModel):
    tracking_type: Optional[TrackingTypeEnum] = None
    valuation_method: Optional[InventoryValuationMethodEnum] = None
    batch_naming_series: Optional[str] = None
    auto_create_batch: Optional[bool] = None
    batch_expiry_required: Optional[bool] = None
    serial_naming_series: Optional[str] = None
    auto_create_serial: Optional[bool] = None
    enable_reorder_alert: Optional[bool] = None
    reorder_level: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    max_stock_level: Optional[Decimal] = None
    procurement_lead_time_days: Optional[int] = None


class ProductTrackingResponse(ProductTrackingBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Warehouse Stock Schemas
class WarehouseStockBase(BaseModel):
    warehouse_id: int = Field(..., description="Warehouse ID")
    product_id: int = Field(..., description="Product ID")
    available_quantity: Decimal = Field(0.000, description="Available quantity")
    committed_quantity: Decimal = Field(0.000, description="Committed quantity")
    on_order_quantity: Decimal = Field(0.000, description="On order quantity")


class WarehouseStockUpdate(BaseModel):
    available_quantity: Optional[Decimal] = None
    committed_quantity: Optional[Decimal] = None
    on_order_quantity: Optional[Decimal] = None


class WarehouseStockResponse(WarehouseStockBase):
    id: int
    organization_id: int
    free_quantity: Decimal
    total_quantity: Decimal
    average_cost: Decimal
    total_value: Decimal
    last_updated: datetime
    last_movement_date: Optional[datetime]
    
    class Config:
        from_attributes = True


# Product Batch Schemas
class ProductBatchBase(BaseModel):
    batch_number: str = Field(..., description="Batch number")
    batch_name: Optional[str] = Field(None, description="Batch name")
    manufacturing_date: Optional[date] = Field(None, description="Manufacturing date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    supplier_batch_number: Optional[str] = Field(None, description="Supplier batch number")
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    quality_grade: Optional[str] = Field(None, description="Quality grade")
    quality_notes: Optional[str] = Field(None, description="Quality notes")
    batch_quantity: Decimal = Field(0.000, description="Batch quantity")


class ProductBatchCreate(ProductBatchBase):
    product_tracking_id: int = Field(..., description="Product tracking ID")


class ProductBatchUpdate(BaseModel):
    batch_name: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    supplier_batch_number: Optional[str] = None
    supplier_id: Optional[int] = None
    quality_grade: Optional[str] = None
    quality_notes: Optional[str] = None
    batch_quantity: Optional[Decimal] = None
    available_quantity: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_expired: Optional[bool] = None


class ProductBatchResponse(ProductBatchBase):
    id: int
    organization_id: int
    product_tracking_id: int
    available_quantity: Decimal
    is_active: bool
    is_expired: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Product Serial Schemas
class ProductSerialBase(BaseModel):
    serial_number: str = Field(..., description="Serial number")
    manufacturing_date: Optional[date] = Field(None, description="Manufacturing date")
    warranty_expiry_date: Optional[date] = Field(None, description="Warranty expiry date")
    supplier_serial_number: Optional[str] = Field(None, description="Supplier serial number")
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    current_status: str = Field("available", description="Current status")
    current_warehouse_id: Optional[int] = Field(None, description="Current warehouse ID")
    current_location_id: Optional[int] = Field(None, description="Current location ID")
    customer_id: Optional[int] = Field(None, description="Customer ID (if sold)")
    sale_date: Optional[date] = Field(None, description="Sale date")
    sale_invoice_number: Optional[str] = Field(None, description="Sale invoice number")
    quality_grade: Optional[str] = Field(None, description="Quality grade")
    quality_notes: Optional[str] = Field(None, description="Quality notes")
    notes: Optional[str] = Field(None, description="Notes")


class ProductSerialCreate(ProductSerialBase):
    product_tracking_id: int = Field(..., description="Product tracking ID")
    batch_id: Optional[int] = Field(None, description="Batch ID")


class ProductSerialUpdate(BaseModel):
    manufacturing_date: Optional[date] = None
    warranty_expiry_date: Optional[date] = None
    supplier_serial_number: Optional[str] = None
    supplier_id: Optional[int] = None
    current_status: Optional[str] = None
    current_warehouse_id: Optional[int] = None
    current_location_id: Optional[int] = None
    customer_id: Optional[int] = None
    sale_date: Optional[date] = None
    sale_invoice_number: Optional[str] = None
    quality_grade: Optional[str] = None
    quality_notes: Optional[str] = None
    notes: Optional[str] = None


class ProductSerialResponse(ProductSerialBase):
    id: int
    organization_id: int
    product_tracking_id: int
    batch_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Stock Movement Schemas
class StockMovementBase(BaseModel):
    warehouse_id: int = Field(..., description="Warehouse ID")
    product_id: int = Field(..., description="Product ID")
    movement_type: StockMovementTypeEnum = Field(..., description="Movement type")
    movement_date: datetime = Field(..., description="Movement date")
    reference_number: Optional[str] = Field(None, description="Reference number")
    quantity: Decimal = Field(..., description="Quantity")
    unit_cost: Optional[Decimal] = Field(None, description="Unit cost")
    total_value: Optional[Decimal] = Field(None, description="Total value")
    batch_id: Optional[int] = Field(None, description="Batch ID")
    serial_numbers: Optional[List[str]] = Field(None, description="Serial numbers")
    from_location_id: Optional[int] = Field(None, description="From location ID")
    to_location_id: Optional[int] = Field(None, description="To location ID")
    source_document_type: Optional[str] = Field(None, description="Source document type")
    source_document_id: Optional[int] = Field(None, description="Source document ID")
    notes: Optional[str] = Field(None, description="Notes")


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementResponse(StockMovementBase):
    id: int
    organization_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Stock Adjustment Schemas
class StockAdjustmentItemBase(BaseModel):
    warehouse_id: int = Field(..., description="Warehouse ID")
    product_id: int = Field(..., description="Product ID")
    book_quantity: Decimal = Field(..., description="Book quantity")
    physical_quantity: Decimal = Field(..., description="Physical quantity")
    adjustment_quantity: Decimal = Field(..., description="Adjustment quantity")
    unit_cost: Decimal = Field(..., description="Unit cost")
    adjustment_value: Decimal = Field(..., description="Adjustment value")
    batch_id: Optional[int] = Field(None, description="Batch ID")
    serial_numbers: Optional[List[str]] = Field(None, description="Serial numbers")
    notes: Optional[str] = Field(None, description="Notes")


class StockAdjustmentItemCreate(StockAdjustmentItemBase):
    pass


class StockAdjustmentItemResponse(StockAdjustmentItemBase):
    id: int
    adjustment_id: int
    
    class Config:
        from_attributes = True


class StockAdjustmentBase(BaseModel):
    adjustment_date: date = Field(..., description="Adjustment date")
    adjustment_type: str = Field(..., description="Adjustment type")
    reason: str = Field(..., description="Reason")
    notes: Optional[str] = Field(None, description="Notes")


class StockAdjustmentCreate(StockAdjustmentBase):
    adjustment_items: List[StockAdjustmentItemCreate] = Field(..., description="Adjustment items")


class StockAdjustmentUpdate(BaseModel):
    adjustment_date: Optional[date] = None
    adjustment_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class StockAdjustmentResponse(StockAdjustmentBase):
    id: int
    organization_id: int
    adjustment_number: str
    status: str
    approved_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    adjustment_items: List[StockAdjustmentItemResponse] = []
    
    class Config:
        from_attributes = True


# Enhanced Inventory Analytics Schemas
class InventoryTurnoverAnalysis(BaseModel):
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    opening_stock: Decimal
    closing_stock: Decimal
    total_issues: Decimal
    average_stock: Decimal
    turnover_ratio: Optional[Decimal]
    days_in_stock: Optional[int]


class StockAgingAnalysis(BaseModel):
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    batch_id: Optional[int]
    batch_number: Optional[str]
    quantity: Decimal
    value: Decimal
    age_days: int
    age_category: str  # 0-30, 31-60, 61-90, 90+


class LowStockAlert(BaseModel):
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    current_stock: Decimal
    reorder_level: Decimal
    suggested_order_quantity: Decimal
    lead_time_days: Optional[int]
    last_movement_date: Optional[datetime]


class ExpiryAlert(BaseModel):
    product_id: int
    product_name: str
    batch_id: int
    batch_number: str
    expiry_date: date
    days_to_expiry: int
    quantity: Decimal
    value: Decimal
    urgency_level: str  # critical, warning, info


class InventoryValuationReport(BaseModel):
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    quantity: Decimal
    average_cost: Decimal
    total_value: Decimal
    valuation_method: InventoryValuationMethodEnum
    last_updated: datetime


class WarehouseUtilization(BaseModel):
    warehouse_id: int
    warehouse_name: str
    total_capacity: Optional[Decimal]
    utilized_capacity: Decimal
    utilization_percentage: Optional[Decimal]
    total_products: int
    total_value: Decimal


class InventoryDashboard(BaseModel):
    total_products: int
    total_warehouses: int
    total_stock_value: Decimal
    low_stock_alerts: int
    expiry_alerts: int
    recent_movements: int
    top_moving_products: List[InventoryTurnoverAnalysis]
    warehouse_utilization: List[WarehouseUtilization]
    organization_id: int
    as_of_date: datetime


# Batch and Serial Tracking Schemas
class BatchLocationBase(BaseModel):
    batch_id: int = Field(..., description="Batch ID")
    stock_location_id: int = Field(..., description="Stock location ID")
    quantity: Decimal = Field(..., description="Quantity")


class BatchLocationResponse(BatchLocationBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BatchTrackingReport(BaseModel):
    batch_id: int
    batch_number: str
    product_id: int
    product_name: str
    manufacturing_date: Optional[date]
    expiry_date: Optional[date]
    total_quantity: Decimal
    available_quantity: Decimal
    locations: List[BatchLocationResponse]
    movements: List[StockMovementResponse]


class SerialTrackingReport(BaseModel):
    serial_number: str
    product_id: int
    product_name: str
    batch_number: Optional[str]
    current_status: str
    current_location: Optional[str]
    customer_name: Optional[str]
    warranty_status: str
    movement_history: List[StockMovementResponse]


# Import/Export Schemas
class BulkStockImport(BaseModel):
    warehouse_id: int = Field(..., description="Warehouse ID")
    import_data: List[Dict[str, Any]] = Field(..., description="Import data")
    import_type: str = Field(..., description="Import type (stock_levels, adjustments)")
    validate_only: bool = Field(False, description="Validate only, don't import")


class BulkImportResponse(BaseModel):
    success: bool = Field(..., description="Import successful")
    total_records: int = Field(..., description="Total records")
    successful_records: int = Field(..., description="Successful records")
    failed_records: int = Field(..., description="Failed records")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Import errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Import warnings")