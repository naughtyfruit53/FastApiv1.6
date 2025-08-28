"""Add CRM, Marketing, and enhanced Service Desk models

Revision ID: add_crm_marketing_service_desk
Revises: 2be0230fa04b
Create Date: 2024-08-27 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_crm_marketing_service_desk'
down_revision = '2be0230fa04b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### CRM Models ###
    
    # Create leads table
    op.create_table('leads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('lead_number', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('company', sa.String(), nullable=True),
    sa.Column('job_title', sa.String(), nullable=True),
    sa.Column('address1', sa.String(), nullable=True),
    sa.Column('address2', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('pin_code', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CONVERTED', 'LOST', 'NURTURING', name='leadstatus'), nullable=False),
    sa.Column('source', sa.Enum('WEBSITE', 'REFERRAL', 'EMAIL_CAMPAIGN', 'SOCIAL_MEDIA', 'COLD_CALL', 'TRADE_SHOW', 'PARTNER', 'ADVERTISEMENT', 'OTHER', name='leadsource'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('is_qualified', sa.Boolean(), nullable=False),
    sa.Column('qualification_notes', sa.Text(), nullable=True),
    sa.Column('estimated_value', sa.Float(), nullable=True),
    sa.Column('expected_close_date', sa.Date(), nullable=True),
    sa.Column('assigned_to_id', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('converted_to_customer_id', sa.Integer(), nullable=True),
    sa.Column('converted_to_opportunity_id', sa.Integer(), nullable=True),
    sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('custom_fields', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_contacted', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], name='fk_lead_assigned_to_id'),
    sa.ForeignKeyConstraint(['converted_to_customer_id'], ['customers.id'], name='fk_lead_converted_customer_id'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_lead_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_lead_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'lead_number', name='uq_lead_org_number')
    )
    
    # Create indexes for leads
    op.create_index('idx_lead_company', 'leads', ['company'], unique=False)
    op.create_index('idx_lead_org_assigned', 'leads', ['organization_id', 'assigned_to_id'], unique=False)
    op.create_index('idx_lead_org_source', 'leads', ['organization_id', 'source'], unique=False)
    op.create_index('idx_lead_org_status', 'leads', ['organization_id', 'status'], unique=False)
    op.create_index('idx_lead_qualified', 'leads', ['is_qualified'], unique=False)
    op.create_index('idx_lead_score', 'leads', ['score'], unique=False)
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=False)
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)
    op.create_index(op.f('ix_leads_lead_number'), 'leads', ['lead_number'], unique=True)
    op.create_index(op.f('ix_leads_organization_id'), 'leads', ['organization_id'], unique=False)
    
    # Create opportunities table
    op.create_table('opportunities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('opportunity_number', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('stage', sa.Enum('PROSPECTING', 'QUALIFICATION', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST', name='opportunitystage'), nullable=False),
    sa.Column('probability', sa.Float(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('expected_revenue', sa.Float(), nullable=False),
    sa.Column('expected_close_date', sa.Date(), nullable=False),
    sa.Column('actual_close_date', sa.Date(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('lead_id', sa.Integer(), nullable=True),
    sa.Column('assigned_to_id', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('competitors', sa.Text(), nullable=True),
    sa.Column('win_reason', sa.Text(), nullable=True),
    sa.Column('loss_reason', sa.Text(), nullable=True),
    sa.Column('source', sa.Enum('WEBSITE', 'REFERRAL', 'EMAIL_CAMPAIGN', 'SOCIAL_MEDIA', 'COLD_CALL', 'TRADE_SHOW', 'PARTNER', 'ADVERTISEMENT', 'OTHER', name='leadsource'), nullable=False),
    sa.Column('custom_fields', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], name='fk_opportunity_assigned_to_id'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_opportunity_created_by_id'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_opportunity_customer_id'),
    sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], name='fk_opportunity_lead_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_opportunity_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'opportunity_number', name='uq_opportunity_org_number')
    )
    
    # Create indexes for opportunities
    op.create_index('idx_opportunity_amount', 'opportunities', ['amount'], unique=False)
    op.create_index('idx_opportunity_close_date', 'opportunities', ['expected_close_date'], unique=False)
    op.create_index('idx_opportunity_org_assigned', 'opportunities', ['organization_id', 'assigned_to_id'], unique=False)
    op.create_index('idx_opportunity_org_stage', 'opportunities', ['organization_id', 'stage'], unique=False)
    op.create_index('idx_opportunity_probability', 'opportunities', ['probability'], unique=False)
    op.create_index(op.f('ix_opportunities_id'), 'opportunities', ['id'], unique=False)
    op.create_index(op.f('ix_opportunities_name'), 'opportunities', ['name'], unique=False)
    op.create_index(op.f('ix_opportunities_opportunity_number'), 'opportunities', ['opportunity_number'], unique=True)
    op.create_index(op.f('ix_opportunities_organization_id'), 'opportunities', ['organization_id'], unique=False)
    
    # Add foreign key constraint from leads to opportunities
    op.create_foreign_key('fk_lead_converted_opportunity_id', 'leads', 'opportunities', ['converted_to_opportunity_id'], ['id'])
    
    # Create lead_activities table
    op.create_table('lead_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('lead_id', sa.Integer(), nullable=False),
    sa.Column('activity_type', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('outcome', sa.String(), nullable=True),
    sa.Column('activity_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_lead_activity_created_by_id'),
    sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], name='fk_lead_activity_lead_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_lead_activity_organization_id'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for lead_activities
    op.create_index('idx_lead_activity_date', 'lead_activities', ['activity_date'], unique=False)
    op.create_index('idx_lead_activity_org_lead', 'lead_activities', ['organization_id', 'lead_id'], unique=False)
    op.create_index('idx_lead_activity_type', 'lead_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_lead_activities_id'), 'lead_activities', ['id'], unique=False)
    op.create_index(op.f('ix_lead_activities_organization_id'), 'lead_activities', ['organization_id'], unique=False)
    
    # Create opportunity_activities table
    op.create_table('opportunity_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('opportunity_id', sa.Integer(), nullable=False),
    sa.Column('activity_type', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('outcome', sa.String(), nullable=True),
    sa.Column('activity_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_opportunity_activity_created_by_id'),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], name='fk_opportunity_activity_opportunity_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_opportunity_activity_organization_id'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for opportunity_activities
    op.create_index('idx_opportunity_activity_date', 'opportunity_activities', ['activity_date'], unique=False)
    op.create_index('idx_opportunity_activity_org_opp', 'opportunity_activities', ['organization_id', 'opportunity_id'], unique=False)
    op.create_index('idx_opportunity_activity_type', 'opportunity_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_opportunity_activities_id'), 'opportunity_activities', ['id'], unique=False)
    op.create_index(op.f('ix_opportunity_activities_organization_id'), 'opportunity_activities', ['organization_id'], unique=False)
    
    # Create opportunity_products table
    op.create_table('opportunity_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('opportunity_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('product_name', sa.String(), nullable=False),
    sa.Column('product_description', sa.Text(), nullable=True),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('discount_percent', sa.Float(), nullable=False),
    sa.Column('discount_amount', sa.Float(), nullable=False),
    sa.Column('final_amount', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], name='fk_opportunity_product_opportunity_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_opportunity_product_organization_id'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_opportunity_product_product_id'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for opportunity_products
    op.create_index('idx_opportunity_product_org_opp', 'opportunity_products', ['organization_id', 'opportunity_id'], unique=False)
    op.create_index(op.f('ix_opportunity_products_id'), 'opportunity_products', ['id'], unique=False)
    op.create_index(op.f('ix_opportunity_products_organization_id'), 'opportunity_products', ['organization_id'], unique=False)
    
    # Create sales_pipelines table
    op.create_table('sales_pipelines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('stages', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_sales_pipeline_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_sales_pipeline_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'name', name='uq_sales_pipeline_org_name')
    )
    
    # Create indexes for sales_pipelines
    op.create_index('idx_sales_pipeline_org_default', 'sales_pipelines', ['organization_id', 'is_default'], unique=False)
    op.create_index(op.f('ix_sales_pipelines_id'), 'sales_pipelines', ['id'], unique=False)
    op.create_index(op.f('ix_sales_pipelines_organization_id'), 'sales_pipelines', ['organization_id'], unique=False)
    
    # Create sales_forecasts table
    op.create_table('sales_forecasts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('forecast_period', sa.String(), nullable=False),
    sa.Column('period_start', sa.Date(), nullable=False),
    sa.Column('period_end', sa.Date(), nullable=False),
    sa.Column('predicted_revenue', sa.Float(), nullable=False),
    sa.Column('weighted_revenue', sa.Float(), nullable=False),
    sa.Column('committed_revenue', sa.Float(), nullable=False),
    sa.Column('best_case_revenue', sa.Float(), nullable=False),
    sa.Column('worst_case_revenue', sa.Float(), nullable=False),
    sa.Column('total_opportunities', sa.Integer(), nullable=False),
    sa.Column('opportunities_by_stage', sa.JSON(), nullable=False),
    sa.Column('model_version', sa.String(), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_sales_forecast_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_sales_forecast_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'forecast_period', 'period_start', 'period_end', name='uq_sales_forecast_period')
    )
    
    # Create indexes for sales_forecasts
    op.create_index('idx_sales_forecast_org_period', 'sales_forecasts', ['organization_id', 'forecast_period', 'period_start'], unique=False)
    op.create_index(op.f('ix_sales_forecasts_id'), 'sales_forecasts', ['id'], unique=False)
    op.create_index(op.f('ix_sales_forecasts_organization_id'), 'sales_forecasts', ['organization_id'], unique=False)
    
    # ### Marketing Models ###
    
    # Create campaigns table
    op.create_table('campaigns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('campaign_number', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('campaign_type', sa.Enum('EMAIL', 'SMS', 'SOCIAL_MEDIA', 'DIGITAL_ADS', 'PRINT', 'EVENT', 'WEBINAR', 'CONTENT_MARKETING', 'REFERRAL', 'OTHER', name='campaigntype'), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'SCHEDULED', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED', name='campaignstatus'), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('scheduled_send_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('budget', sa.Float(), nullable=True),
    sa.Column('target_audience_size', sa.Integer(), nullable=True),
    sa.Column('objective', sa.String(), nullable=True),
    sa.Column('subject_line', sa.String(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('creative_assets', sa.JSON(), nullable=True),
    sa.Column('target_criteria', sa.JSON(), nullable=True),
    sa.Column('sent_count', sa.Integer(), nullable=False),
    sa.Column('delivered_count', sa.Integer(), nullable=False),
    sa.Column('opened_count', sa.Integer(), nullable=False),
    sa.Column('clicked_count', sa.Integer(), nullable=False),
    sa.Column('converted_count', sa.Integer(), nullable=False),
    sa.Column('unsubscribed_count', sa.Integer(), nullable=False),
    sa.Column('revenue_generated', sa.Float(), nullable=False),
    sa.Column('cost_per_acquisition', sa.Float(), nullable=True),
    sa.Column('return_on_investment', sa.Float(), nullable=True),
    sa.Column('assigned_to_id', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('integration_settings', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('launched_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], name='fk_campaign_assigned_to_id'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_campaign_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_campaign_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'campaign_number', name='uq_campaign_org_number')
    )
    
    # Create indexes for campaigns
    op.create_index('idx_campaign_dates', 'campaigns', ['start_date', 'end_date'], unique=False)
    op.create_index('idx_campaign_org_status', 'campaigns', ['organization_id', 'status'], unique=False)
    op.create_index('idx_campaign_org_type', 'campaigns', ['organization_id', 'campaign_type'], unique=False)
    op.create_index(op.f('ix_campaigns_campaign_number'), 'campaigns', ['campaign_number'], unique=True)
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_name'), 'campaigns', ['name'], unique=False)
    op.create_index(op.f('ix_campaigns_organization_id'), 'campaigns', ['organization_id'], unique=False)
    
    # Create promotions table
    op.create_table('promotions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('promotion_code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('promotion_type', sa.Enum('PERCENTAGE_DISCOUNT', 'FIXED_AMOUNT_DISCOUNT', 'BUY_X_GET_Y', 'FREE_SHIPPING', 'BUNDLE_OFFER', 'CASHBACK', 'LOYALTY_POINTS', name='promotiontype'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('valid_from', sa.Date(), nullable=False),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('discount_percentage', sa.Float(), nullable=True),
    sa.Column('discount_amount', sa.Float(), nullable=True),
    sa.Column('minimum_purchase_amount', sa.Float(), nullable=True),
    sa.Column('maximum_discount_amount', sa.Float(), nullable=True),
    sa.Column('usage_limit_total', sa.Integer(), nullable=True),
    sa.Column('usage_limit_per_customer', sa.Integer(), nullable=True),
    sa.Column('current_usage_count', sa.Integer(), nullable=False),
    sa.Column('buy_quantity', sa.Integer(), nullable=True),
    sa.Column('get_quantity', sa.Integer(), nullable=True),
    sa.Column('get_discount_percentage', sa.Float(), nullable=True),
    sa.Column('applicable_products', sa.JSON(), nullable=True),
    sa.Column('applicable_categories', sa.JSON(), nullable=True),
    sa.Column('exclude_products', sa.JSON(), nullable=True),
    sa.Column('target_customer_segments', sa.JSON(), nullable=True),
    sa.Column('new_customers_only', sa.Boolean(), nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.Column('total_redemptions', sa.Integer(), nullable=False),
    sa.Column('total_discount_given', sa.Float(), nullable=False),
    sa.Column('total_revenue_impact', sa.Float(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_promotion_campaign_id'),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_promotion_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_promotion_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'promotion_code', name='uq_promotion_org_code')
    )
    
    # Create indexes for promotions
    op.create_index('idx_promotion_org_active', 'promotions', ['organization_id', 'is_active'], unique=False)
    op.create_index('idx_promotion_org_type', 'promotions', ['organization_id', 'promotion_type'], unique=False)
    op.create_index('idx_promotion_validity', 'promotions', ['valid_from', 'valid_until'], unique=False)
    op.create_index(op.f('ix_promotions_id'), 'promotions', ['id'], unique=False)
    op.create_index(op.f('ix_promotions_name'), 'promotions', ['name'], unique=False)
    op.create_index(op.f('ix_promotions_organization_id'), 'promotions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_promotions_promotion_code'), 'promotions', ['promotion_code'], unique=False)
    
    # ### Enhanced Service Desk Models ###
    
    # Create chatbot_conversations table
    op.create_table('chatbot_conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.String(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('customer_email', sa.String(), nullable=True),
    sa.Column('customer_phone', sa.String(), nullable=True),
    sa.Column('customer_name', sa.String(), nullable=True),
    sa.Column('channel', sa.String(), nullable=False),
    sa.Column('channel_user_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('intent', sa.String(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('escalated_to_human', sa.Boolean(), nullable=False),
    sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('assigned_agent_id', sa.Integer(), nullable=True),
    sa.Column('escalation_reason', sa.String(), nullable=True),
    sa.Column('resolved_by_bot', sa.Boolean(), nullable=False),
    sa.Column('resolution_category', sa.String(), nullable=True),
    sa.Column('customer_satisfaction', sa.Integer(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['assigned_agent_id'], ['users.id'], name='fk_chatbot_conversation_agent_id'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_chatbot_conversation_customer_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_chatbot_conversation_organization_id'),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], name='fk_chatbot_conversation_ticket_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'conversation_id', name='uq_chatbot_conversation_org_id')
    )
    
    # Create indexes for chatbot_conversations
    op.create_index('idx_chatbot_conversation_channel', 'chatbot_conversations', ['channel'], unique=False)
    op.create_index('idx_chatbot_conversation_escalated', 'chatbot_conversations', ['escalated_to_human'], unique=False)
    op.create_index('idx_chatbot_conversation_intent', 'chatbot_conversations', ['intent'], unique=False)
    op.create_index('idx_chatbot_conversation_org_status', 'chatbot_conversations', ['organization_id', 'status'], unique=False)
    op.create_index('idx_chatbot_conversation_started', 'chatbot_conversations', ['started_at'], unique=False)
    op.create_index(op.f('ix_chatbot_conversations_conversation_id'), 'chatbot_conversations', ['conversation_id'], unique=True)
    op.create_index(op.f('ix_chatbot_conversations_id'), 'chatbot_conversations', ['id'], unique=False)
    op.create_index(op.f('ix_chatbot_conversations_organization_id'), 'chatbot_conversations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_chatbot_conversations_session_id'), 'chatbot_conversations', ['session_id'], unique=False)
    
    # Create chatbot_messages table
    op.create_table('chatbot_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('message_type', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('message_format', sa.String(), nullable=False),
    sa.Column('sender_id', sa.String(), nullable=True),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('intent_detected', sa.String(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('entities_extracted', sa.JSON(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['users.id'], name='fk_chatbot_message_agent_id'),
    sa.ForeignKeyConstraint(['conversation_id'], ['chatbot_conversations.id'], name='fk_chatbot_message_conversation_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_chatbot_message_organization_id'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for chatbot_messages
    op.create_index('idx_chatbot_message_created', 'chatbot_messages', ['created_at'], unique=False)
    op.create_index('idx_chatbot_message_org_conversation', 'chatbot_messages', ['organization_id', 'conversation_id'], unique=False)
    op.create_index('idx_chatbot_message_type', 'chatbot_messages', ['message_type'], unique=False)
    op.create_index(op.f('ix_chatbot_messages_id'), 'chatbot_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chatbot_messages_organization_id'), 'chatbot_messages', ['organization_id'], unique=False)
    
    # Create survey_templates table
    op.create_table('survey_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('template_type', sa.String(), nullable=False),
    sa.Column('questions', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('trigger_event', sa.String(), nullable=False),
    sa.Column('trigger_delay_hours', sa.Integer(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_survey_template_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_survey_template_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'name', name='uq_survey_template_org_name')
    )
    
    # Create indexes for survey_templates
    op.create_index('idx_survey_template_active', 'survey_templates', ['is_active'], unique=False)
    op.create_index('idx_survey_template_org_type', 'survey_templates', ['organization_id', 'template_type'], unique=False)
    op.create_index('idx_survey_template_trigger', 'survey_templates', ['trigger_event'], unique=False)
    op.create_index(op.f('ix_survey_templates_id'), 'survey_templates', ['id'], unique=False)
    op.create_index(op.f('ix_survey_templates_name'), 'survey_templates', ['name'], unique=False)
    op.create_index(op.f('ix_survey_templates_organization_id'), 'survey_templates', ['organization_id'], unique=False)
    
    # Create customer_surveys table
    op.create_table('customer_surveys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('survey_token', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('customer_email', sa.String(), nullable=True),
    sa.Column('customer_name', sa.String(), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('responses', sa.JSON(), nullable=True),
    sa.Column('overall_rating', sa.Integer(), nullable=True),
    sa.Column('nps_score', sa.Integer(), nullable=True),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_customer_survey_customer_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_customer_survey_organization_id'),
    sa.ForeignKeyConstraint(['template_id'], ['survey_templates.id'], name='fk_customer_survey_template_id'),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], name='fk_customer_survey_ticket_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'survey_token', name='uq_customer_survey_org_token')
    )
    
    # Create indexes for customer_surveys
    op.create_index('idx_customer_survey_completed', 'customer_surveys', ['completed_at'], unique=False)
    op.create_index('idx_customer_survey_customer', 'customer_surveys', ['customer_id'], unique=False)
    op.create_index('idx_customer_survey_org_template', 'customer_surveys', ['organization_id', 'template_id'], unique=False)
    op.create_index('idx_customer_survey_status', 'customer_surveys', ['status'], unique=False)
    op.create_index('idx_customer_survey_ticket', 'customer_surveys', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_customer_surveys_id'), 'customer_surveys', ['id'], unique=False)
    op.create_index(op.f('ix_customer_surveys_organization_id'), 'customer_surveys', ['organization_id'], unique=False)
    op.create_index(op.f('ix_customer_surveys_survey_token'), 'customer_surveys', ['survey_token'], unique=True)
    
    # Create channel_configurations table
    op.create_table('channel_configurations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('channel_type', sa.String(), nullable=False),
    sa.Column('channel_name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('configuration', sa.JSON(), nullable=False),
    sa.Column('bot_enabled', sa.Boolean(), nullable=False),
    sa.Column('auto_escalation_enabled', sa.Boolean(), nullable=False),
    sa.Column('escalation_threshold_minutes', sa.Integer(), nullable=False),
    sa.Column('business_hours', sa.JSON(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_channel_config_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_channel_config_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'channel_type', 'channel_name', name='uq_channel_config_org_type_name')
    )
    
    # Create indexes for channel_configurations
    op.create_index('idx_channel_config_active', 'channel_configurations', ['is_active'], unique=False)
    op.create_index('idx_channel_config_org_type', 'channel_configurations', ['organization_id', 'channel_type'], unique=False)
    op.create_index(op.f('ix_channel_configurations_id'), 'channel_configurations', ['id'], unique=False)
    op.create_index(op.f('ix_channel_configurations_organization_id'), 'channel_configurations', ['organization_id'], unique=False)
    
    # Create additional tables that are referenced by main tables
    
    # Create promotion_redemptions table
    op.create_table('promotion_redemptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('promotion_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('voucher_type', sa.String(), nullable=True),
    sa.Column('voucher_id', sa.Integer(), nullable=True),
    sa.Column('voucher_number', sa.String(), nullable=True),
    sa.Column('discount_amount', sa.Float(), nullable=False),
    sa.Column('order_amount', sa.Float(), nullable=False),
    sa.Column('final_amount', sa.Float(), nullable=False),
    sa.Column('redeemed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_promotion_redemption_customer_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_promotion_redemption_organization_id'),
    sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], name='fk_promotion_redemption_promotion_id'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for promotion_redemptions
    op.create_index('idx_promotion_redemption_customer', 'promotion_redemptions', ['customer_id'], unique=False)
    op.create_index('idx_promotion_redemption_date', 'promotion_redemptions', ['redeemed_at'], unique=False)
    op.create_index('idx_promotion_redemption_org_promotion', 'promotion_redemptions', ['organization_id', 'promotion_id'], unique=False)
    op.create_index(op.f('ix_promotion_redemptions_id'), 'promotion_redemptions', ['id'], unique=False)
    op.create_index(op.f('ix_promotion_redemptions_organization_id'), 'promotion_redemptions', ['organization_id'], unique=False)
    
    # Create campaign_analytics table
    op.create_table('campaign_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=False),
    sa.Column('analytics_date', sa.Date(), nullable=False),
    sa.Column('hour', sa.Integer(), nullable=True),
    sa.Column('impressions', sa.Integer(), nullable=False),
    sa.Column('clicks', sa.Integer(), nullable=False),
    sa.Column('conversions', sa.Integer(), nullable=False),
    sa.Column('spend', sa.Float(), nullable=False),
    sa.Column('revenue', sa.Float(), nullable=False),
    sa.Column('emails_sent', sa.Integer(), nullable=True),
    sa.Column('emails_delivered', sa.Integer(), nullable=True),
    sa.Column('emails_opened', sa.Integer(), nullable=True),
    sa.Column('emails_clicked', sa.Integer(), nullable=True),
    sa.Column('unsubscribes', sa.Integer(), nullable=True),
    sa.Column('bounces', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('shares', sa.Integer(), nullable=True),
    sa.Column('comments', sa.Integer(), nullable=True),
    sa.Column('followers_gained', sa.Integer(), nullable=True),
    sa.Column('custom_metrics', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_campaign_analytics_campaign_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_campaign_analytics_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('campaign_id', 'analytics_date', 'hour', name='uq_campaign_analytics_date_hour')
    )
    
    # Create indexes for campaign_analytics
    op.create_index('idx_campaign_analytics_date', 'campaign_analytics', ['analytics_date'], unique=False)
    op.create_index('idx_campaign_analytics_org_campaign', 'campaign_analytics', ['organization_id', 'campaign_id'], unique=False)
    op.create_index(op.f('ix_campaign_analytics_id'), 'campaign_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_campaign_analytics_organization_id'), 'campaign_analytics', ['organization_id'], unique=False)
    
    # Create marketing_lists table
    op.create_table('marketing_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('list_type', sa.String(), nullable=False),
    sa.Column('segmentation_criteria', sa.JSON(), nullable=True),
    sa.Column('total_contacts', sa.Integer(), nullable=False),
    sa.Column('active_contacts', sa.Integer(), nullable=False),
    sa.Column('opted_out_contacts', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_marketing_list_created_by_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_marketing_list_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('organization_id', 'name', name='uq_marketing_list_org_name')
    )
    
    # Create indexes for marketing_lists
    op.create_index('idx_marketing_list_active', 'marketing_lists', ['is_active'], unique=False)
    op.create_index('idx_marketing_list_org_type', 'marketing_lists', ['organization_id', 'list_type'], unique=False)
    op.create_index(op.f('ix_marketing_lists_id'), 'marketing_lists', ['id'], unique=False)
    op.create_index(op.f('ix_marketing_lists_name'), 'marketing_lists', ['name'], unique=False)
    op.create_index(op.f('ix_marketing_lists_organization_id'), 'marketing_lists', ['organization_id'], unique=False)
    
    # Create marketing_list_contacts table
    op.create_table('marketing_list_contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('marketing_list_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('is_subscribed', sa.Boolean(), nullable=False),
    sa.Column('subscribed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('unsubscribed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('opt_in_source', sa.String(), nullable=True),
    sa.Column('custom_attributes', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], name='fk_marketing_list_contact_customer_id'),
    sa.ForeignKeyConstraint(['marketing_list_id'], ['marketing_lists.id'], name='fk_marketing_list_contact_list_id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_marketing_list_contact_organization_id'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('marketing_list_id', 'customer_id', name='uq_marketing_list_contact_customer'),
    sa.UniqueConstraint('marketing_list_id', 'email', name='uq_marketing_list_contact_email')
    )
    
    # Create indexes for marketing_list_contacts
    op.create_index('idx_marketing_list_contact_email', 'marketing_list_contacts', ['email'], unique=False)
    op.create_index('idx_marketing_list_contact_org_list', 'marketing_list_contacts', ['organization_id', 'marketing_list_id'], unique=False)
    op.create_index('idx_marketing_list_contact_subscribed', 'marketing_list_contacts', ['is_subscribed'], unique=False)
    op.create_index(op.f('ix_marketing_list_contacts_id'), 'marketing_list_contacts', ['id'], unique=False)
    op.create_index(op.f('ix_marketing_list_contacts_organization_id'), 'marketing_list_contacts', ['organization_id'], unique=False)


def downgrade() -> None:
    # Drop all the new tables in reverse order
    op.drop_table('marketing_list_contacts')
    op.drop_table('marketing_lists')
    op.drop_table('campaign_analytics')
    op.drop_table('promotion_redemptions')
    op.drop_table('channel_configurations')
    op.drop_table('customer_surveys')
    op.drop_table('survey_templates')
    op.drop_table('chatbot_messages')
    op.drop_table('chatbot_conversations')
    op.drop_table('promotions')
    op.drop_table('campaigns')
    op.drop_table('sales_forecasts')
    op.drop_table('sales_pipelines')
    op.drop_table('opportunity_products')
    op.drop_table('opportunity_activities')
    op.drop_table('lead_activities')
    op.drop_table('opportunities')
    op.drop_table('leads')
    
    # Drop enum types
    sa.Enum('leadstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum('leadsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum('opportunitystage').drop(op.get_bind(), checkfirst=True)
    sa.Enum('campaigntype').drop(op.get_bind(), checkfirst=True)
    sa.Enum('campaignstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum('promotiontype').drop(op.get_bind(), checkfirst=True)