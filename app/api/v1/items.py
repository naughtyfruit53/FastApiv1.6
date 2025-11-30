# app/api/v1/items.py
"""
Items router - Alias for products with rate memory APIs
Provides /api/v1/items endpoint as an alias with item-specific features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import Product
from app.api.deps.entitlements import require_permission_with_entitlement
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_id}/last-purchase-rate", response_model=dict)
async def get_item_last_purchase_rate(
    item_id: int,
    auth: tuple = Depends(require_permission_with_entitlement("erp", "products.read", "products")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the last purchase rate for an item.
    Returns the rate from the most recent purchase voucher or GRN.
    """
    current_user, org_id = auth
    
    # First verify product exists and belongs to org
    stmt = select(Product).where(
        Product.id == item_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Import here to avoid circular imports
    from app.models.vouchers.purchase import PurchaseVoucherItem, PurchaseVoucher, GoodsReceiptNoteItem, GoodsReceiptNote
    
    # Try to find from purchase vouchers first (more recent usually)
    stmt = select(
        PurchaseVoucherItem.unit_price,
        PurchaseVoucherItem.gst_rate,
        PurchaseVoucherItem.description,
        PurchaseVoucher.date,
        PurchaseVoucher.voucher_number
    ).join(
        PurchaseVoucher, PurchaseVoucherItem.purchase_voucher_id == PurchaseVoucher.id
    ).where(
        PurchaseVoucherItem.product_id == item_id,
        PurchaseVoucher.organization_id == org_id
    ).order_by(
        PurchaseVoucher.date.desc(),
        PurchaseVoucher.id.desc()
    ).limit(1)
    
    result = await db.execute(stmt)
    pv_row = result.first()
    
    # Also check GRN
    stmt = select(
        GoodsReceiptNoteItem.unit_price,
        GoodsReceiptNote.grn_date,
        GoodsReceiptNote.voucher_number
    ).join(
        GoodsReceiptNote, GoodsReceiptNoteItem.grn_id == GoodsReceiptNote.id
    ).where(
        GoodsReceiptNoteItem.product_id == item_id,
        GoodsReceiptNote.organization_id == org_id
    ).order_by(
        GoodsReceiptNote.grn_date.desc(),
        GoodsReceiptNote.id.desc()
    ).limit(1)
    
    result = await db.execute(stmt)
    grn_row = result.first()
    
    # Return the most recent one
    if pv_row and grn_row:
        if pv_row.date >= grn_row.grn_date:
            return {
                "item_id": item_id,
                "item_name": product.product_name,
                "last_purchase_rate": pv_row.unit_price,
                "gst_rate": pv_row.gst_rate,
                "last_description": pv_row.description,
                "source": "purchase_voucher",
                "source_voucher": pv_row.voucher_number,
                "last_purchase_date": pv_row.date.isoformat() if pv_row.date else None
            }
        else:
            return {
                "item_id": item_id,
                "item_name": product.product_name,
                "last_purchase_rate": grn_row.unit_price,
                "gst_rate": product.gst_rate,
                "last_description": None,
                "source": "goods_receipt_note",
                "source_voucher": grn_row.voucher_number,
                "last_purchase_date": grn_row.grn_date.isoformat() if grn_row.grn_date else None
            }
    elif pv_row:
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_purchase_rate": pv_row.unit_price,
            "gst_rate": pv_row.gst_rate,
            "last_description": pv_row.description,
            "source": "purchase_voucher",
            "source_voucher": pv_row.voucher_number,
            "last_purchase_date": pv_row.date.isoformat() if pv_row.date else None
        }
    elif grn_row:
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_purchase_rate": grn_row.unit_price,
            "gst_rate": product.gst_rate,
            "last_description": None,
            "source": "goods_receipt_note",
            "source_voucher": grn_row.voucher_number,
            "last_purchase_date": grn_row.grn_date.isoformat() if grn_row.grn_date else None
        }
    else:
        # Return product's default rate if no purchase history
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_purchase_rate": product.unit_price,
            "gst_rate": product.gst_rate,
            "last_description": product.description,
            "source": "product_default",
            "source_voucher": None,
            "last_purchase_date": None
        }


@router.get("/{item_id}/last-sales-rate", response_model=dict)
async def get_item_last_sales_rate(
    item_id: int,
    customer_id: Optional[int] = Query(None, description="Optional customer ID to get rate for specific customer"),
    auth: tuple = Depends(require_permission_with_entitlement("erp", "products.read", "products")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the last sales rate for an item.
    Returns the rate from the most recent sales voucher or sales order.
    Optionally filter by customer_id to get the last rate for a specific customer.
    """
    current_user, org_id = auth
    
    # First verify product exists and belongs to org
    stmt = select(Product).where(
        Product.id == item_id,
        Product.organization_id == org_id
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Import here to avoid circular imports
    from app.models.vouchers.presales import SalesOrder, SalesOrderItem
    from app.models.vouchers.sales import SalesVoucher, SalesVoucherItem
    
    # Try to find from sales vouchers first
    sv_stmt = select(
        SalesVoucherItem.unit_price,
        SalesVoucherItem.gst_rate,
        SalesVoucherItem.description,
        SalesVoucher.date,
        SalesVoucher.voucher_number,
        SalesVoucher.customer_id
    ).join(
        SalesVoucher, SalesVoucherItem.sales_voucher_id == SalesVoucher.id
    ).where(
        SalesVoucherItem.product_id == item_id,
        SalesVoucher.organization_id == org_id
    )
    
    if customer_id:
        sv_stmt = sv_stmt.where(SalesVoucher.customer_id == customer_id)
    
    sv_stmt = sv_stmt.order_by(
        SalesVoucher.date.desc(),
        SalesVoucher.id.desc()
    ).limit(1)
    
    result = await db.execute(sv_stmt)
    sv_row = result.first()
    
    # Also check sales orders
    so_stmt = select(
        SalesOrderItem.unit_price,
        SalesOrderItem.gst_rate,
        SalesOrderItem.description,
        SalesOrder.date,
        SalesOrder.voucher_number,
        SalesOrder.customer_id
    ).join(
        SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id
    ).where(
        SalesOrderItem.product_id == item_id,
        SalesOrder.organization_id == org_id
    )
    
    if customer_id:
        so_stmt = so_stmt.where(SalesOrder.customer_id == customer_id)
    
    so_stmt = so_stmt.order_by(
        SalesOrder.date.desc(),
        SalesOrder.id.desc()
    ).limit(1)
    
    result = await db.execute(so_stmt)
    so_row = result.first()
    
    # Return the most recent one
    if sv_row and so_row:
        if sv_row.date >= so_row.date:
            return {
                "item_id": item_id,
                "item_name": product.product_name,
                "last_sales_rate": sv_row.unit_price,
                "gst_rate": sv_row.gst_rate,
                "last_description": sv_row.description,
                "source": "sales_voucher",
                "source_voucher": sv_row.voucher_number,
                "last_sales_date": sv_row.date.isoformat() if sv_row.date else None,
                "customer_id": sv_row.customer_id
            }
        else:
            return {
                "item_id": item_id,
                "item_name": product.product_name,
                "last_sales_rate": so_row.unit_price,
                "gst_rate": so_row.gst_rate,
                "last_description": so_row.description,
                "source": "sales_order",
                "source_voucher": so_row.voucher_number,
                "last_sales_date": so_row.date.isoformat() if so_row.date else None,
                "customer_id": so_row.customer_id
            }
    elif sv_row:
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_sales_rate": sv_row.unit_price,
            "gst_rate": sv_row.gst_rate,
            "last_description": sv_row.description,
            "source": "sales_voucher",
            "source_voucher": sv_row.voucher_number,
            "last_sales_date": sv_row.date.isoformat() if sv_row.date else None,
            "customer_id": sv_row.customer_id
        }
    elif so_row:
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_sales_rate": so_row.unit_price,
            "gst_rate": so_row.gst_rate,
            "last_description": so_row.description,
            "source": "sales_order",
            "source_voucher": so_row.voucher_number,
            "last_sales_date": so_row.date.isoformat() if so_row.date else None,
            "customer_id": so_row.customer_id
        }
    else:
        # Return product's default rate if no sales history
        return {
            "item_id": item_id,
            "item_name": product.product_name,
            "last_sales_rate": product.unit_price,
            "gst_rate": product.gst_rate,
            "last_description": product.description,
            "source": "product_default",
            "source_voucher": None,
            "last_sales_date": None,
            "customer_id": None
        }
