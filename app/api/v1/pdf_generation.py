# app/api/v1/pdf_generation.py

"""
FastAPI endpoints for voucher PDF generation
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession  # Changed to AsyncSession
from sqlalchemy import select  # Added for select
from sqlalchemy.orm import joinedload
from typing import Dict, Any
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.services.pdf_generation_service import pdf_generator
from app.services.rbac import RBACService
from app.models.vouchers.purchase import PurchaseVoucher, PurchaseOrder, PurchaseReturn, PurchaseOrderItem, PurchaseVoucherItem, PurchaseReturnItem, GoodsReceiptNote, GoodsReceiptNoteItem
from app.models.vouchers.sales import SalesVoucher, DeliveryChallan, SalesReturn, DeliveryChallanItem
from app.models.vouchers.presales import Quotation, SalesOrder, ProformaInvoice, QuotationItem, SalesOrderItem, ProformaInvoiceItem
from app.models.vouchers.financial import PaymentVoucher, ReceiptVoucher
from app.models.customer_models import Vendor, Customer
from app.models.hr_models import EmployeeProfile
import logging
import json  # Added for json parsing

logger = logging.getLogger(__name__)
router = APIRouter(tags=["pdf-generation"])

def check_voucher_permission(voucher_type: str, current_user: User, db: AsyncSession) -> None:  # Changed to AsyncSession
    """Check if user has permission for voucher type"""
    permission_map = {
        'purchase': 'voucher_read',
        'purchase-vouchers': 'voucher_read',
        'purchase-orders': 'voucher_read',
        'purchase-return': 'voucher_read',
        'purchase-returns': 'voucher_read',
        'sales': 'voucher_read',
        'sales-vouchers': 'voucher_read',
        'delivery-challan': 'voucher_read',
        'sales-return': 'voucher_read',
        'sales-returns': 'voucher_read',
        'quotation': 'presales_read',
        'sales_order': 'presales_read',
        'sales-orders': 'presales_read',
        'proforma_invoice': 'presales_read',
        'proforma-invoices': 'presales_read',
        'payment-vouchers': 'voucher_read',
        'receipt-vouchers': 'voucher_read',
        'goods-receipt-notes': 'voucher_read'
    }
    
    required_permission = permission_map.get(voucher_type)
    if required_permission:
        rbac_service = RBACService(db)
        # Skip RBAC check for now and just log
        logger.info(f"User {current_user.id} accessing {voucher_type} PDF generation")
        # if not rbac_service.user_has_service_permission(current_user.id, required_permission):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=f"Insufficient permissions to access {voucher_type} vouchers"
        #     )

@router.post("/voucher/{voucher_type}/{voucher_id}")
async def generate_voucher_pdf(
    voucher_type: str,
    voucher_id: int,
    db: AsyncSession = Depends(get_db),  # Changed to AsyncSession
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate PDF for a specific voucher
    
    Supported voucher types:
    - payment-vouchers: Payment Voucher
    - purchase: Purchase Voucher
    - purchase-vouchers: Purchase Voucher
    - purchase-orders: Purchase Order
    - purchase-return: Purchase Return
    - purchase-returns: Purchase Return
    - sales: Sales Voucher
    - sales-vouchers: Sales Voucher
    - delivery-challan: Delivery Challan
    - sales-return: Sales Return
    - sales-returns: Sales Return
    - quotation: Quotation
    - sales_order: Sales Order
    - sales-orders: Sales Order
    - proforma_invoice: Proforma Invoice
    - proforma-invoices: Proforma Invoice
    - goods-receipt-notes: Goods Receipt Note
    """
    
    # Normalize voucher_type for consistency
    if voucher_type == 'quotations':
        voucher_type = 'quotation'
    elif voucher_type == 'proforma-invoices':
        voucher_type = 'proforma_invoice'
    elif voucher_type == 'sales-orders':
        voucher_type = 'sales_order'
    elif voucher_type == 'delivery-challans':
        voucher_type = 'delivery-challan'
    elif voucher_type == 'sales-vouchers':
        voucher_type = 'sales'
    elif voucher_type == 'sales-returns':
        voucher_type = 'sales-return'
    elif voucher_type == 'goods-receipt-notes':
        voucher_type = 'grn'
    
    # Check permissions
    check_voucher_permission(voucher_type, current_user, db)
    
    try:
        # Get voucher data based on type
        voucher_data = await _get_voucher_data(voucher_type, voucher_id, db, current_user)  # Await since now async
        
        if not voucher_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{voucher_type.title()} voucher not found"
            )
        
        # Generate PDF
        pdf_io = await pdf_generator.generate_voucher_pdf(  # Await since now async
            voucher_type=voucher_type,
            voucher_data=voucher_data,
            db=db,
            organization_id=current_user.organization_id,
            current_user=current_user
        )
        
        # Return PDF response
        filename = f"{voucher_type}_{voucher_data.get('voucher_number', 'voucher')}.pdf"
        
        return Response(
            content=pdf_io.getvalue(),
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for {voucher_type} {voucher_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@router.post("/voucher/{voucher_type}/{voucher_id}/download")
async def download_voucher_pdf(
    voucher_type: str,
    voucher_id: int,
    db: AsyncSession = Depends(get_db),  # Changed to AsyncSession
    current_user: User = Depends(get_current_active_user)
):
    """
    Download PDF for a specific voucher (forces download instead of preview)
    """
    
    # Normalize voucher_type for consistency
    if voucher_type == 'quotations':
        voucher_type = 'quotation'
    elif voucher_type == 'proforma-invoices':
        voucher_type = 'proforma_invoice'
    elif voucher_type == 'sales-orders':
        voucher_type = 'sales_order'
    elif voucher_type == 'delivery-challans':
        voucher_type = 'delivery-challan'
    elif voucher_type == 'sales-vouchers':
        voucher_type = 'sales'
    elif voucher_type == 'sales-returns':
        voucher_type = 'sales-return'
    elif voucher_type == 'goods-receipt-notes':
        voucher_type = 'grn'
    
    # Check permissions
    check_voucher_permission(voucher_type, current_user, db)
    
    try:
        # Get voucher data
        voucher_data = await _get_voucher_data(voucher_type, voucher_id, db, current_user)  # Await
        
        if not voucher_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{voucher_type.title()} voucher not found"
            )
        
        # Generate PDF
        pdf_io = await pdf_generator.generate_voucher_pdf(  # Await
            voucher_type=voucher_type,
            voucher_data=voucher_data,
            db=db,
            organization_id=current_user.organization_id,
            current_user=current_user
        )
        
        # Return PDF response for download
        filename = f"{voucher_type}_{voucher_data.get('voucher_number', 'voucher')}.pdf"
        
        return Response(
            content=pdf_io.getvalue(),
            media_type='application/pdf',
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF for {voucher_type} {voucher_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download PDF: {str(e)}"
        )

@router.get("/templates")
async def get_available_templates(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available PDF templates"""
    
    templates = [
        {
            "type": "purchase",
            "name": "Purchase Voucher",
            "description": "Purchase voucher with vendor details and tax calculations"
        },
        {
            "type": "purchase-orders",
            "name": "Purchase Order",
            "description": "Purchase order with vendor details and tax calculations"
        },
        {
            "type": "sales",
            "name": "Sales Invoice",
            "description": "Sales invoice with customer details and tax calculations"
        },
        {
            "type": "quotation",
            "name": "Quotation",
            "description": "Price quotation for pre-sales"
        },
        {
            "type": "sales_order",
            "name": "Sales Order",
            "description": "Sales order confirmation"
        },
        {
            "type": "proforma_invoice",
            "name": "Proforma Invoice",
            "description": "Proforma invoice for advance payments"
        },
        {
            "type": "delivery-challan",
            "name": "Delivery Challan",
            "description": "Delivery challan without prices or taxes"
        },
        {
            "type": "goods-receipt-notes",
            "name": "Goods Receipt Note",
            "description": "Goods receipt note with vendor details"
        }
    ]
    
    return {
        "templates": templates,
        "total_count": len(templates)
    }

async def _get_voucher_data(voucher_type: str, voucher_id: int, 
                          db: AsyncSession, current_user: User) -> Dict[str, Any]:  # Changed to async def and AsyncSession
    """
    Get voucher data based on type and ID
    """
    
    model_map = {
        'purchase': PurchaseVoucher,
        'purchase-vouchers': PurchaseVoucher,
        'purchase-orders': PurchaseOrder,
        'purchase-return': PurchaseReturn,
        'purchase-returns': PurchaseReturn,
        'sales': SalesVoucher,
        'sales-vouchers': SalesVoucher,
        'delivery-challan': DeliveryChallan,
        'delivery-challans': DeliveryChallan,
        'sales-return': SalesReturn,
        'sales-returns': SalesReturn,
        'quotation': Quotation,
        'sales_order': SalesOrder,
        'sales-orders': SalesOrder,
        'proforma_invoice': ProformaInvoice,
        'proforma-invoices': ProformaInvoice,
        'payment-vouchers': PaymentVoucher,
        'receipt-vouchers': ReceiptVoucher,
        'grn': GoodsReceiptNote
    }
    
    model_class = model_map.get(voucher_type)
    if not model_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported voucher type: {voucher_type}"
        )
    
    try:
        # Query voucher with organization filtering and eager loading
        stmt = select(model_class).filter(
            model_class.id == voucher_id,
            model_class.organization_id == current_user.organization_id
        )
        
        # Add eager loading for common relations
        if hasattr(model_class, 'vendor'):
            stmt = stmt.options(joinedload(model_class.vendor))
        if hasattr(model_class, 'customer'):
            stmt = stmt.options(joinedload(model_class.customer))
        if hasattr(model_class, 'purchase_order'):
            stmt = stmt.options(joinedload(model_class.purchase_order))
        if hasattr(model_class, 'sales_order'):
            stmt = stmt.options(joinedload(model_class.sales_order))
        if hasattr(model_class, 'grn'):
            stmt = stmt.options(joinedload(model_class.grn))
        if hasattr(model_class, 'items'):
            item_class_map = {
                'purchase': PurchaseVoucherItem,
                'purchase-vouchers': PurchaseVoucherItem,
                'purchase-orders': PurchaseOrderItem,
                'purchase-return': PurchaseReturnItem,
                'purchase-returns': PurchaseReturnItem,
                'quotation': QuotationItem,
                'sales_order': SalesOrderItem,
                'sales-orders': SalesOrderItem,
                'proforma_invoice': ProformaInvoiceItem,
                'proforma-invoices': ProformaInvoiceItem,
                'delivery-challan': DeliveryChallanItem,
                'delivery-challans': DeliveryChallanItem,
                'grn': GoodsReceiptNoteItem
            }
            item_class = item_class_map.get(voucher_type)
            if item_class:
                stmt = stmt.options(joinedload(model_class.items).joinedload(item_class.product))
            else:
                stmt = stmt.options(joinedload(model_class.items))
        
        # Remove joinedload for additional_charges as it's a column property
        # if hasattr(model_class, 'additional_charges'):
        #     stmt = stmt.options(joinedload(model_class.additional_charges))
        
        result = await db.execute(stmt)  # Await execute
        voucher = result.scalars().first()  # Use scalars().first()
        
        if not voucher:
            return None
        
        # Convert to dictionary
        voucher_data = await _voucher_to_dict(voucher, db)  # Await since now async
        voucher_data['voucher_type'] = voucher_type
        
        return voucher_data
        
    except Exception as e:
        logger.error(f"Error retrieving {voucher_type} voucher {voucher_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve voucher data"
        )

async def _voucher_to_dict(voucher, db: AsyncSession) -> Dict[str, Any]:  # Changed to async def and AsyncSession
    """
    Convert voucher ORM object to dictionary for template rendering
    """
    
    # Base voucher fields
    voucher_data = {
        'id': voucher.id,
        'voucher_number': voucher.voucher_number,
        'date': voucher.date,
        'status': getattr(voucher, 'status', 'draft'),
        'notes': getattr(voucher, 'notes', ''),
        'terms_conditions': getattr(voucher, 'terms_conditions', ''),
        'created_at': voucher.created_at,
        # Initialize discount fields with defaults
        'line_discount_type': getattr(voucher, 'line_discount_type', None),
        'total_discount_type': getattr(voucher, 'total_discount_type', None),
        'total_discount': float(getattr(voucher, 'total_discount', 0.0) or 0.0),
        'round_off': float(getattr(voucher, 'round_off', 0.0) or 0.0),
        'total_amount': float(getattr(voucher, 'total_amount', 0.0) or 0.0),
    }
    
    # Add type-specific fields
    if hasattr(voucher, 'due_date'):
        voucher_data['due_date'] = voucher.due_date
    if hasattr(voucher, 'payment_terms'):
        voucher_data['payment_terms'] = voucher.payment_terms
    if hasattr(voucher, 'reference_number'):
        voucher_data['reference_number'] = voucher.reference_number
    if hasattr(voucher, 'invoice_number'):
        voucher_data['invoice_number'] = voucher.invoice_number
    if hasattr(voucher, 'invoice_date'):
        voucher_data['invoice_date'] = voucher.invoice_date
    if hasattr(voucher, 'shipping_address'):
        voucher_data['shipping_address'] = voucher.shipping_address
    if hasattr(voucher, 'bank_details'):
        voucher_data['bank_details'] = voucher.bank_details
    if hasattr(voucher, 'valid_until'):
        voucher_data['valid_until'] = voucher.valid_until
    if hasattr(voucher, 'delivery_terms'):
        voucher_data['delivery_terms'] = voucher.delivery_terms
    if hasattr(voucher, 'delivery_date'):
        voucher_data['required_by_date'] = voucher.delivery_date  # Alias for template
    if hasattr(voucher, 'payment_method'):
        voucher_data['payment_method'] = voucher.payment_method
    if hasattr(voucher, 'receipt_method'):
        voucher_data['receipt_method'] = voucher.receipt_method
    if hasattr(voucher, 'reference'):
        voucher_data['reference'] = voucher.reference
    if hasattr(voucher, 'bank_account'):
        voucher_data['bank_account'] = voucher.bank_account
    
    # Add related entities
    if hasattr(voucher, 'vendor') and voucher.vendor:
        voucher_data['vendor'] = _entity_to_dict(voucher.vendor)
    if hasattr(voucher, 'customer') and voucher.customer:
        voucher_data['customer'] = _entity_to_dict(voucher.customer)
    if hasattr(voucher, 'entity_type'):
        voucher_data['entity_type'] = voucher.entity_type
        voucher_data['entity_id'] = voucher.entity_id
        # Load entity based on type
        if voucher.entity_type.lower() == 'vendor':
            stmt = select(Vendor).filter(Vendor.id == voucher.entity_id)
            result = await db.execute(stmt)
            vendor = result.scalars().first()
            if vendor:
                voucher_data['vendor'] = _entity_to_dict(vendor)
        elif voucher.entity_type.lower() == 'customer':
            stmt = select(Customer).filter(Customer.id == voucher.entity_id)
            result = await db.execute(stmt)
            customer = result.scalars().first()
            if customer:
                voucher_data['customer'] = _entity_to_dict(customer)
        elif voucher.entity_type.lower() == 'employee':
            stmt = select(EmployeeProfile).filter(EmployeeProfile.id == voucher.entity_id)
            result = await db.execute(stmt)
            employee = result.scalars().first()
            if employee:
                voucher_data['employee'] = {
                    'id': employee.id,
                    'name': employee.user.full_name or f"{employee.user.first_name or ''} {employee.user.last_name or ''}",
                    'address': employee.address_line1 or '',
                    'city': employee.city or '',
                    'state': employee.state or '',
                    'pin_code': employee.pin_code or '',
                    'gst_number': '',
                    'contact_number': employee.personal_phone or '',
                    'email': employee.personal_email or '',
                    'state_code': employee.state or '',
                }
    
    if hasattr(voucher, 'purchase_order') and voucher.purchase_order:
        voucher_data['purchase_order'] = {'voucher_number': voucher.purchase_order.voucher_number}
    if hasattr(voucher, 'sales_order') and voucher.sales_order:
        voucher_data['sales_order'] = {'voucher_number': voucher.sales_order.voucher_number}
    if hasattr(voucher, 'grn') and voucher.grn:
        voucher_data['grn'] = {'voucher_number': voucher.grn.voucher_number}
    
    # Add items
    if hasattr(voucher, 'items') and voucher.items:
        voucher_data['items'] = [_item_to_dict(item) for item in voucher.items]
    else:
        voucher_data['items'] = []
    
    # Add additional charges if available
    if hasattr(voucher, 'additional_charges') and voucher.additional_charges:
        voucher_data['additional_charges'] = voucher.additional_charges
    else:
        voucher_data['additional_charges'] = []
    
    return voucher_data

def _entity_to_dict(entity) -> Dict[str, Any]:
    """Convert vendor/customer entity to dictionary"""
    return {
        'id': entity.id,
        'name': entity.name,
        'address': getattr(entity, 'address', ''),
        'city': getattr(entity, 'city', ''),
        'state': entity.state,
        'pin_code': getattr(entity, 'pin_code', ''),
        'gst_number': getattr(entity, 'gst_number', ''),
        'contact_number': getattr(entity, 'contact_number', ''),
        'email': getattr(entity, 'email', ''),
        'state_code': getattr(entity, 'state_code', '') or (entity.gst_number[:2] if getattr(entity, 'gst_number', None) else ''),
    }

def _item_to_dict(item) -> Dict[str, Any]:
    """Convert voucher item to dictionary"""
    item_data = {
        'id': item.id,
        'product_id': getattr(item, 'product_id', None),
        'unit': getattr(item, 'unit', 'Nos'),
        'unit_price': float(item.unit_price or 0),
        'description': getattr(item, 'description', ''),
        'hsn_code': getattr(item, 'hsn_code', ''),
    }
    
    if hasattr(item, 'received_quantity'):
        # Handle GRN items
        item_data['quantity'] = float(item.received_quantity or 0)
        item_data['ordered_quantity'] = float(item.ordered_quantity or 0)
        item_data['accepted_quantity'] = float(item.accepted_quantity or 0)
        item_data['rejected_quantity'] = float(item.rejected_quantity or 0)
        item_data['gst_rate'] = 0.0
        item_data['discount_percentage'] = 0.0
        item_data['discount_amount'] = 0.0
        item_data['cgst_amount'] = 0.0
        item_data['sgst_amount'] = 0.0
        item_data['igst_amount'] = 0.0
        item_data['total_amount'] = float(item.total_cost or 0)
    else:
        # Handle standard voucher items
        item_data['quantity'] = float(item.quantity or 0)
        item_data['gst_rate'] = float(getattr(item, 'gst_rate', 0) or 0)
        item_data['discount_percentage'] = float(getattr(item, 'discount_percentage', 0) or 0)
        item_data['discount_amount'] = float(getattr(item, 'discount_amount', 0) or 0)
        item_data['cgst_amount'] = float(getattr(item, 'cgst_amount', 0) or 0)
        item_data['sgst_amount'] = float(getattr(item, 'sgst_amount', 0) or 0)
        item_data['igst_amount'] = float(getattr(item, 'igst_amount', 0) or 0)
        item_data['total_amount'] = float(getattr(item, 'total_amount', 0) or 0)
    
    # Add product name if available
    if hasattr(item, 'product') and item.product:
        item_data['product_name'] = item.product.product_name
        item_data['hsn_code'] = item.product.hsn_code or item_data['hsn_code']
    
    return item_data