"""Add transport and freight models

Revision ID: transport_freight_001
Revises: asset_management_001
Create Date: 2024-08-27 17:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'transport_freight_001'
down_revision = 'asset_management_001'
branch_labels = None
depends_on = None


def upgrade():
    # Carriers
    op.create_table('carriers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('carrier_code', sa.String(), nullable=False),
        sa.Column('carrier_name', sa.String(), nullable=False),
        sa.Column('carrier_type', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('address_line1', sa.String(), nullable=True),
        sa.Column('address_line2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('license_number', sa.String(), nullable=True),
        sa.Column('license_expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('insurance_number', sa.String(), nullable=True),
        sa.Column('insurance_expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('service_areas', sa.JSON(), nullable=True),
        sa.Column('vehicle_types', sa.JSON(), nullable=True),
        sa.Column('special_handling', sa.JSON(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True, default=0.0),
        sa.Column('on_time_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('damage_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('transit_time_reliability', sa.String(), nullable=True),
        sa.Column('tracking_capability', sa.Boolean(), nullable=True, default=False),
        sa.Column('real_time_updates', sa.Boolean(), nullable=True, default=False),
        sa.Column('payment_terms', sa.String(), nullable=True),
        sa.Column('credit_limit', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_preferred', sa.Boolean(), nullable=True, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'carrier_code', name='uq_carrier_org_code')
    )
    op.create_index(op.f('ix_carriers_id'), 'carriers', ['id'], unique=False)
    op.create_index('idx_carrier_org_type', 'carriers', ['organization_id', 'carrier_type'], unique=False)
    op.create_index('idx_carrier_org_active', 'carriers', ['organization_id', 'is_active'], unique=False)
    op.create_index('idx_carrier_org_name', 'carriers', ['organization_id', 'carrier_name'], unique=False)

    # Routes
    op.create_table('routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('route_code', sa.String(), nullable=False),
        sa.Column('route_name', sa.String(), nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=False),
        sa.Column('origin_city', sa.String(), nullable=False),
        sa.Column('origin_state', sa.String(), nullable=True),
        sa.Column('origin_country', sa.String(), nullable=True),
        sa.Column('destination_city', sa.String(), nullable=False),
        sa.Column('destination_state', sa.String(), nullable=True),
        sa.Column('destination_country', sa.String(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('estimated_transit_time_hours', sa.Float(), nullable=True),
        sa.Column('max_transit_time_hours', sa.Float(), nullable=True),
        sa.Column('vehicle_type', sa.String(), nullable=True),
        sa.Column('frequency', sa.String(), nullable=True),
        sa.Column('operating_days', sa.JSON(), nullable=True),
        sa.Column('max_weight_kg', sa.Float(), nullable=True),
        sa.Column('max_volume_cbm', sa.Float(), nullable=True),
        sa.Column('temperature_controlled', sa.Boolean(), nullable=True, default=False),
        sa.Column('hazmat_allowed', sa.Boolean(), nullable=True, default=False),
        sa.Column('average_transit_time_hours', sa.Float(), nullable=True),
        sa.Column('on_time_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('fuel_surcharge_applicable', sa.Boolean(), nullable=True, default=True),
        sa.Column('toll_charges_applicable', sa.Boolean(), nullable=True, default=True),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('seasonal_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('seasonal_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'route_code', name='uq_route_org_code')
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)
    op.create_index('idx_route_org_carrier', 'routes', ['organization_id', 'carrier_id'], unique=False)
    op.create_index('idx_route_org_origin', 'routes', ['organization_id', 'origin_city'], unique=False)
    op.create_index('idx_route_org_dest', 'routes', ['organization_id', 'destination_city'], unique=False)
    op.create_index('idx_route_org_status', 'routes', ['organization_id', 'status'], unique=False)

    # Freight Rates
    op.create_table('freight_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('rate_code', sa.String(), nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('freight_mode', sa.String(), nullable=False),
        sa.Column('service_type', sa.String(), nullable=True),
        sa.Column('rate_basis', sa.String(), nullable=False),
        sa.Column('minimum_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('rate_per_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('minimum_weight_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('maximum_weight_kg', sa.Float(), nullable=True),
        sa.Column('rate_per_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('minimum_volume_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('maximum_volume_cbm', sa.Float(), nullable=True),
        sa.Column('rate_per_km', sa.Float(), nullable=True, default=0.0),
        sa.Column('fixed_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('fuel_surcharge_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('handling_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('documentation_charge', sa.Float(), nullable=True, default=0.0),
        sa.Column('insurance_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('cod_charge_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('dangerous_goods_surcharge', sa.Float(), nullable=True, default=0.0),
        sa.Column('oversized_surcharge', sa.Float(), nullable=True, default=0.0),
        sa.Column('standard_transit_days', sa.Integer(), nullable=True),
        sa.Column('express_transit_days', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True, default='USD'),
        sa.Column('tax_applicable', sa.Boolean(), nullable=True, default=True),
        sa.Column('tax_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_negotiated', sa.Boolean(), nullable=True, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('terms_conditions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'rate_code', name='uq_freight_rate_org_code')
    )
    op.create_index(op.f('ix_freight_rates_id'), 'freight_rates', ['id'], unique=False)
    op.create_index('idx_freight_rate_org_carrier', 'freight_rates', ['organization_id', 'carrier_id'], unique=False)
    op.create_index('idx_freight_rate_org_route', 'freight_rates', ['organization_id', 'route_id'], unique=False)
    op.create_index('idx_freight_rate_org_effective', 'freight_rates', ['organization_id', 'effective_date'], unique=False)
    op.create_index('idx_freight_rate_org_active', 'freight_rates', ['organization_id', 'is_active'], unique=False)

    # Shipments
    op.create_table('shipments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('shipment_number', sa.String(), nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('sales_order_id', sa.Integer(), nullable=True),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('manufacturing_order_id', sa.Integer(), nullable=True),
        sa.Column('tracking_number', sa.String(), nullable=True),
        sa.Column('awb_number', sa.String(), nullable=True),
        sa.Column('bol_number', sa.String(), nullable=True),
        sa.Column('freight_mode', sa.String(), nullable=False),
        sa.Column('service_type', sa.String(), nullable=True),
        sa.Column('origin_name', sa.String(), nullable=False),
        sa.Column('origin_address', sa.Text(), nullable=True),
        sa.Column('origin_city', sa.String(), nullable=False),
        sa.Column('origin_state', sa.String(), nullable=True),
        sa.Column('origin_postal_code', sa.String(), nullable=True),
        sa.Column('origin_country', sa.String(), nullable=True),
        sa.Column('destination_name', sa.String(), nullable=False),
        sa.Column('destination_address', sa.Text(), nullable=True),
        sa.Column('destination_city', sa.String(), nullable=False),
        sa.Column('destination_state', sa.String(), nullable=True),
        sa.Column('destination_postal_code', sa.String(), nullable=True),
        sa.Column('destination_country', sa.String(), nullable=True),
        sa.Column('total_weight_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_volume_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_pieces', sa.Integer(), nullable=True, default=0),
        sa.Column('declared_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_fragile', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_hazardous', sa.Boolean(), nullable=True, default=False),
        sa.Column('temperature_controlled', sa.Boolean(), nullable=True, default=False),
        sa.Column('signature_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('pickup_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pickup_time_from', sa.String(), nullable=True),
        sa.Column('pickup_time_to', sa.String(), nullable=True),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='planned'),
        sa.Column('last_location_update', sa.String(), nullable=True),
        sa.Column('last_status_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('freight_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('fuel_surcharge', sa.Float(), nullable=True, default=0.0),
        sa.Column('handling_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('insurance_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('other_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('payment_terms', sa.String(), nullable=True),
        sa.Column('cod_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('shipping_documents', sa.JSON(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['manufacturing_order_id'], ['manufacturing_orders.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'shipment_number', name='uq_shipment_org_number')
    )
    op.create_index(op.f('ix_shipments_id'), 'shipments', ['id'], unique=False)
    op.create_index('idx_shipment_org_carrier', 'shipments', ['organization_id', 'carrier_id'], unique=False)
    op.create_index('idx_shipment_org_status', 'shipments', ['organization_id', 'status'], unique=False)
    op.create_index('idx_shipment_org_pickup_date', 'shipments', ['organization_id', 'pickup_date'], unique=False)
    op.create_index('idx_shipment_org_tracking', 'shipments', ['organization_id', 'tracking_number'], unique=False)

    # Shipment Items
    op.create_table('shipment_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('weight_per_unit_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('volume_per_unit_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('packaging_type', sa.String(), nullable=True),
        sa.Column('number_of_packages', sa.Integer(), nullable=True, default=1),
        sa.Column('package_dimensions', sa.String(), nullable=True),
        sa.Column('batch_number', sa.String(), nullable=True),
        sa.Column('serial_numbers', sa.JSON(), nullable=True),
        sa.Column('unit_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('handling_instructions', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shipment_items_id'), 'shipment_items', ['id'], unique=False)
    op.create_index('idx_shipment_items_org_shipment', 'shipment_items', ['organization_id', 'shipment_id'], unique=False)
    op.create_index('idx_shipment_items_org_product', 'shipment_items', ['organization_id', 'product_id'], unique=False)

    # Shipment Tracking
    op.create_table('shipment_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('facility_name', sa.String(), nullable=True),
        sa.Column('vehicle_number', sa.String(), nullable=True),
        sa.Column('driver_name', sa.String(), nullable=True),
        sa.Column('is_exception', sa.Boolean(), nullable=True, default=False),
        sa.Column('exception_reason', sa.String(), nullable=True),
        sa.Column('resolution_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shipment_tracking_id'), 'shipment_tracking', ['id'], unique=False)
    op.create_index('idx_shipment_tracking_org_shipment', 'shipment_tracking', ['organization_id', 'shipment_id'], unique=False)
    op.create_index('idx_shipment_tracking_org_timestamp', 'shipment_tracking', ['organization_id', 'event_timestamp'], unique=False)
    op.create_index('idx_shipment_tracking_org_status', 'shipment_tracking', ['organization_id', 'status'], unique=False)

    # Freight Cost Analysis
    op.create_table('freight_cost_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('analysis_name', sa.String(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=True),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('total_freight_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('base_freight_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('fuel_surcharges', sa.Float(), nullable=True, default=0.0),
        sa.Column('handling_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('insurance_costs', sa.Float(), nullable=True, default=0.0),
        sa.Column('other_charges', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_shipments', sa.Integer(), nullable=True, default=0),
        sa.Column('total_weight_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_volume_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('average_cost_per_kg', sa.Float(), nullable=True, default=0.0),
        sa.Column('average_cost_per_cbm', sa.Float(), nullable=True, default=0.0),
        sa.Column('average_cost_per_shipment', sa.Float(), nullable=True, default=0.0),
        sa.Column('on_time_delivery_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('damage_incidents', sa.Integer(), nullable=True, default=0),
        sa.Column('previous_period_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('cost_variance', sa.Float(), nullable=True, default=0.0),
        sa.Column('cost_variance_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('cost_optimization_opportunities', sa.Text(), nullable=True),
        sa.Column('recommended_actions', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['carrier_id'], ['carriers.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_freight_cost_analysis_id'), 'freight_cost_analysis', ['id'], unique=False)
    op.create_index('idx_freight_analysis_org_period', 'freight_cost_analysis', ['organization_id', 'period_start'], unique=False)
    op.create_index('idx_freight_analysis_org_carrier', 'freight_cost_analysis', ['organization_id', 'carrier_id'], unique=False)
    op.create_index('idx_freight_analysis_org_route', 'freight_cost_analysis', ['organization_id', 'route_id'], unique=False)


def downgrade():
    op.drop_table('freight_cost_analysis')
    op.drop_table('shipment_tracking')
    op.drop_table('shipment_items')
    op.drop_table('shipments')
    op.drop_table('freight_rates')
    op.drop_table('routes')
    op.drop_table('carriers')