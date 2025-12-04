"""add soft delete to voucher tables

Revision ID: 1617b9684107
Revises: fcf7c7a70f0a
Create Date: 2025-12-04 12:06:30.235868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1617b9684107'
down_revision = 'fcf7c7a70f0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add soft delete columns to voucher tables
    op.add_column('goods_receipt_notes', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('goods_receipt_notes', sa.Column('deletion_remark', sa.Text(), nullable=True))
    op.add_column('purchase_orders', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('purchase_orders', sa.Column('deletion_remark', sa.Text(), nullable=True))
    op.add_column('purchase_returns', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('purchase_returns', sa.Column('deletion_remark', sa.Text(), nullable=True))
    op.add_column('purchase_vouchers', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('purchase_vouchers', sa.Column('deletion_remark', sa.Text(), nullable=True))


def downgrade() -> None:
    # Drop soft delete columns from voucher tables
    op.drop_column('purchase_vouchers', 'deletion_remark')
    op.drop_column('purchase_vouchers', 'is_deleted')
    op.drop_column('purchase_returns', 'deletion_remark')
    op.drop_column('purchase_returns', 'is_deleted')
    op.drop_column('purchase_orders', 'deletion_remark')
    op.drop_column('purchase_orders', 'is_deleted')
    op.drop_column('goods_receipt_notes', 'deletion_remark')
    op.drop_column('goods_receipt_notes', 'is_deleted')