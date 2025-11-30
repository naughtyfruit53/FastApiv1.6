"""add vendor_voucher_number and customer_voucher_number

Revision ID: ece817c4f98d
Revises: f74e5554b7de
Create Date: 2025-11-30 08:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ece817c4f98d'
down_revision = 'f74e5554b7de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add vendor_voucher_number to purchase_vouchers and customer_voucher_number to sales_orders"""
    # Add vendor_voucher_number to purchase_vouchers
    op.add_column('purchase_vouchers', sa.Column('vendor_voucher_number', sa.String(), nullable=True))
    op.create_index('idx_pv_vendor_voucher_number', 'purchase_vouchers', ['organization_id', 'vendor_voucher_number'], unique=False)
    
    # Add customer_voucher_number to sales_orders
    op.add_column('sales_orders', sa.Column('customer_voucher_number', sa.String(), nullable=True))
    op.create_index('idx_so_customer_voucher_number', 'sales_orders', ['organization_id', 'customer_voucher_number'], unique=False)


def downgrade() -> None:
    """Remove vendor_voucher_number and customer_voucher_number"""
    # Remove customer_voucher_number from sales_orders
    op.drop_index('idx_so_customer_voucher_number', table_name='sales_orders')
    op.drop_column('sales_orders', 'customer_voucher_number')
    
    # Remove vendor_voucher_number from purchase_vouchers
    op.drop_index('idx_pv_vendor_voucher_number', table_name='purchase_vouchers')
    op.drop_column('purchase_vouchers', 'vendor_voucher_number')
