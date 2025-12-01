# app/api/v1/vouchers/purchase_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User, Stock
from app.models.vouchers.purchase import PurchaseVoucher, PurchaseVoucherItem, GoodsReceiptNoteItem
from app.schemas.vouchers import PurchaseVoucherCreate, PurchaseVoucherInDB, PurchaseVoucherUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-vouchers"])

@router.get("", response_model=dict)
@router.get("/", response_model=dict)
async def get_purchase_vouchers(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(50, ge=1, le=500, description="Number of records per page"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all purchase vouchers"""
    current_user, org_id = auth
    
    # Compute skip from page and per_page
    skip = (page - 1) * per_page if page > 0 else 0
    
    stmt = select(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.purchase_order),
        joinedload(PurchaseVoucher.grn),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).where(
        PurchaseVoucher.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PurchaseVoucher.status == status)
    
    if hasattr(PurchaseVoucher, sortBy):
        sort_attr = getattr(PurchaseVoucher, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        stmt = stmt.order_by(PurchaseVoucher.created_at.desc())
    
    # Get total count for pagination
    total_stmt = select(func.count(PurchaseVoucher.id)).where(
        PurchaseVoucher.organization_id == org_id
    )
    if status:
        total_stmt = total_stmt.where(PurchaseVoucher.status == status)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0
    
    # Get paginated results
    result = await db.execute(stmt.offset(skip).limit(per_page))
    vouchers = result.unique().scalars().all()
    
    # Convert ORM objects to Pydantic schemas for proper JSON serialization
    serialized_vouchers = [PurchaseVoucherInDB.model_validate(v) for v in vouchers]
    
    return {
        'vouchers': [v.model_dump() for v in serialized_vouchers],
        'total': total,
        'page': page,
        'per_page': per_page
    }

@router.get("/next-number", response_model=str)
async def get_next_purchase_voucher_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
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
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
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

@router.get("/for-grn/{grn_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher_for_grn(
    grn_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the purchase voucher associated with a specific GRN"""
    current_user, org_id = auth
    
    stmt = select(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.purchase_order),
        joinedload(PurchaseVoucher.grn),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).where(
        PurchaseVoucher.grn_id == grn_id,
        PurchaseVoucher.organization_id == org_id
    )
    result = await db.execute(stmt)
    voucher = result.unique().scalar_one_or_none()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No purchase voucher found for this GRN"
        )
    return voucher

@router.post("", response_model=PurchaseVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseVoucherInDB)
async def create_purchase_voucher(
    voucher: PurchaseVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new purchase voucher"""
    current_user, org_id = auth
    
    try:
        # Check if a purchase voucher already exists for this GRN
        if voucher.grn_id:
            logger.debug(f"Creating PV with grn_id: {voucher.grn_id}")
            stmt = select(PurchaseVoucher).where(
                PurchaseVoucher.grn_id == voucher.grn_id,
                PurchaseVoucher.organization_id == org_id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Purchase voucher already created for this GRN"
                )
        
        voucher_data = voucher.dict(exclude={'items'})
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in voucher_data and voucher_data['date']:
            voucher_date = voucher_data['date'] if hasattr(voucher_data['date'], 'year') else None
        elif 'invoice_date' in voucher_data and voucher_data['invoice_date']:
            voucher_date = voucher_data['invoice_date'] if hasattr(voucher_data['invoice_date'], 'year') else None
        
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PV", org_id, PurchaseVoucher, voucher_date=voucher_date
            )
        else:
            stmt = select(PurchaseVoucher).where(
                PurchaseVoucher.organization_id == org_id,
                PurchaseVoucher.voucher_number == voucher_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                voucher_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "PV", org_id, PurchaseVoucher, voucher_date=voucher_date
                )
        
        db_voucher = PurchaseVoucher(**voucher_data)
        db.add(db_voucher)
        await db.flush()
        
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        for item_data in voucher.items:
            item_dict = item_data.dict()
            
            logger.debug(f"Saving purchase voucher item: product_id={item_dict['product_id']}, "
                        f"quantity={item_dict['quantity']}, "
                        f"unit_price={item_dict['unit_price']}, "
                        f"discount_percentage={item_dict['discount_percentage']}, "
                        f"gst_rate={item_dict['gst_rate']}")
            
            item = PurchaseVoucherItem(
                purchase_voucher_id=db_voucher.id,
                **item_dict
            )
            db.add(item)
            
            # Calculate totals
            taxable = item.quantity * item.unit_price - item.discount_amount
            cgst = taxable * (item.gst_rate / 200) if item.cgst_amount else 0
            sgst = taxable * (item.gst_rate / 200) if item.sgst_amount else 0
            igst = taxable * (item.gst_rate / 100) if item.igst_amount else 0
            
            total_amount += taxable + cgst + sgst + igst
            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst
            total_discount += item.discount_amount
            
            # Update stock
            stmt = select(Stock).where(
                Stock.product_id == item.product_id,
                Stock.organization_id == org_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            if not stock:
                stock = Stock(
                    product_id=item.product_id,
                    organization_id=org_id,
                    quantity=0,
                    unit=item.unit
                )
                db.add(stock)
            stock.quantity += item.quantity
            
            # If from GRN, update GRN item
            if item.grn_item_id:
                stmt = select(GoodsReceiptNoteItem).where(
                    GoodsReceiptNoteItem.id == item.grn_item_id
                )
                result = await db.execute(stmt)
                grn_item = result.scalar_one_or_none()
                if grn_item:
                    grn_item.accepted_quantity = item.quantity  # Assuming full acceptance
                    db.add(grn_item)
        
        db_voucher.total_amount = total_amount
        db_voucher.cgst_amount = total_cgst
        db_voucher.sgst_amount = total_sgst
        db_voucher.igst_amount = total_igst
        db_voucher.discount_amount = total_discount
        
        await db.commit()
        
        stmt = select(PurchaseVoucher).options(
            joinedload(PurchaseVoucher.vendor),
            joinedload(PurchaseVoucher.purchase_order),
            joinedload(PurchaseVoucher.grn),
            joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
        ).where(PurchaseVoucher.id == db_voucher.id)
        result = await db.execute(stmt)
        db_voucher = result.unique().scalar_one_or_none()
        
        if send_email and db_voucher.vendor and db_voucher.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.vendor.email,
                recipient_name=db_voucher.vendor.name
            )
        
        logger.info(f"Purchase voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating purchase voucher: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase voucher"
        )

@router.get("/{voucher_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get a specific purchase voucher"""
    current_user, org_id = auth
    
    stmt = select(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.purchase_order),
        joinedload(PurchaseVoucher.grn),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).where(
        PurchaseVoucher.id == voucher_id,
        PurchaseVoucher.organization_id == org_id
    )
    result = await db.execute(stmt)
    voucher = result.unique().scalar_one_or_none()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase voucher not found"
        )
    return voucher

@router.put("/{voucher_id}", response_model=PurchaseVoucherInDB)
async def update_purchase_voucher(
    voucher_id: int,
    voucher_update: PurchaseVoucherUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    """Update a purchase voucher"""
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseVoucher).where(
            PurchaseVoucher.id == voucher_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        update_data = voucher_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        if voucher_update.items is not None:
            stmt = select(PurchaseVoucherItem).where(
                PurchaseVoucherItem.purchase_voucher_id == voucher_id
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
                    stock.quantity -= old_item.quantity
                
                if old_item.grn_item_id:
                    stmt = select(GoodsReceiptNoteItem).where(
                        GoodsReceiptNoteItem.id == old_item.grn_item_id
                    )
                    result = await db.execute(stmt)
                    grn_item = result.scalar_one_or_none()
                    if grn_item:
                        grn_item.accepted_quantity -= old_item.quantity
                        db.add(grn_item)
            
            from sqlalchemy import delete
            stmt_delete = delete(PurchaseVoucherItem).where(PurchaseVoucherItem.purchase_voucher_id == voucher_id)
            await db.execute(stmt_delete)
            await db.flush()
            
            total_amount = 0.0
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            total_discount = 0.0
            
            for item_data in voucher_update.items:
                item_dict = item_data.dict()
                
                logger.debug(f"Updating purchase voucher item: product_id={item_dict['product_id']}, "
                            f"quantity={item_dict['quantity']}, "
                            f"unit_price={item_dict['unit_price']}, "
                            f"discount_percentage={item_dict['discount_percentage']}, "
                            f"gst_rate={item_dict['gst_rate']}")
                
                item = PurchaseVoucherItem(
                    purchase_voucher_id=voucher_id,
                    **item_dict
                )
                db.add(item)
                
                # Calculate totals
                taxable = item.quantity * item.unit_price - item.discount_amount
                cgst = taxable * (item.gst_rate / 200) if item.cgst_amount else 0
                sgst = taxable * (item.gst_rate / 200) if item.sgst_amount else 0
                igst = taxable * (item.gst_rate / 100) if item.igst_amount else 0
                
                total_amount += taxable + cgst + sgst + igst
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
                total_discount += item.discount_amount
                
                # Update stock
                stmt = select(Stock).where(
                    Stock.product_id == item.product_id,
                    Stock.organization_id == org_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                if not stock:
                    stock = Stock(
                        product_id=item.product_id,
                        organization_id=org_id,
                        quantity=0,
                        unit=item.unit
                    )
                    db.add(stock)
                stock.quantity += item.quantity
                
                # If from GRN, update GRN item
                if item.grn_item_id:
                    stmt = select(GoodsReceiptNoteItem).where(
                        GoodsReceiptNoteItem.id == item.grn_item_id
                    )
                    result = await db.execute(stmt)
                    grn_item = result.scalar_one_or_none()
                    if grn_item:
                        grn_item.accepted_quantity = item.quantity
                        db.add(grn_item)
            
            await db.flush()
            
            voucher.total_amount = total_amount
            voucher.cgst_amount = total_cgst
            voucher.sgst_amount = total_sgst
            voucher.igst_amount = total_igst
            voucher.discount_amount = total_discount
        
        logger.debug(f"Before commit for purchase voucher {voucher_id}")
        await db.commit()
        logger.debug(f"After commit for purchase voucher {voucher_id}")
        
        stmt = select(PurchaseVoucher).options(
            joinedload(PurchaseVoucher.vendor),
            joinedload(PurchaseVoucher.purchase_order),
            joinedload(PurchaseVoucher.grn),
            joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
        ).where(
            PurchaseVoucher.id == voucher_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        logger.info(f"Purchase voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating purchase voucher {voucher_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase voucher"
        )

@router.delete("/{voucher_id}")
async def delete_purchase_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    """Delete a purchase voucher"""
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseVoucher).where(
            PurchaseVoucher.id == voucher_id,
            PurchaseVoucher.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        stmt = select(PurchaseVoucherItem).where(
            PurchaseVoucherItem.purchase_voucher_id == voucher_id
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
                stock.quantity -= old_item.quantity
            
            if old_item.grn_item_id:
                stmt = select(GoodsReceiptNoteItem).where(
                    GoodsReceiptNoteItem.id == old_item.grn_item_id
                )
                result = await db.execute(stmt)
                grn_item = result.scalar_one_or_none()
                if grn_item:
                    grn_item.accepted_quantity -= old_item.quantity
                    db.add(grn_item)
        
        from sqlalchemy import delete
        stmt_delete_items = delete(PurchaseVoucherItem).where(PurchaseVoucherItem.purchase_voucher_id == voucher_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(voucher)
        await db.commit()
        
        logger.info(f"Purchase voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase voucher deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase voucher"
        )
    