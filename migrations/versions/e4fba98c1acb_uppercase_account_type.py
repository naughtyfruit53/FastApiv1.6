"""uppercase_account_type

Revision ID: e4fba98c1acb
Revises: 4900389cc5c0
Create Date: 2025-09-22 23:27:11.444748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4fba98c1acb'
down_revision = '4900389cc5c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE chart_of_accounts SET account_type = UPPER(account_type::text)::accounttype")


def downgrade() -> None:
    # No downgrade as this is a one-way data normalization
    pass