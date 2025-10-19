"""add_coa_integration_to_entities

Revision ID: coa_integration_001
Revises: 
Create Date: 2025-01-19 12:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'coa_integration_001'
down_revision = None  # Update this to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Add Chart of Accounts integration to Customer, Vendor, and FreightRate models
    """
    # Add COA fields to vendors table
    op.add_column('vendors', 
        sa.Column('payable_account_id', sa.Integer(), nullable=True)
    )
    op.create_index('ix_vendors_payable_account_id', 'vendors', ['payable_account_id'])
    op.create_foreign_key(
        'fk_vendors_payable_account_id', 
        'vendors', 'chart_of_accounts',
        ['payable_account_id'], ['id']
    )
    
    # Add COA fields to customers table
    op.add_column('customers', 
        sa.Column('receivable_account_id', sa.Integer(), nullable=True)
    )
    op.create_index('ix_customers_receivable_account_id', 'customers', ['receivable_account_id'])
    op.create_foreign_key(
        'fk_customers_receivable_account_id', 
        'customers', 'chart_of_accounts',
        ['receivable_account_id'], ['id']
    )
    
    # Add COA fields to freight_rates table
    op.add_column('freight_rates', 
        sa.Column('freight_expense_account_id', sa.Integer(), nullable=True)
    )
    op.create_index('ix_freight_rates_freight_expense_account_id', 'freight_rates', ['freight_expense_account_id'])
    op.create_foreign_key(
        'fk_freight_rates_freight_expense_account_id', 
        'freight_rates', 'chart_of_accounts',
        ['freight_expense_account_id'], ['id']
    )


def downgrade():
    """
    Remove Chart of Accounts integration from Customer, Vendor, and FreightRate models
    """
    # Remove from freight_rates
    op.drop_constraint('fk_freight_rates_freight_expense_account_id', 'freight_rates', type_='foreignkey')
    op.drop_index('ix_freight_rates_freight_expense_account_id', 'freight_rates')
    op.drop_column('freight_rates', 'freight_expense_account_id')
    
    # Remove from customers
    op.drop_constraint('fk_customers_receivable_account_id', 'customers', type_='foreignkey')
    op.drop_index('ix_customers_receivable_account_id', 'customers')
    op.drop_column('customers', 'receivable_account_id')
    
    # Remove from vendors
    op.drop_constraint('fk_vendors_payable_account_id', 'vendors', type_='foreignkey')
    op.drop_index('ix_vendors_payable_account_id', 'vendors')
    op.drop_column('vendors', 'payable_account_id')
