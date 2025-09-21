"""Add payroll chart account integration models

Revision ID: payroll_coa_phase1
Revises: 76016d4a23bc
Create Date: 2024-09-21 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'payroll_coa_phase1'
down_revision = '76016d4a23bc'
branch_labels = None
depends_on = None


def upgrade():
    """Create payroll chart of accounts integration tables"""
    
    # Create payroll_components table
    op.create_table('payroll_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('component_name', sa.String(length=100), nullable=False),
        sa.Column('component_code', sa.String(length=50), nullable=False),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('expense_account_id', sa.Integer(), nullable=True),
        sa.Column('payable_account_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_taxable', sa.Boolean(), nullable=False, default=True),
        sa.Column('calculation_formula', sa.Text(), nullable=True),
        sa.Column('default_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('default_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['expense_account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['payable_account_id'], ['chart_of_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'component_code', name='uq_payroll_component_org_code')
    )
    
    # Create indexes for payroll_components
    op.create_index('idx_payroll_component_org_type', 'payroll_components', ['organization_id', 'component_type'])
    op.create_index('idx_payroll_component_expense_account', 'payroll_components', ['expense_account_id'])
    op.create_index('idx_payroll_component_payable_account', 'payroll_components', ['payable_account_id'])
    op.create_index(op.f('ix_payroll_components_id'), 'payroll_components', ['id'])
    op.create_index(op.f('ix_payroll_components_organization_id'), 'payroll_components', ['organization_id'])
    
    # Create payroll_runs table
    op.create_table('payroll_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('period_id', sa.Integer(), nullable=False),
        sa.Column('run_name', sa.String(length=200), nullable=False),
        sa.Column('run_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='draft'),
        sa.Column('total_employees', sa.Integer(), nullable=False, default=0),
        sa.Column('processed_employees', sa.Integer(), nullable=False, default=0),
        sa.Column('total_gross_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_deductions', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_net_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('gl_posted', sa.Boolean(), nullable=False, default=False),
        sa.Column('gl_posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gl_reversal_voucher_id', sa.Integer(), nullable=True),
        sa.Column('total_expense_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('total_payable_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0),
        sa.Column('payment_vouchers_generated', sa.Boolean(), nullable=False, default=False),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['period_id'], ['payroll_periods.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'period_id', 'run_name', name='uq_payroll_run_org_period_name')
    )
    
    # Create indexes for payroll_runs
    op.create_index('idx_payroll_run_org_status', 'payroll_runs', ['organization_id', 'status'])
    op.create_index('idx_payroll_run_gl_posted', 'payroll_runs', ['gl_posted'])
    op.create_index('idx_payroll_run_period', 'payroll_runs', ['period_id'])
    op.create_index(op.f('ix_payroll_runs_id'), 'payroll_runs', ['id'])
    op.create_index(op.f('ix_payroll_runs_organization_id'), 'payroll_runs', ['organization_id'])
    
    # Create payroll_lines table
    op.create_table('payroll_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('payroll_run_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('chart_account_id', sa.Integer(), nullable=False),
        sa.Column('line_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('posting_type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('gl_entry_id', sa.Integer(), nullable=True),
        sa.Column('journal_voucher_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chart_account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['payroll_components.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employee_profiles.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for payroll_lines
    op.create_index('idx_payroll_line_org_run', 'payroll_lines', ['organization_id', 'payroll_run_id'])
    op.create_index('idx_payroll_line_employee', 'payroll_lines', ['employee_id'])
    op.create_index('idx_payroll_line_component', 'payroll_lines', ['component_id'])
    op.create_index('idx_payroll_line_account', 'payroll_lines', ['chart_account_id'])
    op.create_index('idx_payroll_line_gl_entry', 'payroll_lines', ['gl_entry_id'])
    op.create_index(op.f('ix_payroll_lines_id'), 'payroll_lines', ['id'])
    op.create_index(op.f('ix_payroll_lines_organization_id'), 'payroll_lines', ['organization_id'])


def downgrade():
    """Drop payroll chart of accounts integration tables"""
    
    # Drop payroll_lines table and indexes
    op.drop_index(op.f('ix_payroll_lines_organization_id'), table_name='payroll_lines')
    op.drop_index(op.f('ix_payroll_lines_id'), table_name='payroll_lines')
    op.drop_index('idx_payroll_line_gl_entry', table_name='payroll_lines')
    op.drop_index('idx_payroll_line_account', table_name='payroll_lines')
    op.drop_index('idx_payroll_line_component', table_name='payroll_lines')
    op.drop_index('idx_payroll_line_employee', table_name='payroll_lines')
    op.drop_index('idx_payroll_line_org_run', table_name='payroll_lines')
    op.drop_table('payroll_lines')
    
    # Drop payroll_runs table and indexes
    op.drop_index(op.f('ix_payroll_runs_organization_id'), table_name='payroll_runs')
    op.drop_index(op.f('ix_payroll_runs_id'), table_name='payroll_runs')
    op.drop_index('idx_payroll_run_period', table_name='payroll_runs')
    op.drop_index('idx_payroll_run_gl_posted', table_name='payroll_runs')
    op.drop_index('idx_payroll_run_org_status', table_name='payroll_runs')
    op.drop_table('payroll_runs')
    
    # Drop payroll_components table and indexes
    op.drop_index(op.f('ix_payroll_components_organization_id'), table_name='payroll_components')
    op.drop_index(op.f('ix_payroll_components_id'), table_name='payroll_components')
    op.drop_index('idx_payroll_component_payable_account', table_name='payroll_components')
    op.drop_index('idx_payroll_component_expense_account', table_name='payroll_components')
    op.drop_index('idx_payroll_component_org_type', table_name='payroll_components')
    op.drop_table('payroll_components')