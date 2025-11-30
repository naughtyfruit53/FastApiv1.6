"""Add FG Receipt, Quotation enhancements, and audit tables

Revision ID: fg_quotation_audit_2025
Revises: f74e5554b7de
Create Date: 2025-11-30 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fg_quotation_audit_2025'
down_revision = 'f74e5554b7de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to quotations table
    op.add_column('quotations', sa.Column('base_quote_id', sa.Integer(), sa.ForeignKey('quotations.id'), nullable=True))
    op.add_column('quotations', sa.Column('is_proforma', sa.Boolean(), nullable=True, server_default='false'))
    
    # Create unique constraint for base_quote_id + revision_number (allow NULLs for original quotes)
    # Note: This constraint only applies when base_quote_id is NOT NULL
    op.create_index('idx_quotation_base_quote', 'quotations', ['base_quote_id'])
    
    # Create finished_good_receipts table
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
    op.create_index('idx_fgr_org_mo', 'finished_good_receipts', ['organization_id', 'manufacturing_order_id'])
    op.create_index('idx_fgr_org_date', 'finished_good_receipts', ['organization_id', 'receipt_date'])
    op.create_index('idx_fgr_org_status', 'finished_good_receipts', ['organization_id', 'status'])
    
    # Create finished_good_receipt_items table
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
    
    # Create fg_receipt_cost_details table
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
    
    # Create fg_receipt_audits table for detailed audit trail
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
    op.create_index('idx_fgra_org_receipt', 'fg_receipt_audits', ['organization_id', 'receipt_id'])
    op.create_index('idx_fgra_action', 'fg_receipt_audits', ['action'])
    op.create_index('idx_fgra_action_at', 'fg_receipt_audits', ['action_at'])


def downgrade() -> None:
    # Drop FG Receipt audit tables
    op.drop_index('idx_fgra_action_at', table_name='fg_receipt_audits')
    op.drop_index('idx_fgra_action', table_name='fg_receipt_audits')
    op.drop_index('idx_fgra_org_receipt', table_name='fg_receipt_audits')
    op.drop_table('fg_receipt_audits')
    
    # Drop FG Receipt cost details
    op.drop_table('fg_receipt_cost_details')
    
    # Drop FG Receipt items
    op.drop_table('finished_good_receipt_items')
    
    # Drop FG Receipts
    op.drop_index('idx_fgr_org_status', table_name='finished_good_receipts')
    op.drop_index('idx_fgr_org_date', table_name='finished_good_receipts')
    op.drop_index('idx_fgr_org_mo', table_name='finished_good_receipts')
    op.drop_table('finished_good_receipts')
    
    # Drop quotation enhancements
    op.drop_index('idx_quotation_base_quote', table_name='quotations')
    op.drop_column('quotations', 'is_proforma')
    op.drop_column('quotations', 'base_quote_id')
