"""add superadmin_full_name to organizations

Revision ID: a475535ea199
Revises: 95fb4af3964e
Create Date: 2025-12-02 22:03:56.170807

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a475535ea199'
down_revision = '95fb4af3964e'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('organizations', sa.Column('superadmin_full_name', sa.String(length=100), nullable=True))

def downgrade() -> None:
    op.drop_column('organizations', 'superadmin_full_name')