"""website agent migration

Revision ID: 493b76db19da
Revises: add_website_agent_20251022, c447472aaa2b
Create Date: 2025-10-22 16:08:07.627474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '493b76db19da'
down_revision = ('add_website_agent_20251022', 'c447472aaa2b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass