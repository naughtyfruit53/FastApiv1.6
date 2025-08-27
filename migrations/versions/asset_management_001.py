"""Add asset management models

Revision ID: asset_management_001
Revises: add_erp_procurement_tally_enhanced_inventory_models
Create Date: 2024-08-27 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'asset_management_001'
down_revision = 'add_erp_procurement_tally_enhanced_inventory_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create AssetStatus and AssetCondition enum tables for SQLite compatibility
    op.create_table('assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('asset_code', sa.String(), nullable=False),
        sa.Column('asset_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('subcategory', sa.String(), nullable=True),
        sa.Column('manufacturer', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('serial_number', sa.String(), nullable=True),
        sa.Column('year_of_manufacture', sa.Integer(), nullable=True),
        sa.Column('purchase_cost', sa.Float(), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('warranty_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('warranty_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('assigned_to_employee', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('condition', sa.String(), nullable=False, default='good'),
        sa.Column('last_inspection_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_inspection_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('operating_capacity', sa.String(), nullable=True),
        sa.Column('power_rating', sa.String(), nullable=True),
        sa.Column('depreciation_method', sa.String(), nullable=True, default='straight_line'),
        sa.Column('useful_life_years', sa.Integer(), nullable=True),
        sa.Column('salvage_value', sa.Float(), nullable=True),
        sa.Column('depreciation_rate', sa.Float(), nullable=True),
        sa.Column('insurance_provider', sa.String(), nullable=True),
        sa.Column('insurance_policy_number', sa.String(), nullable=True),
        sa.Column('insurance_expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photo_path', sa.String(), nullable=True),
        sa.Column('document_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'asset_code', name='uq_asset_org_code')
    )
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)
    op.create_index('idx_asset_org_category', 'assets', ['organization_id', 'category'], unique=False)
    op.create_index('idx_asset_org_status', 'assets', ['organization_id', 'status'], unique=False)
    op.create_index('idx_asset_org_location', 'assets', ['organization_id', 'location'], unique=False)
    op.create_index('idx_asset_org_created', 'assets', ['organization_id', 'created_at'], unique=False)

    # Maintenance Schedules
    op.create_table('maintenance_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('schedule_name', sa.String(), nullable=False),
        sa.Column('maintenance_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('frequency_type', sa.String(), nullable=False),
        sa.Column('frequency_value', sa.Integer(), nullable=True),
        sa.Column('estimated_duration_hours', sa.Float(), nullable=True),
        sa.Column('last_maintenance_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meter_type', sa.String(), nullable=True),
        sa.Column('meter_frequency', sa.Float(), nullable=True),
        sa.Column('last_meter_reading', sa.Float(), nullable=True),
        sa.Column('next_meter_due', sa.Float(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('required_parts', sa.Text(), nullable=True),
        sa.Column('assigned_technician', sa.String(), nullable=True),
        sa.Column('assigned_department', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('priority', sa.String(), nullable=True, default='medium'),
        sa.Column('advance_notice_days', sa.Integer(), nullable=True, default=7),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_schedules_id'), 'maintenance_schedules', ['id'], unique=False)
    op.create_index('idx_maint_sched_org_asset', 'maintenance_schedules', ['organization_id', 'asset_id'], unique=False)
    op.create_index('idx_maint_sched_org_due', 'maintenance_schedules', ['organization_id', 'next_due_date'], unique=False)
    op.create_index('idx_maint_sched_org_type', 'maintenance_schedules', ['organization_id', 'maintenance_type'], unique=False)
    op.create_index('idx_maint_sched_org_active', 'maintenance_schedules', ['organization_id', 'is_active'], unique=False)

    # Maintenance Records
    op.create_table('maintenance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=True),
        sa.Column('work_order_number', sa.String(), nullable=False),
        sa.Column('maintenance_type', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True, default='medium'),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('work_performed', sa.Text(), nullable=True),
        sa.Column('findings', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('assigned_technician', sa.String(), nullable=True),
        sa.Column('performed_by', sa.String(), nullable=True),
        sa.Column('supervised_by', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='scheduled'),
        sa.Column('labor_cost', sa.Float(), nullable=True),
        sa.Column('parts_cost', sa.Float(), nullable=True),
        sa.Column('external_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('meter_reading_before', sa.Float(), nullable=True),
        sa.Column('meter_reading_after', sa.Float(), nullable=True),
        sa.Column('safety_incidents', sa.Text(), nullable=True),
        sa.Column('quality_check_passed', sa.Boolean(), nullable=True, default=True),
        sa.Column('quality_remarks', sa.Text(), nullable=True),
        sa.Column('condition_before', sa.String(), nullable=True),
        sa.Column('condition_after', sa.String(), nullable=True),
        sa.Column('photos_path', sa.String(), nullable=True),
        sa.Column('documents_path', sa.String(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['schedule_id'], ['maintenance_schedules.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'work_order_number', name='uq_maint_rec_org_wo')
    )
    op.create_index(op.f('ix_maintenance_records_id'), 'maintenance_records', ['id'], unique=False)
    op.create_index('idx_maint_rec_org_asset', 'maintenance_records', ['organization_id', 'asset_id'], unique=False)
    op.create_index('idx_maint_rec_org_status', 'maintenance_records', ['organization_id', 'status'], unique=False)
    op.create_index('idx_maint_rec_org_date', 'maintenance_records', ['organization_id', 'scheduled_date'], unique=False)
    op.create_index('idx_maint_rec_org_type', 'maintenance_records', ['organization_id', 'maintenance_type'], unique=False)

    # Maintenance Parts Used
    op.create_table('maintenance_parts_used',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_record_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity_used', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('batch_number', sa.String(), nullable=True),
        sa.Column('serial_number', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['maintenance_record_id'], ['maintenance_records.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_parts_used_id'), 'maintenance_parts_used', ['id'], unique=False)
    op.create_index('idx_maint_parts_org_record', 'maintenance_parts_used', ['organization_id', 'maintenance_record_id'], unique=False)
    op.create_index('idx_maint_parts_org_product', 'maintenance_parts_used', ['organization_id', 'product_id'], unique=False)

    # Depreciation Records
    op.create_table('depreciation_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('depreciation_year', sa.Integer(), nullable=False),
        sa.Column('depreciation_month', sa.Integer(), nullable=True),
        sa.Column('period_start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('opening_book_value', sa.Float(), nullable=False),
        sa.Column('depreciation_amount', sa.Float(), nullable=False),
        sa.Column('accumulated_depreciation', sa.Float(), nullable=False),
        sa.Column('closing_book_value', sa.Float(), nullable=False),
        sa.Column('depreciation_method', sa.String(), nullable=False),
        sa.Column('depreciation_rate', sa.Float(), nullable=True),
        sa.Column('usage_units', sa.Float(), nullable=True),
        sa.Column('is_finalized', sa.Boolean(), nullable=True, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'depreciation_year', 'depreciation_month', name='uq_depr_asset_year_month')
    )
    op.create_index(op.f('ix_depreciation_records_id'), 'depreciation_records', ['id'], unique=False)
    op.create_index('idx_depr_org_asset', 'depreciation_records', ['organization_id', 'asset_id'], unique=False)
    op.create_index('idx_depr_org_period', 'depreciation_records', ['organization_id', 'period_start_date'], unique=False)
    op.create_index('idx_depr_org_year', 'depreciation_records', ['organization_id', 'depreciation_year'], unique=False)


def downgrade():
    op.drop_table('depreciation_records')
    op.drop_table('maintenance_parts_used')
    op.drop_table('maintenance_records')
    op.drop_table('maintenance_schedules')
    op.drop_table('assets')