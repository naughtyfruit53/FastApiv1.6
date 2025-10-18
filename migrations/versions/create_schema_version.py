# migrations/versions/create_schema_version.py

from sqlalchemy import Column, Integer, String
from alembic import op

# Revision identifiers, used by Alembic
revision = '2025101901_create_schema_version'  # Unique revision ID
down_revision = None  # Adjust if other migrations exist
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'schema_version',
        Column('id', Integer, primary_key=True),
        Column('version', String, nullable=False)
    )
    op.execute("INSERT INTO schema_version (version) VALUES ('1.0')")

def downgrade():
    op.drop_table('schema_version')