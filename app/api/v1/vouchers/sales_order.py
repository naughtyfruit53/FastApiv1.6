# app/api/v1/vouchers/sales_order.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers import SalesOrder
from app.schemas.vouchers import SalesOrderCreate, SalesOrderInDB, SalesOrderUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sales-orders"])

@router.get("", response_model=List[SalesOrderInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[SalesOrderInDB])
async def get_sales_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales orders"""
    query = db.query(SalesOrder).options(joinedload(SalesOrder.customer)).filter(
        SalesOrder.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(SalesOrder.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(SalesOrder, sortBy):
        sort_attr = getattr(SalesOrder, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(SalesOrder.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_sales_order_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available sales order number"""
    return VoucherNumberService.generate_voucher_number(
        db, "SO", current_user.organization_id, SalesOrder
    )

# Register both "" and "/" for POST to support both /api/v1/sales-orders and /api/v1/sales-orders/
@router.post("", response_model=SalesOrderInDB, include_in_schema=False)
@router.post("/", response_model=SalesOrderInDB)
async def create_sales_order(
    invoice: SalesOrderCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new sales order"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "SO", current_user.organization_id, SalesOrder
            )
        else:
            existing = db.query(SalesOrder).filter(
                SalesOrder.organization_id == current_user.organization_id,
                SalesOrder.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "SO", current_user.organization_id, SalesOrder
                )
        
        db_invoice = SalesOrder(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import SalesOrderItem
            item = SalesOrderItem(
                sales_order_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="sales_order",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Sales order {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sales order"
        )

@router.get("/{invoice_id}", response_model=SalesOrderInDB)
async def get_sales_order(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(SalesOrder).options(joinedload(SalesOrder.customer)).filter(
        SalesOrder.id == invoice_id,
        SalesOrder.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=SalesOrderInDB)
async def update_sales_order(
    invoice_id: int,
    invoice_update: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(SalesOrder).filter(
            SalesOrder.id == invoice_id,
            SalesOrder.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import SalesOrderItem
            db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = SalesOrderItem(
                    sales_order_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Sales order {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sales order"
        )

@router.delete("/{invoice_id}")
async def delete_sales_order(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(SalesOrder).filter(
            SalesOrder.id == invoice_id,
            SalesOrder.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        from app.models.vouchers import SalesOrderItem
        db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Sales order {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Sales order deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sales order"
        )