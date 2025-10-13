# app/api/v1/manufacturing/schemas.py
"""
Shared schemas for manufacturing module
"""

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


# Manufacturing Journal Voucher Schemas  
class ManufacturingJournalFinishedProductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_cost: float
    notes: Optional[str] = None


class ManufacturingJournalMaterialCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_cost: float
    notes: Optional[str] = None


class ManufacturingJournalByproductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_value: float
    notes: Optional[str] = None


class ManufacturingJournalVoucherCreate(BaseModel):
    manufacturing_order_id: int
    production_date: datetime
    notes: Optional[str] = None
    finished_products: List[ManufacturingJournalFinishedProductCreate] = []
    materials: List[ManufacturingJournalMaterialCreate] = []
    byproducts: List[ManufacturingJournalByproductCreate] = []


# Material Receipt Voucher Schemas
class MaterialReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    notes: Optional[str] = None


class MaterialReceiptVoucherCreate(BaseModel):
    received_from: str
    received_date: datetime
    notes: Optional[str] = None
    items: List[MaterialReceiptItemCreate] = []


# Job Card Voucher Schemas
class JobCardSuppliedMaterialCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    notes: Optional[str] = None


class JobCardReceivedOutputCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    notes: Optional[str] = None


class JobCardVoucherCreate(BaseModel):
    manufacturing_order_id: int
    work_station: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    supplied_materials: List[JobCardSuppliedMaterialCreate] = []
    received_outputs: List[JobCardReceivedOutputCreate] = []


# Stock Journal Schemas
class StockJournalEntryCreate(BaseModel):
    product_id: int
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    quantity: float
    unit: str
    notes: Optional[str] = None


class StockJournalCreate(BaseModel):
    journal_type: str = "transfer"
    notes: Optional[str] = None
    entries: List[StockJournalEntryCreate] = []


# BOM Schemas
class BOMComponentCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    scrap_percentage: float = 0.0


class BOMCreate(BaseModel):
    product_id: int
    output_quantity: float
    unit: str
    notes: Optional[str] = None
    components: List[BOMComponentCreate] = []


class BOMAlternateComponentCreate(BaseModel):
    bom_component_id: int
    alternate_product_id: int
    quantity: float
    unit: str
    notes: Optional[str] = None


class BOMRevisionCreate(BaseModel):
    bom_id: int
    revision_notes: str
    components: List[BOMComponentCreate] = []
