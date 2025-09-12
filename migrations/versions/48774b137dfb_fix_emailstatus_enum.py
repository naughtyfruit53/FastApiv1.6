"""fix emailstatus enum

Revision ID: 48774b137dfb
Revises: 20250907_095635_cf89a715
Create Date: 2025-09-08 09:07:18.933478

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '48774b137dfb'
down_revision = '20250907_095635_cf89a715'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'unread';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'read';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'replied';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'forwarded';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'archived';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'deleted';")
    op.execute("ALTER TYPE emailstatus ADD VALUE IF NOT EXISTS 'spam';")


def downgrade() -> None:
    pass