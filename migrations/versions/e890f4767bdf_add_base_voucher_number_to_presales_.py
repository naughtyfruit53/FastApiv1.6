"""add base_voucher_number to presales vouchers
Revision ID: e890f4767bdf
Revises: ed74844eaf5a
Create Date: 2025-09-16 17:52:23.728850
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e890f4767bdf'
down_revision = 'ed74844eaf5a'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add base_voucher_number to proforma_invoices
    op.add_column('proforma_invoices', sa.Column('base_voucher_number', sa.String(length=50), nullable=True))
    op.create_index('idx_pi_base_vn', 'proforma_invoices', ['base_voucher_number'], unique=False)
    
    # Add base_voucher_number to quotations
    op.add_column('quotations', sa.Column('base_voucher_number', sa.String(length=50), nullable=True))
    op.create_index('idx_quotation_base_vn', 'quotations', ['base_voucher_number'], unique=False)

def downgrade() -> None:
    # Remove base_voucher_number from quotations
    op.drop_index('idx_quotation_base_vn', table_name='quotations')
    op.drop_column('quotations', 'base_voucher_number')
    
    # Remove base_voucher_number from proforma_invoices
    op.drop_index('idx_pi_base_vn', table_name='proforma_invoices')
    op.drop_column('proforma_invoices', 'base_voucher_number')