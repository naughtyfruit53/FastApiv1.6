# app/api/v1/manufacturing/quality_control.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import csv
import io
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import (
    QCTemplateCreate, QCTemplateResponse, QCTemplateUpdate,
    QCInspectionCreate, QCInspectionResponse, QCInspectionUpdate,
    RejectionCreate, RejectionResponse, RejectionUpdate
)
from app.models.vouchers.manufacturing_planning import QCTemplate, QCInspection, Rejection

router = APIRouter(tags=["Quality Control"])

# ==================== QC TEMPLATES ====================

@router.get("/templates", response_model=List[QCTemplateResponse])
async def list_qc_templates(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all QC templates with optional filters"""
    _, org_id = auth
    stmt = select(QCTemplate).where(QCTemplate.organization_id == org_id)
    if product_id is not None:
        stmt = stmt.where(QCTemplate.product_id == product_id)
    if is_active is not None:
        stmt = stmt.where(QCTemplate.is_active == is_active)
    stmt = stmt.offset(skip).limit(limit).order_by(QCTemplate.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/templates/{template_id}", response_model=QCTemplateResponse)
async def get_qc_template(
    template_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific QC template by ID"""
    _, org_id = auth
    stmt = select(QCTemplate).where(
        QCTemplate.id == template_id,
        QCTemplate.organization_id == org_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="QC template not found")
    return template

@router.post("/templates", response_model=QCTemplateResponse)
async def create_qc_template(
    template_data: QCTemplateCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new QC template"""
    current_user, org_id = auth
    return await ProductionPlanningService.create_qc_template(db, org_id, template_data)

@router.put("/templates/{template_id}", response_model=QCTemplateResponse)
async def update_qc_template(
    template_id: int,
    template_data: QCTemplateUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a QC template"""
    _, org_id = auth
    stmt = select(QCTemplate).where(
        QCTemplate.id == template_id,
        QCTemplate.organization_id == org_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="QC template not found")
    
    update_data = template_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    
    await db.commit()
    await db.refresh(template)
    return template

@router.delete("/templates/{template_id}")
async def delete_qc_template(
    template_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a QC template (soft delete by setting inactive)"""
    _, org_id = auth
    stmt = select(QCTemplate).where(
        QCTemplate.id == template_id,
        QCTemplate.organization_id == org_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="QC template not found")
    
    template.is_active = False
    await db.commit()
    return {"message": "QC template deactivated successfully"}

# ==================== QC INSPECTIONS ====================

@router.get("/inspections", response_model=List[QCInspectionResponse])
async def list_qc_inspections(
    status: Optional[str] = Query(None, description="Filter by workflow status (draft/in_progress/completed)"),
    overall_status: Optional[str] = Query(None, description="Filter by result status (pass/fail/pending)"),
    work_order_id: Optional[int] = Query(None, description="Filter by work order ID"),
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all QC inspections with filters"""
    _, org_id = auth
    stmt = select(QCInspection).where(QCInspection.organization_id == org_id)
    if status is not None:
        stmt = stmt.where(QCInspection.status == status)
    if overall_status is not None:
        stmt = stmt.where(QCInspection.overall_status == overall_status)
    if work_order_id is not None:
        stmt = stmt.where(QCInspection.work_order_id == work_order_id)
    if item_id is not None:
        stmt = stmt.where(QCInspection.item_id == item_id)
    if start_date is not None:
        stmt = stmt.where(QCInspection.created_at >= start_date)
    if end_date is not None:
        stmt = stmt.where(QCInspection.created_at <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(QCInspection.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/inspections/{inspection_id}", response_model=QCInspectionResponse)
async def get_qc_inspection(
    inspection_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific QC inspection by ID"""
    _, org_id = auth
    stmt = select(QCInspection).where(
        QCInspection.id == inspection_id,
        QCInspection.organization_id == org_id
    )
    result = await db.execute(stmt)
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="QC inspection not found")
    return inspection

@router.post("/inspections", response_model=QCInspectionResponse)
async def create_qc_inspection(
    inspection_data: QCInspectionCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new QC inspection"""
    current_user, org_id = auth
    return await ProductionPlanningService.create_qc_inspection(db, org_id, inspection_data)

@router.put("/inspections/{inspection_id}", response_model=QCInspectionResponse)
async def update_qc_inspection(
    inspection_id: int,
    inspection_data: QCInspectionUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a QC inspection"""
    _, org_id = auth
    stmt = select(QCInspection).where(
        QCInspection.id == inspection_id,
        QCInspection.organization_id == org_id
    )
    result = await db.execute(stmt)
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="QC inspection not found")
    
    update_data = inspection_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inspection, key, value)
    
    await db.commit()
    await db.refresh(inspection)
    return inspection

@router.post("/inspections/{inspection_id}/sign-off")
async def sign_off_inspection(
    inspection_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Sign off on a QC inspection"""
    current_user, org_id = auth
    stmt = select(QCInspection).where(
        QCInspection.id == inspection_id,
        QCInspection.organization_id == org_id
    )
    result = await db.execute(stmt)
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="QC inspection not found")
    
    inspection.signed_off_by = current_user.id
    inspection.signed_off_at = datetime.now(timezone.utc)
    inspection.status = "completed"
    await db.commit()
    return {"message": "Inspection signed off successfully"}

# ==================== REJECTIONS ====================

@router.get("/rejections", response_model=List[RejectionResponse])
async def list_rejections(
    work_order_id: Optional[int] = Query(None, description="Filter by work order ID"),
    disposition: Optional[str] = Query(None, description="Filter by disposition (rework/scrap/return)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all rejections with filters"""
    _, org_id = auth
    stmt = select(Rejection).where(Rejection.organization_id == org_id)
    if work_order_id is not None:
        stmt = stmt.where(Rejection.work_order_id == work_order_id)
    if disposition is not None:
        stmt = stmt.where(Rejection.disposition == disposition)
    if start_date is not None:
        stmt = stmt.where(Rejection.created_at >= start_date)
    if end_date is not None:
        stmt = stmt.where(Rejection.created_at <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(Rejection.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/rejections/{rejection_id}", response_model=RejectionResponse)
async def get_rejection(
    rejection_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific rejection by ID"""
    _, org_id = auth
    stmt = select(Rejection).where(
        Rejection.id == rejection_id,
        Rejection.organization_id == org_id
    )
    result = await db.execute(stmt)
    rejection = result.scalar_one_or_none()
    if not rejection:
        raise HTTPException(status_code=404, detail="Rejection not found")
    return rejection

@router.post("/rejections", response_model=RejectionResponse)
async def create_rejection(
    rejection_data: RejectionCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new rejection record"""
    current_user, org_id = auth
    return await ProductionPlanningService.create_rejection(db, org_id, rejection_data)

@router.put("/rejections/{rejection_id}", response_model=RejectionResponse)
async def update_rejection(
    rejection_id: int,
    rejection_data: RejectionUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a rejection record"""
    _, org_id = auth
    stmt = select(Rejection).where(
        Rejection.id == rejection_id,
        Rejection.organization_id == org_id
    )
    result = await db.execute(stmt)
    rejection = result.scalar_one_or_none()
    if not rejection:
        raise HTTPException(status_code=404, detail="Rejection not found")
    
    update_data = rejection_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rejection, key, value)
    
    await db.commit()
    await db.refresh(rejection)
    return rejection

@router.post("/rejections/{rejection_id}/approve")
async def approve_rejection(
    rejection_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a rejection record"""
    current_user, org_id = auth
    stmt = select(Rejection).where(
        Rejection.id == rejection_id,
        Rejection.organization_id == org_id
    )
    result = await db.execute(stmt)
    rejection = result.scalar_one_or_none()
    if not rejection:
        raise HTTPException(status_code=404, detail="Rejection not found")
    
    rejection.approved_by = current_user.id
    rejection.approved_at = datetime.now(timezone.utc)
    rejection.approval_status = "approved"
    await db.commit()
    return {"message": "Rejection approved successfully"}

@router.get("/rejections/export/csv")
async def export_rejections_csv(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Export rejections to CSV"""
    _, org_id = auth
    stmt = select(Rejection).where(Rejection.organization_id == org_id)
    if start_date:
        stmt = stmt.where(Rejection.created_at >= start_date)
    if end_date:
        stmt = stmt.where(Rejection.created_at <= end_date)
    result = await db.execute(stmt)
    rejections = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "QC Inspection ID", "Reason", "Quantity", "Disposition", "NCR Reference", "Rework Required", "Created At"])
    for r in rejections:
        writer.writerow([r.id, r.qc_inspection_id, r.reason, r.quantity, r.disposition, r.ncr_reference, r.rework_required, r.created_at])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rejections_export.csv"}
    )