"""add_tally_integration_models

Revision ID: add_tally_integration_models
Revises: add_procurement_models
Create Date: 2024-01-01 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_tally_integration_models'
down_revision = 'add_procurement_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tally Configuration table
    op.create_table('tally_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('tally_server_host', sa.String(length=100), nullable=False, default='localhost'),
        sa.Column('tally_server_port', sa.Integer(), nullable=False, default=9000),
        sa.Column('company_name_in_tally', sa.String(length=200), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('sync_direction', sa.Enum('BIDIRECTIONAL', 'TO_TALLY', 'FROM_TALLY', name='syncdirection'), nullable=False, default='BIDIRECTIONAL'),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('sync_interval_minutes', sa.Integer(), nullable=False, default=30),
        sa.Column('sync_masters', sa.Boolean(), nullable=False, default=True),
        sa.Column('sync_vouchers', sa.Boolean(), nullable=False, default=True),
        sa.Column('sync_reports', sa.Boolean(), nullable=False, default=False),
        sa.Column('field_mappings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ledger_mappings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('voucher_type_mappings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('connection_status', sa.Enum('CONNECTED', 'DISCONNECTED', 'ERROR', 'SYNCING', name='tallyconnectionstatus'), nullable=False, default='DISCONNECTED'),
        sa.Column('last_connection_test', sa.DateTime(), nullable=True),
        sa.Column('connection_error_message', sa.Text(), nullable=True),
        sa.Column('last_sync_datetime', sa.DateTime(), nullable=True),
        sa.Column('last_successful_sync', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('configured_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['configured_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )
    op.create_index(op.f('ix_tally_configuration_id'), 'tally_configuration', ['id'])
    op.create_index(op.f('ix_tally_configuration_organization_id'), 'tally_configuration', ['organization_id'])

    # Tally Ledger Mapping table
    op.create_table('tally_ledger_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tally_configuration_id', sa.Integer(), nullable=False),
        sa.Column('chart_of_accounts_id', sa.Integer(), nullable=False),
        sa.Column('tally_ledger_name', sa.String(length=200), nullable=False),
        sa.Column('tally_ledger_guid', sa.String(length=100), nullable=True),
        sa.Column('tally_parent_ledger', sa.String(length=200), nullable=True),
        sa.Column('is_bidirectional', sa.Boolean(), nullable=False, default=True),
        sa.Column('erp_to_tally_only', sa.Boolean(), nullable=False, default=False),
        sa.Column('tally_to_erp_only', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_synced', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', name='syncstatus'), nullable=False, default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tally_configuration_id'], ['tally_configuration.id'], ),
        sa.ForeignKeyConstraint(['chart_of_accounts_id'], ['chart_of_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tally_configuration_id', 'chart_of_accounts_id', name='uq_tally_ledger_mapping')
    )
    op.create_index('idx_tally_ledger_name', 'tally_ledger_mappings', ['tally_ledger_name'])
    op.create_index(op.f('ix_tally_ledger_mappings_id'), 'tally_ledger_mappings', ['id'])
    op.create_index(op.f('ix_tally_ledger_mappings_tally_configuration_id'), 'tally_ledger_mappings', ['tally_configuration_id'])
    op.create_index(op.f('ix_tally_ledger_mappings_chart_of_accounts_id'), 'tally_ledger_mappings', ['chart_of_accounts_id'])
    op.create_index(op.f('ix_tally_ledger_mappings_tally_ledger_guid'), 'tally_ledger_mappings', ['tally_ledger_guid'])

    # Tally Voucher Mapping table
    op.create_table('tally_voucher_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tally_configuration_id', sa.Integer(), nullable=False),
        sa.Column('erp_voucher_type', sa.String(length=50), nullable=False),
        sa.Column('tally_voucher_type', sa.String(length=100), nullable=False),
        sa.Column('tally_voucher_type_guid', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('field_mappings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tally_configuration_id'], ['tally_configuration.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tally_configuration_id', 'erp_voucher_type', name='uq_tally_voucher_mapping')
    )
    op.create_index('idx_tally_voucher_type', 'tally_voucher_mappings', ['tally_voucher_type'])
    op.create_index(op.f('ix_tally_voucher_mappings_id'), 'tally_voucher_mappings', ['id'])
    op.create_index(op.f('ix_tally_voucher_mappings_tally_configuration_id'), 'tally_voucher_mappings', ['tally_configuration_id'])
    op.create_index(op.f('ix_tally_voucher_mappings_erp_voucher_type'), 'tally_voucher_mappings', ['erp_voucher_type'])

    # Tally Sync Log table
    op.create_table('tally_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tally_configuration_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('sync_direction', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('sync_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', name='syncstatus'), nullable=False),
        sa.Column('records_processed', sa.Integer(), nullable=False, default=0),
        sa.Column('records_successful', sa.Integer(), nullable=False, default=0),
        sa.Column('records_failed', sa.Integer(), nullable=False, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sync_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('triggered_by', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tally_configuration_id'], ['tally_configuration.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_log_type_status', 'tally_sync_logs', ['sync_type', 'sync_status'])
    op.create_index('idx_sync_log_started', 'tally_sync_logs', ['started_at'])
    op.create_index(op.f('ix_tally_sync_logs_id'), 'tally_sync_logs', ['id'])
    op.create_index(op.f('ix_tally_sync_logs_tally_configuration_id'), 'tally_sync_logs', ['tally_configuration_id'])
    op.create_index(op.f('ix_tally_sync_logs_sync_type'), 'tally_sync_logs', ['sync_type'])
    op.create_index(op.f('ix_tally_sync_logs_sync_direction'), 'tally_sync_logs', ['sync_direction'])
    op.create_index(op.f('ix_tally_sync_logs_started_at'), 'tally_sync_logs', ['started_at'])
    op.create_index(op.f('ix_tally_sync_logs_sync_status'), 'tally_sync_logs', ['sync_status'])
    op.create_index(op.f('ix_tally_sync_logs_triggered_by'), 'tally_sync_logs', ['triggered_by'])

    # Tally Sync Items table
    op.create_table('tally_sync_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_log_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('entity_reference', sa.String(length=100), nullable=True),
        sa.Column('tally_guid', sa.String(length=100), nullable=True),
        sa.Column('tally_reference', sa.String(length=100), nullable=True),
        sa.Column('sync_direction', sa.String(length=20), nullable=False),
        sa.Column('sync_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', name='syncstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('before_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('after_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['sync_log_id'], ['tally_sync_logs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_item_entity', 'tally_sync_items', ['entity_type', 'entity_id'])
    op.create_index('idx_sync_item_tally', 'tally_sync_items', ['tally_guid'])
    op.create_index(op.f('ix_tally_sync_items_id'), 'tally_sync_items', ['id'])
    op.create_index(op.f('ix_tally_sync_items_sync_log_id'), 'tally_sync_items', ['sync_log_id'])
    op.create_index(op.f('ix_tally_sync_items_entity_type'), 'tally_sync_items', ['entity_type'])
    op.create_index(op.f('ix_tally_sync_items_entity_id'), 'tally_sync_items', ['entity_id'])
    op.create_index(op.f('ix_tally_sync_items_entity_reference'), 'tally_sync_items', ['entity_reference'])
    op.create_index(op.f('ix_tally_sync_items_tally_guid'), 'tally_sync_items', ['tally_guid'])
    op.create_index(op.f('ix_tally_sync_items_tally_reference'), 'tally_sync_items', ['tally_reference'])
    op.create_index(op.f('ix_tally_sync_items_sync_direction'), 'tally_sync_items', ['sync_direction'])
    op.create_index(op.f('ix_tally_sync_items_sync_status'), 'tally_sync_items', ['sync_status'])
    op.create_index(op.f('ix_tally_sync_items_processed_at'), 'tally_sync_items', ['processed_at'])

    # Tally Data Cache table
    op.create_table('tally_data_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('data_key', sa.String(length=200), nullable=False),
        sa.Column('data_content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('data_hash', sa.String(length=64), nullable=True),
        sa.Column('cached_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('tally_last_modified', sa.DateTime(), nullable=True),
        sa.Column('tally_version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'data_type', 'data_key', name='uq_tally_cache')
    )
    op.create_index('idx_tally_cache_expires', 'tally_data_cache', ['expires_at'])
    op.create_index('idx_tally_cache_hash', 'tally_data_cache', ['data_hash'])
    op.create_index(op.f('ix_tally_data_cache_id'), 'tally_data_cache', ['id'])
    op.create_index(op.f('ix_tally_data_cache_organization_id'), 'tally_data_cache', ['organization_id'])
    op.create_index(op.f('ix_tally_data_cache_data_type'), 'tally_data_cache', ['data_type'])
    op.create_index(op.f('ix_tally_data_cache_data_key'), 'tally_data_cache', ['data_key'])
    op.create_index(op.f('ix_tally_data_cache_data_hash'), 'tally_data_cache', ['data_hash'])
    op.create_index(op.f('ix_tally_data_cache_cached_at'), 'tally_data_cache', ['cached_at'])
    op.create_index(op.f('ix_tally_data_cache_expires_at'), 'tally_data_cache', ['expires_at'])

    # Tally Error Log table
    op.create_table('tally_error_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('error_type', sa.String(length=50), nullable=False),
        sa.Column('error_code', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('operation', sa.String(length=100), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_reference', sa.String(length=100), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('request_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, default='error'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tally_error_type_severity', 'tally_error_logs', ['error_type', 'severity'])
    op.create_index('idx_tally_error_resolved', 'tally_error_logs', ['is_resolved'])
    op.create_index(op.f('ix_tally_error_logs_id'), 'tally_error_logs', ['id'])
    op.create_index(op.f('ix_tally_error_logs_organization_id'), 'tally_error_logs', ['organization_id'])
    op.create_index(op.f('ix_tally_error_logs_error_type'), 'tally_error_logs', ['error_type'])
    op.create_index(op.f('ix_tally_error_logs_error_code'), 'tally_error_logs', ['error_code'])
    op.create_index(op.f('ix_tally_error_logs_occurred_at'), 'tally_error_logs', ['occurred_at'])
    op.create_index(op.f('ix_tally_error_logs_severity'), 'tally_error_logs', ['severity'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tally_error_logs')
    op.drop_table('tally_data_cache')
    op.drop_table('tally_sync_items')
    op.drop_table('tally_sync_logs')
    op.drop_table('tally_voucher_mappings')
    op.drop_table('tally_ledger_mappings')
    op.drop_table('tally_configuration')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS syncdirection')
    op.execute('DROP TYPE IF EXISTS tallyconnectionstatus')
    op.execute('DROP TYPE IF EXISTS syncstatus')