# app/api/v1/manufacturing/material_receipt.py
"""
Material Receipt module - Handles material receipt vouchers
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_operations import MaterialReceiptVoucher, MaterialReceiptItem
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Schemas
class MaterialReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float = 0.0
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None
    quality_status: Optional[str] = "pending"  # pending, accepted, rejected, hold
    received_quantity: Optional[float] = None
    accepted_quantity: Optional[float] = None
    rejected_quantity: Optional[float] = 0.0
    inspection_remarks: Optional[str] = None


class MaterialReceiptCreate(BaseModel):
    source_type: str  # 'return', 'purchase', 'transfer', 'production'
    source_reference: Optional[str] = None
    manufacturing_order_id: Optional[int] = None
    supplier_id: Optional[int] = None  # For purchase receipts
    purchase_order_id: Optional[int] = None  # Link to PO for autofill
    received_from_department: Optional[str] = None
    received_from_employee: Optional[str] = None
    received_by_employee: Optional[str] = None
    receipt_time: Optional[datetime] = None
    inspection_required: bool = False
    condition_on_receipt: Optional[str] = "good"
    notes: Optional[str] = None
    items: List[MaterialReceiptItemCreate] = []


class MaterialReceiptItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    total_amount: float
    batch_number: Optional[str]
    lot_number: Optional[str]
    warehouse_location: Optional[str]
    quality_status: Optional[str]
    received_quantity: Optional[float]
    accepted_quantity: Optional[float]
    rejected_quantity: Optional[float]

    class Config:
        from_attributes = True


class MaterialReceiptResponse(BaseModel):
    id: int
    voucher_number: str
    organization_id: int
    source_type: str
    source_reference: Optional[str]
    manufacturing_order_id: Optional[int]
    received_from_department: Optional[str]
    received_by_employee: Optional[str]
    inspection_required: bool
    inspection_status: Optional[str]
    condition_on_receipt: Optional[str]
    status: Optional[str]
    notes: Optional[str]
    total_amount: Optional[float]
    date: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("")
async def get_material_receipt_vouchers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get material receipt vouchers"""
    current_user, org_id = auth
    try:
        stmt = select(MaterialReceiptVoucher).where(
            MaterialReceiptVoucher.organization_id == org_id
        )
        if source_type:
            stmt = stmt.where(MaterialReceiptVoucher.source_type == source_type)
        if status:
            stmt = stmt.where(MaterialReceiptVoucher.status == status)
        stmt = stmt.order_by(MaterialReceiptVoucher.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        vouchers = result.scalars().all()
        logger.info(f"Fetched {len(vouchers)} material receipt vouchers for organization {org_id}")
        return vouchers
    except Exception as e:
        logger.error(f"Error fetching material receipt vouchers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch material receipt vouchers")


@router.get("/next-number")
async def get_next_material_receipt_number(
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get next material receipt voucher number"""
    current_user, org_id = auth
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MRV", org_id, MaterialReceiptVoucher
        )
        logger.info(f"Generated next MRV number: {next_number} for organization {org_id}")
        return {"next_number": next_number}
    except Exception as e:
        logger.error(f"Error generating MRV number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate material receipt voucher number")


@router.post("", response_model=MaterialReceiptResponse)
async def create_material_receipt(
    receipt_data: MaterialReceiptCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Create new material receipt voucher (draft)"""
    current_user, org_id = auth
    try:
        # Generate voucher number atomically
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MRV", org_id, MaterialReceiptVoucher
        )

        db_receipt = MaterialReceiptVoucher(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=datetime.now(),
            source_type=receipt_data.source_type,
            source_reference=receipt_data.source_reference,
            manufacturing_order_id=receipt_data.manufacturing_order_id,
            received_from_department=receipt_data.received_from_department,
            received_from_employee=receipt_data.received_from_employee,
            received_by_employee=receipt_data.received_by_employee,
            receipt_time=receipt_data.receipt_time or datetime.now(),
            inspection_required=receipt_data.inspection_required,
            inspection_status="pending" if receipt_data.inspection_required else "not_required",
            condition_on_receipt=receipt_data.condition_on_receipt,
            notes=receipt_data.notes,
            status="draft",
            created_by=current_user.id
        )

        db.add(db_receipt)
        await db.flush()

        total_amount = 0.0
        # Add items
        for item_data in receipt_data.items:
            item_total = item_data.quantity * item_data.unit_price
            total_amount += item_total
            
            item = MaterialReceiptItem(
                receipt_id=db_receipt.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_price=item_data.unit_price,
                total_amount=item_total,
                batch_number=item_data.batch_number,
                lot_number=item_data.lot_number,
                warehouse_location=item_data.warehouse_location,
                bin_location=item_data.bin_location,
                quality_status=item_data.quality_status,
                received_quantity=item_data.received_quantity or item_data.quantity,
                accepted_quantity=item_data.accepted_quantity,
                rejected_quantity=item_data.rejected_quantity
            )
            db.add(item)

        db_receipt.total_amount = total_amount
        await db.commit()
        await db.refresh(db_receipt)
        logger.info(f"Created material receipt {voucher_number} for organization {org_id}")
        return db_receipt

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating material receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create material receipt: {str(e)}")


@router.get("/{receipt_id}", response_model=MaterialReceiptResponse)
async def get_material_receipt(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific material receipt voucher"""
    current_user, org_id = auth
    try:
        stmt = select(MaterialReceiptVoucher).options(
            joinedload(MaterialReceiptVoucher.items)
        ).where(
            MaterialReceiptVoucher.id == receipt_id,
            MaterialReceiptVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        if not receipt:
            raise HTTPException(status_code=404, detail="Material receipt not found")
        return receipt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching material receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch material receipt")


@router.put("/{receipt_id}", response_model=MaterialReceiptResponse)
async def update_material_receipt(
    receipt_id: int,
    receipt_data: MaterialReceiptCreate,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Update a material receipt voucher (only drafts can be updated)"""
    current_user, org_id = auth
    try:
        stmt = select(MaterialReceiptVoucher).where(
            MaterialReceiptVoucher.id == receipt_id,
            MaterialReceiptVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="Material receipt not found")
        
        if receipt.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft receipts can be updated")

        # Update receipt fields
        receipt.source_type = receipt_data.source_type
        receipt.source_reference = receipt_data.source_reference
        receipt.received_from_department = receipt_data.received_from_department
        receipt.received_from_employee = receipt_data.received_from_employee
        receipt.received_by_employee = receipt_data.received_by_employee
        receipt.inspection_required = receipt_data.inspection_required
        receipt.condition_on_receipt = receipt_data.condition_on_receipt
        receipt.notes = receipt_data.notes

        # Delete old items and add new ones
        from sqlalchemy import delete
        await db.execute(delete(MaterialReceiptItem).where(MaterialReceiptItem.receipt_id == receipt_id))
        
        total_amount = 0.0
        for item_data in receipt_data.items:
            item_total = item_data.quantity * item_data.unit_price
            total_amount += item_total
            
            item = MaterialReceiptItem(
                receipt_id=receipt.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_price=item_data.unit_price,
                total_amount=item_total,
                batch_number=item_data.batch_number,
                lot_number=item_data.lot_number,
                warehouse_location=item_data.warehouse_location,
                bin_location=item_data.bin_location,
                quality_status=item_data.quality_status,
                received_quantity=item_data.received_quantity or item_data.quantity,
                accepted_quantity=item_data.accepted_quantity,
                rejected_quantity=item_data.rejected_quantity
            )
            db.add(item)

        receipt.total_amount = total_amount
        await db.commit()
        await db.refresh(receipt)
        return receipt

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating material receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update material receipt")


@router.post("/{receipt_id}/post", response_model=MaterialReceiptResponse)
async def post_material_receipt(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Post a material receipt (updates inventory and creates audit trail)"""
    current_user, org_id = auth
    try:
        stmt = select(MaterialReceiptVoucher).options(
            joinedload(MaterialReceiptVoucher.items)
        ).where(
            MaterialReceiptVoucher.id == receipt_id,
            MaterialReceiptVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.unique().scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="Material receipt not found")
        
        if receipt.status == "posted":
            raise HTTPException(status_code=400, detail="Receipt already posted")

        # Update stock for each item
        from app.models import Stock
        for item in receipt.items:
            stock_stmt = select(Stock).where(
                Stock.product_id == item.product_id,
                Stock.organization_id == org_id
            )
            stock_result = await db.execute(stock_stmt)
            stock = stock_result.scalar_one_or_none()
            
            accepted_qty = item.accepted_quantity or item.quantity
            if not stock:
                stock = Stock(
                    product_id=item.product_id,
                    organization_id=org_id,
                    quantity=accepted_qty,
                    unit=item.unit
                )
                db.add(stock)
            else:
                stock.quantity += accepted_qty

        receipt.status = "posted"
        receipt.approved_by = current_user.id
        receipt.approval_date = datetime.now()
        
        await db.commit()
        await db.refresh(receipt)
        logger.info(f"Posted material receipt {receipt.voucher_number} for organization {org_id}")
        return receipt

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error posting material receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to post material receipt")


@router.delete("/{receipt_id}")
async def cancel_material_receipt(
    receipt_id: int,
    auth: tuple = Depends(require_access("manufacturing", "write")),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a material receipt (only drafts can be cancelled)"""
    current_user, org_id = auth
    try:
        stmt = select(MaterialReceiptVoucher).where(
            MaterialReceiptVoucher.id == receipt_id,
            MaterialReceiptVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        receipt = result.scalar_one_or_none()
        
        if not receipt:
            raise HTTPException(status_code=404, detail="Material receipt not found")
        
        if receipt.status == "posted":
            raise HTTPException(status_code=400, detail="Cannot cancel a posted receipt")

        receipt.status = "cancelled"
        await db.commit()
        logger.info(f"Cancelled material receipt {receipt.voucher_number} for organization {org_id}")
        return {"message": "Material receipt cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error cancelling material receipt {receipt_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel material receipt")
