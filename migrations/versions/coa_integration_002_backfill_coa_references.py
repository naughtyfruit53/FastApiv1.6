"""backfill_coa_references

Revision ID: coa_integration_002
Revises: coa_integration_001
Create Date: 2025-01-19 12:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select
from sqlalchemy import Integer, String


# revision identifiers, used by Alembic.
revision = 'coa_integration_002'
down_revision = 'coa_integration_001'
branch_labels = None
depends_on = None


def upgrade():
    """
    Backfill COA references for existing Customer, Vendor, and FreightRate records
    """
    connection = op.get_bind()
    
    # Define table structures for query building
    coa = table('chart_of_accounts',
        column('id', Integer),
        column('organization_id', Integer),
        column('account_code', String),
        column('account_name', String),
    )
    
    vendors = table('vendors',
        column('id', Integer),
        column('organization_id', Integer),
        column('payable_account_id', Integer),
    )
    
    customers = table('customers',
        column('id', Integer),
        column('organization_id', Integer),
        column('receivable_account_id', Integer),
    )
    
    freight_rates = table('freight_rates',
        column('id', Integer),
        column('organization_id', Integer),
        column('freight_expense_account_id', Integer),
    )
    
    # Get all organizations
    organizations = connection.execute(
        sa.text("SELECT DISTINCT id FROM organizations WHERE is_active = true")
    ).fetchall()
    
    for org_row in organizations:
        org_id = org_row[0]
        
        # Find default accounts for this organization
        accounts_payable_account = connection.execute(
            select([coa.c.id]).where(
                sa.and_(
                    coa.c.organization_id == org_id,
                    coa.c.account_code == '2110'  # Accounts Payable
                )
            )
        ).fetchone()
        
        accounts_receivable_account = connection.execute(
            select([coa.c.id]).where(
                sa.and_(
                    coa.c.organization_id == org_id,
                    coa.c.account_code == '1120'  # Accounts Receivable
                )
            )
        ).fetchone()
        
        freight_expense_account = connection.execute(
            select([coa.c.id]).where(
                sa.and_(
                    coa.c.organization_id == org_id,
                    coa.c.account_code == '5210'  # Freight Expense
                )
            )
        ).fetchone()
        
        # Update vendors with payable account
        if accounts_payable_account:
            connection.execute(
                vendors.update().where(
                    sa.and_(
                        vendors.c.organization_id == org_id,
                        vendors.c.payable_account_id == None
                    )
                ).values(payable_account_id=accounts_payable_account[0])
            )
        
        # Update customers with receivable account
        if accounts_receivable_account:
            connection.execute(
                customers.update().where(
                    sa.and_(
                        customers.c.organization_id == org_id,
                        customers.c.receivable_account_id == None
                    )
                ).values(receivable_account_id=accounts_receivable_account[0])
            )
        
        # Update freight rates with freight expense account
        if freight_expense_account:
            connection.execute(
                freight_rates.update().where(
                    sa.and_(
                        freight_rates.c.organization_id == org_id,
                        freight_rates.c.freight_expense_account_id == None
                    )
                ).values(freight_expense_account_id=freight_expense_account[0])
            )


def downgrade():
    """
    Clear COA references from Customer, Vendor, and FreightRate records
    """
    connection = op.get_bind()
    
    # Clear all COA references
    connection.execute(
        sa.text("UPDATE vendors SET payable_account_id = NULL WHERE payable_account_id IS NOT NULL")
    )
    connection.execute(
        sa.text("UPDATE customers SET receivable_account_id = NULL WHERE receivable_account_id IS NOT NULL")
    )
    connection.execute(
        sa.text("UPDATE freight_rates SET freight_expense_account_id = NULL WHERE freight_expense_account_id IS NOT NULL")
    )
