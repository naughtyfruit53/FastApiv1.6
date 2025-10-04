"""add sync tracking fields to user_email_tokens

Revision ID: add_sync_tracking_fields
Revises: 
Create Date: 2025-10-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_sync_tracking_fields'
down_revision = None  # Will be set by alembic
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add sync tracking fields to user_email_tokens table.
    These fields enable efficient incremental sync:
    - last_history_id: For Gmail history API
    - last_delta_token: For Microsoft Graph delta queries
    """
    # Add last_history_id for Gmail incremental sync
    op.add_column('user_email_tokens', 
        sa.Column('last_history_id', sa.String(255), nullable=True)
    )
    
    # Add last_delta_token for Microsoft incremental sync
    op.add_column('user_email_tokens',
        sa.Column('last_delta_token', sa.Text(), nullable=True)
    )
    
    # Add indexes for better query performance
    op.create_index('ix_user_email_tokens_last_history_id', 
                    'user_email_tokens', 
                    ['last_history_id'],
                    unique=False)


def downgrade() -> None:
    """Remove sync tracking fields"""
    op.drop_index('ix_user_email_tokens_last_history_id', 
                  table_name='user_email_tokens')
    op.drop_column('user_email_tokens', 'last_delta_token')
    op.drop_column('user_email_tokens', 'last_history_id')
