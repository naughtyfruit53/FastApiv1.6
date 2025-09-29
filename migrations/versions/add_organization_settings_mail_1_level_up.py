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
    # Create organization_settings table
    op.create_table('organization_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('mail_1_level_up_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_send_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('custom_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_organization_settings_organization_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )
    
    # Create indexes
    op.create_index('idx_organization_settings_organization_id', 'organization_settings', ['organization_id'])
    op.create_index('idx_organization_settings_mail_1_level_up', 'organization_settings', ['mail_1_level_up_enabled'])
    op.create_index(op.f('ix_organization_settings_id'), 'organization_settings', ['id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_organization_settings_id'), 'organization_settings')
    op.drop_index('idx_organization_settings_mail_1_level_up', 'organization_settings')
    op.drop_index('idx_organization_settings_organization_id', 'organization_settings')
    
    # Drop table
    op.drop_table('organization_settings')