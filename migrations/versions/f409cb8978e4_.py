"""empty message

Revision ID: f409cb8978e4
Revises: 001_state_code_not_null, 20251101_08_trigger_update, 20251103_02
Create Date: 2025-11-04 12:03:33.061394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f409cb8978e4'
down_revision = ('001_state_code_not_null', '20251101_08_trigger_update', '20251103_02')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass