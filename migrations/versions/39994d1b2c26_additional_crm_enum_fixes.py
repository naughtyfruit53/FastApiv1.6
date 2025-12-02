"""additional crm enum fixes

Revision ID: 39994d1b2c26
Revises: 4b47ca04f4a4
Create Date: 2025-12-02 14:56:08.978704

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '39994d1b2c26'
down_revision = '4b47ca04f4a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Temporary alter to TEXT for safe updates
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE TEXT")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE TEXT")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE TEXT")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE TEXT")

    # Update data to uppercase
    op.execute("UPDATE leads SET status = UPPER(status)")
    op.execute("UPDATE leads SET source = UPPER(source)")
    op.execute("UPDATE opportunities SET stage = UPPER(stage)")
    op.execute("UPDATE opportunities SET source = UPPER(source)")

    # Drop old enum types if exist
    op.execute("DROP TYPE IF EXISTS leadstatus")
    op.execute("DROP TYPE IF EXISTS leadsource")
    op.execute("DROP TYPE IF EXISTS opportunitystage")

    # Create new enum types with uppercase values
    op.execute("CREATE TYPE leadstatus AS ENUM ('NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CONVERTED', 'LOST', 'NURTURING')")
    op.execute("CREATE TYPE leadsource AS ENUM ('WEBSITE', 'REFERRAL', 'EMAIL_CAMPAIGN', 'SOCIAL_MEDIA', 'COLD_CALL', 'TRADE_SHOW', 'PARTNER', 'ADVERTISEMENT', 'OTHER')")
    op.execute("CREATE TYPE opportunitystage AS ENUM ('PROSPECTING', 'QUALIFICATION', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST')")

    # Alter back to new enums
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE leadstatus USING status::leadstatus")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE leadsource USING source::leadsource")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE opportunitystage USING stage::opportunitystage")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE leadsource USING source::leadsource")

def downgrade() -> None:
    # Temporary alter to TEXT for downgrade
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE TEXT")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE TEXT")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE TEXT")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE TEXT")

    # Update data back to lowercase
    op.execute("UPDATE leads SET status = LOWER(status)")
    op.execute("UPDATE leads SET source = LOWER(source)")
    op.execute("UPDATE opportunities SET stage = LOWER(stage)")
    op.execute("UPDATE opportunities SET source = LOWER(source)")

    # Drop new enum types
    op.execute("DROP TYPE IF EXISTS leadstatus")
    op.execute("DROP TYPE IF EXISTS leadsource")
    op.execute("DROP TYPE IF EXISTS opportunitystage")

    # Recreate old enum types with lowercase values
    op.execute("CREATE TYPE leadstatus AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'converted', 'lost', 'nurturing')")
    op.execute("CREATE TYPE leadsource AS ENUM ('website', 'referral', 'email_campaign', 'social_media', 'cold_call', 'trade_show', 'partner', 'advertisement', 'other')")
    op.execute("CREATE TYPE opportunitystage AS ENUM ('prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost')")

    # Alter back to old enums
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE leadstatus USING status::leadstatus")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE leadsource USING source::leadsource")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE opportunitystage USING stage::opportunitystage")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE leadsource USING source::leadsource")