"""add task_project_id to tasks

Revision ID: 66e977082c1c
Revises: 48774b137dfb
Create Date: 2025-09-08 17:02:08.680789

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '66e977082c1c'
down_revision = '48774b137dfb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('task_project_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'task_projects', ['task_project_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'task_project_id')