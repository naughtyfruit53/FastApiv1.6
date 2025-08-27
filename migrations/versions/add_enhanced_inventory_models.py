"""add_enhanced_inventory_models

Revision ID: add_enhanced_inventory_models
Revises: add_tally_integration_models
Create Date: 2024-01-01 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_enhanced_inventory_models'
down_revision = 'add_tally_integration_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Warehouses table
    op.create_table('warehouses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_code', sa.String(length=50), nullable=False),
        sa.Column('warehouse_name', sa.String(length=200), nullable=False),
        sa.Column('warehouse_type', sa.Enum('MAIN', 'BRANCH', 'VIRTUAL', 'TRANSIT', 'QUARANTINE', name='warehousetype'), nullable=False, default='MAIN'),
        sa.Column('address_line1', sa.String(length=200), nullable=True),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('pincode', sa.String(length=10), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False, default='India'),
        sa.Column('contact_person', sa.String(length=100), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('allow_negative_stock', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_main_warehouse', sa.Boolean(), nullable=False, default=False),
        sa.Column('total_area_sqft', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('storage_capacity_units', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'warehouse_code', name='uq_org_warehouse_code')
    )
    op.create_index('idx_warehouse_type', 'warehouses', ['warehouse_type'])
    op.create_index(op.f('ix_warehouses_id'), 'warehouses', ['id'])
    op.create_index(op.f('ix_warehouses_organization_id'), 'warehouses', ['organization_id'])
    op.create_index(op.f('ix_warehouses_warehouse_code'), 'warehouses', ['warehouse_code'])

    # Stock Locations table
    op.create_table('stock_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('location_code', sa.String(length=50), nullable=False),
        sa.Column('location_name', sa.String(length=200), nullable=False),
        sa.Column('location_type', sa.String(length=50), nullable=True),
        sa.Column('parent_location_id', sa.Integer(), nullable=True),
        sa.Column('row_number', sa.String(length=10), nullable=True),
        sa.Column('column_number', sa.String(length=10), nullable=True),
        sa.Column('level_number', sa.String(length=10), nullable=True),
        sa.Column('max_capacity_units', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('max_weight_kg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_pickable', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_receivable', sa.Boolean(), nullable=False, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['parent_location_id'], ['stock_locations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'location_code', name='uq_warehouse_location_code')
    )
    op.create_index(op.f('ix_stock_locations_id'), 'stock_locations', ['id'])
    op.create_index(op.f('ix_stock_locations_warehouse_id'), 'stock_locations', ['warehouse_id'])
    op.create_index(op.f('ix_stock_locations_location_code'), 'stock_locations', ['location_code'])
    op.create_index(op.f('ix_stock_locations_parent_location_id'), 'stock_locations', ['parent_location_id'])

    # Product Tracking table
    op.create_table('product_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('tracking_type', sa.Enum('NONE', 'BATCH', 'SERIAL', 'BATCH_AND_SERIAL', name='trackingtype'), nullable=False, default='NONE'),
        sa.Column('valuation_method', sa.Enum('FIFO', 'LIFO', 'WEIGHTED_AVERAGE', 'STANDARD_COST', name='inventoryvaluationmethod'), nullable=False, default='WEIGHTED_AVERAGE'),
        sa.Column('batch_naming_series', sa.String(length=50), nullable=True),
        sa.Column('auto_create_batch', sa.Boolean(), nullable=False, default=False),
        sa.Column('batch_expiry_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('serial_naming_series', sa.String(length=50), nullable=True),
        sa.Column('auto_create_serial', sa.Boolean(), nullable=False, default=False),
        sa.Column('enable_reorder_alert', sa.Boolean(), nullable=False, default=True),
        sa.Column('reorder_level', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('reorder_quantity', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('max_stock_level', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('procurement_lead_time_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id')
    )
    op.create_index(op.f('ix_product_tracking_id'), 'product_tracking', ['id'])
    op.create_index(op.f('ix_product_tracking_product_id'), 'product_tracking', ['product_id'])

    # Warehouse Stock table
    op.create_table('warehouse_stock',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('available_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('committed_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('on_order_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('free_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('total_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('average_cost', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('total_value', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('last_movement_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'product_id', name='uq_warehouse_product_stock')
    )
    op.create_index('idx_warehouse_stock_org_warehouse', 'warehouse_stock', ['organization_id', 'warehouse_id'])
    op.create_index(op.f('ix_warehouse_stock_id'), 'warehouse_stock', ['id'])
    op.create_index(op.f('ix_warehouse_stock_organization_id'), 'warehouse_stock', ['organization_id'])
    op.create_index(op.f('ix_warehouse_stock_warehouse_id'), 'warehouse_stock', ['warehouse_id'])
    op.create_index(op.f('ix_warehouse_stock_product_id'), 'warehouse_stock', ['product_id'])

    # Product Batches table
    op.create_table('product_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('product_tracking_id', sa.Integer(), nullable=False),
        sa.Column('batch_number', sa.String(length=100), nullable=False),
        sa.Column('batch_name', sa.String(length=200), nullable=True),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('supplier_batch_number', sa.String(length=100), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('quality_grade', sa.String(length=50), nullable=True),
        sa.Column('quality_notes', sa.Text(), nullable=True),
        sa.Column('batch_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('available_quantity', sa.Numeric(precision=12, scale=3), nullable=False, default=0.000),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_expired', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['product_tracking_id'], ['product_tracking.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'batch_number', name='uq_org_batch_number')
    )
    op.create_index('idx_batch_expiry', 'product_batches', ['expiry_date'])
    op.create_index('idx_batch_active', 'product_batches', ['is_active'])
    op.create_index(op.f('ix_product_batches_id'), 'product_batches', ['id'])
    op.create_index(op.f('ix_product_batches_organization_id'), 'product_batches', ['organization_id'])
    op.create_index(op.f('ix_product_batches_product_tracking_id'), 'product_batches', ['product_tracking_id'])
    op.create_index(op.f('ix_product_batches_batch_number'), 'product_batches', ['batch_number'])
    op.create_index(op.f('ix_product_batches_expiry_date'), 'product_batches', ['expiry_date'])

    # Product Serials table
    op.create_table('product_serials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('product_tracking_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('warranty_expiry_date', sa.Date(), nullable=True),
        sa.Column('supplier_serial_number', sa.String(length=100), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('current_status', sa.String(length=20), nullable=False, default='available'),
        sa.Column('current_warehouse_id', sa.Integer(), nullable=True),
        sa.Column('current_location_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('sale_date', sa.Date(), nullable=True),
        sa.Column('sale_invoice_number', sa.String(length=100), nullable=True),
        sa.Column('quality_grade', sa.String(length=50), nullable=True),
        sa.Column('quality_notes', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['product_tracking_id'], ['product_tracking.id'], ),
        sa.ForeignKeyConstraint(['batch_id'], ['product_batches.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['vendors.id'], ),
        sa.ForeignKeyConstraint(['current_warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['current_location_id'], ['stock_locations.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'serial_number', name='uq_org_serial_number')
    )
    op.create_index('idx_serial_status', 'product_serials', ['current_status'])
    op.create_index('idx_serial_warranty', 'product_serials', ['warranty_expiry_date'])
    op.create_index(op.f('ix_product_serials_id'), 'product_serials', ['id'])
    op.create_index(op.f('ix_product_serials_organization_id'), 'product_serials', ['organization_id'])
    op.create_index(op.f('ix_product_serials_product_tracking_id'), 'product_serials', ['product_tracking_id'])
    op.create_index(op.f('ix_product_serials_batch_id'), 'product_serials', ['batch_id'])
    op.create_index(op.f('ix_product_serials_serial_number'), 'product_serials', ['serial_number'])
    op.create_index(op.f('ix_product_serials_current_status'), 'product_serials', ['current_status'])
    op.create_index(op.f('ix_product_serials_current_warehouse_id'), 'product_serials', ['current_warehouse_id'])
    op.create_index(op.f('ix_product_serials_current_location_id'), 'product_serials', ['current_location_id'])
    op.create_index(op.f('ix_product_serials_customer_id'), 'product_serials', ['customer_id'])

    # Batch Locations table
    op.create_table('batch_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('stock_location_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['product_batches.id'], ),
        sa.ForeignKeyConstraint(['stock_location_id'], ['stock_locations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_id', 'stock_location_id', name='uq_batch_location')
    )
    op.create_index(op.f('ix_batch_locations_id'), 'batch_locations', ['id'])
    op.create_index(op.f('ix_batch_locations_batch_id'), 'batch_locations', ['batch_id'])
    op.create_index(op.f('ix_batch_locations_stock_location_id'), 'batch_locations', ['stock_location_id'])

    # Stock Movements table
    op.create_table('stock_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.Enum('RECEIPT', 'ISSUE', 'TRANSFER', 'ADJUSTMENT', 'RETURN', 'DAMAGE', 'OBSOLETE', name='stockmovementtype'), nullable=False),
        sa.Column('movement_date', sa.DateTime(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('serial_numbers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('from_location_id', sa.Integer(), nullable=True),
        sa.Column('to_location_id', sa.Integer(), nullable=True),
        sa.Column('source_document_type', sa.String(length=50), nullable=True),
        sa.Column('source_document_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['batch_id'], ['product_batches.id'], ),
        sa.ForeignKeyConstraint(['from_location_id'], ['stock_locations.id'], ),
        sa.ForeignKeyConstraint(['to_location_id'], ['stock_locations.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stock_movement_org_date', 'stock_movements', ['organization_id', 'movement_date'])
    op.create_index('idx_stock_movement_type', 'stock_movements', ['movement_type'])
    op.create_index(op.f('ix_stock_movements_id'), 'stock_movements', ['id'])
    op.create_index(op.f('ix_stock_movements_organization_id'), 'stock_movements', ['organization_id'])
    op.create_index(op.f('ix_stock_movements_warehouse_id'), 'stock_movements', ['warehouse_id'])
    op.create_index(op.f('ix_stock_movements_product_id'), 'stock_movements', ['product_id'])
    op.create_index(op.f('ix_stock_movements_movement_type'), 'stock_movements', ['movement_type'])
    op.create_index(op.f('ix_stock_movements_movement_date'), 'stock_movements', ['movement_date'])
    op.create_index(op.f('ix_stock_movements_reference_number'), 'stock_movements', ['reference_number'])
    op.create_index(op.f('ix_stock_movements_batch_id'), 'stock_movements', ['batch_id'])
    op.create_index(op.f('ix_stock_movements_from_location_id'), 'stock_movements', ['from_location_id'])
    op.create_index(op.f('ix_stock_movements_to_location_id'), 'stock_movements', ['to_location_id'])
    op.create_index(op.f('ix_stock_movements_source_document_type'), 'stock_movements', ['source_document_type'])
    op.create_index(op.f('ix_stock_movements_source_document_id'), 'stock_movements', ['source_document_id'])

    # Stock Adjustments table
    op.create_table('stock_adjustments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('adjustment_number', sa.String(length=50), nullable=False),
        sa.Column('adjustment_date', sa.Date(), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='draft'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('adjustment_number')
    )
    op.create_index('idx_stock_adj_org_status', 'stock_adjustments', ['organization_id', 'status'])
    op.create_index(op.f('ix_stock_adjustments_id'), 'stock_adjustments', ['id'])
    op.create_index(op.f('ix_stock_adjustments_organization_id'), 'stock_adjustments', ['organization_id'])
    op.create_index(op.f('ix_stock_adjustments_adjustment_number'), 'stock_adjustments', ['adjustment_number'])
    op.create_index(op.f('ix_stock_adjustments_adjustment_date'), 'stock_adjustments', ['adjustment_date'])
    op.create_index(op.f('ix_stock_adjustments_adjustment_type'), 'stock_adjustments', ['adjustment_type'])
    op.create_index(op.f('ix_stock_adjustments_status'), 'stock_adjustments', ['status'])

    # Stock Adjustment Items table
    op.create_table('stock_adjustment_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('adjustment_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('book_quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('physical_quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('adjustment_quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('adjustment_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('serial_numbers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['adjustment_id'], ['stock_adjustments.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['batch_id'], ['product_batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_adjustment_items_id'), 'stock_adjustment_items', ['id'])
    op.create_index(op.f('ix_stock_adjustment_items_adjustment_id'), 'stock_adjustment_items', ['adjustment_id'])
    op.create_index(op.f('ix_stock_adjustment_items_warehouse_id'), 'stock_adjustment_items', ['warehouse_id'])
    op.create_index(op.f('ix_stock_adjustment_items_product_id'), 'stock_adjustment_items', ['product_id'])
    op.create_index(op.f('ix_stock_adjustment_items_batch_id'), 'stock_adjustment_items', ['batch_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('stock_adjustment_items')
    op.drop_table('stock_adjustments')
    op.drop_table('stock_movements')
    op.drop_table('batch_locations')
    op.drop_table('product_serials')
    op.drop_table('product_batches')
    op.drop_table('warehouse_stock')
    op.drop_table('product_tracking')
    op.drop_table('stock_locations')
    op.drop_table('warehouses')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS warehousetype')
    op.execute('DROP TYPE IF EXISTS trackingtype')
    op.execute('DROP TYPE IF EXISTS inventoryvaluationmethod')
    op.execute('DROP TYPE IF EXISTS stockmovementtype')