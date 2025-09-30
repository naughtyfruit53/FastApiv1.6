# app/api/v1/vouchers/proforma_invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from io import BytesIO
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.presales import ProformaInvoice, ProformaInvoiceItem
from app.schemas.vouchers import ProformaInvoiceCreate, ProformaInvoiceInDB, ProformaInvoiceUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.services.pdf_generation_service import pdf_generator
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all proforma invoices"""
    stmt = select(ProformaInvoice).options(
        joinedload(ProformaInvoice.customer),
        joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
    ).where(
        ProformaInvoice.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(ProformaInvoice.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(ProformaInvoice, sortBy):
        sort_attr = getattr(ProformaInvoice, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(ProformaInvoice.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_proforma_invoice_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available proforma invoice number"""
    return await VoucherNumberService.generate_voucher_number(
        db, "PI", current_user.organization_id, ProformaInvoice
    )

# Register both "" and "/" for POST to support both /api/v1/proforma-invoices and /api/v1/proforma-invoices/
@router.post("", response_model=ProformaInvoiceInDB, include_in_schema=False)
@router.post("/", response_model=ProformaInvoiceInDB)
async def create_proforma_invoice(
    invoice: ProformaInvoiceCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new proforma invoice"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Handle revisions: If parent_id provided, generate revised number
        if invoice.parent_id:
            stmt = select(ProformaInvoice).where(ProformaInvoice.id == invoice.parent_id)
            result = await db.execute(stmt)
            parent = result.scalar_one_or_none()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent proforma invoice not found")
            
            # Get latest revision number
            stmt = select(func.max(ProformaInvoice.revision_number)).where(
                ProformaInvoice.organization_id == current_user.organization_id,
                ProformaInvoice.voucher_number.like(f"{parent.voucher_number}%")
            )
            result = await db.execute(stmt)
            latest_revision = result.scalar() or 0
            
            invoice_data['revision_number'] = latest_revision + 1
            invoice_data['voucher_number'] = f"{parent.voucher_number} Rev {invoice_data['revision_number']}"
            invoice_data['parent_id'] = invoice.parent_id
        else:
            # Generate unique voucher number if not provided or blank
            if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                    db, "PI", current_user.organization_id, ProformaInvoice
                )
            else:
                stmt = select(ProformaInvoice).where(
                    ProformaInvoice.organization_id == current_user.organization_id,
                    ProformaInvoice.voucher_number == invoice_data['voucher_number']
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                        db, "PI", current_user.organization_id, ProformaInvoice
                    )
        
        db_invoice = ProformaInvoice(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        # Initialize sums for header
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        for item_data in invoice.items:
            item_dict = item_data.dict()
            
            # Set defaults for missing optional fields to prevent None values
            item_dict.setdefault('discount_percentage', 0.0)
            item_dict.setdefault('discount_amount', 0.0)
            item_dict.setdefault('taxable_amount', 0.0)
            item_dict.setdefault('gst_rate', 18.0)
            item_dict.setdefault('cgst_amount', 0.0)
            item_dict.setdefault('sgst_amount', 0.0)
            item_dict.setdefault('igst_amount', 0.0)
            item_dict.setdefault('description', None)
            
            # Recalculate taxable_amount if it's 0 or inconsistent
            if item_dict['taxable_amount'] == 0:
                gross_amount = item_dict['quantity'] * item_dict['unit_price']
                discount_amount = gross_amount * (item_dict['discount_percentage'] / 100) if item_dict['discount_percentage'] else item_dict['discount_amount']
                item_dict['discount_amount'] = discount_amount
                item_dict['taxable_amount'] = gross_amount - discount_amount
            
            # Recalculate tax amounts if they are 0 (assuming intra-state by default; adjust if inter-state logic added later)
            taxable = item_dict['taxable_amount']
            if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                half_rate = item_dict['gst_rate'] / 2 / 100
                item_dict['cgst_amount'] = taxable * half_rate
                item_dict['sgst_amount'] = taxable * half_rate
                item_dict['igst_amount'] = 0.0
            
            # Always calculate total_amount to ensure it's not None or incorrect
            item_dict['total_amount'] = (
                item_dict['taxable_amount'] +
                item_dict['cgst_amount'] +
                item_dict['sgst_amount'] +
                item_dict['igst_amount']
            )
            
            item = ProformaInvoiceItem(
                proforma_invoice_id=db_invoice.id,
                **item_dict
            )
            db.add(item)
            
            # Accumulate sums for header
            total_amount += item_dict['total_amount']
            total_cgst += item_dict['cgst_amount']
            total_sgst += item_dict['sgst_amount']
            total_igst += item_dict['igst_amount']
            total_discount += item_dict['discount_amount']
        
        # Override header totals with calculated sums for consistency
        db_invoice.total_amount = total_amount
        db_invoice.cgst_amount = total_cgst
        db_invoice.sgst_amount = total_sgst
        db_invoice.igst_amount = total_igst
        db_invoice.discount_amount = total_discount
        
        await db.commit()
        
        # Re-query with joins to load relationships
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
        ).where(ProformaInvoice.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalar_one_or_none()
        
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
        await db.rollback()
        logger.error(f"Error creating proforma invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create proforma invoice"
        )

@router.get("/{invoice_id}", response_model=ProformaInvoiceInDB)
async def get_proforma_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(ProformaInvoice).options(
        joinedload(ProformaInvoice.customer),
        joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
    ).where(
        ProformaInvoice.id == invoice_id,
        ProformaInvoice.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proforma invoice not found"
        )
    return invoice

@router.get("/{invoice_id}/pdf")
async def generate_proforma_invoice_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
        ).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Proforma invoice not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="proforma_invoice",
            voucher_data=voucher.__dict__,
            db=db,
            organization_id=current_user.organization_id,
            current_user=current_user
        )
        
        headers = {
            'Content-Disposition': f'attachment; filename="proforma_invoice_{voucher.voucher_number}.pdf"'
        }
        
        return StreamingResponse(pdf_content, media_type='application/pdf', headers=headers)
        
    except Exception as e:
        logger.error(f"Error generating PDF for proforma invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.put("/{invoice_id}", response_model=ProformaInvoiceInDB)
async def update_proforma_invoice(
    invoice_id: int,
    invoice_update: ProformaInvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(ProformaInvoice).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        # Initialize sums for header if items are updated
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        if invoice_update.items is not None:
            from sqlalchemy import delete
            stmt_delete = delete(ProformaInvoiceItem).where(ProformaInvoiceItem.proforma_invoice_id == invoice_id)
            await db.execute(stmt_delete)
            await db.flush()  # Flush deletes before adding new items to avoid potential locks
            for item_data in invoice_update.items:
                item_dict = item_data.dict()
                
                # Set defaults for missing optional fields to prevent None values
                item_dict.setdefault('discount_percentage', 0.0)
                item_dict.setdefault('discount_amount', 0.0)
                item_dict.setdefault('taxable_amount', 0.0)
                item_dict.setdefault('gst_rate', 18.0)
                item_dict.setdefault('cgst_amount', 0.0)
                item_dict.setdefault('sgst_amount', 0.0)
                item_dict.setdefault('igst_amount', 0.0)
                item_dict.setdefault('description', None)
                
                # Recalculate taxable_amount if it's 0 or inconsistent
                if item_dict['taxable_amount'] == 0:
                    gross_amount = item_dict['quantity'] * item_dict['unit_price']
                    discount_amount = gross_amount * (item_dict['discount_percentage'] / 100) if item_dict['discount_percentage'] else item_dict['discount_amount']
                    item_dict['discount_amount'] = discount_amount
                    item_dict['taxable_amount'] = gross_amount - discount_amount
                
                # Recalculate tax amounts if they are 0 (assuming intra-state by default; adjust if inter-state logic added later)
                taxable = item_dict['taxable_amount']
                if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                    half_rate = item_dict['gst_rate'] / 2 / 100
                    item_dict['cgst_amount'] = taxable * half_rate
                    item_dict['sgst_amount'] = taxable * half_rate
                    item_dict['igst_amount'] = 0.0
                
                # Always calculate total_amount to ensure it's not None or incorrect
                item_dict['total_amount'] = (
                    item_dict['taxable_amount'] +
                    item_dict['cgst_amount'] +
                    item_dict['sgst_amount'] +
                    item_dict['igst_amount']
                )
                
                item = ProformaInvoiceItem(
                    proforma_invoice_id=invoice_id,
                    **item_dict
                )
                db.add(item)
                
                # Accumulate sums for header
                total_amount += item_dict['total_amount']
                total_cgst += item_dict['cgst_amount']
                total_sgst += item_dict['sgst_amount']
                total_igst += item_dict['igst_amount']
                total_discount += item_dict['discount_amount']
            
            await db.flush()  # Flush adds before commit
            
            # Override header totals with calculated sums for consistency
            invoice.total_amount = total_amount
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            invoice.discount_amount = total_discount
        
        logger.debug(f"Before commit for proforma invoice {invoice_id}")
        await db.commit()
        logger.debug(f"After commit for proforma invoice {invoice_id}")
        
        # Re-query with joins to load relationships
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
        ).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        logger.info(f"Proforma invoice {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating proforma invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update proforma invoice"
        )

@router.delete("/{invoice_id}")
async def delete_proforma_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(ProformaInvoice).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(ProformaInvoiceItem).where(ProformaInvoiceItem.proforma_invoice_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Proforma invoice {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Proforma invoice deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting proforma invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete proforma invoice"
        )