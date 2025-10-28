from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from io import BytesIO
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseReturn, PurchaseReturnItem
from app.schemas.vouchers import PurchaseReturnCreate, PurchaseReturnInDB, PurchaseReturnUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.services.pdf_generation_service import pdf_generator
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
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all purchase returns"""
    current_user, org_id = auth
    
    stmt = select(PurchaseReturn).options(
        joinedload(PurchaseReturn.vendor),
        joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
    ).where(
        PurchaseReturn.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PurchaseReturn.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseReturn, sortBy):
        sort_attr = getattr(PurchaseReturn, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(PurchaseReturn.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_return_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available purchase return number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PR", org_id, PurchaseReturn, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Check if creating a voucher with the given date would create conflicts"""
    current_user, org_id = auth
    
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PR", org_id, PurchaseReturn, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# Register both "" and "/" for POST to support both /api/v1/purchase-returns and /api/v1/purchase-returns/
@router.post("", response_model=PurchaseReturnInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseReturnInDB)
async def create_purchase_return(
    invoice: PurchaseReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new purchase return"""
    current_user, org_id = auth
    
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in invoice_data and invoice_data['date']:
            voucher_date = invoice_data['date'] if hasattr(invoice_data['date'], 'year') else None
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PR", org_id, PurchaseReturn, voucher_date=voucher_date
            )
        else:
            stmt = select(PurchaseReturn).where(
                PurchaseReturn.organization_id == org_id,
                PurchaseReturn.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PR", org_id, PurchaseReturn, voucher_date=voucher_date
            )
        
        db_invoice = PurchaseReturn(**invoice_data)
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
            
            item = PurchaseReturnItem(
                purchase_return_id=db_invoice.id,
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
        stmt = select(PurchaseReturn).options(
            joinedload(PurchaseReturn.vendor),
            joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
        ).where(PurchaseReturn.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalar_one_or_none()
        
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
        await db.rollback()
        logger.error(f"Error creating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase return"
        )

@router.get("/{invoice_id}", response_model=PurchaseReturnInDB)
async def get_purchase_return(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(PurchaseReturn).options(
        joinedload(PurchaseReturn.vendor),
        joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
    ).where(
        PurchaseReturn.id == invoice_id,
        PurchaseReturn.organization_id == org_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase return not found"
        )
    return invoice

@router.get("/{invoice_id}/pdf")
async def generate_purchase_return_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseReturn).options(
            joinedload(PurchaseReturn.vendor),
            joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
        ).where(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Purchase return not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="purchase_return",
            voucher_data=voucher.__dict__,
            db=db,
            organization_id=org_id,
            current_user=current_user
        )
        
        # Sanitize voucher_number for filename (replace /, :, etc. with -)
        safe_filename = re.sub(r'[/\\:?"<>|]', '-', voucher.voucher_number) + '.pdf'
        
        headers = {
            'Content-Disposition': f'attachment; filename="{safe_filename}"'
        }
        
        return StreamingResponse(pdf_content, media_type='application/pdf', headers=headers)
        
    except Exception as e:
        logger.error(f"Error generating PDF for purchase return {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.put("/{invoice_id}", response_model=PurchaseReturnInDB)
async def update_purchase_return(
    invoice_id: int,
    invoice_update: PurchaseReturnUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseReturn).where(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
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
            stmt_delete = delete(PurchaseReturnItem).where(PurchaseReturnItem.purchase_return_id == invoice_id)
            await db.execute(stmt_delete)
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
                
                item = PurchaseReturnItem(
                    purchase_return_id=invoice_id,
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
            invoice.total_amount = total_amount
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            invoice.discount_amount = total_discount
        
        await db.commit()
        
        # Re-query with joins to load relationships
        stmt = select(PurchaseReturn).options(
            joinedload(PurchaseReturn.vendor),
            joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
        ).where(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        logger.info(f"Purchase return {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase return"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_return(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseReturn).where(
            PurchaseReturn.id == invoice_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(PurchaseReturnItem).where(PurchaseReturnItem.purchase_return_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Purchase return {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase return deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase return"
        )