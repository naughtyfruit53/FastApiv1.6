"""empty message

Revision ID: c0449a6e5215
Revises: add_sync_tracking_fields, d6115615e370
Create Date: 2025-10-04 14:28:46.362734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0449a6e5215'
down_revision = ('add_sync_tracking_fields', 'd6115615e370')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass