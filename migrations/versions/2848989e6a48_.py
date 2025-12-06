"""empty message

Revision ID: 2848989e6a48
Revises: permission_dotted_fmt_001, b278097a4a56
Create Date: 2025-12-06 17:33:57.838052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2848989e6a48'
down_revision = ('permission_dotted_fmt_001', 'b278097a4a56')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass