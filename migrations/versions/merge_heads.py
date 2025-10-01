# alembic/versions/merge_heads.py

"""merge heads

Revision ID: merge_heads
Revises: 19362ee21e5b, mail_1_level_up_001, da9jdxsrvo2i
Create Date: 2025-10-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('19362ee21e5b', 'mail_1_level_up_001', 'da9jdxsrvo2i')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass