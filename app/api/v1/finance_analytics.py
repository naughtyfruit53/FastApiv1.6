# app/api/v1/finance_analytics.py
"""
Finance Analytics API endpoints - Financial reporting, KPIs, and dashboards
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, case, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models import (
    User, Organization, ChartOfAccounts, GeneralLedger, CostCenter,
    BankAccount, AccountsPayable, AccountsReceivable, FinancialKPI,
    FinancialStatement
)
from app.schemas.erp import (
    FinancialStatementResponse, CashFlowResponse, BalanceSheetResponse,
    ProfitAndLossResponse, TrialBalanceResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class FinanceAnalyticsService:
    """Service class for finance analytics operations"""
    
    @staticmethod
    def calculate_financial_ratios(db: Session, organization_id: int, as_of_date: date = None) -> Dict[str, float]:
        """Calculate key financial ratios"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Get account balances
        asset_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type == 'asset'
        ).all()
        
        liability_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type == 'liability'
        ).all()
        
        total_assets = sum(acc.current_balance for acc in asset_accounts)
        total_liabilities = sum(acc.current_balance for acc in liability_accounts)
        
        # Current assets vs current liabilities (simplified)
        current_assets = total_assets * 0.6  # Assuming 60% are current assets
        current_liabilities = total_liabilities * 0.7  # Assuming 70% are current liabilities
        
        ratios = {
            "current_ratio": float(current_assets / current_liabilities) if current_liabilities > 0 else 0,
            "debt_to_equity": float(total_liabilities / (total_assets - total_liabilities)) if (total_assets - total_liabilities) > 0 else 0,
            "working_capital": float(current_assets - current_liabilities),
            "total_assets": float(total_assets),
            "total_liabilities": float(total_liabilities),
            "total_equity": float(total_assets - total_liabilities)
        }
        
        return ratios


# Financial Analytics Endpoints
@router.get("/analytics/dashboard")
async def get_finance_analytics_dashboard(
    period_days: int = Query(30, description="Number of days for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get comprehensive finance analytics dashboard"""
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    # Financial ratios
    ratios = FinanceAnalyticsService.calculate_financial_ratios(db, organization_id)
    
    # Cash flow analysis
    cash_inflow = db.query(func.sum(GeneralLedger.credit_amount)).filter(
        GeneralLedger.organization_id == organization_id,
        GeneralLedger.transaction_date.between(start_date, end_date),
        GeneralLedger.account_id.in_(
            db.query(ChartOfAccounts.id).filter(
                ChartOfAccounts.organization_id == organization_id,
                ChartOfAccounts.account_type.in_(['bank', 'cash'])
            )
        )
    ).scalar() or 0
    
    cash_outflow = db.query(func.sum(GeneralLedger.debit_amount)).filter(
        GeneralLedger.organization_id == organization_id,
        GeneralLedger.transaction_date.between(start_date, end_date),
        GeneralLedger.account_id.in_(
            db.query(ChartOfAccounts.id).filter(
                ChartOfAccounts.organization_id == organization_id,
                ChartOfAccounts.account_type.in_(['bank', 'cash'])
            )
        )
    ).scalar() or 0
    
    # AP/AR aging
    overdue_ap = db.query(func.sum(AccountsPayable.outstanding_amount)).filter(
        AccountsPayable.organization_id == organization_id,
        AccountsPayable.due_date < date.today(),
        AccountsPayable.payment_status == 'pending'
    ).scalar() or 0
    
    overdue_ar = db.query(func.sum(AccountsReceivable.outstanding_amount)).filter(
        AccountsReceivable.organization_id == organization_id,
        AccountsReceivable.due_date < date.today(),
        AccountsReceivable.payment_status == 'pending'
    ).scalar() or 0
    
    # Cost center performance
    cost_center_performance = db.query(
        CostCenter.cost_center_name,
        CostCenter.budget_amount,
        CostCenter.actual_amount,
        ((CostCenter.actual_amount - CostCenter.budget_amount) / CostCenter.budget_amount * 100).label('variance_percent')
    ).filter(
        CostCenter.organization_id == organization_id,
        CostCenter.is_active == True
    ).all()
    
    # Recent KPI trends
    recent_kpis = db.query(FinancialKPI).filter(
        FinancialKPI.organization_id == organization_id,
        FinancialKPI.period_end.between(start_date, end_date)
    ).order_by(desc(FinancialKPI.period_end)).limit(10).all()
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "financial_ratios": ratios,
        "cash_flow": {
            "inflow": float(cash_inflow),
            "outflow": float(cash_outflow),
            "net_flow": float(cash_inflow - cash_outflow)
        },
        "accounts_aging": {
            "overdue_payables": float(overdue_ap),
            "overdue_receivables": float(overdue_ar)
        },
        "cost_centers": [
            {
                "name": cc.cost_center_name,
                "budget": float(cc.budget_amount),
                "actual": float(cc.actual_amount),
                "variance_percent": float(cc.variance_percent) if cc.variance_percent else 0
            }
            for cc in cost_center_performance
        ],
        "recent_kpis": [
            {
                "code": kpi.kpi_code,
                "name": kpi.kpi_name,
                "category": kpi.kpi_category,
                "value": float(kpi.kpi_value),
                "target": float(kpi.target_value) if kpi.target_value else None,
                "variance": float(kpi.variance_percentage) if kpi.variance_percentage else None,
                "period_end": kpi.period_end
            }
            for kpi in recent_kpis
        ]
    }


@router.get("/analytics/cash-flow-forecast")
async def get_cash_flow_forecast(
    forecast_days: int = Query(90, description="Number of days to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get cash flow forecast"""
    today = date.today()
    forecast_end = today + timedelta(days=forecast_days)
    
    # Get current cash position
    current_cash = db.query(func.sum(BankAccount.current_balance)).filter(
        BankAccount.organization_id == organization_id,
        BankAccount.is_active == True
    ).scalar() or 0
    
    # Get expected receivables (by due date)
    expected_receivables = db.query(
        AccountsReceivable.due_date,
        func.sum(AccountsReceivable.outstanding_amount).label('amount')
    ).filter(
        AccountsReceivable.organization_id == organization_id,
        AccountsReceivable.payment_status == 'pending',
        AccountsReceivable.due_date.between(today, forecast_end)
    ).group_by(AccountsReceivable.due_date).all()
    
    # Get expected payables (by due date)
    expected_payables = db.query(
        AccountsPayable.due_date,
        func.sum(AccountsPayable.outstanding_amount).label('amount')
    ).filter(
        AccountsPayable.organization_id == organization_id,
        AccountsPayable.payment_status == 'pending',
        AccountsPayable.due_date.between(today, forecast_end)
    ).group_by(AccountsPayable.due_date).all()
    
    # Create daily forecast
    forecast_data = []
    running_balance = current_cash
    
    for i in range(forecast_days + 1):
        forecast_date = today + timedelta(days=i)
        
        # Find receivables for this date
        receivables = next((r.amount for r in expected_receivables if r.due_date == forecast_date), 0)
        
        # Find payables for this date
        payables = next((p.amount for p in expected_payables if p.due_date == forecast_date), 0)
        
        running_balance += receivables - payables
        
        forecast_data.append({
            "date": forecast_date,
            "receivables": float(receivables),
            "payables": float(payables),
            "net_flow": float(receivables - payables),
            "running_balance": float(running_balance)
        })
    
    return {
        "current_cash": float(current_cash),
        "forecast_period": {"start": today, "end": forecast_end},
        "forecast_data": forecast_data,
        "summary": {
            "total_expected_receivables": float(sum(r.amount for r in expected_receivables)),
            "total_expected_payables": float(sum(p.amount for p in expected_payables)),
            "projected_ending_balance": running_balance
        }
    }


@router.get("/analytics/profit-loss-trend")
async def get_profit_loss_trend(
    months: int = Query(12, description="Number of months for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get profit and loss trend analysis"""
    end_date = date.today()
    start_date = end_date.replace(month=1, day=1) if months >= 12 else end_date - timedelta(days=months * 30)
    
    # Get monthly P&L data
    monthly_data = db.query(
        extract('year', GeneralLedger.transaction_date).label('year'),
        extract('month', GeneralLedger.transaction_date).label('month'),
        func.sum(
            case(
                (ChartOfAccounts.account_type == 'income', GeneralLedger.credit_amount),
                else_=0
            )
        ).label('income'),
        func.sum(
            case(
                (ChartOfAccounts.account_type == 'expense', GeneralLedger.debit_amount),
                else_=0
            )
        ).label('expenses')
    ).join(ChartOfAccounts).filter(
        GeneralLedger.organization_id == organization_id,
        GeneralLedger.transaction_date.between(start_date, end_date)
    ).group_by(
        extract('year', GeneralLedger.transaction_date),
        extract('month', GeneralLedger.transaction_date)
    ).order_by(
        extract('year', GeneralLedger.transaction_date),
        extract('month', GeneralLedger.transaction_date)
    ).all()
    
    trend_data = [
        {
            "period": f"{int(row.year)}-{int(row.month):02d}",
            "income": float(row.income),
            "expenses": float(row.expenses),
            "net_profit": float(row.income - row.expenses),
            "profit_margin": float((row.income - row.expenses) / row.income * 100) if row.income > 0 else 0
        }
        for row in monthly_data
    ]
    
    # Calculate totals and averages
    total_income = sum(d["income"] for d in trend_data)
    total_expenses = sum(d["expenses"] for d in trend_data)
    avg_monthly_profit = sum(d["net_profit"] for d in trend_data) / len(trend_data) if trend_data else 0
    
    return {
        "period": {"start": start_date, "end": end_date},
        "trend_data": trend_data,
        "summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_net_profit": total_income - total_expenses,
            "average_monthly_profit": avg_monthly_profit,
            "overall_profit_margin": (total_income - total_expenses) / total_income * 100 if total_income > 0 else 0
        }
    }


@router.get("/analytics/expense-breakdown")
async def get_expense_breakdown(
    period_days: int = Query(30, description="Number of days for analysis"),
    group_by: str = Query("account", description="Group by: account, cost_center, or category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get expense breakdown analysis"""
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    if group_by == "account":
        # Group by account
        expense_data = db.query(
            ChartOfAccounts.account_name,
            ChartOfAccounts.account_code,
            func.sum(GeneralLedger.debit_amount).label('total_amount')
        ).join(GeneralLedger).filter(
            GeneralLedger.organization_id == organization_id,
            ChartOfAccounts.account_type == 'expense',
            GeneralLedger.transaction_date.between(start_date, end_date)
        ).group_by(
            ChartOfAccounts.account_name,
            ChartOfAccounts.account_code
        ).order_by(desc('total_amount')).all()
        
        breakdown = [
            {
                "category": row.account_name,
                "code": row.account_code,
                "amount": float(row.total_amount)
            }
            for row in expense_data
        ]
        
    elif group_by == "cost_center":
        # Group by cost center
        expense_data = db.query(
            CostCenter.cost_center_name,
            CostCenter.cost_center_code,
            func.sum(GeneralLedger.debit_amount).label('total_amount')
        ).join(GeneralLedger).filter(
            GeneralLedger.organization_id == organization_id,
            GeneralLedger.transaction_date.between(start_date, end_date)
        ).group_by(
            CostCenter.cost_center_name,
            CostCenter.cost_center_code
        ).order_by(desc('total_amount')).all()
        
        breakdown = [
            {
                "category": row.cost_center_name,
                "code": row.cost_center_code,
                "amount": float(row.total_amount)
            }
            for row in expense_data
        ]
    
    else:
        # Default to account type grouping
        breakdown = [{"category": "No breakdown available", "code": "", "amount": 0}]
    
    total_expenses = sum(item["amount"] for item in breakdown)
    
    # Add percentages
    for item in breakdown:
        item["percentage"] = (item["amount"] / total_expenses * 100) if total_expenses > 0 else 0
    
    return {
        "period": {"start": start_date, "end": end_date},
        "group_by": group_by,
        "breakdown": breakdown,
        "total_expenses": total_expenses
    }


@router.get("/analytics/kpi-trends")
async def get_kpi_trends(
    kpi_codes: List[str] = Query(None, description="List of KPI codes to analyze"),
    months: int = Query(6, description="Number of months for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get KPI trend analysis"""
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)
    
    query = db.query(FinancialKPI).filter(
        FinancialKPI.organization_id == organization_id,
        FinancialKPI.period_end.between(start_date, end_date)
    )
    
    if kpi_codes:
        query = query.filter(FinancialKPI.kpi_code.in_(kpi_codes))
    
    kpis = query.order_by(FinancialKPI.kpi_code, FinancialKPI.period_end).all()
    
    # Group by KPI code
    kpi_trends = {}
    for kpi in kpis:
        if kpi.kpi_code not in kpi_trends:
            kpi_trends[kpi.kpi_code] = {
                "kpi_name": kpi.kpi_name,
                "kpi_category": kpi.kpi_category,
                "data_points": []
            }
        
        kpi_trends[kpi.kpi_code]["data_points"].append({
            "period_end": kpi.period_end,
            "value": float(kpi.kpi_value),
            "target": float(kpi.target_value) if kpi.target_value else None,
            "variance": float(kpi.variance_percentage) if kpi.variance_percentage else None
        })
    
    return {
        "period": {"start": start_date, "end": end_date},
        "kpi_trends": kpi_trends
    }