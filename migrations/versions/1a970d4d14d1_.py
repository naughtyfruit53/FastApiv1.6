"""empty message

Revision ID: 1a970d4d14d1
Revises: 5693912f1c33, add_tracking_fields
Create Date: 2025-10-07 12:57:10.743271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a970d4d14d1'
down_revision = ('5693912f1c33', 'add_tracking_fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass