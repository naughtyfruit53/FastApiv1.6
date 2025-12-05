# app/api/v1/vouchers/delivery_challan.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
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
from app.models.vouchers.sales import DeliveryChallan, DeliveryChallanItem
from app.schemas.vouchers import DeliveryChallanCreate, DeliveryChallanInDB, DeliveryChallanUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod
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
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all delivery challans"""
    current_user, org_id = auth
    
    stmt = select(DeliveryChallan).options(
        joinedload(DeliveryChallan.customer),
        joinedload(DeliveryChallan.items).joinedload(DeliveryChallanItem.product)
    ).where(
        DeliveryChallan.organization_id == org_id
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
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available delivery challan number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "DC", org_id, DeliveryChallan, voucher_date=date_to_use
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
            db, "DC", org_id, DeliveryChallan, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# Register both "" and "/" for POST to support both /api/v1/delivery-challans and /api/v1/delivery-challans/
@router.post("", response_model=DeliveryChallanInDB, include_in_schema=False)
@router.post("/", response_model=DeliveryChallanInDB)
async def create_delivery_challan(
    invoice: DeliveryChallanCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new delivery challan"""
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
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "DC", org_id, DeliveryChallan, voucher_date=voucher_date
            )
        else:
            stmt = select(DeliveryChallan).where(
                DeliveryChallan.organization_id == org_id,
                DeliveryChallan.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "DC", org_id, DeliveryChallan, voucher_date=voucher_date
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
        await db.refresh(db_invoice)  # Refresh for fresh data post-commit

        # Calculate search_pattern for the period
        current_year = db_invoice.date.year
        current_month = db_invoice.date.month
        
        stmt_settings = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == org_id
        )
        result_settings = await db.execute(stmt_settings)
        org_settings = result_settings.scalars().first()
        
        full_prefix = "DC"
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
        max_date_stmt = select(func.max(DeliveryChallan.date)).where(
            DeliveryChallan.organization_id == org_id,
            DeliveryChallan.voucher_number.like(search_pattern),
            DeliveryChallan.id != db_invoice.id,
            DeliveryChallan.is_deleted == False
        )
        result = await db.execute(max_date_stmt)
        max_date = result.scalar()
        
        if max_date and db_invoice.date < max_date:
            logger.info(f"Detected backdated insert for DC {db_invoice.voucher_number} - triggering reindex")
            reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                db, "DC", org_id, DeliveryChallan, db_invoice.date, db_invoice.id
            )
            if not reindex_result["success"]:
                logger.error(f"Reindex failed after backdated insert: {reindex_result['error']}")
                # Don't raise - continue with high number
            else:
                await db.refresh(db_invoice)
                logger.info(f"Reindex successful - new number: {db_invoice.voucher_number}")
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(DeliveryChallan).options(
            joinedload(DeliveryChallan.customer),
            selectinload(DeliveryChallan.items).selectinload(DeliveryChallanItem.product)  # Nested eager for async safety
        ).where(DeliveryChallan.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalars().first()
        
        # Async-safe model_validate (with error handling)
        try:
            validated_invoice = DeliveryChallanInDB.model_validate(db_invoice)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_invoice = DeliveryChallanInDB.model_validate(db_invoice.__dict__)
        
        if send_email and db_invoice.customer and db_invoice.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="delivery_challan",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.customer.email,
                recipient_name=db_invoice.customer.name
            )
        
        logger.info(f"Delivery challan {db_invoice.voucher_number} created by {current_user.email}")
        
        # Convert to Pydantic model before returning (ensures data access while session is open)
        return validated_invoice
        
    except HTTPException as he:
        await db.rollback()
        raise he
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
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(DeliveryChallan).options(
        joinedload(DeliveryChallan.customer),
        joinedload(DeliveryChallan.items).joinedload(DeliveryChallanItem.product)
    ).where(
        DeliveryChallan.id == invoice_id,
        DeliveryChallan.organization_id == org_id
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
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
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
        await db.refresh(invoice)  # Refresh for fresh data post-commit

        # Check for backdated conflict and reindex if necessary
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "DC", org_id, DeliveryChallan, invoice.date
        )
        if conflict_info["has_conflict"] and conflict_info["later_voucher_count"] > 0:  # Skip if no vouchers to reindex
            try:
                reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                    db, "DC", org_id, DeliveryChallan, invoice.date, invoice.id
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
        stmt = select(DeliveryChallan).options(
            joinedload(DeliveryChallan.customer),
            selectinload(DeliveryChallan.items).selectinload(DeliveryChallanItem.product)  # Nested eager for async safety
        ).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalars().first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
            )
        
        # Async-safe model_validate (with error handling)
        try:
            validated_invoice = DeliveryChallanInDB.model_validate(invoice)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_invoice = DeliveryChallanInDB.model_validate(invoice.__dict__)
        
        logger.info(f"Delivery challan {invoice.voucher_number} updated by {current_user.email}")
        
        # Convert to Pydantic model before returning
        return validated_invoice
        
    except HTTPException as he:
        await db.rollback()
        raise he
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
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == org_id
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

@router.put("/{invoice_id}/tracking")
async def update_delivery_challan_tracking(
    invoice_id: int,
    transporter_name: Optional[str] = None,
    tracking_number: Optional[str] = None,
    tracking_link: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    """Update tracking details for a delivery challan"""
    current_user, org_id = auth
    
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == org_id
        )
        result = await db.execute(stmt)
        dc = result.scalar_one_or_none()
        
        if not dc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
            )
        
        # Update tracking fields
        if transporter_name is not None:
            dc.transporter_name = transporter_name
        if tracking_number is not None:
            dc.tracking_number = tracking_number
        if tracking_link is not None:
            dc.tracking_link = tracking_link
        
        await db.commit()
        await db.refresh(dc)
        
        logger.info(f"Tracking details updated for DC {dc.voucher_number} by {current_user.email}")
        return {
            "message": "Tracking details updated successfully",
            "transporter_name": dc.transporter_name,
            "tracking_number": dc.tracking_number,
            "tracking_link": dc.tracking_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating tracking details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tracking details"
        )

@router.get("/{invoice_id}/tracking")
async def get_delivery_challan_tracking(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get tracking details for a delivery challan"""
    current_user, org_id = auth
    
    try:
        stmt = select(DeliveryChallan).where(
            DeliveryChallan.id == invoice_id,
            DeliveryChallan.organization_id == org_id
        )
        result = await db.execute(stmt)
        dc = result.scalar_one_or_none()
        
        if not dc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery challan not found"
            )
        
        return {
            "transporter_name": dc.transporter_name,
            "tracking_number": dc.tracking_number,
            "tracking_link": dc.tracking_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tracking details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tracking details"
        )
    