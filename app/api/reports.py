from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
from app.core.org_restrictions import ensure_organization_context
from app.schemas.ledger import (
    LedgerFilters, CompleteLedgerResponse, OutstandingLedgerResponse
)
from app.services.ledger_service import LedgerService
from app.services.excel_service import ExcelService, ReportsExcelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard-stats")
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics"""
    try:
        org_id = require_current_organization_id()
        
        # Count masters
        vendors_count = TenantQueryMixin.filter_by_tenant(
            db.query(Vendor), Vendor, org_id
        ).filter(Vendor.is_active == True).count()
        
        customers_count = TenantQueryMixin.filter_by_tenant(
            db.query(Customer), Customer, org_id
        ).filter(Customer.is_active == True).count()
        
        products_count = TenantQueryMixin.filter_by_tenant(
            db.query(Product), Product, org_id
        ).filter(Product.is_active == True).count()
        
        # Count vouchers
        purchase_vouchers_count = TenantQueryMixin.filter_by_tenant(
            db.query(PurchaseVoucher), PurchaseVoucher, org_id
        ).count()
        
        sales_vouchers_count = TenantQueryMixin.filter_by_tenant(
            db.query(SalesVoucher), SalesVoucher, org_id
        ).count()
        
        # Low stock items
        low_stock_query = TenantQueryMixin.filter_by_tenant(
            db.query(Stock), Stock, org_id
        ).join(Product).filter(
            Stock.quantity <= Product.reorder_level,
            Product.is_active == True
        )
        low_stock_count = low_stock_query.count()
        
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales report"""
    try:
        org_id = require_current_organization_id()
        
        query = TenantQueryMixin.filter_by_tenant(
            db.query(SalesVoucher), SalesVoucher, org_id
        ).join(Customer)
        
        if start_date:
            query = query.filter(SalesVoucher.date >= start_date)
        if end_date:
            query = query.filter(SalesVoucher.date <= end_date)
        if customer_id:
            query = query.filter(SalesVoucher.customer_id == customer_id)
        
        sales_vouchers = query.all()
        
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
                    "customer_name": voucher.customer.name,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get purchase report"""
    try:
        org_id = require_current_organization_id()
        
        query = TenantQueryMixin.filter_by_tenant(
            db.query(PurchaseVoucher), PurchaseVoucher, org_id
        ).join(Vendor)
        
        if start_date:
            query = query.filter(PurchaseVoucher.date >= start_date)
        if end_date:
            query = query.filter(PurchaseVoucher.date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseVoucher.vendor_id == vendor_id)
        
        purchase_vouchers = query.all()
        
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
                    "vendor_name": voucher.vendor.name,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory report"""
    try:
        org_id = require_current_organization_id()
        
        query = TenantQueryMixin.filter_by_tenant(
            db.query(Stock), Stock, org_id
        ).join(Product).filter(Product.is_active == True)
        
        if low_stock_only:
            query = query.filter(Stock.quantity <= Product.reorder_level)
        
        stock_items = query.all()
        
        total_value = sum(
            item.quantity * item.product.unit_price 
            for item in stock_items if item.product
        )
        
        return {
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product.name if item.product else "Unknown",
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get pending orders report"""
    try:
        org_id = require_current_organization_id()
        
        pending_orders = []
        
        if order_type in ["all", "purchase"]:
            purchase_orders = TenantQueryMixin.filter_by_tenant(
                db.query(PurchaseOrder), PurchaseOrder, org_id
            ).filter(PurchaseOrder.status.in_(["draft", "pending"])).all()
            
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
            sales_orders = TenantQueryMixin.filter_by_tenant(
                db.query(SalesOrder), SalesOrder, org_id
            ).filter(SalesOrder.status.in_(["draft", "pending"])).all()
            
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


# =============================================
# LEDGER ENDPOINTS
# =============================================

def _check_ledger_access(current_user: User) -> None:
    """
    Check if user has access to ledger reports.
    Access is granted to: Super Admin, Admin, and Standard User (with access)
    """
    # Block app super admins from accessing organization data
    ensure_organization_context(current_user)
    
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
    account_id: Optional[int] = None,
    voucher_type: Optional[str] = "all",
    db: Session = Depends(get_db),
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
        org_id = ensure_organization_context(current_user)
        
        # Prepare filters
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,
            voucher_type=voucher_type
        )
        
        # Generate complete ledger
        ledger_response = LedgerService.get_complete_ledger(db, org_id, filters)
        
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
    account_id: Optional[int] = None,
    voucher_type: Optional[str] = "all",
    db: Session = Depends(get_db),
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
        org_id = ensure_organization_context(current_user)
        
        # Prepare filters
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,
            voucher_type=voucher_type
        )
        
        # Generate outstanding ledger
        ledger_response = LedgerService.get_outstanding_ledger(db, org_id, filters)
        
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


# Export endpoints
@router.get("/sales-report/export/excel")
async def export_sales_report_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
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
        
        org_id = require_current_organization_id()
        
        # Get sales data using the same logic as the sales report endpoint
        query = TenantQueryMixin.filter_by_tenant(
            db.query(SalesVoucher), SalesVoucher, org_id
        ).join(Customer)
        
        if start_date:
            query = query.filter(SalesVoucher.date >= start_date)
        if end_date:
            query = query.filter(SalesVoucher.date <= end_date)
        if customer_id:
            query = query.filter(SalesVoucher.customer_id == customer_id)
        
        sales_vouchers = query.all()
        
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
                    "customer_name": voucher.customer.name,
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
    db: Session = Depends(get_db),
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
        
        org_id = require_current_organization_id()
        
        # Get purchase data using the same logic as the purchase report endpoint
        query = TenantQueryMixin.filter_by_tenant(
            db.query(PurchaseVoucher), PurchaseVoucher, org_id
        ).join(Vendor)
        
        if start_date:
            query = query.filter(PurchaseVoucher.date >= start_date)
        if end_date:
            query = query.filter(PurchaseVoucher.date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseVoucher.vendor_id == vendor_id)
        
        purchase_vouchers = query.all()
        
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
                    "vendor_name": voucher.vendor.name,
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
    db: Session = Depends(get_db),
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
        
        org_id = require_current_organization_id()
        
        # Get inventory data using the same logic as the inventory report endpoint
        query = TenantQueryMixin.filter_by_tenant(
            db.query(Stock), Stock, org_id
        ).join(Product).filter(Product.is_active == True)
        
        if not include_zero_stock:
            query = query.filter(Stock.quantity > 0)
        
        stocks = query.all()
        
        total_value = sum(stock.quantity * stock.product.unit_price for stock in stocks)
        low_stock_items = sum(1 for stock in stocks if stock.quantity <= stock.product.reorder_level)
        
        inventory_data = {
            "items": [
                {
                    "product_name": stock.product.name,
                    "hsn_code": stock.product.hsn_code or "",
                    "quantity": stock.quantity,
                    "unit": stock.product.unit,
                    "unit_price": stock.product.unit_price,
                    "reorder_level": stock.product.reorder_level
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
    db: Session = Depends(get_db),
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
        
        org_id = require_current_organization_id()
        
        orders = []
        
        # Get purchase orders
        if order_type in ["all", "purchase"]:
            purchase_orders = TenantQueryMixin.filter_by_tenant(
                db.query(PurchaseOrder), PurchaseOrder, org_id
            ).filter(PurchaseOrder.status.in_(["pending", "partial"])).join(Vendor).all()
            
            orders.extend([
                {
                    "order_number": order.order_number,
                    "order_type": "Purchase Order",
                    "date": order.date,
                    "party_name": order.vendor.name,
                    "total_amount": order.total_amount,
                    "status": order.status,
                    "days_pending": (datetime.now().date() - order.date).days
                }
                for order in purchase_orders
            ])
        
        # Get sales orders
        if order_type in ["all", "sales"]:
            sales_orders = TenantQueryMixin.filter_by_tenant(
                db.query(SalesOrder), SalesOrder, org_id
            ).filter(SalesOrder.status.in_(["pending", "partial"])).join(Customer).all()
            
            orders.extend([
                {
                    "order_number": order.order_number,
                    "order_type": "Sales Order",
                    "date": order.date,
                    "party_name": order.customer.name,
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


@router.get("/complete-ledger/export/excel")
async def export_complete_ledger_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_type: str = "all",
    account_id: Optional[int] = None,
    voucher_type: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export complete ledger to Excel"""
    try:
        # Check access permissions
        _check_ledger_access(current_user)
        
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        # Get organization context
        org_id = ensure_organization_context(current_user)
        
        # Prepare filters
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,
            voucher_type=voucher_type
        )
        
        # Generate complete ledger
        ledger_response = LedgerService.get_complete_ledger(db, org_id, filters)
        
        excel_data = ReportsExcelService.export_ledger_report(ledger_response.dict(), "complete")
        return ExcelService.create_streaming_response(excel_data, "complete_ledger_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting complete ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export complete ledger report"
        )


@router.get("/outstanding-ledger/export/excel")
async def export_outstanding_ledger_excel(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_type: str = "all",
    account_id: Optional[int] = None,
    voucher_type: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export outstanding ledger to Excel"""
    try:
        # Check access permissions
        _check_ledger_access(current_user)
        
        # Check if user has permission to export reports
        if not PermissionChecker.has_permission(current_user, Permission.VIEW_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to export reports"
            )
        
        # Get organization context
        org_id = ensure_organization_context(current_user)
        
        # Prepare filters
        filters = LedgerFilters(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type,
            account_id=account_id,
            voucher_type=voucher_type
        )
        
        # Generate outstanding ledger
        ledger_response = LedgerService.get_outstanding_ledger(db, org_id, filters)
        
        excel_data = ReportsExcelService.export_ledger_report(ledger_response.dict(), "outstanding")
        return ExcelService.create_streaming_response(excel_data, "outstanding_ledger_report.xlsx")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting outstanding ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export outstanding ledger report"
        )


def _check_ledger_access(current_user: User):
    """Check if user has access to ledger reports"""
    if not canAccessLedger(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Ledger reports require Super Admin, Admin, or authorized Standard User permissions."
        )

@router.get("/pending-purchase-orders-with-grn-status")
async def get_pending_purchase_orders_with_grn_status(
    db: Session = Depends(get_db),
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
            org_id = require_current_organization_id()
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
        
        # Get all purchase orders with items
        purchase_orders = TenantQueryMixin.filter_by_tenant(
            db.query(PurchaseOrder), PurchaseOrder, org_id
        ).all()
        
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
                    grns = TenantQueryMixin.filter_by_tenant(
                        db.query(GoodsReceiptNote), GoodsReceiptNote, org_id
                    ).filter(GoodsReceiptNote.purchase_order_id == po.id).all()
                    
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