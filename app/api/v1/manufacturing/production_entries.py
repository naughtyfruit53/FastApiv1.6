# app/api/v1/manufacturing/production_entries.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func  # UPDATED: Added func
from typing import List, Optional
from datetime import datetime, date
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.schemas.manufacturing import (
    ProductionEntryCreate,
    ProductionEntryUpdate,
    ProductionEntryResponse,
    StatusUpdateSchema
)
from app.services.voucher_service import VoucherNumberService
from app.models.vouchers.manufacturing_operations import ProductionEntry, ProductionEntryConsumption
from app.core.enforcement import require_access
from app.api.v1.manufacturing.manufacturing_orders import update_manufacturing_order_status  # Reuse status update if needed

logger = logging.getLogger(__name__)

router = APIRouter(tags=["production-entries"])

@router.get("/test")
async def test_production_entries():
    """Test endpoint to verify router registration"""
    logger.info("Test production entries endpoint accessed")
    return {"message": "Production entries router is registered"}

@router.get("/next-number")
async def get_next_production_entry_number(
    voucher_date: Optional[date] = None,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next production entry number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "PE", org_id, ProductionEntry, voucher_date
        )
        logger.info(f"Generated next voucher number: {next_number} for organization {org_id}")
        return next_number
    except Exception as e:
        logger.error(f"Error generating voucher number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate voucher number")

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: date,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Check for backdated voucher conflicts"""
    current_user, org_id = auth
    try:
        # Check if there are future vouchers
        stmt = select(func.count(ProductionEntry.id)).where(
            ProductionEntry.organization_id == org_id,
            ProductionEntry.date > voucher_date
        )
        result = await db.execute(stmt)
        future_count = result.scalar_one()
        
        has_conflict = future_count > 0
        return {
            "has_conflict": has_conflict,
            "future_count": future_count,
            "message": f"There are {future_count} future-dated entries that may conflict" if has_conflict else "No conflicts detected"
        }
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check backdated conflict")

@router.get("", response_model=List[ProductionEntryResponse])
async def get_production_entries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    include_deleted: bool = False,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get list of production entries"""
    current_user, org_id = auth
    try:
        stmt = select(ProductionEntry).where(
            ProductionEntry.organization_id == org_id
        )
        
        if status:
            stmt = stmt.where(ProductionEntry.status == status)
        
        if not include_deleted:
            stmt = stmt.where(ProductionEntry.is_deleted == False)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        entries = result.scalars().all()
        logger.info(f"Fetched {len(entries)} production entries for organization {org_id}")
        return entries
    except Exception as e:
        logger.error(f"Error fetching production entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch production entries")

@router.get("/{entry_id}", response_model=ProductionEntryResponse)
async def get_production_entry(
    entry_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get specific production entry"""
    current_user, org_id = auth
    try:
        stmt = select(ProductionEntry).where(
            ProductionEntry.id == entry_id,
            ProductionEntry.organization_id == org_id
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            logger.error(f"Production entry {entry_id} not found for organization {org_id}")
            raise HTTPException(status_code=404, detail="Production entry not found")
        
        logger.info(f"Fetched production entry {entry_id} for organization {org_id}")
        return entry
    except Exception as e:
        logger.error(f"Error fetching production entry {entry_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch production entry")

@router.post("", response_model=ProductionEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_production_entry(
    entry_data: ProductionEntryCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create new production entry"""
    current_user, org_id = auth
    try:
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "PE", org_id, ProductionEntry, entry_data.date
        )
        
        entry = ProductionEntry(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=entry_data.date or datetime.now(),
            production_order_id=entry_data.production_order_id,
            shift=entry_data.shift,
            machine=entry_data.machine,
            operator=entry_data.operator,
            batch_number=entry_data.batch_number,
            actual_quantity=entry_data.actual_quantity,
            rejected_quantity=entry_data.rejected_quantity,
            time_taken=entry_data.time_taken,
            labor_hours=entry_data.labor_hours,
            machine_hours=entry_data.machine_hours,
            power_consumption=entry_data.power_consumption,
            downtime_events=entry_data.downtime_events,
            notes=entry_data.notes,
            created_by=current_user.id
        )
        
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        
        # Update order status
        await update_manufacturing_order_status(db, entry.production_order_id, "in_progress", current_user)
        
        logger.info(f"Created production entry {voucher_number} for organization {org_id}")
        return entry
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating production entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create production entry")

@router.patch("/{entry_id}", response_model=ProductionEntryResponse)
async def update_production_entry(
    entry_id: int,
    update_data: ProductionEntryUpdate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update production entry (including soft delete)"""
    current_user, org_id = auth
    try:
        stmt = select(ProductionEntry).where(
            ProductionEntry.id == entry_id,
            ProductionEntry.organization_id == org_id
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Production entry not found")
        
        # If soft deleting
        if update_data.is_deleted:
            if not update_data.deletion_remark:
                raise HTTPException(status_code=400, detail="Deletion remark is required for delete operation")
            entry.is_deleted = True
            entry.deletion_remark = update_data.deletion_remark
        else:
            # Regular update
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(entry, field, value)
        
        entry.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(entry)
        
        logger.info(f"Updated production entry {entry_id} for organization {org_id}")
        return entry
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating production entry {entry_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update production entry")

@router.patch("/{entry_id}/status", response_model=ProductionEntryResponse)
async def update_production_entry_status(
    entry_id: int,
    status_data: StatusUpdateSchema,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update production entry status"""
    current_user, org_id = auth
    try:
        stmt = select(ProductionEntry).where(
            ProductionEntry.id == entry_id,
            ProductionEntry.organization_id == org_id
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Production entry not found")
        
        if entry.is_deleted:
            raise HTTPException(status_code=400, detail="Cannot update status of deleted entry")
        
        entry.status = status_data.status
        entry.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(entry)
        
        logger.info(f"Updated status for production entry {entry_id} to {status_data.status}")
        return entry
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating status for entry {entry_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update entry status")