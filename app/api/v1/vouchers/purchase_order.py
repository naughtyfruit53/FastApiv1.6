# app/api/v1/vouchers/purchase_order.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from io import BytesIO
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem
from app.schemas.vouchers import PurchaseOrderCreate, PurchaseOrderInDB, PurchaseOrderUpdate
from app.services.system_email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
from app.services.pdf_generation_service import pdf_generator
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-orders"])

@router.get("", response_model=List[PurchaseOrderInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PurchaseOrderInDB])
async def get_purchase_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=99999, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc' (default 'desc' for latest first)"),
    sortBy: str = Query("created_at", description="Field to sort by (default 'created_at')"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase orders with GRN completion status for color coding"""
    from app.models.vouchers.purchase import GoodsReceiptNote
    
    stmt = select(PurchaseOrder).options(
        joinedload(PurchaseOrder.vendor),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).where(
        PurchaseOrder.organization_id == current_user.organization_id
    )
    
    if status:
        stmt = stmt.where(PurchaseOrder.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseOrder, sortBy):
        sort_attr = getattr(PurchaseOrder, sortBy)
        if sort.lower() == "asc":
            stmt = stmt.order_by(sort_attr.asc())
        else:
            stmt = stmt.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        stmt = stmt.order_by(PurchaseOrder.created_at.desc())
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    purchase_orders = result.unique().scalars().all()
    
    # Add GRN completion status and color coding to each PO
    for po in purchase_orders:
        # Check if any GRN exists for this PO
        grn_stmt = select(GoodsReceiptNote).where(
            GoodsReceiptNote.purchase_order_id == po.id
        )
        grn_result = await db.execute(grn_stmt)
        grns = grn_result.scalars().all()
        
        # Compute GRN status based on pending quantities
        # Check if all items are fully received
        all_items_received = True
        has_pending_items = False
        if po.items:
            for item in po.items:
                if item.pending_quantity > 0:
                    all_items_received = False
                    has_pending_items = True
                    break
        
        # Set grn_status attribute (not persisted, just for API response)
        if all_items_received and grns:
            po.grn_status = "complete"
        elif grns:
            po.grn_status = "partial"
        else:
            po.grn_status = "pending"
        
        # Set color_status for UI highlighting
        # Red: no tracking details and GRN pending
        # Yellow: has tracking but GRN still pending
        # Green: GRN complete (all items received)
        has_tracking = bool(po.tracking_number or po.transporter_name)
        
        if all_items_received:
            po.color_status = "green"
        elif has_tracking:
            po.color_status = "yellow"
        else:
            po.color_status = "red"
    
    return purchase_orders

@router.get("/next-number", response_model=str)
async def get_next_purchase_order_number(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available purchase order number"""
    return await VoucherNumberService.generate_voucher_number_async(
        db, "PO", current_user.organization_id, PurchaseOrder
    )

# Register both "" and "/" for POST to support both /api/v1/purchase-orders and /api/v1/purchase-orders/
@router.post("", response_model=PurchaseOrderInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseOrderInDB)
async def create_purchase_order(
    invoice: PurchaseOrderCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new purchase order"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                db, "PO", current_user.organization_id, PurchaseOrder
            )
        else:
            stmt = select(PurchaseOrder).where(
                PurchaseOrder.organization_id == current_user.organization_id,
                PurchaseOrder.voucher_number == invoice_data['voucher_number']
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                invoice_data['voucher_number'] = await VoucherNumberService.generate_voucher_number_async(
                    db, "PO", current_user.organization_id, PurchaseOrder
                )
        
        db_invoice = PurchaseOrder(**invoice_data)
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
            
            item = PurchaseOrderItem(
                purchase_order_id=db_invoice.id,
                delivered_quantity=0.0,
                pending_quantity=item_dict['quantity'],  # Set pending_quantity to quantity
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
    current_user: User = Depends(get_current_active_user)
):
    stmt = select(PurchaseOrder).options(
        joinedload(PurchaseOrder.vendor),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).where(
        PurchaseOrder.id == invoice_id,
        PurchaseOrder.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return invoice

@router.get("/{invoice_id}/pdf")
async def generate_purchase_order_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        voucher = result.unique().scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        pdf_content = await pdf_generator.generate_voucher_pdf(
            voucher_type="purchase_order",
            voucher_data=voucher.__dict__,
            db=db,
            organization_id=current_user.organization_id,
            current_user=current_user
        )
        
        headers = {
            'Content-Disposition': f'attachment; filename="purchase_order_{voucher.voucher_number}.pdf"'
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
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
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
            stmt_delete = delete(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == invoice_id)
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
                
                item = PurchaseOrderItem(
                    purchase_order_id=invoice_id,
                    delivered_quantity=0.0,
                    pending_quantity=item_dict['quantity'],  # Set pending_quantity to quantity
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
        stmt = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
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
    current_user: User = Depends(get_current_active_user)
):
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
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
    current_user: User = Depends(get_current_active_user)
):
    """Update tracking details for a purchase order"""
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        po = result.scalar_one_or_none()
        
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        # Update tracking fields
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
    current_user: User = Depends(get_current_active_user)
):
    """Get tracking details for a purchase order"""
    try:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.id == invoice_id,
            PurchaseOrder.organization_id == current_user.organization_id
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