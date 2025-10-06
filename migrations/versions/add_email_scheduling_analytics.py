"""Add email scheduling and analytics fields

Revision ID: add_email_scheduling_analytics
Revises: add_voucher_enhancements
Create Date: 2024-10-06 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_email_scheduling_analytics'
down_revision = 'add_voucher_enhancements'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add email scheduling and analytics fields to email_sends table.
    Requirement 4: Email scheduling and analytics (delayed send, open rates, bounces)
    """
    # Add scheduling and analytics columns to email_sends table
    with op.batch_alter_table('email_sends', schema=None) as batch_op:
        # Email scheduling
        batch_op.add_column(sa.Column('scheduled_send_at', sa.DateTime(timezone=True), nullable=True))
        
        # Email analytics tracking
        batch_op.add_column(sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('bounced_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('bounce_reason', sa.String(500), nullable=True))
        batch_op.add_column(sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'))
        
        # Add index for scheduled emails lookup
        batch_op.create_index('idx_email_sends_scheduled', ['scheduled_send_at'], unique=False)


def downgrade():
    """Remove email scheduling and analytics fields"""
    with op.batch_alter_table('email_sends', schema=None) as batch_op:
        # Remove index
        batch_op.drop_index('idx_email_sends_scheduled')
        
        # Remove columns
        batch_op.drop_column('click_count')
        batch_op.drop_column('open_count')
        batch_op.drop_column('bounce_reason')
        batch_op.drop_column('bounced_at')
        batch_op.drop_column('clicked_at')
        batch_op.drop_column('opened_at')
        batch_op.drop_column('scheduled_send_at')
