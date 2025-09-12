"""Add business suite core modules

Revision ID: business_suite_core_modules
Revises: 3dcc06f2ad14
Create Date: 2024-12-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'business_suite_core_modules'
down_revision = '3dcc06f2ad14'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums using conditional SQL with proper values
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstatus') THEN
            CREATE TYPE projectstatus AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectpriority') THEN
            CREATE TYPE projectpriority AS ENUM ('low', 'medium', 'high', 'critical');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projecttype') THEN
            CREATE TYPE projecttype AS ENUM ('internal', 'client', 'research', 'maintenance', 'development');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'milestonestatus') THEN
            CREATE TYPE milestonestatus AS ENUM ('not_started', 'in_progress', 'completed', 'delayed');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resourcetype') THEN
            CREATE TYPE resourcetype AS ENUM ('human', 'equipment', 'material', 'budget');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflowstatus') THEN
            CREATE TYPE workflowstatus AS ENUM ('active', 'inactive', 'draft', 'archived');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflowtriggertype') THEN
            CREATE TYPE workflowtriggertype AS ENUM ('manual', 'automatic', 'scheduled', 'event_based');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approvalstatus') THEN
            CREATE TYPE approvalstatus AS ENUM ('pending', 'approved', 'rejected', 'delegated', 'escalated', 'cancelled');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'steptype') THEN
            CREATE TYPE steptype AS ENUM ('approval', 'notification', 'condition', 'action', 'parallel', 'sequential');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'instancestatus') THEN
            CREATE TYPE instancestatus AS ENUM ('created', 'in_progress', 'completed', 'failed', 'cancelled', 'paused');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'escalationaction') THEN
            CREATE TYPE escalationaction AS ENUM ('email', 'notification', 'reassign', 'auto_approve', 'escalate_to_manager');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'apikeystatus') THEN
            CREATE TYPE apikeystatus AS ENUM ('active', 'inactive', 'revoked', 'expired');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ratelimittype') THEN
            CREATE TYPE ratelimittype AS ENUM ('per_minute', 'per_hour', 'per_day', 'per_month');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'accesslevel') THEN
            CREATE TYPE accesslevel AS ENUM ('read_only', 'read_write', 'admin', 'full_access');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'loglevel') THEN
            CREATE TYPE loglevel AS ENUM ('info', 'warning', 'error', 'debug');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'webhookstatus') THEN
            CREATE TYPE webhookstatus AS ENUM ('active', 'inactive', 'failed');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'integrationtype') THEN
            CREATE TYPE integrationtype AS ENUM ('erp', 'crm', 'ecommerce', 'payment', 'shipping', 'accounting', 'email', 'sms', 'social_media', 'analytics', 'storage', 'communication', 'hr', 'marketing');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'integrationstatus') THEN
            CREATE TYPE integrationstatus AS ENUM ('active', 'inactive', 'failed', 'testing', 'maintenance');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'authtype') THEN
            CREATE TYPE authtype AS ENUM ('api_key', 'oauth2', 'oauth1', 'basic_auth', 'bearer_token', 'custom');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'syncdirection') THEN
            CREATE TYPE syncdirection AS ENUM ('inbound', 'outbound', 'bidirectional');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'syncstatus') THEN
            CREATE TYPE syncstatus AS ENUM ('success', 'failed', 'partial', 'in_progress');
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mappingtype') THEN
            CREATE TYPE mappingtype AS ENUM ('field', 'transformation', 'conditional', 'static');
        END IF;
    END $$;
    """)
    
    # Create Project Management tables
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('project_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_type', postgresql.ENUM('internal', 'client', 'research', 'maintenance', 'development', name='projecttype', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('planning', 'active', 'on_hold', 'completed', 'cancelled', name='projectstatus', create_type=False), nullable=False),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'critical', name='projectpriority', create_type=False), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('planned_start_date', sa.Date(), nullable=True),
        sa.Column('planned_end_date', sa.Date(), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('project_manager_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('is_billable', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['project_manager_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'project_code', name='uq_project_org_code')
    )
    op.create_index('idx_project_org_status', 'projects', ['organization_id', 'status'], unique=False)
    # op.create_index('idx_project_org_type', 'projects', ['organization_id', 'project_type'], unique=False)
    op.create_index('idx_project_org_manager', 'projects', ['organization_id', 'project_manager_id'], unique=False)
    op.create_index('idx_project_org_client', 'projects', ['organization_id', 'client_id'], unique=False)
    
    op.create_table(
        'project_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'completed', 'delayed', name='milestonestatus', create_type=False), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_milestone_org_project', 'project_milestones', ['organization_id', 'project_id'], unique=False)
    op.create_index('idx_milestone_org_status', 'project_milestones', ['organization_id', 'status'], unique=False)
    op.create_index('idx_milestone_org_target_date', 'project_milestones', ['organization_id', 'target_date'], unique=False)
    
    op.create_table(
        'project_resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', postgresql.ENUM('human', 'equipment', 'material', 'budget', name='resourcetype', create_type=False), nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('allocated_quantity', sa.Float(), nullable=False),
        sa.Column('used_quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('unit_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('allocation_start_date', sa.Date(), nullable=True),
        sa.Column('allocation_end_date', sa.Date(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_resource_org_project', 'project_resources', ['organization_id', 'project_id'], unique=False)
    op.create_index('idx_resource_org_type', 'project_resources', ['organization_id', 'resource_type'], unique=False)
    op.create_index('idx_resource_org_user', 'project_resources', ['organization_id', 'user_id'], unique=False)
    
    op.create_table(
        'project_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('document_name', sa.String(255), nullable=False),
        sa.Column('document_type', sa.String(100), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('version', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_document_org_project', 'project_documents', ['organization_id', 'project_id'], unique=False)
    op.create_index('idx_document_org_type', 'project_documents', ['organization_id', 'document_type'], unique=False)
    op.create_index('idx_document_org_public', 'project_documents', ['organization_id', 'is_public'], unique=False)
    
    op.create_table(
        'project_time_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('work_type', sa.String(100), nullable=True),
        sa.Column('is_billable', sa.Boolean(), nullable=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('billable_amount', sa.Float(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_timelog_org_project', 'project_time_logs', ['organization_id', 'project_id'], unique=False)
    op.create_index('idx_timelog_org_user', 'project_time_logs', ['organization_id', 'user_id'], unique=False)
    op.create_index('idx_timelog_org_date', 'project_time_logs', ['organization_id', 'start_time'], unique=False)
    op.create_index('idx_timelog_org_billable', 'project_time_logs', ['organization_id', 'is_billable'], unique=False)
    
    # Create Workflow Management tables
    op.create_table(
        'workflow_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'draft', 'archived', name='workflowstatus', create_type=False), nullable=False),
        sa.Column('trigger_type', postgresql.ENUM('manual', 'automatic', 'scheduled', 'event_based', name='workflowtriggertype', create_type=False), nullable=False),
        sa.Column('version', sa.String(20), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('allow_parallel_execution', sa.Boolean(), nullable=True),
        sa.Column('auto_complete', sa.Boolean(), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_conditions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', 'version', name='uq_workflow_template_org_name_version')
    )
    op.create_index('idx_workflow_template_org_category', 'workflow_templates', ['organization_id', 'category'], unique=False)
    op.create_index('idx_workflow_template_org_status', 'workflow_templates', ['organization_id', 'status'], unique=False)
    op.create_index('idx_workflow_template_org_entity', 'workflow_templates', ['organization_id', 'entity_type'], unique=False)
    
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=False),
        sa.Column('step_type', postgresql.ENUM('approval', 'notification', 'condition', 'action', 'parallel', 'sequential', name='steptype', create_type=False), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('allow_delegation', sa.Boolean(), nullable=True),
        sa.Column('allow_rejection', sa.Boolean(), nullable=True),
        sa.Column('assigned_role', sa.String(100), nullable=True),
        sa.Column('assigned_user_id', sa.Integer(), nullable=True),
        sa.Column('assignment_rules', sa.JSON(), nullable=True),
        sa.Column('condition_rules', sa.JSON(), nullable=True),
        sa.Column('parallel_group', sa.String(50), nullable=True),
        sa.Column('escalation_enabled', sa.Boolean(), nullable=True),
        sa.Column('escalation_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_action', postgresql.ENUM('email', 'notification', 'reassign', 'auto_approve', 'escalate_to_manager', name='escalationaction', create_type=False), nullable=True),
        sa.Column('escalation_to_user_id', sa.Integer(), nullable=True),
        sa.Column('notification_template', sa.Text(), nullable=True),
        sa.Column('send_email', sa.Boolean(), nullable=True),
        sa.Column('send_in_app', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['workflow_templates.id'], ),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalation_to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflow_step_org_template', 'workflow_steps', ['organization_id', 'template_id'], unique=False)
    op.create_index('idx_workflow_step_org_order', 'workflow_steps', ['organization_id', 'template_id', 'step_order'], unique=False)
    op.create_index('idx_workflow_step_org_type', 'workflow_steps', ['organization_id', 'step_type'], unique=False)


def downgrade():
    # Drop Workflow Management tables
    op.drop_index('idx_workflow_step_org_type', table_name='workflow_steps')
    op.drop_index('idx_workflow_step_org_order', table_name='workflow_steps')
    op.drop_index('idx_workflow_step_org_template', table_name='workflow_steps')
    op.drop_table('workflow_steps')
    op.drop_index('idx_workflow_template_org_entity', table_name='workflow_templates')
    op.drop_index('idx_workflow_template_org_status', table_name='workflow_templates')
    op.drop_index('idx_workflow_template_org_category', table_name='workflow_templates')
    op.drop_table('workflow_templates')
    # Drop Project Management tables
    op.drop_index('idx_timelog_org_billable', table_name='project_time_logs')
    op.drop_index('idx_timelog_org_date', table_name='project_time_logs')
    op.drop_index('idx_timelog_org_user', table_name='project_time_logs')
    op.drop_index('idx_timelog_org_project', table_name='project_time_logs')
    op.drop_table('project_time_logs')
    op.drop_index('idx_document_org_public', table_name='project_documents')
    op.drop_index('idx_document_org_type', table_name='project_documents')
    op.drop_index('idx_document_org_project', table_name='project_documents')
    op.drop_table('project_documents')
    op.drop_index('idx_resource_org_user', table_name='project_resources')
    op.drop_index('idx_resource_org_type', table_name='project_resources')
    op.drop_index('idx_resource_org_project', table_name='project_resources')
    op.drop_table('project_resources')
    op.drop_index('idx_milestone_org_target_date', table_name='project_milestones')
    op.drop_index('idx_milestone_org_status', table_name='project_milestones')
    op.drop_index('idx_milestone_org_project', table_name='project_milestones')
    op.drop_table('project_milestones')
    op.drop_index('idx_project_org_client', table_name='projects')
    op.drop_index('idx_project_org_manager', table_name='projects')
    op.drop_index('idx_project_org_type', table_name='projects')
    op.drop_index('idx_project_org_status', table_name='projects')
    op.drop_table('projects')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS mappingtype")
    op.execute("DROP TYPE IF EXISTS syncstatus")
    op.execute("DROP TYPE IF EXISTS syncdirection")
    op.execute("DROP TYPE IF EXISTS authtype")
    op.execute("DROP TYPE IF EXISTS integrationstatus")
    op.execute("DROP TYPE IF EXISTS integrationtype")
    op.execute("DROP TYPE IF EXISTS webhookstatus")
    op.execute("DROP TYPE IF EXISTS loglevel")
    op.execute("DROP TYPE IF EXISTS accesslevel")
    op.execute("DROP TYPE IF EXISTS ratelimittype")
    op.execute("DROP TYPE IF EXISTS apikeystatus")
    op.execute("DROP TYPE IF EXISTS escalationaction")
    op.execute("DROP TYPE IF EXISTS instancestatus")
    op.execute("DROP TYPE IF EXISTS steptype")
    op.execute("DROP TYPE IF EXISTS approvalstatus")
    op.execute("DROP TYPE IF EXISTS workflowtriggertype")
    op.execute("DROP TYPE IF EXISTS workflowstatus")
    op.execute("DROP TYPE IF EXISTS resourcetype")
    op.execute("DROP TYPE IF EXISTS milestonestatus")
    op.execute("DROP TYPE IF EXISTS projecttype")
    op.execute("DROP TYPE IF EXISTS projectpriority")
    op.execute("DROP TYPE IF EXISTS projectstatus")
