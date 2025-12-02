"""add_owner_id_to_leads.py

Revision ID: 95fb4af3964e
Revises: 39994d1b2c26
Create Date: 2025-12-02 17:01:13.763552

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '95fb4af3964e'
down_revision = '39994d1b2c26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add owner_id column to leads table
    op.add_column('leads', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_lead_owner_id', 'leads', 'users', ['owner_id'], ['id'])

def downgrade() -> None:
    # Remove owner_id column
    op.drop_constraint('fk_lead_owner_id', 'leads', type_='foreignkey')
    op.drop_column('leads', 'owner_id')