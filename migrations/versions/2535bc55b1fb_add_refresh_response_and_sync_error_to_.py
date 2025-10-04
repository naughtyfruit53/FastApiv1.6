"""add refresh response and sync error to user_email_tokens

Revision ID: 2535bc55b1fb
Revises: b9b00637e71a
Create Date: 2025-10-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2535bc55b1fb'
down_revision = 'b9b00637e71a'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns if they don't exist
    op.execute("""
        ALTER TABLE user_email_tokens 
        ADD COLUMN IF NOT EXISTS last_refresh_response TEXT NULL
    """)
    op.execute("""
        ALTER TABLE user_email_tokens 
        ADD COLUMN IF NOT EXISTS last_sync_error TEXT NULL
    """)


def downgrade():
    # Remove columns (no IF EXISTS needed for drop, as it will fail if not exist but that's fine for downgrade)
    op.drop_column('user_email_tokens', 'last_sync_error')
    op.drop_column('user_email_tokens', 'last_refresh_response')