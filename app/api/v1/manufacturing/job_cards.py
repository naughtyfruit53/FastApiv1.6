# app/api/v1/manufacturing/job_cards.py
"""Job Cards module"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.vouchers import JobCardVoucher, JobCardSuppliedMaterial, JobCardReceivedOutput
from app.services.voucher_service import VoucherNumberService
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Job Card Voucher Schemas
class JobCardSuppliedMaterialCreate(BaseModel):
    product_id: int
    quantity_supplied: float
    unit: str
    unit_rate: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    supply_date: Optional[datetime] = None

class JobCardReceivedOutputCreate(BaseModel):
    product_id: int
    quantity_received: float
    unit: str
    unit_rate: float = 0.0
    quality_status: Optional[str] = None
    inspection_date: Optional[datetime] = None
    inspection_remarks: Optional[str] = None
    batch_number: Optional[str] = None
    receipt_date: Optional[datetime] = None

class JobCardVoucherCreate(BaseModel):
    job_type: str
    vendor_id: int
    manufacturing_order_id: Optional[int] = None
    job_description: str
    job_category: Optional[str] = None
    expected_completion_date: Optional[datetime] = None
    materials_supplied_by: str = "company"
    delivery_address: Optional[str] = None
    transport_mode: Optional[str] = None
    quality_specifications: Optional[str] = None
    quality_check_required: bool = True
    notes: Optional[str] = None
    supplied_materials: List[JobCardSuppliedMaterialCreate] = []
    received_outputs: List[JobCardReceivedOutputCreate] = []

class JobCardVoucherResponse(BaseModel):
    id: int
    voucher_number: str
    date: datetime
    job_type: str
    vendor_id: int
    manufacturing_order_id: Optional[int]
    job_description: str
    job_category: Optional[str]
    expected_completion_date: Optional[datetime]
    materials_supplied_by: str
    delivery_address: Optional[str]
    transport_mode: Optional[str]
    quality_specifications: Optional[str]
    quality_check_required: bool
    notes: Optional[str]
    total_amount: float
    created_by: int

    class Config:
        from_attributes = True

@router.get("", response_model=List[JobCardVoucherResponse])
async def get_job_card_vouchers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of job card vouchers at /api/v1/job-card-vouchers"""
    try:
        stmt = select(JobCardVoucher).where(
            JobCardVoucher.organization_id == current_user.organization_id
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        vouchers = result.scalars().all()
        logger.info(f"Fetched {len(vouchers)} job card vouchers for organization {current_user.organization_id}")
        return vouchers
    except Exception as e:
        logger.error(f"Error fetching job card vouchers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch job card vouchers")

@router.get("/next-number")
async def get_next_job_card_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get next job card number at /api/v1/job-card-vouchers/next-number"""
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "JCV", current_user.organization_id, JobCardVoucher
        )
        logger.info(f"Generated next job card number: {next_number} for organization {current_user.organization_id}")
        return next_number
    except Exception as e:
        logger.error(f"Error generating job card number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate job card number")

@router.post("")
async def create_job_card_voucher(
    voucher_data: JobCardVoucherCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new job card voucher at /api/v1/job-card-vouchers"""
    try:
        # Generate voucher number
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "JCV", current_user.organization_id, JobCardVoucher
        )

        # Calculate total amount from supplied materials and outputs
        supplied_value = sum(sm.quantity_supplied * sm.unit_rate for sm in voucher_data.supplied_materials)
        output_value = sum(ro.quantity_received * ro.unit_rate for ro in voucher_data.received_outputs)
        total_amount = output_value - supplied_value  # Net job work value

        db_voucher = JobCardVoucher(
            organization_id=current_user.organization_id,
            voucher_number=voucher_number,
            date=datetime.now(),
            job_type=voucher_data.job_type,
            vendor_id=voucher_data.vendor_id,
            manufacturing_order_id=voucher_data.manufacturing_order_id,
            job_description=voucher_data.job_description,
            job_category=voucher_data.job_category,
            expected_completion_date=voucher_data.expected_completion_date,
            materials_supplied_by=voucher_data.materials_supplied_by,
            delivery_address=voucher_data.delivery_address,
            transport_mode=voucher_data.transport_mode,
            quality_specifications=voucher_data.quality_specifications,
            quality_check_required=voucher_data.quality_check_required,
            notes=voucher_data.notes,
            total_amount=total_amount,
            created_by=current_user.id
        )

        db.add(db_voucher)
        await db.flush()

        # Add supplied materials
        for sm_data in voucher_data.supplied_materials:
            sm = JobCardSuppliedMaterial(
                organization_id=current_user.organization_id,
                job_card_id=db_voucher.id,
                product_id=sm_data.product_id,
                quantity_supplied=sm_data.quantity_supplied,
                unit=sm_data.unit,
                unit_rate=sm_data.unit_rate,
                total_value=sm_data.quantity_supplied * sm_data.unit_rate,
                batch_number=sm_data.batch_number,
                lot_number=sm_data.lot_number,
                supply_date=sm_data.supply_date
            )
            db.add(sm)

        # Add received outputs
        for ro_data in voucher_data.received_outputs:
            ro = JobCardReceivedOutput(
                organization_id=current_user.organization_id,
                job_card_id=db_voucher.id,
                product_id=ro_data.product_id,
                quantity_received=ro_data.quantity_received,
                unit=ro_data.unit,
                unit_rate=ro_data.unit_rate,
                total_value=ro_data.quantity_received * ro_data.unit_rate,
                quality_status=ro_data.quality_status,
                inspection_date=ro_data.inspection_date,
                inspection_remarks=ro_data.inspection_remarks,
                batch_number=ro_data.batch_number,
                receipt_date=ro_data.receipt_date
            )
            db.add(ro)

        await db.commit()
        await db.refresh(db_voucher)
        logger.info(f"Created job card voucher {voucher_number} for organization {current_user.organization_id}")
        return db_voucher
    except Exception as e:
        logger.error(f"Error creating job card voucher: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job card voucher")