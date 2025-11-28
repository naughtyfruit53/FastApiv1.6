"""add soft delete to manufacturing_order

Revision ID: 70ad2d33fc29
Revises: f74e5554b7de
Create Date: 2025-11-28 11:13:16.226323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70ad2d33fc29'
down_revision = 'f74e5554b7de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns for soft delete
    op.add_column('manufacturing_orders', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('manufacturing_orders', sa.Column('deletion_remark', sa.Text(), nullable=True))
    op.create_index('idx_mo_deleted', 'manufacturing_orders', ['is_deleted'], unique=False)


def downgrade() -> None:
    # Remove soft delete columns and index
    op.drop_index('idx_mo_deleted', table_name='manufacturing_orders')
    op.drop_column('manufacturing_orders', 'deletion_remark')
    op.drop_column('manufacturing_orders', 'is_deleted')