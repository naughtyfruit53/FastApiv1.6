"""increase alembic version length

Revision ID: increase_alembic_version_length
Revises: da9jdxsrvo2i
Create Date: 2025-10-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'increase_alembic_version_length'
down_revision = 'da9jdxsrvo2i'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('alembic_version', 'version_num',
               existing_type=sa.String(length=32),
               type_=sa.String(length=255),
               existing_nullable=False)

def downgrade():
    op.alter_column('alembic_version', 'version_num',
               existing_type=sa.String(length=255),
               type_=sa.String(length=32),
               existing_nullable=False)