"""Add organization role hierarchy and voucher approval workflow

Revision ID: add_role_approval_workflow
Revises: 649c2623e6c7
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_role_approval_workflow'
down_revision = '649c2623e6c7'
branch_labels = None
depends_on = None


def upgrade():
    """Add new tables for organization role hierarchy and voucher approval workflow"""
    
    # Organization Roles table
    op.create_table('organization_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('hierarchy_level', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_org_role_created_by_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_org_role_organization_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_org_role_org_name')
    )
    
    # Create indexes for organization_roles
    op.create_index('idx_org_role_org_active', 'organization_roles', ['organization_id', 'is_active'])
    op.create_index('idx_org_role_hierarchy', 'organization_roles', ['hierarchy_level'])
    op.create_index(op.f('ix_organization_roles_organization_id'), 'organization_roles', ['organization_id'])
    
    # Role Module Assignments table
    op.create_table('role_module_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(), nullable=False),
        sa.Column('access_level', sa.String(), nullable=False, server_default='full'),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], name='fk_role_module_assigned_by_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_role_module_organization_id'),
        sa.ForeignKeyConstraint(['role_id'], ['organization_roles.id'], name='fk_role_module_role_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'module_name', name='uq_role_module')
    )
    
    # Create indexes for role_module_assignments
    op.create_index('idx_role_module_org', 'role_module_assignments', ['organization_id'])
    op.create_index('idx_role_module_active', 'role_module_assignments', ['is_active'])
    op.create_index(op.f('ix_role_module_assignments_organization_id'), 'role_module_assignments', ['organization_id'])
    
    # User Organization Roles table
    op.create_table('user_organization_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('manager_assignments', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], name='fk_user_org_role_assigned_by_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_user_org_role_organization_id'),
        sa.ForeignKeyConstraint(['role_id'], ['organization_roles.id'], name='fk_user_org_role_role_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_org_role_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_org_role')
    )
    
    # Create indexes for user_organization_roles
    op.create_index('idx_user_org_role_user', 'user_organization_roles', ['user_id'])
    op.create_index('idx_user_org_role_role', 'user_organization_roles', ['role_id'])
    op.create_index('idx_user_org_role_active', 'user_organization_roles', ['is_active'])
    op.create_index(op.f('ix_user_organization_roles_organization_id'), 'user_organization_roles', ['organization_id'])
    
    # Organization Approval Settings table
    op.create_table('organization_approval_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('approval_model', sa.String(), nullable=False, server_default='no_approval'),
        sa.Column('level_2_approvers', sa.JSON(), nullable=True),
        sa.Column('auto_approve_threshold', sa.Float(), nullable=True),
        sa.Column('escalation_timeout_hours', sa.Integer(), nullable=True, server_default='72'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_approval_settings_organization_id'),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], name='fk_approval_settings_updated_by_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', name=op.f('organization_approval_settings_organization_id_key'))
    )
    
    # Create indexes for organization_approval_settings
    op.create_index('idx_approval_settings_model', 'organization_approval_settings', ['approval_model'])
    op.create_index(op.f('ix_organization_approval_settings_organization_id'), 'organization_approval_settings', ['organization_id'])
    
    # Voucher Approvals table
    op.create_table('voucher_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('approval_settings_id', sa.Integer(), nullable=False),
        sa.Column('voucher_type', sa.String(), nullable=False),
        sa.Column('voucher_id', sa.Integer(), nullable=False),
        sa.Column('voucher_number', sa.String(), nullable=True),
        sa.Column('voucher_amount', sa.Float(), nullable=True),
        sa.Column('submitted_by_id', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('current_approver_id', sa.Integer(), nullable=True),
        sa.Column('level_1_approver_id', sa.Integer(), nullable=True),
        sa.Column('level_1_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('level_1_comments', sa.Text(), nullable=True),
        sa.Column('level_2_approver_id', sa.Integer(), nullable=True),
        sa.Column('level_2_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('level_2_comments', sa.Text(), nullable=True),
        sa.Column('final_decision', sa.String(), nullable=True),
        sa.Column('final_decision_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('final_decision_by_id', sa.Integer(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approval_settings_id'], ['organization_approval_settings.id'], name='fk_voucher_approval_settings_id'),
        sa.ForeignKeyConstraint(['current_approver_id'], ['users.id'], name='fk_voucher_approval_current_approver_id'),
        sa.ForeignKeyConstraint(['final_decision_by_id'], ['users.id'], name='fk_voucher_approval_final_decision_by_id'),
        sa.ForeignKeyConstraint(['level_1_approver_id'], ['users.id'], name='fk_voucher_approval_level_1_approver_id'),
        sa.ForeignKeyConstraint(['level_2_approver_id'], ['users.id'], name='fk_voucher_approval_level_2_approver_id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_voucher_approval_organization_id'),
        sa.ForeignKeyConstraint(['submitted_by_id'], ['users.id'], name='fk_voucher_approval_submitted_by_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('voucher_type', 'voucher_id', name='uq_voucher_approval')
    )
    
    # Create indexes for voucher_approvals
    op.create_index('idx_voucher_approval_org', 'voucher_approvals', ['organization_id'])
    op.create_index('idx_voucher_approval_status', 'voucher_approvals', ['status'])
    op.create_index('idx_voucher_approval_submitted', 'voucher_approvals', ['submitted_by_id'])
    op.create_index('idx_voucher_approval_current', 'voucher_approvals', ['current_approver_id'])
    op.create_index(op.f('ix_voucher_approvals_organization_id'), 'voucher_approvals', ['organization_id'])


def downgrade():
    """Remove all new tables for organization role hierarchy and voucher approval workflow"""
    
    # Drop tables in reverse order of creation to handle foreign keys
    op.drop_table('voucher_approvals')
    op.drop_table('organization_approval_settings')
    op.drop_table('user_organization_roles')
    op.drop_table('role_module_assignments')
    op.drop_table('organization_roles')