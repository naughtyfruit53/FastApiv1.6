"""add_enhanced_finance_models

Revision ID: add_enhanced_finance_models
Revises: 2be0230fa04b
Create Date: 2024-12-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_enhanced_finance_models'
down_revision = '2be0230fa04b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # General Ledger table
    op.create_table('general_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('transaction_number', sa.String(length=100), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('debit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('credit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('running_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('narration', sa.Text(), nullable=True),
        sa.Column('cost_center_id', sa.Integer(), nullable=True),
        sa.Column('is_reconciled', sa.Boolean(), nullable=False, default=False),
        sa.Column('reconciled_date', sa.Date(), nullable=True),
        sa.Column('reconciled_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id'], ),
        sa.ForeignKeyConstraint(['reconciled_by'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_gl_org_account_date', 'general_ledger', ['organization_id', 'account_id', 'transaction_date'])
    op.create_index('idx_gl_reference', 'general_ledger', ['reference_type', 'reference_id'])
    op.create_index('idx_gl_transaction_number', 'general_ledger', ['transaction_number'])
    op.create_index(op.f('ix_general_ledger_id'), 'general_ledger', ['id'])

    # Cost Centers table
    op.create_table('cost_centers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('cost_center_code', sa.String(length=50), nullable=False),
        sa.Column('cost_center_name', sa.String(length=200), nullable=False),
        sa.Column('parent_cost_center_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
        sa.Column('budget_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('actual_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['parent_cost_center_id'], ['cost_centers.id'], ),
        sa.ForeignKeyConstraint(['manager_id'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'cost_center_code', name='uq_org_cost_center_code')
    )
    op.create_index('idx_cc_org_active', 'cost_centers', ['organization_id', 'is_active'])
    op.create_index(op.f('ix_cost_centers_id'), 'cost_centers', ['id'])

    # Bank Accounts table
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('chart_account_id', sa.Integer(), nullable=False),
        sa.Column('bank_name', sa.String(length=200), nullable=False),
        sa.Column('branch_name', sa.String(length=200), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('ifsc_code', sa.String(length=20), nullable=True),
        sa.Column('swift_code', sa.String(length=20), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='INR'),
        sa.Column('opening_balance', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('auto_reconcile', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['chart_account_id'], ['chart_of_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'account_number', name='uq_org_account_number')
    )
    op.create_index('idx_bank_org_active', 'bank_accounts', ['organization_id', 'is_active'])
    op.create_index(op.f('ix_bank_accounts_id'), 'bank_accounts', ['id'])

    # Bank Reconciliation table
    op.create_table('bank_reconciliations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('reconciliation_date', sa.Date(), nullable=False),
        sa.Column('statement_date', sa.Date(), nullable=False),
        sa.Column('bank_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('book_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('outstanding_deposits', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('outstanding_checks', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('bank_charges', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('interest_earned', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('difference_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_recon_org_date', 'bank_reconciliations', ['organization_id', 'reconciliation_date'])
    op.create_index('idx_recon_status', 'bank_reconciliations', ['status'])
    op.create_index(op.f('ix_bank_reconciliations_id'), 'bank_reconciliations', ['id'])

    # Financial Statements table
    op.create_table('financial_statements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('statement_type', sa.String(length=50), nullable=False),
        sa.Column('statement_name', sa.String(length=200), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('statement_data', sa.JSON(), nullable=False),
        sa.Column('summary_data', sa.JSON(), nullable=True),
        sa.Column('is_final', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_audited', sa.Boolean(), nullable=False, default=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['generated_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_fs_org_type_period', 'financial_statements', ['organization_id', 'statement_type', 'period_end'])
    op.create_index('idx_fs_period', 'financial_statements', ['period_start', 'period_end'])
    op.create_index(op.f('ix_financial_statements_id'), 'financial_statements', ['id'])

    # Financial KPIs table
    op.create_table('financial_kpis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('kpi_code', sa.String(length=50), nullable=False),
        sa.Column('kpi_name', sa.String(length=200), nullable=False),
        sa.Column('kpi_category', sa.String(length=100), nullable=False),
        sa.Column('kpi_value', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('calculation_method', sa.Text(), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('target_value', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('variance_percentage', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('calculated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['calculated_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kpi_org_category_period', 'financial_kpis', ['organization_id', 'kpi_category', 'period_end'])
    op.create_index('idx_kpi_code_period', 'financial_kpis', ['kpi_code', 'period_end'])
    op.create_index(op.f('ix_financial_kpis_id'), 'financial_kpis', ['id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('financial_kpis')
    op.drop_table('financial_statements')
    op.drop_table('bank_reconciliations')
    op.drop_table('bank_accounts')
    op.drop_table('cost_centers')
    op.drop_table('general_ledger')