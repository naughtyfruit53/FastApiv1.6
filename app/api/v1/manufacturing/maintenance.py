# app/api/v1/manufacturing/maintenance.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import MachineCreate, MachineResponse, PreventiveMaintenanceScheduleCreate, BreakdownMaintenanceCreate  # Add others

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@router.get("/machines", response_model=List[MachineResponse])
async def get_machines(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.get_machines(db, org_id)

@router.post("/machines", response_model=MachineResponse)
async def create_machine(
    machine_data: MachineCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_machine(db, org_id, machine_data)

# Add similar for preventive, breakdown, etc.