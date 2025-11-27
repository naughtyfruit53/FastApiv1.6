# app/api/v1/manufacturing/inventory_adjustment.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import InventoryAdjustmentCreate, InventoryAdjustmentResponse

router = APIRouter(tags=["Inventory Adjustment"])

@router.post("", response_model=InventoryAdjustmentResponse)
async def create_inventory_adjustment(
    adjustment_data: InventoryAdjustmentCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_inventory_adjustment(db, org_id, adjustment_data)

# Add GET, etc.