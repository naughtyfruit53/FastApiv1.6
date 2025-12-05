# app/api/v1/vouchers/payment_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import timezone, datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.financial import PaymentVoucher
from app.models.customer_models import Vendor, Customer  # Vendor and Customer are in customer_models.py
from app.models.hr_models import EmployeeProfile as Employee  # Employee is EmployeeProfile in hr_models.py
from app.models.erp_models import ChartOfAccounts
from app.schemas.vouchers import PaymentVoucherCreate, PaymentVoucherInDB, PaymentVoucherUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["payment-vouchers"])

async def load_entity(db: AsyncSession, entity_id: int, entity_type: str) -> Optional[Dict[str, Any]]:
    if entity_type == 'Vendor':
        stmt = select(Vendor).where(Vendor.id == entity_id)
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
        return {'id': entity.id, 'name': entity.name, 'type': 'Vendor'} if entity else None
    elif entity_type == 'Customer':
        stmt = select(Customer).where(Customer.id == entity_id)
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return {'id': entity.id, 'name': entity.name, 'type': 'Customer'} if entity else None
    elif entity_type == 'Employee':
        stmt = select(Employee).where(Employee.id == entity_id)
        result = await db.execute(stmt)
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return {'id': entity.id, 'name': entity.name, 'type': 'Employee'} if entity else None
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid entity type")

async def validate_chart_account(db: AsyncSession, chart_account_id: int, organization_id: int) -> ChartOfAccounts:
    """Validate that chart_account_id exists and belongs to organization"""
    stmt = select(ChartOfAccounts).where(
        ChartOfAccounts.id == chart_account_id,
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_active == True
    )
    result = await db.execute(stmt)
    chart_account = result.scalar_one_or_none()
    
    if not chart_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chart account ID or account not found for this organization"
        )
    
    return chart_account

@router.get("", response_model=List[PaymentVoucherInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PaymentVoucherInDB])
async def get_payment_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "read"))
):
    """Get all payment vouchers with enhanced sorting and pagination"""
    current_user, org_id = auth
    
    stmt = select(PaymentVoucher).where(
        PaymentVoucher.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PaymentVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PaymentVoucher, sortBy):
        sort_attr = getattr(PaymentVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(PaymentVoucher.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    vouchers = result.scalars().all()
    
    for voucher in vouchers:
        voucher.entity = await load_entity(db, voucher.entity_id, voucher.entity_type)
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        voucher.chart_account = chart_account
    
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_payment_voucher_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "read"))
):
    """Get the next available payment voucher number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PMT", org_id, PaymentVoucher, voucher_date=date_to_use
    )

@router.get("/check-backdated-conflict")
async def check_backdated_conflict(
    voucher_date: str = Query(..., description="Voucher date (ISO format) to check for conflicts"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "read"))
):
    """Check if creating a voucher with the given date would create conflicts"""
    current_user, org_id = auth
    
    try:
        parsed_date = date_parser.parse(voucher_date)
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PMT", org_id, PaymentVoucher, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# Register both "" and "/" for POST to support both /api/v1/payment-vouchers and /api/v1/payment-vouchers/
@router.post("", response_model=PaymentVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PaymentVoucherInDB)
async def create_payment_voucher(
    voucher: PaymentVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "write"))
):
    """Create new payment voucher"""
    current_user, org_id = auth
    
    try:
        if voucher.entity_type not in ['Vendor', 'Customer', 'Employee']:
            raise HTTPException(status_code=400, detail="Invalid entity_type")
        
        # Validate chart account
        chart_account = await validate_chart_account(db, voucher.chart_account_id, org_id)
        
        voucher_data = voucher.dict()
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in voucher_data and voucher_data['date']:
            voucher_data['date'] = voucher_data['date'].replace(tzinfo=timezone.utc)
            voucher_date = voucher_data['date']
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PMT", org_id, PaymentVoucher, voucher_date=voucher_date
            )
        else:
            stmt = select(PaymentVoucher).where(
                PaymentVoucher.organization_id == org_id,
                PaymentVoucher.voucher_number == voucher_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "PMT", org_id, PaymentVoucher, voucher_date=voucher_date
                )
        
        db_voucher = PaymentVoucher(**voucher_data)
        db.add(db_voucher)
        await db.commit()
        await db.refresh(db_voucher)  # Refresh for fresh data post-commit

        # Calculate search_pattern for the period
        current_year = db_voucher.date.year
        current_month = db_voucher.date.month
        
        stmt_settings = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == org_id
        )
        result_settings = await db.execute(stmt_settings)
        org_settings = result_settings.scalars().first()
        
        full_prefix = "PMT"
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
        max_date_stmt = select(func.max(PaymentVoucher.date)).where(
            PaymentVoucher.organization_id == org_id,
            PaymentVoucher.voucher_number.like(search_pattern),
            PaymentVoucher.id != db_voucher.id,
            PaymentVoucher.is_deleted == False
        )
        result = await db.execute(max_date_stmt)
        max_date = result.scalar()
        
        if max_date and db_voucher.date < max_date:
            logger.info(f"Detected backdated insert for PMT {db_voucher.voucher_number} - triggering reindex")
            reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                db, "PMT", org_id, PaymentVoucher, db_voucher.date, db_voucher.id
            )
            if not reindex_result["success"]:
                logger.error(f"Reindex failed after backdated insert: {reindex_result['error']}")
                # Don't raise - continue with high number
            else:
                await db.refresh(db_voucher)
                logger.info(f"Reindex successful - new number: {db_voucher.voucher_number}")
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(PaymentVoucher).where(PaymentVoucher.id == db_voucher.id)
        result = await db.execute(stmt)
        db_voucher = result.unique().scalars().first()
        
        # Async-safe model_validate (with error handling)
        try:
            validated_voucher = PaymentVoucherInDB.model_validate(db_voucher)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_voucher = PaymentVoucherInDB.model_validate(db_voucher.__dict__)
        
        validated_voucher.entity = await load_entity(db, validated_voucher.entity_id, validated_voucher.entity_type)
        
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == validated_voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        validated_voucher.chart_account = chart_account
        
        if send_email and validated_voucher.entity and 'email' in validated_voucher.entity:  # Assuming entity has email, but for simplicity
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="payment_voucher",
                voucher_id=validated_voucher.id,
                recipient_email=validated_voucher.entity.get('email', ''),
                recipient_name=validated_voucher.entity['name']
            )
        
        logger.info(f"Payment voucher {validated_voucher.voucher_number} created by {current_user.email}")
        
        # Convert to Pydantic model before returning (ensures data access while session is open)
        return validated_voucher
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating payment voucher: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment voucher"
        )

@router.get("/{voucher_id}", response_model=PaymentVoucherInDB)
async def get_payment_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "read"))
):
    current_user, org_id = auth
    
    stmt = select(PaymentVoucher).where(
        PaymentVoucher.id == voucher_id,
        PaymentVoucher.organization_id == org_id
    )
    result = await db.execute(stmt)
    voucher = result.scalar_one_or_none()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment voucher not found"
        )
    voucher.entity = await load_entity(db, voucher.entity_id, voucher.entity_type)
    
    # Load chart account details
    stmt_chart = select(ChartOfAccounts).where(
        ChartOfAccounts.id == voucher.chart_account_id
    )
    result_chart = await db.execute(stmt_chart)
    chart_account = result_chart.scalar_one_or_none()
    voucher.chart_account = chart_account
    
    return voucher

@router.put("/{voucher_id}", response_model=PaymentVoucherInDB)
async def update_payment_voucher(
    voucher_id: int,
    voucher_update: PaymentVoucherUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "write"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PaymentVoucher).where(
            PaymentVoucher.id == voucher_id,
            PaymentVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment voucher not found"
            )
        
        update_data = voucher_update.dict(exclude_unset=True)
        if 'entity_type' in update_data and update_data['entity_type'] not in ['Vendor', 'Customer', 'Employee']:
            raise HTTPException(status_code=400, detail="Invalid entity_type")
        
        # Validate chart account if being updated
        if 'chart_account_id' in update_data:
            await validate_chart_account(db, update_data['chart_account_id'], org_id)
        
        if 'date' in update_data and update_data['date']:
            update_data['date'] = update_data['date'].replace(tzinfo=timezone.utc)
        
        # If date is being updated, check if it's crossing periods
        if 'date' in update_data:
            old_date = voucher.date
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
            setattr(voucher, field, value)
        
        logger.debug(f"Before commit for payment voucher {voucher_id}")
        await db.commit()
        logger.debug(f"After commit for payment voucher {voucher_id}")
        await db.refresh(voucher)  # Refresh for fresh data post-commit

        # Check for backdated conflict and reindex if necessary
        conflict_info = await VoucherNumberService.check_backdated_voucher_conflict(
            db, "PMT", org_id, PaymentVoucher, voucher.date
        )
        if conflict_info["has_conflict"] and conflict_info["later_voucher_count"] > 0:  # Skip if no vouchers to reindex
            try:
                reindex_result = await VoucherNumberService.reindex_vouchers_after_backdated_insert(
                    db, "PMT", org_id, PaymentVoucher, voucher.date, voucher.id
                )
                if not reindex_result["success"]:
                    logger.error(f"Reindex failed: {reindex_result['error']}")
                    # Continue but log - don't rollback update
                else:
                    await db.refresh(voucher)
            except Exception as e:
                logger.error(f"Error during reindex: {str(e)}")
                # Don't rollback update; log only
        
        # Final query with full eager loading to prevent lazy loads
        stmt = select(PaymentVoucher).where(
            PaymentVoucher.id == voucher_id,
            PaymentVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalars().first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment voucher not found"
            )
        
        # Async-safe model_validate (with error handling)
        try:
            validated_voucher = PaymentVoucherInDB.model_validate(voucher)
        except Exception as validate_err:
            logger.error(f"Validation error post-load: {str(validate_err)}")
            # Fallback to dict serialization if Pydantic fails on rels
            validated_voucher = PaymentVoucherInDB.model_validate(voucher.__dict__)
        
        validated_voucher.entity = await load_entity(db, validated_voucher.entity_id, validated_voucher.entity_type)
        
        # Load chart account details
        stmt_chart = select(ChartOfAccounts).where(
            ChartOfAccounts.id == validated_voucher.chart_account_id
        )
        result_chart = await db.execute(stmt_chart)
        chart_account = result_chart.scalar_one_or_none()
        validated_voucher.chart_account = chart_account
        
        logger.info(f"Payment voucher {voucher.voucher_number} updated by {current_user.email}")
        
        # Convert to Pydantic model before returning
        return validated_voucher
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating payment voucher: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment voucher"
        )

@router.delete("/{voucher_id}")
async def delete_payment_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("finance", "delete"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PaymentVoucher).where(
            PaymentVoucher.id == voucher_id,
            PaymentVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment voucher not found"
            )
        
        await db.delete(voucher)
        await db.commit()
        
        logger.info(f"Payment voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Payment voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting payment voucher: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment voucher"
        )
    