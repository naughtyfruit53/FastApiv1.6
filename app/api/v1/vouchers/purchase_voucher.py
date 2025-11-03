# app/api/v1/vouchers/purchase_voucher.py

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
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models import User
from app.models.user_models import Organization
from app.models.customer_models import Vendor
from app.models.vouchers.purchase import PurchaseVoucher, PurchaseVoucherItem
from app.schemas.vouchers import PurchaseVoucherCreate, PurchaseVoucherInDB, PurchaseVoucherUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.services.pdf_generation_service import pdf_generator
from app.utils.gst_calculator import calculate_gst_amounts
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-vouchers"])

@router.get("", response_model=List[PurchaseVoucherInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PurchaseVoucherInDB])
async def get_purchase_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    auth: tuple = Depends(require_access("voucher", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all purchase vouchers"""
    current_user, org_id = auth
    
    stmt = select(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).where(
        PurchaseVoucher.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PurchaseVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseVoucher, sortBy):
        sort_attr = getattr(PurchaseVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(PurchaseVoucher.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_voucher_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    auth: tuple = Depends(require_access("voucher", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get the next available purchase voucher number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PV", org_id, PurchaseVoucher, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    auth: tuple = Depends(require_access("voucher", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Check if creating a voucher with the given date would create conflicts"""
    current_user, org_id = auth
    
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PV", org_id, PurchaseVoucher, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# Register both "" and "/" for POST to support both /api/v1/purchase-vouchers and /api/v1/purchase-vouchers/
@router.post("", response_model=PurchaseVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseVoucherInDB)
async def create_purchase_voucher(
    invoice: PurchaseVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    auth: tuple = Depends(require_access("voucher", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new purchase voucher"""
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
                db, "PV", org_id, PurchaseVoucher, voucher_date=voucher_date
            )
        else:
            stmt = select(PurchaseVoucher).where(
                PurchaseVoucher.organization_id == org_id,
                PurchaseVoucher.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PV", org_id, PurchaseVoucher, voucher_date=voucher_date
            )
        
        db_invoice = PurchaseVoucher(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        # Get organization's state code for GST calculation (REQUIRED)
        org_result = await db.execute(
            select(Organization.state_code).where(Organization.id == org_id)
        )
        company_state_code = org_result.scalar_one_or_none()
        if not company_state_code:
            logger.error(f"Organization {org_id} is missing state_code - required for GST calculation")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization state code is required for GST calculation. Please update organization details."
            )
        
        # Get vendor's state code if vendor is specified (REQUIRED for GST)
        vendor_state_code = None
        if invoice_data.get('vendor_id'):
            vendor_result = await db.execute(
                select(Vendor.state_code).where(Vendor.id == invoice_data['vendor_id'])
            )
            vendor_state_code = vendor_result.scalar_one_or_none()
            if not vendor_state_code:
                logger.error(f"Vendor {invoice_data['vendor_id']} is missing state_code - required for GST calculation")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vendor state code is required for GST calculation. Please update vendor details."
                )
        
        logger.info(f"Purchase GST Calculation: Company State={company_state_code}, Vendor State={vendor_state_code}")
        
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
            
            # SMART GST CALCULATION: Use company and vendor state codes
            taxable = item_dict['taxable_amount']
            if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                # Ensure we have both state codes for GST calculation
                if not vendor_state_code:
                    logger.error("Cannot calculate GST without vendor state code")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vendor state code is required for GST calculation"
                    )
                
                gst_amounts = calculate_gst_amounts(
                    taxable_amount=taxable,
                    gst_rate=item_dict['gst_rate'],
                    company_state_code=company_state_code,
                    customer_state_code=vendor_state_code  # For purchase, vendor is the "other party"
                )
                item_dict['cgst_amount'] = gst_amounts['cgst_amount']
                item_dict['sgst_amount'] = gst_amounts['sgst_amount']
                item_dict['igst_amount'] = gst_amounts['igst_amount']
                
                logger.debug(f"Purchase Item GST: Taxable={taxable}, Rate={item_dict['gst_rate']}%, "
                           f"CGST={item_dict['cgst_amount']}, SGST={item_dict['sgst_amount']}, "
                           f"IGST={item_dict['igst_amount']}")
            
            # Always calculate total_amount to ensure it's not None or incorrect
            item_dict['total_amount'] = (
                item_dict['taxable_amount'] +
                item_dict['cgst_amount'] +
                item_dict['sgst_amount'] +
                item_dict['igst_amount']
            )
            
            item = PurchaseVoucherItem(
                purchase_voucher_id=db_invoice.id,
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
        stmt = select(PurchaseVoucher).options(
            joinedload(PurchaseVoucher.vendor),
            joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
        ).where(PurchaseVoucher.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalar_one_or_none()
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_voucher",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Purchase voucher {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase voucher"
        )

@router.get("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher(
    invoice_id: int,
    auth: tuple = Depends(require_access("voucher", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).where(
        PurchaseVoucher.id == invoice_id,
        PurchaseVoucher.organization_id == org_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase voucher not found"
        )
    return invoice

@router.get("/{invoice_id}/pdf")
async def generate_purchase_voucher_pdf(
    invoice_id: int,
    auth: tuple = Depends(require_access("voucher", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseVoucher).options(
            joinedload(PurchaseVoucher.vendor),
            joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
        ).where(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Purchase voucher not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="purchase_voucher",
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
        logger.error(f"Error generating PDF for purchase voucher {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.put("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def update_purchase_voucher(
    invoice_id: int,
    invoice_update: PurchaseVoucherUpdate,
    auth: tuple = Depends(require_access("voucher", "update")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseVoucher).where(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
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
            stmt_delete = delete(PurchaseVoucherItem).where(PurchaseVoucherItem.purchase_voucher_id == invoice_id)
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
                
                item = PurchaseVoucherItem(
                    purchase_voucher_id=invoice_id,
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
        stmt = select(PurchaseVoucher).options(
            joinedload(PurchaseVoucher.vendor),
            joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
        ).where(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        logger.info(f"Purchase voucher {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase voucher"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_voucher(
    invoice_id: int,
    auth: tuple = Depends(require_access("voucher", "delete")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseVoucher).where(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(PurchaseVoucherItem).where(PurchaseVoucherItem.purchase_voucher_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Purchase voucher {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase voucher"
        )