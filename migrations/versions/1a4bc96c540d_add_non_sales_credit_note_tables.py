"""Add non_sales_credit_note tables

Revision ID: 1a4bc96c540d
Revises: 493b76db19da
Create Date: 2025-10-24 21:27:43.398374

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a4bc96c540d'
down_revision = '493b76db19da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create non_sales_credit_notes table
    op.create_table('non_sales_credit_notes',
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('chart_account_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('voucher_number', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('cgst_amount', sa.Float(), nullable=True),
        sa.Column('sgst_amount', sa.Float(), nullable=True),
        sa.Column('igst_amount', sa.Float(), nullable=True),
        sa.Column('discount_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['chart_account_id'], ['chart_of_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'voucher_number', name='uq_nscn_org_voucher_number')
    )
    op.create_index('idx_nscn_chart_account', 'non_sales_credit_notes', ['chart_account_id'], unique=False)
    op.create_index('idx_nscn_org_date', 'non_sales_credit_notes', ['organization_id', 'date'], unique=False)
    op.create_index(op.f('ix_non_sales_credit_notes_chart_account_id'), 'non_sales_credit_notes', ['chart_account_id'], unique=False)
    op.create_index(op.f('ix_non_sales_credit_notes_id'), 'non_sales_credit_notes', ['id'], unique=False)
    op.create_index(op.f('ix_non_sales_credit_notes_organization_id'), 'non_sales_credit_notes', ['organization_id'], unique=False)
    op.create_index(op.f('ix_non_sales_credit_notes_voucher_number'), 'non_sales_credit_notes', ['voucher_number'], unique=False)

    # Create non_sales_credit_note_items table
    op.create_table('non_sales_credit_note_items',
        sa.Column('non_sales_credit_note_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['non_sales_credit_note_id'], ['non_sales_credit_notes.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_non_sales_credit_note_items_id'), 'non_sales_credit_note_items', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_non_sales_credit_note_items_id'), table_name='non_sales_credit_note_items')
    op.drop_table('non_sales_credit_note_items')
    op.drop_index(op.f('ix_non_sales_credit_notes_voucher_number'), table_name='non_sales_credit_notes')
    op.drop_index(op.f('ix_non_sales_credit_notes_organization_id'), table_name='non_sales_credit_notes')
    op.drop_index(op.f('ix_non_sales_credit_notes_id'), table_name='non_sales_credit_notes')
    op.drop_index(op.f('ix_non_sales_credit_notes_chart_account_id'), table_name='non_sales_credit_notes')
    op.drop_index('idx_nscn_org_date', table_name='non_sales_credit_notes')
    op.drop_index('idx_nscn_chart_account', table_name='non_sales_credit_notes')
    op.drop_table('non_sales_credit_notes')