"""add_website_agent_tables

Revision ID: add_website_agent_20251022
Revises: None
Create Date: 2025-10-22 02:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_website_agent_20251022'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create website_projects table
    op.create_table(
        'website_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('project_type', sa.String(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('subdomain', sa.String(), nullable=True),
        sa.Column('theme', sa.String(), nullable=False),
        sa.Column('primary_color', sa.String(), nullable=True),
        sa.Column('secondary_color', sa.String(), nullable=True),
        sa.Column('site_title', sa.String(), nullable=True),
        sa.Column('site_description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('favicon_url', sa.String(), nullable=True),
        sa.Column('pages_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('seo_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('analytics_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('deployment_url', sa.String(), nullable=True),
        sa.Column('deployment_provider', sa.String(), nullable=True),
        sa.Column('last_deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('chatbot_enabled', sa.Boolean(), nullable=False),
        sa.Column('chatbot_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_website_project_organization_id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_website_project_customer_id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_website_project_created_by_id'),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], name='fk_website_project_updated_by_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'project_name', name='uq_website_project_org_name')
    )
    op.create_index('idx_website_project_org_status', 'website_projects', ['organization_id', 'status'])
    op.create_index('idx_website_project_org_type', 'website_projects', ['organization_id', 'project_type'])
    op.create_index('idx_website_project_customer', 'website_projects', ['customer_id'])
    op.create_index('idx_website_project_created_at', 'website_projects', ['created_at'])
    op.create_index(op.f('ix_website_projects_id'), 'website_projects', ['id'])
    op.create_index(op.f('ix_website_projects_organization_id'), 'website_projects', ['organization_id'])
    op.create_index(op.f('ix_website_projects_project_name'), 'website_projects', ['project_name'])

    # Create website_pages table
    op.create_table(
        'website_pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('page_name', sa.String(), nullable=False),
        sa.Column('page_slug', sa.String(), nullable=False),
        sa.Column('page_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sections_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('seo_keywords', sa.Text(), nullable=True),
        sa.Column('og_image', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_website_page_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['website_projects.id'], name='fk_website_page_project_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'page_slug', name='uq_website_page_project_slug')
    )
    op.create_index('idx_website_page_org_project', 'website_pages', ['organization_id', 'project_id'])
    op.create_index('idx_website_page_type', 'website_pages', ['page_type'])
    op.create_index('idx_website_page_published', 'website_pages', ['is_published'])
    op.create_index('idx_website_page_order', 'website_pages', ['project_id', 'order_index'])
    op.create_index(op.f('ix_website_pages_id'), 'website_pages', ['id'])
    op.create_index(op.f('ix_website_pages_organization_id'), 'website_pages', ['organization_id'])

    # Create website_deployments table
    op.create_table(
        'website_deployments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('deployment_version', sa.String(), nullable=False),
        sa.Column('deployment_status', sa.String(), nullable=False),
        sa.Column('deployment_url', sa.String(), nullable=True),
        sa.Column('deployment_provider', sa.String(), nullable=False),
        sa.Column('deployment_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('deployment_log', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deployed_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_website_deployment_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['website_projects.id'], name='fk_website_deployment_project_id'),
        sa.ForeignKeyConstraint(['deployed_by_id'], ['users.id'], name='fk_website_deployment_deployed_by_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_website_deployment_org_project', 'website_deployments', ['organization_id', 'project_id'])
    op.create_index('idx_website_deployment_status', 'website_deployments', ['deployment_status'])
    op.create_index('idx_website_deployment_created', 'website_deployments', ['created_at'])
    op.create_index(op.f('ix_website_deployments_id'), 'website_deployments', ['id'])
    op.create_index(op.f('ix_website_deployments_organization_id'), 'website_deployments', ['organization_id'])

    # Create website_maintenance_logs table
    op.create_table(
        'website_maintenance_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        sa.Column('files_affected', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('automated', sa.Boolean(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('performed_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_website_maintenance_log_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['website_projects.id'], name='fk_website_maintenance_log_project_id'),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'], name='fk_website_maintenance_log_performed_by_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_website_maintenance_log_org_project', 'website_maintenance_logs', ['organization_id', 'project_id'])
    op.create_index('idx_website_maintenance_log_type', 'website_maintenance_logs', ['maintenance_type'])
    op.create_index('idx_website_maintenance_log_status', 'website_maintenance_logs', ['status'])
    op.create_index('idx_website_maintenance_log_created', 'website_maintenance_logs', ['created_at'])
    op.create_index('idx_website_maintenance_log_automated', 'website_maintenance_logs', ['automated'])
    op.create_index(op.f('ix_website_maintenance_logs_id'), 'website_maintenance_logs', ['id'])
    op.create_index(op.f('ix_website_maintenance_logs_organization_id'), 'website_maintenance_logs', ['organization_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('website_maintenance_logs')
    op.drop_table('website_deployments')
    op.drop_table('website_pages')
    op.drop_table('website_projects')