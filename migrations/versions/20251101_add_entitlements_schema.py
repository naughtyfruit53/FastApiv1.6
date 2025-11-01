"""add entitlements schema

Revision ID: 20251101_entitlements
Revises: f178178734f5
Create Date: 2025-11-01 03:10:09.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251101_entitlements'
down_revision = 'f178178734f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_key', name='uq_modules_module_key')
    )
    op.create_index('idx_modules_key', 'modules', ['module_key'], unique=False)
    op.create_index('idx_modules_active', 'modules', ['is_active'], unique=False)

    # Create submodules table
    op.create_table(
        'submodules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('submodule_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('menu_path', sa.String(length=500), nullable=True),
        sa.Column('permission_key', sa.String(length=200), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], name='fk_submodules_module_id', ondelete='CASCADE'),
        sa.UniqueConstraint('module_id', 'submodule_key', name='uq_submodules_module_submodule')
    )
    op.create_index('idx_submodules_module', 'submodules', ['module_id'], unique=False)
    op.create_index('idx_submodules_key', 'submodules', ['submodule_key'], unique=False)
    op.create_index('idx_submodules_active', 'submodules', ['is_active'], unique=False)

    # Create plans table
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly', sa.Numeric(10, 2), nullable=True),
        sa.Column('price_annual', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_key', name='uq_plans_plan_key')
    )
    op.create_index('idx_plans_key', 'plans', ['plan_key'], unique=False)
    op.create_index('idx_plans_active', 'plans', ['is_active'], unique=False)

    # Create plan_entitlements table
    op.create_table(
        'plan_entitlements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('submodule_id', sa.Integer(), nullable=True),
        sa.Column('is_included', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name='fk_plan_entitlements_plan_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], name='fk_plan_entitlements_module_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submodule_id'], ['submodules.id'], name='fk_plan_entitlements_submodule_id', ondelete='CASCADE'),
        sa.UniqueConstraint('plan_id', 'module_id', 'submodule_id', name='uq_plan_entitlements')
    )
    op.create_index('idx_plan_entitlements_plan', 'plan_entitlements', ['plan_id'], unique=False)
    op.create_index('idx_plan_entitlements_module', 'plan_entitlements', ['module_id'], unique=False)
    op.create_index('idx_plan_entitlements_submodule', 'plan_entitlements', ['submodule_id'], unique=False)

    # Create org_entitlements table
    op.create_table(
        'org_entitlements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='disabled'),
        sa.Column('trial_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], name='fk_org_entitlements_org_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], name='fk_org_entitlements_module_id', ondelete='CASCADE'),
        sa.UniqueConstraint('org_id', 'module_id', name='uq_org_entitlements_org_module'),
        sa.CheckConstraint("status IN ('enabled', 'disabled', 'trial')", name='ck_org_entitlements_status')
    )
    op.create_index('idx_org_entitlements_org', 'org_entitlements', ['org_id'], unique=False)
    op.create_index('idx_org_entitlements_module', 'org_entitlements', ['module_id'], unique=False)
    op.create_index('idx_org_entitlements_org_module', 'org_entitlements', ['org_id', 'module_id'], unique=False)
    op.create_index('idx_org_entitlements_status', 'org_entitlements', ['status'], unique=False)

    # Create org_subentitlements table
    op.create_table(
        'org_subentitlements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('submodule_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], name='fk_org_subentitlements_org_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], name='fk_org_subentitlements_module_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submodule_id'], ['submodules.id'], name='fk_org_subentitlements_submodule_id', ondelete='CASCADE'),
        sa.UniqueConstraint('org_id', 'module_id', 'submodule_id', name='uq_org_subentitlements')
    )
    op.create_index('idx_org_subentitlements_org', 'org_subentitlements', ['org_id'], unique=False)
    op.create_index('idx_org_subentitlements_module', 'org_subentitlements', ['module_id'], unique=False)
    op.create_index('idx_org_subentitlements_submodule', 'org_subentitlements', ['submodule_id'], unique=False)
    op.create_index('idx_org_subentitlements_org_module', 'org_subentitlements', ['org_id', 'module_id'], unique=False)
    op.create_index('idx_org_subentitlements_org_module_sub', 'org_subentitlements', ['org_id', 'module_id', 'submodule_id'], unique=False)

    # Create entitlement_events table
    op.create_table(
        'entitlement_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], name='fk_entitlement_events_org_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], name='fk_entitlement_events_actor_id', ondelete='SET NULL')
    )
    op.create_index('idx_entitlement_events_org', 'entitlement_events', ['org_id'], unique=False)
    op.create_index('idx_entitlement_events_type', 'entitlement_events', ['event_type'], unique=False)
    op.create_index('idx_entitlement_events_actor', 'entitlement_events', ['actor_user_id'], unique=False)
    op.create_index('idx_entitlement_events_created', 'entitlement_events', ['created_at'], unique=False)

    # Create v_effective_entitlements view
    op.execute("""
        CREATE OR REPLACE VIEW v_effective_entitlements AS
        SELECT 
            oe.org_id,
            m.id AS module_id,
            m.module_key,
            m.display_name AS module_display_name,
            oe.status AS module_status,
            oe.trial_expires_at,
            s.id AS submodule_id,
            s.submodule_key,
            s.display_name AS submodule_display_name,
            COALESCE(ose.enabled, true) AS submodule_enabled,
            CASE 
                WHEN oe.status = 'enabled' AND COALESCE(ose.enabled, true) = true THEN 'enabled'
                WHEN oe.status = 'trial' AND COALESCE(ose.enabled, true) = true AND (oe.trial_expires_at IS NULL OR oe.trial_expires_at > CURRENT_TIMESTAMP) THEN 'trial'
                ELSE 'disabled'
            END AS effective_status,
            oe.source AS module_source,
            ose.source AS submodule_source
        FROM org_entitlements oe
        INNER JOIN modules m ON oe.module_id = m.id
        LEFT JOIN submodules s ON s.module_id = m.id
        LEFT JOIN org_subentitlements ose ON ose.org_id = oe.org_id AND ose.module_id = m.id AND ose.submodule_id = s.id
        WHERE m.is_active = true
    """)


def downgrade() -> None:
    # Drop view
    op.execute('DROP VIEW IF EXISTS v_effective_entitlements')
    
    # Drop tables in reverse order
    op.drop_table('entitlement_events')
    op.drop_table('org_subentitlements')
    op.drop_table('org_entitlements')
    op.drop_table('plan_entitlements')
    op.drop_table('plans')
    op.drop_table('submodules')
    op.drop_table('modules')
