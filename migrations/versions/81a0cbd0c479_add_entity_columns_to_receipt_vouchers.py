"""Add entity columns to receipt_vouchers

Revision ID: 81a0cbd0c479
Revises: 73527960eaa4
Create Date: 2025-09-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '81a0cbd0c479'
down_revision = '73527960eaa4'
branch_labels = None
depends_on = None

def index_exists():
    connection = op.get_bind()
    result = connection.execute(text("SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_rv_org_entity')"))
    return result.scalar()

def column_exists(column_name):
    connection = op.get_bind()
    result = connection.execute(text(f"SELECT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'receipt_vouchers'::regclass AND attname = '{column_name}')"))
    return result.scalar()

def upgrade():
    op.add_column('receipt_vouchers', sa.Column('entity_id', sa.Integer(), nullable=False))
    op.add_column('receipt_vouchers', sa.Column('entity_type', sa.String(length=50), nullable=False))
    op.create_index('idx_rv_org_entity', 'receipt_vouchers', ['organization_id', 'entity_id'], unique=False)

def downgrade():
    if index_exists():
        op.drop_index('idx_rv_org_entity', table_name='receipt_vouchers')
    if column_exists('entity_type'):
        op.drop_column('receipt_vouchers', 'entity_type')
    if column_exists('entity_id'):
        op.drop_column('receipt_vouchers', 'entity_id')