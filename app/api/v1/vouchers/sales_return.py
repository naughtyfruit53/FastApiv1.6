# app/api/v1/vouchers/sales_return.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.sales import SalesReturn
from app.schemas.vouchers import SalesReturnCreate, SalesReturnInDB, SalesReturnUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sales-returns"])

@router.get("", response_model=List[SalesReturnInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[SalesReturnInDB])
async def get_sales_returns(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales returns"""
    query = db.query(SalesReturn).options(joinedload(SalesReturn.customer)).filter(
        SalesReturn.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(SalesReturn.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(SalesReturn, sortBy):
        sort_attr = getattr(SalesReturn, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(SalesReturn.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_sales_return_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available sales return number"""
    return VoucherNumberService.generate_voucher_number(
        db, "SR", current_user.organization_id, SalesReturn
    )

# Register both "" and "/" for POST to support both /api/v1/sales-returns and /api/v1/sales-returns/
@router.post("", response_model=SalesReturnInDB, include_in_schema=False)
@router.post("/", response_model=SalesReturnInDB)
async def create_sales_return(
    invoice: SalesReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new sales return"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "SR", current_user.organization_id, SalesReturn
            )
        else:
            existing = db.query(SalesReturn).filter(
                SalesReturn.organization_id == current_user.organization_id,
                SalesReturn.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "SR", current_user.organization_id, SalesReturn
                )
        
        db_invoice = SalesReturn(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import SalesReturnItem
            item = SalesReturnItem(
                sales_return_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="sales_return",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Sales return {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sales return"
        )

@router.get("/{invoice_id}", response_model=SalesReturnInDB)
async def get_sales_return(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(SalesReturn).options(joinedload(SalesReturn.customer)).filter(
        SalesReturn.id == invoice_id,
        SalesReturn.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales return not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=SalesReturnInDB)
async def update_sales_return(
    invoice_id: int,
    invoice_update: SalesReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(SalesReturn).filter(
            SalesReturn.id == invoice_id,
            SalesReturn.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales return not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import SalesReturnItem
            db.query(SalesReturnItem).filter(SalesReturnItem.sales_return_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = SalesReturnItem(
                    sales_return_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Sales return {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sales return"
        )

@router.delete("/{invoice_id}")
async def delete_sales_return(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(SalesReturn).filter(
            SalesReturn.id == invoice_id,
            SalesReturn.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales return not found"
            )
        
        from app.models.vouchers import SalesReturnItem
        db.query(SalesReturnItem).filter(SalesReturnItem.sales_return_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Sales return {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Sales return deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sales return"
        )