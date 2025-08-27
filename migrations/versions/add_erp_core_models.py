"""add_erp_procurement_tally_enhanced_inventory_models

Revision ID: add_erp_procurement_models
Revises: add_organization_id_to_otp_verifications
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_erp_procurement_models'
down_revision = 'add_organization_id_to_otp_verifications'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Chart of Accounts table
    op.create_table('chart_of_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('account_code', sa.String(length=50), nullable=False),
        sa.Column('account_name', sa.String(length=200), nullable=False),
        sa.Column('account_type', sa.Enum('ASSET', 'LIABILITY', 'EQUITY', 'INCOME', 'EXPENSE', 'BANK', 'CASH', name='accounttype'), nullable=False),
        sa.Column('parent_account_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
        sa.Column('is_group', sa.Boolean(), nullable=False, default=False),
        sa.Column('opening_balance', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('can_post', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_reconcilable', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['parent_account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'account_code', name='uq_org_account_code')
    )
    op.create_index('idx_coa_org_type', 'chart_of_accounts', ['organization_id', 'account_type'])
    op.create_index('idx_coa_parent', 'chart_of_accounts', ['parent_account_id'])
    op.create_index(op.f('ix_chart_of_accounts_id'), 'chart_of_accounts', ['id'])
    op.create_index(op.f('ix_chart_of_accounts_organization_id'), 'chart_of_accounts', ['organization_id'])
    op.create_index(op.f('ix_chart_of_accounts_account_code'), 'chart_of_accounts', ['account_code'])
    op.create_index(op.f('ix_chart_of_accounts_account_name'), 'chart_of_accounts', ['account_name'])
    op.create_index(op.f('ix_chart_of_accounts_account_type'), 'chart_of_accounts', ['account_type'])

    # GST Configuration table
    op.create_table('gst_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('gstin', sa.String(length=15), nullable=False),
        sa.Column('trade_name', sa.String(length=200), nullable=False),
        sa.Column('legal_name', sa.String(length=200), nullable=False),
        sa.Column('registration_date', sa.Date(), nullable=False),
        sa.Column('constitution', sa.String(length=100), nullable=False),
        sa.Column('business_type', sa.String(length=100), nullable=False),
        sa.Column('address_line1', sa.String(length=200), nullable=False),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=10), nullable=False),
        sa.Column('is_composition_scheme', sa.Boolean(), nullable=False, default=False),
        sa.Column('composition_tax_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gstin')
    )
    op.create_index(op.f('ix_gst_configuration_id'), 'gst_configuration', ['id'])
    op.create_index(op.f('ix_gst_configuration_organization_id'), 'gst_configuration', ['organization_id'])
    op.create_index(op.f('ix_gst_configuration_gstin'), 'gst_configuration', ['gstin'])

    # Tax Codes table
    op.create_table('tax_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('gst_configuration_id', sa.Integer(), nullable=True),
        sa.Column('tax_code', sa.String(length=50), nullable=False),
        sa.Column('tax_name', sa.String(length=200), nullable=False),
        sa.Column('tax_type', sa.Enum('CGST', 'SGST', 'IGST', 'CESS', 'TCS', 'TDS', name='taxtype'), nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('is_inclusive', sa.Boolean(), nullable=False, default=False),
        sa.Column('hsn_sac_code', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('tax_payable_account_id', sa.Integer(), nullable=True),
        sa.Column('tax_input_account_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['gst_configuration_id'], ['gst_configuration.id'], ),
        sa.ForeignKeyConstraint(['tax_payable_account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['tax_input_account_id'], ['chart_of_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'tax_code', name='uq_org_tax_code')
    )
    op.create_index('idx_tax_org_type', 'tax_codes', ['organization_id', 'tax_type'])
    op.create_index(op.f('ix_tax_codes_id'), 'tax_codes', ['id'])
    op.create_index(op.f('ix_tax_codes_organization_id'), 'tax_codes', ['organization_id'])
    op.create_index(op.f('ix_tax_codes_gst_configuration_id'), 'tax_codes', ['gst_configuration_id'])
    op.create_index(op.f('ix_tax_codes_tax_code'), 'tax_codes', ['tax_code'])
    op.create_index(op.f('ix_tax_codes_tax_type'), 'tax_codes', ['tax_type'])
    op.create_index(op.f('ix_tax_codes_hsn_sac_code'), 'tax_codes', ['hsn_sac_code'])

    # Journal Entries table
    op.create_table('journal_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('entry_number', sa.String(length=50), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_number', sa.String(length=50), nullable=True),
        sa.Column('debit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('credit_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_reconciled', sa.Boolean(), nullable=False, default=False),
        sa.Column('reconciled_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_journal_org_date', 'journal_entries', ['organization_id', 'entry_date'])
    op.create_index('idx_journal_reference', 'journal_entries', ['reference_type', 'reference_id'])
    op.create_index(op.f('ix_journal_entries_id'), 'journal_entries', ['id'])
    op.create_index(op.f('ix_journal_entries_organization_id'), 'journal_entries', ['organization_id'])
    op.create_index(op.f('ix_journal_entries_account_id'), 'journal_entries', ['account_id'])
    op.create_index(op.f('ix_journal_entries_entry_number'), 'journal_entries', ['entry_number'])
    op.create_index(op.f('ix_journal_entries_entry_date'), 'journal_entries', ['entry_date'])
    op.create_index(op.f('ix_journal_entries_reference_type'), 'journal_entries', ['reference_type'])
    op.create_index(op.f('ix_journal_entries_reference_id'), 'journal_entries', ['reference_id'])
    op.create_index(op.f('ix_journal_entries_reference_number'), 'journal_entries', ['reference_number'])

    # Accounts Payable table
    op.create_table('accounts_payable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('bill_number', sa.String(length=100), nullable=False),
        sa.Column('bill_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('bill_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('outstanding_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('payment_status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'vendor_id', 'bill_number', name='uq_org_vendor_bill')
    )
    op.create_index('idx_ap_org_status', 'accounts_payable', ['organization_id', 'payment_status'])
    op.create_index('idx_ap_due_date', 'accounts_payable', ['due_date'])
    op.create_index(op.f('ix_accounts_payable_id'), 'accounts_payable', ['id'])
    op.create_index(op.f('ix_accounts_payable_organization_id'), 'accounts_payable', ['organization_id'])
    op.create_index(op.f('ix_accounts_payable_vendor_id'), 'accounts_payable', ['vendor_id'])
    op.create_index(op.f('ix_accounts_payable_bill_number'), 'accounts_payable', ['bill_number'])
    op.create_index(op.f('ix_accounts_payable_bill_date'), 'accounts_payable', ['bill_date'])
    op.create_index(op.f('ix_accounts_payable_due_date'), 'accounts_payable', ['due_date'])
    op.create_index(op.f('ix_accounts_payable_reference_type'), 'accounts_payable', ['reference_type'])
    op.create_index(op.f('ix_accounts_payable_reference_id'), 'accounts_payable', ['reference_id'])
    op.create_index(op.f('ix_accounts_payable_payment_status'), 'accounts_payable', ['payment_status'])

    # Accounts Receivable table
    op.create_table('accounts_receivable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('invoice_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('received_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('outstanding_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('payment_status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'customer_id', 'invoice_number', name='uq_org_customer_invoice')
    )
    op.create_index('idx_ar_org_status', 'accounts_receivable', ['organization_id', 'payment_status'])
    op.create_index('idx_ar_due_date', 'accounts_receivable', ['due_date'])
    op.create_index(op.f('ix_accounts_receivable_id'), 'accounts_receivable', ['id'])
    op.create_index(op.f('ix_accounts_receivable_organization_id'), 'accounts_receivable', ['organization_id'])
    op.create_index(op.f('ix_accounts_receivable_customer_id'), 'accounts_receivable', ['customer_id'])
    op.create_index(op.f('ix_accounts_receivable_invoice_number'), 'accounts_receivable', ['invoice_number'])
    op.create_index(op.f('ix_accounts_receivable_invoice_date'), 'accounts_receivable', ['invoice_date'])
    op.create_index(op.f('ix_accounts_receivable_due_date'), 'accounts_receivable', ['due_date'])
    op.create_index(op.f('ix_accounts_receivable_reference_type'), 'accounts_receivable', ['reference_type'])
    op.create_index(op.f('ix_accounts_receivable_reference_id'), 'accounts_receivable', ['reference_id'])
    op.create_index(op.f('ix_accounts_receivable_payment_status'), 'accounts_receivable', ['payment_status'])

    # Payment Records table
    op.create_table('payment_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('payment_number', sa.String(length=100), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('accounts_payable_id', sa.Integer(), nullable=True),
        sa.Column('accounts_receivable_id', sa.Integer(), nullable=True),
        sa.Column('bank_account', sa.String(length=100), nullable=True),
        sa.Column('cheque_number', sa.String(length=50), nullable=True),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['accounts_payable_id'], ['accounts_payable.id'], ),
        sa.ForeignKeyConstraint(['accounts_receivable_id'], ['accounts_receivable.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_org_date', 'payment_records', ['organization_id', 'payment_date'])
    op.create_index('idx_payment_method', 'payment_records', ['payment_method'])
    op.create_index(op.f('ix_payment_records_id'), 'payment_records', ['id'])
    op.create_index(op.f('ix_payment_records_organization_id'), 'payment_records', ['organization_id'])
    op.create_index(op.f('ix_payment_records_payment_number'), 'payment_records', ['payment_number'])
    op.create_index(op.f('ix_payment_records_payment_date'), 'payment_records', ['payment_date'])
    op.create_index(op.f('ix_payment_records_accounts_payable_id'), 'payment_records', ['accounts_payable_id'])
    op.create_index(op.f('ix_payment_records_accounts_receivable_id'), 'payment_records', ['accounts_receivable_id'])

    # Continue with procurement models in the next part due to size...


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('payment_records')
    op.drop_table('accounts_receivable')
    op.drop_table('accounts_payable')
    op.drop_table('journal_entries')
    op.drop_table('tax_codes')
    op.drop_table('gst_configuration')
    op.drop_table('chart_of_accounts')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS accounttype')
    op.execute('DROP TYPE IF EXISTS taxtype')