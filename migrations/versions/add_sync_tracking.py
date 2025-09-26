"""Add sync tracking columns to user_email_tokens

Revision ID: add_sync_tracking
Revises: change_email_fk
Create Date: 2025-09-26 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_sync_tracking'
down_revision = 'change_email_fk'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_history_id column
    op.add_column('user_email_tokens',
        sa.Column('last_history_id', sa.String(), nullable=True)
    )
    
    # Add last_delta_token column
    op.add_column('user_email_tokens',
        sa.Column('last_delta_token', sa.String(), nullable=True)
    )


def downgrade():
    # Remove last_delta_token column
    op.drop_column('user_email_tokens', 'last_delta_token')
    
    # Remove last_history_id column
    op.drop_column('user_email_tokens', 'last_history_id')