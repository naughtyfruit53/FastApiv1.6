"""add customer voucher number

Revision ID: 825c29e91e03
Revises: d293b5557387
Create Date: 2025-12-01 14:15:34.554852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '825c29e91e03'
down_revision = 'd293b5557387'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add vendor_voucher_number to purchase_vouchers and customer_voucher_number to sales_orders"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Add vendor_voucher_number to purchase_vouchers if not exists
    if 'vendor_voucher_number' not in [c['name'] for c in inspector.get_columns('purchase_vouchers')]:
        op.add_column('purchase_vouchers', sa.Column('vendor_voucher_number', sa.String(), nullable=True))
    
    # Create index if not exists
    purchase_indexes = [index['name'] for index in inspector.get_indexes('purchase_vouchers')]
    if 'idx_pv_vendor_voucher_number' not in purchase_indexes:
        op.create_index('idx_pv_vendor_voucher_number', 'purchase_vouchers', ['organization_id', 'vendor_voucher_number'], unique=False)
    
    # Add customer_voucher_number to sales_orders if not exists
    if 'customer_voucher_number' not in [c['name'] for c in inspector.get_columns('sales_orders')]:
        op.add_column('sales_orders', sa.Column('customer_voucher_number', sa.String(), nullable=True))
    
    # Create index if not exists
    sales_indexes = [index['name'] for index in inspector.get_indexes('sales_orders')]
    if 'idx_so_customer_voucher_number' not in sales_indexes:
        op.create_index('idx_so_customer_voucher_number', 'sales_orders', ['organization_id', 'customer_voucher_number'], unique=False)


def downgrade() -> None:
    """Remove vendor_voucher_number and customer_voucher_number"""
    # Remove customer_voucher_number from sales_orders
    op.drop_index('idx_so_customer_voucher_number', table_name='sales_orders')
    op.drop_column('sales_orders', 'customer_voucher_number')
    
    # Remove vendor_voucher_number from purchase_vouchers
    op.drop_index('idx_pv_vendor_voucher_number', table_name='purchase_vouchers')
    op.drop_column('purchase_vouchers', 'vendor_voucher_number')
    