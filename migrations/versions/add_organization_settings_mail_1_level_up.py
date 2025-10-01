"""add organization settings mail 1 level up

Revision ID: mail_1_level_up_001
Revises: abc123def456
Create Date: 2024-09-29 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'mail_1_level_up_001'
down_revision: Union[str, None] = 'abc123def456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organization_settings table if not exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS organization_settings (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL UNIQUE,
            mail_1_level_up_enabled BOOLEAN NOT NULL DEFAULT FALSE,
            auto_send_notifications BOOLEAN NOT NULL DEFAULT TRUE,
            custom_settings JSON,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT fk_organization_settings_organization_id FOREIGN KEY(organization_id) REFERENCES organizations(id)
        )
    """)
    
    # Create indexes if not exists
    op.execute("CREATE INDEX IF NOT EXISTS idx_organization_settings_organization_id ON organization_settings (organization_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_organization_settings_mail_1_level_up ON organization_settings (mail_1_level_up_enabled)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_organization_settings_id ON organization_settings (id)")


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_organization_settings_id")
    op.execute("DROP INDEX IF EXISTS idx_organization_settings_mail_1_level_up")
    op.execute("DROP INDEX IF EXISTS idx_organization_settings_organization_id")
    
    # Drop table
    op.execute("DROP TABLE IF EXISTS organization_settings")