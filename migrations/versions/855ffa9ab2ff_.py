"""empty message

Revision ID: 855ffa9ab2ff
Revises: add_voucher_enhancements, c0449a6e5215
Create Date: 2025-10-06 10:27:41.232069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '855ffa9ab2ff'
down_revision = ('add_voucher_enhancements', 'c0449a6e5215')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass