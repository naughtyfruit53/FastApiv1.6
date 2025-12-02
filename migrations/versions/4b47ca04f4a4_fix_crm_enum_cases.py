# migrations/versions/4b47ca04f4a4_fix_crm_enum_cases.py

"""fix crm enum cases
Revision ID: 4b47ca04f4a4
Revises: 1862ae9d20c2
Create Date: 2025-12-02 14:41:26.936047
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '4b47ca04f4a4'
down_revision = '1862ae9d20c2'

def upgrade() -> None:
    # Update existing data to uppercase with proper casting
    op.execute("UPDATE leads SET status = UPPER(status::text)::leadstatus")
    op.execute("UPDATE leads SET source = UPPER(source::text)::leadsource")
    op.execute("UPDATE opportunities SET stage = UPPER(stage::text)::opportunitystage")
    op.execute("UPDATE opportunities SET source = UPPER(source::text)::leadsource")

    # Rename old enums
    op.execute("ALTER TYPE leadstatus RENAME TO leadstatus_old")
    op.execute("ALTER TYPE leadsource RENAME TO leadsource_old")
    op.execute("ALTER TYPE opportunitystage RENAME TO opportunitystage_old")

    # Create new enums with uppercase values
    op.execute("CREATE TYPE leadstatus AS ENUM ('NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CONVERTED', 'LOST', 'NURTURING')")
    op.execute("CREATE TYPE leadsource AS ENUM ('WEBSITE', 'REFERRAL', 'EMAIL_CAMPAIGN', 'SOCIAL_MEDIA', 'COLD_CALL', 'TRADE_SHOW', 'PARTNER', 'ADVERTISEMENT', 'OTHER')")
    op.execute("CREATE TYPE opportunitystage AS ENUM ('PROSPECTING', 'QUALIFICATION', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST')")

    # Alter columns to use new enums
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE leadstatus USING status::text::leadstatus")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE leadsource USING source::text::leadsource")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE opportunitystage USING stage::text::opportunitystage")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE leadsource USING source::text::leadsource")

    # Drop old enums
    op.execute("DROP TYPE leadstatus_old")
    op.execute("DROP TYPE leadsource_old")
    op.execute("DROP TYPE opportunitystage_old")

def downgrade() -> None:
    # Reverse the enum changes
    op.execute("UPDATE leads SET status = LOWER(status::text)::leadstatus")
    op.execute("UPDATE leads SET source = LOWER(source::text)::leadsource")
    op.execute("UPDATE opportunities SET stage = LOWER(stage::text)::opportunitystage")
    op.execute("UPDATE opportunities SET source = LOWER(source::text)::leadsource")

    op.execute("ALTER TYPE leadstatus RENAME TO leadstatus_new")
    op.execute("ALTER TYPE leadsource RENAME TO leadsource_new")
    op.execute("ALTER TYPE opportunitystage RENAME TO opportunitystage_new")

    op.execute("CREATE TYPE leadstatus AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'converted', 'lost', 'nurturing')")
    op.execute("CREATE TYPE leadsource AS ENUM ('website', 'referral', 'email_campaign', 'social_media', 'cold_call', 'trade_show', 'partner', 'advertisement', 'other')")
    op.execute("CREATE TYPE opportunitystage AS ENUM ('prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost')")

    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE leadstatus USING status::text::leadstatus")
    op.execute("ALTER TABLE leads ALTER COLUMN source TYPE leadsource USING source::text::leadsource")
    op.execute("ALTER TABLE opportunities ALTER COLUMN stage TYPE opportunitystage USING stage::text::opportunitystage")
    op.execute("ALTER TABLE opportunities ALTER COLUMN source TYPE leadsource USING source::text::leadsource")

    op.execute("DROP TYPE leadstatus_new")
    op.execute("DROP TYPE leadsource_new")
    op.execute("DROP TYPE opportunitystage_new")