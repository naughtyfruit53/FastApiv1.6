"""add email scheduling and analytics

Revision ID: add_email_scheduling_analytics
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_email_scheduling_analytics'
down_revision = None  # Set to the latest revision hash if needed
branch_labels = None
depends_on = None


def upgrade():
    # Create email_schedule_status enum
    email_schedule_status_enum = postgresql.ENUM(
        'pending', 'sent', 'failed', 'cancelled',
        name='emailschedulestatus',
        create_type=False
    )
    email_schedule_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create scheduled_emails table
    op.create_table(
        'scheduled_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('to_address', sa.String(length=255), nullable=False),
        sa.Column('cc_addresses', sa.Text(), nullable=True),
        sa.Column('bcc_addresses', sa.Text(), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', email_schedule_status_enum, nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attachment_paths', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scheduled_email_status_time', 'scheduled_emails', ['status', 'scheduled_at'])
    op.create_index('idx_scheduled_email_org', 'scheduled_emails', ['organization_id', 'scheduled_at'])
    
    # Create email_analytics table
    op.create_table(
        'email_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.Integer(), nullable=True),
        sa.Column('scheduled_email_id', sa.Integer(), nullable=True),
        sa.Column('message_id', sa.String(length=255), nullable=True),
        sa.Column('to_address', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('delivered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bounced', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('bounced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bounce_type', sa.String(length=50), nullable=True),
        sa.Column('bounce_reason', sa.Text(), nullable=True),
        sa.Column('marked_as_spam', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('marked_as_spam_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.ForeignKeyConstraint(['scheduled_email_id'], ['scheduled_emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_email_analytics_org_delivered', 'email_analytics', ['organization_id', 'delivered'])
    op.create_index('idx_email_analytics_opened', 'email_analytics', ['opened', 'opened_at'])
    op.create_index('idx_email_analytics_bounced', 'email_analytics', ['bounced', 'bounced_at'])
    op.create_index('idx_email_analytics_email_id', 'email_analytics', ['email_id'])
    op.create_index('idx_email_analytics_scheduled_email_id', 'email_analytics', ['scheduled_email_id'])
    op.create_index('idx_email_analytics_message_id', 'email_analytics', ['message_id'])
    op.create_index('idx_email_analytics_to_address', 'email_analytics', ['to_address'])


def downgrade():
    # Drop email_analytics table
    op.drop_index('idx_email_analytics_to_address', table_name='email_analytics')
    op.drop_index('idx_email_analytics_message_id', table_name='email_analytics')
    op.drop_index('idx_email_analytics_scheduled_email_id', table_name='email_analytics')
    op.drop_index('idx_email_analytics_email_id', table_name='email_analytics')
    op.drop_index('idx_email_analytics_bounced', table_name='email_analytics')
    op.drop_index('idx_email_analytics_opened', table_name='email_analytics')
    op.drop_index('idx_email_analytics_org_delivered', table_name='email_analytics')
    op.drop_table('email_analytics')
    
    # Drop scheduled_emails table
    op.drop_index('idx_scheduled_email_org', table_name='scheduled_emails')
    op.drop_index('idx_scheduled_email_status_time', table_name='scheduled_emails')
    op.drop_table('scheduled_emails')
    
    # Drop enum
    email_schedule_status_enum = postgresql.ENUM(
        'pending', 'sent', 'failed', 'cancelled',
        name='emailschedulestatus'
    )
    email_schedule_status_enum.drop(op.get_bind(), checkfirst=True)
