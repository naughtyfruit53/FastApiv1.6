"""add email core models

Revision ID: da9jdxsrvo2i
Revises: abc123def456
Create Date: 2025-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'da9jdxsrvo2i'
down_revision: Union[str, None] = 'abc123def456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types for email models
    email_account_type_enum = postgresql.ENUM(
        'imap', 'pop3', 'exchange', 'gmail_api', 'outlook_api', 
        name='emailaccounttype'
    )
    email_account_type_enum.create(op.get_bind())
    
    email_sync_status_enum = postgresql.ENUM(
        'active', 'paused', 'error', 'disabled', 
        name='emailsyncstatus'
    )
    email_sync_status_enum.create(op.get_bind())
    
    email_status_enum = postgresql.ENUM(
        'unread', 'read', 'replied', 'forwarded', 'archived', 'deleted', 'spam',
        name='emailmessagestatus'
    )
    email_status_enum.create(op.get_bind())
    
    email_priority_enum = postgresql.ENUM(
        'low', 'normal', 'high', 'urgent',
        name='emailpriority'
    )
    email_priority_enum.create(op.get_bind())
    
    # Create mail_accounts table
    op.create_table('mail_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email_address', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('account_type', email_account_type_enum, nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        
        # IMAP/SMTP settings
        sa.Column('incoming_server', sa.String(length=255), nullable=True),
        sa.Column('incoming_port', sa.Integer(), nullable=True),
        sa.Column('incoming_ssl', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('incoming_auth_method', sa.String(length=50), nullable=True),
        sa.Column('outgoing_server', sa.String(length=255), nullable=True),
        sa.Column('outgoing_port', sa.Integer(), nullable=True),
        sa.Column('outgoing_ssl', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('outgoing_auth_method', sa.String(length=50), nullable=True),
        
        # Authentication
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('password_encrypted', sa.Text(), nullable=True),
        sa.Column('oauth_token_id', sa.Integer(), nullable=True),
        
        # Sync configuration
        sa.Column('sync_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sync_frequency_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('sync_folders', sa.JSON(), nullable=True),
        sa.Column('full_sync_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_sync_uid', sa.String(length=255), nullable=True),
        
        # Integration settings
        sa.Column('auto_link_to_customers', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_link_to_vendors', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_create_tasks', sa.Boolean(), nullable=False, server_default='false'),
        
        # Organization and user
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Status tracking
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sync_status', email_sync_status_enum, nullable=False, server_default='active'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_error', sa.Text(), nullable=True),
        sa.Column('total_messages_synced', sa.Integer(), nullable=False, server_default='0'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['oauth_token_id'], ['user_email_tokens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email_threads table
    op.create_table('email_threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('original_subject', sa.String(length=500), nullable=False),
        sa.Column('participants', sa.JSON(), nullable=False),
        sa.Column('primary_participants', sa.JSON(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unread_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('has_attachments', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', email_status_enum, nullable=False, server_default='unread'),
        sa.Column('priority', email_priority_enum, nullable=False, server_default='normal'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_important', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('first_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('labels', sa.JSON(), nullable=True),
        sa.Column('folder', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['mail_accounts.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create emails table
    op.create_table('emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=True),
        sa.Column('provider_message_id', sa.String(length=255), nullable=True),
        sa.Column('uid', sa.String(length=255), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('from_address', sa.String(length=255), nullable=False),
        sa.Column('from_name', sa.String(length=255), nullable=True),
        sa.Column('reply_to', sa.String(length=255), nullable=True),
        sa.Column('to_addresses', sa.JSON(), nullable=False),
        sa.Column('cc_addresses', sa.JSON(), nullable=True),
        sa.Column('bcc_addresses', sa.JSON(), nullable=True),
        sa.Column('body_text', sa.Text(), nullable=True),
        sa.Column('body_html', sa.Text(), nullable=True),
        sa.Column('body_html_raw', sa.Text(), nullable=True),
        sa.Column('status', email_status_enum, nullable=False, server_default='unread'),
        sa.Column('priority', email_priority_enum, nullable=False, server_default='normal'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_important', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_attachments', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('folder', sa.String(length=255), nullable=True),
        sa.Column('labels', sa.JSON(), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('headers_raw', sa.JSON(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['mail_accounts.id'], ),
        sa.ForeignKeyConstraint(['thread_id'], ['email_threads.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email_attachments table
    op.create_table('email_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('content_id', sa.String(length=255), nullable=True),
        sa.Column('content_disposition', sa.String(length=50), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('is_safe', sa.Boolean(), nullable=True),
        sa.Column('scan_result', sa.Text(), nullable=True),
        sa.Column('is_quarantined', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_downloaded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_downloaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_inline', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create email_sync_logs table
    op.create_table('email_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('folder', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('messages_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_new', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_deleted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('sync_from_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_to_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_uid_synced', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['account_id'], ['mail_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for mail_accounts
    op.create_index('idx_mail_account_email_address', 'mail_accounts', ['email_address'])
    op.create_index('idx_mail_account_org_user', 'mail_accounts', ['organization_id', 'user_id'])
    op.create_index('idx_mail_account_sync_status', 'mail_accounts', ['sync_status'])
    op.create_index('idx_mail_account_last_sync', 'mail_accounts', ['last_sync_at'])
    
    # Create indexes for email_threads
    op.create_index('idx_email_thread_thread_id', 'email_threads', ['thread_id'])
    op.create_index('idx_email_thread_subject', 'email_threads', ['subject'])
    op.create_index('idx_email_thread_org_account', 'email_threads', ['organization_id', 'account_id'])
    op.create_index('idx_email_thread_last_activity', 'email_threads', ['last_activity_at'])
    op.create_index('idx_email_thread_status', 'email_threads', ['status'])
    
    # Create indexes for emails
    op.create_index('idx_email_message_id', 'emails', ['message_id'])
    op.create_index('idx_email_uid', 'emails', ['uid'])
    op.create_index('idx_email_provider_message_id', 'emails', ['provider_message_id'])
    op.create_index('idx_email_from_address', 'emails', ['from_address'])
    op.create_index('idx_email_subject', 'emails', ['subject'])
    op.create_index('idx_email_org_account', 'emails', ['organization_id', 'account_id'])
    op.create_index('idx_email_from_received', 'emails', ['from_address', 'received_at'])
    op.create_index('idx_email_status_received', 'emails', ['status', 'received_at'])
    op.create_index('idx_email_sent_at', 'emails', ['sent_at'])
    op.create_index('idx_email_received_at', 'emails', ['received_at'])
    op.create_index('idx_email_folder', 'emails', ['folder'])
    
    # Create indexes for email_attachments
    op.create_index('idx_email_attachment_email_id', 'email_attachments', ['email_id'])
    op.create_index('idx_email_attachment_filename', 'email_attachments', ['filename'])
    op.create_index('idx_email_attachment_hash', 'email_attachments', ['file_hash'])
    
    # Create indexes for email_sync_logs
    op.create_index('idx_email_sync_log_account_started', 'email_sync_logs', ['account_id', 'started_at'])
    op.create_index('idx_email_sync_log_status', 'email_sync_logs', ['status'])
    
    # Create unique constraints
    op.create_unique_constraint('uq_mail_account_email_user', 'mail_accounts', ['email_address', 'user_id'])
    op.create_unique_constraint('uq_email_thread_id_account', 'email_threads', ['thread_id', 'account_id'])
    op.create_unique_constraint('uq_email_message_id_account', 'emails', ['message_id', 'account_id'])


def downgrade() -> None:
    # Drop unique constraints
    op.drop_constraint('uq_email_message_id_account', 'emails', type_='unique')
    op.drop_constraint('uq_email_thread_id_account', 'email_threads', type_='unique')
    op.drop_constraint('uq_mail_account_email_user', 'mail_accounts', type_='unique')
    
    # Drop indexes for email_sync_logs
    op.drop_index('idx_email_sync_log_status', 'email_sync_logs')
    op.drop_index('idx_email_sync_log_account_started', 'email_sync_logs')
    
    # Drop indexes for email_attachments
    op.drop_index('idx_email_attachment_hash', 'email_attachments')
    op.drop_index('idx_email_attachment_filename', 'email_attachments')
    op.drop_index('idx_email_attachment_email_id', 'email_attachments')
    
    # Drop indexes for emails
    op.drop_index('idx_email_folder', 'emails')
    op.drop_index('idx_email_received_at', 'emails')
    op.drop_index('idx_email_sent_at', 'emails')
    op.drop_index('idx_email_status_received', 'emails')
    op.drop_index('idx_email_from_received', 'emails')
    op.drop_index('idx_email_org_account', 'emails')
    op.drop_index('idx_email_subject', 'emails')
    op.drop_index('idx_email_from_address', 'emails')
    op.drop_index('idx_email_provider_message_id', 'emails')
    op.drop_index('idx_email_uid', 'emails')
    op.drop_index('idx_email_message_id', 'emails')
    
    # Drop indexes for email_threads
    op.drop_index('idx_email_thread_status', 'email_threads')
    op.drop_index('idx_email_thread_last_activity', 'email_threads')
    op.drop_index('idx_email_thread_org_account', 'email_threads')
    op.drop_index('idx_email_thread_subject', 'email_threads')
    op.drop_index('idx_email_thread_thread_id', 'email_threads')
    
    # Drop indexes for mail_accounts
    op.drop_index('idx_mail_account_last_sync', 'mail_accounts')
    op.drop_index('idx_mail_account_sync_status', 'mail_accounts')
    op.drop_index('idx_mail_account_org_user', 'mail_accounts')
    op.drop_index('idx_mail_account_email_address', 'mail_accounts')
    
    # Drop tables
    op.drop_table('email_sync_logs')
    op.drop_table('email_attachments')
    op.drop_table('emails')
    op.drop_table('email_threads')
    op.drop_table('mail_accounts')
    
    # Drop enum types
    email_priority_enum = postgresql.ENUM(name='emailpriority')
    email_priority_enum.drop(op.get_bind())
    
    email_status_enum = postgresql.ENUM(name='emailmessagestatus')
    email_status_enum.drop(op.get_bind())
    
    email_sync_status_enum = postgresql.ENUM(name='emailsyncstatus')
    email_sync_status_enum.drop(op.get_bind())
    
    email_account_type_enum = postgresql.ENUM(name='emailaccounttype')
    email_account_type_enum.drop(op.get_bind())