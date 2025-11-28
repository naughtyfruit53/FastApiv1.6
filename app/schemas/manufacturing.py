# app/schemas/manufacturing.py
"""Pydantic schemas for manufacturing module"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

# Manufacturing Order Schemas - Enhanced
class ManufacturingOrderCreate(BaseModel):
    bom_id: int
    planned_quantity: float
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    production_status: str = "planned"
    priority: str = "medium"
    production_department: Optional[str] = None
    production_location: Optional[str] = None
    notes: Optional[str] = None
    # NEW
    shift: Optional[str] = None
    machine_id: Optional[str] = None
    operator: Optional[str] = None
    wastage_percentage: Optional[float] = 0.0
    time_taken: Optional[float] = 0.0
    power_consumption: Optional[float] = 0.0
    downtime_events: Optional[List[str]] = None
    sales_order_id: Optional[int] = None

class ManufacturingOrderResponse(BaseModel):
    id: int
    voucher_number: str
    date: datetime
    bom_id: int
    planned_quantity: float
    produced_quantity: float
    scrap_quantity: float
    production_status: str
    priority: str
    total_amount: float
    bom: Optional[dict] = None
    # NEW
    shift: Optional[str]
    machine_id: Optional[str]
    operator: Optional[str]
    wastage_percentage: float
    time_taken: float
    power_consumption: float
    downtime_events: Optional[List[str]]
    sales_order_id: Optional[int]

    class Config:
        from_attributes = True

# NEW: ProductionEntry Schemas
class ProductionEntryCreate(BaseModel):
    manufacturing_order_id: int
    production_order_no: str
    date: date
    shift: Optional[str]
    machine_id: int
    operator_id: int
    status: str
    product_id: int
    planned_quantity: float
    actual_quantity: float
    wastage_percentage: float = 0.0
    batch_number: str
    rejected_quantity: float = 0.0
    time_taken: float
    labor_hours: float
    machine_hours: float
    power_consumption: float = 0.0
    downtime_events: Optional[str]  # JSON string
    notes: Optional[str]
    attachments: Optional[str]  # JSON string
    qc_approval: bool = False

class ProductionEntryResponse(BaseModel):
    id: int
    manufacturing_order_id: int
    production_order_no: str
    date: date
    shift: Optional[str]
    machine_id: int
    operator_id: int
    status: str
    product_id: int
    planned_quantity: float
    actual_quantity: float
    wastage_percentage: float
    batch_number: str
    rejected_quantity: float
    time_taken: float
    labor_hours: float
    machine_hours: float
    power_consumption: float
    downtime_events: Optional[str]
    notes: Optional[str]
    attachments: Optional[str]
    qc_approval: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: Machine Schemas
class MachineCreate(BaseModel):
    name: str
    code: str
    location: str
    model: str
    serial_no: Optional[str] = None
    supplier: Optional[str] = None
    amc_details: Optional[str] = None

class MachineResponse(BaseModel):
    id: int
    name: str
    code: str
    location: str
    model: str
    serial_no: Optional[str]
    supplier: Optional[str]
    amc_details: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: PreventiveMaintenanceSchedule Schemas
class PreventiveMaintenanceScheduleCreate(BaseModel):
    machine_id: int
    frequency: str
    tasks: str  # JSON string
    assigned_technician: Optional[str] = None
    next_due_date: datetime

class PreventiveMaintenanceScheduleResponse(BaseModel):
    id: int
    machine_id: int
    frequency: str
    tasks: str
    assigned_technician: Optional[str]
    next_due_date: datetime
    overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: BreakdownMaintenance Schemas
class BreakdownMaintenanceCreate(BaseModel):
    machine_id: int
    breakdown_type: str
    date: datetime
    reported_by: str
    description: str
    root_cause: Optional[str] = None
    time_to_fix: Optional[float] = None
    spare_parts_used: Optional[str] = None  # JSON string
    cost: Optional[float] = 0.0
    downtime_hours: Optional[float] = 0.0

class BreakdownMaintenanceResponse(BaseModel):
    id: int
    machine_id: int
    breakdown_type: str
    date: datetime
    reported_by: str
    description: str
    root_cause: Optional[str]
    time_to_fix: Optional[float]
    spare_parts_used: Optional[str]
    cost: float
    downtime_hours: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: MachinePerformanceLog Schemas
class MachinePerformanceLogCreate(BaseModel):
    machine_id: int
    date: datetime
    runtime_hours: float
    idle_hours: float
    efficiency_percentage: float
    error_codes: Optional[str] = None  # JSON string

class MachinePerformanceLogResponse(BaseModel):
    id: int
    machine_id: int
    date: datetime
    runtime_hours: float
    idle_hours: float
    efficiency_percentage: float
    error_codes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# NEW: SparePart Schemas
class SparePartCreate(BaseModel):
    machine_id: int
    name: str
    code: str
    quantity: float
    min_level: float = 0.0
    reorder_level: float = 0.0
    unit_cost: float = 0.0

class SparePartResponse(BaseModel):
    id: int
    machine_id: int
    name: str
    code: str
    quantity: float
    min_level: float
    reorder_level: float
    unit_cost: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: QCTemplate Schemas
class QCTemplateCreate(BaseModel):
    product_id: int
    test_name: str
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    unit: Optional[str] = None

class QCTemplateResponse(BaseModel):
    id: int
    product_id: int
    test_name: str
    tolerance_min: Optional[float]
    tolerance_max: Optional[float]
    unit: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: QCInspection Schemas
class QCInspectionCreate(BaseModel):
    batch_id: int
    inspector: str
    test_results: str  # JSON string
    overall_status: str

class QCInspectionResponse(BaseModel):
    id: int
    batch_id: int
    inspector: str
    test_results: str
    overall_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: Rejection Schemas
class RejectionCreate(BaseModel):
    qc_inspection_id: int
    reason: str
    rework_required: bool = False

class RejectionResponse(BaseModel):
    id: int
    qc_inspection_id: int
    reason: str
    rework_required: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# NEW: InventoryAdjustment Schemas
class InventoryAdjustmentCreate(BaseModel):
    type: str
    item_id: int
    batch_number: Optional[str] = None
    old_quantity: float
    new_quantity: float
    reason: str
    documents: Optional[str] = None  # JSON string

class InventoryAdjustmentResponse(BaseModel):
    id: int
    type: str
    item_id: int
    batch_number: Optional[str]
    old_quantity: float
    new_quantity: float
    reason: str
    documents: Optional[str]
    approved_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True