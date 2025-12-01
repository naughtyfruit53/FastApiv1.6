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
    LeaveType, LeaveApplication, LeaveBalance
)
from app.schemas.hr_schemas import (
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse,
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse,
    LeaveBalanceCreate, LeaveBalanceUpdate, LeaveBalanceResponse
)

router = APIRouter(prefix="/hr", tags=["Human Resources - Leave"])

# Leave Type Management
@router.post("/leave-types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type_data: LeaveTypeCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new leave type"""
    current_user, org_id = auth
   
    # Check if leave type code is unique within organization
    stmt = select(LeaveType).where(
        and_(
            LeaveType.organization_id == org_id,
            LeaveType.code == leave_type_data.code
        )
    )
    result = await db.execute(stmt)
    existing_code = result.scalar_one_or_none()
   
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type code already exists"
        )
   
    leave_type = LeaveType(
        **leave_type_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(leave_type)
    await db.commit()
    await db.refresh(leave_type)
   
    return leave_type

@router.get("/leave-types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    is_active: Optional[bool] = Query(default=None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all leave types"""
    current_user, org_id = auth
   
    stmt = select(LeaveType).where(
        LeaveType.organization_id == org_id
    )
   
    if is_active is not None:
        stmt = stmt.where(LeaveType.is_active == is_active)
   
    result = await db.execute(stmt.order_by(LeaveType.name))
    leave_types = result.scalars().all()
    return leave_types

# Leave Application Management
@router.post("/leave-applications", response_model=LeaveApplicationResponse)
async def create_leave_application(
    leave_data: LeaveApplicationCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new leave application"""
    current_user, org_id = auth
   
    leave_application = LeaveApplication(
        **leave_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(leave_application)
    await db.commit()
    await db.refresh(leave_application)
   
    return leave_application

@router.get("/leave-applications", response_model=List[LeaveApplicationResponse])
async def get_leave_applications(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get leave applications with filtering"""
    current_user, org_id = auth
   
    stmt = select(LeaveApplication).where(
        LeaveApplication.organization_id == org_id
    )
   
    # Apply filters
    if employee_id:
        stmt = stmt.where(LeaveApplication.employee_id == employee_id)
   
    if status:
        stmt = stmt.where(LeaveApplication.status == status)
   
    if start_date:
        stmt = stmt.where(LeaveApplication.start_date >= start_date)
   
    if end_date:
        stmt = stmt.where(LeaveApplication.end_date <= end_date)
   
    # Order by application date (newest first)
    stmt = stmt.order_by(desc(LeaveApplication.applied_date))
   
    result = await db.execute(stmt.offset(skip).limit(limit))
    applications = result.scalars().all()
    return applications

@router.put("/leave-applications/{application_id}/approve")
async def approve_leave_application(
    application_id: int,
    approval_remarks: Optional[str] = None,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a leave application"""
    current_user, org_id = auth
   
    stmt = select(LeaveApplication).where(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
   
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
   
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending applications can be approved"
        )
   
    application.status = "approved"
    application.approved_by_id = current_user.id
    application.approved_date = datetime.utcnow()
    application.approval_remarks = approval_remarks
   
    await db.commit()
   
    return {"message": "Leave application approved successfully"}

@router.put("/leave-applications/{application_id}/reject")
async def reject_leave_application(
    application_id: int,
    approval_remarks: str,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Reject a leave application"""
    current_user, org_id = auth
   
    stmt = select(LeaveApplication).where(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
   
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
   
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending applications can be rejected"
        )
   
    application.status = "rejected"
    application.approved_by_id = current_user.id
    application.approved_date = datetime.utcnow()
    application.approval_remarks = approval_remarks
   
    await db.commit()
   
    return {"message": "Leave application rejected successfully"}

# ============================================================================
# Leave Balance Management
# ============================================================================
@router.get("/leave-balances", response_model=List[LeaveBalanceResponse])
async def get_leave_balances(
    employee_id: Optional[int] = Query(None),
    leave_type_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get leave balances for employees"""
    current_user, org_id = auth
   
    stmt = select(LeaveBalance).where(LeaveBalance.organization_id == org_id)
   
    if employee_id:
        stmt = stmt.where(LeaveBalance.employee_id == employee_id)
    if leave_type_id:
        stmt = stmt.where(LeaveBalance.leave_type_id == leave_type_id)
    if year:
        stmt = stmt.where(LeaveBalance.year == year)
   
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/leave-balances", response_model=LeaveBalanceResponse)
async def create_leave_balance(
    balance_data: LeaveBalanceCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create or update leave balance for an employee"""
    current_user, org_id = auth
   
    # Check if balance already exists
    stmt = select(LeaveBalance).where(
        and_(
            LeaveBalance.organization_id == org_id,
            LeaveBalance.employee_id == balance_data.employee_id,
            LeaveBalance.leave_type_id == balance_data.leave_type_id,
            LeaveBalance.year == balance_data.year
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
   
    if existing:
        # Update existing balance
        for field, value in balance_data.model_dump(exclude={'employee_id', 'leave_type_id', 'year'}).items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing
   
    balance = LeaveBalance(
        **balance_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(balance)
    await db.commit()
    await db.refresh(balance)
   
    return balance
