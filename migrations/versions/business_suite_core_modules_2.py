"""Add business suite core modules part 2

Revision ID: business_suite_core_modules_2
Revises: business_suite_core_modules
Create Date: 2024-12-06 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'business_suite_core_modules_2'
down_revision = 'business_suite_core_modules'
branch_labels = None
depends_on = None


def upgrade():
    # Continue creating Workflow Management tables
    
    op.create_table(
        'workflow_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('instance_name', sa.String(255), nullable=False),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('entity_data', sa.JSON(), nullable=True),
        sa.Column('status', postgresql.ENUM(name='instancestatus'), nullable=False, default='created'),
        sa.Column('current_step_id', sa.Integer(), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_steps', sa.Integer(), nullable=False, default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('triggered_by', sa.Integer(), nullable=False),
        sa.Column('trigger_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_workflow_instance_organization_id'),
        sa.ForeignKeyConstraint(['template_id'], ['workflow_templates.id'], name='fk_workflow_instance_template_id'),
        sa.ForeignKeyConstraint(['current_step_id'], ['workflow_steps.id'], name='fk_workflow_instance_current_step_id'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], name='fk_workflow_instance_triggered_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflow_instance_org_template', 'workflow_instances', ['organization_id', 'template_id'])
    op.create_index('idx_workflow_instance_org_entity', 'workflow_instances', ['organization_id', 'entity_type', 'entity_id'])
    op.create_index('idx_workflow_instance_org_status', 'workflow_instances', ['organization_id', 'status'])
    op.create_index('idx_workflow_instance_org_triggered', 'workflow_instances', ['organization_id', 'triggered_by'])
    
    op.create_table(
        'workflow_step_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('instance_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM(name='instancestatus'), nullable=False, default='created'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_workflow_step_instance_organization_id'),
        sa.ForeignKeyConstraint(['instance_id'], ['workflow_instances.id'], name='fk_workflow_step_instance_instance_id'),
        sa.ForeignKeyConstraint(['step_id'], ['workflow_steps.id'], name='fk_workflow_step_instance_step_id'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name='fk_workflow_step_instance_assigned_to'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflow_step_instance_org_instance', 'workflow_step_instances', ['organization_id', 'instance_id'])
    op.create_index('idx_workflow_step_instance_org_step', 'workflow_step_instances', ['organization_id', 'step_id'])
    op.create_index('idx_workflow_step_instance_org_status', 'workflow_step_instances', ['organization_id', 'status'])
    op.create_index('idx_workflow_step_instance_org_assigned', 'workflow_step_instances', ['organization_id', 'assigned_to'])
    
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('approval_code', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('entity_data', sa.JSON(), nullable=True),
        sa.Column('status', postgresql.ENUM(name='approvalstatus'), nullable=False, default='pending'),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=False),
        sa.Column('workflow_instance_id', sa.Integer(), nullable=True),
        sa.Column('step_instance_id', sa.Integer(), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('decision', postgresql.ENUM(name='approvalstatus'), nullable=True),
        sa.Column('decision_comments', sa.Text(), nullable=True),
        sa.Column('decision_data', sa.JSON(), nullable=True),
        sa.Column('delegated_to', sa.Integer(), nullable=True),
        sa.Column('delegation_reason', sa.Text(), nullable=True),
        sa.Column('escalated_to', sa.Integer(), nullable=True),
        sa.Column('escalation_reason', sa.Text(), nullable=True),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_approval_request_organization_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_approval_request_company_id'),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], name='fk_approval_request_requested_by'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name='fk_approval_request_assigned_to'),
        sa.ForeignKeyConstraint(['delegated_to'], ['users.id'], name='fk_approval_request_delegated_to'),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], name='fk_approval_request_escalated_to'),
        sa.ForeignKeyConstraint(['workflow_instance_id'], ['workflow_instances.id'], name='fk_approval_request_workflow_instance_id'),
        sa.ForeignKeyConstraint(['step_instance_id'], ['workflow_step_instances.id'], name='fk_approval_request_step_instance_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'approval_code', name='uq_approval_org_code')
    )
    op.create_index('idx_approval_org_entity', 'approval_requests', ['organization_id', 'entity_type', 'entity_id'])
    op.create_index('idx_approval_org_status', 'approval_requests', ['organization_id', 'status'])
    op.create_index('idx_approval_org_assigned', 'approval_requests', ['organization_id', 'assigned_to'])
    op.create_index('idx_approval_org_requested', 'approval_requests', ['organization_id', 'requested_by'])
    
    op.create_table(
        'approval_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('approval_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('previous_status', postgresql.ENUM(name='approvalstatus'), nullable=True),
        sa.Column('new_status', postgresql.ENUM(name='approvalstatus'), nullable=False),
        sa.Column('performed_by', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_approval_history_organization_id'),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], name='fk_approval_history_approval_id'),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], name='fk_approval_history_performed_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_approval_history_org_approval', 'approval_history', ['organization_id', 'approval_id'])
    op.create_index('idx_approval_history_org_performer', 'approval_history', ['organization_id', 'performed_by'])
    op.create_index('idx_approval_history_org_action', 'approval_history', ['organization_id', 'action'])
    
    op.create_table(
        'approval_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('approval_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_approval_attachment_organization_id'),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], name='fk_approval_attachment_approval_id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='fk_approval_attachment_uploaded_by'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_approval_attachment_org_approval', 'approval_attachments', ['organization_id', 'approval_id'])
    op.create_index('idx_approval_attachment_org_uploader', 'approval_attachments', ['organization_id', 'uploaded_by'])
    
    # Create API Gateway tables
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('key_name', sa.String(255), nullable=False),
        sa.Column('api_key', sa.String(500), nullable=False, unique=True),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('status', postgresql.ENUM(name='apikeystatus'), nullable=False, default='active'),
        sa.Column('access_level', postgresql.ENUM(name='accesslevel'), nullable=False, default='read_only'),
        sa.Column('allowed_endpoints', sa.JSON(), nullable=True),
        sa.Column('restricted_endpoints', sa.JSON(), nullable=True),
        sa.Column('allowed_methods', sa.JSON(), nullable=True),
        sa.Column('rate_limit_requests', sa.Integer(), nullable=True, default=1000),
        sa.Column('rate_limit_type', postgresql.ENUM(name='ratelimittype'), nullable=False, default='per_hour'),
        sa.Column('current_usage', sa.Integer(), default=0, nullable=False),
        sa.Column('allowed_ips', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_api_key_organization_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_api_key_company_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_api_key_created_by'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'key_name', name='uq_api_key_org_name')
    )
    op.create_index('idx_api_key_org_status', 'api_keys', ['organization_id', 'status'])
    op.create_index('idx_api_key_org_access_level', 'api_keys', ['organization_id', 'access_level'])
    op.create_index('idx_api_key_prefix', 'api_keys', ['key_prefix'])
    
    op.create_table(
        'api_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=True),
        sa.Column('endpoint', sa.String(500), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('request_ip', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_headers', sa.JSON(), nullable=True),
        sa.Column('request_body_size', sa.Integer(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('request_id', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_api_usage_log_organization_id'),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], name='fk_api_usage_log_api_key_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_usage_org_timestamp', 'api_usage_logs', ['organization_id', 'timestamp'])
    op.create_index('idx_api_usage_org_endpoint', 'api_usage_logs', ['organization_id', 'endpoint'])
    op.create_index('idx_api_usage_org_status', 'api_usage_logs', ['organization_id', 'status_code'])
    op.create_index('idx_api_usage_org_api_key', 'api_usage_logs', ['organization_id', 'api_key_id'])
    
    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('status', postgresql.ENUM(name='webhookstatus'), nullable=False, default='active'),
        sa.Column('secret_key', sa.String(255), nullable=True),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.Column('entity_types', sa.JSON(), nullable=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('auth_type', sa.String(50), nullable=True),
        sa.Column('auth_config', sa.JSON(), nullable=True),
        sa.Column('max_retries', sa.Integer(), default=3, nullable=False),
        sa.Column('retry_delay_seconds', sa.Integer(), default=60, nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), default=30, nullable=False),
        sa.Column('success_status_codes', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=False),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_webhook_organization_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_webhook_company_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_webhook_created_by'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_webhook_org_name')
    )
    op.create_index('idx_webhook_org_status', 'webhooks', ['organization_id', 'status'])


def downgrade():
    # Drop API Gateway tables
    op.drop_table('webhooks')
    op.drop_table('api_usage_logs')
    op.drop_table('api_keys')
    
    # Drop Workflow tables
    op.drop_table('approval_attachments')
    op.drop_table('approval_history')
    op.drop_table('approval_requests')
    op.drop_table('workflow_step_instances')
    op.drop_table('workflow_instances')