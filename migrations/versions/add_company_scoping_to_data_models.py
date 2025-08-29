"""add company scoping to data models

Revision ID: add_company_scoping_to_data_models
Revises: add_multicompany_support_002
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_company_scoping_to_data_models'
down_revision = 'add_multicompany_support_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add company_id to tasks table
    op.add_column('tasks', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_company_id', 'tasks', 'companies', ['company_id'], ['id'])
    op.create_index('idx_task_company', 'tasks', ['company_id'])
    
    # Add company_id to task_projects table
    op.add_column('task_projects', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_project_company_id', 'task_projects', 'companies', ['company_id'], ['id'])
    op.create_index('idx_task_project_company', 'task_projects', ['company_id'])
    
    # Data migration: Associate existing tasks and projects with the first company in each organization
    # For organizations with only one company, assign all records to that company
    # For organizations with multiple companies, leave company_id as NULL (admin will need to assign manually)
    
    # Create a temporary view to help with data migration
    connection = op.get_bind()
    
    # Update tasks for single-company organizations
    connection.execute(sa.text("""
        UPDATE tasks 
        SET company_id = (
            SELECT c.id 
            FROM companies c 
            WHERE c.organization_id = tasks.organization_id 
            AND c.id = (
                SELECT MIN(id) 
                FROM companies 
                WHERE organization_id = c.organization_id
            )
        )
        WHERE organization_id IN (
            SELECT organization_id 
            FROM companies 
            GROUP BY organization_id 
            HAVING COUNT(*) = 1
        )
    """))
    
    # Update task_projects for single-company organizations
    connection.execute(sa.text("""
        UPDATE task_projects 
        SET company_id = (
            SELECT c.id 
            FROM companies c 
            WHERE c.organization_id = task_projects.organization_id 
            AND c.id = (
                SELECT MIN(id) 
                FROM companies 
                WHERE organization_id = c.organization_id
            )
        )
        WHERE organization_id IN (
            SELECT organization_id 
            FROM companies 
            GROUP BY organization_id 
            HAVING COUNT(*) = 1
        )
    """))


def downgrade() -> None:
    # Drop foreign keys and indexes
    op.drop_index('idx_task_project_company', 'task_projects')
    op.drop_constraint('fk_task_project_company_id', 'task_projects', type_='foreignkey')
    op.drop_column('task_projects', 'company_id')
    
    op.drop_index('idx_task_company', 'tasks')
    op.drop_constraint('fk_task_company_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'company_id')