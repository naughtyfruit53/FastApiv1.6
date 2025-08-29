"""add multi-company support

Revision ID: add_multicompany_support_002
Revises: add_sticky_notes_001
Create Date: 2025-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_multicompany_support_002'
down_revision = 'add_sticky_notes_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add max_companies column to organizations table
    op.add_column('organizations', sa.Column('max_companies', sa.Integer(), nullable=False, server_default='1'))
    
    # Drop the unique constraint that prevents multiple companies per org
    op.drop_constraint('uq_company_org', 'companies', type_='unique')
    
    # Add new unique constraint for company name per organization
    op.create_unique_constraint('uq_company_org_name', 'companies', ['organization_id', 'name'])
    
    # Create user_companies table for many-to-many relationship
    op.create_table('user_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_company_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], name='fk_user_company_assigned_by_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_user_company_company_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_user_company_organization_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_company_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'company_id', name='uq_user_company')
    )
    
    # Create indexes for user_companies table
    op.create_index('idx_user_company_active', 'user_companies', ['is_active'])
    op.create_index('idx_user_company_admin', 'user_companies', ['is_company_admin'])
    op.create_index('idx_user_company_company', 'user_companies', ['company_id'])
    op.create_index('idx_user_company_org', 'user_companies', ['organization_id'])
    op.create_index('idx_user_company_user', 'user_companies', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_user_company_user', 'user_companies')
    op.drop_index('idx_user_company_org', 'user_companies')
    op.drop_index('idx_user_company_company', 'user_companies')
    op.drop_index('idx_user_company_admin', 'user_companies')
    op.drop_index('idx_user_company_active', 'user_companies')
    
    # Drop user_companies table
    op.drop_table('user_companies')
    
    # Restore original unique constraint
    op.drop_constraint('uq_company_org_name', 'companies', type_='unique')
    op.create_unique_constraint('uq_company_org', 'companies', ['organization_id'])
    
    # Remove max_companies column from organizations
    op.drop_column('organizations', 'max_companies')