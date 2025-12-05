# app/api/v1/vouchers/purchase_return.py

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
from app.models import User, Stock
from app.models.vouchers.purchase import PurchaseReturn, PurchaseReturnItem
from app.schemas.vouchers import PurchaseReturnCreate, PurchaseReturnInDB, PurchaseReturnUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-returns"])

@router.get("", response_model=List[PurchaseReturnInDB])
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
        joinedload(PurchaseReturn.reference_voucher),
        joinedload(PurchaseReturn.grn),
        joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
    ).where(
        PurchaseReturn.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PurchaseReturn.status == status)
    
    if hasattr(PurchaseReturn, sortBy):
        sort_attr = getattr(PurchaseReturn, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        stmt = stmt.order_by(PurchaseReturn.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    returns = result.unique().scalars().all()
    
    return returns

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

@router.post("", response_model=PurchaseReturnInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseReturnInDB)
async def create_purchase_return(
    return_data: PurchaseReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new purchase return"""
    current_user, org_id = auth
    
    try:
        # Check if a purchase return already exists for this GRN
        if return_data.grn_id:
            stmt = select(PurchaseReturn).where(
                PurchaseReturn.grn_id == return_data.grn_id,
                PurchaseReturn.organization_id == org_id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Purchase return already created for this GRN"
                )
        
        voucher_data = return_data.dict(exclude={'items'})
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in voucher_data and voucher_data['date']:
            voucher_data['date'] = voucher_data['date'].replace(tzinfo=timezone.utc)
            voucher_date = voucher_data['date']
        
        # Always generate high number for insert to avoid duplicate
        voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
            db, "PR", org_id, PurchaseReturn, voucher_date=voucher_date
        )
        
        db_return = PurchaseReturn(**voucher_data)
        db.add(db_return)
        await db.flush()
        
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        for item_data in return_data.items:
            item_dict = item_data.dict()
            
            logger.debug(f"Saving purchase return item: product_id={item_dict['product_id']}, "
                        f"quantity={item_dict['quantity']}, "
                        f"unit_price={item_dict['unit_price']}, "
                        f"discount_percentage={item_dict['discount_percentage']}, "
                        f"gst_rate={item_dict['gst_rate']}")
            
            # Calculate taxable_amount if not provided
            if 'taxable_amount' not in item_dict or item_dict['taxable_amount'] is None:
                item_dict['taxable_amount'] = item_dict['quantity'] * item_dict['unit_price'] - item_dict.get('discount_amount', 0.0)
            
            taxable = item_dict['taxable_amount']
            
            # Calculate GST amounts if not provided
            if 'cgst_amount' not in item_dict or item_dict['cgst_amount'] is None:
                item_dict['cgst_amount'] = taxable * (item_dict['gst_rate'] / 200)
            
            if 'sgst_amount' not in item_dict or item_dict['sgst_amount'] is None:
                item_dict['sgst_amount'] = taxable * (item_dict['gst_rate'] / 200)
            
            if 'igst_amount' not in item_dict or item_dict['igst_amount'] is None:
                item_dict['igst_amount'] = 0.0
            
            cgst = item_dict['cgst_amount']
            sgst = item_dict['sgst_amount']
            igst = item_dict['igst_amount']
            
            # Set total_amount for item
            item_dict['total_amount'] = taxable + cgst + sgst + igst
            
            item = PurchaseReturnItem(
                purchase_return_id=db_return.id,
                **item_dict
            )
            db.add(item)
            
            # Update totals
            total_amount += item.total_amount
            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst
            total_discount += item_dict.get('discount_amount', 0.0)
            
            # Update stock (deduct returned quantity)
            stmt = select(Stock).where(
                Stock.product_id == item.product_id,
                Stock.organization_id == org_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock:
                stock.quantity -= item.quantity
            else:
                logger.warning(f"No stock found for product {item.product_id} during return")
        
        db_return.total_amount = total_amount
        db_return.cgst_amount = total_cgst
        db_return.sgst_amount = total_sgst
        db_return.igst_amount = total_igst
        db_return.discount_amount = total_discount
        
        await db.commit()
        await db.refresh(db_return)  # Refresh for fresh data post-commit

        # Calculate search_pattern for the period
        current_year = db_return.date.year
        current_month = db_return.date.month
        
        stmt_settings = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == org_id
        )
        result_settings = await db.execute(stmt_settings)
        org_settings = result_settings.scalars().first()
        
        full_prefix = "PR"
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
        max_date_stmt = select(func.max(PurchaseReturn.date)).where(
            PurchaseReturn.organization_id == org_id,
            PurchaseReturn.voucher_number.like(search_pattern),
            PurchaseReturn.id != db_return.id,
            PurchaseReturn.is_deleted == False
        )
        result = await db.execute(max_date_stmt)
        max_date = result.scalar()
        
        if max_date and db_return.date < max_date:
            logger.info(f"Detected backdated insert for PR {db_return.voucher_number} - triggering reindex")
            reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                db, "PR", org_id, PurchaseReturn, db_return.date, db_return.id
            )
            if not reindex_result["success"]:
                logger.error(f"Reindex failed after backdated insert: {reindex_result['error']}")
                # Don't raise - continue with high number
            else:
                await db.refresh(db_return)
                logger.info(f"Reindex successful - new number: {db_return.voucher_number}")
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(PurchaseReturn).options(
            joinedload(PurchaseReturn.vendor),
            joinedload(PurchaseReturn.reference_voucher),
            joinedload(PurchaseReturn.grn),
            selectinload(PurchaseReturn.items).selectinload(PurchaseReturnItem.product)  # Nested eager for async safety
        ).where(PurchaseReturn.id == db_return.id)
        result = await db.execute(stmt)
        db_return = result.unique().scalars().first()
        
        # Async-safe model_validate (with error handling)
        try:
            validated_return = PurchaseReturnInDB.model_validate(db_return)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_return = PurchaseReturnInDB.model_validate(db_return.__dict__)
        
        if send_email and db_return.vendor and db_return.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_return",
                voucher_id=db_return.id,
                recipient_email=db_return.vendor.email,
                recipient_name=db_return.vendor.name
            )
        
        logger.info(f"Purchase return {db_return.voucher_number} created by {current_user.email}")
        
        # Convert to Pydantic model before returning (ensures data access while session is open)
        return validated_return
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating purchase return: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase return"
        )

@router.get("/{return_id}", response_model=PurchaseReturnInDB)
async def get_purchase_return(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get a specific purchase return"""
    current_user, org_id = auth
    
    stmt = select(PurchaseReturn).options(
        joinedload(PurchaseReturn.vendor),
        joinedload(PurchaseReturn.reference_voucher),
        joinedload(PurchaseReturn.grn),
        joinedload(PurchaseReturn.items).joinedload(PurchaseReturnItem.product)
    ).where(
        PurchaseReturn.id == return_id,
        PurchaseReturn.organization_id == org_id
    )
    result = await db.execute(stmt)
    return_data = result.unique().scalar_one_or_none()
    if not return_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase return not found"
        )
    return return_data

@router.put("/{return_id}", response_model=PurchaseReturnInDB)
async def update_purchase_return(
    return_id: int,
    return_update: PurchaseReturnUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    """Update a purchase return"""
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseReturn).where(
            PurchaseReturn.id == return_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        return_data = result.scalar_one_or_none()
        if not return_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        update_data = return_update.dict(exclude_unset=True, exclude={'items'})
        
        if 'date' in update_data and update_data['date']:
            update_data['date'] = update_data['date'].replace(tzinfo=timezone.utc)
        
        # If date is being updated, check if it's crossing periods
        if 'date' in update_data:
            old_date = return_data.date
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
            setattr(return_data, field, value)
        
        if return_update.items is not None:
            stmt = select(PurchaseReturnItem).where(
                PurchaseReturnItem.purchase_return_id == return_id
            )
            result = await db.execute(stmt)
            old_items = result.scalars().all()
            
            for old_item in old_items:
                stmt = select(Stock).where(
                    Stock.product_id == old_item.product_id,
                    Stock.organization_id == org_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                if stock:
                    stock.quantity += old_item.quantity  # Add back old returned quantity
            
            from sqlalchemy import delete
            stmt_delete = delete(PurchaseReturnItem).where(PurchaseReturnItem.purchase_return_id == return_id)
            await db.execute(stmt_delete)
            await db.flush()
            
            total_amount = 0.0
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            total_discount = 0.0
            
            for item_data in return_update.items:
                item_dict = item_data.dict()
                
                logger.debug(f"Updating purchase return item: product_id={item_dict['product_id']}, "
                            f"quantity={item_dict['quantity']}, "
                            f"unit_price={item_dict['unit_price']}, "
                            f"discount_percentage={item_dict['discount_percentage']}, "
                            f"gst_rate={item_dict['gst_rate']}")
                
                # Calculate taxable_amount if not provided
                if 'taxable_amount' not in item_dict or item_dict['taxable_amount'] is None:
                    item_dict['taxable_amount'] = item_dict['quantity'] * item_dict['unit_price'] - item_dict.get('discount_amount', 0.0)
                
                taxable = item_dict['taxable_amount']
                
                # Calculate GST amounts if not provided
                if 'cgst_amount' not in item_dict or item_dict['cgst_amount'] is None:
                    item_dict['cgst_amount'] = taxable * (item_dict['gst_rate'] / 200)
                
                if 'sgst_amount' not in item_dict or item_dict['sgst_amount'] is None:
                    item_dict['sgst_amount'] = taxable * (item_dict['gst_rate'] / 200)
                
                if 'igst_amount' not in item_dict or item_dict['igst_amount'] is None:
                    item_dict['igst_amount'] = 0.0
                
                cgst = item_dict['cgst_amount']
                sgst = item_dict['sgst_amount']
                igst = item_dict['igst_amount']
                
                # Set total_amount for item
                item_dict['total_amount'] = taxable + cgst + sgst + igst
                
                item = PurchaseReturnItem(
                    purchase_return_id=return_id,
                    **item_dict
                )
                db.add(item)
                
                # Update totals
                total_amount += item.total_amount
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
                total_discount += item_dict.get('discount_amount', 0.0)
                
                # Update stock (deduct new returned quantity)
                stmt = select(Stock).where(
                    Stock.product_id == item.product_id,
                    Stock.organization_id == org_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                if stock:
                    stock.quantity -= item.quantity
                else:
                    logger.warning(f"No stock found for product {item.product_id} during return update")
            
            await db.flush()
            
            return_data.total_amount = total_amount
            return_data.cgst_amount = total_cgst
            return_data.sgst_amount = total_sgst
            return_data.igst_amount = total_igst
            return_data.discount_amount = total_discount
        
        logger.debug(f"Before commit for purchase return {return_id}")
        await db.commit()
        logger.debug(f"After commit for purchase return {return_id}")
        await db.refresh(return_data)  # Refresh for fresh data post-commit

        # Check for backdated conflict and reindex if necessary
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PR", org_id, PurchaseReturn, return_data.date
        )
        if conflict_info["has_conflict"] and conflict_info["later_voucher_count"] > 0:  # Skip if no vouchers to reindex
            try:
                reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                    db, "PR", org_id, PurchaseReturn, return_data.date, return_data.id
                )
                if not reindex_result["success"]:
                    logger.error(f"Reindex failed: {reindex_result['error']}")
                    # Continue but log - don't rollback update
                else:
                    await db.refresh(return_data)
            except Exception as e:
                logger.error(f"Error during reindex: {str(e)}")
                # Don't rollback update; log only
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(PurchaseReturn).options(
            joinedload(PurchaseReturn.vendor),
            joinedload(PurchaseReturn.reference_voucher),
            joinedload(PurchaseReturn.grn),
            selectinload(PurchaseReturn.items).selectinload(PurchaseReturnItem.product)  # Nested eager for async safety
        ).where(
            PurchaseReturn.id == return_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        return_data = result.unique().scalars().first()
        if not return_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        # Async-safe model_validate (with error handling)
        try:
            validated_return = PurchaseReturnInDB.model_validate(return_data)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_return = PurchaseReturnInDB.model_validate(return_data.__dict__)
        
        logger.info(f"Purchase return {return_data.voucher_number} updated by {current_user.email}")
        
        # Convert to Pydantic model before returning
        return validated_return
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating purchase return {return_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase return"
        )

@router.delete("/{return_id}")
async def delete_purchase_return(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    """Delete a purchase return"""
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseReturn).where(
            PurchaseReturn.id == return_id,
            PurchaseReturn.organization_id == org_id
        )
        result = await db.execute(stmt)
        return_data = result.scalar_one_or_none()
        if not return_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        stmt = select(PurchaseReturnItem).where(
            PurchaseReturnItem.purchase_return_id == return_id
        )
        result = await db.execute(stmt)
        old_items = result.scalars().all()
        
        for old_item in old_items:
            stmt = select(Stock).where(
                Stock.product_id == old_item.product_id,
                Stock.organization_id == org_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock:
                stock.quantity += old_item.quantity  # Add back deleted return quantity
        
        from sqlalchemy import delete
        stmt_delete_items = delete(PurchaseReturnItem).where(PurchaseReturnItem.purchase_return_id == return_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(return_data)
        await db.commit()
        
        logger.info(f"Purchase return {return_data.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase return deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase return"
        )
    