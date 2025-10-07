"""empty message

Revision ID: 5693912f1c33
Revises: 855ffa9ab2ff, add_email_scheduling_analytics
Create Date: 2025-10-07 12:46:15.922577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5693912f1c33'
down_revision = ('855ffa9ab2ff', 'add_email_scheduling_analytics')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass