"""enforce state_code NOT NULL for GST compliance

Revision ID: 001_state_code_not_null
Revises: 
Create Date: 2025-11-03

This migration ensures that state_code is NOT NULL in organizations, customers, and vendors tables.
This is required for strict GST enforcement across all voucher endpoints.

IMPORTANT: Before running this migration:
1. Ensure all existing organizations have state_code populated
2. Ensure all existing customers have state_code populated
3. Ensure all existing vendors have state_code populated

You can run data validation queries to check:
  SELECT COUNT(*) FROM organizations WHERE state_code IS NULL OR state_code = '';
  SELECT COUNT(*) FROM customers WHERE state_code IS NULL OR state_code = '';
  SELECT COUNT(*) FROM vendors WHERE state_code IS NULL OR state_code = '';

If any records are missing state_code, update them first before running this migration.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_state_code_not_null'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Apply the migration: Make state_code NOT NULL
    
    NOTE: The models already define state_code as NOT NULL.
    This migration is primarily for documentation and validation.
    If you have existing NULL values, this will fail - fix the data first.
    """
    
    # Check if any NULL values exist and raise error if found
    conn = op.get_bind()
    
    # Check organizations
    result = conn.execute(sa.text(
        "SELECT COUNT(*) as cnt FROM organizations WHERE state_code IS NULL OR state_code = ''"
    ))
    org_nulls = result.scalar()
    if org_nulls > 0:
        raise ValueError(
            f"Found {org_nulls} organizations with missing state_code. "
            "Please update all organizations with valid state codes before running this migration."
        )
    
    # Check customers
    result = conn.execute(sa.text(
        "SELECT COUNT(*) as cnt FROM customers WHERE state_code IS NULL OR state_code = ''"
    ))
    cust_nulls = result.scalar()
    if cust_nulls > 0:
        raise ValueError(
            f"Found {cust_nulls} customers with missing state_code. "
            "Please update all customers with valid state codes before running this migration."
        )
    
    # Check vendors
    result = conn.execute(sa.text(
        "SELECT COUNT(*) as cnt FROM vendors WHERE state_code IS NULL OR state_code = ''"
    ))
    vendor_nulls = result.scalar()
    if vendor_nulls > 0:
        raise ValueError(
            f"Found {vendor_nulls} vendors with missing state_code. "
            "Please update all vendors with valid state codes before running this migration."
        )
    
    # If we got here, all data is clean - apply NOT NULL constraints
    # (Note: Models already define NOT NULL, but we can add explicit constraints)
    
    op.alter_column('organizations', 'state_code',
                    existing_type=sa.String(),
                    nullable=False,
                    existing_nullable=True)
    
    op.alter_column('customers', 'state_code',
                    existing_type=sa.String(),
                    nullable=False,
                    existing_nullable=True)
    
    op.alter_column('vendors', 'state_code',
                    existing_type=sa.String(),
                    nullable=False,
                    existing_nullable=True)


def downgrade():
    """
    Revert the migration: Allow NULL state_code (NOT RECOMMENDED)
    
    WARNING: This will disable strict GST enforcement and may cause issues
    with voucher creation. Only use this if absolutely necessary.
    """
    
    op.alter_column('organizations', 'state_code',
                    existing_type=sa.String(),
                    nullable=True,
                    existing_nullable=False)
    
    op.alter_column('customers', 'state_code',
                    existing_type=sa.String(),
                    nullable=True,
                    existing_nullable=False)
    
    op.alter_column('vendors', 'state_code',
                    existing_type=sa.String(),
                    nullable=True,
                    existing_nullable=False)
