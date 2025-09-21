# seed_finance_data.py
"""
Script to seed a standard Chart of Accounts structure (no balances or sample transactions).
This creates a pre-loaded template hierarchy for actual data entry.
"""

import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user_models import Organization
from app.models.erp_models import ChartOfAccounts
from app.models.erp_models import AccountType
from decimal import Decimal

def create_standard_chart_of_accounts(db, organization_id):
    """Create a standard chart of accounts structure without balances"""
    accounts = [
        # ASSETS (1000-1999)
        # Current Assets (1000-1199)
        {"code": "1000", "name": "Current Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1010", "name": "Cash in Hand", "type": "cash", "is_group": False, "parent": "1000"},
        {"code": "1020", "name": "Petty Cash", "type": "cash", "is_group": False, "parent": "1000"},
        {"code": "1100", "name": "Bank Accounts", "type": "bank", "is_group": True, "parent": "1000"},
        {"code": "1110", "name": "Primary Bank Account", "type": "bank", "is_group": False, "parent": "1100", "reconcilable": True},
        {"code": "1120", "name": "Secondary Bank Account", "type": "bank", "is_group": False, "parent": "1100", "reconcilable": True},
        {"code": "1200", "name": "Accounts Receivable", "type": "asset", "is_group": True, "parent": "1000"},
        {"code": "1210", "name": "Trade Receivables", "type": "asset", "is_group": False, "parent": "1200"},
        {"code": "1220", "name": "Other Receivables", "type": "asset", "is_group": False, "parent": "1200"},
        {"code": "1300", "name": "Inventory", "type": "asset", "is_group": True, "parent": "1000"},
        {"code": "1310", "name": "Raw Materials", "type": "asset", "is_group": False, "parent": "1300"},
        {"code": "1320", "name": "Finished Goods", "type": "asset", "is_group": False, "parent": "1300"},
        {"code": "1330", "name": "Work in Progress", "type": "asset", "is_group": False, "parent": "1300"},
        
        # Fixed Assets (1500-1799)
        {"code": "1500", "name": "Fixed Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1510", "name": "Plant & Machinery", "type": "asset", "is_group": False, "parent": "1500"},
        {"code": "1520", "name": "Office Equipment", "type": "asset", "is_group": False, "parent": "1500"},
        {"code": "1530", "name": "Furniture & Fixtures", "type": "asset", "is_group": False, "parent": "1500"},
        {"code": "1540", "name": "Vehicles", "type": "asset", "is_group": False, "parent": "1500"},
        {"code": "1550", "name": "Computer Equipment", "type": "asset", "is_group": False, "parent": "1500"},
        
        # LIABILITIES (2000-2999)
        # Current Liabilities (2000-2199)
        {"code": "2000", "name": "Current Liabilities", "type": "liability", "is_group": True, "parent": None},
        {"code": "2010", "name": "Accounts Payable", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2011", "name": "Trade Payables", "type": "liability", "is_group": False, "parent": "2010"},
        {"code": "2012", "name": "Other Payables", "type": "liability", "is_group": False, "parent": "2010"},
        {"code": "2100", "name": "Tax Liabilities", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2110", "name": "GST Payable", "type": "liability", "is_group": False, "parent": "2100"},
        {"code": "2120", "name": "TDS Payable", "type": "liability", "is_group": False, "parent": "2100"},
        {"code": "2130", "name": "Income Tax Payable", "type": "liability", "is_group": False, "parent": "2100"},
        {"code": "2200", "name": "Accrued Expenses", "type": "liability", "is_group": True, "parent": "2000"},
        {"code": "2210", "name": "Salary Payable", "type": "liability", "is_group": False, "parent": "2200"},
        {"code": "2220", "name": "Utility Bills Payable", "type": "liability", "is_group": False, "parent": "2200"},
        
        # Long-term Liabilities (2500-2799)
        {"code": "2500", "name": "Long-term Liabilities", "type": "liability", "is_group": True, "parent": None},
        {"code": "2510", "name": "Bank Loans", "type": "liability", "is_group": False, "parent": "2500"},
        {"code": "2520", "name": "Equipment Loans", "type": "liability", "is_group": False, "parent": "2500"},
        
        # EQUITY (3000-3999)
        {"code": "3000", "name": "Equity", "type": "equity", "is_group": True, "parent": None},
        {"code": "3100", "name": "Share Capital", "type": "equity", "is_group": False, "parent": "3000"},
        {"code": "3200", "name": "Retained Earnings", "type": "equity", "is_group": False, "parent": "3000"},
        {"code": "3300", "name": "Current Year Earnings", "type": "equity", "is_group": False, "parent": "3000"},
        
        # INCOME (4000-4999)
        {"code": "4000", "name": "Revenue", "type": "income", "is_group": True, "parent": None},
        {"code": "4100", "name": "Sales Revenue", "type": "income", "is_group": True, "parent": "4000"},
        {"code": "4110", "name": "Product Sales", "type": "income", "is_group": False, "parent": "4100"},
        {"code": "4120", "name": "Service Revenue", "type": "income", "is_group": False, "parent": "4100"},
        {"code": "4130", "name": "Consulting Revenue", "type": "income", "is_group": False, "parent": "4100"},
        {"code": "4200", "name": "Other Income", "type": "income", "is_group": True, "parent": "4000"},
        {"code": "4210", "name": "Interest Income", "type": "income", "is_group": False, "parent": "4200"},
        {"code": "4220", "name": "Dividend Income", "type": "income", "is_group": False, "parent": "4200"},
        {"code": "4230", "name": "Miscellaneous Income", "type": "income", "is_group": False, "parent": "4200"},
        
        # EXPENSES (5000-5999)
        {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "is_group": True, "parent": None},
        {"code": "5100", "name": "Material Costs", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5200", "name": "Labor Costs", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5300", "name": "Manufacturing Overhead", "type": "expense", "is_group": False, "parent": "5000"},
        
        # Operating Expenses (6000-6999)
        {"code": "6000", "name": "Operating Expenses", "type": "expense", "is_group": True, "parent": None},
        {"code": "6100", "name": "Administrative Expenses", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6110", "name": "Salaries & Wages", "type": "expense", "is_group": False, "parent": "6100"},
        {"code": "6120", "name": "Office Rent", "type": "expense", "is_group": False, "parent": "6100"},
        {"code": "6130", "name": "Utilities", "type": "expense", "is_group": False, "parent": "6100"},
        {"code": "6140", "name": "Communication", "type": "expense", "is_group": False, "parent": "6100"},
        {"code": "6150", "name": "Office Supplies", "type": "expense", "is_group": False, "parent": "6100"},
        {"code": "6200", "name": "Sales & Marketing", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6210", "name": "Advertising", "type": "expense", "is_group": False, "parent": "6200"},
        {"code": "6220", "name": "Marketing Events", "type": "expense", "is_group": False, "parent": "6200"},
        {"code": "6230", "name": "Sales Commission", "type": "expense", "is_group": False, "parent": "6200"},
        {"code": "6240", "name": "Travel & Entertainment", "type": "expense", "is_group": False, "parent": "6200"},
        {"code": "6300", "name": "IT & Technology", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6310", "name": "Software Licenses", "type": "expense", "is_group": False, "parent": "6300"},
        {"code": "6320", "name": "Hardware Maintenance", "type": "expense", "is_group": False, "parent": "6300"},
        {"code": "6330", "name": "Internet & Hosting", "type": "expense", "is_group": False, "parent": "6300"},
        {"code": "6400", "name": "Professional Services", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6410", "name": "Legal Fees", "type": "expense", "is_group": False, "parent": "6400"},
        {"code": "6420", "name": "Audit Fees", "type": "expense", "is_group": False, "parent": "6400"},
        {"code": "6430", "name": "Consulting Fees", "type": "expense", "is_group": False, "parent": "6400"},
        {"code": "6500", "name": "Finance Costs", "type": "expense", "is_group": True, "parent": "6000"},
        {"code": "6510", "name": "Interest Expense", "type": "expense", "is_group": False, "parent": "6500"},
        {"code": "6520", "name": "Bank Charges", "type": "expense", "is_group": False, "parent": "6500"},
        {"code": "6530", "name": "Foreign Exchange Loss", "type": "expense", "is_group": False, "parent": "6500"},
    ]
    
    # Create accounts and maintain parent-child relationships
    created_accounts = {}
    
    # First pass: Create all accounts
    for acc_data in accounts:
        account = ChartOfAccounts(
            organization_id=organization_id,
            account_code=acc_data["code"],
            account_name=acc_data["name"],
            account_type=AccountType(acc_data["type"]),
            is_group=acc_data["is_group"],
            opening_balance=Decimal('0.00'),
            current_balance=Decimal('0.00'),
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

def main():
    """Main function to seed standard chart of accounts for all organizations"""
    db = SessionLocal()
    
    try:
        # Get all organizations
        organizations = db.query(Organization).all()
        if not organizations:
            print("No organizations found. Please create at least one organization first.")
            return
        
        total_created = 0
        for org in organizations:
            # Check if already seeded to avoid duplicates
            existing_count = db.query(ChartOfAccounts).filter(ChartOfAccounts.organization_id == org.id).count()
            if existing_count > 0:
                print(f"Skipping organization '{org.name}' (ID: {org.id}) - already has {existing_count} accounts.")
                continue
            
            print(f"Seeding standard chart of accounts for organization: {org.name} (ID: {org.id})")
            
            # Create standard chart of accounts
            chart_accounts = create_standard_chart_of_accounts(db, org.id)
            total_created += len(chart_accounts)
            print(f"Created {len(chart_accounts)} chart of accounts for {org.name}")
        
        print(f"\n🎉 Standard chart of accounts seeded successfully for all eligible organizations!")
        print(f"Total accounts created: {total_created}")
        print("You can now edit these accounts with your actual balances in the app.")
        
    except Exception as e:
        print(f"Error seeding chart of accounts: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()