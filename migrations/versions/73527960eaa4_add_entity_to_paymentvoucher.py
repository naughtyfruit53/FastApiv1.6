"""Add entity to PaymentVoucher

Revision ID: 73527960eaa4
Revises: 3bc2f13cdd2f
Create Date: 2025-09-15 10:06:02.288431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73527960eaa4'
down_revision = '3bc2f13cdd2f'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns as nullable first
    op.add_column('payment_vouchers', sa.Column('entity_id', sa.Integer(), nullable=True))
    op.add_column('payment_vouchers', sa.Column('entity_type', sa.String(length=50), nullable=True))
    
    # Data migration: Set entity_id to vendor_id and entity_type to 'Vendor' for existing records
    op.execute(
        "UPDATE payment_vouchers SET entity_id = vendor_id, entity_type = 'Vendor' WHERE vendor_id IS NOT NULL"
    )
    
    # Handle rows where vendor_id is NULL (if any, set to 0 or handle as needed; assuming no NULLs, but to be safe)
    op.execute(
        "UPDATE payment_vouchers SET entity_id = 0, entity_type = 'Unknown' WHERE entity_id IS NULL"
    )
    
    # Now alter columns to NOT NULL
    op.alter_column('payment_vouchers', 'entity_id', nullable=False)
    op.alter_column('payment_vouchers', 'entity_type', nullable=False)
    
    # Drop the foreign key constraint
    op.drop_constraint('payment_vouchers_vendor_id_fkey', 'payment_vouchers', type_='foreignkey')
    
    # Drop old column
    op.drop_column('payment_vouchers', 'vendor_id')
    
    # Drop old index if exists
    op.execute("DROP INDEX IF EXISTS idx_pv_payment_org_vendor")
    
    # Create new index
    op.create_index('idx_pv_payment_org_entity', 'payment_vouchers', ['organization_id', 'entity_id'], unique=False)


def downgrade():
    # Add old column as nullable first
    op.add_column('payment_vouchers', sa.Column('vendor_id', sa.INTEGER(), autoincrement=False, nullable=True))
    
    # Data migration back: Set vendor_id to entity_id where entity_type = 'Vendor'
    op.execute(
        "UPDATE payment_vouchers SET vendor_id = entity_id WHERE entity_type = 'Vendor'"
    )
    
    # Alter to NOT NULL
    op.alter_column('payment_vouchers', 'vendor_id', nullable=False)
    
    # Create foreign key back
    op.create_foreign_key('payment_vouchers_vendor_id_fkey', 'payment_vouchers', 'vendors', ['vendor_id'], ['id'])
    
    # Drop new columns
    op.drop_column('payment_vouchers', 'entity_type')
    op.drop_column('payment_vouchers', 'entity_id')
    
    # Drop new index if exists
    op.execute("DROP INDEX IF EXISTS idx_pv_payment_org_entity")
    
    # Create old index back
    op.create_index('idx_pv_payment_org_vendor', 'payment_vouchers', ['organization_id', 'vendor_id'], unique=False)