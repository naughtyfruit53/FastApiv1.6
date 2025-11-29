# app/api/v1/manufacturing/maintenance.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import csv
import io
from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.production_planning_service import ProductionPlanningService
from app.schemas.manufacturing import (
    MachineCreate, MachineResponse, MachineUpdate,
    PreventiveMaintenanceScheduleCreate, PreventiveMaintenanceScheduleResponse, PreventiveMaintenanceScheduleUpdate,
    BreakdownMaintenanceCreate, BreakdownMaintenanceResponse, BreakdownMaintenanceUpdate,
    MachinePerformanceLogCreate, MachinePerformanceLogResponse,
    SparePartCreate, SparePartResponse, SparePartUpdate
)
from app.models.vouchers.manufacturing_planning import (
    Machine, PreventiveMaintenanceSchedule, BreakdownMaintenance,
    MachinePerformanceLog, SparePart
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

# ==================== MACHINE MASTER ====================

@router.get("/machines", response_model=List[MachineResponse])
async def list_machines(
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all machines with optional filters"""
    _, org_id = auth
    stmt = select(Machine).where(Machine.organization_id == org_id)
    if location:
        stmt = stmt.where(Machine.location == location)
    if status:
        stmt = stmt.where(Machine.status == status)
    stmt = stmt.offset(skip).limit(limit).order_by(Machine.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/machines/{machine_id}", response_model=MachineResponse)
async def get_machine(
    machine_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific machine by ID"""
    _, org_id = auth
    stmt = select(Machine).where(
        Machine.id == machine_id,
        Machine.organization_id == org_id
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.post("/machines", response_model=MachineResponse)
async def create_machine(
    machine_data: MachineCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new machine"""
    _, org_id = auth
    return await ProductionPlanningService.create_machine(db, org_id, machine_data)

@router.put("/machines/{machine_id}", response_model=MachineResponse)
async def update_machine(
    machine_id: int,
    machine_data: MachineUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a machine"""
    _, org_id = auth
    stmt = select(Machine).where(
        Machine.id == machine_id,
        Machine.organization_id == org_id
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    update_data = machine_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(machine, key, value)
    
    await db.commit()
    await db.refresh(machine)
    return machine

@router.delete("/machines/{machine_id}")
async def delete_machine(
    machine_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a machine (soft delete)"""
    _, org_id = auth
    stmt = select(Machine).where(
        Machine.id == machine_id,
        Machine.organization_id == org_id
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine.status = "inactive"
    await db.commit()
    return {"message": "Machine deactivated successfully"}

# ==================== PREVENTIVE MAINTENANCE SCHEDULES ====================

@router.get("/preventive-schedules", response_model=List[PreventiveMaintenanceScheduleResponse])
async def list_preventive_schedules(
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    overdue: Optional[bool] = Query(None, description="Filter by overdue status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all preventive maintenance schedules"""
    _, org_id = auth
    stmt = select(PreventiveMaintenanceSchedule).where(PreventiveMaintenanceSchedule.organization_id == org_id)
    if machine_id:
        stmt = stmt.where(PreventiveMaintenanceSchedule.machine_id == machine_id)
    if overdue is not None:
        stmt = stmt.where(PreventiveMaintenanceSchedule.overdue == overdue)
    stmt = stmt.offset(skip).limit(limit).order_by(PreventiveMaintenanceSchedule.next_due_date.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/preventive-schedules/{schedule_id}", response_model=PreventiveMaintenanceScheduleResponse)
async def get_preventive_schedule(
    schedule_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific preventive maintenance schedule"""
    _, org_id = auth
    stmt = select(PreventiveMaintenanceSchedule).where(
        PreventiveMaintenanceSchedule.id == schedule_id,
        PreventiveMaintenanceSchedule.organization_id == org_id
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Preventive schedule not found")
    return schedule

@router.post("/preventive-schedules", response_model=PreventiveMaintenanceScheduleResponse)
async def create_preventive_schedule(
    schedule_data: PreventiveMaintenanceScheduleCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new preventive maintenance schedule"""
    _, org_id = auth
    return await ProductionPlanningService.create_preventive_schedule(db, org_id, schedule_data)

@router.put("/preventive-schedules/{schedule_id}", response_model=PreventiveMaintenanceScheduleResponse)
async def update_preventive_schedule(
    schedule_id: int,
    schedule_data: PreventiveMaintenanceScheduleUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a preventive maintenance schedule"""
    _, org_id = auth
    stmt = select(PreventiveMaintenanceSchedule).where(
        PreventiveMaintenanceSchedule.id == schedule_id,
        PreventiveMaintenanceSchedule.organization_id == org_id
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Preventive schedule not found")
    
    update_data = schedule_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)
    
    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.post("/preventive-schedules/{schedule_id}/complete")
async def complete_preventive_maintenance(
    schedule_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Mark a preventive maintenance task as completed"""
    _, org_id = auth
    stmt = select(PreventiveMaintenanceSchedule).where(
        PreventiveMaintenanceSchedule.id == schedule_id,
        PreventiveMaintenanceSchedule.organization_id == org_id
    )
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Preventive schedule not found")
    
    schedule.last_completed_at = datetime.utcnow()
    schedule.overdue = False
    # Update next due date based on frequency
    await db.commit()
    return {"message": "Preventive maintenance completed successfully"}

# ==================== BREAKDOWN MAINTENANCE ====================

@router.get("/breakdowns", response_model=List[BreakdownMaintenanceResponse])
async def list_breakdowns(
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    status: Optional[str] = Query(None, description="Filter by status (open/closed)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all breakdown maintenance records"""
    _, org_id = auth
    stmt = select(BreakdownMaintenance).where(BreakdownMaintenance.organization_id == org_id)
    if machine_id:
        stmt = stmt.where(BreakdownMaintenance.machine_id == machine_id)
    if status:
        stmt = stmt.where(BreakdownMaintenance.status == status)
    if start_date:
        stmt = stmt.where(BreakdownMaintenance.date >= start_date)
    if end_date:
        stmt = stmt.where(BreakdownMaintenance.date <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(BreakdownMaintenance.date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/breakdowns/{breakdown_id}", response_model=BreakdownMaintenanceResponse)
async def get_breakdown(
    breakdown_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific breakdown record"""
    _, org_id = auth
    stmt = select(BreakdownMaintenance).where(
        BreakdownMaintenance.id == breakdown_id,
        BreakdownMaintenance.organization_id == org_id
    )
    result = await db.execute(stmt)
    breakdown = result.scalar_one_or_none()
    if not breakdown:
        raise HTTPException(status_code=404, detail="Breakdown record not found")
    return breakdown

@router.post("/breakdowns", response_model=BreakdownMaintenanceResponse)
async def create_breakdown(
    breakdown_data: BreakdownMaintenanceCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new breakdown maintenance record"""
    _, org_id = auth
    return await ProductionPlanningService.create_breakdown(db, org_id, breakdown_data)

@router.put("/breakdowns/{breakdown_id}", response_model=BreakdownMaintenanceResponse)
async def update_breakdown(
    breakdown_id: int,
    breakdown_data: BreakdownMaintenanceUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a breakdown record"""
    _, org_id = auth
    stmt = select(BreakdownMaintenance).where(
        BreakdownMaintenance.id == breakdown_id,
        BreakdownMaintenance.organization_id == org_id
    )
    result = await db.execute(stmt)
    breakdown = result.scalar_one_or_none()
    if not breakdown:
        raise HTTPException(status_code=404, detail="Breakdown record not found")
    
    update_data = breakdown_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(breakdown, key, value)
    
    await db.commit()
    await db.refresh(breakdown)
    return breakdown

@router.post("/breakdowns/{breakdown_id}/close")
async def close_breakdown(
    breakdown_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Close a breakdown record"""
    _, org_id = auth
    stmt = select(BreakdownMaintenance).where(
        BreakdownMaintenance.id == breakdown_id,
        BreakdownMaintenance.organization_id == org_id
    )
    result = await db.execute(stmt)
    breakdown = result.scalar_one_or_none()
    if not breakdown:
        raise HTTPException(status_code=404, detail="Breakdown record not found")
    
    breakdown.status = "closed"
    breakdown.end_time = datetime.utcnow()
    await db.commit()
    return {"message": "Breakdown closed successfully"}

# ==================== PERFORMANCE LOGS ====================

@router.get("/performance-logs", response_model=List[MachinePerformanceLogResponse])
async def list_performance_logs(
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all performance logs"""
    _, org_id = auth
    stmt = select(MachinePerformanceLog).where(MachinePerformanceLog.organization_id == org_id)
    if machine_id:
        stmt = stmt.where(MachinePerformanceLog.machine_id == machine_id)
    if start_date:
        stmt = stmt.where(MachinePerformanceLog.date >= start_date)
    if end_date:
        stmt = stmt.where(MachinePerformanceLog.date <= end_date)
    stmt = stmt.offset(skip).limit(limit).order_by(MachinePerformanceLog.date.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/performance-logs", response_model=MachinePerformanceLogResponse)
async def create_performance_log(
    log_data: MachinePerformanceLogCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new performance log entry"""
    _, org_id = auth
    return await ProductionPlanningService.create_performance_log(db, org_id, log_data)

@router.get("/performance-logs/export/csv")
async def export_performance_logs_csv(
    machine_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Export performance logs to CSV"""
    _, org_id = auth
    stmt = select(MachinePerformanceLog).where(MachinePerformanceLog.organization_id == org_id)
    if machine_id:
        stmt = stmt.where(MachinePerformanceLog.machine_id == machine_id)
    if start_date:
        stmt = stmt.where(MachinePerformanceLog.date >= start_date)
    if end_date:
        stmt = stmt.where(MachinePerformanceLog.date <= end_date)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Machine ID", "Date", "Runtime Hours", "Idle Hours", "Efficiency %", "Error Codes"])
    for log in logs:
        writer.writerow([log.id, log.machine_id, log.date, log.runtime_hours, log.idle_hours, log.efficiency_percentage, log.error_codes])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=performance_logs_export.csv"}
    )

# ==================== SPARE PARTS ====================

@router.get("/spare-parts", response_model=List[SparePartResponse])
async def list_spare_parts(
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all spare parts"""
    _, org_id = auth
    stmt = select(SparePart).where(SparePart.organization_id == org_id)
    if machine_id:
        stmt = stmt.where(SparePart.machine_id == machine_id)
    if low_stock:
        stmt = stmt.where(SparePart.quantity <= SparePart.reorder_level)
    stmt = stmt.offset(skip).limit(limit).order_by(SparePart.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
async def get_spare_part(
    spare_part_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific spare part"""
    _, org_id = auth
    stmt = select(SparePart).where(
        SparePart.id == spare_part_id,
        SparePart.organization_id == org_id
    )
    result = await db.execute(stmt)
    spare_part = result.scalar_one_or_none()
    if not spare_part:
        raise HTTPException(status_code=404, detail="Spare part not found")
    return spare_part

@router.post("/spare-parts", response_model=SparePartResponse)
async def create_spare_part(
    spare_data: SparePartCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new spare part"""
    _, org_id = auth
    return await ProductionPlanningService.create_spare_part(db, org_id, spare_data)

@router.put("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
async def update_spare_part(
    spare_part_id: int,
    spare_data: SparePartUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a spare part"""
    _, org_id = auth
    stmt = select(SparePart).where(
        SparePart.id == spare_part_id,
        SparePart.organization_id == org_id
    )
    result = await db.execute(stmt)
    spare_part = result.scalar_one_or_none()
    if not spare_part:
        raise HTTPException(status_code=404, detail="Spare part not found")
    
    update_data = spare_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(spare_part, key, value)
    
    await db.commit()
    await db.refresh(spare_part)
    return spare_part

@router.get("/spare-parts/alerts/reorder")
async def get_reorder_alerts(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get spare parts that need reordering"""
    _, org_id = auth
    stmt = select(SparePart).where(
        SparePart.organization_id == org_id,
        SparePart.quantity <= SparePart.reorder_level
    )
    result = await db.execute(stmt)
    spare_parts = result.scalars().all()
    return {"count": len(spare_parts), "items": spare_parts}