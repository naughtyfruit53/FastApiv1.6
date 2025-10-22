"""empty message

Revision ID: c447472aaa2b
Revises: add_commissions_table, cded334ab127
Create Date: 2025-10-22 15:51:26.918889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c447472aaa2b'
down_revision = ('add_commissions_table', 'cded334ab127')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass