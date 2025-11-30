# app/api/v1/manufacturing/manufacturing_journals.py
"""
Manufacturing Journals module - Handles manufacturing journal vouchers
Extracted from monolithic manufacturing.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_operations import (
    ManufacturingJournalVoucher,
    ManufacturingJournalFinishedProduct,
    ManufacturingJournalMaterial,
    ManufacturingJournalByproduct
)
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Schemas
class ManufacturingJournalFinishedProductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_cost: float = 0.0
    quality_grade: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None


class ManufacturingJournalMaterialCreate(BaseModel):
    product_id: int
    quantity_consumed: float
    unit: str
    unit_cost: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None


class ManufacturingJournalByproductCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_value: float = 0.0
    batch_number: Optional[str] = None
    condition: Optional[str] = None


class ManufacturingJournalVoucherCreate(BaseModel):
    manufacturing_order_id: int
    bom_id: int
    date_of_manufacture: datetime
    shift: Optional[str] = None
    operator: Optional[str] = None
    supervisor: Optional[str] = None
    machine_used: Optional[str] = None
    finished_quantity: float = 0.0
    scrap_quantity: float = 0.0
    rework_quantity: float = 0.0
    byproduct_quantity: float = 0.0
    material_cost: float = 0.0
    labor_cost: float = 0.0
    overhead_cost: float = 0.0
    quality_grade: Optional[str] = None
    quality_remarks: Optional[str] = None
    narration: Optional[str] = None
    finished_products: List[ManufacturingJournalFinishedProductCreate] = []
    consumed_materials: List[ManufacturingJournalMaterialCreate] = []
    byproducts: List[ManufacturingJournalByproductCreate] = []


class ManufacturingJournalVoucherResponse(BaseModel):
    id: int
    voucher_number: str
    organization_id: int
    manufacturing_order_id: int
    bom_id: int
    date_of_manufacture: datetime
    shift: Optional[str]
    operator: Optional[str]
    supervisor: Optional[str]
    machine_used: Optional[str]
    finished_quantity: float
    scrap_quantity: float
    rework_quantity: float
    byproduct_quantity: float
    material_cost: float
    labor_cost: float
    overhead_cost: float
    total_manufacturing_cost: float
    quality_grade: Optional[str]
    quality_remarks: Optional[str]
    narration: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("", response_model=List[ManufacturingJournalVoucherResponse])
async def get_manufacturing_journal_vouchers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Filter by status"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get manufacturing journal vouchers"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingJournalVoucher).where(
            ManufacturingJournalVoucher.organization_id == org_id
        )
        if status:
            stmt = stmt.where(ManufacturingJournalVoucher.status == status)
        stmt = stmt.order_by(ManufacturingJournalVoucher.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        vouchers = result.scalars().all()
        logger.info(f"Fetched {len(vouchers)} manufacturing journal vouchers for organization {org_id}")
        return vouchers
    except Exception as e:
        logger.error(f"Error fetching manufacturing journal vouchers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch manufacturing journal vouchers"
        )


@router.get("/next-number")
async def get_next_manufacturing_journal_number(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next manufacturing journal voucher number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MJV", org_id, ManufacturingJournalVoucher
        )
        logger.info(f"Generated next MJV number: {next_number} for organization {org_id}")
        return {"next_number": next_number}
    except Exception as e:
        logger.error(f"Error generating MJV number: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate manufacturing journal voucher number"
        )


@router.post("", response_model=ManufacturingJournalVoucherResponse)
async def create_manufacturing_journal_voucher(
    voucher_data: ManufacturingJournalVoucherCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create new manufacturing journal voucher"""
    current_user, org_id = auth
    try:
        # Generate voucher number atomically
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MJV", org_id, ManufacturingJournalVoucher
        )

        # Calculate total manufacturing cost
        total_cost = voucher_data.material_cost + voucher_data.labor_cost + voucher_data.overhead_cost

        db_voucher = ManufacturingJournalVoucher(
            organization_id=org_id,
            voucher_number=voucher_number,
            manufacturing_order_id=voucher_data.manufacturing_order_id,
            bom_id=voucher_data.bom_id,
            date=datetime.now(),
            date_of_manufacture=voucher_data.date_of_manufacture,
            shift=voucher_data.shift,
            operator=voucher_data.operator,
            supervisor=voucher_data.supervisor,
            machine_used=voucher_data.machine_used,
            finished_quantity=voucher_data.finished_quantity,
            scrap_quantity=voucher_data.scrap_quantity,
            rework_quantity=voucher_data.rework_quantity,
            byproduct_quantity=voucher_data.byproduct_quantity,
            material_cost=voucher_data.material_cost,
            labor_cost=voucher_data.labor_cost,
            overhead_cost=voucher_data.overhead_cost,
            total_manufacturing_cost=total_cost,
            quality_grade=voucher_data.quality_grade,
            quality_remarks=voucher_data.quality_remarks,
            narration=voucher_data.narration,
            status="draft",
            created_by=current_user.id
        )

        db.add(db_voucher)
        await db.flush()

        # Add finished products
        for fp_data in voucher_data.finished_products:
            fp = ManufacturingJournalFinishedProduct(
                organization_id=org_id,
                journal_id=db_voucher.id,
                product_id=fp_data.product_id,
                quantity=fp_data.quantity,
                unit=fp_data.unit,
                unit_cost=fp_data.unit_cost,
                total_cost=fp_data.quantity * fp_data.unit_cost,
                quality_grade=fp_data.quality_grade,
                batch_number=fp_data.batch_number,
                lot_number=fp_data.lot_number
            )
            db.add(fp)

        # Add consumed materials
        for cm_data in voucher_data.consumed_materials:
            cm = ManufacturingJournalMaterial(
                organization_id=org_id,
                journal_id=db_voucher.id,
                product_id=cm_data.product_id,
                quantity_consumed=cm_data.quantity_consumed,
                unit=cm_data.unit,
                unit_cost=cm_data.unit_cost,
                total_cost=cm_data.quantity_consumed * cm_data.unit_cost,
                batch_number=cm_data.batch_number,
                lot_number=cm_data.lot_number
            )
            db.add(cm)

        # Add byproducts
        for bp_data in voucher_data.byproducts:
            bp = ManufacturingJournalByproduct(
                organization_id=org_id,
                journal_id=db_voucher.id,
                product_id=bp_data.product_id,
                quantity=bp_data.quantity,
                unit=bp_data.unit,
                unit_value=bp_data.unit_value,
                total_value=bp_data.quantity * bp_data.unit_value,
                batch_number=bp_data.batch_number,
                condition=bp_data.condition
            )
            db.add(bp)

        await db.commit()
        await db.refresh(db_voucher)
        logger.info(f"Created manufacturing journal voucher {voucher_number} for organization {org_id}")
        return db_voucher

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating manufacturing journal voucher: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create manufacturing journal voucher: {str(e)}"
        )


@router.get("/{voucher_id}", response_model=ManufacturingJournalVoucherResponse)
async def get_manufacturing_journal_voucher(
    voucher_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific manufacturing journal voucher"""
    current_user, org_id = auth
    try:
        stmt = select(ManufacturingJournalVoucher).where(
            ManufacturingJournalVoucher.id == voucher_id,
            ManufacturingJournalVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=404,
                detail="Manufacturing journal voucher not found"
            )
        return voucher
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching manufacturing journal voucher {voucher_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch manufacturing journal voucher"
        )
