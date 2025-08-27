"""add_procurement_models

Revision ID: add_procurement_models
Revises: add_erp_core_models
Create Date: 2024-01-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_procurement_models'
down_revision = 'add_erp_core_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Request for Quotations table
    op.create_table('request_for_quotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('rfq_number', sa.String(length=50), nullable=False),
        sa.Column('rfq_title', sa.String(length=200), nullable=False),
        sa.Column('rfq_description', sa.Text(), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('submission_deadline', sa.Date(), nullable=False),
        sa.Column('validity_period', sa.Integer(), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('delivery_requirements', sa.Text(), nullable=True),
        sa.Column('payment_terms', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SENT', 'RESPONDED', 'EVALUATED', 'AWARDED', 'CANCELLED', name='rfqstatus'), nullable=False, default='DRAFT'),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('requires_samples', sa.Boolean(), nullable=False, default=False),
        sa.Column('allow_partial_quotes', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_number')
    )
    op.create_index('idx_rfq_org_status', 'request_for_quotations', ['organization_id', 'status'])
    op.create_index('idx_rfq_deadline', 'request_for_quotations', ['submission_deadline'])
    op.create_index(op.f('ix_request_for_quotations_id'), 'request_for_quotations', ['id'])
    op.create_index(op.f('ix_request_for_quotations_organization_id'), 'request_for_quotations', ['organization_id'])
    op.create_index(op.f('ix_request_for_quotations_rfq_number'), 'request_for_quotations', ['rfq_number'])
    op.create_index(op.f('ix_request_for_quotations_issue_date'), 'request_for_quotations', ['issue_date'])
    op.create_index(op.f('ix_request_for_quotations_submission_deadline'), 'request_for_quotations', ['submission_deadline'])
    op.create_index(op.f('ix_request_for_quotations_status'), 'request_for_quotations', ['status'])

    # RFQ Items table
    op.create_table('rfq_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rfq_id', sa.Integer(), nullable=False),
        sa.Column('item_code', sa.String(length=100), nullable=False),
        sa.Column('item_name', sa.String(length=200), nullable=False),
        sa.Column('item_description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('specifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('required_delivery_date', sa.Date(), nullable=True),
        sa.Column('delivery_location', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rfq_id'], ['request_for_quotations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rfq_items_id'), 'rfq_items', ['id'])
    op.create_index(op.f('ix_rfq_items_rfq_id'), 'rfq_items', ['rfq_id'])
    op.create_index(op.f('ix_rfq_items_item_code'), 'rfq_items', ['item_code'])

    # Vendor RFQ table
    op.create_table('vendor_rfqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rfq_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('invited_date', sa.Date(), nullable=False),
        sa.Column('invitation_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('has_responded', sa.Boolean(), nullable=False, default=False),
        sa.Column('response_date', sa.Date(), nullable=True),
        sa.Column('decline_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rfq_id'], ['request_for_quotations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rfq_id', 'vendor_id', name='uq_rfq_vendor')
    )
    op.create_index('idx_vendor_rfq_response', 'vendor_rfqs', ['has_responded'])
    op.create_index(op.f('ix_vendor_rfqs_id'), 'vendor_rfqs', ['id'])
    op.create_index(op.f('ix_vendor_rfqs_rfq_id'), 'vendor_rfqs', ['rfq_id'])
    op.create_index(op.f('ix_vendor_rfqs_vendor_id'), 'vendor_rfqs', ['vendor_id'])
    op.create_index(op.f('ix_vendor_rfqs_invited_date'), 'vendor_rfqs', ['invited_date'])

    # Vendor Quotations table
    op.create_table('vendor_quotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('rfq_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('quotation_number', sa.String(length=50), nullable=False),
        sa.Column('quotation_date', sa.Date(), nullable=False),
        sa.Column('validity_date', sa.Date(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.00),
        sa.Column('grand_total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_terms', sa.String(length=100), nullable=True),
        sa.Column('delivery_terms', sa.String(length=100), nullable=True),
        sa.Column('warranty_terms', sa.Text(), nullable=True),
        sa.Column('is_selected', sa.Boolean(), nullable=False, default=False),
        sa.Column('selection_rank', sa.Integer(), nullable=True),
        sa.Column('technical_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('commercial_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('overall_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('evaluation_notes', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['rfq_id'], ['request_for_quotations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'quotation_number', name='uq_org_quotation_number')
    )
    op.create_index('idx_quotation_rfq_vendor', 'vendor_quotations', ['rfq_id', 'vendor_id'])
    op.create_index('idx_quotation_selected', 'vendor_quotations', ['is_selected'])
    op.create_index(op.f('ix_vendor_quotations_id'), 'vendor_quotations', ['id'])
    op.create_index(op.f('ix_vendor_quotations_organization_id'), 'vendor_quotations', ['organization_id'])
    op.create_index(op.f('ix_vendor_quotations_rfq_id'), 'vendor_quotations', ['rfq_id'])
    op.create_index(op.f('ix_vendor_quotations_vendor_id'), 'vendor_quotations', ['vendor_id'])
    op.create_index(op.f('ix_vendor_quotations_quotation_number'), 'vendor_quotations', ['quotation_number'])
    op.create_index(op.f('ix_vendor_quotations_quotation_date'), 'vendor_quotations', ['quotation_date'])

    # Quotation Items table
    op.create_table('quotation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quotation_id', sa.Integer(), nullable=False),
        sa.Column('rfq_item_id', sa.Integer(), nullable=False),
        sa.Column('vendor_item_code', sa.String(length=100), nullable=True),
        sa.Column('vendor_item_name', sa.String(length=200), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('quoted_quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('delivery_period', sa.String(length=50), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('meets_specifications', sa.Boolean(), nullable=False, default=True),
        sa.Column('deviation_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['quotation_id'], ['vendor_quotations.id'], ),
        sa.ForeignKeyConstraint(['rfq_item_id'], ['rfq_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quotation_items_id'), 'quotation_items', ['id'])
    op.create_index(op.f('ix_quotation_items_quotation_id'), 'quotation_items', ['quotation_id'])
    op.create_index(op.f('ix_quotation_items_rfq_item_id'), 'quotation_items', ['rfq_item_id'])

    # Vendor Evaluations table
    op.create_table('vendor_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_date', sa.Date(), nullable=False),
        sa.Column('evaluation_type', sa.String(length=50), nullable=False),
        sa.Column('quality_rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('delivery_rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('service_rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('price_rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('communication_rating', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('overall_rating', sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('on_time_delivery_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('quality_rejection_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('vendor_status', sa.Enum('ACTIVE', 'INACTIVE', 'BLACKLISTED', 'UNDER_REVIEW', name='vendorstatus'), nullable=False, default='ACTIVE'),
        sa.Column('evaluated_by', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.ForeignKeyConstraint(['evaluated_by'], ['platform_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_vendor_eval_org_date', 'vendor_evaluations', ['organization_id', 'evaluation_date'])
    op.create_index('idx_vendor_eval_rating', 'vendor_evaluations', ['overall_rating'])
    op.create_index(op.f('ix_vendor_evaluations_id'), 'vendor_evaluations', ['id'])
    op.create_index(op.f('ix_vendor_evaluations_organization_id'), 'vendor_evaluations', ['organization_id'])
    op.create_index(op.f('ix_vendor_evaluations_vendor_id'), 'vendor_evaluations', ['vendor_id'])
    op.create_index(op.f('ix_vendor_evaluations_evaluation_date'), 'vendor_evaluations', ['evaluation_date'])

    # Purchase Requisitions table
    op.create_table('purchase_requisitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('requisition_number', sa.String(length=50), nullable=False),
        sa.Column('requisition_date', sa.Date(), nullable=False),
        sa.Column('required_date', sa.Date(), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('cost_center', sa.String(length=100), nullable=True),
        sa.Column('project_code', sa.String(length=100), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('estimated_budget', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['platform_users.id'], ),
        sa.ForeignKeyConstraint(['requested_by'], ['platform_users.id'], ),
        # Note: purchase_order_id FK will be added when purchase_orders table is created
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requisition_number')
    )
    op.create_index('idx_pr_org_status', 'purchase_requisitions', ['organization_id', 'approval_status'])
    op.create_index('idx_pr_required_date', 'purchase_requisitions', ['required_date'])
    op.create_index(op.f('ix_purchase_requisitions_id'), 'purchase_requisitions', ['id'])
    op.create_index(op.f('ix_purchase_requisitions_organization_id'), 'purchase_requisitions', ['organization_id'])
    op.create_index(op.f('ix_purchase_requisitions_requisition_number'), 'purchase_requisitions', ['requisition_number'])
    op.create_index(op.f('ix_purchase_requisitions_requisition_date'), 'purchase_requisitions', ['requisition_date'])
    op.create_index(op.f('ix_purchase_requisitions_required_date'), 'purchase_requisitions', ['required_date'])
    op.create_index(op.f('ix_purchase_requisitions_approval_status'), 'purchase_requisitions', ['approval_status'])
    op.create_index(op.f('ix_purchase_requisitions_purchase_order_id'), 'purchase_requisitions', ['purchase_order_id'])

    # Purchase Requisition Items table
    op.create_table('purchase_requisition_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requisition_id', sa.Integer(), nullable=False),
        sa.Column('item_code', sa.String(length=100), nullable=False),
        sa.Column('item_name', sa.String(length=200), nullable=False),
        sa.Column('item_description', sa.Text(), nullable=True),
        sa.Column('required_quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('estimated_unit_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('estimated_total_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('specifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_vendor', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_requisition_items_id'), 'purchase_requisition_items', ['id'])
    op.create_index(op.f('ix_purchase_requisition_items_requisition_id'), 'purchase_requisition_items', ['requisition_id'])
    op.create_index(op.f('ix_purchase_requisition_items_item_code'), 'purchase_requisition_items', ['item_code'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('purchase_requisition_items')
    op.drop_table('purchase_requisitions')
    op.drop_table('vendor_evaluations')
    op.drop_table('quotation_items')
    op.drop_table('vendor_quotations')
    op.drop_table('vendor_rfqs')
    op.drop_table('rfq_items')
    op.drop_table('request_for_quotations')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS rfqstatus')
    op.execute('DROP TYPE IF EXISTS vendorstatus')