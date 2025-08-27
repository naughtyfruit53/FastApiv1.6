# app/api/v1/vouchers/purchase_order.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem
from app.schemas.vouchers import PurchaseOrderCreate, PurchaseOrderInDB, PurchaseOrderUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-orders"])

@router.get("", response_model=List[PurchaseOrderInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PurchaseOrderInDB])
async def get_purchase_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase orders"""
    query = db.query(PurchaseOrder).options(joinedload(PurchaseOrder.vendor), joinedload(PurchaseOrder.items)).filter(
        PurchaseOrder.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseOrder, sortBy):
        sort_attr = getattr(PurchaseOrder, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(PurchaseOrder.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_order_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available purchase order number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PO", current_user.organization_id, PurchaseOrder
    )

# Register both "" and "/" for POST to support both /api/v1/purchase-orders and /api/v1/purchase-orders/
@router.post("", response_model=PurchaseOrderInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseOrderInDB)
async def create_purchase_order(
    invoice: PurchaseOrderCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new purchase order"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PO", current_user.organization_id, PurchaseOrder
            )
        else:
            existing = db.query(PurchaseOrder).filter(
                PurchaseOrder.organization_id == current_user.organization_id,
                PurchaseOrder.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PO", current_user.organization_id, PurchaseOrder
                )
        
        db_invoice = PurchaseOrder(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            item = PurchaseOrderItem(
                purchase_order_id=db_invoice.id,
                delivered_quantity=0.0,
                pending_quantity=item_data.quantity,  # Set pending_quantity to quantity
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_order",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Purchase order {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase order"
        )

@router.get("/{invoice_id}", response_model=PurchaseOrderInDB)
async def get_purchase_order(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.vendor),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).filter(
        PurchaseOrder.id == invoice_id,
        PurchaseOrder.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=PurchaseOrderInDB)
async def update_purchase_order(
    invoice_id: int,
    invoice_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = PurchaseOrderItem(
                    purchase_order_id=invoice_id,
                    delivered_quantity=0.0,
                    pending_quantity=item_data.quantity,  # Set pending_quantity to quantity
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Purchase order {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase order"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_order(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Purchase order {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase order deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase order"
        )