"""merge heads

Revision ID: 538365d334d1
Revises: add_ca_id_to_fv, payroll_coa_phase1
Create Date: 2025-09-22 10:48:44.318072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '538365d334d1'
down_revision = ('add_ca_id_to_fv', 'payroll_coa_phase1')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass