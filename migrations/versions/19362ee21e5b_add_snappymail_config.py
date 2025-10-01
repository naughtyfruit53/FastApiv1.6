"""add snappymail config

Revision ID: 19362ee21e5b
Revises: c6e8167fd6ef
Create Date: 2025-09-25 20:43:31.599358

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '19362ee21e5b'
down_revision = 'c6e8167fd6ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create snappymail_configs table if not exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS snappymail_configs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            email VARCHAR NOT NULL,
            imap_host VARCHAR NOT NULL,
            imap_port INTEGER NOT NULL,
            smtp_host VARCHAR NOT NULL,
            smtp_port INTEGER NOT NULL,
            use_ssl BOOLEAN NOT NULL,
            password VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT fk_snappymail_config_user_id FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Create indexes if not exists
    op.execute("CREATE INDEX IF NOT EXISTS ix_snappymail_configs_email ON snappymail_configs (email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_snappymail_configs_id ON snappymail_configs (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_snappymail_configs_user_id ON snappymail_configs (user_id)")


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_snappymail_configs_user_id")
    op.execute("DROP INDEX IF EXISTS ix_snappymail_configs_id")
    op.execute("DROP INDEX IF EXISTS ix_snappymail_configs_email")
    
    # Drop table
    op.execute("DROP TABLE IF EXISTS snappymail_configs")