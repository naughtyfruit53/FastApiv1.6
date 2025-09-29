# app/api/v1/vouchers/goods_receipt_note.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User, Stock
from app.models.vouchers.purchase import GoodsReceiptNote, GoodsReceiptNoteItem, PurchaseOrderItem
from app.schemas.vouchers import GRNCreate, GRNInDB, GRNUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["goods-receipt-notes"])

@router.get("", response_model=List[GRNInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[GRNInDB])
async def get_goods_receipt_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all goods receipt notes"""
    stmt = select(GoodsReceiptNote).options(
        joinedload(GoodsReceiptNote.vendor),
        joinedload(GoodsReceiptNote.purchase_order),
        joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
    ).where(
        GoodsReceiptNote.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(GoodsReceiptNote.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(GoodsReceiptNote, sortBy):
        sort_attr = getattr(GoodsReceiptNote, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(GoodsReceiptNote.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    invoices = result.unique().scalars().all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_goods_receipt_note_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available goods receipt note number"""
    return await VoucherNumberService.generate_voucher_number(
        db, "GRN", current_user.organization_id, GoodsReceiptNote
    )

# Register both "" and "/" for POST to support both /api/v1/goods-receipt-notes and /api/v1/goods-receipt-notes/
@router.post("", response_model=GRNInDB, include_in_schema=False)
@router.post("/", response_model=GRNInDB)
async def create_goods_receipt_note(
    invoice: GRNCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new goods receipt note"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                db, "GRN", current_user.organization_id, GoodsReceiptNote
            )
        else:
            stmt = select(GoodsReceiptNote).where(
                GoodsReceiptNote.organization_id == current_user.organization_id,
                GoodsReceiptNote.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number(
                    db, "GRN", current_user.organization_id, GoodsReceiptNote
                )
        
        db_invoice = GoodsReceiptNote(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        total_amount = 0.0
        
        for item_data in invoice.items:
            item_dict = item_data.dict()
            
            # Validate quantities
            if item_dict['accepted_quantity'] + item_dict['rejected_quantity'] > item_dict['received_quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Accepted + Rejected quantities cannot exceed Received quantity for product {item_dict.get('product_id')}"
                )
            
            item = GoodsReceiptNoteItem(
                grn_id=db_invoice.id,
                **item_dict
            )
            db.add(item)
            
            total_amount += item.accepted_quantity * item.unit_price
            
            # Update stock
            stmt = select(Stock).where(
                Stock.product_id == item.product_id,
                Stock.organization_id == current_user.organization_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            if not stock:
                stock = Stock(
                    product_id=item.product_id,
                    organization_id=current_user.organization_id,
                    quantity=0,
                    unit=item.unit
                )
                db.add(stock)
            stock.quantity += item.accepted_quantity
            
            # Update PO item if po_item_id provided
            if item.po_item_id:
                stmt = select(PurchaseOrderItem).where(
                    PurchaseOrderItem.id == item.po_item_id
                )
                result = await db.execute(stmt)
                po_item = result.scalar_one_or_none()
                if po_item:
                    po_item.delivered_quantity += item.accepted_quantity
                    po_item.pending_quantity = max(0, po_item.pending_quantity - item.accepted_quantity)
                    db.add(po_item)
        
        db_invoice.total_amount = total_amount
        
        await db.commit()
        
        # Re-query with joins to load relationships
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
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(GoodsReceiptNote).options(
        joinedload(GoodsReceiptNote.vendor),
        joinedload(GoodsReceiptNote.purchase_order),
        joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
    ).where(
        GoodsReceiptNote.id == invoice_id,
        GoodsReceiptNote.organization_id == current_user.organization_id
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
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
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
            # Fetch old items to revert stock and PO updates
            stmt = select(GoodsReceiptNoteItem).where(
                GoodsReceiptNoteItem.grn_id == invoice_id
            )
            result = await db.execute(stmt)
            old_items = result.scalars().all()
            
            for old_item in old_items:
                # Revert stock
                stmt = select(Stock).where(
                    Stock.product_id == old_item.product_id,
                    Stock.organization_id == current_user.organization_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                if stock:
                    stock.quantity -= old_item.accepted_quantity
                
                # Revert PO item if po_item_id
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
            await db.flush()  # Flush deletes before adding new items
            
            total_amount = 0.0
            
            for item_data in invoice_update.items:
                item_dict = item_data.dict()
                
                # Validate quantities
                if item_dict['accepted_quantity'] + item_dict['rejected_quantity'] > item_dict['received_quantity']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Accepted + Rejected quantities cannot exceed Received quantity for product {item_dict.get('product_id')}"
                    )
                
                item = GoodsReceiptNoteItem(
                    grn_id=invoice_id,
                    **item_dict
                )
                db.add(item)
                
                total_amount += item.accepted_quantity * item.unit_price
                
                # Update stock
                stmt = select(Stock).where(
                    Stock.product_id == item.product_id,
                    Stock.organization_id == current_user.organization_id
                )
                result = await db.execute(stmt)
                stock = result.scalar_one_or_none()
                if not stock:
                    stock = Stock(
                        product_id=item.product_id,
                        organization_id=current_user.organization_id,
                        quantity=0,
                        unit=item.unit
                    )
                    db.add(stock)
                stock.quantity += item.accepted_quantity
                
                # Update PO item if po_item_id
                if item.po_item_id:
                    stmt = select(PurchaseOrderItem).where(
                        PurchaseOrderItem.id == item.po_item_id
                    )
                    result = await db.execute(stmt)
                    po_item = result.scalar_one_or_none()
                    if po_item:
                        po_item.delivered_quantity += item.accepted_quantity
                        po_item.pending_quantity = max(0, po_item.pending_quantity - item.accepted_quantity)
                        db.add(po_item)
            
            await db.flush()  # Flush adds before commit
            
            invoice.total_amount = total_amount
        
        logger.debug(f"Before commit for goods receipt note {invoice_id}")
        await db.commit()
        logger.debug(f"After commit for goods receipt note {invoice_id}")
        
        # Re-query with joins to load relationships
        stmt = select(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.vendor),
            joinedload(GoodsReceiptNote.purchase_order),
            joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
        ).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
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
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
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
            # Revert stock
            stmt = select(Stock).where(
                Stock.product_id == old_item.product_id,
                Stock.organization_id == current_user.organization_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock:
                stock.quantity -= old_item.accepted_quantity
            
            # Revert PO item if po_item_id
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