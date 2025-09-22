# cleanup_chart_accounts.py
"""
Script to clean non-group chart of accounts for a specific organization (keep types/groups)
"""

import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.erp_models import ChartOfAccounts

def cleanup_chart_accounts(db, organization_id):
    """Delete non-group chart of accounts for the organization"""
    accounts = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_group == False  # Only delete leaf accounts
    ).all()
    
    count = len(accounts)
    for account in accounts:
        db.delete(account)
    
    db.commit()
    return count

def main():
    db = SessionLocal()
    
    try:
        org_id = 1  # Your organization ID
        deleted = cleanup_chart_accounts(db, org_id)
        print(f"Deleted {deleted} non-group chart of accounts for organization ID {org_id}")
        
    except Exception as e:
        print(f"Error cleaning chart of accounts: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()