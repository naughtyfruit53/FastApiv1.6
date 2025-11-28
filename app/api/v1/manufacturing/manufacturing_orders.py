# app/api/v1/manufacturing/manufacturing_orders.py
"""
Manufacturing Orders module - Handles manufacturing order CRUD and lifecycle operations
Extracted from monolithic manufacturing.py for better maintainability
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func  # UPDATED: Added func
from typing import List, Optional
from datetime import datetime, date  # NEW: Import date
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_planning import ManufacturingOrder, BillOfMaterials, BOMComponent  # FIXED: Use full path to manufacturing_planning.py and added BOMComponent for auto-debit section
from app.models.vouchers.manufacturing_planning import QCInspection, Machine, ProductionEntry  # UPDATED: Corrected path to vouchers.manufacturing_planning and added Machine
from app.services.voucher_service import VoucherNumberService
from app.services.mrp_service import MRPService
from app.services.production_planning_service import ProductionPlanningService
from app.services.inventory_service import InventoryService
from app.schemas.manufacturing import ManufacturingOrderCreate, ManufacturingOrderResponse, MachineCreate, MachineResponse, QCInspectionCreate, QCInspectionResponse, ProductionEntryCreate, ProductionEntryResponse, ManufacturingOrderUpdate, StatusUpdateSchema  # NEW: Added QCInspectionCreate and QCInspectionResponse
from app.services.notification_service import NotificationService  # NEW: For QC notify

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test")
async def test_manufacturing_orders():
    """Test endpoint to verify router registration"""
    logger.info("Test manufacturing orders endpoint accessed")
    return {"message": "Manufacturing orders router is registered"}

@router.get("/next-number")  # CHANGED: Removed /manufacturing-orders
async def get_next_manufacturing_order_number(
    voucher_date: Optional[date] = None,  # NEW: Add param
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Get next manufacturing order number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MO", org_id, ManufacturingOrder, voucher_date  # NEW: Pass date
        )
        logger.info(f"Generated next voucher number: {next_number} for organization {org_id}")
        return next_number
    except Exception as e:
        logger.error(f"Error generating voucher number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate voucher number")

@router.get("/check-backdated-conflict")  # CHANGED: Removed /manufacturing-orders
async def check_backdated_conflict(
    voucher_date: date,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Check for backdated voucher conflicts"""
    current_user, org_id = auth
    try:
        # Check if there are future vouchers
        stmt = select(func.count(ManufacturingOrder.id)).where(
            ManufacturingOrder.organization_id == org_id,
            ManufacturingOrder.date > voucher_date
        )
        result = await db.execute(stmt)
        future_count = result.scalar_one()
        
        has_conflict = future_count > 0
        return {
            "has_conflict": has_conflict,
            "future_count": future_count,
            "message": f"There are {future_count} future-dated orders that may conflict" if has_conflict else "No conflicts detected"
        }
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check backdated conflict")

@router.get("", response_model=List[ManufacturingOrderResponse])  # CHANGED: Removed /manufacturing-orders
async def get_manufacturing_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    include_deleted: bool = False,  # NEW: Param to include deleted
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Get list of manufacturing orders"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.organization_id == org_id
        )
        
        if status:
            stmt = stmt.where(ManufacturingOrder.production_status == status)
        
        if not include_deleted:
            stmt = stmt.where(ManufacturingOrder.is_deleted == False)  # NEW: Filter out deleted by default
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        orders = result.scalars().all()
        logger.info(f"Fetched {len(orders)} manufacturing orders for organization {org_id}")
        return orders
    except Exception as e:
        logger.error(f"Error fetching manufacturing orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch manufacturing orders")

@router.get("/machines", response_model=List[MachineResponse])
async def get_machines(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    stmt = select(Machine).where(Machine.organization_id == org_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{order_id}", response_model=ManufacturingOrderResponse)  # CHANGED: Removed /manufacturing-orders/
async def get_manufacturing_order(
    order_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Get specific manufacturing order"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == order_id,
            ManufacturingOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            logger.error(f"Manufacturing order {order_id} not found for organization {org_id}")
            raise HTTPException(status_code=404, detail="Manufacturing order not found")
        
        logger.info(f"Fetched manufacturing order {order_id} for organization {org_id}")
        return order
    except Exception as e:
        logger.error(f"Error fetching manufacturing order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch manufacturing order")

@router.get("/bom/{bom_id}/max-producible")  # NEW: Endpoint for max producible
async def get_max_producible(
    bom_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    try:
        max_p = await MRPService.calculate_max_producible(db, org_id, bom_id)
        return {"max_producible": max_p}
    except Exception as e:
        logger.error(f"Error calculating max producible for BOM {bom_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate max producible")

@router.get("/bom/{bom_id}/check-producible")  # NEW: Endpoint for check producible
async def check_producible(
    bom_id: int,
    quantity: float,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    try:
        info = await MRPService.check_producible(db, org_id, bom_id, quantity)
        return info
    except Exception as e:
        logger.error(f"Error checking producible for BOM {bom_id} quantity {quantity}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check producible")

@router.post("")  # CHANGED: Removed /manufacturing-orders
async def create_manufacturing_order(
    order_data: ManufacturingOrderCreate,
    check_material_availability: bool = True,
    auth: tuple = Depends(require_access("manufacturing", "write")),

    db: AsyncSession = Depends(get_db)
):
    """Create new manufacturing order"""
    current_user, org_id = auth
    try:
        # Verify BOM exists
        stmt = select(BillOfMaterials).where(
            BillOfMaterials.id == order_data.bom_id,
            BillOfMaterials.organization_id == org_id
        )
        result = await db.execute(stmt)
        bom = result.scalar_one_or_none()
        
        if not bom:
            logger.error(f"BOM {order_data.bom_id} not found for organization {org_id}")
            raise HTTPException(status_code=404, detail="BOM not found")
        
        # Generate voucher number
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MO", org_id, ManufacturingOrder
        )
        
        # Calculate estimated cost
        multiplier = order_data.planned_quantity / bom.output_quantity
        estimated_cost = bom.total_cost * multiplier
        
        db_order = ManufacturingOrder(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=order_data.date or datetime.now(),  # NEW: Use provided date or now
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
            sales_order_id=order_data.sales_order_id,
            is_deleted=False,  # NEW: Default to not deleted
            deletion_remark=None  # NEW: Default remark
        )
        
        db.add(db_order)
        await db.flush()
        
        material_check_result = None
        if check_material_availability:
            is_available, shortages = await MRPService.check_material_availability_for_mo(
                db, org_id, db_order.id
            )
            material_check_result = {
                'is_available': is_available,
                'shortages': shortages
            }
            if not is_available:
                logger.warning(
                    f"Manufacturing Order {voucher_number} created with material shortages: "
                    f"{len(shortages)} items short"
                )
        
        # NEW: Auto-debit if materials available
        if material_check_result and material_check_result['is_available']:
            stmt = select(BOMComponent).where(BOMComponent.bom_id == db_order.bom_id)
            result = await db.execute(stmt)
            components = result.scalars().all()
            
            multiplier = db_order.planned_quantity / bom.output_quantity
            
            for component in components:
                wastage_factor = 1 + (component.wastage_percentage / 100)
                required_qty = component.quantity_required * multiplier * wastage_factor
                await InventoryService.update_stock(db, org_id, component.component_item_id, -required_qty)
            
            logger.info(f"Auto-debited materials for Manufacturing Order {voucher_number}")
        
        await db.commit()
        await db.refresh(db_order)
        
        # NEW: Notify QC if completed
        if db_order.production_status == "completed":
            await NotificationService.send_notification(
                db, 
                org_id, 
                "QC Team", 
                "New batch ready for QC",
                f"Manufacturing Order {voucher_number} completed. Please perform QC."
            )
        
        logger.info(f"Created manufacturing order {voucher_number} for organization {org_id}")
        return {
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
    except Exception as e:
        logger.error(f"Error creating manufacturing order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create manufacturing order")

@router.post("/machines", response_model=MachineResponse)
async def create_machine(
    machine_data: MachineCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_machine(db, org_id, machine_data)

@router.patch("/{order_id}", response_model=ManufacturingOrderResponse)  # CHANGED: Removed /manufacturing-orders/
async def update_manufacturing_order(
    order_id: int,
    update_data: ManufacturingOrderUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update manufacturing order (including soft delete)"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == order_id,
            ManufacturingOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing order not found")
        
        # If soft deleting
        if update_data.is_deleted:
            if not update_data.deletion_remark:
                raise HTTPException(status_code=400, detail="Deletion remark is required for delete operation")
            order.is_deleted = True
            order.deletion_remark = update_data.deletion_remark
        else:
            # Regular update
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(order, field, value)
        
        order.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"Updated manufacturing order {order_id} for organization {org_id}")
        return order
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating manufacturing order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update manufacturing order")

@router.patch("/{order_id}/status", response_model=ManufacturingOrderResponse)  # CHANGED: Removed /manufacturing-orders/
async def update_manufacturing_order_status(
    order_id: int,
    status_data: StatusUpdateSchema,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update manufacturing order status"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == order_id,
            ManufacturingOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing order not found")
        
        if order.is_deleted:
            raise HTTPException(status_code=400, detail="Cannot update status of deleted order")
        
        order.production_status = status_data.status
        order.updated_at = datetime.now()
        
        # NEW: Notify on completion
        if status_data.status == "completed":
            await NotificationService.send_notification(
                db, 
                org_id, 
                "QC Team", 
                "New batch ready for QC",
                f"Manufacturing Order {order.voucher_number} completed. Please perform QC."
            )
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"Updated status for manufacturing order {order_id} to {status_data.status}")
        return order
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating status for order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update order status")

# NEW: Similar routes for preventive, breakdown, etc.
# Example for QC Inspection
@router.post("/qc-inspections", response_model=QCInspectionResponse)
async def create_qc_inspection(
    inspection_data: QCInspectionCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    db_inspection = QCInspection(**inspection_data.dict(), organization_id=org_id)
    db.add(db_inspection)
    await db.commit()
    await db.refresh(db_inspection)
    return db_inspection

# Add more as needed...