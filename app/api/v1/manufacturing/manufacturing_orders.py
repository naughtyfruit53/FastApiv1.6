# app/api/v1/manufacturing/manufacturing_orders.py
"""
Manufacturing Orders module - Handles manufacturing order CRUD and lifecycle operations
Extracted from monolithic manufacturing.py for better maintainability
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import ManufacturingOrder, BillOfMaterials
from app.services.voucher_service import VoucherNumberService
from app.services.mrp_service import MRPService
from .schemas import ManufacturingOrderCreate, ManufacturingOrderResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/manufacturing-orders", response_model=List[ManufacturingOrderResponse])
async def get_manufacturing_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of manufacturing orders"""
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
    """Get next manufacturing order number"""
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
    """Create new manufacturing order"""
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
    await db.flush()
    
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
        
        if not is_available:
            logger.warning(
                f"Manufacturing Order {voucher_number} created with material shortages: "
                f"{len(shortages)} items short"
            )
    
    await db.commit()
    await db.refresh(db_order)
    
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


@router.get("/manufacturing-orders/{order_id}", response_model=ManufacturingOrderResponse)
async def get_manufacturing_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get specific manufacturing order"""
    stmt = select(ManufacturingOrder).where(
        ManufacturingOrder.id == order_id,
        ManufacturingOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")
    
    return order


# Additional endpoints (complete, start, etc.) would go here but are kept in original file
# to minimize changes in this refactoring phase
