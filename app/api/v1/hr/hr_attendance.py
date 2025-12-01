from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.hr_models import (
    AttendanceRecord, AttendancePolicy, Timesheet
)
from app.schemas.hr_schemas import (
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    AttendancePolicyCreate, AttendancePolicyUpdate, AttendancePolicyResponse,
    TimesheetCreate, TimesheetUpdate, TimesheetResponse
)

router = APIRouter(prefix="/hr", tags=["Human Resources - Attendance"])

# Attendance Management
@router.post("/attendance", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    attendance_data: AttendanceRecordCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create attendance record"""
    current_user, org_id = auth
   
    # Check if attendance record already exists for this date
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.organization_id == org_id,
            AttendanceRecord.employee_id == attendance_data.employee_id,
            AttendanceRecord.attendance_date == attendance_data.attendance_date
        )
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()
   
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this date"
        )
   
    attendance_record = AttendanceRecord(
        **attendance_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(attendance_record)
    await db.commit()
    await db.refresh(attendance_record)
   
    return attendance_record

@router.get("/attendance", response_model=List[AttendanceRecordResponse])
async def get_attendance_records(
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get attendance records with filtering"""
    current_user, org_id = auth
   
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.organization_id == org_id
    )
   
    # Apply filters
    if employee_id:
        stmt = stmt.where(AttendanceRecord.employee_id == employee_id)
   
    if start_date:
        stmt = stmt.where(AttendanceRecord.attendance_date >= start_date)
   
    if end_date:
        stmt = stmt.where(AttendanceRecord.attendance_date <= end_date)
   
    if status:
        stmt = stmt.where(AttendanceRecord.attendance_status == status)
   
    # Order by date (newest first)
    stmt = stmt.order_by(desc(AttendanceRecord.attendance_date))
   
    result = await db.execute(stmt.offset(skip).limit(limit))
    records = result.scalars().all()
    return records

@router.put("/attendance/{attendance_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    attendance_id: int,
    attendance_data: AttendanceRecordUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update attendance record"""
    current_user, org_id = auth
   
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.id == attendance_id,
            AttendanceRecord.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
   
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
   
    # Update fields
    for field, value in attendance_data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
   
    # Set approval details if being approved
    if attendance_data.is_approved is not None and attendance_data.is_approved:
        record.approved_by_id = current_user.id
        record.approved_at = datetime.utcnow()
   
    await db.commit()
    await db.refresh(record)
   
    return record

# ============================================================================
# Attendance Policy Management
# ============================================================================
@router.post("/attendance-policies", response_model=AttendancePolicyResponse)
async def create_attendance_policy(
    policy_data: AttendancePolicyCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new attendance policy"""
    current_user, org_id = auth
   
    # Check for unique code
    stmt = select(AttendancePolicy).where(
        and_(
            AttendancePolicy.organization_id == org_id,
            AttendancePolicy.code == policy_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Attendance policy code already exists")
   
    policy = AttendancePolicy(
        **policy_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
   
    return policy

@router.get("/attendance-policies", response_model=List[AttendancePolicyResponse])
async def get_attendance_policies(
    is_active: Optional[bool] = Query(default=None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all attendance policies"""
    current_user, org_id = auth
   
    stmt = select(AttendancePolicy).where(AttendancePolicy.organization_id == org_id)
   
    if is_active is not None:
        stmt = stmt.where(AttendancePolicy.is_active == is_active)
   
    stmt = stmt.order_by(AttendancePolicy.name)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/attendance-policies/{policy_id}", response_model=AttendancePolicyResponse)
async def update_attendance_policy(
    policy_id: int,
    policy_data: AttendancePolicyUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update attendance policy"""
    current_user, org_id = auth
   
    stmt = select(AttendancePolicy).where(
        and_(
            AttendancePolicy.id == policy_id,
            AttendancePolicy.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    policy = result.scalar_one_or_none()
   
    if not policy:
        raise HTTPException(status_code=404, detail="Attendance policy not found")
   
    for field, value in policy_data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
   
    await db.commit()
    await db.refresh(policy)
   
    return policy

# ============================================================================
# Timesheet Management
# ============================================================================
@router.get("/timesheets", response_model=List[TimesheetResponse])
async def get_timesheets(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get timesheets"""
    current_user, org_id = auth
   
    stmt = select(Timesheet).where(Timesheet.organization_id == org_id)
   
    if employee_id:
        stmt = stmt.where(Timesheet.employee_id == employee_id)
    if status:
        stmt = stmt.where(Timesheet.status == status)
   
    stmt = stmt.order_by(desc(Timesheet.period_start)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/timesheets", response_model=TimesheetResponse)
async def create_timesheet(
    timesheet_data: TimesheetCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new timesheet"""
    current_user, org_id = auth
   
    timesheet = Timesheet(
        **timesheet_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(timesheet)
    await db.commit()
    await db.refresh(timesheet)
   
    return timesheet

@router.put("/timesheets/{timesheet_id}/submit")
async def submit_timesheet(
    timesheet_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Submit a timesheet for approval"""
    current_user, org_id = auth
   
    stmt = select(Timesheet).where(
        and_(
            Timesheet.id == timesheet_id,
            Timesheet.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    timesheet = result.scalar_one_or_none()
   
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
   
    if timesheet.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft timesheets can be submitted")
   
    timesheet.status = "submitted"
    timesheet.submitted_at = datetime.now(timezone.utc)
   
    await db.commit()
   
    return {"message": "Timesheet submitted successfully"}

@router.put("/timesheets/{timesheet_id}/approve")
async def approve_timesheet(
    timesheet_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a submitted timesheet"""
    current_user, org_id = auth
   
    stmt = select(Timesheet).where(
        and_(
            Timesheet.id == timesheet_id,
            Timesheet.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    timesheet = result.scalar_one_or_none()
   
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
   
    if timesheet.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted timesheets can be approved")
   
    timesheet.status = "approved"
    timesheet.approved_by_id = current_user.id
    timesheet.approved_at = datetime.now(timezone.utc)
   
    await db.commit()
   
    return {"message": "Timesheet approved successfully"}
