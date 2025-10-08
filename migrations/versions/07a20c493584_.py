"""empty message

Revision ID: 07a20c493584
Revises: 1a970d4d14d1, add_voucher_terms
Create Date: 2025-10-08 11:37:38.724463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a20c493584'
down_revision = ('1a970d4d14d1', 'add_voucher_terms')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass