"""add commissions table

Revision ID: add_commissions_table
Revises: add missing tally fields
Create Date: 2025-10-22 01:11:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_commissions_table'
down_revision = 'add missing tally fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create commissions table
    op.create_table('commissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('sales_person_id', sa.Integer(), nullable=False),
        sa.Column('sales_person_name', sa.String(), nullable=False),
        sa.Column('person_type', sa.String(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('commission_type', sa.String(), nullable=False),
        sa.Column('commission_rate', sa.Float(), nullable=True),
        sa.Column('commission_amount', sa.Float(), nullable=True),
        sa.Column('base_amount', sa.Float(), nullable=False),
        sa.Column('commission_date', sa.Date(), nullable=False),
        sa.Column('payment_status', sa.String(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_commission_created_by_id'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], name='fk_commission_lead_id'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], name='fk_commission_opportunity_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_commission_organization_id'),
        sa.ForeignKeyConstraint(['sales_person_id'], ['users.id'], name='fk_commission_sales_person_id'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for commissions table
    op.create_index('idx_commission_org_person', 'commissions', ['organization_id', 'sales_person_id'], unique=False)
    op.create_index('idx_commission_payment_status', 'commissions', ['payment_status', 'commission_date'], unique=False)
    op.create_index(op.f('ix_commissions_id'), 'commissions', ['id'], unique=False)
    op.create_index(op.f('ix_commissions_organization_id'), 'commissions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_commissions_sales_person_id'), 'commissions', ['sales_person_id'], unique=False)
    op.create_index(op.f('ix_commissions_opportunity_id'), 'commissions', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_commissions_lead_id'), 'commissions', ['lead_id'], unique=False)
    op.create_index(op.f('ix_commissions_commission_date'), 'commissions', ['commission_date'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_commissions_commission_date'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_lead_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_opportunity_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_sales_person_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_organization_id'), table_name='commissions')
    op.drop_index(op.f('ix_commissions_id'), table_name='commissions')
    op.drop_index('idx_commission_payment_status', table_name='commissions')
    op.drop_index('idx_commission_org_person', table_name='commissions')
    
    # Drop table
    op.drop_table('commissions')
