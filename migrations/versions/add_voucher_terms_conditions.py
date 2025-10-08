"""add voucher terms and conditions

Revision ID: add_voucher_terms
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_voucher_terms'
down_revision = None  # Will be set by alembic
head = None


def upgrade():
    # Add terms and conditions columns to organization_settings
    op.add_column('organization_settings', sa.Column('purchase_order_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('purchase_voucher_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('sales_order_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('sales_voucher_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('quotation_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('proforma_invoice_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('delivery_challan_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('grn_terms', sa.Text(), nullable=True))
    op.add_column('organization_settings', sa.Column('manufacturing_terms', sa.Text(), nullable=True))


def downgrade():
    # Remove terms and conditions columns from organization_settings
    op.drop_column('organization_settings', 'manufacturing_terms')
    op.drop_column('organization_settings', 'grn_terms')
    op.drop_column('organization_settings', 'delivery_challan_terms')
    op.drop_column('organization_settings', 'proforma_invoice_terms')
    op.drop_column('organization_settings', 'quotation_terms')
    op.drop_column('organization_settings', 'sales_voucher_terms')
    op.drop_column('organization_settings', 'sales_order_terms')
    op.drop_column('organization_settings', 'purchase_voucher_terms')
    op.drop_column('organization_settings', 'purchase_order_terms')
