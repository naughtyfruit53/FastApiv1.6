"""add module action to service_permissions

Revision ID: 3fba9cac4b29
Revises: 0f8fa3f1e5c4
Create Date: 2025-11-08 09:07:22.574647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fba9cac4b29'
down_revision = '0f8fa3f1e5c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE service_permissions ADD COLUMN IF NOT EXISTS module VARCHAR(50)')
    op.execute('ALTER TABLE service_permissions ADD COLUMN IF NOT EXISTS action VARCHAR(50)')


def downgrade() -> None:
    op.execute('ALTER TABLE service_permissions DROP COLUMN IF EXISTS action')
    op.execute('ALTER TABLE service_permissions DROP COLUMN IF EXISTS module')