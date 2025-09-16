# app/api/v1/vouchers/proforma_invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.presales import ProformaInvoice, ProformaInvoiceItem
from app.schemas.vouchers import ProformaInvoiceCreate, ProformaInvoiceInDB, ProformaInvoiceUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["proforma-invoices"])

@router.get("", response_model=List[ProformaInvoiceInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[ProformaInvoiceInDB])
async def get_proforma_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all proforma invoices"""
    query = db.query(ProformaInvoice).options(joinedload(ProformaInvoice.customer)).filter(
        ProformaInvoice.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ProformaInvoice.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ProformaInvoice, sortBy):
        sort_attr = getattr(ProformaInvoice, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(ProformaInvoice.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_proforma_invoice_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available proforma invoice number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PI", current_user.organization_id, ProformaInvoice
    )

# Register both "" and "/" for POST to support both /api/v1/proforma-invoices and /api/v1/proforma-invoices/
@router.post("", response_model=ProformaInvoiceInDB, include_in_schema=False)
@router.post("/", response_model=ProformaInvoiceInDB)
async def create_proforma_invoice(
    invoice: ProformaInvoiceCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new proforma invoice"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PI", current_user.organization_id, ProformaInvoice
            )
        else:
            existing = db.query(ProformaInvoice).filter(
                ProformaInvoice.organization_id == current_user.organization_id,
                ProformaInvoice.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PI", current_user.organization_id, ProformaInvoice
                )
        
        db_invoice = ProformaInvoice(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            item = ProformaInvoiceItem(
                proforma_invoice_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="proforma_invoice",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Proforma invoice {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating proforma invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create proforma invoice"
        )

@router.get("/{invoice_id}", response_model=ProformaInvoiceInDB)
async def get_proforma_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(ProformaInvoice).options(
        joinedload(ProformaInvoice.customer),
        joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
    ).filter(
        ProformaInvoice.id == invoice_id,
        ProformaInvoice.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proforma invoice not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=ProformaInvoiceInDB)
async def update_proforma_invoice(
    invoice_id: int,
    invoice_update: ProformaInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(ProformaInvoice).filter(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            db.query(ProformaInvoiceItem).filter(ProformaInvoiceItem.proforma_invoice_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = ProformaInvoiceItem(
                    proforma_invoice_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Proforma invoice {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating proforma invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update proforma invoice"
        )

@router.delete("/{invoice_id}")
async def delete_proforma_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(ProformaInvoice).filter(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        db.query(ProformaInvoiceItem).filter(ProformaInvoiceItem.proforma_invoice_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Proforma invoice {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Proforma invoice deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting proforma invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete proforma invoice"
        )