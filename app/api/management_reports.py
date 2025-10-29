from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User, Product, Stock, Vendor, Customer, Organization
from app.models.vouchers import (
    PurchaseVoucher, SalesVoucher, PurchaseOrder, SalesOrder,
    PaymentVoucher, ReceiptVoucher
)
from app.models.analytics_models import ReportConfiguration
from app.services.excel_service import ExcelService, ReportsExcelService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/management-reports", tags=["management-reports"])

@router.get("/executive-dashboard")
async def get_executive_dashboard(
    period: str = "month",  # day, week, month, quarter, year
    auth: tuple = Depends(require_access("management_reports", "read")),
    db:  = Depends(get_db)
):
    """
    Get executive dashboard with key business metrics and KPIs.
    Requires elevated permissions for management-level reporting.
    """
    try:
        # Check permissions - only admins and authorized users can access
        if notFalse:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for management reports"
            )        # Calculate date range based on period
        end_date = datetime.now().date()
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
        sales_query = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(SalesVoucher.date >= start_date)
        
        total_revenue = sales_query.with_entities(
            func.sum(SalesVoucher.total_amount)
        ).scalar() or Decimal(0)
        
        sales_count = sales_query.count()
        
        # Purchase and Cost Metrics
        purchase_query = db.query(PurchaseVoucher).filter(PurchaseVoucher.organization_id == org_id).filter(PurchaseVoucher.date >= start_date)
        
        total_costs = purchase_query.with_entities(
            func.sum(PurchaseVoucher.total_amount)
        ).scalar() or Decimal(0)
        
        purchase_count = purchase_query.count()
        
        # Customer Metrics
        active_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(Customer.is_active == True).count()
        
        new_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(
            Customer.created_at >= start_date,
            Customer.is_active == True
        ).count()
        
        # Inventory Metrics
        total_products = db.query(Product).filter(Product.organization_id == org_id).filter(Product.is_active == True).count()
        
        low_stock_items = db.query(Stock).filter(Stock.organization_id == org_id).join(Product).filter(
            Stock.quantity <= Product.reorder_level,
            Product.is_active == True
        ).count()
        
        # Outstanding Amounts
        pending_receivables = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(SalesVoucher.status.in_(["pending", "partial"])).with_entities(
            func.sum(SalesVoucher.total_amount)
        ).scalar() or Decimal(0)
        
        pending_payables = db.query(PurchaseVoucher).filter(PurchaseVoucher.organization_id == org_id).filter(PurchaseVoucher.status.in_(["pending", "partial"])).with_entities(
            func.sum(PurchaseVoucher.total_amount)
        ).scalar() or Decimal(0)
        
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
    db:  = Depends(get_db)
):
    """
    Get business intelligence reports with advanced analytics and insights.
    """
    try:
        # Check permissions
        if notFalse:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for business intelligence reports"
            )        # Default date range to last 6 months if not specified
        if not end_date:
            end_date = datetime.now().date()
        if not start_date:
            start_date = end_date - timedelta(days=180)
        
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
    db:  = Depends(get_db)
):
    """
    Get operational KPIs for performance monitoring and management insights.
    """
    try:
        # Check permissions
        if notFalse:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for operational KPIs"
            )        # Calculate current month and previous month for comparison
        current_date = datetime.now().date()
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
    db:  = Depends(get_db)
):
    """
    Create a scheduled management report configuration.
    """
    try:
        # Check permissions
        if notFalse:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create scheduled reports"
            )        # Create report configuration
        new_config = ReportConfiguration(
            organization_id=org_id,
            name=report_config.get("name", "Management Report"),
            description=report_config.get("description"),
            metric_types=report_config.get("metric_types", ["executive_dashboard"]),
            default_filters=report_config.get("default_filters", {}),
            schedule_enabled=report_config.get("schedule_enabled", False),
            schedule_frequency=report_config.get("schedule_frequency"),
            schedule_time=report_config.get("schedule_time"),
            email_recipients=report_config.get("email_recipients", []),
            email_subject_template=report_config.get("email_subject_template"),
            created_by_id=current_user.id
        )
        
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
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
    db:  = Depends(get_db)
):
    """
    Export executive dashboard data to Excel or PDF.
    """
    try:
        # Check permissions
        if notFalse:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to export management reports"
            )
        
        # Get dashboard data
        dashboard_data = await get_executive_dashboard(period, db, current_user)
        
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
async def _get_sales_intelligence(db: Session, org_id: int, start_date: date, end_date: date):
    """Get sales-specific business intelligence metrics."""
    sales_query = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(
        SalesVoucher.date >= start_date,
        SalesVoucher.date <= end_date
    )
    
    # Monthly sales trend
    monthly_sales = sales_query.with_entities(
        func.extract('month', SalesVoucher.date).label('month'),
        func.sum(SalesVoucher.total_amount).label('total'),
        func.count(SalesVoucher.id).label('count')
    ).group_by(func.extract('month', SalesVoucher.date)).all()
    
    # Top customers
    top_customers = sales_query.join(Customer).with_entities(
        Customer.name,
        func.sum(SalesVoucher.total_amount).label('total_sales'),
        func.count(SalesVoucher.id).label('order_count')
    ).group_by(Customer.name).order_by(desc(func.sum(SalesVoucher.total_amount))).limit(10).all()
    
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


async def _get_customer_intelligence(db: Session, org_id: int, start_date: date, end_date: date):
    """Get customer-specific business intelligence metrics."""
    # Customer acquisition and retention metrics
    total_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(Customer.is_active == True).count()
    
    new_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(
        Customer.created_at >= start_date,
        Customer.is_active == True
    ).count()
    
    return {
        "total_active_customers": total_customers,
        "new_customers_period": new_customers,
        "acquisition_rate": (new_customers / total_customers * 100) if total_customers > 0 else 0
    }


async def _get_inventory_intelligence(db: Session, org_id: int, start_date: date, end_date: date):
    """Get inventory-specific business intelligence metrics."""
    # Inventory turnover and performance metrics
    total_products = db.query(Product).filter(Product.organization_id == org_id).filter(Product.is_active == True).count()
    
    low_stock_count = db.query(Stock).filter(Stock.organization_id == org_id).join(Product).filter(
        Stock.quantity <= Product.reorder_level,
        Product.is_active == True
    ).count()
    
    return {
        "total_products": total_products,
        "low_stock_items": low_stock_count,
        "stock_health_percentage": ((total_products - low_stock_count) / total_products * 100) if total_products > 0 else 100
    }


async def _get_financial_intelligence(db: Session, org_id: int, start_date: date, end_date: date):
    """Get financial-specific business intelligence metrics."""
    # Cash flow and financial health metrics
    total_receivables = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(
        SalesVoucher.date >= start_date,
        SalesVoucher.status.in_(["pending", "partial"])
    ).with_entities(func.sum(SalesVoucher.total_amount)).scalar() or Decimal(0)
    
    total_payables = db.query(PurchaseVoucher).filter(PurchaseVoucher.organization_id == org_id).filter(
        PurchaseVoucher.date >= start_date,
        PurchaseVoucher.status.in_(["pending", "partial"])
    ).with_entities(func.sum(PurchaseVoucher.total_amount)).scalar() or Decimal(0)
    
    return {
        "total_receivables": float(total_receivables),
        "total_payables": float(total_payables),
        "net_position": float(total_receivables - total_payables)
    }


# KPI calculation helper functions
async def _calculate_efficiency_kpis(db: Session, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate efficiency-related KPIs."""
    # Order processing time, inventory turnover, etc.
    current_orders = db.query(SalesOrder).filter(SalesOrder.organization_id == org_id).filter(SalesOrder.date >= current_start, SalesOrder.date <= current_end).count()
    
    prev_orders = db.query(SalesOrder).filter(SalesOrder.organization_id == org_id).filter(SalesOrder.date >= prev_start, SalesOrder.date <= prev_end).count()
    
    order_growth = ((current_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
    
    return {
        "order_processing_volume": {
            "current": current_orders,
            "previous": prev_orders,
            "growth_percentage": order_growth
        }
    }


async def _calculate_quality_kpis(db: Session, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate quality-related KPIs."""
    # For now, return placeholder data
    return {
        "defect_rate": {"current": 2.1, "previous": 2.8, "improvement": True},
        "customer_satisfaction": {"current": 4.2, "previous": 4.0, "improvement": True}
    }


async def _calculate_customer_kpis(db: Session, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate customer-related KPIs."""
    current_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(
        Customer.created_at >= current_start,
        Customer.created_at <= current_end,
        Customer.is_active == True
    ).count()
    
    prev_customers = db.query(Customer).filter(Customer.organization_id == org_id).filter(
        Customer.created_at >= prev_start,
        Customer.created_at <= prev_end,
        Customer.is_active == True
    ).count()
    
    acquisition_growth = ((current_customers - prev_customers) / prev_customers * 100) if prev_customers > 0 else 0
    
    return {
        "customer_acquisition": {
            "current": current_customers,
            "previous": prev_customers,
            "growth_percentage": acquisition_growth
        }
    }


async def _calculate_financial_kpis(db: Session, org_id: int, current_start: date, current_end: date, prev_start: date, prev_end: date):
    """Calculate financial-related KPIs."""
    current_revenue = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(
        SalesVoucher.date >= current_start,
        SalesVoucher.date <= current_end
    ).with_entities(func.sum(SalesVoucher.total_amount)).scalar() or Decimal(0)
    
    prev_revenue = db.query(SalesVoucher).filter(SalesVoucher.organization_id == org_id).filter(
        SalesVoucher.date >= prev_start,
        SalesVoucher.date <= prev_end
    ).with_entities(func.sum(SalesVoucher.total_amount)).scalar() or Decimal(0)
    
    revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    return {
        "revenue_growth": {
            "current": float(current_revenue),
            "previous": float(prev_revenue),
            "growth_percentage": float(revenue_growth)
        }
    }