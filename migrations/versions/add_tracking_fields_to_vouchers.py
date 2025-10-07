"""add tracking fields to vouchers

Revision ID: add_tracking_fields
Revises: abc123def456_add_email_sends_audit_table
Create Date: 2024-10-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tracking_fields'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade():
    # Add tracking fields to purchase_orders
    op.add_column('purchase_orders', sa.Column('transporter_name', sa.String(), nullable=True))
    op.add_column('purchase_orders', sa.Column('tracking_number', sa.String(), nullable=True))
    op.add_column('purchase_orders', sa.Column('tracking_link', sa.String(), nullable=True))
    
    # Add tracking fields to delivery_challans
    op.add_column('delivery_challans', sa.Column('transporter_name', sa.String(), nullable=True))
    op.add_column('delivery_challans', sa.Column('tracking_number', sa.String(), nullable=True))
    op.add_column('delivery_challans', sa.Column('tracking_link', sa.String(), nullable=True))


def downgrade():
    # Remove tracking fields from delivery_challans
    op.drop_column('delivery_challans', 'tracking_link')
    op.drop_column('delivery_challans', 'tracking_number')
    op.drop_column('delivery_challans', 'transporter_name')
    
    # Remove tracking fields from purchase_orders
    op.drop_column('purchase_orders', 'tracking_link')
    op.drop_column('purchase_orders', 'tracking_number')
    op.drop_column('purchase_orders', 'transporter_name')
