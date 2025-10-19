# app/schemas/manufacturing.py
"""Pydantic schemas for manufacturing module"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Manufacturing Order Schemas
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

    class Config:
        from_attributes = True

# Material Issue Schemas
class MaterialIssueItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    notes: Optional[str] = None

class MaterialIssueCreate(BaseModel):
    manufacturing_order_id: Optional[int] = None
    issued_to_department: Optional[str] = None
    issued_to_employee: Optional[str] = None
    purpose: str = "production"
    notes: Optional[str] = None
    items: List[MaterialIssueItemCreate] = []

# Enhanced Material Issue Schemas
class MaterialIssueItemCreateEnhanced(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None
    notes: Optional[str] = None

class MaterialIssueCreateEnhanced(BaseModel):
    manufacturing_order_id: Optional[int] = None
    issued_to_department: Optional[str] = None
    issued_to_employee: Optional[str] = None
    purpose: str = "production"
    destination: Optional[str] = None
    issue_time: Optional[datetime] = None
    expected_return_time: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[MaterialIssueItemCreateEnhanced] = []

# Manufacturing Journal Voucher Schemas
class ManufacturingJournalFinishedProductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_cost: float = 0.0
    quality_grade: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None

class ManufacturingJournalMaterialCreate(BaseModel):
    product_id: int
    quantity_consumed: float
    unit: str
    unit_cost: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None

class ManufacturingJournalByproductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_value: float = 0.0
    batch_number: Optional[str] = None
    condition: Optional[str] = None

class ManufacturingJournalVoucherCreate(BaseModel):
    manufacturing_order_id: int
    bom_id: int
    date_of_manufacture: datetime
    shift: Optional[str] = None
    operator: Optional[str] = None
    supervisor: Optional[str] = None
    machine_used: Optional[str] = None
    finished_quantity: float = 0.0
    scrap_quantity: float = 0.0
    rework_quantity: float = 0.0
    byproduct_quantity: float = 0.0
    material_cost: float = 0.0
    labor_cost: float = 0.0
    overhead_cost: float = 0.0
    quality_grade: Optional[str] = None
    quality_remarks: Optional[str] = None
    narration: Optional[str] = None
    notes: Optional[str] = None
    finished_products: List[ManufacturingJournalFinishedProductCreate] = []
    consumed_materials: List[ManufacturingJournalMaterialCreate] = []
    byproducts: List[ManufacturingJournalByproductCreate] = []

# Material Receipt Voucher Schemas
class MaterialReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    received_quantity: Optional[float] = None
    accepted_quantity: Optional[float] = None
    rejected_quantity: Optional[float] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None
    quality_status: Optional[str] = None
    inspection_remarks: Optional[str] = None
    notes: Optional[str] = None

class MaterialReceiptVoucherCreate(BaseModel):
    manufacturing_order_id: Optional[int] = None
    source_type: str  # 'return', 'purchase', 'transfer'
    source_reference: Optional[str] = None
    received_from_department: Optional[str] = None
    received_from_employee: Optional[str] = None
    received_by_employee: Optional[str] = None
    receipt_time: Optional[datetime] = None
    inspection_required: bool = False
    inspection_status: str = "pending"
    inspector_name: Optional[str] = None
    inspection_date: Optional[datetime] = None
    inspection_remarks: Optional[str] = None
    condition_on_receipt: Optional[str] = None
    notes: Optional[str] = None
    items: List[MaterialReceiptItemCreate] = []

# Job Card Voucher Schemas
class JobCardSuppliedMaterialCreate(BaseModel):
    product_id: int
    quantity_supplied: float
    unit: str
    unit_rate: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    supply_date: Optional[datetime] = None

class JobCardReceivedOutputCreate(BaseModel):
    product_id: int
    quantity_received: float
    unit: str
    unit_rate: float = 0.0
    quality_status: Optional[str] = None
    inspection_date: Optional[datetime] = None
    inspection_remarks: Optional[str] = None
    batch_number: Optional[str] = None
    receipt_date: Optional[datetime] = None

class JobCardVoucherCreate(BaseModel):
    job_type: str
    vendor_id: int
    manufacturing_order_id: Optional[int] = None
    job_description: str
    job_category: Optional[str] = None
    expected_completion_date: Optional[datetime] = None
    materials_supplied_by: str = "company"
    delivery_address: Optional[str] = None
    transport_mode: Optional[str] = None
    quality_specifications: Optional[str] = None
    quality_check_required: bool = True
    notes: Optional[str] = None
    supplied_materials: List[JobCardSuppliedMaterialCreate] = []
    received_outputs: List[JobCardReceivedOutputCreate] = []

# Stock Journal Schemas
class StockJournalEntryCreate(BaseModel):
    product_id: int
    debit_quantity: float = 0.0
    credit_quantity: float = 0.0
    unit: str
    unit_rate: float = 0.0
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    from_bin: Optional[str] = None
    to_bin: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    transformation_type: Optional[str] = None

class StockJournalCreate(BaseModel):
    journal_type: str  # 'transfer', 'assembly', 'disassembly', 'adjustment', 'manufacturing'
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    manufacturing_order_id: Optional[int] = None
    bom_id: Optional[int] = None
    transfer_reason: Optional[str] = None
    assembly_product_id: Optional[int] = None
    assembly_quantity: Optional[float] = None
    physical_verification_done: bool = False
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    notes: Optional[str] = None
    entries: List[StockJournalEntryCreate] = []