# app/scripts/seed_finance_data.py

"""
Script to seed a standard Chart of Accounts structure (no balances or sample transactions).
This creates a pre-loaded template hierarchy for actual data entry.
"""

import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user_models import Organization
from app.models.erp_models import ChartOfAccounts
from app.models.erp_models import AccountType
from decimal import Decimal

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def create_standard_chart_of_accounts(db: AsyncSession, organization_id: int):
    """Create a standard chart of accounts structure without balances"""
    accounts = [
        # ASSETS (1000-1999)
        # Current Assets (1000-1199)
        {"code": "1000", "name": "Current Assets", "type": "ASSET", "is_group": True, "parent": None},
        {"code": "1100", "name": "Bank Accounts", "type": "BANK", "is_group": True, "parent": "1000"},
        {"code": "1200", "name": "Accounts Receivable", "type": "ASSET", "is_group": True, "parent": "1000"},
        {"code": "1300", "name": "Inventory", "type": "ASSET", "is_group": True, "parent": "1000"},
        
        # Fixed Assets (1500-1799)
        {"code": "1500", "name": "Fixed Assets", "type": "ASSET", "is_group": True, "parent": None},
        
        # LIABILITIES (2000-2999)
        # Current Liabilities (2000-2199)
        {"code": "2000", "name": "Current Liabilities", "type": "LIABILITY", "is_group": True, "parent": None},
        {"code": "2010", "name": "Accounts Payable", "type": "LIABILITY", "is_group": True, "parent": "2000"},
        {"code": "2100", "name": "Tax Liabilities", "type": "LIABILITY", "is_group": True, "parent": "2000"},
        {"code": "2200", "name": "Accrued Expenses", "type": "LIABILITY", "is_group": True, "parent": "2000"},
        
        # Long-term Liabilities (2500-2799)
        {"code": "2500", "name": "Long-term Liabilities", "type": "LIABILITY", "is_group": True, "parent": None},
        
        # EQUITY (3000-3999)
        {"code": "3000", "name": "Equity", "type": "EQUITY", "is_group": True, "parent": None},
        
        # INCOME (4000-4999)
        {"code": "4000", "name": "Revenue", "type": "INCOME", "is_group": True, "parent": None},
        {"code": "4100", "name": "Sales Revenue", "type": "INCOME", "is_group": True, "parent": "4000"},
        {"code": "4200", "name": "Other Income", "type": "INCOME", "is_group": True, "parent": "4000"},
        
        # EXPENSES (5000-5999)
        {"code": "5000", "name": "Cost of Goods Sold", "type": "EXPENSE", "is_group": True, "parent": None},
        
        # Operating Expenses (6000-6999)
        {"code": "6000", "name": "Operating Expenses", "type": "EXPENSE", "is_group": True, "parent": None},
        {"code": "6100", "name": "Administrative Expenses", "type": "EXPENSE", "is_group": True, "parent": "6000"},
        {"code": "6200", "name": "Sales & Marketing", "type": "EXPENSE", "is_group": True, "parent": "6000"},
        {"code": "6300", "name": "IT & Technology", "type": "EXPENSE", "is_group": True, "parent": "6000"},
        {"code": "6400", "name": "Professional Services", "type": "EXPENSE", "is_group": True, "parent": "6000"},
        {"code": "6500", "name": "Finance Costs", "type": "EXPENSE", "is_group": True, "parent": "6000"},
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
        await db.flush()  # Get the ID
        created_accounts[acc_data["code"]] = account
    
    # Second pass: Set parent relationships
    for acc_data in accounts:
        if acc_data["parent"]:
            created_accounts[acc_data["code"]].parent_account_id = created_accounts[acc_data["parent"]].id
    
    await db.commit()
    return created_accounts

async def main():
    """Main function to seed standard chart of accounts for all organizations"""
    db = AsyncSessionLocal()
    
    try:
        # Get all organizations
        result = await db.execute(db.query(Organization))
        organizations = result.scalars().all()
        if not organizations:
            print("No organizations found. Please create at least one organization first.")
            return
        
        total_created = 0
        for org in organizations:
            # Check if already seeded to avoid duplicates
            result = await db.execute(db.query(ChartOfAccounts).filter(ChartOfAccounts.organization_id == org.id))
            existing_count = len(result.scalars().all())
            if existing_count > 0:
                print(f"Skipping organization '{org.name}' (ID: {org.id}) - already has {existing_count} accounts.")
                continue
            
            print(f"Seeding standard chart of accounts for organization: {org.name} (ID: {org.id})")
            
            # Create standard chart of accounts
            chart_accounts = await create_standard_chart_of_accounts(db, org.id)
            total_created += len(chart_accounts)
            print(f"Created {len(chart_accounts)} chart of accounts for {org.name}")
        
        print(f"\n🎉 Standard chart of accounts seeded successfully for all eligible organizations!")
        print(f"Total accounts created: {total_created}")
        print("You can now edit these accounts with your actual balances in the app.")
        
    except Exception as e:
        print(f"Error seeding chart of accounts: {str(e)}")
        await db.rollback()
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())