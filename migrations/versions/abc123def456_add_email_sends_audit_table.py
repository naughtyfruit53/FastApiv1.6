"""add email sends audit table

Revision ID: abc123def456
Revises: e4fba98c1acb
Create Date: 2024-09-29 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = 'e4fba98c1acb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    email_provider_enum = postgresql.ENUM('brevo', 'smtp', 'gmail_api', 'outlook_api', name='emailprovider')
    email_provider_enum.create(op.get_bind())
    
    email_status_enum = postgresql.ENUM('pending', 'sent', 'failed', 'retry', 'delivered', 'bounced', name='emailstatus')
    email_status_enum.create(op.get_bind())
    
    email_type_enum = postgresql.ENUM('user_invite', 'password_reset', 'user_creation', 'otp', 'notification', 'marketing', 'transactional', name='emailtype')
    email_type_enum.create(op.get_bind())
    
    # Create email_sends table
    op.create_table('email_sends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('to_email', sa.String(length=255), nullable=False),
        sa.Column('from_email', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('email_type', email_type_enum, nullable=False),
        sa.Column('provider_used', email_provider_enum, nullable=False),
        sa.Column('status', email_status_enum, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('provider_message_id', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_brevo_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_email_sends_org_type', 'email_sends', ['organization_id', 'email_type'])
    op.create_index('idx_email_sends_provider_status', 'email_sends', ['provider_used', 'status'])
    op.create_index('idx_email_sends_status_created', 'email_sends', ['status', 'created_at'])
    op.create_index('idx_email_sends_user_created', 'email_sends', ['user_id', 'created_at'])
    op.create_index(op.f('ix_email_sends_email_type'), 'email_sends', ['email_type'])
    op.create_index(op.f('ix_email_sends_id'), 'email_sends', ['id'])
    op.create_index(op.f('ix_email_sends_provider_message_id'), 'email_sends', ['provider_message_id'])
    op.create_index(op.f('ix_email_sends_provider_used'), 'email_sends', ['provider_used'])
    op.create_index(op.f('ix_email_sends_status'), 'email_sends', ['status'])
    op.create_index(op.f('ix_email_sends_to_email'), 'email_sends', ['to_email'])
    
    # Add password reset token fields to users table
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('reset_token_used', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Drop added columns from users table
    op.drop_column('users', 'reset_token_used')
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
    
    # Drop indexes
    op.drop_index(op.f('ix_email_sends_to_email'), 'email_sends')
    op.drop_index(op.f('ix_email_sends_status'), 'email_sends')
    op.drop_index(op.f('ix_email_sends_provider_used'), 'email_sends')
    op.drop_index(op.f('ix_email_sends_provider_message_id'), 'email_sends')
    op.drop_index(op.f('ix_email_sends_id'), 'email_sends')
    op.drop_index(op.f('ix_email_sends_email_type'), 'email_sends')
    op.drop_index('idx_email_sends_user_created', 'email_sends')
    op.drop_index('idx_email_sends_status_created', 'email_sends')
    op.drop_index('idx_email_sends_provider_status', 'email_sends')
    op.drop_index('idx_email_sends_org_type', 'email_sends')
    
    # Drop table
    op.drop_table('email_sends')
    
    # Drop enum types
    email_type_enum = postgresql.ENUM('user_invite', 'password_reset', 'user_creation', 'otp', 'notification', 'marketing', 'transactional', name='emailtype')
    email_type_enum.drop(op.get_bind())
    
    email_status_enum = postgresql.ENUM('pending', 'sent', 'failed', 'retry', 'delivered', 'bounced', name='emailstatus')
    email_status_enum.drop(op.get_bind())
    
    email_provider_enum = postgresql.ENUM('brevo', 'smtp', 'gmail_api', 'outlook_api', name='emailprovider')
    email_provider_enum.drop(op.get_bind())