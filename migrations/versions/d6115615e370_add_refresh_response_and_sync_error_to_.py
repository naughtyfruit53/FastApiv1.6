"""add refresh response and sync error to user_email_tokens with conditionals

Revision ID: d6115615e370
Revises: 2535bc55b1fb
Create Date: 2025-10-04 09:13:14.554384

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd6115615e370'
down_revision = '2535bc55b1fb'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns if they don't exist using raw SQL
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'user_email_tokens' AND column_name = 'last_refresh_response'
            ) THEN
                ALTER TABLE user_email_tokens ADD COLUMN last_refresh_response TEXT NULL;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'user_email_tokens' AND column_name = 'last_sync_error'
            ) THEN
                ALTER TABLE user_email_tokens ADD COLUMN last_sync_error TEXT NULL;
            END IF;
        END $$;
    """)

def downgrade():
    # Remove columns if they exist
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'user_email_tokens' AND column_name = 'last_sync_error'
            ) THEN
                ALTER TABLE user_email_tokens DROP COLUMN last_sync_error;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'user_email_tokens' AND column_name = 'last_refresh_response'
            ) THEN
                ALTER TABLE user_email_tokens DROP COLUMN last_refresh_response;
            END IF;
        END $$;
    """)