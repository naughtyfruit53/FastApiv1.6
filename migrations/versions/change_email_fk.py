"""Change FK for emails and sent_emails to user_email_tokens

Revision ID: change_email_fk
Revises: e4fba98c1acb
Create Date: 2025-09-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'change_email_fk'
down_revision = 'e4fba98c1acb'
branch_labels = None
depends_on = None


def upgrade():
    # Change FK for emails table
    op.drop_constraint('emails_account_id_fkey', 'emails', type_='foreignkey')
    op.create_foreign_key('emails_account_id_fkey', 'emails', 'user_email_tokens', ['account_id'], ['id'])
    
    # Change FK for sent_emails table
    op.drop_constraint('sent_emails_account_id_fkey', 'sent_emails', type_='foreignkey')
    op.create_foreign_key('sent_emails_account_id_fkey', 'sent_emails', 'user_email_tokens', ['account_id'], ['id'])


def downgrade():
    # Revert FK for emails table
    op.drop_constraint('emails_account_id_fkey', 'emails', type_='foreignkey')
    op.create_foreign_key('emails_account_id_fkey', 'emails', 'email_accounts', ['account_id'], ['id'])
    
    # Revert FK for sent_emails table
    op.drop_constraint('sent_emails_account_id_fkey', 'sent_emails', type_='foreignkey')
    op.create_foreign_key('sent_emails_account_id_fkey', 'sent_emails', 'email_accounts', ['account_id'], ['id'])