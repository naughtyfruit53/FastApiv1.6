# app/api/v1/manufacturing/quality_control.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import QCTemplateCreate, QCTemplateResponse, QCInspectionCreate, QCInspectionResponse, RejectionCreate, RejectionResponse

router = APIRouter(tags=["Quality Control"])

@router.post("/templates", response_model=QCTemplateResponse)
async def create_qc_template(
    template_data: QCTemplateCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_qc_template(db, org_id, template_data)

@router.post("/inspections", response_model=QCInspectionResponse)
async def create_qc_inspection(
    inspection_data: QCInspectionCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_qc_inspection(db, org_id, inspection_data)

@router.post("/rejections", response_model=RejectionResponse)
async def create_rejection(
    rejection_data: RejectionCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    return await ProductionPlanningService.create_rejection(db, org_id, rejection_data)

# Add GET endpoints etc.