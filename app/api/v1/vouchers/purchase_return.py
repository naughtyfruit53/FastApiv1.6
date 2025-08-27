# app/api/v1/vouchers/purchase_return.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseReturn
from app.schemas.vouchers import PurchaseReturnCreate, PurchaseReturnInDB, PurchaseReturnUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-returns"])

@router.get("", response_model=List[PurchaseReturnInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PurchaseReturnInDB])
async def get_purchase_returns(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase returns"""
    query = db.query(PurchaseReturn).options(joinedload(PurchaseReturn.vendor)).filter(
        PurchaseReturn.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseReturn.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseReturn, sortBy):
        sort_attr = getattr(PurchaseReturn, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(PurchaseReturn.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_return_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available purchase return number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PR", current_user.organization_id, PurchaseReturn
    )

# Register both "" and "/" for POST to support both /api/v1/purchase-returns and /api/v1/purchase-returns/
@router.post("", response_model=PurchaseReturnInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseReturnInDB)
async def create_purchase_return(
    invoice: PurchaseReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new purchase return"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PR", current_user.organization_id, PurchaseReturn
            )
        else:
            existing = db.query(PurchaseReturn).filter(
                PurchaseReturn.organization_id == current_user.organization_id,
                PurchaseReturn.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PR", current_user.organization_id, PurchaseReturn
                )
        
        db_invoice = PurchaseReturn(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import PurchaseReturnItem
            item = PurchaseReturnItem(
                purchase_return_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_return",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Purchase return {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase return"
        )

@router.get("/{invoice_id}", response_model=PurchaseReturnInDB)
async def get_purchase_return(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(PurchaseReturn).options(joinedload(PurchaseReturn.vendor)).filter(
        PurchaseReturn.id == invoice_id,
        PurchaseReturn.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase return not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=PurchaseReturnInDB)
async def update_purchase_return(
    invoice_id: int,
    invoice_update: PurchaseReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import PurchaseReturnItem
            db.query(PurchaseReturnItem).filter(PurchaseReturnItem.purchase_return_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = PurchaseReturnItem(
                    purchase_return_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Purchase return {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase return"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_return(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        from app.models.vouchers import PurchaseReturnItem
        db.query(PurchaseReturnItem).filter(PurchaseReturnItem.purchase_return_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Purchase return {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase return deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase return"
        )