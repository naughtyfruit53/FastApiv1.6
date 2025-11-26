# app/api/v1/vouchers/goods_receipt_note.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser
from app.core.database import get_db
from app.core.enforcement import require_access, TenantEnforcement
from app.api.v1.auth import get_current_active_user
from app.models import User, Stock
from app.models.vouchers.purchase import GoodsReceiptNote, GoodsReceiptNoteItem, PurchaseOrderItem, PurchaseVoucher, PurchaseReturn
from app.schemas.vouchers import GRNCreate, GRNInDB, GRNUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["goods-receipt-notes"])

@router.get("", response_model=List[GRNInDB])
@router.get("/", response_model=List[GRNInDB])
async def get_goods_receipt_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all goods receipt notes"""
    current_user, org_id = auth
    
    stmt = select(GoodsReceiptNote).options(
        joinedload(GoodsReceiptNote.vendor),
        joinedload(GoodsReceiptNote.purchase_order),
        joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
    ).where(
        GoodsReceiptNote.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(GoodsReceiptNote.status == status)
    
    if hasattr(GoodsReceiptNote, sortBy):
        sort_attr = getattr(GoodsReceiptNote, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        stmt = stmt.order_by(GoodsReceiptNote.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    
    for grn in invoices:
        has_rejection = any(item.rejected_quantity > 0 for item in grn.items)
        is_full_rejection = all(item.rejected_quantity == item.received_quantity for item in grn.items if item.received_quantity > 0)
        
        stmt_pv = select(PurchaseVoucher).where(PurchaseVoucher.grn_id == grn.id)
        has_pv = (await db.execute(stmt_pv)).scalar_one_or_none() is not None
        
        stmt_pr = select(PurchaseReturn).where(PurchaseReturn.grn_id == grn.id)
        has_pr = (await db.execute(stmt_pr)).scalar_one_or_none() is not None
        
        logger.debug(f"GRN {grn.voucher_number} - has_rejection: {has_rejection}, is_full_rejection: {is_full_rejection}, has_pv: {has_pv}, has_pr: {has_pr}")
        
        color_status = 'pending'  # Default
        
        if has_pv:
            if not has_rejection:
                color_status = 'green'
            else:
                if not has_pr:
                    color_status = 'yellow'
                else:
                    color_status = 'green'  # Rejection with PR and PV: treat as resolved (green)
        else:  # No PV
            if has_rejection:
                if is_full_rejection:
                    color_status = 'orange' if has_pr else 'red'
                else:
                    color_status = 'blue' if has_pr else 'red'  # Partial rejection no PR: red (consistent with full)
        
        grn.has_purchase_voucher = has_pv
        grn.has_purchase_return = has_pr
        grn.color_status = color_status
        
        # Add debug log for color_status
        logger.debug(f"GRN {grn.voucher_number} - has_rejection: {has_rejection}, is_full_rejection: {is_full_rejection}, has_pv: {has_pv}, has_pr: {has_pr}, color_status: {color_status}")
        
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_goods_receipt_note_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available goods receipt note number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "GRN", org_id, GoodsReceiptNote, voucher_date=date_to_use
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
            db, "GRN", org_id, GoodsReceiptNote, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.get("/for-po/{po_id}", response_model=GRNInDB)
async def get_grn_for_purchase_order(
    po_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the GRN associated with a specific Purchase Order"""
    current_user, org_id = auth
    
    stmt = select(GoodsReceiptNote).options(
        joinedload(GoodsReceiptNote.vendor),
        joinedload(GoodsReceiptNote.purchase_order),
        joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
    ).where(
        GoodsReceiptNote.purchase_order_id == po_id,
        GoodsReceiptNote.organization_id == org_id
    )
    result = await db.execute(stmt)
    grn = result.unique().scalar_one_or_none()
    if not grn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GRN found for this Purchase Order"
        )
    return grn

@router.post("", response_model=GRNInDB, include_in_schema=False)
@router.post("/", response_model=GRNInDB)
async def create_goods_receipt_note(
    invoice: GRNCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new goods receipt note"""
    current_user, org_id = auth
    
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = org_id
        
        # Get the voucher date for numbering
        voucher_date = None
        if 'date' in invoice_data and invoice_data['date']:
            voucher_date = invoice_data['date'] if hasattr(invoice_data['date'], 'year') else None
        elif 'grn_date' in invoice_data and invoice_data['grn_date']:
            voucher_date = invoice_data['grn_date'] if hasattr(invoice_data['grn_date'], 'year') else None
        
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "GRN", org_id, GoodsReceiptNote, voucher_date=voucher_date
            )
        else:
            stmt = select(GoodsReceiptNote).where(
                GoodsReceiptNote.organization_id == org_id,
                GoodsReceiptNote.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "GRN", org_id, GoodsReceiptNote, voucher_date=voucher_date
                )
        
        db_invoice = GoodsReceiptNote(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        total_amount = 0.0
        
        for item_data in invoice.items:
            item_dict = item_data.dict()
            
            if item_dict['accepted_quantity'] + item_dict['rejected_quantity'] > item_dict['received_quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Accepted + Rejected quantities cannot exceed Received quantity for product {item_dict.get('product_id')}"
                )
            if item_dict['received_quantity'] > item_dict['ordered_quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Received quantity cannot exceed Ordered quantity for product {item_dict.get('product_id')}"
                )
            if item_dict['accepted_quantity'] > item_dict['received_quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Accepted quantity cannot exceed Received quantity for product {item_dict.get('product_id')}"
                )
            
            logger.debug(f"Saving GRN item: product_id={item_dict['product_id']}, "
                        f"ordered_quantity={item_dict['ordered_quantity']}, "
                        f"received_quantity={item_dict['received_quantity']}, "
                        f"accepted_quantity={item_dict['accepted_quantity']}, "
                        f"rejected_quantity={item_dict['rejected_quantity']}")
            
            item = GoodsReceiptNoteItem(
                grn_id=db_invoice.id,
                **item_dict
            )
            db.add(item)
            
            total_amount += item.accepted_quantity * item.unit_price
            
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
            stock.quantity += item.accepted_quantity
            
            if item.po_item_id:
                stmt = select(PurchaseOrderItem).where(
                    PurchaseOrderItem.id == item.po_item_id
                )
                result = await db.execute(stmt)
                po_item = result.scalar_one_or_none()
                if po_item:
                    po_item.delivered_quantity += item.accepted_quantity
                    po_item.pending_quantity = max(0, po_item.quantity - po_item.delivered_quantity)
                    db.add(po_item)
        
        db_invoice.total_amount = total_amount
        
        await db.commit()
        
        stmt = select(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.vendor),
            joinedload(GoodsReceiptNote.purchase_order),
            joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
        ).where(GoodsReceiptNote.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalar_one_or_none()
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="goods_receipt_note",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Goods receipt note {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goods receipt note"
        )

@router.get("/{invoice_id}", response_model=GRNInDB)
async def get_goods_receipt_note(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get a specific goods receipt note"""
    current_user, org_id = auth
    
    stmt = select(GoodsReceiptNote).options(
        joinedload(GoodsReceiptNote.vendor),
        joinedload(GoodsReceiptNote.purchase_order),
        joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
    ).where(
        GoodsReceiptNote.id == invoice_id,
        GoodsReceiptNote.organization_id == org_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goods receipt note not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=GRNInDB)
async def update_goods_receipt_note(
    invoice_id: int,
    invoice_update: GRNUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    """Update a goods receipt note"""
    current_user, org_id = auth
    
    try:
        stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            stmt = select(GoodsReceiptNoteItem).where(
                GoodsReceiptNoteItem.grn_id == invoice_id
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
                    stock.quantity -= old_item.accepted_quantity
                
                if old_item.po_item_id:
                    stmt = select(PurchaseOrderItem).where(
                        PurchaseOrderItem.id == old_item.po_item_id
                    )
                    result = await db.execute(stmt)
                    po_item = result.scalar_one_or_none()
                    if po_item:
                        po_item.delivered_quantity -= old_item.accepted_quantity
                        po_item.pending_quantity += old_item.accepted_quantity
                        db.add(po_item)
            
            from sqlalchemy import delete
            stmt_delete = delete(GoodsReceiptNoteItem).where(GoodsReceiptNoteItem.grn_id == invoice_id)
            await db.execute(stmt_delete)
            await db.flush()
            
            total_amount = 0.0
            
            for item_data in invoice_update.items:
                item_dict = item_data.dict()
                
                if item_dict['accepted_quantity'] + item_dict['rejected_quantity'] > item_dict['received_quantity']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Accepted + Rejected quantities cannot exceed Received quantity for product {item_dict.get('product_id')}"
                    )
                if item_dict['received_quantity'] > item_dict['ordered_quantity']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Received quantity cannot exceed Ordered quantity for product {item_dict.get('product_id')}"
                    )
                if item_dict['accepted_quantity'] > item_dict['received_quantity']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Accepted quantity cannot exceed Received quantity for product {item_dict.get('product_id')}"
                    )
                
                logger.debug(f"Updating GRN item: product_id={item_dict['product_id']}, "
                            f"ordered_quantity={item_dict['ordered_quantity']}, "
                            f"received_quantity={item_dict['received_quantity']}, "
                            f"accepted_quantity={item_dict['accepted_quantity']}, "
                            f"rejected_quantity={item_dict['rejected_quantity']}")
                
                item = GoodsReceiptNoteItem(
                    grn_id=invoice_id,
                    **item_dict
                )
                db.add(item)
                
                total_amount += item.accepted_quantity * item.unit_price
                
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
                stock.quantity += item.accepted_quantity
                
                if item.po_item_id:
                    stmt = select(PurchaseOrderItem).where(
                        PurchaseOrderItem.id == item.po_item_id
                    )
                    result = await db.execute(stmt)
                    po_item = result.scalar_one_or_none()
                    if po_item:
                        po_item.delivered_quantity += item.accepted_quantity
                        po_item.pending_quantity = max(0, po_item.quantity - po_item.delivered_quantity)
                        db.add(po_item)
            
            await db.flush()
            
            invoice.total_amount = total_amount
        
        logger.debug(f"Before commit for goods receipt note {invoice_id}")
        await db.commit()
        logger.debug(f"After commit for goods receipt note {invoice_id}")
        
        stmt = select(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.vendor),
            joinedload(GoodsReceiptNote.purchase_order),
            joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
        ).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        logger.info(f"Goods receipt note {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating goods receipt note {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goods receipt note"
        )

@router.delete("/{invoice_id}")
async def delete_goods_receipt_note(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    """Delete a goods receipt note"""
    current_user, org_id = auth
    
    try:
        stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        stmt = select(GoodsReceiptNoteItem).where(
            GoodsReceiptNoteItem.grn_id == invoice_id
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
                stock.quantity -= old_item.accepted_quantity
            
            if old_item.po_item_id:
                stmt = select(PurchaseOrderItem).where(
                    PurchaseOrderItem.id == old_item.po_item_id
                )
                result = await db.execute(stmt)
                po_item = result.scalar_one_or_none()
                if po_item:
                    po_item.delivered_quantity -= old_item.accepted_quantity
                    po_item.pending_quantity += old_item.accepted_quantity
                    db.add(po_item)
        
        from sqlalchemy import delete
        stmt_delete_items = delete(GoodsReceiptNoteItem).where(GoodsReceiptNoteItem.grn_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Goods receipt note {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Goods receipt note deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goods receipt note"
        )