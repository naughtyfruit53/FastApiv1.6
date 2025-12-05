# app/api/v1/vouchers/proforma_invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional
from datetime import timezone, datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.presales import ProformaInvoice, ProformaInvoiceItem
from app.schemas.vouchers import ProformaInvoiceCreate, ProformaInvoiceInDB, ProformaInvoiceUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.services.pdf_generation_service import pdf_generator
from app.utils.gst_calculator import calculate_gst_amounts
from app.utils.voucher_gst_helper import get_state_codes_for_sales
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod
import logging
import re  # For filename sanitization

logger = logging.getLogger(__name__)
router = APIRouter(tags=["proforma-invoices"])

@router.get("", response_model=List[ProformaInvoiceInDB])
@router.get("/", response_model=List[ProformaInvoiceInDB])
async def get_proforma_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all proforma invoices"""
    current_user, org_id = auth
    
    stmt = select(ProformaInvoice).options(
        joinedload(ProformaInvoice.customer),
        joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
    ).where(
        ProformaInvoice.organization_id == org_id
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
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available proforma invoice number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PI", org_id, ProformaInvoice, voucher_date=date_to_use
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
            db, "PI", org_id, ProformaInvoice, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# Register both "" and "/" for POST to support both /api/v1/proforma-invoices and /api/v1/proforma-invoices/
@router.post("", response_model=ProformaInvoiceInDB, include_in_schema=False)
@router.post("/", response_model=ProformaInvoiceInDB)
async def create_proforma_invoice(
    invoice: ProformaInvoiceCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new proforma invoice"""
    current_user, org_id = auth
    
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in invoice_data and invoice_data['date']:
            invoice_data['date'] = invoice_data['date'].replace(tzinfo=timezone.utc)
            voucher_date = invoice_data['date']
        
        # Handle revisions: If parent_id provided, generate revised number
        if invoice.parent_id:
            stmt = select(ProformaInvoice).where(ProformaInvoice.id == invoice.parent_id)
            result = await db.execute(stmt)
            parent = result.scalar_one_or_none()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent proforma invoice not found")
            
            # Get latest revision number
            stmt = select(func.max(ProformaInvoice.revision_number)).where(
                ProformaInvoice.organization_id == org_id,
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
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "PI", org_id, ProformaInvoice, voucher_date=voucher_date
                )
            else:
                stmt = select(ProformaInvoice).where(
                    ProformaInvoice.organization_id == org_id,
                    ProformaInvoice.voucher_number == invoice_data['voucher_number']
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                        db, "PI", org_id, ProformaInvoice, voucher_date=voucher_date
                    )
        
        db_invoice = ProformaInvoice(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        # STRICT GST ENFORCEMENT: Get state codes (NO FALLBACK)
        company_state_code, customer_state_code = await get_state_codes_for_sales(
            db=db,
            org_id=org_id,
            customer_id=invoice_data.get('customer_id'),
            voucher_type="proforma invoice"
        )
        
        logger.info(f"Proforma Invoice GST: Company State={company_state_code}, Customer State={customer_state_code}")
        
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
            
            # SMART GST CALCULATION: Use company and customer state codes
            taxable = item_dict['taxable_amount']
            if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                # calculate_gst_amounts will validate state codes and raise ValueError if missing
                gst_amounts = calculate_gst_amounts(
                    taxable_amount=taxable,
                    gst_rate=item_dict['gst_rate'],
                    company_state_code=company_state_code,
                    customer_state_code=customer_state_code,
                    organization_id=org_id,
                    entity_id=invoice_data.get('customer_id'),
                    entity_type='customer'
                )
                item_dict['cgst_amount'] = gst_amounts['cgst_amount']
                item_dict['sgst_amount'] = gst_amounts['sgst_amount']
                item_dict['igst_amount'] = gst_amounts['igst_amount']
            
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
        await db.refresh(db_invoice)  # Refresh for fresh data post-commit

        # Calculate search_pattern for the period
        current_year = db_invoice.date.year
        current_month = db_invoice.date.month
        
        stmt_settings = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == org_id
        )
        result_settings = await db.execute(stmt_settings)
        org_settings = result_settings.scalars().first()
        
        full_prefix = "PI"
        if org_settings and org_settings.voucher_prefix_enabled and org_settings.voucher_prefix:
            full_prefix = f"{org_settings.voucher_prefix}-{full_prefix}"
        
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        reset_period = org_settings.voucher_counter_reset_period if org_settings else VoucherCounterResetPeriod.ANNUALLY
        
        period_segment = ""
        if reset_period == VoucherCounterResetPeriod.MONTHLY:
            month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            period_segment = month_names[current_month - 1]
        elif reset_period == VoucherCounterResetPeriod.QUARTERLY:
            quarter = ((current_month - 1) // 3) + 1
            period_segment = f"Q{quarter}"
        
        if period_segment:
            search_pattern = f"{full_prefix}/{fiscal_year}/{period_segment}/%"
        else:
            search_pattern = f"{full_prefix}/{fiscal_year}/%"
        
        # Check if backdated: if new date < max date in period (excluding this)
        max_date_stmt = select(func.max(ProformaInvoice.date)).where(
            ProformaInvoice.organization_id == org_id,
            ProformaInvoice.voucher_number.like(search_pattern),
            ProformaInvoice.id != db_invoice.id,
            ProformaInvoice.is_deleted == False
        )
        result = await db.execute(max_date_stmt)
        max_date = result.scalar()
        
        if max_date and db_invoice.date < max_date:
            logger.info(f"Detected backdated insert for PI {db_invoice.voucher_number} - triggering reindex")
            reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                db, "PI", org_id, ProformaInvoice, db_invoice.date, db_invoice.id
            )
            if not reindex_result["success"]:
                logger.error(f"Reindex failed after backdated insert: {reindex_result['error']}")
                # Don't raise - continue with high number
            else:
                await db.refresh(db_invoice)
                logger.info(f"Reindex successful - new number: {db_invoice.voucher_number}")
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            selectinload(ProformaInvoice.items).selectinload(ProformaInvoiceItem.product)  # Nested eager for async safety
        ).where(ProformaInvoice.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalars().first()
        
        # Async-safe model_validate (with error handling)
        try:
            validated_invoice = ProformaInvoiceInDB.model_validate(db_invoice)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_invoice = ProformaInvoiceInDB.model_validate(db_invoice.__dict__)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="proforma_invoice",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Proforma invoice {db_invoice.voucher_number} created by {current_user.email}")
        
        # Convert to Pydantic model before returning (ensures data access while session is open)
        return validated_invoice
        
    except HTTPException as he:
        await db.rollback()
        raise he
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
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(ProformaInvoice).options(
        joinedload(ProformaInvoice.customer),
        joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
    ).where(
        ProformaInvoice.id == invoice_id,
        ProformaInvoice.organization_id == org_id
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
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            joinedload(ProformaInvoice.items).joinedload(ProformaInvoiceItem.product)
        ).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Proforma invoice not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="proforma_invoice",
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
        logger.error(f"Error generating PDF for proforma invoice {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.put("/{invoice_id}", response_model=ProformaInvoiceInDB)
async def update_proforma_invoice(
    invoice_id: int,
    invoice_update: ProformaInvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(ProformaInvoice).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        
        if 'date' in update_data and update_data['date']:
            update_data['date'] = update_data['date'].replace(tzinfo=timezone.utc)
        
        # If date is being updated, check if it's crossing periods
        if 'date' in update_data:
            old_date = invoice.date
            new_date = update_data['date']
            stmt_settings = select(OrganizationSettings).where(
                OrganizationSettings.organization_id == org_id
            )
            result_settings = await db.execute(stmt_settings)
            org_settings = result_settings.scalars().first()
            reset_period = org_settings.voucher_counter_reset_period if org_settings else VoucherCounterResetPeriod.ANNUALLY

            def get_period(dt: datetime) -> str:
                year = dt.year
                month = dt.month
                fiscal_year = f"{str(year)[-2:]}{str(year + 1 if month > 3 else year)[-2:]}"
                if reset_period == VoucherCounterResetPeriod.MONTHLY:
                    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                    return f"{fiscal_year}/{month_names[month - 1]}"
                elif reset_period == VoucherCounterResetPeriod.QUARTERLY:
                    quarter = ((month - 1) // 3) + 1
                    return f"{fiscal_year}/Q{quarter}"
                else:
                    return fiscal_year

            old_period = get_period(old_date)
            new_period = get_period(new_date)
            if old_period != new_period:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot change voucher date across numbering periods"
                )
            
            # DO NOT regenerate voucher number on date change within same period!
            # Keep the original number — that's the whole point
            # Only regenerate if crossing fiscal periods (which is blocked above)
            pass
        
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
        await db.refresh(invoice)  # Refresh for fresh data post-commit

        # Check for backdated conflict and reindex if necessary
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PI", org_id, ProformaInvoice, invoice.date
        )
        if conflict_info["has_conflict"] and conflict_info["later_voucher_count"] > 0:  # Skip if no vouchers to reindex
            try:
                reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                    db, "PI", org_id, ProformaInvoice, invoice.date, invoice.id
                )
                if not reindex_result["success"]:
                    logger.error(f"Reindex failed: {reindex_result['error']}")
                    # Continue but log - don't rollback update
                else:
                    await db.refresh(invoice)
            except Exception as e:
                logger.error(f"Error during reindex: {str(e)}")
                # Don't rollback update; log only
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(ProformaInvoice).options(
            joinedload(ProformaInvoice.customer),
            selectinload(ProformaInvoice.items).selectinload(ProformaInvoiceItem.product)  # Nested eager for async safety
        ).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalars().first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proforma invoice not found"
            )
        
        # Async-safe model_validate (with error handling)
        try:
            validated_invoice = ProformaInvoiceInDB.model_validate(invoice)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_invoice = ProformaInvoiceInDB.model_validate(invoice.__dict__)
        
        logger.info(f"Proforma invoice {invoice.voucher_number} updated by {current_user.email}")
        
        # Convert to Pydantic model before returning
        return validated_invoice
        
    except HTTPException as he:
        await db.rollback()
        raise he
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
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(ProformaInvoice).where(
            ProformaInvoice.id == invoice_id,
            ProformaInvoice.organization_id == org_id
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
    