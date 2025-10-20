# app/api/v1/reports.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User, Product, Stock, Vendor, Customer
from app.models.vouchers import (
    PurchaseVoucher, SalesVoucher, PurchaseOrder, SalesOrder,
    GoodsReceiptNote, DeliveryChallan
)
from app.core.tenant import require_current_organization_id, TenantQueryMixin
from app.core.permissions import PermissionChecker, Permission
from app.core.org_restrictions import require_current_organization_id
from app.schemas.ledger import (
    LedgerFilters, CompleteLedgerResponse, OutstandingLedgerResponse
)
from app.services.ledger_service import LedgerService
from app.services.excel_service import ExcelService, ReportsExcelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/dashboard-stats")
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics"""
    try:
        org_id = require_current_organization_id(current_user)
        
        # Count masters with eager loading
        vendors_query = select(Vendor).where(Vendor.is_active == True)
        vendors_query = TenantQueryMixin.filter_by_tenant(vendors_query, Vendor, org_id)
        vendors_result = await db.execute(vendors_query)
        vendors_count = len(vendors_result.scalars().all())
        
        customers_query = select(Customer).where(Customer.is_active == True)
        customers_query = TenantQueryMixin.filter_by_tenant(customers_query, Customer, org_id)
        customers_result = await db.execute(customers_query)
        customers_count = len(customers_result.scalars().all())
        
        products_query = select(Product).where(Product.is_active == True)
        products_query = TenantQueryMixin.filter_by_tenant(products_query, Product, org_id)
        products_result = await db.execute(products_query)
        products_count = len(products_result.scalars().all())
        
        # Count vouchers
        purchase_vouchers_query = select(PurchaseVoucher)
        purchase_vouchers_query = TenantQueryMixin.filter_by_tenant(purchase_vouchers_query, PurchaseVoucher, org_id)
        purchase_vouchers_result = await db.execute(purchase_vouchers_query)
        purchase_vouchers_count = len(purchase_vouchers_result.scalars().all())
        
        sales_vouchers_query = select(SalesVoucher)
        sales_vouchers_query = TenantQueryMixin.filter_by_tenant(sales_vouchers_query, SalesVoucher, org_id)
        sales_vouchers_result = await db.execute(sales_vouchers_query)
        sales_vouchers_count = len(sales_vouchers_result.scalars().all())
        
        # Low stock items with eager loading
        low_stock_query = select(Stock).join(Product).where(
            Stock.quantity <= Product.reorder_level,
            Product.is_active == True
        ).options(selectinload(Stock.product))
        low_stock_query = TenantQueryMixin.filter_by_tenant(low_stock_query, Stock, org_id)
        low_stock_result = await db.execute(low_stock_query)
        low_stock_count = len(low_stock_result.scalars().all())
        
        return {
            "masters": {
                "vendors": vendors_count,
                "customers": customers_count,
                "products": products_count
            },
            "vouchers": {
                "purchase_vouchers": purchase_vouchers_count,
                "sales_vouchers": sales_vouchers_count
            },
            "inventory": {
                "low_stock_items": low_stock_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )

@router.get("/sales-report")
async def get_sales_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales report"""
    try:
        org_id = require_current_organization_id(current_user)
        
        query = select(SalesVoucher).join(Customer).options(selectinload(SalesVoucher.customer))
        query = TenantQueryMixin.filter_by_tenant(query, SalesVoucher, org_id)
        
        if start_date:
            query = query.filter(SalesVoucher.date >= start_date)
        if end_date:
            query = query.filter(SalesVoucher.date <= end_date)
        if customer_id:
            query = query.filter(SalesVoucher.customer_id == customer_id)
        
        result = await db.execute(query)
        sales_vouchers = result.scalars().all()
        
        total_sales = sum(voucher.total_amount for voucher in sales_vouchers)
        total_gst = sum(
            voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount 
            for voucher in sales_vouchers
        )
        
        return {
            "vouchers": [
                {
                    "id": voucher.id,
                    "voucher_number": voucher.voucher_number,
                    "date": voucher.date,
                    "customer_name": voucher.customer.name if voucher.customer else "Unknown",
                    "total_amount": voucher.total_amount,
                    "gst_amount": voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount,
                    "status": voucher.status
                }
                for voucher in sales_vouchers
            ],
            "summary": {
                "total_vouchers": len(sales_vouchers),
                "total_sales": total_sales,
                "total_gst": total_gst
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting sales report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sales report"
        )

@router.get("/purchase-report")
async def get_purchase_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vendor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get purchase report"""
    try:
        org_id = require_current_organization_id(current_user)
        
        query = select(PurchaseVoucher).join(Vendor).options(selectinload(PurchaseVoucher.vendor))
        query = TenantQueryMixin.filter_by_tenant(query, PurchaseVoucher, org_id)
        
        if start_date:
            query = query.filter(PurchaseVoucher.date >= start_date)
        if end_date:
            query = query.filter(PurchaseVoucher.date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseVoucher.vendor_id == vendor_id)
        
        result = await db.execute(query)
        purchase_vouchers = result.scalars().all()
        
        total_purchases = sum(voucher.total_amount for voucher in purchase_vouchers)
        total_gst = sum(
            voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount 
            for voucher in purchase_vouchers
        )
        
        return {
            "vouchers": [
                {
                    "id": voucher.id,
                    "voucher_number": voucher.voucher_number,
                    "date": voucher.date,
                    "vendor_name": voucher.vendor.name if voucher.vendor else "Unknown",
                    "total_amount": voucher.total_amount,
                    "gst_amount": voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount,
                    "status": voucher.status
                }
                for voucher in purchase_vouchers
            ],
            "summary": {
                "total_vouchers": len(purchase_vouchers),
                "total_purchases": total_purchases,
                "total_gst": total_gst
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting purchase report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get purchase report"
        )

@router.get("/inventory-report")
async def get_inventory_report(
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory report"""
    try:
        org_id = require_current_organization_id(current_user)
        
        query = select(Stock).join(Product).filter(Product.is_active == True).options(selectinload(Stock.product))
        query = TenantQueryMixin.filter_by_tenant(query, Stock, org_id)
        
        if low_stock_only:
            query = query.filter(Stock.quantity <= Product.reorder_level)
        
        result = await db.execute(query)
        stock_items = result.scalars().all()
        
        total_value = sum(
            item.quantity * item.product.unit_price 
            for item in stock_items if item.product
        )
        
        return {
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product.product_name if item.product else "Unknown",
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "unit_price": item.product.unit_price if item.product else 0,
                    "total_value": item.quantity * (item.product.unit_price if item.product else 0),
                    "reorder_level": item.product.reorder_level if item.product else 0,
                    "is_low_stock": item.quantity <= (item.product.reorder_level if item.product else 0)
                }
                for item in stock_items
            ],
            "summary": {
                "total_items": len(stock_items),
                "total_value": total_value,
                "low_stock_items": sum(
                    1 for item in stock_items 
                    if item.product and item.quantity <= item.product.reorder_level
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting inventory report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get inventory report"
        )

@router.get("/pending-orders")
async def get_pending_orders(
    order_type: str = "all",  # all, purchase, sales
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get pending orders report"""
    try:
        org_id = require_current_organization_id(current_user)
        
        pending_orders = []
        
        if order_type in ["all", "purchase"]:
            purchase_orders_query = select(PurchaseOrder).filter(
                PurchaseOrder.status.in_(["draft", "pending"])
            ).options(selectinload(PurchaseOrder.vendor))
            purchase_orders_query = TenantQueryMixin.filter_by_tenant(purchase_orders_query, PurchaseOrder, org_id)
            purchase_orders_result = await db.execute(purchase_orders_query)
            purchase_orders = purchase_orders_result.scalars().all()
            
            for order in purchase_orders:
                pending_orders.append({
                    "id": order.id,
                    "type": "Purchase Order",
                    "number": order.voucher_number,
                    "date": order.date,
                    "party": order.vendor.name if order.vendor else "Unknown",
                    "amount": order.total_amount,
                    "status": order.status
                })
        
        if order_type in ["all", "sales"]:
            sales_orders_query = select(SalesOrder).filter(
                SalesOrder.status.in_(["draft", "pending"])
            ).options(selectinload(SalesOrder.customer))
            sales_orders_query = TenantQueryMixin.filter_by_tenant(sales_orders_query, SalesOrder, org_id)
            sales_orders_result = await db.execute(sales_orders_query)
            sales_orders = sales_orders_result.scalars().all()
            
            for order in sales_orders:
                pending_orders.append({
                    "id": order.id,
                    "type": "Sales Order",
                    "number": order.voucher_number,
                    "date": order.date,
                    "party": order.customer.name if order.customer else "Unknown",
                    "amount": order.total_amount,
                    "status": order.status
                })
        
        # Sort by date
        pending_orders.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "orders": pending_orders,
            "summary": {
                "total_orders": len(pending_orders),
                "total_value": sum(order["amount"] for order in pending_orders)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting pending orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending orders"
        )

def _check_ledger_access(current_user: User) -> None:
    """
    Check if user has access to ledger reports.
    Access is granted to: Super Admin, Admin, and Standard User (with access)
    """
    # Allow org-level super admins, admins, and standard users
    allowed_roles = ["super_admin", "org_admin", "admin", "standard_user"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access ledger reports"
        )

@router.get("/complete-ledger", response_model=CompleteLedgerResponse)
async def get_complete_ledger(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_type: Optional[str] = "all",
    account_id: Optional[str] = None,  # Changed to string to handle raw input
    voucher_type: Optional[str] = "all",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get complete ledger showing all debit/credit account transactions.
    
    **Access Control**: Super Admin, Admin, and Standard User (with access)
    
    **Parameters**:
    - **start_date**: Start date for filtering transactions (YYYY-MM-DD)
    - **end_date**: End date for filtering transactions (YYYY-MM-DD)  
    - **account_type**: Type of account ("vendor", "customer", "all")
    - **account_id**: Specific vendor or customer ID to filter by
    - **voucher_type**: Type of voucher to filter by ("purchase_voucher", "sales_voucher", "payment_voucher", "receipt_voucher", "debit_note", "credit_note", "all")
    
    **Returns**: Complete ledger with all transactions, running balances, and summary statistics
    """
    try:
        # Check access permissions
        _check_ledger_access(current_user)
        
        # Get organization context
        org_id = require_current_organization_id(current_user)
        
        # Prepare filters, manually converting account_id
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,  # Pass raw string to validator
            voucher_type=voucher_type
        )
        
        # Log filter values for debugging
        logger.debug(f"Ledger filters: {filters.dict()}")
        
        # Generate complete ledger
        ledger_response = await LedgerService.get_complete_ledger(db, org_id, filters)
        
        logger.info(f"Complete ledger generated for user {current_user.email}, org {org_id}")
        return ledger_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating complete ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate complete ledger report"
        )

@router.get("/outstanding-ledger", response_model=OutstandingLedgerResponse)
async def get_outstanding_ledger(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_type: Optional[str] = "all",
    account_id: Optional[str] = None,  # Changed to string to handle raw input
    voucher_type: Optional[str] = "all",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get outstanding ledger showing only open balances by account.
    
    **Access Control**: Super Admin, Admin, and Standard User (with access)
    
    **Sign Convention**:
    - **Negative amounts**: Payable to vendors (money owed TO vendors)
    - **Positive amounts**: Receivable from customers (money owed BY customers)
    
    **Parameters**:
    - **start_date**: Start date for filtering transactions (YYYY-MM-DD)
    - **end_date**: End date for filtering transactions (YYYY-MM-DD)
    - **account_type**: Type of account ("vendor", "customer", "all")
    - **account_id**: Specific vendor or customer ID to filter by
    - **voucher_type**: Type of voucher to filter by ("purchase_voucher", "sales_voucher", "payment_voucher", "receipt_voucher", "debit_note", "credit_note", "all")
    
    **Returns**: Outstanding balances by account with proper sign convention and summary statistics
    """
    try:
        # Check access permissions
        _check_ledger_access(current_user)
        
        # Get organization context
        org_id = require_current_organization_id(current_user)
        
        # Prepare filters, manually converting account_id
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,  # Pass raw string to validator
            voucher_type=voucher_type
        )
        
        # Log filter values for debugging
        logger.debug(f"Ledger filters: {filters.dict()}")
        
        # Generate outstanding ledger
        ledger_response = await LedgerService.get_outstanding_ledger(db, org_id, filters)
        
        logger.info(f"Outstanding ledger generated for user {current_user.email}, org {org_id}")
        return ledger_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating outstanding ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate outstanding ledger report"
        )

@router.get("/sales-report/export/excel")
async def export_sales_report_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export sales report to Excel"""
    try:
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        org_id = require_current_organization_id(current_user)
        
        # Get sales data using the same logic as the sales report endpoint
        query = select(SalesVoucher).join(Customer).options(selectinload(SalesVoucher.customer))
        query = TenantQueryMixin.filter_by_tenant(query, SalesVoucher, org_id)
        
        if start_date:
            query = query.filter(SalesVoucher.date >= start_date)
        if end_date:
            query = query.filter(SalesVoucher.date <= end_date)
        if customer_id:
            query = query.filter(SalesVoucher.customer_id == customer_id)
        
        result = await db.execute(query)
        sales_vouchers = result.scalars().all()
        
        total_sales = sum(voucher.total_amount for voucher in sales_vouchers)
        total_gst = sum(
            voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount 
            for voucher in sales_vouchers
        )
        
        sales_data = {
            "vouchers": [
                {
                    "voucher_number": voucher.voucher_number,
                    "date": voucher.date,
                    "customer_name": voucher.customer.name if voucher.customer else "Unknown",
                    "total_amount": voucher.total_amount,
                    "gst_amount": voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount,
                    "status": voucher.status
                }
                for voucher in sales_vouchers
            ],
            "summary": {
                "total_vouchers": len(sales_vouchers),
                "total_sales": total_sales,
                "total_gst": total_gst
            }
        }
        
        excel_data = ReportsExcelService.export_sales_report(sales_data)
        return ExcelService.create_streaming_response(excel_data, "sales_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting sales report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export sales report"
        )

@router.get("/purchase-report/export/excel")
async def export_purchase_report_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vendor_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export purchase report to Excel"""
    try:
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        org_id = require_current_organization_id(current_user)
        
        # Get purchase data using the same logic as the purchase report endpoint
        query = select(PurchaseVoucher).join(Vendor).options(selectinload(PurchaseVoucher.vendor))
        query = TenantQueryMixin.filter_by_tenant(query, PurchaseVoucher, org_id)
        
        if start_date:
            query = query.filter(PurchaseVoucher.date >= start_date)
        if end_date:
            query = query.filter(PurchaseVoucher.date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseVoucher.vendor_id == vendor_id)
        
        result = await db.execute(query)
        purchase_vouchers = result.scalars().all()
        
        total_purchases = sum(voucher.total_amount for voucher in purchase_vouchers)
        total_gst = sum(
            voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount 
            for voucher in purchase_vouchers
        )
        
        purchase_data = {
            "vouchers": [
                {
                    "voucher_number": voucher.voucher_number,
                    "date": voucher.date,
                    "vendor_name": voucher.vendor.name if voucher.vendor else "Unknown",
                    "total_amount": voucher.total_amount,
                    "gst_amount": voucher.cgst_amount + voucher.sgst_amount + voucher.igst_amount,
                    "status": voucher.status
                }
                for voucher in purchase_vouchers
            ],
            "summary": {
                "total_vouchers": len(purchase_vouchers),
                "total_purchases": total_purchases,
                "total_gst": total_gst
            }
        }
        
        excel_data = ReportsExcelService.export_purchase_report(purchase_data)
        return ExcelService.create_streaming_response(excel_data, "purchase_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting purchase report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export purchase report"
        )

@router.get("/inventory-report/export/excel")
async def export_inventory_report_excel(
    include_zero_stock: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export inventory report to Excel"""
    try:
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        org_id = require_current_organization_id(current_user)
        
        # Get inventory data using the same logic as the inventory report endpoint
        query = select(Stock).join(Product).filter(Product.is_active == True).options(selectinload(Stock.product))
        query = TenantQueryMixin.filter_by_tenant(query, Stock, org_id)
        
        if not include_zero_stock:
            query = query.filter(Stock.quantity > 0)
        
        result = await db.execute(query)
        stocks = result.scalars().all()
        
        total_value = sum(stock.quantity * stock.product.unit_price for stock in stocks if stock.product)
        low_stock_items = sum(1 for stock in stocks if stock.product and stock.quantity <= stock.product.reorder_level)
        
        inventory_data = {
            "items": [
                {
                    "product_name": stock.product.product_name if stock.product else "Unknown",
                    "hsn_code": stock.product.hsn_code or "" if stock.product else "",
                    "quantity": stock.quantity,
                    "unit": stock.product.unit if stock.product else "",
                    "unit_price": stock.product.unit_price if stock.product else 0,
                    "reorder_level": stock.product.reorder_level if stock.product else 0
                }
                for stock in stocks
            ],
            "summary": {
                "total_products": len(stocks),
                "total_value": total_value,
                "low_stock_items": low_stock_items
            }
        }
        
        excel_data = ReportsExcelService.export_inventory_report(inventory_data)
        return ExcelService.create_streaming_response(excel_data, "inventory_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting inventory report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export inventory report"
        )

@router.get("/pending-orders/export/excel")
async def export_pending_orders_excel(
    order_type: str = "all",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export pending orders report to Excel"""
    try:
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        org_id = require_current_organization_id(current_user)
        
        orders = []
        
        if order_type in ["all", "purchase"]:
            purchase_orders_query = select(PurchaseOrder).filter(
                PurchaseOrder.status.in_(["pending", "partial"])
            ).options(selectinload(PurchaseOrder.vendor))
            purchase_orders_query = TenantQueryMixin.filter_by_tenant(purchase_orders_query, PurchaseOrder, org_id)
            purchase_orders_result = await db.execute(purchase_orders_query)
            purchase_orders = purchase_orders_result.scalars().all()
            
            orders.extend([
                {
                    "order_number": order.voucher_number,
                    "order_type": "Purchase Order",
                    "date": order.date,
                    "party_name": order.vendor.name if order.vendor else "Unknown",
                    "total_amount": order.total_amount,
                    "status": order.status,
                    "days_pending": (datetime.now().date() - order.date).days
                }
                for order in purchase_orders
            ])
        
        if order_type in ["all", "sales"]:
            sales_orders_query = select(SalesOrder).filter(
                SalesOrder.status.in_(["pending", "partial"])
            ).options(selectinload(SalesOrder.customer))
            sales_orders_query = TenantQueryMixin.filter_by_tenant(sales_orders_query, SalesOrder, org_id)
            sales_orders_result = await db.execute(sales_orders_query)
            sales_orders = sales_orders_result.scalars().all()
            
            orders.extend([
                {
                    "order_number": order.voucher_number,
                    "order_type": "Sales Order",
                    "date": order.date,
                    "party_name": order.customer.name if order.customer else "Unknown",
                    "total_amount": order.total_amount,
                    "status": order.status,
                    "days_pending": (datetime.now().date() - order.date).days
                }
                for order in sales_orders
            ])
        
        total_value = sum(order['total_amount'] for order in orders)
        
        orders_data = {
            "orders": orders,
            "summary": {
                "total_orders": len(orders),
                "total_value": total_value
            }
        }
        
        excel_data = ReportsExcelService.export_pending_orders_report(orders_data)
        return ExcelService.create_streaming_response(excel_data, "pending_orders_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting pending orders report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export pending orders report"
        )

@router.get("/pending-purchase-orders-with-grn-status")
async def get_pending_purchase_orders_with_grn_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get pending purchase orders with GRN status and tracking information for inventory management.
    
    This endpoint returns ALL purchase orders that:
    1. Have at least one item with pending_quantity > 0, OR
    2. Have not been fully received yet
    
    Color coding:
    - Red: No tracking details (no transporter_name and no tracking_number)
    - Yellow: Has tracking but GRN still pending
    - Green: GRN complete (not shown in pending orders)
    """
    try:
        # Ensure organization context is set
        try:
            org_id = require_current_organization_id(current_user)
        except Exception as org_err:
            logger.warning(f"Organization context error: {org_err}, using user's organization_id")
            org_id = current_user.organization_id
        
        if not org_id:
            logger.error("No organization context available")
            return {
                "orders": [],
                "summary": {
                    "total_orders": 0,
                    "total_value": 0,
                    "with_tracking": 0,
                    "without_tracking": 0
                }
            }
        
        # Get all purchase orders with items and vendor
        purchase_orders_query = select(PurchaseOrder).options(
            selectinload(PurchaseOrder.items),
            selectinload(PurchaseOrder.vendor)
        )
        purchase_orders_query = TenantQueryMixin.filter_by_tenant(purchase_orders_query, PurchaseOrder, org_id)
        purchase_orders_result = await db.execute(purchase_orders_query)
        purchase_orders = purchase_orders_result.scalars().all()
        
        pending_orders = []
        
        for po in purchase_orders:
            try:
                # Skip if PO has no items
                if not po.items:
                    continue
                
                # Calculate total ordered vs received using pending_quantity from items
                total_ordered_qty = sum(item.quantity for item in po.items)
                total_pending_qty = sum(item.pending_quantity for item in po.items)
                total_received_qty = total_ordered_qty - total_pending_qty
                
                # Only include POs that have pending quantities
                if total_pending_qty > 0:
                    # Check if GRN exists for this PO
                    grns_query = select(GoodsReceiptNote).filter(
                        GoodsReceiptNote.purchase_order_id == po.id
                    ).options(selectinload(GoodsReceiptNote.purchase_order))
                    grns_query = TenantQueryMixin.filter_by_tenant(grns_query, GoodsReceiptNote, org_id)
                    grns_result = await db.execute(grns_query)
                    grns = grns_result.scalars().all()
                    
                    # Determine color coding
                    # Red: no tracking details (neither transporter_name nor tracking_number)
                    # Yellow: has tracking but GRN pending
                    has_tracking = bool(po.tracking_number or po.transporter_name)
                    
                    color_status = "yellow" if has_tracking else "red"
                    
                    pending_orders.append({
                        "id": po.id,
                        "voucher_number": po.voucher_number,
                        "date": po.date,
                        "vendor_name": po.vendor.name if po.vendor else "Unknown",
                        "vendor_id": po.vendor_id,
                        "total_amount": po.total_amount,
                        "status": po.status,
                        "total_ordered_qty": total_ordered_qty,
                        "total_received_qty": total_received_qty,
                        "pending_qty": total_pending_qty,
                        "grn_count": len(grns),
                        "has_tracking": has_tracking,
                        "transporter_name": po.transporter_name,
                        "tracking_number": po.tracking_number,
                        "tracking_link": po.tracking_link,
                        "color_status": color_status,
                        "days_pending": (datetime.now().date() - po.date.date()).days if po.date else 0
                    })
            except Exception as po_err:
                logger.error(f"Error processing PO {po.id}: {po_err}", exc_info=True)
                continue
        
        # Sort by date (newest first)
        pending_orders.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "orders": pending_orders,
            "summary": {
                "total_orders": len(pending_orders),
                "total_value": sum(order["total_amount"] for order in pending_orders),
                "with_tracking": sum(1 for order in pending_orders if order["has_tracking"]),
                "without_tracking": sum(1 for order in pending_orders if not order["has_tracking"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting pending purchase orders with GRN status: {e}", exc_info=True)
        # Never return 500, always return empty result
        return {
            "orders": [],
            "summary": {
                "total_orders": 0,
                "total_value": 0,
                "with_tracking": 0,
                "without_tracking": 0
            }
        }

def canAccessLedger(user) -> bool:
    """Check if user can access ledger functionality"""
    if not user:
        return False
    
    # Super Admin and Admin always have access
    if hasattr(user, 'is_super_admin') and user.is_super_admin:
        return True
    if hasattr(user, 'role') and user.role in ['admin', 'org_admin']:
        return True
    
    # Standard users need specific permission
    if hasattr(user, 'role') and user.role == 'standard_user':
        return PermissionChecker.has_permission(user, Permission.VIEW_USERS)
    
    return False