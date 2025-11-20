"""Merge multiple heads for entitlements

Revision ID: 784448bbeca4
Revises: 4dfb99055368, 20251101_entitlements
Create Date: 2025-11-01 10:23:02.764392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '784448bbeca4'
down_revision = ('4dfb99055368', '20251101_entitlements')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass