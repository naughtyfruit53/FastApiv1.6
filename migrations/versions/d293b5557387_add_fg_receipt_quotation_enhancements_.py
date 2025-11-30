"""add fg receipt quotation enhancements with revision numbering and audit tables

Revision ID: d293b5557387
Revises: 605ab52c9295
Create Date: 2025-11-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'd293b5557387'
down_revision = '605ab52c9295'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    # Conditional add columns to quotations table for revision tracking
    result = connection.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='quotations' AND column_name='base_quote_id'")).fetchone()
    if not result:
        op.add_column('quotations', sa.Column('base_quote_id', sa.Integer(), nullable=True))

    result = connection.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='quotations' AND column_name='revision_number'")).fetchone()
    if not result:
        op.add_column('quotations', sa.Column('revision_number', sa.Integer(), nullable=False, server_default='0'))  # 0 for original, increment for revisions

    result = connection.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='quotations' AND column_name='is_proforma'")).fetchone()
    if not result:
        op.add_column('quotations', sa.Column('is_proforma', sa.Boolean(), nullable=True, server_default='false'))

    # Conditional create foreign key constraint
    result = connection.execute(text("SELECT 1 FROM pg_constraint WHERE conname = 'fk_quotations_base_quote_id'")).fetchone()
    if not result:
        op.create_foreign_key(
            'fk_quotations_base_quote_id',
            'quotations',
            'quotations',
            ['base_quote_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # Conditional create index for quotations
    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_quotation_base_quote'")).fetchone()
    if not result:
        op.create_index('idx_quotation_base_quote', 'quotations', ['base_quote_id'])

    # Conditional create finished_good_receipts table
    result = connection.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name='finished_good_receipts'")).fetchone()
    if not result:
        op.create_table('finished_good_receipts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
            sa.Column('voucher_number', sa.String(100), nullable=False),
            sa.Column('date', sa.DateTime(timezone=True)),
            sa.Column('manufacturing_order_id', sa.Integer(), sa.ForeignKey('manufacturing_orders.id'), nullable=True),
            sa.Column('bom_id', sa.Integer(), sa.ForeignKey('bill_of_materials.id'), nullable=True),
            sa.Column('receipt_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('production_batch_number', sa.String(100)),
            sa.Column('lot_number', sa.String(100)),
            sa.Column('expected_quantity', sa.Float(), server_default='0.0'),
            sa.Column('received_quantity', sa.Float(), server_default='0.0'),
            sa.Column('accepted_quantity', sa.Float(), server_default='0.0'),
            sa.Column('rejected_quantity', sa.Float(), server_default='0.0'),
            sa.Column('qc_status', sa.String(50), server_default='pending'),
            sa.Column('qc_remarks', sa.Text()),
            sa.Column('inspector_name', sa.String(200)),
            sa.Column('inspection_date', sa.DateTime(timezone=True)),
            sa.Column('base_cost', sa.Float(), server_default='0.0'),
            sa.Column('material_cost', sa.Float(), server_default='0.0'),
            sa.Column('labor_cost', sa.Float(), server_default='0.0'),
            sa.Column('overhead_cost', sa.Float(), server_default='0.0'),
            sa.Column('freight_cost', sa.Float(), server_default='0.0'),
            sa.Column('duty_cost', sa.Float(), server_default='0.0'),
            sa.Column('total_cost', sa.Float(), server_default='0.0'),
            sa.Column('unit_cost', sa.Float(), server_default='0.0'),
            sa.Column('inventory_posted', sa.Boolean(), server_default='false'),
            sa.Column('inventory_posted_at', sa.DateTime(timezone=True)),
            sa.Column('inventory_posted_by', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('warehouse_location', sa.String(200)),
            sa.Column('bin_location', sa.String(200)),
            sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('approval_date', sa.DateTime(timezone=True)),
            sa.Column('total_amount', sa.Float(), server_default='0.0'),
            sa.Column('cgst_amount', sa.Float(), server_default='0.0'),
            sa.Column('sgst_amount', sa.Float(), server_default='0.0'),
            sa.Column('igst_amount', sa.Float(), server_default='0.0'),
            sa.Column('discount_amount', sa.Float(), server_default='0.0'),
            sa.Column('status', sa.String(50), server_default='draft'),
            sa.Column('notes', sa.Text()),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True)),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('organization_id', 'voucher_number', name='uq_fgr_org_voucher_number')
        )

    # Conditional create indexes for finished_good_receipts
    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgr_org_mo'")).fetchone()
    if not result:
        op.create_index('idx_fgr_org_mo', 'finished_good_receipts', ['organization_id', 'manufacturing_order_id'])

    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgr_org_date'")).fetchone()
    if not result:
        op.create_index('idx_fgr_org_date', 'finished_good_receipts', ['organization_id', 'receipt_date'])

    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgr_org_status'")).fetchone()
    if not result:
        op.create_index('idx_fgr_org_status', 'finished_good_receipts', ['organization_id', 'status'])

    # Conditional create finished_good_receipt_items table
    result = connection.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name='finished_good_receipt_items'")).fetchone()
    if not result:
        op.create_table('finished_good_receipt_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('finished_good_receipts.id'), nullable=False),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
            sa.Column('quantity', sa.Float(), nullable=False),
            sa.Column('unit', sa.String(50), nullable=False),
            sa.Column('unit_cost', sa.Float(), server_default='0.0'),
            sa.Column('total_cost', sa.Float(), server_default='0.0'),
            sa.Column('batch_number', sa.String(100)),
            sa.Column('lot_number', sa.String(100)),
            sa.Column('expiry_date', sa.DateTime(timezone=True)),
            sa.Column('qc_status', sa.String(50), server_default='pending'),
            sa.Column('qc_remarks', sa.Text()),
            sa.PrimaryKeyConstraint('id')
        )

    # Conditional create fg_receipt_cost_details table
    result = connection.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name='fg_receipt_cost_details'")).fetchone()
    if not result:
        op.create_table('fg_receipt_cost_details',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('finished_good_receipts.id'), nullable=False),
            sa.Column('cost_type', sa.String(50), nullable=False),
            sa.Column('description', sa.String(500)),
            sa.Column('amount', sa.Float(), server_default='0.0'),
            sa.Column('allocation_basis', sa.String(50)),
            sa.Column('allocation_value', sa.Float(), server_default='0.0'),
            sa.Column('reference_document', sa.String(200)),
            sa.Column('reference_id', sa.Integer()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id')),
            sa.PrimaryKeyConstraint('id')
        )

    # Conditional create fg_receipt_audits table
    result = connection.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name='fg_receipt_audits'")).fetchone()
    if not result:
        op.create_table('fg_receipt_audits',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('finished_good_receipts.id'), nullable=False),
            sa.Column('action', sa.String(50), nullable=False),
            sa.Column('action_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('action_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('before_json', postgresql.JSON()),
            sa.Column('after_json', postgresql.JSON()),
            sa.Column('notes', sa.Text()),
            sa.Column('ip_address', sa.String(100)),
            sa.Column('user_agent', sa.String(500)),
            sa.PrimaryKeyConstraint('id')
        )

    # Conditional create indexes for fg_receipt_audits
    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgra_org_receipt'")).fetchone()
    if not result:
        op.create_index('idx_fgra_org_receipt', 'fg_receipt_audits', ['organization_id', 'receipt_id'])

    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgra_action'")).fetchone()
    if not result:
        op.create_index('idx_fgra_action', 'fg_receipt_audits', ['action'])

    result = connection.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_fgra_action_at'")).fetchone()
    if not result:
        op.create_index('idx_fgra_action_at', 'fg_receipt_audits', ['action_at'])


def downgrade() -> None:
    # Drop FG Receipt audit tables if exist
    op.drop_index('idx_fgra_action_at', table_name='fg_receipt_audits', if_exists=True)
    op.drop_index('idx_fgra_action', table_name='fg_receipt_audits', if_exists=True)
    op.drop_index('idx_fgra_org_receipt', table_name='fg_receipt_audits', if_exists=True)
    op.drop_table('fg_receipt_audits', if_exists=True)
    
    # Drop FG Receipt cost details if exist
    op.drop_table('fg_receipt_cost_details', if_exists=True)
    
    # Drop FG Receipt items if exist
    op.drop_table('finished_good_receipt_items', if_exists=True)
    
    # Drop FG Receipts if exist
    op.drop_index('idx_fgr_org_status', table_name='finished_good_receipts', if_exists=True)
    op.drop_index('idx_fgr_org_date', table_name='finished_good_receipts', if_exists=True)
    op.drop_index('idx_fgr_org_mo', table_name='finished_good_receipts', if_exists=True)
    op.drop_table('finished_good_receipts', if_exists=True)
    
    # Drop quotation enhancements if exist
    op.drop_index('idx_quotation_base_quote', table_name='quotations', if_exists=True)
    op.drop_constraint('fk_quotations_base_quote_id', 'quotations', type_='foreignkey', if_exists=True)
    op.drop_column('quotations', 'is_proforma', if_exists=True)
    op.drop_column('quotations', 'revision_number', if_exists=True)
    op.drop_column('quotations', 'base_quote_id', if_exists=True)