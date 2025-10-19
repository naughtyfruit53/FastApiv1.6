#!/usr/bin/env python3
"""
Seed Default Chart of Accounts
Creates default generic accounts for all organizations
"""

from sqlalchemy.orm import Session
from app.models.erp_models import ChartOfAccounts, AccountType
from app.core.database import SessionLocal
from app.models.user_models import Organization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_COA_ACCOUNTS = [
    # ASSETS
    {
        "account_code": "1000",
        "account_name": "Assets",
        "account_type": AccountType.ASSET,
        "is_group": True,
        "can_post": False,
        "level": 0,
        "description": "All Assets"
    },
    {
        "account_code": "1100",
        "account_name": "Current Assets",
        "account_type": AccountType.ASSET,
        "is_group": True,
        "can_post": False,
        "level": 1,
        "parent_code": "1000",
        "description": "Assets that can be converted to cash within one year"
    },
    {
        "account_code": "1110",
        "account_name": "Cash and Cash Equivalents",
        "account_type": AccountType.CASH,
        "is_group": True,
        "can_post": False,
        "level": 2,
        "parent_code": "1100",
        "description": "Cash on hand and in bank"
    },
    {
        "account_code": "1111",
        "account_name": "Cash in Hand",
        "account_type": AccountType.CASH,
        "is_group": False,
        "can_post": True,
        "level": 3,
        "parent_code": "1110",
        "description": "Physical cash"
    },
    {
        "account_code": "1112",
        "account_name": "Cash at Bank",
        "account_type": AccountType.BANK,
        "is_group": False,
        "can_post": True,
        "is_reconcilable": True,
        "level": 3,
        "parent_code": "1110",
        "description": "Bank account balance"
    },
    {
        "account_code": "1120",
        "account_name": "Accounts Receivable",
        "account_type": AccountType.ASSET,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "1100",
        "description": "Amount owed by customers"
    },
    {
        "account_code": "1130",
        "account_name": "Inventory",
        "account_type": AccountType.ASSET,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "1100",
        "description": "Stock of goods"
    },
    {
        "account_code": "1200",
        "account_name": "Fixed Assets",
        "account_type": AccountType.ASSET,
        "is_group": True,
        "can_post": False,
        "level": 1,
        "parent_code": "1000",
        "description": "Long-term tangible assets"
    },
    {
        "account_code": "1210",
        "account_name": "Property, Plant & Equipment",
        "account_type": AccountType.ASSET,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "1200",
        "description": "Buildings, machinery, equipment"
    },
    
    # LIABILITIES
    {
        "account_code": "2000",
        "account_name": "Liabilities",
        "account_type": AccountType.LIABILITY,
        "is_group": True,
        "can_post": False,
        "level": 0,
        "description": "All Liabilities"
    },
    {
        "account_code": "2100",
        "account_name": "Current Liabilities",
        "account_type": AccountType.LIABILITY,
        "is_group": True,
        "can_post": False,
        "level": 1,
        "parent_code": "2000",
        "description": "Liabilities due within one year"
    },
    {
        "account_code": "2110",
        "account_name": "Accounts Payable",
        "account_type": AccountType.LIABILITY,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "2100",
        "description": "Amount owed to vendors"
    },
    {
        "account_code": "2120",
        "account_name": "GST Payable",
        "account_type": AccountType.LIABILITY,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "2100",
        "description": "GST collected and payable to government"
    },
    {
        "account_code": "2130",
        "account_name": "Payroll Payable",
        "account_type": AccountType.LIABILITY,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "2100",
        "description": "Salaries and wages payable"
    },
    
    # EQUITY
    {
        "account_code": "3000",
        "account_name": "Equity",
        "account_type": AccountType.EQUITY,
        "is_group": True,
        "can_post": False,
        "level": 0,
        "description": "Owner's Equity"
    },
    {
        "account_code": "3100",
        "account_name": "Capital",
        "account_type": AccountType.EQUITY,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "3000",
        "description": "Owner's capital investment"
    },
    {
        "account_code": "3200",
        "account_name": "Retained Earnings",
        "account_type": AccountType.EQUITY,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "3000",
        "description": "Accumulated profits"
    },
    
    # INCOME
    {
        "account_code": "4000",
        "account_name": "Income",
        "account_type": AccountType.INCOME,
        "is_group": True,
        "can_post": False,
        "level": 0,
        "description": "All Income"
    },
    {
        "account_code": "4100",
        "account_name": "Sales Income",
        "account_type": AccountType.INCOME,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "4000",
        "description": "Revenue from sales"
    },
    {
        "account_code": "4200",
        "account_name": "Service Income",
        "account_type": AccountType.INCOME,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "4000",
        "description": "Revenue from services"
    },
    {
        "account_code": "4300",
        "account_name": "Other Income",
        "account_type": AccountType.INCOME,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "4000",
        "description": "Miscellaneous income"
    },
    {
        "account_code": "4400",
        "account_name": "Discount Income",
        "account_type": AccountType.INCOME,
        "is_group": False,
        "can_post": True,
        "level": 1,
        "parent_code": "4000",
        "description": "Income from discounts received"
    },
    
    # EXPENSES
    {
        "account_code": "5000",
        "account_name": "Expenses",
        "account_type": AccountType.EXPENSE,
        "is_group": True,
        "can_post": False,
        "level": 0,
        "description": "All Expenses"
    },
    {
        "account_code": "5100",
        "account_name": "Cost of Goods Sold",
        "account_type": AccountType.EXPENSE,
        "is_group": True,
        "can_post": False,
        "level": 1,
        "parent_code": "5000",
        "description": "Direct costs of production"
    },
    {
        "account_code": "5110",
        "account_name": "Purchase Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5100",
        "description": "Cost of goods purchased"
    },
    {
        "account_code": "5200",
        "account_name": "Operating Expenses",
        "account_type": AccountType.EXPENSE,
        "is_group": True,
        "can_post": False,
        "level": 1,
        "parent_code": "5000",
        "description": "General business expenses"
    },
    {
        "account_code": "5210",
        "account_name": "Freight Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "Transportation and freight costs"
    },
    {
        "account_code": "5220",
        "account_name": "Salary Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "Employee salaries and wages"
    },
    {
        "account_code": "5230",
        "account_name": "Rent Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "Office and facility rent"
    },
    {
        "account_code": "5240",
        "account_name": "Utilities Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "Electricity, water, internet"
    },
    {
        "account_code": "5250",
        "account_name": "Discount Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "Discounts given to customers"
    },
    {
        "account_code": "5260",
        "account_name": "GST Expense",
        "account_type": AccountType.EXPENSE,
        "is_group": False,
        "can_post": True,
        "level": 2,
        "parent_code": "5200",
        "description": "GST paid on purchases (input tax)"
    },
]


def create_default_accounts(db: Session, organization_id: int, user_id: int = None):
    """
    Create default chart of accounts for an organization
    """
    logger.info(f"Creating default COA accounts for organization {organization_id}")
    
    # Check existing accounts
    existing_accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id
    ).all()
    existing_codes = {account.account_code for account in existing_accounts}
    expected_count = len(DEFAULT_COA_ACCOUNTS)  # 35 accounts expected
    
    if len(existing_accounts) >= expected_count:
        logger.info(f"Organization {organization_id} already has {len(existing_accounts)} accounts, expected {expected_count}. Skipping.")
        return False
    
    # Build parent lookup
    parent_lookup = {}
    created_accounts = {}
    
    # Create missing accounts
    for account_data in DEFAULT_COA_ACCOUNTS:
        if account_data['account_code'] in existing_codes:
            logger.info(f"Account {account_data['account_code']} already exists for organization {organization_id}. Skipping.")
            continue
        
        account_dict = account_data.copy()
        parent_code = account_dict.pop('parent_code', None)
        
        account = ChartOfAccounts(
            organization_id=organization_id,
            created_by=user_id,
            **account_dict
        )
        db.add(account)
        db.flush()  # Get the ID without committing
        
        created_accounts[account_dict['account_code']] = account
        if parent_code:
            parent_lookup[account.id] = parent_code
    
    # Set parent relationships
    for account_id, parent_code in parent_lookup.items():
        account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == account_id).first()
        parent_account = created_accounts.get(parent_code) or next(
            (acc for acc in existing_accounts if acc.account_code == parent_code), None
        )
        if parent_account:
            account.parent_account_id = parent_account.id
    
    db.commit()
    logger.info(f"Created {len(created_accounts)} new COA accounts for organization {organization_id}. Total accounts: {len(existing_accounts) + len(created_accounts)}")
    return True


def seed_all_organizations():
    """
    Seed default accounts for all organizations that don't have any accounts yet
    """
    db = SessionLocal()
    try:
        organizations = db.query(Organization).filter(Organization.status.in_(["active", "trial"])).all()
        
        logger.info(f"Found {len(organizations)} active or trial organizations")
        
        for org in organizations:
            try:
                create_default_accounts(db, org.id)
            except Exception as e:
                logger.error(f"Error creating accounts for organization {org.id}: {str(e)}")
                db.rollback()
        
        logger.info("Default COA seeding completed")
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_organizations()