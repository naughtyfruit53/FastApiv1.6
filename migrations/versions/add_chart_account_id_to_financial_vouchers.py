"""add chart_account_id to financial vouchers

Revision ID: add_chart_account_id_financial_vouchers
Revises: 76016d4a23bc
Create Date: 2024-12-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chart_account_id_financial_vouchers'
down_revision = '76016d4a23bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add chart_account_id column to payment_vouchers
    op.add_column('payment_vouchers', sa.Column('chart_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_payment_vouchers_chart_account_id', 'payment_vouchers', 'chart_of_accounts', ['chart_account_id'], ['id'])
    op.create_index('idx_pv_payment_chart_account', 'payment_vouchers', ['chart_account_id'])
    
    # Add chart_account_id column to receipt_vouchers
    op.add_column('receipt_vouchers', sa.Column('chart_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_receipt_vouchers_chart_account_id', 'receipt_vouchers', 'chart_of_accounts', ['chart_account_id'], ['id'])
    op.create_index('idx_rv_chart_account', 'receipt_vouchers', ['chart_account_id'])
    
    # Add chart_account_id column to contra_vouchers
    op.add_column('contra_vouchers', sa.Column('chart_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_contra_vouchers_chart_account_id', 'contra_vouchers', 'chart_of_accounts', ['chart_account_id'], ['id'])
    op.create_index('idx_contra_chart_account', 'contra_vouchers', ['chart_account_id'])
    
    # Add chart_account_id column to journal_vouchers
    op.add_column('journal_vouchers', sa.Column('chart_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_journal_vouchers_chart_account_id', 'journal_vouchers', 'chart_of_accounts', ['chart_account_id'], ['id'])
    op.create_index('idx_journal_chart_account', 'journal_vouchers', ['chart_account_id'])


def downgrade() -> None:
    # Remove indexes and foreign keys first, then columns
    op.drop_index('idx_journal_chart_account', 'journal_vouchers')
    op.drop_constraint('fk_journal_vouchers_chart_account_id', 'journal_vouchers', type_='foreignkey')
    op.drop_column('journal_vouchers', 'chart_account_id')
    
    op.drop_index('idx_contra_chart_account', 'contra_vouchers')
    op.drop_constraint('fk_contra_vouchers_chart_account_id', 'contra_vouchers', type_='foreignkey')
    op.drop_column('contra_vouchers', 'chart_account_id')
    
    op.drop_index('idx_rv_chart_account', 'receipt_vouchers')
    op.drop_constraint('fk_receipt_vouchers_chart_account_id', 'receipt_vouchers', type_='foreignkey')
    op.drop_column('receipt_vouchers', 'chart_account_id')
    
    op.drop_index('idx_pv_payment_chart_account', 'payment_vouchers')
    op.drop_constraint('fk_payment_vouchers_chart_account_id', 'payment_vouchers', type_='foreignkey')
    op.drop_column('payment_vouchers', 'chart_account_id')