"""Fix receipt_vouchers table by dropping obsolete columns
Revision ID: bebe23977bb0
Revises: 81a0cbd0c479
Create Date: 2025-09-16 09:16:49.592669
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'bebe23977bb0'
down_revision = '81a0cbd0c479'
branch_labels = None
depends_on = None

def column_exists(column_name):
    connection = op.get_bind()
    result = connection.execute(text(f"SELECT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'receipt_vouchers'::regclass AND attname = '{column_name}')"))
    return result.scalar()

def upgrade() -> None:
    # Drop only the obsolete customer_id column if it exists
    if column_exists('customer_id'):
        op.drop_constraint('receipt_vouchers_customer_id_fkey', 'receipt_vouchers', type_='foreignkey')
        op.drop_index('idx_rv_org_customer', table_name='receipt_vouchers')
        op.drop_column('receipt_vouchers', 'customer_id')

def downgrade() -> None:
    # Add back the customer_id column as nullable
    op.add_column('receipt_vouchers', sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('receipt_vouchers_customer_id_fkey', 'receipt_vouchers', 'customers', ['customer_id'], ['id'])
    op.create_index('idx_rv_org_customer', 'receipt_vouchers', ['organization_id', 'customer_id'], unique=False)