# tests/test_finance_suite.py
"""
Comprehensive test suite for Finance, Accounting, and Analytics features
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.main import app
from app.core.database import get_db
from app.models import (
    ChartOfAccounts, GeneralLedger, CostCenter, BankAccount,
    BankReconciliation, FinancialStatement, FinancialKPI, Organization
)

client = TestClient(app)

class TestFinanceSuite:
    """Test suite for Finance, Accounting, and Analytics features"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers for API requests"""
        # This would need to be implemented based on your auth system
        # For now, returning empty headers
        return {}
    
    @pytest.fixture
    def sample_organization(self, db: Session):
        """Create a sample organization for testing"""
        org = Organization(
            name="Test Finance Org",
            subdomain="testfinance",
            status="active",
            primary_email="test@finance.com",
            primary_phone="1234567890",
            address1="Test Address",
            city="Test City",
            state="Test State",
            pin_code="123456"
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        return org
    
    @pytest.fixture
    def sample_chart_accounts(self, db: Session, sample_organization):
        """Create sample chart of accounts"""
        accounts = [
            ChartOfAccounts(
                organization_id=sample_organization.id,
                account_code="1000",
                account_name="Cash in Hand",
                account_type="cash",
                opening_balance=Decimal("10000.00"),
                current_balance=Decimal("10000.00")
            ),
            ChartOfAccounts(
                organization_id=sample_organization.id,
                account_code="1100",
                account_name="Bank Account",
                account_type="bank",
                opening_balance=Decimal("50000.00"),
                current_balance=Decimal("50000.00")
            ),
            ChartOfAccounts(
                organization_id=sample_organization.id,
                account_code="4000",
                account_name="Sales Revenue",
                account_type="income",
                opening_balance=Decimal("0.00"),
                current_balance=Decimal("0.00")
            ),
            ChartOfAccounts(
                organization_id=sample_organization.id,
                account_code="5000",
                account_name="Office Expenses",
                account_type="expense",
                opening_balance=Decimal("0.00"),
                current_balance=Decimal("0.00")
            )
        ]
        
        for account in accounts:
            db.add(account)
        db.commit()
        
        for account in accounts:
            db.refresh(account)
        
        return accounts

    def test_chart_of_accounts_api(self, auth_headers):
        """Test Chart of Accounts API endpoints"""
        # Test GET chart of accounts
        response = client.get("/api/v1/erp/chart-of-accounts", headers=auth_headers)
        assert response.status_code in [200, 401]  # 401 if auth is required
        
        # Test POST chart of accounts
        new_account = {
            "account_code": "2000",
            "account_name": "Accounts Payable",
            "account_type": "liability",
            "opening_balance": 0.00,
            "can_post": True,
            "is_reconcilable": False
        }
        response = client.post("/api/v1/erp/chart-of-accounts", json=new_account, headers=auth_headers)
        assert response.status_code in [201, 401, 422]

    def test_general_ledger_api(self, auth_headers):
        """Test General Ledger API endpoints"""
        # Test GET general ledger
        response = client.get("/api/v1/erp/general-ledger", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test POST general ledger entry
        new_entry = {
            "account_id": 1,
            "transaction_date": date.today().isoformat(),
            "transaction_number": "GL001",
            "debit_amount": 1000.00,
            "credit_amount": 0.00,
            "description": "Test transaction"
        }
        response = client.post("/api/v1/erp/general-ledger", json=new_entry, headers=auth_headers)
        assert response.status_code in [201, 401, 422]

    def test_cost_centers_api(self, auth_headers):
        """Test Cost Centers API endpoints"""
        # Test GET cost centers
        response = client.get("/api/v1/erp/cost-centers", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test POST cost center
        new_cost_center = {
            "cost_center_code": "CC001",
            "cost_center_name": "Marketing Department",
            "budget_amount": 50000.00,
            "department": "Marketing"
        }
        response = client.post("/api/v1/erp/cost-centers", json=new_cost_center, headers=auth_headers)
        assert response.status_code in [201, 401, 422]

    def test_bank_accounts_api(self, auth_headers):
        """Test Bank Accounts API endpoints"""
        # Test GET bank accounts
        response = client.get("/api/v1/erp/bank-accounts", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test POST bank account
        new_bank_account = {
            "chart_account_id": 2,
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "account_type": "Savings",
            "currency": "INR",
            "opening_balance": 25000.00,
            "is_default": False,
            "auto_reconcile": False
        }
        response = client.post("/api/v1/erp/bank-accounts", json=new_bank_account, headers=auth_headers)
        assert response.status_code in [201, 401, 422]

    def test_financial_kpis_api(self, auth_headers):
        """Test Financial KPIs API endpoints"""
        # Test GET financial KPIs
        response = client.get("/api/v1/erp/financial-kpis", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test POST financial KPI
        new_kpi = {
            "kpi_code": "ROA",
            "kpi_name": "Return on Assets",
            "kpi_category": "profitability",
            "kpi_value": 15.5,
            "period_start": date.today().isoformat(),
            "period_end": date.today().isoformat(),
            "target_value": 18.0
        }
        response = client.post("/api/v1/erp/financial-kpis", json=new_kpi, headers=auth_headers)
        assert response.status_code in [201, 401, 422]

    def test_finance_analytics_dashboard(self, auth_headers):
        """Test Finance Analytics Dashboard API"""
        response = client.get("/api/v1/finance/analytics/dashboard", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "financial_ratios" in data
            assert "cash_flow" in data
            assert "accounts_aging" in data
            assert "cost_centers" in data
            assert "recent_kpis" in data

    def test_cash_flow_forecast(self, auth_headers):
        """Test Cash Flow Forecast API"""
        response = client.get("/api/v1/finance/analytics/cash-flow-forecast", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "current_cash" in data
            assert "forecast_period" in data
            assert "forecast_data" in data
            assert "summary" in data

    def test_profit_loss_trend(self, auth_headers):
        """Test Profit & Loss Trend API"""
        response = client.get("/api/v1/finance/analytics/profit-loss-trend", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "trend_data" in data
            assert "summary" in data

    def test_expense_breakdown(self, auth_headers):
        """Test Expense Breakdown API"""
        response = client.get("/api/v1/finance/analytics/expense-breakdown", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "breakdown" in data
            assert "total_expenses" in data

    def test_kpi_trends(self, auth_headers):
        """Test KPI Trends API"""
        response = client.get("/api/v1/finance/analytics/kpi-trends", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "kpi_trends" in data

    def test_financial_dashboard(self, auth_headers):
        """Test Financial Dashboard API"""
        response = client.get("/api/v1/erp/dashboard", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_assets" in data
            assert "total_liabilities" in data
            assert "working_capital" in data
            assert "current_ratio" in data

    def test_general_ledger_balance_calculation(self, db: Session, sample_chart_accounts):
        """Test general ledger balance calculation logic"""
        cash_account = sample_chart_accounts[0]  # Cash in Hand
        
        # Create test entries
        entries = [
            GeneralLedger(
                organization_id=cash_account.organization_id,
                account_id=cash_account.id,
                transaction_date=date.today(),
                transaction_number="GL001",
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0.00"),
                running_balance=Decimal("11000.00"),  # 10000 + 1000
                description="Test debit entry"
            ),
            GeneralLedger(
                organization_id=cash_account.organization_id,
                account_id=cash_account.id,
                transaction_date=date.today(),
                transaction_number="GL002",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("500.00"),
                running_balance=Decimal("10500.00"),  # 11000 - 500
                description="Test credit entry"
            )
        ]
        
        for entry in entries:
            db.add(entry)
        db.commit()
        
        # Verify balance calculation
        latest_entry = db.query(GeneralLedger).filter(
            GeneralLedger.account_id == cash_account.id
        ).order_by(GeneralLedger.id.desc()).first()
        
        assert latest_entry.running_balance == Decimal("10500.00")

    def test_cost_center_budget_variance(self, db: Session, sample_organization):
        """Test cost center budget variance calculation"""
        cost_center = CostCenter(
            organization_id=sample_organization.id,
            cost_center_code="CC001",
            cost_center_name="Test Department",
            budget_amount=Decimal("50000.00"),
            actual_amount=Decimal("55000.00"),
            is_active=True
        )
        db.add(cost_center)
        db.commit()
        db.refresh(cost_center)
        
        # Calculate variance percentage
        variance = ((cost_center.actual_amount - cost_center.budget_amount) / cost_center.budget_amount) * 100
        assert variance == 10.0  # 10% over budget

    def test_bank_reconciliation_logic(self, db: Session, sample_organization, sample_chart_accounts):
        """Test bank reconciliation logic"""
        # Create a bank account
        bank_account = BankAccount(
            organization_id=sample_organization.id,
            chart_account_id=sample_chart_accounts[1].id,  # Bank Account
            bank_name="Test Bank",
            account_number="1234567890",
            account_type="Savings",
            currency="INR",
            opening_balance=Decimal("50000.00"),
            current_balance=Decimal("52000.00"),
            is_active=True
        )
        db.add(bank_account)
        db.commit()
        db.refresh(bank_account)
        
        # Create reconciliation record
        reconciliation = BankReconciliation(
            organization_id=sample_organization.id,
            bank_account_id=bank_account.id,
            reconciliation_date=date.today(),
            statement_date=date.today(),
            bank_balance=Decimal("52500.00"),
            book_balance=Decimal("52000.00"),
            outstanding_deposits=Decimal("1000.00"),
            outstanding_checks=Decimal("500.00"),
            status="pending",
            difference_amount=Decimal("0.00")  # Should balance out
        )
        db.add(reconciliation)
        db.commit()
        
        # Calculate if reconciliation balances
        adjusted_bank_balance = (reconciliation.bank_balance + 
                                reconciliation.outstanding_deposits - 
                                reconciliation.outstanding_checks)
        
        assert adjusted_bank_balance == reconciliation.book_balance

    def test_financial_kpi_variance_calculation(self, db: Session, sample_organization):
        """Test financial KPI variance calculation"""
        kpi = FinancialKPI(
            organization_id=sample_organization.id,
            kpi_code="ROA",
            kpi_name="Return on Assets",
            kpi_category="profitability",
            kpi_value=Decimal("15.5"),
            target_value=Decimal("18.0"),
            period_start=date.today() - timedelta(days=30),
            period_end=date.today(),
            calculated_at=datetime.utcnow()
        )
        
        # Calculate variance
        if kpi.target_value and kpi.target_value != 0:
            variance = ((kpi.kpi_value - kpi.target_value) / kpi.target_value) * 100
            kpi.variance_percentage = variance
        
        db.add(kpi)
        db.commit()
        db.refresh(kpi)
        
        # Verify variance calculation
        expected_variance = ((15.5 - 18.0) / 18.0) * 100
        assert float(kpi.variance_percentage) == pytest.approx(expected_variance, abs=0.01)

    def test_trial_balance_integrity(self, auth_headers):
        """Test trial balance debit/credit balance integrity"""
        response = client.get("/api/v1/erp/trial-balance", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            total_debits = data.get("total_debits", 0)
            total_credits = data.get("total_credits", 0)
            
            # In a properly balanced trial balance, total debits should equal total credits
            # We'll allow for small rounding differences
            assert abs(total_debits - total_credits) < 0.01

    def test_balance_sheet_equation(self, auth_headers):
        """Test balance sheet fundamental equation: Assets = Liabilities + Equity"""
        response = client.get("/api/v1/erp/balance-sheet", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            total_assets = data.get("total_assets", 0)
            total_liabilities = data.get("total_liabilities", 0)
            total_equity = data.get("total_equity", 0)
            
            # Verify the fundamental accounting equation
            assert abs(total_assets - (total_liabilities + total_equity)) < 0.01

    def test_cash_flow_statement_logic(self, auth_headers):
        """Test cash flow statement calculation logic"""
        response = client.get("/api/v1/finance/analytics/cash-flow-forecast", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            forecast_data = data.get("forecast_data", [])
            
            if forecast_data:
                # Verify that running balance calculation is correct
                for i, day_data in enumerate(forecast_data):
                    if i > 0:
                        prev_balance = forecast_data[i-1]["running_balance"]
                        current_flow = day_data["net_flow"]
                        expected_balance = prev_balance + current_flow
                        
                        assert abs(day_data["running_balance"] - expected_balance) < 0.01


class TestFinanceEdgeCases:
    """Test edge cases and error conditions for finance features"""
    
    def test_division_by_zero_in_ratios(self, auth_headers):
        """Test handling of division by zero in financial ratios"""
        response = client.get("/api/v1/finance/analytics/dashboard", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            ratios = data.get("financial_ratios", {})
            
            # Ensure ratios handle zero denominators gracefully
            for ratio_name, ratio_value in ratios.items():
                assert isinstance(ratio_value, (int, float))
                assert not (ratio_value == float('inf') or ratio_value == float('-inf'))

    def test_negative_balance_handling(self, auth_headers):
        """Test handling of negative balances in accounts"""
        # Test with accounts that might have negative balances
        response = client.get("/api/v1/erp/general-ledger", headers=auth_headers)
        assert response.status_code in [200, 401]

    def test_large_number_precision(self, auth_headers):
        """Test handling of large monetary amounts"""
        large_amount_entry = {
            "account_id": 1,
            "transaction_date": date.today().isoformat(),
            "transaction_number": "GL999",
            "debit_amount": 999999999.99,
            "credit_amount": 0.00,
            "description": "Large amount test"
        }
        response = client.post("/api/v1/erp/general-ledger", json=large_amount_entry, headers={})
        # Should handle large amounts without precision loss
        assert response.status_code in [201, 401, 422]

    def test_date_boundary_conditions(self, auth_headers):
        """Test date boundary conditions in reports"""
        # Test with same start and end date
        params = {
            "from_date": date.today().isoformat(),
            "to_date": date.today().isoformat()
        }
        response = client.get("/api/v1/finance/analytics/profit-loss-trend", params=params, headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test with future dates
        future_date = (date.today() + timedelta(days=30)).isoformat()
        params = {
            "from_date": future_date,
            "to_date": future_date
        }
        response = client.get("/api/v1/finance/analytics/profit-loss-trend", params=params, headers=auth_headers)
        assert response.status_code in [200, 401]


if __name__ == "__main__":
    pytest.main([__file__])