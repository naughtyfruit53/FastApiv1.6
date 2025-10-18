"""Merge multiple heads

Revision ID: 4f9bc2056f63
Revises: 2025101901_create_schema_version, add missing tally fields
Create Date: 2025-10-19 00:36:56.219224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f9bc2056f63'
down_revision = ('2025101901_create_schema_version', 'add missing tally fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass