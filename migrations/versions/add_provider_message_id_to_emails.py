"""add provider_message_id to emails

Revision ID: add_provider_message_id_to_emails
Revises: increase_alembic_version_length
Create Date: 2025-10-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_provider_message_id_to_emails'
down_revision = 'increase_alembic_version_length'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('emails', sa.Column('provider_message_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_emails_provider_message_id'), 'emails', ['provider_message_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_emails_provider_message_id'), table_name='emails')
    op.drop_column('emails', 'provider_message_id')