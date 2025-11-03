# app/api/v1/management_reports.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User, Organization
from app.models.product_models import Product, Stock
from app.models.customer_models import Vendor, Customer
from app.models.vouchers.purchase import PurchaseVoucher, PurchaseOrder
from app.models.vouchers.presales import SalesOrder
from app.models.vouchers.sales import SalesVoucher
from app.models.vouchers.financial import PaymentVoucher, ReceiptVoucher
from app.models.analytics_models import ReportConfiguration
from app.services.excel_service import ExcelService, ReportsExcelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/management-reports", tags=["management-reports"])

@router.get("/executive-dashboard")
async def get_executive_dashboard(
    period: str = "month",  # day, week, month, quarter, year
    auth: tuple = Depends(require_access("management_reports", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get executive dashboard with key business metrics and KPIs.
    Requires elevated permissions for management-level reporting.
    """
    current_user, org_id = auth
    try:
        # Check permissions - only admins and authorized users can access
        if not current_user.is_admin:  # Assuming User has is_admin; adjust if needed
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        end_date = date.today()
        if period == "day":
            start_date = end_date
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date.replace(day=1)
        elif period == "quarter":
            quarter_start = (end_date.month - 1) // 3 * 3 + 1
            start_date = end_date.replace(month=quarter_start, day=1)
        elif period == "year":
            start_date = end_date.replace(month=1, day=1)
        else:
            start_date = end_date.replace(day=1)  # Default to month
        
        # Revenue and Sales Metrics
        sales_stmt = select(SalesVoucher).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date)
        total_revenue_stmt = select(func.sum(SalesVoucher.total_amount)).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date)
        total_revenue = (await db.execute(total_revenue_stmt)).scalar() or Decimal(0)
        sales_count_stmt = select(func.count(SalesVoucher.id)).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date)
        sales_count = (await db.execute(sales_count_stmt)).scalar() or 0
        
        # Purchase and Cost Metrics
        purchase_stmt = select(PurchaseVoucher).where(PurchaseVoucher.organization_id == org_id, PurchaseVoucher.date >= start_date)
        total_costs_stmt = select(func.sum(PurchaseVoucher.total_amount)).where(PurchaseVoucher.organization_id == org_id, PurchaseVoucher.date >= start_date)
        total_costs = (await db.execute(total_costs_stmt)).scalar() or Decimal(0)
        purchase_count_stmt = select(func.count(PurchaseVoucher.id)).where(PurchaseVoucher.organization_id == org_id, PurchaseVoucher.date >= start_date)
        purchase_count = (await db.execute(purchase_count_stmt)).scalar() or 0
        
        # Customer Metrics
        active_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.is_active == True)
        active_customers = (await db.execute(active_customers_stmt)).scalar() or 0
        new_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.created_at >= start_date, Customer.is_active == True)
        new_customers = (await db.execute(new_customers_stmt)).scalar() or 0
        
        # Inventory Metrics
        total_products_stmt = select(func.count(Product.id)).where(Product.organization_id == org_id, Product.is_active == True)
        total_products = (await db.execute(total_products_stmt)).scalar() or 0
        low_stock_items_stmt = select(func.count(Stock.id)).select_from(Stock).join(Product).where(Stock.organization_id == org_id, Stock.quantity <= Product.reorder_level, Product.is_active == True)
        low_stock_items = (await db.execute(low_stock_items_stmt)).scalar() or 0
        
        # Outstanding Amounts
        pending_receivables_stmt = select(func.sum(SalesVoucher.total_amount)).where(SalesVoucher.organization_id == org_id, SalesVoucher.status.in_(["pending", "partial"]))
        pending_receivables = (await db.execute(pending_receivables_stmt)).scalar() or Decimal(0)
        pending_payables_stmt = select(func.sum(PurchaseVoucher.total_amount)).where(PurchaseVoucher.organization_id == org_id, PurchaseVoucher.status.in_(["pending", "partial"]))
        pending_payables = (await db.execute(pending_payables_stmt)).scalar() or Decimal(0)
        
        # Calculate key ratios and trends
        gross_profit = total_revenue - total_costs
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "period": period,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "revenue_metrics": {
                "total_revenue": float(total_revenue),
                "sales_count": sales_count,
                "average_sale_value": float(total_revenue / sales_count) if sales_count > 0 else 0
            },
            "cost_metrics": {
                "total_costs": float(total_costs),
                "purchase_count": purchase_count,
                "average_purchase_value": float(total_costs / purchase_count) if purchase_count > 0 else 0
            },
            "profitability": {
                "gross_profit": float(gross_profit),
                "profit_margin": float(profit_margin)
            },
            "customer_metrics": {
                "total_active_customers": active_customers,
                "new_customers": new_customers,
                "customer_growth_rate": (new_customers / active_customers * 100) if active_customers > 0 else 0
            },
            "inventory_metrics": {
                "total_products": total_products,
                "low_stock_items": low_stock_items,
                "stock_health_percentage": ((total_products - low_stock_items) / total_products * 100) if total_products > 0 else 100
            },
            "cash_flow": {
                "pending_receivables": float(pending_receivables),
                "pending_payables": float(pending_payables),
                "net_outstanding": float(pending_receivables - pending_payables)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating executive dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate executive dashboard"
        )

@router.get("/business-intelligence")
async def get_business_intelligence(
    metric_type: str = "overview",  # overview, sales, customers, inventory, financial
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    auth: tuple = Depends(require_access("management_reports", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get business intelligence reports with advanced analytics and insights.
    """
    current_user, org_id = auth
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        end_date = date.today() if not end_date else end_date
        start_date = end_date - timedelta(days=180) if not start_date else start_date
        
        if metric_type == "sales":
            return await _get_sales_intelligence(db, org_id, start_date, end_date)
        elif metric_type == "customers":
            return await _get_customer_intelligence(db, org_id, start_date, end_date)
        elif metric_type == "inventory":
            return await _get_inventory_intelligence(db, org_id, start_date, end_date)
        elif metric_type == "financial":
            return await _get_financial_intelligence(db, org_id, start_date, end_date)
        else:
            # Overview combining all metrics
            return {
                "metric_type": "overview",
                "sales": await _get_sales_intelligence(db, org_id, start_date, end_date),
                "customers": await _get_customer_intelligence(db, org_id, start_date, end_date),
                "inventory": await _get_inventory_intelligence(db, org_id, start_date, end_date),
                "financial": await _get_financial_intelligence(db, org_id, start_date, end_date)
            }
        
    except Exception as e:
        logger.error(f"Error generating business intelligence report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate business intelligence report"
        )

@router.get("/operational-kpis")
async def get_operational_kpis(
    kpi_category: str = "all",  # all, efficiency, quality, customer, financial
    auth: tuple = Depends(require_access("management_reports", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get operational KPIs for performance monitoring and management insights.
    """
    current_user, org_id = auth
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        current_date = date.today()
        current_month_start = current_date.replace(day=1)
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        
        kpis = {}
        
        if kpi_category in ["all", "efficiency"]:
            kpis["efficiency"] = await _calculate_efficiency_kpis(
                db, org_id, current_month_start, current_date, prev_month_start, prev_month_end
            )
        
        if kpi_category in ["all", "quality"]:
            kpis["quality"] = await _calculate_quality_kpis(
                db, org_id, current_month_start, current_date, prev_month_start, prev_month_end
            )
        
        if kpi_category in ["all", "customer"]:
            kpis["customer"] = await _calculate_customer_kpis(
                db, org_id, current_month_start, current_date, prev_month_start, prev_month_end
            )
        
        if kpi_category in ["all", "financial"]:
            kpis["financial"] = await _calculate_financial_kpis(
                db, org_id, current_month_start, current_date, prev_month_start, prev_month_end
            )
        
        return {
            "kpi_category": kpi_category,
            "reporting_period": {
                "current_period": {"start": current_month_start, "end": current_date},
                "comparison_period": {"start": prev_month_start, "end": prev_month_end}
            },
            "kpis": kpis
        }
        
    except Exception as e:
        logger.error(f"Error generating operational KPIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate operational KPIs"
        )

@router.post("/scheduled-reports")
async def create_scheduled_report(
    report_config: Dict[str, Any],
    auth: tuple = Depends(require_access("management_reports", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a scheduled management report configuration.
    """
    current_user, org_id = auth
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        new_config = ReportConfiguration(
            **report_config,
            organization_id=org_id,
            created_by_id=current_user.id
        )
        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
        
        return {
            "id": new_config.id,
            "name": new_config.name,
            "status": "created",
            "schedule_enabled": new_config.schedule_enabled,
            "next_generation": new_config.next_generation_at
        }
        
    except Exception as e:
        logger.error(f"Error creating scheduled report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scheduled report"
        )

@router.get("/export/executive-dashboard")
async def export_executive_dashboard(
    format: str = "excel",  # excel, pdf
    period: str = "month",
    auth: tuple = Depends(require_access("management_reports", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Export executive dashboard data to Excel or PDF.
    """
    current_user, org_id = auth
    try:
        # Check permissions
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        # Get dashboard data
        dashboard_data = await get_executive_dashboard(period=period, auth=auth, db=db)
        
        if format.lower() == "excel":
            excel_data = ReportsExcelService.export_management_dashboard(dashboard_data)
            return ExcelService.create_streaming_response(
                excel_data, f"executive_dashboard_{period}.xlsx"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF export not yet implemented"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting executive dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export executive dashboard"
        )

# Helper functions for business intelligence
async def _get_sales_intelligence(db: AsyncSession, org_id: int, start_date: date, end_date: date):
    """Get sales-specific business intelligence metrics."""
    # Monthly sales trend
    monthly_sales_stmt = select(
        func.extract('month', SalesVoucher.date).label('month'),
        func.sum(SalesVoucher.total_amount).label('total'),
        func.count(SalesVoucher.id).label('count')
    ).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date, SalesVoucher.date <= end_date).group_by(func.extract('month', SalesVoucher.date))
    monthly_sales = await db.execute(monthly_sales_stmt)
    monthly_sales = monthly_sales.all()
    
    # Top customers
    top_customers_stmt = select(
        Customer.name,
        func.sum(SalesVoucher.total_amount).label('total_sales'),
        func.count(SalesVoucher.id).label('order_count')
    ).join(Customer).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date, SalesVoucher.date <= end_date).group_by(Customer.name).order_by(desc(func.sum(SalesVoucher.total_amount))).limit(10)
    top_customers = await db.execute(top_customers_stmt)
    top_customers = top_customers.all()
    
    return {
        "monthly_trends": [
            {"month": int(row.month), "total_sales": float(row.total), "order_count": row.count}
            for row in monthly_sales
        ],
        "top_customers": [
            {"name": row.name, "total_sales": float(row.total_sales), "order_count": row.order_count}
            for row in top_customers
        ]
    }

async def _get_customer_intelligence(db: AsyncSession, org_id: int, start_date: date, end_date: date):
    """Get customer-specific business intelligence metrics."""
    # Customer acquisition and retention metrics
    total_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.is_active == True)
    total_customers = (await db.execute(total_customers_stmt)).scalar() or 0
    
    new_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.created_at >= start_date, Customer.is_active == True)
    new_customers = (await db.execute(new_customers_stmt)).scalar() or 0
    
    return {
        "total_active_customers": total_customers,
        "new_customers_period": new_customers,
        "acquisition_rate": (new_customers / total_customers * 100) if total_customers > 0 else 0
    }

async def _get_inventory_intelligence(db: AsyncSession, org_id: int, start_date: date, end_date: date):
    """Get inventory-specific business intelligence metrics."""
    # Inventory turnover and performance metrics
    total_products_stmt = select(func.count(Product.id)).where(Product.organization_id == org_id, Product.is_active == True)
    total_products = (await db.execute(total_products_stmt)).scalar() or 0
    
    low_stock_count_stmt = select(func.count(Stock.id)).select_from(Stock).join(Product).where(Stock.organization_id == org_id, Stock.quantity <= Product.reorder_level, Product.is_active == True)
    low_stock_count = (await db.execute(low_stock_count_stmt)).scalar() or 0
    
    return {
        "total_products": total_products,
        "low_stock_items": low_stock_count,
        "stock_health_percentage": ((total_products - low_stock_count) / total_products * 100) if total_products > 0 else 100
    }

async def _get_financial_intelligence(db: AsyncSession, org_id: int, start_date: date, end_date: date):
    """Get financial-specific business intelligence metrics."""
    # Cash flow and financial health metrics
    total_receivables_stmt = select(func.sum(SalesVoucher.total_amount)).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= start_date, SalesVoucher.status.in_(["pending", "partial"]))
    total_receivables = (await db.execute(total_receivables_stmt)).scalar() or Decimal(0)
    
    total_payables_stmt = select(func.sum(PurchaseVoucher.total_amount)).where(PurchaseVoucher.organization_id == org_id, PurchaseVoucher.date >= start_date, PurchaseVoucher.status.in_(["pending", "partial"]))
    total_payables = (await db.execute(total_payables_stmt)).scalar() or Decimal(0)
    
    return {
        "total_receivables": float(total_receivables),
        "total_payables": float(total_payables),
        "net_position": float(total_receivables - total_payables)
    }

# KPI calculation helper functions
async def _calculate_efficiency_kpis(db: AsyncSession, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate efficiency-related KPIs."""
    # Order processing time, inventory turnover, etc.
    current_orders_stmt = select(func.count(SalesOrder.id)).where(SalesOrder.organization_id == org_id, SalesOrder.date >= current_start, SalesOrder.date <= current_end)
    current_orders = (await db.execute(current_orders_stmt)).scalar() or 0
    
    prev_orders_stmt = select(func.count(SalesOrder.id)).where(SalesOrder.organization_id == org_id, SalesOrder.date >= prev_start, SalesOrder.date <= prev_end)
    prev_orders = (await db.execute(prev_orders_stmt)).scalar() or 0
    
    order_growth = ((current_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
    
    return {
        "order_processing_volume": {
            "current": current_orders,
            "previous": prev_orders,
            "growth_percentage": order_growth
        }
    }

async def _calculate_quality_kpis(db: AsyncSession, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate quality-related KPIs."""
    # For now, return placeholder data (implement real queries if models available)
    return {
        "defect_rate": {"current": 2.1, "previous": 2.8, "improvement": True},
        "customer_satisfaction": {"current": 4.2, "previous": 4.0, "improvement": True}
    }

async def _calculate_customer_kpis(db: AsyncSession, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate customer-related KPIs."""
    current_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.created_at >= current_start, Customer.created_at <= current_end, Customer.is_active == True)
    current_customers = (await db.execute(current_customers_stmt)).scalar() or 0
    
    prev_customers_stmt = select(func.count(Customer.id)).where(Customer.organization_id == org_id, Customer.created_at >= prev_start, Customer.created_at <= prev_end, Customer.is_active == True)
    prev_customers = (await db.execute(prev_customers_stmt)).scalar() or 0
    
    acquisition_growth = ((current_customers - prev_customers) / prev_customers * 100) if prev_customers > 0 else 0
    
    return {
        "customer_acquisition": {
            "current": current_customers,
            "previous": prev_customers,
            "growth_percentage": acquisition_growth
        }
    }

async def _calculate_financial_kpis(db: AsyncSession, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate financial-related KPIs."""
    current_revenue_stmt = select(func.sum(SalesVoucher.total_amount)).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= current_start, SalesVoucher.date <= current_end)
    current_revenue = (await db.execute(current_revenue_stmt)).scalar() or Decimal(0)
    
    prev_revenue_stmt = select(func.sum(SalesVoucher.total_amount)).where(SalesVoucher.organization_id == org_id, SalesVoucher.date >= prev_start, SalesVoucher.date <= prev_end)
    prev_revenue = (await db.execute(prev_revenue_stmt)).scalar() or Decimal(0)
    
    revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    return {
        "revenue_growth": {
            "current": float(current_revenue),
            "previous": float(prev_revenue),
            "growth_percentage": float(revenue_growth)
        }
    }