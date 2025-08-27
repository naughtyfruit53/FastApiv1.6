"""
Inventory & Parts Management Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums for better type safety
class TransactionType(str, Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class ReferenceType(str, Enum):
    JOB = "job"
    PURCHASE = "purchase"
    MANUAL = "manual"
    TRANSFER = "transfer"


class JobPartsStatus(str, Enum):
    PLANNED = "planned"
    ALLOCATED = "allocated"
    USED = "used"
    RETURNED = "returned"


class AlertType(str, Enum):
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    REORDER = "reorder"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Inventory Transaction Schemas
class InventoryTransactionBase(BaseModel):
    product_id: int
    transaction_type: TransactionType
    quantity: float
    unit: str
    location: Optional[str] = None
    reference_type: Optional[ReferenceType] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    transaction_date: datetime


class InventoryTransactionCreate(InventoryTransactionBase):
    """Schema for creating inventory transaction"""
    stock_before: float
    stock_after: float

    @validator('quantity')
    def validate_quantity(cls, v):
        if v == 0:
            raise ValueError('Quantity cannot be zero')
        return v


class InventoryTransactionUpdate(BaseModel):
    """Schema for updating inventory transaction (limited fields)"""
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None


class InventoryTransactionInDB(InventoryTransactionBase):
    """Schema for inventory transaction data from database"""
    id: int
    organization_id: int
    stock_before: float
    stock_after: float
    created_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryTransactionResponse(InventoryTransactionInDB):
    """Enhanced response with related data"""
    product_name: Optional[str] = None
    created_by_name: Optional[str] = None


# Job Parts Schemas
class JobPartsBase(BaseModel):
    job_id: int
    product_id: int
    quantity_required: float
    unit: str
    notes: Optional[str] = None


class JobPartsCreate(JobPartsBase):
    """Schema for creating job parts assignment"""
    pass

    @validator('quantity_required')
    def validate_quantity_required(cls, v):
        if v <= 0:
            raise ValueError('Quantity required must be positive')
        return v


class JobPartsUpdate(BaseModel):
    """Schema for updating job parts"""
    quantity_required: Optional[float] = None
    quantity_used: Optional[float] = None
    status: Optional[JobPartsStatus] = None
    location_used: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None

    @validator('quantity_required')
    def validate_quantity_required(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity required must be positive')
        return v

    @validator('quantity_used')
    def validate_quantity_used(cls, v):
        if v is not None and v < 0:
            raise ValueError('Quantity used cannot be negative')
        return v


class JobPartsInDB(JobPartsBase):
    """Schema for job parts data from database"""
    id: int
    organization_id: int
    quantity_used: float
    status: JobPartsStatus
    location_used: Optional[str] = None
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    allocated_by_id: Optional[int] = None
    used_by_id: Optional[int] = None
    allocated_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobPartsResponse(JobPartsInDB):
    """Enhanced response with related data"""
    product_name: Optional[str] = None
    job_number: Optional[str] = None
    allocated_by_name: Optional[str] = None
    used_by_name: Optional[str] = None


# Inventory Alert Schemas
class InventoryAlertBase(BaseModel):
    product_id: int
    alert_type: AlertType
    current_stock: float
    reorder_level: float
    location: Optional[str] = None
    priority: AlertPriority = AlertPriority.MEDIUM
    message: Optional[str] = None
    suggested_order_quantity: Optional[float] = None


class InventoryAlertCreate(InventoryAlertBase):
    """Schema for creating inventory alert"""
    pass


class InventoryAlertUpdate(BaseModel):
    """Schema for updating inventory alert"""
    status: Optional[AlertStatus] = None
    priority: Optional[AlertPriority] = None
    message: Optional[str] = None
    suggested_order_quantity: Optional[float] = None


class InventoryAlertInDB(InventoryAlertBase):
    """Schema for inventory alert data from database"""
    id: int
    organization_id: int
    status: AlertStatus
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryAlertResponse(InventoryAlertInDB):
    """Enhanced response with related data"""
    product_name: Optional[str] = None
    acknowledged_by_name: Optional[str] = None


# Inventory Report Schemas
class InventoryUsageReport(BaseModel):
    """Schema for inventory usage reports"""
    product_id: int
    product_name: str
    total_issued: float
    total_received: float
    current_stock: float
    reorder_level: int
    total_jobs_used: int
    unit: str
    location: Optional[str] = None


class InventoryValueReport(BaseModel):
    """Schema for inventory valuation reports"""
    product_id: int
    product_name: str
    current_stock: float
    unit_cost: Optional[float] = None
    total_value: Optional[float] = None
    unit: str
    location: Optional[str] = None


class LowStockReport(BaseModel):
    """Schema for low stock reports"""
    product_id: int
    product_name: str
    current_stock: float
    reorder_level: int
    stock_deficit: float
    suggested_order_quantity: Optional[float] = None
    unit: str
    location: Optional[str] = None
    days_since_last_receipt: Optional[int] = None


# Bulk Operations Schemas
class BulkJobPartsAssignment(BaseModel):
    """Schema for bulk job parts assignment"""
    job_id: int
    parts: List[JobPartsCreate]


class BulkInventoryAdjustment(BaseModel):
    """Schema for bulk inventory adjustments"""
    adjustments: List[InventoryTransactionCreate]
    reason: str


class BulkInventoryResponse(BaseModel):
    """Schema for bulk operation responses"""
    message: str
    total_processed: int
    successful: int
    failed: int
    errors: List[str] = []
    warnings: List[str] = []


# Enhanced Stock Query Schemas
class InventoryFilter(BaseModel):
    """Schema for inventory filtering options"""
    product_id: Optional[int] = None
    location: Optional[str] = None
    low_stock_only: bool = False
    out_of_stock_only: bool = False
    search: Optional[str] = None
    category: Optional[str] = None


class InventoryListResponse(BaseModel):
    """Schema for paginated inventory list response"""
    items: List[InventoryTransactionResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool