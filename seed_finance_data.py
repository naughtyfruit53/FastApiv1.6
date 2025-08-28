# seed_finance_data.py
"""
Comprehensive seed data script for Finance, Accounting, and Analytics modules
Creates realistic sample data for demonstration and testing purposes
"""

import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import (
    Organization, ChartOfAccounts, GeneralLedger, CostCenter, 
    BankAccount, BankReconciliation, FinancialStatement, FinancialKPI
)

def create_comprehensive_chart_of_accounts(db, organization_id):
    """Create a comprehensive chart of accounts structure"""
    accounts = [
        # ASSETS (1000-1999)
        # Current Assets (1000-1199)
        {"code": "1000", "name": "Current Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1010", "name": "Cash in Hand", "type": "cash", "is_group": False, "parent": "1000", "opening": 25000},
        {"code": "1020", "name": "Petty Cash", "type": "cash", "is_group": False, "parent": "1000", "opening": 5000},
        {"code": "1100", "name": "Bank Accounts", "type": "bank", "is_group": True, "parent": "1000"},
        {"code": "1110", "name": "HDFC Bank - Current", "type": "bank", "is_group": False, "parent": "1100", "opening": 150000, "reconcilable": True},
        {"code": "1120", "name": "ICICI Bank - Savings", "type": "bank", "is_group": False, "parent": "1100", "opening": 75000, "reconcilable": True},
        {"code": "1130", "name": "SBI Bank - Export", "type": "bank", "is_group": False, "parent": "1100", "opening": 200000, "reconcilable": True},
        {"code": "1200", "name": "Accounts Receivable", "type": "asset", "is_group": True, "parent": "1000"},
        {"code": "1210", "name": "Trade Receivables", "type": "asset", "is_group": False, "parent": "1200", "opening": 180000},
        {"code": "1220", "name": "Other Receivables", "type": "asset", "is_group": False, "parent": "1200", "opening": 25000},
        {"code": "1300", "name": "Inventory", "type": "asset", "is_group": True, "parent": "1000"},
        {"code": "1310", "name": "Raw Materials", "type": "asset", "is_group": False, "parent": "1300", "opening": 120000},
        {"code": "1320", "name": "Finished Goods", "type": "asset", "is_group": False, "parent": "1300", "opening": 95000},
        {"code": "1330", "name": "Work in Progress", "type": "asset", "is_group": False, "parent": "1300", "opening": 35000},
        
        # Fixed Assets (1500-1799)
        {"code": "1500", "name": "Fixed Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1510", "name": "Plant & Machinery", "type": "asset", "is_group": False, "parent": "1500", "opening": 500000},
        {"code": "1520", "name": "Office Equipment", "type": "asset", "is_group": False, "parent": "1500", "opening": 85000},
        {"code": "1530", "name": "Furniture & Fixtures", "type": "asset", "is_group": False, "parent": "1500", "opening": 45000},
        {"code": "1540", "name": "Vehicles", "type": "asset", "is_group": False, "parent": "1500", "opening": 125000},
        {"code": "1550", "name": "Computer Equipment", "type": "asset", "is_group": False, "parent": "1500", "opening": 65000},
        
        # LIABILITIES (2000-2999)
        # Current Liabilities (2000-2199)
        {"code": "2000", "name": "Current Liabilities", "type": "liability", "is_group": True, "parent": None},
        {"code": "2010", "name": "Accounts Payable", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2011", "name": "Trade Payables", "type": "liability", "is_group": False, "parent": "2010", "opening": 95000},
        {"code": "2012", "name": "Other Payables", "type": "liability", "is_group": False, "parent": "2010", "opening": 15000},
        {"code": "2100", "name": "Tax Liabilities", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2110", "name": "GST Payable", "type": "liability", "is_group": False, "parent": "2100", "opening": 18000},
        {"code": "2120", "name": "TDS Payable", "type": "liability", "is_group": False, "parent": "2100", "opening": 8500},
        {"code": "2130", "name": "Income Tax Payable", "type": "liability", "is_group": False, "parent": "2100", "opening": 45000},
        {"code": "2200", "name": "Accrued Expenses", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2210", "name": "Salary Payable", "type": "liability", "is_group": False, "parent": "2200", "opening": 125000},
        {"code": "2220", "name": "Utility Bills Payable", "type": "liability", "is_group": False, "parent": "2200", "opening": 12000},
        
        # Long-term Liabilities (2500-2799)
        {"code": "2500", "name": "Long-term Liabilities", "type": "liability", "is_group": True, "parent": None},
        {"code": "2510", "name": "Bank Loans", "type": "liability", "is_group": False, "parent": "2500", "opening": 350000},
        {"code": "2520", "name": "Equipment Loans", "type": "liability", "is_group": False, "parent": "2500", "opening": 180000},
        
        # EQUITY (3000-3999)
        {"code": "3000", "name": "Equity", "type": "equity", "is_group": True, "parent": None},
        {"code": "3100", "name": "Share Capital", "type": "equity", "is_group": False, "parent": "3000", "opening": 500000},
        {"code": "3200", "name": "Retained Earnings", "type": "equity", "is_group": False, "parent": "3000", "opening": 285000},
        {"code": "3300", "name": "Current Year Earnings", "type": "equity", "is_group": False, "parent": "3000", "opening": 0},
        
        # INCOME (4000-4999)
        {"code": "4000", "name": "Revenue", "type": "income", "is_group": True, "parent": None},
        {"code": "4100", "name": "Sales Revenue", "type": "income", "is_group": True, "parent": "4000"},
        {"code": "4110", "name": "Product Sales", "type": "income", "is_group": False, "parent": "4100", "opening": 0},
        {"code": "4120", "name": "Service Revenue", "type": "income", "is_group": False, "parent": "4100", "opening": 0},
        {"code": "4130", "name": "Consulting Revenue", "type": "income", "is_group": False, "parent": "4100", "opening": 0},
        {"code": "4200", "name": "Other Income", "type": "income", "is_group": True, "parent": "4000"},
        {"code": "4210", "name": "Interest Income", "type": "income", "is_group": False, "parent": "4200", "opening": 0},
        {"code": "4220", "name": "Dividend Income", "type": "income", "is_group": False, "parent": "4200", "opening": 0},
        {"code": "4230", "name": "Miscellaneous Income", "type": "income", "is_group": False, "parent": "4200", "opening": 0},
        
        # EXPENSES (5000-5999)
        {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "is_group": True, "parent": None},
        {"code": "5100", "name": "Material Costs", "type": "expense", "is_group": False, "parent": "5000", "opening": 0},
        {"code": "5200", "name": "Labor Costs", "type": "expense", "is_group": False, "parent": "5000", "opening": 0},
        {"code": "5300", "name": "Manufacturing Overhead", "type": "expense", "is_group": False, "parent": "5000", "opening": 0},
        
        # Operating Expenses (6000-6999)
        {"code": "6000", "name": "Operating Expenses", "type": "expense", "is_group": True, "parent": None},
        {"code": "6100", "name": "Administrative Expenses", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6110", "name": "Salaries & Wages", "type": "expense", "is_group": False, "parent": "6100", "opening": 0},
        {"code": "6120", "name": "Office Rent", "type": "expense", "is_group": False, "parent": "6100", "opening": 0},
        {"code": "6130", "name": "Utilities", "type": "expense", "is_group": False, "parent": "6100", "opening": 0},
        {"code": "6140", "name": "Communication", "type": "expense", "is_group": False, "parent": "6100", "opening": 0},
        {"code": "6150", "name": "Office Supplies", "type": "expense", "is_group": False, "parent": "6100", "opening": 0},
        {"code": "6200", "name": "Sales & Marketing", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6210", "name": "Advertising", "type": "expense", "is_group": False, "parent": "6200", "opening": 0},
        {"code": "6220", "name": "Marketing Events", "type": "expense", "is_group": False, "parent": "6200", "opening": 0},
        {"code": "6230", "name": "Sales Commission", "type": "expense", "is_group": False, "parent": "6200", "opening": 0},
        {"code": "6240", "name": "Travel & Entertainment", "type": "expense", "is_group": False, "parent": "6200", "opening": 0},
        {"code": "6300", "name": "IT & Technology", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6310", "name": "Software Licenses", "type": "expense", "is_group": False, "parent": "6300", "opening": 0},
        {"code": "6320", "name": "Hardware Maintenance", "type": "expense", "is_group": False, "parent": "6300", "opening": 0},
        {"code": "6330", "name": "Internet & Hosting", "type": "expense", "is_group": False, "parent": "6300", "opening": 0},
        {"code": "6400", "name": "Professional Services", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6410", "name": "Legal Fees", "type": "expense", "is_group": False, "parent": "6400", "opening": 0},
        {"code": "6420", "name": "Audit Fees", "type": "expense", "is_group": False, "parent": "6400", "opening": 0},
        {"code": "6430", "name": "Consulting Fees", "type": "expense", "is_group": False, "parent": "6400", "opening": 0},
        {"code": "6500", "name": "Finance Costs", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6510", "name": "Interest Expense", "type": "expense", "is_group": False, "parent": "6500", "opening": 0},
        {"code": "6520", "name": "Bank Charges", "type": "expense", "is_group": False, "parent": "6500", "opening": 0},
        {"code": "6530", "name": "Foreign Exchange Loss", "type": "expense", "is_group": False, "parent": "6500", "opening": 0},
    ]
    
    # Create accounts and maintain parent-child relationships
    created_accounts = {}
    
    # First pass: Create all accounts
    for acc_data in accounts:
        account = ChartOfAccounts(
            organization_id=organization_id,
            account_code=acc_data["code"],
            account_name=acc_data["name"],
            account_type=acc_data["type"],
            is_group=acc_data["is_group"],
            opening_balance=Decimal(str(acc_data.get("opening", 0))),
            current_balance=Decimal(str(acc_data.get("opening", 0))),
            is_reconcilable=acc_data.get("reconcilable", False)
        )
        db.add(account)
        db.flush()  # Get the ID
        created_accounts[acc_data["code"]] = account
    
    # Second pass: Set parent relationships
    for acc_data in accounts:
        if acc_data["parent"]:
            created_accounts[acc_data["code"]].parent_account_id = created_accounts[acc_data["parent"]].id
    
    db.commit()
    return created_accounts

def create_cost_centers(db, organization_id):
    """Create sample cost centers"""
    cost_centers = [
        {"code": "CC001", "name": "Administration", "department": "Admin", "budget": 250000},
        {"code": "CC002", "name": "Sales & Marketing", "department": "Sales", "budget": 180000},
        {"code": "CC003", "name": "Production", "department": "Manufacturing", "budget": 320000},
        {"code": "CC004", "name": "Research & Development", "department": "R&D", "budget": 150000},
        {"code": "CC005", "name": "Quality Control", "department": "QC", "budget": 85000},
        {"code": "CC006", "name": "IT & Technology", "department": "IT", "budget": 120000},
        {"code": "CC007", "name": "Human Resources", "department": "HR", "budget": 95000},
        {"code": "CC008", "name": "Finance & Accounts", "department": "Finance", "budget": 110000},
    ]
    
    created_cost_centers = {}
    for cc_data in cost_centers:
        # Simulate some actual spending (70-110% of budget)
        actual_percentage = random.uniform(0.7, 1.1)
        actual_amount = Decimal(str(cc_data["budget"] * actual_percentage))
        
        cost_center = CostCenter(
            organization_id=organization_id,
            cost_center_code=cc_data["code"],
            cost_center_name=cc_data["name"],
            department=cc_data["department"],
            budget_amount=Decimal(str(cc_data["budget"])),
            actual_amount=actual_amount,
            is_active=True,
            description=f"Cost center for {cc_data['name']} operations"
        )
        db.add(cost_center)
        db.flush()
        created_cost_centers[cc_data["code"]] = cost_center
    
    db.commit()
    return created_cost_centers

def create_bank_accounts(db, organization_id, chart_accounts):
    """Create sample bank accounts"""
    bank_accounts_data = [
        {
            "chart_account": "1110",
            "bank_name": "HDFC Bank",
            "branch_name": "Commercial Street Branch",
            "account_number": "50100123456789",
            "ifsc_code": "HDFC0001234",
            "account_type": "Current",
            "is_default": True
        },
        {
            "chart_account": "1120",
            "bank_name": "ICICI Bank",
            "branch_name": "MG Road Branch",
            "account_number": "602301234567",
            "ifsc_code": "ICIC0006023",
            "account_type": "Savings",
            "is_default": False
        },
        {
            "chart_account": "1130",
            "bank_name": "State Bank of India",
            "branch_name": "Export Department",
            "account_number": "38421234567",
            "ifsc_code": "SBIN0003842",
            "account_type": "Current",
            "is_default": False
        }
    ]
    
    created_bank_accounts = []
    for bank_data in bank_accounts_data:
        chart_account = chart_accounts[bank_data["chart_account"]]
        
        bank_account = BankAccount(
            organization_id=organization_id,
            chart_account_id=chart_account.id,
            bank_name=bank_data["bank_name"],
            branch_name=bank_data["branch_name"],
            account_number=bank_data["account_number"],
            ifsc_code=bank_data["ifsc_code"],
            account_type=bank_data["account_type"],
            currency="INR",
            opening_balance=chart_account.opening_balance,
            current_balance=chart_account.current_balance,
            is_active=True,
            is_default=bank_data["is_default"],
            auto_reconcile=False
        )
        db.add(bank_account)
        db.flush()
        created_bank_accounts.append(bank_account)
    
    db.commit()
    return created_bank_accounts

def create_sample_transactions(db, organization_id, chart_accounts, cost_centers):
    """Create sample general ledger transactions for the past 3 months"""
    transactions = []
    start_date = date.today() - timedelta(days=90)
    
    # Sample transaction types with realistic amounts
    transaction_templates = [
        # Sales transactions
        {"debit_account": "1210", "credit_account": "4110", "amount_range": (15000, 75000), "desc": "Product sales", "frequency": 15},
        {"debit_account": "1210", "credit_account": "4120", "amount_range": (8000, 35000), "desc": "Service revenue", "frequency": 10},
        
        # Cash collections
        {"debit_account": "1110", "credit_account": "1210", "amount_range": (10000, 60000), "desc": "Customer payment received", "frequency": 12},
        {"debit_account": "1120", "credit_account": "1210", "amount_range": (5000, 40000), "desc": "Customer payment received", "frequency": 8},
        
        # Purchase transactions
        {"debit_account": "5100", "credit_account": "2011", "amount_range": (8000, 45000), "desc": "Material purchase", "frequency": 20},
        {"debit_account": "1310", "credit_account": "2011", "amount_range": (12000, 65000), "desc": "Raw material purchase", "frequency": 15},
        
        # Expense transactions
        {"debit_account": "6110", "credit_account": "1110", "amount_range": (85000, 95000), "desc": "Salary payment", "frequency": 1, "monthly": True},
        {"debit_account": "6120", "credit_account": "1110", "amount_range": (25000, 35000), "desc": "Office rent", "frequency": 1, "monthly": True},
        {"debit_account": "6130", "credit_account": "1110", "amount_range": (8000, 15000), "desc": "Utility bills", "frequency": 1, "monthly": True},
        {"debit_account": "6140", "credit_account": "1110", "amount_range": (3000, 8000), "desc": "Communication expenses", "frequency": 1, "monthly": True},
        {"debit_account": "6210", "credit_account": "1110", "amount_range": (5000, 25000), "desc": "Advertising expenses", "frequency": 5},
        {"debit_account": "6240", "credit_account": "1110", "amount_range": (2000, 12000), "desc": "Travel expenses", "frequency": 8},
        {"debit_account": "6310", "credit_account": "1110", "amount_range": (15000, 45000), "desc": "Software licenses", "frequency": 2},
        {"debit_account": "6520", "credit_account": "1110", "amount_range": (500, 2500), "desc": "Bank charges", "frequency": 6},
        {"debit_account": "6510", "credit_account": "1110", "amount_range": (8000, 15000), "desc": "Interest payment", "frequency": 1, "monthly": True},
    ]
    
    transaction_counter = 1
    cost_center_codes = list(cost_centers.keys())
    
    for days_ago in range(90):
        transaction_date = start_date + timedelta(days=days_ago)
        
        for template in transaction_templates:
            # Determine if transaction should occur on this day
            should_create = False
            if template.get("monthly"):
                # Monthly transactions on the 1st of each month
                if transaction_date.day == 1:
                    should_create = True
            else:
                # Random transactions based on frequency
                if random.random() < template["frequency"] / 30:  # Convert monthly frequency to daily probability
                    should_create = True
            
            if should_create:
                amount = Decimal(str(random.uniform(*template["amount_range"])))
                amount = amount.quantize(Decimal('0.01'))
                
                debit_account = chart_accounts[template["debit_account"]]
                credit_account = chart_accounts[template["credit_account"]]
                cost_center = cost_centers[random.choice(cost_center_codes)]
                
                # Create debit entry
                debit_entry = GeneralLedger(
                    organization_id=organization_id,
                    account_id=debit_account.id,
                    transaction_date=transaction_date,
                    transaction_number=f"GL{transaction_counter:06d}",
                    reference_type="AUTO",
                    reference_number=f"TXN{transaction_counter}",
                    debit_amount=amount,
                    credit_amount=Decimal('0.00'),
                    running_balance=Decimal('0.00'),  # Will be calculated later
                    description=template["desc"],
                    cost_center_id=cost_center.id
                )
                transactions.append(debit_entry)
                
                # Create credit entry
                credit_entry = GeneralLedger(
                    organization_id=organization_id,
                    account_id=credit_account.id,
                    transaction_date=transaction_date,
                    transaction_number=f"GL{transaction_counter:06d}",
                    reference_type="AUTO",
                    reference_number=f"TXN{transaction_counter}",
                    debit_amount=Decimal('0.00'),
                    credit_amount=amount,
                    running_balance=Decimal('0.00'),  # Will be calculated later
                    description=template["desc"],
                    cost_center_id=cost_center.id
                )
                transactions.append(credit_entry)
                
                transaction_counter += 1
    
    # Add all transactions to database
    for transaction in transactions:
        db.add(transaction)
    
    db.commit()
    
    # Update running balances
    update_running_balances(db, organization_id, chart_accounts)
    
    return transactions

def update_running_balances(db, organization_id, chart_accounts):
    """Update running balances for all accounts"""
    for account_code, account in chart_accounts.items():
        if account.is_group:
            continue
            
        # Get all transactions for this account, ordered by date and ID
        entries = db.query(GeneralLedger).filter(
            GeneralLedger.organization_id == organization_id,
            GeneralLedger.account_id == account.id
        ).order_by(GeneralLedger.transaction_date, GeneralLedger.id).all()
        
        running_balance = account.opening_balance
        
        for entry in entries:
            if account.account_type.value in ['asset', 'expense']:
                running_balance += entry.debit_amount - entry.credit_amount
            else:
                running_balance += entry.credit_amount - entry.debit_amount
            
            entry.running_balance = running_balance
        
        # Update account current balance
        account.current_balance = running_balance
    
    db.commit()

def create_financial_kpis(db, organization_id):
    """Create sample financial KPIs"""
    kpis_data = [
        # Profitability KPIs
        {"code": "ROA", "name": "Return on Assets", "category": "profitability", "value": 15.5, "target": 18.0},
        {"code": "ROE", "name": "Return on Equity", "category": "profitability", "value": 22.3, "target": 25.0},
        {"code": "GPM", "name": "Gross Profit Margin", "category": "profitability", "value": 35.2, "target": 40.0},
        {"code": "NPM", "name": "Net Profit Margin", "category": "profitability", "value": 12.8, "target": 15.0},
        
        # Liquidity KPIs
        {"code": "CR", "name": "Current Ratio", "category": "liquidity", "value": 2.1, "target": 2.0},
        {"code": "QR", "name": "Quick Ratio", "category": "liquidity", "value": 1.5, "target": 1.2},
        {"code": "CCR", "name": "Cash Coverage Ratio", "category": "liquidity", "value": 0.8, "target": 1.0},
        
        # Efficiency KPIs
        {"code": "ATO", "name": "Asset Turnover", "category": "efficiency", "value": 1.2, "target": 1.5},
        {"code": "ITO", "name": "Inventory Turnover", "category": "efficiency", "value": 6.5, "target": 8.0},
        {"code": "RTO", "name": "Receivables Turnover", "category": "efficiency", "value": 8.2, "target": 10.0},
        
        # Leverage KPIs
        {"code": "DER", "name": "Debt to Equity Ratio", "category": "leverage", "value": 0.65, "target": 0.5},
        {"code": "DAR", "name": "Debt to Assets Ratio", "category": "leverage", "value": 0.35, "target": 0.3},
        {"code": "ICR", "name": "Interest Coverage Ratio", "category": "leverage", "value": 8.5, "target": 10.0},
    ]
    
    # Create KPIs for the past 6 months
    created_kpis = []
    for month_offset in range(6):
        period_end = date.today() - timedelta(days=month_offset * 30)
        period_start = period_end - timedelta(days=30)
        
        for kpi_data in kpis_data:
            # Add some random variation to values (±10%)
            base_value = kpi_data["value"]
            variation = random.uniform(-0.1, 0.1)
            current_value = base_value * (1 + variation)
            
            # Calculate variance percentage
            target_value = kpi_data["target"]
            variance_percentage = ((current_value - target_value) / target_value) * 100 if target_value != 0 else 0
            
            kpi = FinancialKPI(
                organization_id=organization_id,
                kpi_code=kpi_data["code"],
                kpi_name=kpi_data["name"],
                kpi_category=kpi_data["category"],
                kpi_value=Decimal(str(round(current_value, 2))),
                target_value=Decimal(str(target_value)),
                variance_percentage=Decimal(str(round(variance_percentage, 2))),
                period_start=period_start,
                period_end=period_end,
                calculation_method=f"Calculated based on {kpi_data['category']} metrics",
                calculated_at=datetime.utcnow()
            )
            db.add(kpi)
            created_kpis.append(kpi)
    
    db.commit()
    return created_kpis

def create_bank_reconciliation_data(db, organization_id, bank_accounts):
    """Create sample bank reconciliation records"""
    reconciliations = []
    
    for bank_account in bank_accounts:
        # Create reconciliation for the past 3 months
        for month_offset in range(3):
            reconciliation_date = date.today() - timedelta(days=month_offset * 30)
            statement_date = reconciliation_date - timedelta(days=1)
            
            # Simulate some reconciliation discrepancies
            book_balance = bank_account.current_balance + Decimal(str(random.uniform(-5000, 5000)))
            outstanding_deposits = Decimal(str(random.uniform(0, 10000)))
            outstanding_checks = Decimal(str(random.uniform(0, 8000)))
            bank_charges = Decimal(str(random.uniform(100, 500)))
            interest_earned = Decimal(str(random.uniform(50, 200)))
            
            # Calculate bank balance to create realistic scenario
            bank_balance = book_balance + outstanding_checks - outstanding_deposits + bank_charges + interest_earned
            difference = abs(bank_balance - book_balance - outstanding_checks + outstanding_deposits - bank_charges - interest_earned)
            
            status = "reconciled" if difference < 100 else "pending"
            
            reconciliation = BankReconciliation(
                organization_id=organization_id,
                bank_account_id=bank_account.id,
                reconciliation_date=reconciliation_date,
                statement_date=statement_date,
                bank_balance=bank_balance,
                book_balance=book_balance,
                outstanding_deposits=outstanding_deposits,
                outstanding_checks=outstanding_checks,
                bank_charges=bank_charges,
                interest_earned=interest_earned,
                status=status,
                difference_amount=difference,
                notes=f"Monthly reconciliation for {bank_account.bank_name}"
            )
            db.add(reconciliation)
            reconciliations.append(reconciliation)
    
    db.commit()
    return reconciliations

def main():
    """Main function to create all finance seed data"""
    db = SessionLocal()
    
    try:
        # Get the first organization (assuming it exists)
        organization = db.query(Organization).first()
        if not organization:
            print("No organization found. Please create an organization first.")
            return
        
        print(f"Creating finance seed data for organization: {organization.name}")
        
        # Create comprehensive chart of accounts
        print("Creating chart of accounts...")
        chart_accounts = create_comprehensive_chart_of_accounts(db, organization.id)
        print(f"Created {len(chart_accounts)} chart of accounts")
        
        # Create cost centers
        print("Creating cost centers...")
        cost_centers = create_cost_centers(db, organization.id)
        print(f"Created {len(cost_centers)} cost centers")
        
        # Create bank accounts
        print("Creating bank accounts...")
        bank_accounts = create_bank_accounts(db, organization.id, chart_accounts)
        print(f"Created {len(bank_accounts)} bank accounts")
        
        # Create sample transactions
        print("Creating sample transactions...")
        transactions = create_sample_transactions(db, organization.id, chart_accounts, cost_centers)
        print(f"Created {len(transactions)} general ledger transactions")
        
        # Create financial KPIs
        print("Creating financial KPIs...")
        kpis = create_financial_kpis(db, organization.id)
        print(f"Created {len(kpis)} financial KPIs")
        
        # Create bank reconciliation data
        print("Creating bank reconciliation data...")
        reconciliations = create_bank_reconciliation_data(db, organization.id, bank_accounts)
        print(f"Created {len(reconciliations)} bank reconciliation records")
        
        print("\n🎉 Finance seed data creation completed successfully!")
        print("\nSummary:")
        print(f"  📊 Chart of Accounts: {len(chart_accounts)} accounts")
        print(f"  🏢 Cost Centers: {len(cost_centers)} departments")
        print(f"  🏦 Bank Accounts: {len(bank_accounts)} accounts")
        print(f"  📝 Transactions: {len(transactions)} entries")
        print(f"  📈 Financial KPIs: {len(kpis)} metrics")
        print(f"  🔄 Bank Reconciliations: {len(reconciliations)} records")
        
        print("\nYou can now:")
        print("  • View the Finance Dashboard")
        print("  • Explore General Ledger entries")
        print("  • Analyze Cost Center performance")
        print("  • Review Bank Account details")
        print("  • Generate Financial Reports")
        print("  • Track KPI trends")
        
    except Exception as e:
        print(f"Error creating finance seed data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()