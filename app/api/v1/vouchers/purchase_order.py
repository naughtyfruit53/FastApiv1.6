# app/api/v1/vouchers/purchase_order.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from io import BytesIO
from app.core.database import get_db
from app.core.enforcement import require_access
from app.api.v1.auth import get_current_active_user
from app.models import User, Product
from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem
from app.schemas.vouchers.purchase import PurchaseOrderCreate, PurchaseOrderInDB, PurchaseOrderUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging
from datetime import timezone, datetime
from dateutil import parser as date_parser
import re
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])

@router.get("", response_model=List[PurchaseOrderInDB])
@router.get("/", response_model=List[PurchaseOrderInDB])
async def get_purchase_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=99999, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get all purchase orders with GRN completion status for color coding"""
    current_user, org_id = auth
    
    stmt = select(PurchaseOrder).options(
        joinedload(PurchaseOrder.vendor),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).where(
        PurchaseOrder.organization_id == org_id
    )
    
    if status:
        stmt = stmt.where(PurchaseOrder.status == status)
    
    if hasattr(PurchaseOrder, sortBy):
        sort_attr = getattr(PurchaseOrder, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        stmt = stmt.order_by(PurchaseOrder.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    purchase_orders = result.unique().scalars().all()
    
    for po in purchase_orders:
        grn_stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.purchase_order_id == po.id,
            GoodsReceiptNote.organization_id == org_id
        )
        grn_result = await db.execute(grn_stmt)
        grns = grn_result.scalars().all()
        
        total_ordered_quantity = 0.0
        total_pending_quantity = 0.0
        total_received_quantity = 0.0
        
        if po.items:
            for item in po.items:
                total_ordered_quantity += item.quantity
                total_pending_quantity += item.pending_quantity
                # Use delivered_quantity from PO items for accurate tracking
                total_received_quantity += (item.delivered_quantity or 0)
        
        remaining_quantity = total_ordered_quantity - total_received_quantity
        
        logger.debug(f"PO {po.voucher_number}: "
                    f"ordered={total_ordered_quantity}, "
                    f"received={total_received_quantity}, "
                    f"pending={total_pending_quantity}, "
                    f"remaining={remaining_quantity}, "
                    f"grns_exist={bool(grns)}")
        
        # Fix color-coding: green only when fully received, yellow for partial
        if remaining_quantity <= 0 and grns:
            po.grn_status = "complete"
        elif grns and total_received_quantity > 0:
            po.grn_status = "partial"
        else:
            po.grn_status = "pending"
        
        logger.debug(f"PO {po.voucher_number} assigned grn_status: {po.grn_status}")
    
    return purchase_orders

@router.get("/next-number", response_model=str)
async def get_next_purchase_order_number(
    voucher_date: Optional[str] = Query(None, description="Optional voucher date (ISO format) to generate number for specific period"),
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    """Get the next available purchase order number for a given date"""
    current_user, org_id = auth
    
    # Parse the voucher_date if provided
    date_to_use = None
    if voucher_date:
        try:
            date_to_use = date_parser.parse(voucher_date)
        except Exception:
            pass
    
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PO", org_id, PurchaseOrder, voucher_date=date_to_use
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
            db, "PO", org_id, PurchaseOrder, parsed_date
        )
        return conflict_info
    except Exception as e:
        logger.error(f"Error checking backdated conflict: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")


@router.post("", response_model=PurchaseOrderInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseOrderInDB)
async def create_purchase_order(
    invoice: PurchaseOrderCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "create"))
):
    """Create new purchase order"""
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
        if 'delivery_date' in invoice_data and invoice_data['delivery_date']:
            invoice_data['delivery_date'] = invoice_data['delivery_date'].replace(tzinfo=timezone.utc)
        
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            # Generate voucher number based on the entered date
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PO", org_id, PurchaseOrder, voucher_date=voucher_date
            )
        else:
            stmt = select(PurchaseOrder).where(
                PurchaseOrder.organization_id == org_id,
                PurchaseOrder.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "PO", org_id, PurchaseOrder, voucher_date=voucher_date
                )
        
        product_ids = [item.product_id for item in invoice.items]
        stmt = select(Product).where(
            Product.id.in_(product_ids),
            Product.organization_id == org_id
        )
        result = await db.execute(stmt)
        products = result.scalars().all()
        product_dict = {p.id: p for p in products}
        
        for item in invoice.items:
            product = product_dict.get(item.product_id)
            if not product or not product.product_name or product.product_name.strip() == '':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product ID {item.product_id} has no valid name"
                )
        
        db_invoice = PurchaseOrder(**invoice_data)
        db.add(db_invoice)
        await db.flush()
        
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        for item_data in invoice.items:
            item_dict = item_data.dict()
            
            item_dict.setdefault('discount_percentage', 0.0)
            item_dict.setdefault('discount_amount', 0.0)
            item_dict.setdefault('taxable_amount', 0.0)
            item_dict.setdefault('gst_rate', 18.0)
            item_dict.setdefault('cgst_amount', 0.0)
            item_dict.setdefault('sgst_amount', 0.0)
            item_dict.setdefault('igst_amount', 0.0)
            item_dict.setdefault('description', None)
            
            if item_dict['taxable_amount'] == 0:
                gross_amount = item_dict['quantity'] * item_dict['unit_price']
                discount_amount = gross_amount * (item_dict['discount_percentage'] / 100) if item_dict['discount_percentage'] else item_dict['discount_amount']
                item_dict['discount_amount'] = discount_amount
                item_dict['taxable_amount'] = gross_amount - discount_amount
            
            taxable = item_dict['taxable_amount']
            if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                half_rate = item_dict['gst_rate'] / 2 / 100
                item_dict['cgst_amount'] = taxable * half_rate
                item_dict['sgst_amount'] = taxable * half_rate
                item_dict['igst_amount'] = 0.0
            
            item_dict['total_amount'] = (
                item_dict['taxable_amount'] +
                item_dict['cgst_amount'] +
                item_dict['sgst_amount'] +
                item_dict['igst_amount']
            )
            
            item_dict['discounted_price'] = item_dict['unit_price'] - (item_dict['discount_amount'] / item_dict['quantity']) if item_dict['quantity'] > 0 else item_dict['unit_price']
            
            item = PurchaseOrderItem(
                purchase_order_id=db_invoice.id,
                delivered_quantity=0.0,
                pending_quantity=item_dict['quantity'],
                **item_dict
            )
            db.add(item)
            
            total_amount += item_dict['total_amount']
            total_cgst += item_dict['cgst_amount']
            total_sgst += item_dict['sgst_amount']
            total_igst += item_dict['igst_amount']
            total_discount += item_dict['discount_amount']
        
        db_invoice.total_amount = total_amount
        db_invoice.cgst_amount = total_cgst
        db_invoice.sgst_amount = total_sgst
        db_invoice.igst_amount = total_igst
        db_invoice.discount_amount = total_discount
        
        await db.commit()
        
        stmt = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).where(PurchaseOrder.id == db_invoice.id)
        result = await db.execute(stmt)
        db_invoice = result.unique().scalar_one_or_none()
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_order",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Purchase order {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase order"
        )

@router.get("/{invoice_id}", response_model=PurchaseOrderInDB)
async def get_purchase_order(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    stmt = select(PurchaseOrder).options(
        joinedload(PurchaseOrder.vendor),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).where(
        PurchaseOrder.id == invoice_id,
        PurchaseOrder.organization_id == org_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    grn_stmt = select(GoodsReceiptNote).where(
        GoodsReceiptNote.purchase_order_id == invoice.id,
        GoodsReceiptNote.organization_id == org_id
    )
    grn_result = await db.execute(grn_stmt)
    grns = grn_result.scalars().all()
    
    total_ordered_quantity = 0.0
    total_pending_quantity = 0.0
    total_received_quantity = 0.0
    
    if invoice.items:
        for item in invoice.items:
            total_ordered_quantity += item.quantity
            total_pending_quantity += item.pending_quantity
    
    if grns:
        grn_items_stmt = select(GoodsReceiptNoteItem).where(
            GoodsReceiptNoteItem.grn_id.in_([grn.id for grn in grns])
        )
        grn_items_result = await db.execute(grn_items_stmt)
        grn_items = grn_items_result.scalars().all()
        total_received_quantity = sum(item.accepted_quantity for item in grn_items)
    
    remaining_quantity = total_ordered_quantity - total_received_quantity
    
    logger.debug(f"PO {invoice.voucher_number}: "
                f"ordered={total_ordered_quantity}, "
                f"received={total_received_quantity}, "
                f"pending={total_pending_quantity}, "
                f"remaining={remaining_quantity}, "
                f"grns_exist={bool(grns)}, "
                f"items={[{ 'id': item.id, 'product_id': item.product_id, 'product_name': item.product.product_name if item.product else None } for item in invoice.items]}")
    
    if grns and remaining_quantity <= 0:
        invoice.grn_status = "complete"
    elif grns:
        invoice.grn_status = "partial"
    else:
        invoice.grn_status = "pending"
    
    logger.debug(f"PO {invoice.voucher_number} assigned grn_status: {invoice.grn_status}")
    
    return invoice

@router.get("/{invoice_id}/pdf")
async def generate_purchase_order_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="purchase_orders",
            voucher_data=voucher.__dict__,
            db=db,
            organization_id=org_id,
            current_user=current_user
        )
        
        safe_filename = re.sub(r'[/\\:?"<>|]', '-', voucher.voucher_number) + '.pdf'
        
        headers = {
            'Content-Disposition': f'attachment; filename="{safe_filename}"'
        }
        
        return StreamingResponse(pdf_content, media_type='application/pdf', headers=headers)
        
    except Exception as e:
        logger.error(f"Error generating PDF for purchase order {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.put("/{invoice_id}", response_model=PurchaseOrderInDB)
async def update_purchase_order(
    invoice_id: int,
    invoice_update: PurchaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        
        if 'date' in update_data and update_data['date']:
            update_data['date'] = update_data['date'].replace(tzinfo=timezone.utc)
        if 'delivery_date' in update_data and update_data['delivery_date']:
            update_data['delivery_date'] = update_data['delivery_date'].replace(tzinfo=timezone.utc)
        
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_discount = 0.0
        
        if invoice_update.items is not None:
            product_ids = [item.product_id for item in invoice_update.items]
            stmt = select(Product).where(
                Product.id.in_(product_ids),
                Product.organization_id == org_id
            )
            result = await db.execute(stmt)
            products = result.scalars().all()
            product_dict = {p.id: p for p in products}
            
            for item in invoice_update.items:
                product = product_dict.get(item.product_id)
                if not product or not product.product_name or product.product_name.strip() == '':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product ID {item.product_id} has no valid name"
                    )
            
            from sqlalchemy import delete
            stmt_delete = delete(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == invoice_id)
            await db.execute(stmt_delete)
            for item_data in invoice_update.items:
                item_dict = item_data.dict()
                
                item_dict.setdefault('discount_percentage', 0.0)
                item_dict.setdefault('discount_amount', 0.0)
                item_dict.setdefault('taxable_amount', 0.0)
                item_dict.setdefault('gst_rate', 18.0)
                item_dict.setdefault('cgst_amount', 0.0)
                item_dict.setdefault('sgst_amount', 0.0)
                item_dict.setdefault('igst_amount', 0.0)
                item_dict.setdefault('description', None)
                
                if item_dict['taxable_amount'] == 0:
                    gross_amount = item_dict['quantity'] * item_dict['unit_price']
                    discount_amount = gross_amount * (item_dict['discount_percentage'] / 100) if item_dict['discount_percentage'] else item_dict['discount_amount']
                    item_dict['discount_amount'] = discount_amount
                    item_dict['taxable_amount'] = gross_amount - discount_amount
                
                taxable = item_dict['taxable_amount']
                if item_dict['cgst_amount'] == 0 and item_dict['sgst_amount'] == 0 and item_dict['igst_amount'] == 0:
                    half_rate = item_dict['gst_rate'] / 2 / 100
                    item_dict['cgst_amount'] = taxable * half_rate
                    item_dict['sgst_amount'] = taxable * half_rate
                    item_dict['igst_amount'] = 0.0
                
                item_dict['total_amount'] = (
                    item_dict['taxable_amount'] +
                    item_dict['cgst_amount'] +
                    item_dict['sgst_amount'] +
                    item_dict['igst_amount']
                )
                
                item_dict['discounted_price'] = item_dict['unit_price'] - (item_dict['discount_amount'] / item_dict['quantity']) if item_dict['quantity'] > 0 else item_dict['unit_price']
                
                item = PurchaseOrderItem(
                    purchase_order_id=invoice_id,
                    delivered_quantity=0.0,
                    pending_quantity=item_dict['quantity'],
                    **item_dict
                )
                db.add(item)
                
                total_amount += item_dict['total_amount']
                total_cgst += item_dict['cgst_amount']
                total_sgst += item_dict['sgst_amount']
                total_igst += item_dict['igst_amount']
                total_discount += item_dict['discount_amount']
            
            invoice.total_amount = total_amount
            invoice.cgst_amount = total_cgst
            invoice.sgst_amount = total_sgst
            invoice.igst_amount = total_igst
            invoice.discount_amount = total_discount
        
        await db.commit()
        
        stmt = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.unique().scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        logger.info(f"Purchase order {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase order"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_order(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "delete"))
):
    """Delete purchase order"""
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        from sqlalchemy import delete
        stmt_delete_items = delete(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == invoice_id)
        await db.execute(stmt_delete_items)
        
        await db.delete(invoice)
        await db.commit()
        
        logger.info(f"Purchase order {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase order deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase order"
        )

@router.put("/{invoice_id}/tracking")
async def update_purchase_order_tracking(
    invoice_id: int,
    transporter_name: Optional[str] = None,
    tracking_number: Optional[str] = None,
    tracking_link: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "update"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        po = result.scalar_one_or_none()
        
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        if transporter_name is not None:
            po.transporter_name = transporter_name
        if tracking_number is not None:
            po.tracking_number = tracking_number
        if tracking_link is not None:
            po.tracking_link = tracking_link
        
        await db.commit()
        await db.refresh(po)
        
        logger.info(f"Tracking details updated for PO {po.voucher_number} by {current_user.email}")
        return {
            "message": "Tracking details updated successfully",
            "transporter_name": po.transporter_name,
            "tracking_number": po.tracking_number,
            "tracking_link": po.tracking_link
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
async def get_purchase_order_tracking(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == org_id
        )
        result = await db.execute(stmt)
        po = result.scalar_one_or_none()
        
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        return {
            "transporter_name": po.transporter_name,
            "tracking_number": po.tracking_number,
            "tracking_link": po.tracking_link
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tracking details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tracking details"
        )

@router.get("/product/{product_id}/previous-discount")
async def get_previous_discount(
    product_id: int,
    vendor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    auth: tuple = Depends(require_access("voucher", "read"))
):
    current_user, org_id = auth
    
    try:
        stmt = select(PurchaseOrderItem).join(PurchaseOrder).where(
            PurchaseOrderItem.product_id == product_id,
            PurchaseOrder.organization_id == org_id
        ).order_by(PurchaseOrder.date.desc())
        
        if vendor_id:
            stmt = stmt.where(PurchaseOrder.vendor_id == vendor_id)
        
        result = await db.execute(stmt.limit(1))
        last_item = result.scalar_one_or_none()
        
        if not last_item:
            return {"discount_percentage": 0.0, "discount_amount": 0.0}
        
        return {
            "discount_percentage": last_item.discount_percentage,
            "discount_amount": last_item.discount_amount
        }
        
    except Exception as e:
        logger.error(f"Error fetching previous discount: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch previous discount")