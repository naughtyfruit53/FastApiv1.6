"""Drop mail management tables and relationships

Revision ID: c6e8167fd6ef
Revises: change_email_fk
Create Date: 2025-09-25 19:43:32.074567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c6e8167fd6ef'
down_revision = 'change_email_fk'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop mail management tables using raw SQL with CASCADE to handle dependencies automatically
    op.execute("DROP TABLE IF EXISTS email_attachments CASCADE")
    op.execute("DROP TABLE IF EXISTS email_actions CASCADE")
    op.execute("DROP TABLE IF EXISTS sent_emails CASCADE")
    op.execute("DROP TABLE IF EXISTS email_rules CASCADE")
    op.execute("DROP TABLE IF EXISTS email_templates CASCADE")
    op.execute("DROP TABLE IF EXISTS email_accounts CASCADE")
    op.execute("DROP TABLE IF EXISTS emails CASCADE")

def downgrade() -> None:
    # Recreate email_accounts table
    op.create_table('email_accounts',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('email_accounts_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email_address', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('account_type', postgresql.ENUM('IMAP', 'POP3', 'EXCHANGE', 'GMAIL', 'OUTLOOK', name='emailaccounttype'), autoincrement=False, nullable=False),
    sa.Column('incoming_server', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('incoming_port', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('incoming_ssl', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('outgoing_server', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('outgoing_port', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('outgoing_ssl', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('password_encrypted', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('oauth_token', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('oauth_refresh_token', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('oauth_expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('sync_enabled', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('sync_frequency_minutes', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sync_folders', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('auto_link_to_tasks', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('auto_link_to_calendar', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('last_sync_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_sync_status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('last_sync_error', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_email_accounts_organization_id'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_email_accounts_user_id'),
    sa.PrimaryKeyConstraint('id', name='email_accounts_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_email_accounts_id', 'email_accounts', ['id'], unique=False)
    op.create_index('ix_email_accounts_email_address', 'email_accounts', ['email_address'], unique=False)

    # Recreate emails table
    op.create_table('emails',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('emails_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('message_id', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('thread_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('subject', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('from_address', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('from_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('to_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('cc_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('bcc_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('reply_to', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('body_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('body_html', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('UNREAD', 'READ', 'REPLIED', 'FORWARDED', 'ARCHIVED', 'DELETED', 'SPAM', name='emailstatus'), autoincrement=False, nullable=False),
    sa.Column('priority', postgresql.ENUM('LOW', 'NORMAL', 'HIGH', 'URGENT', name='emailpriority'), autoincrement=False, nullable=False),
    sa.Column('is_flagged', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_important', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('sent_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('received_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('calendar_event_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('folder', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('labels', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('size_bytes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('has_attachments', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['email_accounts.id'], name='fk_emails_account_id'),
    sa.ForeignKeyConstraint(['calendar_event_id'], ['calendar_events.id'], name='fk_emails_calendar_event_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_emails_organization_id'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_emails_task_id'),
    sa.PrimaryKeyConstraint('id', name='emails_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_emails_id', 'emails', ['id'], unique=False)
    op.create_index('ix_emails_message_id', 'emails', ['message_id'], unique=False)
    op.create_index('ix_emails_from_address', 'emails', ['from_address'], unique=False)
    op.create_index('ix_emails_received_at', 'emails', ['received_at'], unique=False)
    op.create_index('ix_emails_sent_at', 'emails', ['sent_at'], unique=False)
    op.create_index('ix_emails_subject', 'emails', ['subject'], unique=False)
    op.create_index('ix_emails_thread_id', 'emails', ['thread_id'], unique=False)

    # Recreate sent_emails table
    op.create_table('sent_emails',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('sent_emails_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('message_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('thread_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('subject', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('to_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('cc_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('bcc_addresses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('body_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('body_html', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('account_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sent_by', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('calendar_event_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('in_reply_to_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('delivery_status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('sent_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('scheduled_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['email_accounts.id'], name='fk_sent_emails_account_id'),
    sa.ForeignKeyConstraint(['calendar_event_id'], ['calendar_events.id'], name='fk_sent_emails_calendar_event_id'),
    sa.ForeignKeyConstraint(['in_reply_to_id'], ['emails.id'], name='fk_sent_emails_in_reply_to_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_sent_emails_organization_id'),
    sa.ForeignKeyConstraint(['sent_by'], ['users.id'], name='fk_sent_emails_sent_by'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_sent_emails_task_id'),
    sa.PrimaryKeyConstraint('id', name='sent_emails_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_sent_emails_id', 'sent_emails', ['id'], unique=False)
    op.create_index('ix_sent_emails_message_id', 'sent_emails', ['message_id'], unique=False)
    op.create_index('ix_sent_emails_thread_id', 'sent_emails', ['thread_id'], unique=False)

    # Recreate email_templates table
    op.create_table('email_templates',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('subject_template', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('body_text_template', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('body_html_template', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_shared', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('category', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_email_templates_created_by'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_email_templates_organization_id'),
    sa.PrimaryKeyConstraint('id', name='email_templates_pkey')
    )
    op.create_index('ix_email_templates_id', 'email_templates', ['id'], unique=False)
    op.create_index('ix_email_templates_name', 'email_templates', ['name'], unique=False)

    # Recreate email_rules table
    op.create_table('email_rules',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('conditions', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('actions', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('priority', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_email_rules_organization_id'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_email_rules_user_id'),
    sa.PrimaryKeyConstraint('id', name='email_rules_pkey')
    )
    op.create_index('ix_email_rules_id', 'email_rules', ['id'], unique=False)

    # Recreate email_actions table
    op.create_table('email_actions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('action_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('action_data', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('performed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['email_id'], ['emails.id'], name='fk_email_actions_email_id'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_email_actions_user_id'),
    sa.PrimaryKeyConstraint('id', name='email_actions_pkey')
    )
    op.create_index('ix_email_actions_id', 'email_actions', ['id'], unique=False)

    # Recreate email_attachments table
    op.create_table('email_attachments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('filename', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('content_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('size_bytes', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('content_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('file_path', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('file_data', sa.LARGEBINARY(), autoincrement=False, nullable=True),
    sa.Column('is_inline', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_downloaded', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['email_id'], ['emails.id'], name='fk_email_attachments_email_id'),
    sa.PrimaryKeyConstraint('id', name='email_attachments_pkey')
    )
    op.create_index('ix_email_attachments_id', 'email_attachments', ['id'], unique=False)