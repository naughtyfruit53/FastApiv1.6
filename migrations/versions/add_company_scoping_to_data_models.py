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
    
    # Add company_id to vendors table
    op.add_column('vendors', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_vendor_company_id', 'vendors', 'companies', ['company_id'], ['id'])
    op.create_index('idx_vendor_company', 'vendors', ['company_id'])
    
    # Add company_id to customers table
    op.add_column('customers', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_customer_company_id', 'customers', 'companies', ['company_id'], ['id'])
    op.create_index('idx_customer_company', 'customers', ['company_id'])
    
    # Add company_id to products table
    op.add_column('products', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_product_company_id', 'products', 'companies', ['company_id'], ['id'])
    op.create_index('idx_product_company', 'products', ['company_id'])
    
    # Data migration: Associate existing records with the first company in each organization
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
    
    # Update vendors for single-company organizations
    connection.execute(sa.text("""
        UPDATE vendors 
        SET company_id = (
            SELECT c.id 
            FROM companies c 
            WHERE c.organization_id = vendors.organization_id 
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
    
    # Update customers for single-company organizations
    connection.execute(sa.text("""
        UPDATE customers 
        SET company_id = (
            SELECT c.id 
            FROM companies c 
            WHERE c.organization_id = customers.organization_id 
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
    
    # Update products for single-company organizations
    connection.execute(sa.text("""
        UPDATE products 
        SET company_id = (
            SELECT c.id 
            FROM companies c 
            WHERE c.organization_id = products.organization_id 
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
    # Drop foreign keys and indexes for products
    op.drop_index('idx_product_company', 'products')
    op.drop_constraint('fk_product_company_id', 'products', type_='foreignkey')
    op.drop_column('products', 'company_id')
    
    # Drop foreign keys and indexes for customers
    op.drop_index('idx_customer_company', 'customers')
    op.drop_constraint('fk_customer_company_id', 'customers', type_='foreignkey')
    op.drop_column('customers', 'company_id')
    
    # Drop foreign keys and indexes for vendors
    op.drop_index('idx_vendor_company', 'vendors')
    op.drop_constraint('fk_vendor_company_id', 'vendors', type_='foreignkey')
    op.drop_column('vendors', 'company_id')
    
    # Drop foreign keys and indexes for task_projects
    op.drop_index('idx_task_project_company', 'task_projects')
    op.drop_constraint('fk_task_project_company_id', 'task_projects', type_='foreignkey')
    op.drop_column('task_projects', 'company_id')
    
    # Drop foreign keys and indexes for tasks
    op.drop_index('idx_task_company', 'tasks')
    op.drop_constraint('fk_task_company_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'company_id')