"""empty message

Revision ID: 7384d03ac956
Revises: 20251104_01_fix_perms, f409cb8978e4
Create Date: 2025-11-05 09:03:03.428168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7384d03ac956'
down_revision = ('20251104_01_fix_perms', 'f409cb8978e4')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass