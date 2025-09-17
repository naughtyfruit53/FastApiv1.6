"""add revision fields to presales models
Revision ID: caab765e48ad
Revises: e890f4767bdf
Create Date: 2025-09-17 08:29:14.473781
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'caab765e48ad'
down_revision = 'e890f4767bdf'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add revision fields to quotations
    op.add_column('quotations', sa.Column('parent_id', sa.Integer(), sa.ForeignKey('quotations.id'), nullable=True))
    op.add_column('quotations', sa.Column('revision_number', sa.Integer(), server_default=sa.text('0'), nullable=False))

    # Add revision fields to proforma_invoices
    op.add_column('proforma_invoices', sa.Column('parent_id', sa.Integer(), sa.ForeignKey('proforma_invoices.id'), nullable=True))
    op.add_column('proforma_invoices', sa.Column('revision_number', sa.Integer(), server_default=sa.text('0'), nullable=False))

def downgrade() -> None:
    # Remove revision fields from proforma_invoices
    op.drop_column('proforma_invoices', 'revision_number')
    op.drop_column('proforma_invoices', 'parent_id')

    # Remove revision fields from quotations
    op.drop_column('quotations', 'revision_number')
    op.drop_column('quotations', 'parent_id')