"""empty message

Revision ID: 22038f457955
Revises: 552db06e45b2, add_provider_message_id_to_emails
Create Date: 2025-10-01 20:16:06.240436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22038f457955'
down_revision = ('552db06e45b2', 'add_provider_message_id_to_emails')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass