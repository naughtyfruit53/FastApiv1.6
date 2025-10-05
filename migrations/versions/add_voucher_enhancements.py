"""add voucher enhancements

Revision ID: add_voucher_enhancements
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_voucher_enhancements'
down_revision = None  # Will be set by alembic
branch_labels = None
depends_on = None


def upgrade():
    # Create VoucherCounterResetPeriod enum
    voucher_counter_reset_period_enum = sa.Enum(
        'never', 'monthly', 'quarterly', 'annually',
        name='vouchercounterresetperiod'
    )
    voucher_counter_reset_period_enum.create(op.get_bind(), checkfirst=True)
    
    # Add new columns to organization_settings
    op.add_column('organization_settings', 
        sa.Column('voucher_prefix', sa.String(length=5), nullable=True))
    op.add_column('organization_settings', 
        sa.Column('voucher_prefix_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('organization_settings', 
        sa.Column('voucher_counter_reset_period', 
                  voucher_counter_reset_period_enum, 
                  nullable=False, 
                  server_default='annually'))
    op.add_column('organization_settings', 
        sa.Column('voucher_format_template_id', sa.Integer(), nullable=True))
    
    # Create VoucherFormatTemplate table
    op.create_table('voucher_format_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('template_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('preview_image_url', sa.String(length=500), nullable=True),
        sa.Column('is_system_template', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_voucher_format_template_active', 'voucher_format_templates', ['is_active'])
    op.create_index('idx_voucher_format_template_system', 'voucher_format_templates', ['is_system_template'])
    
    # Create VoucherEmailTemplate table
    op.create_table('voucher_email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('voucher_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('subject_template', sa.String(length=500), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], 
                                name='fk_voucher_email_templates_organization_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'voucher_type', 'entity_type', 
                           name='uq_org_voucher_entity_template')
    )
    op.create_index('idx_voucher_email_template_org_type', 'voucher_email_templates', 
                    ['organization_id', 'voucher_type', 'entity_type'])


def downgrade():
    # Drop tables and columns in reverse order
    op.drop_index('idx_voucher_email_template_org_type', table_name='voucher_email_templates')
    op.drop_table('voucher_email_templates')
    
    op.drop_index('idx_voucher_format_template_system', table_name='voucher_format_templates')
    op.drop_index('idx_voucher_format_template_active', table_name='voucher_format_templates')
    op.drop_table('voucher_format_templates')
    
    op.drop_column('organization_settings', 'voucher_format_template_id')
    op.drop_column('organization_settings', 'voucher_counter_reset_period')
    op.drop_column('organization_settings', 'voucher_prefix_enabled')
    op.drop_column('organization_settings', 'voucher_prefix')
    
    # Drop enum
    sa.Enum(name='vouchercounterresetperiod').drop(op.get_bind(), checkfirst=True)
