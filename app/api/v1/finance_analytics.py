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
from app.core.enforcement import require_access
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
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get comprehensive finance analytics dashboard"""
    current_user, organization_id = auth
    
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
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get cash flow forecast"""
    current_user, organization_id = auth
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
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get profit and loss trend analysis"""
    current_user, organization_id = auth
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
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get expense breakdown analysis"""
    current_user, organization_id = auth
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
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get KPI trend analysis"""
    current_user, organization_id = auth
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


@router.get("/analytics/vendor-aging")
async def get_vendor_aging(
    aging_periods: List[int] = Query([30, 60, 90], description="Aging period buckets"),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get vendor aging analysis"""
    current_user, organization_id = auth
    today = date.today()
    
    # Get all outstanding payables
    payables = db.query(AccountsPayable).filter(
        AccountsPayable.organization_id == organization_id,
        AccountsPayable.payment_status.in_(['pending', 'partial'])
    ).all()
    
    # Initialize aging buckets
    aging_buckets = {
        "current": {"amount": 0, "count": 0, "vendors": set()},
    }
    
    for period in aging_periods:
        aging_buckets[f"{period}_days"] = {"amount": 0, "count": 0, "vendors": set()}
    
    aging_buckets["over_90"] = {"amount": 0, "count": 0, "vendors": set()}
    
    # Categorize payables into aging buckets
    for payable in payables:
        if payable.due_date and payable.outstanding_amount:
            days_overdue = (today - payable.due_date).days
            amount = float(payable.outstanding_amount)
            
            if days_overdue <= 0:
                aging_buckets["current"]["amount"] += amount
                aging_buckets["current"]["count"] += 1
                if payable.vendor_id:
                    aging_buckets["current"]["vendors"].add(payable.vendor_id)
            elif days_overdue <= aging_periods[0]:
                bucket_key = f"{aging_periods[0]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if payable.vendor_id:
                    aging_buckets[bucket_key]["vendors"].add(payable.vendor_id)
            elif len(aging_periods) > 1 and days_overdue <= aging_periods[1]:
                bucket_key = f"{aging_periods[1]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if payable.vendor_id:
                    aging_buckets[bucket_key]["vendors"].add(payable.vendor_id)
            elif len(aging_periods) > 2 and days_overdue <= aging_periods[2]:
                bucket_key = f"{aging_periods[2]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if payable.vendor_id:
                    aging_buckets[bucket_key]["vendors"].add(payable.vendor_id)
            else:
                aging_buckets["over_90"]["amount"] += amount
                aging_buckets["over_90"]["count"] += 1
                if payable.vendor_id:
                    aging_buckets["over_90"]["vendors"].add(payable.vendor_id)
    
    # Convert sets to counts
    for bucket in aging_buckets.values():
        bucket["vendors"] = len(bucket["vendors"])
    
    total_outstanding = sum(bucket["amount"] for bucket in aging_buckets.values())
    
    return {
        "as_of_date": today,
        "aging_buckets": aging_buckets,
        "total_outstanding": total_outstanding,
        "summary": {
            "total_vendors": len(payables),
            "total_invoices": len(payables),
            "total_outstanding": total_outstanding
        }
    }


@router.get("/analytics/customer-aging")
async def get_customer_aging(
    aging_periods: List[int] = Query([30, 60, 90], description="Aging period buckets"),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get customer aging analysis"""
    current_user, organization_id = auth
    today = date.today()
    
    # Get all outstanding receivables
    receivables = db.query(AccountsReceivable).filter(
        AccountsReceivable.organization_id == organization_id,
        AccountsReceivable.payment_status.in_(['pending', 'partial'])
    ).all()
    
    # Initialize aging buckets
    aging_buckets = {
        "current": {"amount": 0, "count": 0, "customers": set()},
    }
    
    for period in aging_periods:
        aging_buckets[f"{period}_days"] = {"amount": 0, "count": 0, "customers": set()}
    
    aging_buckets["over_90"] = {"amount": 0, "count": 0, "customers": set()}
    
    # Categorize receivables into aging buckets
    for receivable in receivables:
        if receivable.due_date and receivable.outstanding_amount:
            days_overdue = (today - receivable.due_date).days
            amount = float(receivable.outstanding_amount)
            
            if days_overdue <= 0:
                aging_buckets["current"]["amount"] += amount
                aging_buckets["current"]["count"] += 1
                if receivable.customer_id:
                    aging_buckets["current"]["customers"].add(receivable.customer_id)
            elif days_overdue <= aging_periods[0]:
                bucket_key = f"{aging_periods[0]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if receivable.customer_id:
                    aging_buckets[bucket_key]["customers"].add(receivable.customer_id)
            elif len(aging_periods) > 1 and days_overdue <= aging_periods[1]:
                bucket_key = f"{aging_periods[1]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if receivable.customer_id:
                    aging_buckets[bucket_key]["customers"].add(receivable.customer_id)
            elif len(aging_periods) > 2 and days_overdue <= aging_periods[2]:
                bucket_key = f"{aging_periods[2]}_days"
                aging_buckets[bucket_key]["amount"] += amount
                aging_buckets[bucket_key]["count"] += 1
                if receivable.customer_id:
                    aging_buckets[bucket_key]["customers"].add(receivable.customer_id)
            else:
                aging_buckets["over_90"]["amount"] += amount
                aging_buckets["over_90"]["count"] += 1
                if receivable.customer_id:
                    aging_buckets["over_90"]["customers"].add(receivable.customer_id)
    
    # Convert sets to counts
    for bucket in aging_buckets.values():
        bucket["customers"] = len(bucket["customers"])
    
    total_outstanding = sum(bucket["amount"] for bucket in aging_buckets.values())
    
    return {
        "as_of_date": today,
        "aging_buckets": aging_buckets,
        "total_outstanding": total_outstanding,
        "summary": {
            "total_customers": len(receivables),
            "total_invoices": len(receivables),
            "total_outstanding": total_outstanding
        }
    }


@router.get("/analytics/budgets")
async def get_budgets(
    budget_year: Optional[int] = Query(None, description="Budget year"),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get budget management data"""
    current_user, organization_id = auth
    if not budget_year:
        budget_year = date.today().year
    
    # Get cost centers with budget information
    cost_centers = db.query(CostCenter).filter(
        CostCenter.organization_id == organization_id,
        CostCenter.is_active == True
    ).all()
    
    budget_data = []
    total_budget = Decimal(0)
    total_actual = Decimal(0)
    
    for cc in cost_centers:
        budget_amt = cc.budget_amount or Decimal(0)
        actual_amt = cc.actual_amount or Decimal(0)
        variance = actual_amt - budget_amt
        variance_percent = (variance / budget_amt * 100) if budget_amt > 0 else 0
        
        budget_data.append({
            "cost_center_id": cc.id,
            "cost_center_name": cc.cost_center_name,
            "cost_center_code": cc.cost_center_code,
            "budget_amount": float(budget_amt),
            "actual_amount": float(actual_amt),
            "variance": float(variance),
            "variance_percent": float(variance_percent),
            "status": "over_budget" if variance > 0 else "under_budget" if variance < 0 else "on_track"
        })
        
        total_budget += budget_amt
        total_actual += actual_amt
    
    return {
        "budget_year": budget_year,
        "cost_centers": budget_data,
        "summary": {
            "total_budget": float(total_budget),
            "total_actual": float(total_actual),
            "total_variance": float(total_actual - total_budget),
            "variance_percent": float((total_actual - total_budget) / total_budget * 100) if total_budget > 0 else 0
        }
    }


@router.get("/analytics/expense-analysis")
async def get_expense_analysis(
    period_months: int = Query(6, description="Number of months for analysis"),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get expense analysis by category"""
    current_user, organization_id = auth
    end_date = date.today()
    start_date = end_date - timedelta(days=period_months * 30)
    
    # Get expense accounts
    expense_accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.account_type == 'expense',
        ChartOfAccounts.is_active == True
    ).all()
    
    expense_analysis = []
    total_expenses = Decimal(0)
    
    for account in expense_accounts:
        amount = abs(account.current_balance)
        if amount > 0:
            expense_analysis.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "amount": float(amount),
                "parent_account": account.parent_account_code or "Root"
            })
            total_expenses += amount
    
    # Calculate percentages
    for expense in expense_analysis:
        expense["percentage"] = (expense["amount"] / float(total_expenses) * 100) if total_expenses > 0 else 0
    
    # Sort by amount descending
    expense_analysis.sort(key=lambda x: x["amount"], reverse=True)
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "expenses": expense_analysis,
        "summary": {
            "total_expenses": float(total_expenses),
            "expense_count": len(expense_analysis),
            "top_expense": expense_analysis[0] if expense_analysis else None
        }
    }


@router.get("/analytics/financial-kpis")
async def get_financial_kpis(
    period_months: int = Query(3, description="Number of months for KPI analysis"),
    auth: tuple = Depends(require_access("finance", "read")),
    db: Session = Depends(get_db)
):
    """Get financial KPIs dashboard"""
    current_user, organization_id = auth
    end_date = date.today()
    start_date = end_date - timedelta(days=period_months * 30)
    
    # Get recent KPIs
    kpis = db.query(FinancialKPI).filter(
        FinancialKPI.organization_id == organization_id,
        FinancialKPI.period_end.between(start_date, end_date)
    ).order_by(desc(FinancialKPI.period_end)).all()
    
    kpi_data = []
    for kpi in kpis:
        kpi_data.append({
            "kpi_code": kpi.kpi_code,
            "kpi_name": kpi.kpi_name,
            "kpi_category": kpi.kpi_category,
            "value": float(kpi.kpi_value),
            "target": float(kpi.target_value) if kpi.target_value else None,
            "variance": float(kpi.variance_percentage) if kpi.variance_percentage else None,
            "period_end": kpi.period_end,
            "status": "on_track" if kpi.variance_percentage and abs(kpi.variance_percentage) < 5 else "needs_attention"
        })
    
    # Calculate financial ratios
    ratios = FinanceAnalyticsService.calculate_financial_ratios(db, organization_id)
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "kpis": kpi_data,
        "financial_ratios": ratios,
        "summary": {
            "total_kpis": len(kpi_data),
            "on_track_count": sum(1 for k in kpi_data if k["status"] == "on_track"),
            "needs_attention_count": sum(1 for k in kpi_data if k["status"] == "needs_attention")
        }
    }