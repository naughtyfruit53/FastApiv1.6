# app/api/v1/vouchers/purchase_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseVoucher, PurchaseOrder, GoodsReceiptNote, PurchaseOrderItem, GoodsReceiptNoteItem
from app.schemas.vouchers import PurchaseVoucherCreate, PurchaseVoucherInDB, PurchaseVoucherUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase vouchers with enhanced sorting and pagination"""
    query = db.query(PurchaseVoucher).options(joinedload(PurchaseVoucher.vendor)).filter(
        PurchaseVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseVoucher.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(PurchaseVoucher, sortBy):
        sort_attr = getattr(PurchaseVoucher, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(PurchaseVoucher.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available purchase voucher number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PV", current_user.organization_id, PurchaseVoucher
    )

@router.get("/reference-options", response_model=List[dict])
async def get_purchase_voucher_reference_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get available reference document types for purchase vouchers"""
    return [
        {"value": "purchase-order", "label": "Purchase Order", "endpoint": "/purchase-orders"},
        {"value": "grn", "label": "GRN", "endpoint": "/goods-receipt-notes"}
    ]

@router.get("/reference-documents/{ref_type}", response_model=List[dict])
async def get_reference_documents_for_purchase_voucher(
    ref_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get available reference documents of a specific type for purchase vouchers"""
    
    if ref_type == "purchase-order":
        documents = db.query(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
        ).filter(
            PurchaseOrder.organization_id == current_user.organization_id
        ).order_by(PurchaseOrder.created_at.desc()).limit(50).all()
        
        return [
            {
                "id": doc.id,
                "voucher_number": doc.voucher_number,
                "date": doc.date.isoformat() if doc.date else None,
                "total_amount": doc.total_amount,
                "vendor_id": doc.vendor_id,
                "vendor_name": doc.vendor.name if doc.vendor else '',
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product.name if item.product else '',
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "unit": item.unit,
                        "gst_rate": item.gst_rate
                    } for item in doc.items
                ] if hasattr(doc, 'items') and doc.items else []
            } for doc in documents
        ]
    
    elif ref_type == "grn":
        documents = db.query(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.vendor),
            joinedload(GoodsReceiptNote.items).joinedload(GoodsReceiptNoteItem.product)
        ).filter(
            GoodsReceiptNote.organization_id == current_user.organization_id
        ).order_by(GoodsReceiptNote.created_at.desc()).limit(50).all()
        
        return [
            {
                "id": doc.id,
                "voucher_number": doc.voucher_number,
                "date": doc.date.isoformat() if doc.date else None,
                "total_amount": doc.total_amount,
                "vendor_id": doc.vendor_id,
                "vendor_name": doc.vendor.name if doc.vendor else '',
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product.name if item.product else '',
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "unit": item.unit,
                        "gst_rate": item.gst_rate
                    } for item in doc.items
                ] if hasattr(doc, 'items') and doc.items else []
            } for doc in documents
        ]
    
    else:
        raise HTTPException(status_code=400, detail=f"Invalid reference type: {ref_type}")

# Register both "" and "/" for POST to support both /api/v1/purchase-vouchers and /api/v1/purchase-vouchers/
@router.post("", response_model=PurchaseVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseVoucherInDB)
async def create_purchase_voucher(
    invoice: PurchaseVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new purchase voucher"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PV", current_user.organization_id, PurchaseVoucher
            )
        else:
            existing = db.query(PurchaseVoucher).filter(
                PurchaseVoucher.organization_id == current_user.organization_id,
                PurchaseVoucher.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PV", current_user.organization_id, PurchaseVoucher
                )
        
        db_invoice = PurchaseVoucher(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import PurchaseVoucherItem
            item = PurchaseVoucherItem(
                purchase_voucher_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
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
        db.rollback()
        logger.error(f"Error creating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase voucher"
        )

@router.get("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(PurchaseVoucher).options(
        joinedload(PurchaseVoucher.vendor),
        joinedload(PurchaseVoucher.items).joinedload(PurchaseVoucherItem.product)
    ).filter(
        PurchaseVoucher.id == invoice_id,
        PurchaseVoucher.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase voucher not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def update_purchase_voucher(
    invoice_id: int,
    invoice_update: PurchaseVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import PurchaseVoucherItem
            db.query(PurchaseVoucherItem).filter(PurchaseVoucherItem.purchase_voucher_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = PurchaseVoucherItem(
                    purchase_voucher_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Purchase voucher {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase voucher"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_voucher(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        from app.models.vouchers import PurchaseVoucherItem
        db.query(PurchaseVoucherItem).filter(PurchaseVoucherItem.purchase_voucher_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Purchase voucher {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase voucher"
        )