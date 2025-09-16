"""Drop obsolete customer_id from receipt_vouchers

Revision ID: 9519442f824d
Revises: bebe23977bb0
Create Date: 2025-09-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '9519442f824d'
down_revision = 'bebe23977bb0'
branch_labels = None
depends_on = None

def column_exists(column_name):
    connection = op.get_bind()
    result = connection.execute(text(f"SELECT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'receipt_vouchers'::regclass AND attname = '{column_name}')"))
    return result.scalar()

def upgrade():
    if column_exists('customer_id'):
        op.drop_constraint('receipt_vouchers_customer_id_fkey', 'receipt_vouchers', type_='foreignkey')
        op.drop_index('idx_rv_org_customer', table_name='receipt_vouchers')
        op.drop_column('receipt_vouchers', 'customer_id')
    # If vendor_id exists and is obsolete, add:
    # if column_exists('vendor_id'):
    #     op.drop_constraint('receipt_vouchers_vendor_id_fkey', 'receipt_vouchers', type_='foreignkey')
    #     op.drop_index('idx_rv_org_vendor', table_name='receipt_vouchers')  # Adjust index name if exists
    #     op.drop_column('receipt_vouchers', 'vendor_id')

def downgrade():
    op.add_column('receipt_vouchers', sa.Column('customer_id', sa.Integer(), nullable=True))
    op.create_foreign_key('receipt_vouchers_customer_id_fkey', 'receipt_vouchers', 'customers', ['customer_id'], ['id'])
    op.create_index('idx_rv_org_customer', 'receipt_vouchers', ['organization_id', 'customer_id'], unique=False)
    # Add back if vendor_id was dropped:
    # op.add_column('receipt_vouchers', sa.Column('vendor_id', sa.Integer(), nullable=True))
    # op.create_foreign_key('receipt_vouchers_vendor_id_fkey', 'receipt_vouchers', 'vendors', ['vendor_id'], ['id'])
    # op.create_index('idx_rv_org_vendor', 'receipt_vouchers', ['organization_id', 'vendor_id'], unique=False)