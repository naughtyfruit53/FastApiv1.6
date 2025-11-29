# app/schemas/manufacturing.py
"""Pydantic schemas for manufacturing module"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

# Manufacturing Order Schemas - Enhanced
class ManufacturingOrderCreate(BaseModel):
    date: Optional[datetime] = None  # NEW: Added date field
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

class ManufacturingOrderUpdate(BaseModel):  # NEW: For general updates including soft delete
    bom_id: Optional[int] = None
    planned_quantity: Optional[float] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    production_status: Optional[str] = None
    priority: Optional[str] = None
    production_department: Optional[str] = None
    production_location: Optional[str] = None
    notes: Optional[str] = None
    shift: Optional[str] = None
    machine_id: Optional[str] = None
    operator: Optional[str] = None
    wastage_percentage: Optional[float] = None
    time_taken: Optional[float] = None
    power_consumption: Optional[float] = None
    downtime_events: Optional[List[str]] = None
    sales_order_id: Optional[int] = None
    is_deleted: Optional[bool] = False  # NEW
    deletion_remark: Optional[str] = None  # NEW: Required if is_deleted=True

class StatusUpdateSchema(BaseModel):  # NEW: For status updates
    status: str

class ManufacturingOrderResponse(BaseModel):
    id: int
    voucher_number: str
    date: datetime
    bom_id: int
    planned_quantity: float
    produced_quantity: float
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
    is_deleted: bool  # NEW
    deletion_remark: Optional[str]  # NEW

    class Config:
        from_attributes = True

# NEW: ProductionEntry Schemas
class ProductionEntryConsumptionCreate(BaseModel):
    component_id: int
    actual_qty: float
    wastage_qty: float = 0.0

class ProductionEntryCreate(BaseModel):
    production_order_id: int
    date: date
    shift: Optional[str]
    machine: Optional[str]
    operator: Optional[str]
    batch_number: str
    actual_quantity: float
    rejected_quantity: float = 0.0
    time_taken: float
    labor_hours: float
    machine_hours: float
    power_consumption: float = 0.0
    downtime_events: Optional[List[str]] = None
    notes: Optional[str]
    # attachments: Optional[List[str]] = None  # List of file paths or URLs
    bom_consumption: List[ProductionEntryConsumptionCreate]

class ProductionEntryUpdate(BaseModel):
    date: Optional[date]
    shift: Optional[str]
    machine: Optional[str]
    operator: Optional[str]
    batch_number: Optional[str]
    actual_quantity: Optional[float]
    rejected_quantity: Optional[float]
    time_taken: Optional[float]
    labor_hours: Optional[float]
    machine_hours: Optional[float]
    power_consumption: Optional[float]
    downtime_events: Optional[List[str]]
    notes: Optional[str]
    # attachments: Optional[List[str]]
    bom_consumption: Optional[List[ProductionEntryConsumptionCreate]]
    is_deleted: Optional[bool] = False
    deletion_remark: Optional[str]

class ProductionEntryConsumptionResponse(BaseModel):
    id: int
    component_id: int
    actual_qty: float
    wastage_qty: float

class ProductionEntryResponse(BaseModel):
    id: int
    voucher_number: str
    production_order_id: int
    date: date
    shift: Optional[str]
    machine: Optional[str]
    operator: Optional[str]
    batch_number: str
    actual_quantity: float
    rejected_quantity: float
    time_taken: float
    labor_hours: float
    machine_hours: float
    power_consumption: float
    downtime_events: Optional[List[str]]
    notes: Optional[str]
    # attachments: Optional[List[str]]
    bom_consumption: List[ProductionEntryConsumptionResponse]
    is_deleted: bool
    deletion_remark: Optional[str]
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
    make: Optional[str] = None
    serial_no: Optional[str] = None
    supplier: Optional[str] = None
    commissioning_date: Optional[datetime] = None
    status: str = "active"  # active, inactive, under_maintenance
    criticality: str = "medium"  # low, medium, high, critical
    amc_details: Optional[str] = None
    attachments: Optional[str] = None  # JSON string of attachment URLs
    mtbf: Optional[float] = None  # Mean Time Between Failures
    mttr: Optional[float] = None  # Mean Time To Repair
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    model: Optional[str] = None
    make: Optional[str] = None
    serial_no: Optional[str] = None
    supplier: Optional[str] = None
    commissioning_date: Optional[datetime] = None
    status: Optional[str] = None
    criticality: Optional[str] = None
    amc_details: Optional[str] = None
    attachments: Optional[str] = None
    mtbf: Optional[float] = None
    mttr: Optional[float] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None

class MachineResponse(BaseModel):
    id: int
    name: str
    code: str
    location: str
    model: str
    make: Optional[str] = None
    serial_no: Optional[str] = None
    supplier: Optional[str] = None
    commissioning_date: Optional[datetime] = None
    status: str = "active"
    criticality: str = "medium"
    amc_details: Optional[str] = None
    attachments: Optional[str] = None
    mtbf: Optional[float] = None
    mttr: Optional[float] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: PreventiveMaintenanceSchedule Schemas
class PreventiveMaintenanceScheduleCreate(BaseModel):
    machine_id: int
    frequency: str  # daily, weekly, monthly, quarterly, annually
    tasks: str  # JSON string checklist
    assigned_technician: Optional[str] = None
    planned_date: Optional[datetime] = None
    next_due_date: datetime

class PreventiveMaintenanceScheduleUpdate(BaseModel):
    machine_id: Optional[int] = None
    frequency: Optional[str] = None
    tasks: Optional[str] = None
    assigned_technician: Optional[str] = None
    planned_date: Optional[datetime] = None
    next_due_date: Optional[datetime] = None
    overdue: Optional[bool] = None
    last_completed_at: Optional[datetime] = None

class PreventiveMaintenanceScheduleResponse(BaseModel):
    id: int
    machine_id: int
    frequency: str
    tasks: str
    assigned_technician: Optional[str] = None
    planned_date: Optional[datetime] = None
    next_due_date: datetime
    overdue: bool = False
    last_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: BreakdownMaintenance Schemas
class BreakdownMaintenanceCreate(BaseModel):
    machine_id: int
    breakdown_type: str
    date: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reported_by: str
    description: str
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    time_to_fix: Optional[float] = None
    spare_parts_used: Optional[str] = None  # JSON string
    cost: Optional[float] = 0.0
    downtime_hours: Optional[float] = 0.0
    status: str = "open"  # open, in_progress, closed

class BreakdownMaintenanceUpdate(BaseModel):
    machine_id: Optional[int] = None
    breakdown_type: Optional[str] = None
    date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reported_by: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    time_to_fix: Optional[float] = None
    spare_parts_used: Optional[str] = None
    cost: Optional[float] = None
    downtime_hours: Optional[float] = None
    status: Optional[str] = None

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
    description: Optional[str] = None
    quantity: float
    min_level: float = 0.0
    max_level: float = 0.0
    reorder_level: float = 0.0
    unit_cost: float = 0.0
    location_bin: Optional[str] = None

class SparePartUpdate(BaseModel):
    machine_id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    min_level: Optional[float] = None
    max_level: Optional[float] = None
    reorder_level: Optional[float] = None
    unit_cost: Optional[float] = None
    location_bin: Optional[str] = None

class SparePartResponse(BaseModel):
    id: int
    machine_id: int
    name: str
    code: str
    description: Optional[str] = None
    quantity: float
    min_level: float = 0.0
    max_level: float = 0.0
    reorder_level: float = 0.0
    unit_cost: float = 0.0
    location_bin: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: QCTemplate Schemas
class QCTemplateCreate(BaseModel):
    product_id: int
    test_name: str
    description: Optional[str] = None
    parameters: Optional[str] = None  # JSON string of specs with target values
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    unit: Optional[str] = None
    method: Optional[str] = None
    sampling_size: Optional[int] = None
    version: str = "1.0"
    is_active: bool = True

class QCTemplateUpdate(BaseModel):
    product_id: Optional[int] = None
    test_name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[str] = None
    tolerance_min: Optional[float] = None
    tolerance_max: Optional[float] = None
    unit: Optional[str] = None
    method: Optional[str] = None
    sampling_size: Optional[int] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None

class QCTemplateResponse(BaseModel):
    id: int
    product_id: int
    test_name: str
    description: Optional[str] = None
    parameters: Optional[str] = None
    tolerance_min: Optional[float]
    tolerance_max: Optional[float]
    unit: Optional[str]
    method: Optional[str] = None
    sampling_size: Optional[int] = None
    version: str = "1.0"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: QCInspection Schemas
class QCInspectionCreate(BaseModel):
    batch_id: int
    work_order_id: Optional[int] = None
    item_id: Optional[int] = None
    template_id: Optional[int] = None
    inspector: str
    scheduled_date: Optional[datetime] = None
    test_results: str  # JSON string
    measurements: Optional[str] = None  # JSON string of measurements vs template specs
    photos: Optional[str] = None  # JSON string of photo URLs
    overall_status: str = "pending"  # pending, pass, fail
    status: str = "draft"  # draft, in_progress, completed
    notes: Optional[str] = None

class QCInspectionUpdate(BaseModel):
    batch_id: Optional[int] = None
    work_order_id: Optional[int] = None
    item_id: Optional[int] = None
    template_id: Optional[int] = None
    inspector: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    test_results: Optional[str] = None
    measurements: Optional[str] = None
    photos: Optional[str] = None
    overall_status: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class QCInspectionResponse(BaseModel):
    id: int
    batch_id: int
    work_order_id: Optional[int] = None
    item_id: Optional[int] = None
    template_id: Optional[int] = None
    inspector: str
    scheduled_date: Optional[datetime] = None
    test_results: str
    measurements: Optional[str] = None
    photos: Optional[str] = None
    overall_status: str
    status: str = "draft"
    notes: Optional[str] = None
    signed_off_by: Optional[int] = None
    signed_off_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: Rejection Schemas
class RejectionCreate(BaseModel):
    qc_inspection_id: int
    work_order_id: Optional[int] = None
    lot_number: Optional[str] = None
    reason: str
    reason_code: Optional[str] = None
    quantity: float = 0.0
    ncr_reference: Optional[str] = None  # Non-Conformance Report reference
    mrb_reference: Optional[str] = None  # Material Review Board reference
    disposition: Optional[str] = None  # rework, scrap, return
    rework_required: bool = False
    notes: Optional[str] = None

class RejectionUpdate(BaseModel):
    qc_inspection_id: Optional[int] = None
    work_order_id: Optional[int] = None
    lot_number: Optional[str] = None
    reason: Optional[str] = None
    reason_code: Optional[str] = None
    quantity: Optional[float] = None
    ncr_reference: Optional[str] = None
    mrb_reference: Optional[str] = None
    disposition: Optional[str] = None
    rework_required: Optional[bool] = None
    notes: Optional[str] = None
    approval_status: Optional[str] = None

class RejectionResponse(BaseModel):
    id: int
    qc_inspection_id: int
    work_order_id: Optional[int] = None
    lot_number: Optional[str] = None
    reason: str
    reason_code: Optional[str] = None
    quantity: float = 0.0
    ncr_reference: Optional[str] = None
    mrb_reference: Optional[str] = None
    disposition: Optional[str] = None
    rework_required: bool
    notes: Optional[str] = None
    approval_status: str = "pending"
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: InventoryAdjustment Schemas
class InventoryAdjustmentCreate(BaseModel):
    type: str  # increase, decrease, conversion, wip, write-off
    item_id: int
    batch_number: Optional[str] = None
    old_quantity: float
    new_quantity: float
    reason: str  # audit, damage, wastage, theft, error, remeasure
    reason_code: Optional[str] = None
    reference_doc: Optional[str] = None
    documents: Optional[str] = None  # JSON string
    comment: Optional[str] = None

class InventoryAdjustmentSubmit(BaseModel):
    """Schema for submitting inventory adjustment with confirmation"""
    type: str  # increase, decrease, conversion, wip, write-off
    item_id: int
    batch_number: Optional[str] = None
    old_quantity: float
    new_quantity: float
    reason: str  # audit, damage, wastage, theft, error, remeasure
    reason_code: Optional[str] = None
    reference_doc: Optional[str] = None
    documents: Optional[str] = None  # JSON string
    comment: str  # Required for submission

class InventoryAdjustmentResponse(BaseModel):
    id: int
    type: str
    item_id: int
    batch_number: Optional[str] = None
    old_quantity: float
    new_quantity: float
    reason: str
    reason_code: Optional[str] = None
    reference_doc: Optional[str] = None
    documents: Optional[str] = None
    comment: Optional[str] = None
    status: str = "pending"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NEW: Added missing schemas for BOM
class BOMComponentCreate(BaseModel):
    component_item_id: int
    quantity_required: float
    unit: str
    wastage_percentage: float = 0.0
    is_optional: bool = False
    sequence: int = 0
    notes: Optional[str] = None

class BillOfMaterialsCreate(BaseModel):
    bom_name: str
    output_item_id: int
    output_quantity: float
    version: str = "1.0"
    description: Optional[str] = None
    components: Optional[List[BOMComponentCreate]] = None

class BillOfMaterialsResponse(BaseModel):
    id: int
    bom_name: str
    output_item_id: int
    output_quantity: float
    version: str
    is_active: bool
    description: Optional[str] = None
    material_cost: float
    labor_cost: float
    overhead_cost: float
    total_cost: float
    created_by: int

    class Config:
        from_attributes = True