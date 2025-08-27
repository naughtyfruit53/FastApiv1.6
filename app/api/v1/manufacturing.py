# app/api/v1/manufacturing.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import (
    ManufacturingOrder, MaterialIssue, ProductionEntry, BillOfMaterials,
    ManufacturingJournalVoucher, MaterialReceiptVoucher, JobCardVoucher, StockJournal,
    MaterialIssueItem, ManufacturingJournalFinishedProduct, ManufacturingJournalMaterial, 
    ManufacturingJournalByproduct, MaterialReceiptItem, JobCardSuppliedMaterial, 
    JobCardReceivedOutput, StockJournalEntry
)
from app.services.voucher_service import VoucherNumberService
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

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

# Manufacturing Order Endpoints
@router.get("/manufacturing-orders/", response_model=List[ManufacturingOrderResponse])
async def get_manufacturing_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ManufacturingOrder.production_status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/manufacturing-orders/next-number")
async def get_next_manufacturing_order_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "MO", current_user.organization_id, ManufacturingOrder
    )
    return next_number

@router.post("/manufacturing-orders/", response_model=ManufacturingOrderResponse)
async def create_manufacturing_order(
    order_data: ManufacturingOrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify BOM exists
    bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == order_data.bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Generate voucher number
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "MO", current_user.organization_id, ManufacturingOrder
    )
    
    # Calculate estimated cost
    multiplier = order_data.planned_quantity / bom.output_quantity
    estimated_cost = bom.total_cost * multiplier
    
    db_order = ManufacturingOrder(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        bom_id=order_data.bom_id,
        planned_quantity=order_data.planned_quantity,
        planned_start_date=order_data.planned_start_date,
        planned_end_date=order_data.planned_end_date,
        production_status=order_data.production_status,
        priority=order_data.priority,
        production_department=order_data.production_department,
        production_location=order_data.production_location,
        notes=order_data.notes,
        total_amount=estimated_cost,
        created_by=current_user.id
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.get("/manufacturing-orders/{order_id}", response_model=ManufacturingOrderResponse)
async def get_manufacturing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    order = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    return order

# Material Issue Endpoints
@router.get("/material-issues/")
async def get_material_issues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    issues = db.query(MaterialIssue).filter(
        MaterialIssue.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return issues

@router.get("/material-issues/next-number")
async def get_next_material_issue_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "MI", current_user.organization_id, MaterialIssue
    )
    return next_number

@router.post("/material-issues/")
async def create_material_issue(
    issue_data: MaterialIssueCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "MI", current_user.organization_id, MaterialIssue
    )
    
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in issue_data.items)
    
    db_issue = MaterialIssue(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        manufacturing_order_id=issue_data.manufacturing_order_id,
        issued_to_department=issue_data.issued_to_department,
        issued_to_employee=issue_data.issued_to_employee,
        purpose=issue_data.purpose,
        notes=issue_data.notes,
        total_amount=total_amount,
        created_by=current_user.id
    )
    
    db.add(db_issue)
    db.flush()
    
    # Add items
    from app.models.vouchers import MaterialIssueItem
    for item_data in issue_data.items:
        item = MaterialIssueItem(
            organization_id=current_user.organization_id,
            material_issue_id=db_issue.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            taxable_amount=item_data.quantity * item_data.unit_price,
            total_amount=item_data.quantity * item_data.unit_price,
            notes=item_data.notes
        )
        db.add(item)
    
    db.commit()
    db.refresh(db_issue)
    return db_issue

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

# Manufacturing Journal Voucher Endpoints
@router.get("/manufacturing-journal-vouchers/")
async def get_manufacturing_journal_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    vouchers = db.query(ManufacturingJournalVoucher).filter(
        ManufacturingJournalVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return vouchers

@router.get("/manufacturing-journal-vouchers/next-number")
async def get_next_manufacturing_journal_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "MJV", current_user.organization_id, ManufacturingJournalVoucher
    )
    return next_number

@router.post("/manufacturing-journal-vouchers/")
async def create_manufacturing_journal_voucher(
    voucher_data: ManufacturingJournalVoucherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify Manufacturing Order and BOM exist
    mo = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.id == voucher_data.manufacturing_order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    ).first()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    bom = db.query(BillOfMaterials).filter(
        BillOfMaterials.id == voucher_data.bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    ).first()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Generate voucher number
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "MJV", current_user.organization_id, ManufacturingJournalVoucher
    )
    
    # Calculate total manufacturing cost
    total_cost = voucher_data.material_cost + voucher_data.labor_cost + voucher_data.overhead_cost
    
    db_voucher = ManufacturingJournalVoucher(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        manufacturing_order_id=voucher_data.manufacturing_order_id,
        bom_id=voucher_data.bom_id,
        date_of_manufacture=voucher_data.date_of_manufacture,
        shift=voucher_data.shift,
        operator=voucher_data.operator,
        supervisor=voucher_data.supervisor,
        machine_used=voucher_data.machine_used,
        finished_quantity=voucher_data.finished_quantity,
        scrap_quantity=voucher_data.scrap_quantity,
        rework_quantity=voucher_data.rework_quantity,
        byproduct_quantity=voucher_data.byproduct_quantity,
        material_cost=voucher_data.material_cost,
        labor_cost=voucher_data.labor_cost,
        overhead_cost=voucher_data.overhead_cost,
        total_manufacturing_cost=total_cost,
        quality_grade=voucher_data.quality_grade,
        quality_remarks=voucher_data.quality_remarks,
        narration=voucher_data.narration,
        notes=voucher_data.notes,
        total_amount=total_cost,
        created_by=current_user.id
    )
    
    db.add(db_voucher)
    db.flush()
    
    # Add finished products
    for fp_data in voucher_data.finished_products:
        fp = ManufacturingJournalFinishedProduct(
            organization_id=current_user.organization_id,
            journal_id=db_voucher.id,
            product_id=fp_data.product_id,
            quantity=fp_data.quantity,
            unit=fp_data.unit,
            unit_cost=fp_data.unit_cost,
            total_cost=fp_data.quantity * fp_data.unit_cost,
            quality_grade=fp_data.quality_grade,
            batch_number=fp_data.batch_number,
            lot_number=fp_data.lot_number
        )
        db.add(fp)
    
    # Add consumed materials
    for cm_data in voucher_data.consumed_materials:
        cm = ManufacturingJournalMaterial(
            organization_id=current_user.organization_id,
            journal_id=db_voucher.id,
            product_id=cm_data.product_id,
            quantity_consumed=cm_data.quantity_consumed,
            unit=cm_data.unit,
            unit_cost=cm_data.unit_cost,
            total_cost=cm_data.quantity_consumed * cm_data.unit_cost,
            batch_number=cm_data.batch_number,
            lot_number=cm_data.lot_number
        )
        db.add(cm)
    
    # Add byproducts
    for bp_data in voucher_data.byproducts:
        bp = ManufacturingJournalByproduct(
            organization_id=current_user.organization_id,
            journal_id=db_voucher.id,
            product_id=bp_data.product_id,
            quantity=bp_data.quantity,
            unit=bp_data.unit,
            unit_value=bp_data.unit_value,
            total_value=bp_data.quantity * bp_data.unit_value,
            batch_number=bp_data.batch_number,
            condition=bp_data.condition
        )
        db.add(bp)
    
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

# Material Receipt Voucher Endpoints
@router.get("/material-receipt-vouchers/")
async def get_material_receipt_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    vouchers = db.query(MaterialReceiptVoucher).filter(
        MaterialReceiptVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return vouchers

@router.get("/material-receipt-vouchers/next-number")
async def get_next_material_receipt_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "MRV", current_user.organization_id, MaterialReceiptVoucher
    )
    return next_number

@router.post("/material-receipt-vouchers/")
async def create_material_receipt_voucher(
    voucher_data: MaterialReceiptVoucherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "MRV", current_user.organization_id, MaterialReceiptVoucher
    )
    
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in voucher_data.items)
    
    db_voucher = MaterialReceiptVoucher(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        manufacturing_order_id=voucher_data.manufacturing_order_id,
        source_type=voucher_data.source_type,
        source_reference=voucher_data.source_reference,
        received_from_department=voucher_data.received_from_department,
        received_from_employee=voucher_data.received_from_employee,
        received_by_employee=voucher_data.received_by_employee,
        receipt_time=voucher_data.receipt_time,
        inspection_required=voucher_data.inspection_required,
        inspection_status=voucher_data.inspection_status,
        inspector_name=voucher_data.inspector_name,
        inspection_date=voucher_data.inspection_date,
        inspection_remarks=voucher_data.inspection_remarks,
        condition_on_receipt=voucher_data.condition_on_receipt,
        notes=voucher_data.notes,
        total_amount=total_amount,
        created_by=current_user.id
    )
    
    db.add(db_voucher)
    db.flush()
    
    # Add items
    for item_data in voucher_data.items:
        item = MaterialReceiptItem(
            organization_id=current_user.organization_id,
            receipt_id=db_voucher.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            taxable_amount=item_data.quantity * item_data.unit_price,
            total_amount=item_data.quantity * item_data.unit_price,
            received_quantity=item_data.received_quantity or item_data.quantity,
            accepted_quantity=item_data.accepted_quantity,
            rejected_quantity=item_data.rejected_quantity,
            batch_number=item_data.batch_number,
            lot_number=item_data.lot_number,
            expiry_date=item_data.expiry_date,
            warehouse_location=item_data.warehouse_location,
            bin_location=item_data.bin_location,
            quality_status=item_data.quality_status,
            inspection_remarks=item_data.inspection_remarks,
            notes=item_data.notes
        )
        db.add(item)
    
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

# Job Card Voucher Endpoints
@router.get("/job-card-vouchers/")
async def get_job_card_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    vouchers = db.query(JobCardVoucher).filter(
        JobCardVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return vouchers

@router.get("/job-card-vouchers/next-number")
async def get_next_job_card_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "JCV", current_user.organization_id, JobCardVoucher
    )
    return next_number

@router.post("/job-card-vouchers/")
async def create_job_card_voucher(
    voucher_data: JobCardVoucherCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "JCV", current_user.organization_id, JobCardVoucher
    )
    
    # Calculate total amount from supplied materials and outputs
    supplied_value = sum(sm.quantity_supplied * sm.unit_rate for sm in voucher_data.supplied_materials)
    output_value = sum(ro.quantity_received * ro.unit_rate for ro in voucher_data.received_outputs)
    total_amount = output_value - supplied_value  # Net job work value
    
    db_voucher = JobCardVoucher(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        job_type=voucher_data.job_type,
        vendor_id=voucher_data.vendor_id,
        manufacturing_order_id=voucher_data.manufacturing_order_id,
        job_description=voucher_data.job_description,
        job_category=voucher_data.job_category,
        expected_completion_date=voucher_data.expected_completion_date,
        materials_supplied_by=voucher_data.materials_supplied_by,
        delivery_address=voucher_data.delivery_address,
        transport_mode=voucher_data.transport_mode,
        quality_specifications=voucher_data.quality_specifications,
        quality_check_required=voucher_data.quality_check_required,
        notes=voucher_data.notes,
        total_amount=total_amount,
        created_by=current_user.id
    )
    
    db.add(db_voucher)
    db.flush()
    
    # Add supplied materials
    for sm_data in voucher_data.supplied_materials:
        sm = JobCardSuppliedMaterial(
            organization_id=current_user.organization_id,
            job_card_id=db_voucher.id,
            product_id=sm_data.product_id,
            quantity_supplied=sm_data.quantity_supplied,
            unit=sm_data.unit,
            unit_rate=sm_data.unit_rate,
            total_value=sm_data.quantity_supplied * sm_data.unit_rate,
            batch_number=sm_data.batch_number,
            lot_number=sm_data.lot_number,
            supply_date=sm_data.supply_date
        )
        db.add(sm)
    
    # Add received outputs
    for ro_data in voucher_data.received_outputs:
        ro = JobCardReceivedOutput(
            organization_id=current_user.organization_id,
            job_card_id=db_voucher.id,
            product_id=ro_data.product_id,
            quantity_received=ro_data.quantity_received,
            unit=ro_data.unit,
            unit_rate=ro_data.unit_rate,
            total_value=ro_data.quantity_received * ro_data.unit_rate,
            quality_status=ro_data.quality_status,
            inspection_date=ro_data.inspection_date,
            inspection_remarks=ro_data.inspection_remarks,
            batch_number=ro_data.batch_number,
            receipt_date=ro_data.receipt_date
        )
        db.add(ro)
    
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

# Stock Journal Endpoints
@router.get("/stock-journals/")
async def get_stock_journals(
    skip: int = 0,
    limit: int = 100,
    journal_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(StockJournal).filter(
        StockJournal.organization_id == current_user.organization_id
    )
    
    if journal_type:
        query = query.filter(StockJournal.journal_type == journal_type)
    
    journals = query.offset(skip).limit(limit).all()
    return journals

@router.get("/stock-journals/next-number")
async def get_next_stock_journal_number(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = VoucherNumberService.generate_voucher_number(
        db, "SJ", current_user.organization_id, StockJournal
    )
    return next_number

@router.post("/stock-journals/")
async def create_stock_journal(
    journal_data: StockJournalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = VoucherNumberService.generate_voucher_number(
        db, "SJ", current_user.organization_id, StockJournal
    )
    
    # Calculate total amount from entries
    total_amount = sum(
        (entry.debit_value or 0.0) - (entry.credit_value or 0.0) 
        for entry in journal_data.entries
    )
    
    db_journal = StockJournal(
        organization_id=current_user.organization_id,
        voucher_number=voucher_number,
        date=datetime.now(),
        journal_type=journal_data.journal_type,
        from_location=journal_data.from_location,
        to_location=journal_data.to_location,
        from_warehouse=journal_data.from_warehouse,
        to_warehouse=journal_data.to_warehouse,
        manufacturing_order_id=journal_data.manufacturing_order_id,
        bom_id=journal_data.bom_id,
        transfer_reason=journal_data.transfer_reason,
        assembly_product_id=journal_data.assembly_product_id,
        assembly_quantity=journal_data.assembly_quantity,
        physical_verification_done=journal_data.physical_verification_done,
        verified_by=journal_data.verified_by,
        verification_date=journal_data.verification_date,
        notes=journal_data.notes,
        total_amount=total_amount,
        created_by=current_user.id
    )
    
    db.add(db_journal)
    db.flush()
    
    # Add entries
    for entry_data in journal_data.entries:
        debit_value = entry_data.debit_quantity * entry_data.unit_rate
        credit_value = entry_data.credit_quantity * entry_data.unit_rate
        
        entry = StockJournalEntry(
            organization_id=current_user.organization_id,
            stock_journal_id=db_journal.id,
            product_id=entry_data.product_id,
            debit_quantity=entry_data.debit_quantity,
            credit_quantity=entry_data.credit_quantity,
            unit=entry_data.unit,
            unit_rate=entry_data.unit_rate,
            debit_value=debit_value,
            credit_value=credit_value,
            from_location=entry_data.from_location,
            to_location=entry_data.to_location,
            from_warehouse=entry_data.from_warehouse,
            to_warehouse=entry_data.to_warehouse,
            from_bin=entry_data.from_bin,
            to_bin=entry_data.to_bin,
            batch_number=entry_data.batch_number,
            lot_number=entry_data.lot_number,
            expiry_date=entry_data.expiry_date,
            transformation_type=entry_data.transformation_type
        )
        db.add(entry)
    
    db.commit()
    db.refresh(db_journal)
    return db_journal