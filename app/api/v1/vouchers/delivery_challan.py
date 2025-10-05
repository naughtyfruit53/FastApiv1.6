# app/api/v1/vouchers/delivery_challan.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.sales import DeliveryChallan, DeliveryChallanItem
from app.schemas.vouchers import DeliveryChallanCreate, DeliveryChallanInDB, DeliveryChallanUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["delivery-challans"])

@router.get("", response_model=List[DeliveryChallanInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[DeliveryChallanInDB])
async def get_delivery_challans(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all delivery challans"""
    stmt = select(DeliveryChallan).options(
        joinedload(DeliveryChallan.customer),
        joinedload(DeliveryChallan.items).joinedload(DeliveryChallanItem.product)
    ).where(
        DeliveryChallan.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(DeliveryChallan.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(DeliveryChallan, sortBy):
        sort_attr = getattr(DeliveryChallan, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(DeliveryChallan.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_delivery_challan_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available delivery challan number"""
    return await VoucherNumberService.generate_voucher_number(
        db, "DC", current_user.organization_id, DeliveryChallan
    )

# Register both "" and "/" for POST to support both /api/v1/delivery-challans and /api/v1/delivery-challans/
@router.post("", response_model=DeliveryChallanInDB, include_in_schema=False)
@router.post("/", response_model=DeliveryChallanInDB)
async def create_delivery_challan(
    invoice: DeliveryChallanCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new delivery challan"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                db, "DC", current_user.organization_id, DeliveryChallan
            )
        else:
            stmt = select(DeliveryChallan).where(
                DeliveryChallan.organization_id == current_user.organization_id,
                DeliveryChallan.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                    db, "DC", current_user.organization_id, DeliveryChallan
                )
        
        db_invoice = DeliveryChallan(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        for item_data in invoice.items:
            item = DeliveryChallanItem(
                delivery_challan_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(db_invoice)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="delivery_challan",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Delivery challan {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating delivery challan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create delivery challan"
        )

@router.get("/{invoice_id}", response_model=DeliveryChallanInDB)
async def get_delivery_challan(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(DeliveryChallan).options(
        joinedload(DeliveryChallan.customer),
        joinedload(DeliveryChallan.items).joinedload(DeliveryChallanItem.product)
    ).where(
        DeliveryChallan.id == invoice_id,
        DeliveryChallan.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery challan not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=DeliveryChallanInDB)
async def update_delivery_challan(
    invoice_id: int,
    invoice_update: DeliveryChallanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from sqlalchemy import delete
            stmt_delete = delete(DeliveryChallanItem).where(DeliveryChallanItem.delivery_challan_id == invoice_id)
            await db.execute(stmt_delete)
            await db.flush()  # Flush deletes before adding new items to avoid potential locks
            for item_data in invoice_update.items:
                item = DeliveryChallanItem(
                    delivery_challan_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
            await db.flush()  # Flush adds before commit
        
        logger.debug(f"Before commit for delivery challan {invoice_id}")
        await db.commit()
        logger.debug(f"After commit for delivery challan {invoice_id}")
        await db.refresh(invoice)
        
        logger.info(f"Delivery challan {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating delivery challan {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update delivery challan"
        )

@router.delete("/{invoice_id}")
async def delete_delivery_challan(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(DeliveryChallanItem).where(DeliveryChallanItem.delivery_challan_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Delivery challan {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Delivery challan deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting delivery challan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete delivery challan"
        )