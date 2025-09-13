"""Add discount fields to quotation_items without product_id

Revision ID: 8c40a7ce3604
Revises: 2cd9a7ce3604
Create Date: 2025-09-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c40a7ce3604'
down_revision = '2cd9a7ce3604'
branch_labels = None
depends_on = None


def upgrade():
    # Conditional addition of columns to avoid DuplicateColumn errors
    # Check if column exists before adding
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'discount_percentage') THEN
                ALTER TABLE quotation_items ADD COLUMN discount_percentage FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'gst_rate') THEN
                ALTER TABLE quotation_items ADD COLUMN gst_rate FLOAT NOT NULL DEFAULT 18.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'discount_amount') THEN
                ALTER TABLE quotation_items ADD COLUMN discount_amount FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'taxable_amount') THEN
                ALTER TABLE quotation_items ADD COLUMN taxable_amount FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'cgst_amount') THEN
                ALTER TABLE quotation_items ADD COLUMN cgst_amount FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'sgst_amount') THEN
                ALTER TABLE quotation_items ADD COLUMN sgst_amount FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'igst_amount') THEN
                ALTER TABLE quotation_items ADD COLUMN igst_amount FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_attribute 
                           WHERE attrelid = 'quotation_items'::regclass 
                           AND attname = 'description') THEN
                ALTER TABLE quotation_items ADD COLUMN description TEXT;
            END IF;
        END $$;
    """)


def downgrade():
    # Conditional removal of columns
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'description') THEN
                ALTER TABLE quotation_items DROP COLUMN description;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'igst_amount') THEN
                ALTER TABLE quotation_items DROP COLUMN igst_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'sgst_amount') THEN
                ALTER TABLE quotation_items DROP COLUMN sgst_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'cgst_amount') THEN
                ALTER TABLE quotation_items DROP COLUMN cgst_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'taxable_amount') THEN
                ALTER TABLE quotation_items DROP COLUMN taxable_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'discount_amount') THEN
                ALTER TABLE quotation_items DROP COLUMN discount_amount;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'gst_rate') THEN
                ALTER TABLE quotation_items DROP COLUMN gst_rate;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_attribute 
                       WHERE attrelid = 'quotation_items'::regclass 
                       AND attname = 'discount_percentage') THEN
                ALTER TABLE quotation_items DROP COLUMN discount_percentage;
            END IF;
        END $$;
    """)