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
    # Create enums for new models
    
    # Project Management enums
    project_status_enum = postgresql.ENUM('planning', 'active', 'on_hold', 'completed', 'cancelled', name='projectstatus')
    project_priority_enum = postgresql.ENUM('low', 'medium', 'high', 'critical', name='projectpriority')
    project_type_enum = postgresql.ENUM('internal', 'client', 'research', 'maintenance', 'development', name='projecttype')
    milestone_status_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', 'delayed', name='milestonestatus')
    resource_type_enum = postgresql.ENUM('human', 'equipment', 'material', 'budget', name='resourcetype')
    
    project_status_enum.create(op.get_bind())
    project_priority_enum.create(op.get_bind())
    project_type_enum.create(op.get_bind())
    milestone_status_enum.create(op.get_bind())
    resource_type_enum.create(op.get_bind())
    
    # Workflow enums
    workflow_status_enum = postgresql.ENUM('active', 'inactive', 'draft', 'archived', name='workflowstatus')
    workflow_trigger_type_enum = postgresql.ENUM('manual', 'automatic', 'scheduled', 'event_based', name='workflowtriggertype')
    approval_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'delegated', 'escalated', 'cancelled', name='approvalstatus')
    step_type_enum = postgresql.ENUM('approval', 'notification', 'condition', 'action', 'parallel', 'sequential', name='steptype')
    instance_status_enum = postgresql.ENUM('created', 'in_progress', 'completed', 'failed', 'cancelled', 'paused', name='instancestatus')
    escalation_action_enum = postgresql.ENUM('email', 'notification', 'reassign', 'auto_approve', 'escalate_to_manager', name='escalationaction')
    
    workflow_status_enum.create(op.get_bind())
    workflow_trigger_type_enum.create(op.get_bind())
    approval_status_enum.create(op.get_bind())
    step_type_enum.create(op.get_bind())
    instance_status_enum.create(op.get_bind())
    escalation_action_enum.create(op.get_bind())
    
    # API Gateway enums
    api_key_status_enum = postgresql.ENUM('active', 'inactive', 'revoked', 'expired', name='apikeystatus')
    rate_limit_type_enum = postgresql.ENUM('per_minute', 'per_hour', 'per_day', 'per_month', name='ratelimittype')
    access_level_enum = postgresql.ENUM('read_only', 'read_write', 'admin', 'full_access', name='accesslevel')
    log_level_enum = postgresql.ENUM('info', 'warning', 'error', 'debug', name='loglevel')
    webhook_status_enum = postgresql.ENUM('active', 'inactive', 'failed', name='webhookstatus')
    
    api_key_status_enum.create(op.get_bind())
    rate_limit_type_enum.create(op.get_bind())
    access_level_enum.create(op.get_bind())
    log_level_enum.create(op.get_bind())
    webhook_status_enum.create(op.get_bind())
    
    # Integration enums
    integration_type_enum = postgresql.ENUM('erp', 'crm', 'ecommerce', 'payment', 'shipping', 'accounting', 'email', 'sms', 'social_media', 'analytics', 'storage', 'communication', 'hr', 'marketing', name='integrationtype')
    integration_status_enum = postgresql.ENUM('active', 'inactive', 'failed', 'testing', 'maintenance', name='integrationstatus')
    auth_type_enum = postgresql.ENUM('api_key', 'oauth2', 'oauth1', 'basic_auth', 'bearer_token', 'custom', name='authtype')
    sync_direction_enum = postgresql.ENUM('inbound', 'outbound', 'bidirectional', name='syncdirection')
    sync_status_enum = postgresql.ENUM('success', 'failed', 'partial', 'in_progress', name='syncstatus')
    mapping_type_enum = postgresql.ENUM('field', 'transformation', 'conditional', 'static', name='mappingtype')
    
    integration_type_enum.create(op.get_bind())
    integration_status_enum.create(op.get_bind())
    auth_type_enum.create(op.get_bind())
    sync_direction_enum.create(op.get_bind())
    sync_status_enum.create(op.get_bind())
    mapping_type_enum.create(op.get_bind())
    
    # Create Project Management tables
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('project_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_type', project_type_enum, nullable=False, default='internal'),
        sa.Column('status', project_status_enum, nullable=False, default='planning'),
        sa.Column('priority', project_priority_enum, nullable=False, default='medium'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('planned_start_date', sa.Date(), nullable=True),
        sa.Column('planned_end_date', sa.Date(), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True, default=0.0),
        sa.Column('actual_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('project_manager_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('is_billable', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_project_organization_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_project_company_id'),
        sa.ForeignKeyConstraint(['client_id'], ['customers.id'], name='fk_project_client_id'),
        sa.ForeignKeyConstraint(['project_manager_id'], ['users.id'], name='fk_project_manager_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_project_created_by'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'project_code', name='uq_project_org_code')
    )
    op.create_index('idx_project_org_status', 'projects', ['organization_id', 'status'])
    op.create_index('idx_project_org_type', 'projects', ['organization_id', 'project_type'])
    op.create_index('idx_project_org_manager', 'projects', ['organization_id', 'project_manager_id'])
    op.create_index('idx_project_org_client', 'projects', ['organization_id', 'client_id'])
    
    op.create_table(
        'project_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', milestone_status_enum, nullable=False, default='not_started'),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_milestone_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_milestone_project_id'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name='fk_milestone_assigned_to'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_milestone_created_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_milestone_org_project', 'project_milestones', ['organization_id', 'project_id'])
    op.create_index('idx_milestone_org_status', 'project_milestones', ['organization_id', 'status'])
    op.create_index('idx_milestone_org_target_date', 'project_milestones', ['organization_id', 'target_date'])
    
    op.create_table(
        'project_resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', resource_type_enum, nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('allocated_quantity', sa.Float(), nullable=False, default=1.0),
        sa.Column('used_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('unit_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('allocation_start_date', sa.Date(), nullable=True),
        sa.Column('allocation_end_date', sa.Date(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_resource_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_resource_project_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_resource_user_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_resource_created_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_resource_org_project', 'project_resources', ['organization_id', 'project_id'])
    op.create_index('idx_resource_org_type', 'project_resources', ['organization_id', 'resource_type'])
    op.create_index('idx_resource_org_user', 'project_resources', ['organization_id', 'user_id'])
    
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
        sa.Column('version', sa.String(20), default='1.0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_document_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_document_project_id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='fk_document_uploaded_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_document_org_project', 'project_documents', ['organization_id', 'project_id'])
    op.create_index('idx_document_org_type', 'project_documents', ['organization_id', 'document_type'])
    op.create_index('idx_document_org_public', 'project_documents', ['organization_id', 'is_public'])
    
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
        sa.Column('is_billable', sa.Boolean(), default=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('billable_amount', sa.Float(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), default=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_timelog_organization_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_timelog_project_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_timelog_user_id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_timelog_task_id'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], name='fk_timelog_approved_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_timelog_org_project', 'project_time_logs', ['organization_id', 'project_id'])
    op.create_index('idx_timelog_org_user', 'project_time_logs', ['organization_id', 'user_id'])
    op.create_index('idx_timelog_org_date', 'project_time_logs', ['organization_id', 'start_time'])
    op.create_index('idx_timelog_org_billable', 'project_time_logs', ['organization_id', 'is_billable'])
    
    # Create Workflow Management tables
    op.create_table(
        'workflow_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('status', workflow_status_enum, nullable=False, default='draft'),
        sa.Column('trigger_type', workflow_trigger_type_enum, nullable=False, default='manual'),
        sa.Column('version', sa.String(20), default='1.0'),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('allow_parallel_execution', sa.Boolean(), default=False),
        sa.Column('auto_complete', sa.Boolean(), default=True),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_conditions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_workflow_template_organization_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_workflow_template_company_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_workflow_template_created_by'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', 'version', name='uq_workflow_template_org_name_version')
    )
    op.create_index('idx_workflow_template_org_category', 'workflow_templates', ['organization_id', 'category'])
    op.create_index('idx_workflow_template_org_status', 'workflow_templates', ['organization_id', 'status'])
    op.create_index('idx_workflow_template_org_entity', 'workflow_templates', ['organization_id', 'entity_type'])
    
    # Continue with remaining tables in next part due to length...
    
    # Create Workflow Steps table
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=False),
        sa.Column('step_type', step_type_enum, nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), default=True),
        sa.Column('allow_delegation', sa.Boolean(), default=True),
        sa.Column('allow_rejection', sa.Boolean(), default=True),
        sa.Column('assigned_role', sa.String(100), nullable=True),
        sa.Column('assigned_user_id', sa.Integer(), nullable=True),
        sa.Column('assignment_rules', sa.JSON(), nullable=True),
        sa.Column('condition_rules', sa.JSON(), nullable=True),
        sa.Column('parallel_group', sa.String(50), nullable=True),
        sa.Column('escalation_enabled', sa.Boolean(), default=False),
        sa.Column('escalation_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_action', escalation_action_enum, nullable=True),
        sa.Column('escalation_to_user_id', sa.Integer(), nullable=True),
        sa.Column('notification_template', sa.Text(), nullable=True),
        sa.Column('send_email', sa.Boolean(), default=True),
        sa.Column('send_in_app', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_workflow_step_organization_id'),
        sa.ForeignKeyConstraint(['template_id'], ['workflow_templates.id'], name='fk_workflow_step_template_id'),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], name='fk_workflow_step_assigned_user_id'),
        sa.ForeignKeyConstraint(['escalation_to_user_id'], ['users.id'], name='fk_workflow_step_escalation_to_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflow_step_org_template', 'workflow_steps', ['organization_id', 'template_id'])
    op.create_index('idx_workflow_step_org_order', 'workflow_steps', ['organization_id', 'template_id', 'step_order'])
    op.create_index('idx_workflow_step_org_type', 'workflow_steps', ['organization_id', 'step_type'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('workflow_steps')
    op.drop_table('workflow_templates')
    op.drop_table('project_time_logs')
    op.drop_table('project_documents')
    op.drop_table('project_resources')
    op.drop_table('project_milestones')
    op.drop_table('projects')
    
    # Drop enums
    postgresql.ENUM(name='escalationaction').drop(op.get_bind())
    postgresql.ENUM(name='instancestatus').drop(op.get_bind())
    postgresql.ENUM(name='steptype').drop(op.get_bind())
    postgresql.ENUM(name='approvalstatus').drop(op.get_bind())
    postgresql.ENUM(name='workflowtriggertype').drop(op.get_bind())
    postgresql.ENUM(name='workflowstatus').drop(op.get_bind())
    postgresql.ENUM(name='mappingtype').drop(op.get_bind())
    postgresql.ENUM(name='syncstatus').drop(op.get_bind())
    postgresql.ENUM(name='syncdirection').drop(op.get_bind())
    postgresql.ENUM(name='authtype').drop(op.get_bind())
    postgresql.ENUM(name='integrationstatus').drop(op.get_bind())
    postgresql.ENUM(name='integrationtype').drop(op.get_bind())
    postgresql.ENUM(name='webhookstatus').drop(op.get_bind())
    postgresql.ENUM(name='loglevel').drop(op.get_bind())
    postgresql.ENUM(name='accesslevel').drop(op.get_bind())
    postgresql.ENUM(name='ratelimittype').drop(op.get_bind())
    postgresql.ENUM(name='apikeystatus').drop(op.get_bind())
    postgresql.ENUM(name='resourcetype').drop(op.get_bind())
    postgresql.ENUM(name='milestonestatus').drop(op.get_bind())
    postgresql.ENUM(name='projecttype').drop(op.get_bind())
    postgresql.ENUM(name='projectpriority').drop(op.get_bind())
    postgresql.ENUM(name='projectstatus').drop(op.get_bind())