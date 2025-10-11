# app/api/v1/manufacturing.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import (
    ManufacturingOrder, MaterialIssue, ProductionEntry, BillOfMaterials, BOMComponent,
    ManufacturingJournalVoucher, MaterialReceiptVoucher, JobCardVoucher, StockJournal,
    MaterialIssueItem, ManufacturingJournalFinishedProduct, ManufacturingJournalMaterial, 
    ManufacturingJournalByproduct, MaterialReceiptItem, JobCardSuppliedMaterial, 
    JobCardReceivedOutput, StockJournalEntry
)
from app.models.vouchers.manufacturing_planning import BOMAlternateComponent, BOMRevision
from app.services.voucher_service import VoucherNumberService
from app.services.mrp_service import MRPService
from app.services.production_planning_service import ProductionPlanningService
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
@router.get("/manufacturing-orders", response_model=List[ManufacturingOrderResponse])
async def get_manufacturing_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(ManufacturingOrder.production_status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return orders

@router.get("/manufacturing-orders/next-number")
async def get_next_manufacturing_order_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "MO", current_user.organization_id, ManufacturingOrder
    )
    return next_number

@router.post("/manufacturing-orders")
async def create_manufacturing_order(
    order_data: ManufacturingOrderCreate,
    check_material_availability: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify BOM exists
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == order_data.bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    bom = result.scalar_one_or_none()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Generate voucher number
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
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
    await db.flush()  # Flush to get the ID
    
    # Check material availability if requested
    material_check_result = None
    if check_material_availability:
        is_available, shortages = await MRPService.check_material_availability_for_mo(
            db, current_user.organization_id, db_order.id
        )
        material_check_result = {
            'is_available': is_available,
            'shortages': shortages
        }
        
        # Log warning if materials are not available
        if not is_available:
            logger.warning(
                f"Manufacturing Order {voucher_number} created with material shortages: "
                f"{len(shortages)} items short"
            )
    
    await db.commit()
    await db.refresh(db_order)
    
    # Return order with material availability info
    response = {
        'id': db_order.id,
        'voucher_number': db_order.voucher_number,
        'date': db_order.date,
        'bom_id': db_order.bom_id,
        'planned_quantity': db_order.planned_quantity,
        'produced_quantity': db_order.produced_quantity,
        'production_status': db_order.production_status,
        'priority': db_order.priority,
        'total_amount': db_order.total_amount,
        'material_availability': material_check_result
    }
    
    return response

@router.get("/manufacturing-orders/{order_id}", response_model=ManufacturingOrderResponse)
async def get_manufacturing_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    return order

@router.post("/manufacturing-orders/{order_id}/complete")
async def complete_manufacturing_order(
    order_id: int,
    completed_quantity: float,
    scrap_quantity: float = 0.0,
    update_inventory: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Mark a manufacturing order as completed and update inventory.
    
    This endpoint:
    - Updates the MO status to 'completed'
    - Records produced and scrap quantities
    - Optionally updates finished goods inventory
    - Creates inventory transactions for traceability
    """
    # Get the manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    if mo.production_status == "completed":
        raise HTTPException(status_code=400, detail="Manufacturing order already completed")
    
    # Get BOM to find output product
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == mo.bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    bom = result.scalar_one_or_none()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Update manufacturing order
    mo.produced_quantity = completed_quantity
    mo.scrap_quantity = scrap_quantity
    mo.production_status = "completed"
    mo.actual_end_date = datetime.now()
    
    inventory_updates = []
    
    # Update finished goods inventory if requested
    if update_inventory and completed_quantity > 0:
        from app.models.product_models import Stock
        from app.schemas.inventory import InventoryTransactionCreate, TransactionType
        from app.api.v1.inventory import InventoryService
        
        # Get or create stock record for output product
        stmt = select(Stock).where(
            Stock.organization_id == current_user.organization_id,
            Stock.product_id == bom.output_item_id
        )
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()
        
        current_stock = stock.quantity if stock else 0.0
        new_stock = current_stock + completed_quantity
        
        # Update stock
        await InventoryService.update_stock_level(
            db,
            current_user.organization_id,
            bom.output_item_id,
            new_stock
        )
        
        # Create inventory transaction for traceability
        from app.models.enhanced_inventory_models import InventoryTransaction
        transaction = InventoryTransaction(
            organization_id=current_user.organization_id,
            product_id=bom.output_item_id,
            transaction_type=TransactionType.RECEIPT,
            quantity=completed_quantity,
            unit=bom.output_item.unit if bom.output_item else "PCS",
            reference_type="manufacturing_order",
            reference_id=mo.id,
            reference_number=mo.voucher_number,
            notes=f"Production completion for MO {mo.voucher_number}",
            stock_before=current_stock,
            stock_after=new_stock,
            transaction_date=datetime.now(),
            created_by_id=current_user.id
        )
        db.add(transaction)
        
        inventory_updates.append({
            'product_id': bom.output_item_id,
            'product_name': bom.output_item.product_name if bom.output_item else "Unknown",
            'quantity_added': completed_quantity,
            'stock_before': current_stock,
            'stock_after': new_stock
        })
    
    await db.commit()
    await db.refresh(mo)
    
    return {
        'id': mo.id,
        'voucher_number': mo.voucher_number,
        'production_status': mo.production_status,
        'produced_quantity': mo.produced_quantity,
        'scrap_quantity': mo.scrap_quantity,
        'actual_end_date': mo.actual_end_date,
        'inventory_updates': inventory_updates,
        'message': f"Manufacturing order {mo.voucher_number} completed successfully"
    }

@router.post("/manufacturing-orders/{order_id}/start")
async def start_manufacturing_order(
    order_id: int,
    deduct_materials: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Start a manufacturing order and optionally deduct materials from inventory.
    
    This endpoint:
    - Changes MO status to 'in_progress'
    - Records actual start date
    - Optionally deducts materials from inventory based on BOM
    - Creates material issue transactions
    """
    # Get the manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    if mo.production_status not in ["planned"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start order in {mo.production_status} status"
        )
    
    # Check material availability
    is_available, shortages = await MRPService.check_material_availability_for_mo(
        db, current_user.organization_id, order_id
    )
    
    if not is_available:
        logger.warning(f"Starting MO {mo.voucher_number} with material shortages")
    
    # Update MO status
    mo.production_status = "in_progress"
    mo.actual_start_date = datetime.now()
    
    material_deductions = []
    
    # Deduct materials if requested
    if deduct_materials:
        from app.api.v1.inventory import InventoryService
        from app.schemas.inventory import TransactionType
        
        # Get BOM components
        stmt = select(BOMComponent).where(
            BOMComponent.bom_id == mo.bom_id,
            BOMComponent.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        components = result.scalars().all()
        
        # Get BOM for output quantity
        stmt = select(BillOfMaterials).where(BillOfMaterials.id == mo.bom_id)
        result = await db.execute(stmt)
        bom = result.scalar_one_or_none()
        
        multiplier = mo.planned_quantity / bom.output_quantity
        
        for component in components:
            # Calculate required quantity with wastage
            wastage_factor = 1 + (component.wastage_percentage / 100)
            required_qty = component.quantity_required * multiplier * wastage_factor
            
            # Get current stock
            from app.models.product_models import Stock
            stmt = select(Stock).where(
                Stock.organization_id == current_user.organization_id,
                Stock.product_id == component.component_item_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            
            current_stock = stock.quantity if stock else 0.0
            
            # Deduct stock (but don't go negative - log warning instead)
            actual_deduction = min(required_qty, current_stock)
            new_stock = max(0, current_stock - actual_deduction)
            
            if actual_deduction < required_qty:
                logger.warning(
                    f"Insufficient stock for component {component.component_item_id}. "
                    f"Required: {required_qty}, Available: {current_stock}"
                )
            
            # Update stock
            await InventoryService.update_stock_level(
                db,
                current_user.organization_id,
                component.component_item_id,
                new_stock
            )
            
            # Create transaction
            from app.models.enhanced_inventory_models import InventoryTransaction
            transaction = InventoryTransaction(
                organization_id=current_user.organization_id,
                product_id=component.component_item_id,
                transaction_type=TransactionType.ISSUE,
                quantity=-actual_deduction,
                unit=component.unit,
                reference_type="manufacturing_order",
                reference_id=mo.id,
                reference_number=mo.voucher_number,
                notes=f"Material issue for MO {mo.voucher_number}",
                stock_before=current_stock,
                stock_after=new_stock,
                transaction_date=datetime.now(),
                created_by_id=current_user.id
            )
            db.add(transaction)
            
            material_deductions.append({
                'product_id': component.component_item_id,
                'product_name': component.component_item.product_name if component.component_item else "Unknown",
                'required_quantity': required_qty,
                'deducted_quantity': actual_deduction,
                'stock_before': current_stock,
                'stock_after': new_stock,
                'shortage': required_qty - actual_deduction if actual_deduction < required_qty else 0
            })
    
    await db.commit()
    await db.refresh(mo)
    
    return {
        'id': mo.id,
        'voucher_number': mo.voucher_number,
        'production_status': mo.production_status,
        'actual_start_date': mo.actual_start_date,
        'material_availability': {
            'is_available': is_available,
            'shortages': shortages
        },
        'material_deductions': material_deductions,
        'message': f"Manufacturing order {mo.voucher_number} started successfully"
    }

@router.get("/manufacturing-orders/{order_id}/check-shortages")
async def check_mo_shortages(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Check material shortages for a manufacturing order with enhanced information.
    
    This endpoint provides:
    - Material shortage details
    - Purchase order status for shortage items
    - Color coding (warning/critical) based on PO status
    - Recommendations for proceeding
    
    Use this endpoint before starting an MO or creating vouchers to check
    if material shortages exist and whether purchase orders have been placed.
    """
    # Get the manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    # Check material availability with PO status
    is_available, shortages = await MRPService.check_material_availability_for_mo(
        db, current_user.organization_id, order_id, include_po_status=True
    )
    
    # Categorize shortages by severity
    critical_shortages = [s for s in shortages if s.get('severity') == 'critical']
    warning_shortages = [s for s in shortages if s.get('severity') == 'warning']
    
    response = {
        'manufacturing_order_id': mo.id,
        'voucher_number': mo.voucher_number,
        'production_status': mo.production_status,
        'is_material_available': is_available,
        'total_shortage_items': len(shortages),
        'critical_items': len(critical_shortages),
        'warning_items': len(warning_shortages),
        'shortages': shortages,
        'recommendations': []
    }
    
    # Add recommendations
    if critical_shortages:
        response['recommendations'].append({
            'type': 'critical',
            'message': f"{len(critical_shortages)} item(s) have no purchase order placed. Immediate action required.",
            'action': 'Place purchase orders for critical items before proceeding.'
        })
    
    if warning_shortages:
        response['recommendations'].append({
            'type': 'warning',
            'message': f"{len(warning_shortages)} item(s) have purchase orders placed but not yet received.",
            'action': 'Verify delivery dates and coordinate with procurement team.'
        })
    
    if not shortages:
        response['recommendations'].append({
            'type': 'success',
            'message': 'All materials are available.',
            'action': 'You can proceed with manufacturing.'
        })
    
    return response

# Material Issue Endpoints
@router.get("/material-issues")
async def get_material_issues(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(MaterialIssue).where(
        MaterialIssue.organization_id == current_user.organization_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    issues = result.scalars().all()
    return issues

@router.get("/material-issues/next-number")
async def get_next_material_issue_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "MI", current_user.organization_id, MaterialIssue
    )
    return next_number

@router.post("/material-issues")
async def create_material_issue(
    issue_data: MaterialIssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
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
    await db.flush()
    
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
    
    await db.commit()
    await db.refresh(db_issue)
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
@router.get("/manufacturing-journal-vouchers")
async def get_manufacturing_journal_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(ManufacturingJournalVoucher).where(
        ManufacturingJournalVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    vouchers = result.scalars().all()
    return vouchers

@router.get("/manufacturing-journal-vouchers/next-number")
async def get_next_manufacturing_journal_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "MJV", current_user.organization_id, ManufacturingJournalVoucher
    )
    return next_number

@router.post("/manufacturing-journal-vouchers")
async def create_manufacturing_journal_voucher(
    voucher_data: ManufacturingJournalVoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Verify Manufacturing Order and BOM exist
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == voucher_data.manufacturing_order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == voucher_data.bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    bom = result.scalar_one_or_none()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Generate voucher number
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
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
    await db.flush()
    
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
    
    await db.commit()
    await db.refresh(db_voucher)
    return db_voucher

# Material Receipt Voucher Endpoints
@router.get("/material-receipt-vouchers")
async def get_material_receipt_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(MaterialReceiptVoucher).where(
        MaterialReceiptVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    vouchers = result.scalars().all()
    return vouchers

@router.get("/material-receipt-vouchers/next-number")
async def get_next_material_receipt_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "MRV", current_user.organization_id, MaterialReceiptVoucher
    )
    return next_number

@router.post("/material-receipt-vouchers")
async def create_material_receipt_voucher(
    voucher_data: MaterialReceiptVoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
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
    await db.flush()
    
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
    
    await db.commit()
    await db.refresh(db_voucher)
    return db_voucher

# Job Card Voucher Endpoints
@router.get("/job-card-vouchers")
async def get_job_card_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(JobCardVoucher).where(
        JobCardVoucher.organization_id == current_user.organization_id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    vouchers = result.scalars().all()
    return vouchers

@router.get("/job-card-vouchers/next-number")
async def get_next_job_card_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "JCV", current_user.organization_id, JobCardVoucher
    )
    return next_number

@router.post("/job-card-vouchers")
async def create_job_card_voucher(
    voucher_data: JobCardVoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
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
    await db.flush()
    
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
    
    await db.commit()
    await db.refresh(db_voucher)
    return db_voucher

# Stock Journal Endpoints
@router.get("/stock-journals")
async def get_stock_journals(
    skip: int = 0,
    limit: int = 100,
    journal_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    stmt = select(StockJournal).where(
        StockJournal.organization_id == current_user.organization_id
    )
    
    if journal_type:
        stmt = stmt.where(StockJournal.journal_type == journal_type)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    journals = result.scalars().all()
    return journals

@router.get("/stock-journals/next-number")
async def get_next_stock_journal_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    next_number = await VoucherNumberService.generate_voucher_number_async(
        db, "SJ", current_user.organization_id, StockJournal
    )
    return next_number

@router.post("/stock-journals")
async def create_stock_journal(
    journal_data: StockJournalCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Generate voucher number
    voucher_number = await VoucherNumberService.generate_voucher_number_async(
        db, "SJ", current_user.organization_id, StockJournal
    )
    
    # Calculate total amount from entries
    total_amount = sum(
        (entry.debit_quantity * entry.unit_rate) - (entry.credit_quantity * entry.unit_rate) 
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
    await db.flush()
    
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
    
    await db.commit()
    await db.refresh(db_journal)
    return db_journal

# MRP (Material Requirements Planning) Endpoints
@router.post("/mrp/analyze")
async def run_mrp_analysis(
    create_alerts: bool = True,
    generate_pr_data: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Run Material Requirements Planning analysis for all active manufacturing orders.
    
    This endpoint:
    - Calculates material requirements from BOMs and manufacturing orders
    - Identifies material shortages
    - Optionally creates shortage alerts
    - Optionally generates purchase requisition data
    """
    result = await MRPService.run_mrp_analysis(
        db,
        current_user.organization_id,
        create_alerts=create_alerts,
        generate_pr_data=generate_pr_data
    )
    return result

@router.get("/mrp/material-requirements")
async def get_material_requirements(
    manufacturing_order_ids: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get material requirements for manufacturing orders.
    
    Query parameters:
    - manufacturing_order_ids: Comma-separated list of MO IDs (optional)
    - start_date: Filter by MO planned start date (optional)
    - end_date: Filter by MO planned end date (optional)
    """
    mo_ids = None
    if manufacturing_order_ids:
        mo_ids = [int(id.strip()) for id in manufacturing_order_ids.split(',')]
    
    requirements = await MRPService.calculate_material_requirements(
        db,
        current_user.organization_id,
        manufacturing_order_ids=mo_ids,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        {
            'product_id': r.product_id,
            'product_name': r.product_name,
            'required_quantity': r.required_quantity,
            'available_quantity': r.available_quantity,
            'shortage_quantity': r.shortage_quantity,
            'unit': r.unit,
            'manufacturing_orders': r.manufacturing_orders
        }
        for r in requirements
    ]

@router.get("/mrp/check-availability/{order_id}")
async def check_material_availability(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Check material availability for a specific manufacturing order.
    
    Returns:
    - is_available: Boolean indicating if all materials are available
    - shortages: List of materials with shortages (if any)
    """
    is_available, shortages = await MRPService.check_material_availability_for_mo(
        db,
        current_user.organization_id,
        order_id
    )
    
    return {
        'manufacturing_order_id': order_id,
        'is_available': is_available,
        'shortages': shortages
    }

# BOM Management Endpoints
@router.post("/bom/{bom_id}/clone")
async def clone_bom(
    bom_id: int,
    new_name: str,
    new_version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Clone an existing BOM with all its components.
    Useful for creating variations or new versions.
    """
    # Get source BOM
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    source_bom = result.scalar_one_or_none()
    
    if not source_bom:
        raise HTTPException(status_code=404, detail="Source BOM not found")
    
    # Create new BOM
    new_bom = BillOfMaterials(
        organization_id=current_user.organization_id,
        bom_name=new_name,
        output_item_id=source_bom.output_item_id,
        output_quantity=source_bom.output_quantity,
        version=new_version or "1.0",
        is_active=True,
        description=f"Cloned from {source_bom.bom_name} v{source_bom.version}",
        notes=source_bom.notes,
        material_cost=source_bom.material_cost,
        labor_cost=source_bom.labor_cost,
        overhead_cost=source_bom.overhead_cost,
        total_cost=source_bom.total_cost,
        created_by=current_user.id
    )
    
    db.add(new_bom)
    await db.flush()
    
    # Clone components
    stmt = select(BOMComponent).where(
        BOMComponent.bom_id == bom_id,
        BOMComponent.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    source_components = result.scalars().all()
    
    for source_comp in source_components:
        new_comp = BOMComponent(
            organization_id=current_user.organization_id,
            bom_id=new_bom.id,
            component_item_id=source_comp.component_item_id,
            quantity_required=source_comp.quantity_required,
            unit=source_comp.unit,
            unit_cost=source_comp.unit_cost,
            total_cost=source_comp.total_cost,
            wastage_percentage=source_comp.wastage_percentage,
            is_optional=source_comp.is_optional,
            sequence=source_comp.sequence,
            notes=source_comp.notes
        )
        db.add(new_comp)
    
    await db.commit()
    await db.refresh(new_bom)
    
    return {
        'id': new_bom.id,
        'bom_name': new_bom.bom_name,
        'version': new_bom.version,
        'output_item_id': new_bom.output_item_id,
        'components_cloned': len(source_components),
        'message': f"BOM cloned successfully as '{new_name}'"
    }

@router.post("/bom/{bom_id}/revisions")
async def create_bom_revision(
    bom_id: int,
    new_version: str,
    change_type: str,
    change_description: str,
    change_reason: Optional[str] = None,
    cost_impact: float = 0.0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a revision record for BOM changes.
    Tracks engineering changes for audit and compliance.
    """
    # Get BOM
    stmt = select(BillOfMaterials).where(
        BillOfMaterials.id == bom_id,
        BillOfMaterials.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    bom = result.scalar_one_or_none()
    
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # Get latest revision number
    stmt = select(func.count(BOMRevision.id)).where(
        BOMRevision.bom_id == bom_id,
        BOMRevision.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    revision_count = result.scalar()
    
    revision_number = f"REV-{revision_count + 1:04d}"
    
    # Count affected orders
    stmt = select(func.count(ManufacturingOrder.id)).where(
        ManufacturingOrder.bom_id == bom_id,
        ManufacturingOrder.organization_id == current_user.organization_id,
        ManufacturingOrder.production_status.in_(['planned', 'in_progress'])
    )
    result = await db.execute(stmt)
    affected_orders = result.scalar()
    
    # Create revision record
    revision = BOMRevision(
        organization_id=current_user.organization_id,
        bom_id=bom_id,
        revision_number=revision_number,
        previous_version=bom.version,
        new_version=new_version,
        change_type=change_type,
        change_description=change_description,
        change_reason=change_reason,
        change_requested_by=current_user.id,
        approval_status="pending",
        cost_impact=cost_impact,
        affected_orders_count=affected_orders
    )
    
    db.add(revision)
    await db.commit()
    await db.refresh(revision)
    
    return {
        'id': revision.id,
        'revision_number': revision.revision_number,
        'previous_version': revision.previous_version,
        'new_version': revision.new_version,
        'change_type': revision.change_type,
        'approval_status': revision.approval_status,
        'affected_orders_count': revision.affected_orders_count,
        'message': 'BOM revision created and pending approval'
    }

@router.get("/bom/{bom_id}/revisions")
async def get_bom_revisions(
    bom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all revisions for a BOM"""
    stmt = select(BOMRevision).where(
        BOMRevision.bom_id == bom_id,
        BOMRevision.organization_id == current_user.organization_id
    ).order_by(BOMRevision.revision_date.desc())
    
    result = await db.execute(stmt)
    revisions = result.scalars().all()
    
    return [
        {
            'id': rev.id,
            'revision_number': rev.revision_number,
            'revision_date': rev.revision_date.isoformat() if rev.revision_date else None,
            'previous_version': rev.previous_version,
            'new_version': rev.new_version,
            'change_type': rev.change_type,
            'change_description': rev.change_description,
            'approval_status': rev.approval_status,
            'cost_impact': rev.cost_impact,
            'affected_orders_count': rev.affected_orders_count
        }
        for rev in revisions
    ]

@router.post("/bom/components/{component_id}/alternates")
async def add_alternate_component(
    component_id: int,
    alternate_item_id: int,
    quantity_required: float,
    unit: str,
    unit_cost: float = 0.0,
    preference_rank: int = 1,
    is_preferred: bool = False,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Add an alternate component that can be used in place of the primary component.
    Useful for material substitutions or vendor alternatives.
    """
    # Verify component exists
    stmt = select(BOMComponent).where(
        BOMComponent.id == component_id,
        BOMComponent.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    component = result.scalar_one_or_none()
    
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Calculate cost difference
    cost_difference = unit_cost - component.unit_cost
    
    # Create alternate
    alternate = BOMAlternateComponent(
        organization_id=current_user.organization_id,
        primary_component_id=component_id,
        alternate_item_id=alternate_item_id,
        quantity_required=quantity_required,
        unit=unit,
        unit_cost=unit_cost,
        cost_difference=cost_difference,
        preference_rank=preference_rank,
        is_preferred=is_preferred,
        notes=notes
    )
    
    db.add(alternate)
    await db.commit()
    await db.refresh(alternate)
    
    return {
        'id': alternate.id,
        'primary_component_id': component_id,
        'alternate_item_id': alternate_item_id,
        'quantity_required': quantity_required,
        'unit': unit,
        'cost_difference': cost_difference,
        'preference_rank': preference_rank,
        'message': 'Alternate component added successfully'
    }

@router.get("/bom/components/{component_id}/alternates")
async def get_alternate_components(
    component_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all alternate components for a primary component"""
    stmt = select(BOMAlternateComponent).where(
        BOMAlternateComponent.primary_component_id == component_id,
        BOMAlternateComponent.organization_id == current_user.organization_id
    ).order_by(BOMAlternateComponent.preference_rank)
    
    result = await db.execute(stmt)
    alternates = result.scalars().all()
    
    return [
        {
            'id': alt.id,
            'alternate_item_id': alt.alternate_item_id,
            'quantity_required': alt.quantity_required,
            'unit': alt.unit,
            'unit_cost': alt.unit_cost,
            'cost_difference': alt.cost_difference,
            'preference_rank': alt.preference_rank,
            'is_preferred': alt.is_preferred,
            'notes': alt.notes
        }
        for alt in alternates
    ]

# Production Planning & Scheduling Endpoints
@router.get("/production-schedule")
async def get_production_schedule(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get production schedule with prioritized manufacturing orders.
    Orders are sorted by priority score based on multiple factors.
    """
    schedule_items = await ProductionPlanningService.get_production_schedule(
        db,
        current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
        department=department
    )
    
    return [
        {
            'mo_id': item.mo_id,
            'voucher_number': item.voucher_number,
            'product_name': item.product_name,
            'planned_quantity': item.planned_quantity,
            'priority': item.priority,
            'planned_start_date': item.planned_start_date.isoformat() if item.planned_start_date else None,
            'planned_end_date': item.planned_end_date.isoformat() if item.planned_end_date else None,
            'estimated_hours': item.estimated_hours,
            'assigned_resources': item.assigned_resources
        }
        for item in schedule_items
    ]

@router.post("/manufacturing-orders/{order_id}/allocate-resources")
async def allocate_resources_to_order(
    order_id: int,
    operator: Optional[str] = None,
    supervisor: Optional[str] = None,
    machine_id: Optional[str] = None,
    workstation_id: Optional[str] = None,
    check_availability: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Allocate resources (operator, supervisor, machine, workstation) to a manufacturing order.
    Optionally checks for resource conflicts.
    """
    result = await ProductionPlanningService.allocate_resources(
        db,
        current_user.organization_id,
        order_id,
        operator=operator,
        supervisor=supervisor,
        machine_id=machine_id,
        workstation_id=workstation_id,
        check_availability=check_availability
    )
    
    return result

@router.get("/capacity-utilization")
async def get_capacity_utilization(
    start_date: datetime,
    end_date: datetime,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Calculate capacity utilization metrics for a time period.
    Shows planned vs actual hours, utilization rate, and order counts.
    """
    metrics = await ProductionPlanningService.calculate_capacity_utilization(
        db,
        current_user.organization_id,
        start_date,
        end_date,
        department=department
    )
    
    return metrics

@router.post("/production-schedule/optimize")
async def suggest_optimal_schedule(
    planning_horizon_days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Generate an optimal production schedule based on priorities and constraints.
    Suggests start/end dates for all pending manufacturing orders.
    """
    suggested_schedule = await ProductionPlanningService.suggest_optimal_schedule(
        db,
        current_user.organization_id,
        planning_horizon_days=planning_horizon_days
    )
    
    return {
        'planning_horizon_days': planning_horizon_days,
        'total_orders': len(suggested_schedule),
        'schedule': suggested_schedule
    }

# Shop Floor Control & Execution Endpoints
@router.post("/manufacturing-orders/{order_id}/update-progress")
async def update_manufacturing_order_progress(
    order_id: int,
    produced_quantity: float,
    scrap_quantity: float = 0.0,
    completion_percentage: Optional[float] = None,
    actual_labor_hours: Optional[float] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update progress on a manufacturing order.
    Can be called multiple times during production to track progress.
    """
    # Get manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    if mo.production_status not in ['in_progress', 'planned']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update progress for order in {mo.production_status} status"
        )
    
    # Update progress
    mo.produced_quantity = produced_quantity
    mo.scrap_quantity = scrap_quantity
    
    if completion_percentage is not None:
        mo.completion_percentage = min(completion_percentage, 100.0)
    else:
        # Auto-calculate completion percentage
        mo.completion_percentage = min((produced_quantity / mo.planned_quantity * 100), 100.0)
    
    if actual_labor_hours is not None:
        mo.actual_labor_hours = actual_labor_hours
    
    # Update status if completion is 100%
    if mo.completion_percentage >= 100.0 and mo.production_status != 'completed':
        mo.production_status = 'completed'
        mo.actual_end_date = datetime.now()
    elif mo.production_status == 'planned':
        mo.production_status = 'in_progress'
        if not mo.actual_start_date:
            mo.actual_start_date = datetime.now()
    
    # Add notes if provided
    if notes:
        if mo.notes:
            mo.notes += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
        else:
            mo.notes = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
    
    await db.commit()
    await db.refresh(mo)
    
    return {
        'id': mo.id,
        'voucher_number': mo.voucher_number,
        'production_status': mo.production_status,
        'produced_quantity': mo.produced_quantity,
        'planned_quantity': mo.planned_quantity,
        'scrap_quantity': mo.scrap_quantity,
        'completion_percentage': mo.completion_percentage,
        'actual_labor_hours': mo.actual_labor_hours,
        'message': 'Progress updated successfully'
    }

@router.get("/manufacturing-orders/{order_id}/progress")
async def get_manufacturing_order_progress(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed progress information for a manufacturing order.
    Includes production metrics, resource utilization, and timeline.
    """
    # Get manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    # Calculate metrics
    duration_planned = None
    duration_actual = None
    
    if mo.planned_start_date and mo.planned_end_date:
        duration_planned = (mo.planned_end_date - mo.planned_start_date).total_seconds() / 3600  # hours
    
    if mo.actual_start_date:
        end_date = mo.actual_end_date if mo.actual_end_date else datetime.now()
        duration_actual = (end_date - mo.actual_start_date).total_seconds() / 3600  # hours
    
    # Calculate efficiency
    quantity_efficiency = None
    if mo.planned_quantity > 0:
        quantity_efficiency = (mo.produced_quantity / mo.planned_quantity * 100)
    
    time_efficiency = None
    if duration_planned and duration_actual and duration_planned > 0:
        time_efficiency = (duration_planned / duration_actual * 100)
    
    labor_efficiency = None
    if mo.estimated_labor_hours > 0 and mo.actual_labor_hours:
        labor_efficiency = (mo.estimated_labor_hours / mo.actual_labor_hours * 100)
    
    return {
        'id': mo.id,
        'voucher_number': mo.voucher_number,
        'production_status': mo.production_status,
        'priority': mo.priority,
        'quantities': {
            'planned': mo.planned_quantity,
            'produced': mo.produced_quantity,
            'scrap': mo.scrap_quantity,
            'remaining': max(0, mo.planned_quantity - mo.produced_quantity)
        },
        'completion_percentage': mo.completion_percentage,
        'timeline': {
            'planned_start': mo.planned_start_date.isoformat() if mo.planned_start_date else None,
            'planned_end': mo.planned_end_date.isoformat() if mo.planned_end_date else None,
            'actual_start': mo.actual_start_date.isoformat() if mo.actual_start_date else None,
            'actual_end': mo.actual_end_date.isoformat() if mo.actual_end_date else None,
            'duration_planned_hours': round(duration_planned, 2) if duration_planned else None,
            'duration_actual_hours': round(duration_actual, 2) if duration_actual else None
        },
        'resources': {
            'operator': mo.assigned_operator,
            'supervisor': mo.assigned_supervisor,
            'machine': mo.machine_id,
            'workstation': mo.workstation_id,
            'estimated_labor_hours': mo.estimated_labor_hours,
            'actual_labor_hours': mo.actual_labor_hours
        },
        'efficiency': {
            'quantity_efficiency': round(quantity_efficiency, 2) if quantity_efficiency else None,
            'time_efficiency': round(time_efficiency, 2) if time_efficiency else None,
            'labor_efficiency': round(labor_efficiency, 2) if labor_efficiency else None
        },
        'location': {
            'department': mo.production_department,
            'location': mo.production_location
        }
    }

@router.post("/manufacturing-orders/{order_id}/barcode-scan")
async def record_barcode_scan(
    order_id: int,
    barcode: str,
    scan_type: str,  # 'start', 'progress', 'complete', 'material_issue'
    quantity: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Record a barcode scan event for shop floor data collection.
    Supports various scan types for different operations.
    """
    # Get manufacturing order
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    mo = result.scalar_one_or_none()
    
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    # Process scan based on type
    action_taken = None
    
    if scan_type == 'start':
        if mo.production_status == 'planned':
            mo.production_status = 'in_progress'
            mo.actual_start_date = datetime.now()
            action_taken = 'Manufacturing order started'
        else:
            action_taken = f'Order already in {mo.production_status} status'
    
    elif scan_type == 'progress' and quantity:
        mo.produced_quantity = quantity
        mo.completion_percentage = min((quantity / mo.planned_quantity * 100), 100.0)
        action_taken = f'Progress updated: {quantity} units produced'
    
    elif scan_type == 'complete':
        mo.production_status = 'completed'
        mo.actual_end_date = datetime.now()
        if not mo.produced_quantity:
            mo.produced_quantity = mo.planned_quantity
        mo.completion_percentage = 100.0
        action_taken = 'Manufacturing order completed'
    
    elif scan_type == 'material_issue':
        action_taken = f'Material barcode {barcode} scanned for issue'
        # In a real implementation, this would trigger material deduction
    
    # Log the scan event
    scan_note = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Barcode scan: {barcode} - Type: {scan_type} - {action_taken}"
    if mo.notes:
        mo.notes += f"\n{scan_note}"
    else:
        mo.notes = scan_note
    
    await db.commit()
    await db.refresh(mo)
    
    return {
        'id': mo.id,
        'voucher_number': mo.voucher_number,
        'barcode': barcode,
        'scan_type': scan_type,
        'action_taken': action_taken,
        'current_status': mo.production_status,
        'produced_quantity': mo.produced_quantity,
        'completion_percentage': mo.completion_percentage,
        'timestamp': datetime.now().isoformat()
    }

@router.get("/shop-floor/active-orders")
async def get_active_shop_floor_orders(
    department: Optional[str] = None,
    operator: Optional[str] = None,
    machine_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all active manufacturing orders for shop floor display.
    Filtered by department, operator, or machine.
    """
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.organization_id == current_user.organization_id,
        ManufacturingOrder.production_status.in_(['planned', 'in_progress'])
    )
    
    if department:
        stmt = stmt.where(ManufacturingOrder.production_department == department)
    
    if operator:
        stmt = stmt.where(ManufacturingOrder.assigned_operator == operator)
    
    if machine_id:
        stmt = stmt.where(ManufacturingOrder.machine_id == machine_id)
    
    stmt = stmt.order_by(ManufacturingOrder.priority.desc(), ManufacturingOrder.planned_start_date)
    
    result = await db.execute(stmt)
    orders = result.scalars().all()
    
    # Get BOM and product details for each order
    enriched_orders = []
    for mo in orders:
        stmt = select(BillOfMaterials).where(BillOfMaterials.id == mo.bom_id)
        result = await db.execute(stmt)
        bom = result.scalar_one_or_none()
        
        product_name = "Unknown"
        if bom:
            stmt = select(Product).where(Product.id == bom.output_item_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()
            if product:
                product_name = product.product_name
        
        enriched_orders.append({
            'id': mo.id,
            'voucher_number': mo.voucher_number,
            'product_name': product_name,
            'production_status': mo.production_status,
            'priority': mo.priority,
            'planned_quantity': mo.planned_quantity,
            'produced_quantity': mo.produced_quantity,
            'completion_percentage': mo.completion_percentage,
            'planned_start_date': mo.planned_start_date.isoformat() if mo.planned_start_date else None,
            'planned_end_date': mo.planned_end_date.isoformat() if mo.planned_end_date else None,
            'assigned_operator': mo.assigned_operator,
            'assigned_supervisor': mo.assigned_supervisor,
            'machine_id': mo.machine_id,
            'workstation_id': mo.workstation_id
        })
    
    return {
        'total_orders': len(enriched_orders),
        'filters_applied': {
            'department': department,
            'operator': operator,
            'machine_id': machine_id
        },
        'orders': enriched_orders
    }