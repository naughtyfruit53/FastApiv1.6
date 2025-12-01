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
    HRAnalyticsSnapshot, PositionBudget, EmployeeTransfer, IntegrationAdapter
)
from app.schemas.hr_schemas import (
    HRAnalyticsSnapshotResponse,
    PositionBudgetCreate, PositionBudgetUpdate, PositionBudgetResponse,
    EmployeeTransferCreate, EmployeeTransferUpdate, EmployeeTransferResponse,
    IntegrationAdapterCreate, IntegrationAdapterUpdate, IntegrationAdapterResponse
)

router = APIRouter(prefix="/hr", tags=["Human Resources - Advanced"])

# ============================================================================
# Phase 4 Scaffolding: Analytics, Position Budgeting, Transfers
# (Feature-flagged endpoints)
# ============================================================================
@router.get("/analytics/snapshots", response_model=List[HRAnalyticsSnapshotResponse])
async def get_hr_analytics_snapshots(
    snapshot_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get HR analytics snapshots (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(HRAnalyticsSnapshot).where(HRAnalyticsSnapshot.organization_id == org_id)
   
    if snapshot_type:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_type == snapshot_type)
    if start_date:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_date >= start_date)
    if end_date:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_date <= end_date)
   
    stmt = stmt.order_by(desc(HRAnalyticsSnapshot.snapshot_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/position-budgets", response_model=List[PositionBudgetResponse])
async def get_position_budgets(
    fiscal_year: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get position budgets (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(PositionBudget).where(PositionBudget.organization_id == org_id)
   
    if fiscal_year:
        stmt = stmt.where(PositionBudget.fiscal_year == fiscal_year)
    if department_id:
        stmt = stmt.where(PositionBudget.department_id == department_id)
    if status:
        stmt = stmt.where(PositionBudget.status == status)
   
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/position-budgets", response_model=PositionBudgetResponse)
async def create_position_budget(
    budget_data: PositionBudgetCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new position budget (Feature-flagged)"""
    current_user, org_id = auth
   
    budget = PositionBudget(
        **budget_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
   
    return budget

@router.get("/employee-transfers", response_model=List[EmployeeTransferResponse])
async def get_employee_transfers(
    employee_id: Optional[int] = Query(None),
    transfer_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get employee transfers (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(EmployeeTransfer).where(EmployeeTransfer.organization_id == org_id)
   
    if employee_id:
        stmt = stmt.where(EmployeeTransfer.employee_id == employee_id)
    if transfer_type:
        stmt = stmt.where(EmployeeTransfer.transfer_type == transfer_type)
    if status:
        stmt = stmt.where(EmployeeTransfer.status == status)
   
    stmt = stmt.order_by(desc(EmployeeTransfer.effective_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/employee-transfers", response_model=EmployeeTransferResponse)
async def create_employee_transfer(
    transfer_data: EmployeeTransferCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new employee transfer (Feature-flagged)"""
    current_user, org_id = auth
   
    transfer = EmployeeTransfer(
        **transfer_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
   
    return transfer

@router.put("/employee-transfers/{transfer_id}/approve")
async def approve_employee_transfer(
    transfer_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve an employee transfer (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(EmployeeTransfer).where(
        and_(
            EmployeeTransfer.id == transfer_id,
            EmployeeTransfer.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    transfer = result.scalar_one_or_none()
   
    if not transfer:
        raise HTTPException(status_code=404, detail="Employee transfer not found")
   
    if transfer.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending transfers can be approved")
   
    transfer.status = "approved"
    transfer.approved_by_id = current_user.id
    transfer.approved_at = datetime.now(timezone.utc)
   
    await db.commit()
   
    return {"message": "Employee transfer approved successfully"}

# ============================================================================
# Integration Adapters (Feature-flagged)
# ============================================================================
@router.get("/integration-adapters", response_model=List[IntegrationAdapterResponse])
async def get_integration_adapters(
    adapter_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get integration adapters (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(IntegrationAdapter).where(IntegrationAdapter.organization_id == org_id)
   
    if adapter_type:
        stmt = stmt.where(IntegrationAdapter.adapter_type == adapter_type)
    if is_active is not None:
        stmt = stmt.where(IntegrationAdapter.is_active == is_active)
   
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/integration-adapters", response_model=IntegrationAdapterResponse)
async def create_integration_adapter(
    adapter_data: IntegrationAdapterCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration adapter (Feature-flagged)"""
    current_user, org_id = auth
   
    # Check for unique adapter type + provider combination
    stmt = select(IntegrationAdapter).where(
        and_(
            IntegrationAdapter.organization_id == org_id,
            IntegrationAdapter.adapter_type == adapter_data.adapter_type,
            IntegrationAdapter.provider == adapter_data.provider
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Integration adapter already exists for this type and provider")
   
    adapter = IntegrationAdapter(
        **adapter_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(adapter)
    await db.commit()
    await db.refresh(adapter)
   
    return adapter

@router.put("/integration-adapters/{adapter_id}", response_model=IntegrationAdapterResponse)
async def update_integration_adapter(
    adapter_id: int,
    adapter_data: IntegrationAdapterUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update integration adapter (Feature-flagged)"""
    current_user, org_id = auth
   
    stmt = select(IntegrationAdapter).where(
        and_(
            IntegrationAdapter.id == adapter_id,
            IntegrationAdapter.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    adapter = result.scalar_one_or_none()
   
    if not adapter:
        raise HTTPException(status_code=404, detail="Integration adapter not found")
   
    for field, value in adapter_data.model_dump(exclude_unset=True).items():
        setattr(adapter, field, value)
   
    await db.commit()
    await db.refresh(adapter)
   
    return adapter
