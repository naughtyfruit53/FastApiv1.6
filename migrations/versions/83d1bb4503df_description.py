"""description

Revision ID: 83d1bb4503df
Revises: 8c40a7ce3604
Create Date: 2025-09-13 02:53:35.816281

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83d1bb4503df'
down_revision = '8c40a7ce3604'
branch_labels = None
depends_on = None


def upgrade():
    # Add the missing columns to the quotations table
    op.add_column('quotations', sa.Column('line_discount_type', sa.String(), nullable=True))
    op.add_column('quotations', sa.Column('total_discount_type', sa.String(), nullable=True))
    op.add_column('quotations', sa.Column('total_discount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('quotations', sa.Column('round_off', sa.Float(), nullable=True, server_default='0.0'))

def downgrade():
    # Remove the columns if rolling back
    op.drop_column('quotations', 'line_discount_type')
    op.drop_column('quotations', 'total_discount_type')
    op.drop_column('quotations', 'total_discount')
    op.drop_column('quotations', 'round_off')