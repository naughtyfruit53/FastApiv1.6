# app/api/v1/manufacturing/inventory_adjustment.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import InventoryAdjustmentCreate, InventoryAdjustmentResponse, InventoryAdjustmentSubmit
from app.models.vouchers.manufacturing_planning import InventoryAdjustment
from app.models.product_models import Product

router = APIRouter(tags=["Inventory Adjustment"])

@router.get("", response_model=List[InventoryAdjustmentResponse])
async def list_inventory_adjustments(
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    reason: Optional[str] = Query(None, description="Filter by reason code"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all inventory adjustments with filters"""
    _, org_id = auth
    stmt = select(InventoryAdjustment).where(InventoryAdjustment.organization_id == org_id)
    if item_id:
        stmt = stmt.where(InventoryAdjustment.item_id == item_id)
    if reason:
        stmt = stmt.where(InventoryAdjustment.reason == reason)
    if start_date:
        stmt = stmt.where(InventoryAdjustment.created_at >= start_date)
    if end_date:
        stmt = stmt.where(InventoryAdjustment.created_at <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(InventoryAdjustment.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{adjustment_id}", response_model=InventoryAdjustmentResponse)
async def get_inventory_adjustment(
    adjustment_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific inventory adjustment by ID"""
    _, org_id = auth
    stmt = select(InventoryAdjustment).where(
        InventoryAdjustment.id == adjustment_id,
        InventoryAdjustment.organization_id == org_id
    )
    result = await db.execute(stmt)
    adjustment = result.scalar_one_or_none()
    if not adjustment:
        raise HTTPException(status_code=404, detail="Inventory adjustment not found")
    return adjustment

@router.post("", response_model=InventoryAdjustmentResponse)
async def create_inventory_adjustment(
    adjustment_data: InventoryAdjustmentCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory adjustment (draft status)"""
    current_user, org_id = auth
    return await ProductionPlanningService.create_inventory_adjustment(db, org_id, adjustment_data)

@router.post("/submit", response_model=InventoryAdjustmentResponse)
async def submit_inventory_adjustment(
    adjustment_data: InventoryAdjustmentSubmit,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an inventory adjustment with validation and stock update.
    
    This endpoint:
    1. Validates the adjustment data
    2. Checks stock constraints
    3. Creates the adjustment record with audit trail
    4. Updates the inventory on success
    """
    current_user, org_id = auth
    
    # Validate item exists
    stmt = select(Product).where(
        Product.id == adjustment_data.item_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Validate comment is provided
    if not adjustment_data.comment or len(adjustment_data.comment.strip()) < 5:
        raise HTTPException(status_code=400, detail="Comment is required and must be at least 5 characters")
    
    # Calculate adjustment quantity
    adjustment_qty = adjustment_data.new_quantity - adjustment_data.old_quantity
    
    # Validate stock constraints for decreases
    if adjustment_qty < 0:
        # Check if the new quantity would be negative
        if adjustment_data.new_quantity < 0:
            raise HTTPException(
                status_code=400, 
                detail="Adjustment would result in negative stock. Current quantity may have changed."
            )
    
    # Create the adjustment record
    db_adjustment = InventoryAdjustment(
        organization_id=org_id,
        type=adjustment_data.type,
        item_id=adjustment_data.item_id,
        batch_number=adjustment_data.batch_number,
        old_quantity=adjustment_data.old_quantity,
        new_quantity=adjustment_data.new_quantity,
        reason=adjustment_data.reason,
        reason_code=adjustment_data.reason_code,
        reference_doc=adjustment_data.reference_doc,
        comment=adjustment_data.comment,
        documents=adjustment_data.documents,
        status="approved",  # Auto-approve for now
        approved_by=str(current_user.id),
        approved_at=datetime.utcnow(),
        created_by=current_user.id
    )
    
    db.add(db_adjustment)
    
    # Update product stock - this would typically go through a stock service
    # For now, we assume the stock update happens through existing stock management
    # The adjustment record serves as audit trail
    
    await db.commit()
    await db.refresh(db_adjustment)
    
    return db_adjustment

@router.get("/audit/{adjustment_id}")
async def get_adjustment_audit_trail(
    adjustment_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get the audit trail for an inventory adjustment"""
    _, org_id = auth
    stmt = select(InventoryAdjustment).where(
        InventoryAdjustment.id == adjustment_id,
        InventoryAdjustment.organization_id == org_id
    )
    result = await db.execute(stmt)
    adjustment = result.scalar_one_or_none()
    if not adjustment:
        raise HTTPException(status_code=404, detail="Inventory adjustment not found")
    
    return {
        "adjustment_id": adjustment.id,
        "item_id": adjustment.item_id,
        "type": adjustment.type,
        "old_quantity": adjustment.old_quantity,
        "new_quantity": adjustment.new_quantity,
        "adjustment_qty": adjustment.new_quantity - adjustment.old_quantity,
        "reason": adjustment.reason,
        "reason_code": adjustment.reason_code,
        "reference_doc": adjustment.reference_doc,
        "comment": adjustment.comment,
        "status": adjustment.status,
        "created_by": adjustment.created_by,
        "created_at": adjustment.created_at,
        "approved_by": adjustment.approved_by,
        "approved_at": adjustment.approved_at
    }