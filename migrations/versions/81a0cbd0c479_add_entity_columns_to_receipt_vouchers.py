"""Add entity columns to receipt_vouchers

Revision ID: 81a0cbd0c479
Revises: 73527960eaa4  # Adjust if needed based on alembic history
Create Date: 2025-09-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81a0cbd0c479'
down_revision = '73527960eaa4'  # Replace with actual previous revision ID from alembic history
branch_labels = None
depends_on = None


def upgrade():
    # Columns already exist, so no operations needed
    pass


def downgrade():
    # To reverse, would drop columns, but since they exist and are needed, do nothing or comment out
    pass