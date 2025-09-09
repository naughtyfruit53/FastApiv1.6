"""add discount fields

Revision ID: 9803e9064995
Revises: 66e977082c1c
Create Date: 2025-09-09 20:38:29.577044

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9803e9064995'
down_revision = '66e977082c1c'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to purchase_orders
    op.add_column('purchase_orders', sa.Column('line_discount_type', sa.String(), nullable=True))
    op.add_column('purchase_orders', sa.Column('total_discount_type', sa.String(), nullable=True))
    op.add_column('purchase_orders', sa.Column('total_discount', sa.Float(), nullable=True, server_default='0.0'))

    # Make discount_amount non-nullable in purchase_order_items
    op.execute("""
        UPDATE purchase_order_items 
        SET discount_amount = 0.0 
        WHERE discount_amount IS NULL
    """)
    op.alter_column('purchase_order_items', 'discount_amount',
        existing_type=sa.Float(),
        nullable=False
    )

def downgrade():
    op.drop_column('purchase_orders', 'line_discount_type')
    op.drop_column('purchase_orders', 'total_discount_type')
    op.drop_column('purchase_orders', 'total_discount')
    
    # Revert discount_amount to nullable
    op.alter_column('purchase_order_items', 'discount_amount',
        existing_type=sa.Float(),
        nullable=True
    )