# seed_crm_marketing_service_data.py

"""
Sample data seeding script for CRM, Marketing, and enhanced Service Desk modules.
This script creates realistic demo data for testing and demonstration purposes.
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import (
    Organization, User, Customer, Product,
    # CRM Models
    Lead, Opportunity, OpportunityProduct, LeadActivity, OpportunityActivity,
    SalesPipeline, SalesForecast,
    # Marketing Models
    Campaign, Promotion, PromotionRedemption, CampaignAnalytics,
    MarketingList, MarketingListContact,
    # Service Desk Models
    ChatbotConversation, ChatbotMessage, SurveyTemplate, CustomerSurvey,
    ChannelConfiguration
)
from app.models.crm_models import LeadStatus, LeadSource, OpportunityStage
from app.models.marketing_models import CampaignType, CampaignStatus, PromotionType

def seed_crm_data(db: Session, org_id: int, user_id: int, customers: List[Customer]):
    """Seed CRM data - leads, opportunities, activities, etc."""
    print("🔄 Seeding CRM data...")
    
    # Create Sales Pipeline
    pipeline = SalesPipeline(
        organization_id=org_id,
        name="Standard Sales Pipeline",
        description="Default sales pipeline for all opportunities",
        is_default=True,
        is_active=True,
        stages={
            "prospecting": {"probability": 10, "color": "#f3f4f6"},
            "qualification": {"probability": 25, "color": "#dbeafe"},
            "proposal": {"probability": 50, "color": "#fef3c7"},
            "negotiation": {"probability": 75, "color": "#fecaca"},
            "closed_won": {"probability": 100, "color": "#dcfce7"},
            "closed_lost": {"probability": 0, "color": "#f3f4f6"}
        },
        created_by_id=user_id
    )
    db.add(pipeline)
    db.flush()
    
    # Create Leads
    leads_data = [
        {
            "first_name": "John", "last_name": "Doe", "email": "john.doe@abccorp.com",
            "phone": "+1-555-0101", "company": "ABC Corporation",
            "job_title": "IT Manager", "status": LeadStatus.QUALIFIED,
            "source": LeadSource.WEBSITE, "score": 85, "estimated_value": 75000,
            "description": "Interested in ERP implementation for manufacturing division"
        },
        {
            "first_name": "Jane", "last_name": "Smith", "email": "jane.smith@xyzinc.com",
            "phone": "+1-555-0102", "company": "XYZ Inc",
            "job_title": "CTO", "status": LeadStatus.CONTACTED,
            "source": LeadSource.REFERRAL, "score": 92, "estimated_value": 120000,
            "description": "Looking for comprehensive business management solution"
        },
        {
            "first_name": "Mike", "last_name": "Johnson", "email": "mike.j@techstart.com",
            "phone": "+1-555-0103", "company": "TechStart Solutions",
            "job_title": "Operations Director", "status": LeadStatus.NEW,
            "source": LeadSource.EMAIL_CAMPAIGN, "score": 68, "estimated_value": 45000,
            "description": "Startup looking for scalable ERP solution"
        },
        {
            "first_name": "Sarah", "last_name": "Williams", "email": "sarah.williams@megacorp.com",
            "phone": "+1-555-0104", "company": "MegaCorp Industries",
            "job_title": "CFO", "status": LeadStatus.PROPOSAL,
            "source": LeadSource.TRADE_SHOW, "score": 95, "estimated_value": 250000,
            "description": "Enterprise client seeking full digital transformation"
        },
        {
            "first_name": "David", "last_name": "Brown", "email": "david.brown@retailplus.com",
            "phone": "+1-555-0105", "company": "RetailPlus",
            "job_title": "Store Manager", "status": LeadStatus.NURTURING,
            "source": LeadSource.SOCIAL_MEDIA, "score": 55, "estimated_value": 25000,
            "description": "Retail chain interested in inventory management"
        }
    ]
    
    leads = []
    for i, lead_data in enumerate(leads_data):
        lead = Lead(
            organization_id=org_id,
            lead_number=f"LD{str(i+1).zfill(6)}",
            assigned_to_id=user_id,
            created_by_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=30-i*5),
            **lead_data
        )
        leads.append(lead)
        db.add(lead)
    
    db.flush()
    
    # Create Opportunities
    opportunities_data = [
        {
            "name": "ABC Corp - ERP Implementation",
            "stage": OpportunityStage.PROPOSAL, "probability": 60, "amount": 85000,
            "expected_close_date": date.today() + timedelta(days=30),
            "lead_id": leads[0].id, "customer_id": customers[0].id if customers else None,
            "description": "Complete ERP implementation with training and support"
        },
        {
            "name": "XYZ Inc - Digital Transformation",
            "stage": OpportunityStage.NEGOTIATION, "probability": 80, "amount": 150000,
            "expected_close_date": date.today() + timedelta(days=15),
            "lead_id": leads[1].id, "customer_id": customers[1].id if len(customers) > 1 else None,
            "description": "End-to-end digital transformation project"
        },
        {
            "name": "MegaCorp - Enterprise Solution",
            "stage": OpportunityStage.QUALIFICATION, "probability": 40, "amount": 280000,
            "expected_close_date": date.today() + timedelta(days=60),
            "lead_id": leads[3].id,
            "description": "Large-scale enterprise implementation"
        }
    ]
    
    opportunities = []
    for i, opp_data in enumerate(opportunities_data):
        opportunity = Opportunity(
            organization_id=org_id,
            opportunity_number=f"OP{str(i+1).zfill(6)}",
            assigned_to_id=user_id,
            created_by_id=user_id,
            source=LeadSource.WEBSITE,
            created_at=datetime.utcnow() - timedelta(days=20-i*3),
            **opp_data
        )
        opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
        opportunities.append(opportunity)
        db.add(opportunity)
    
    db.flush()
    
    # Create Lead Activities
    for i, lead in enumerate(leads[:3]):
        activity = LeadActivity(
            organization_id=org_id,
            lead_id=lead.id,
            activity_type="call",
            subject=f"Initial discovery call with {lead.first_name}",
            description="Discussed current challenges and potential solutions",
            outcome="positive",
            activity_date=datetime.utcnow() - timedelta(days=15-i*2),
            duration_minutes=45,
            created_by_id=user_id
        )
        db.add(activity)
    
    # Create Sales Forecast
    forecast = SalesForecast(
        organization_id=org_id,
        forecast_period="quarterly",
        period_start=date.today().replace(day=1),
        period_end=(date.today().replace(day=1) + timedelta(days=90)),
        predicted_revenue=515000,
        weighted_revenue=308000,  # Based on probabilities
        committed_revenue=150000,  # High probability deals
        best_case_revenue=515000,
        worst_case_revenue=200000,
        total_opportunities=len(opportunities),
        opportunities_by_stage={
            "qualification": 1,
            "proposal": 1,
            "negotiation": 1
        },
        model_version="1.0",
        confidence_score=85.5,
        created_by_id=user_id
    )
    db.add(forecast)
    
    print(f"✅ Created {len(leads)} leads, {len(opportunities)} opportunities, and sales forecast")

def seed_marketing_data(db: Session, org_id: int, user_id: int, customers: List[Customer]):
    """Seed Marketing data - campaigns, promotions, lists, etc."""
    print("🔄 Seeding Marketing data...")
    
    # Create Marketing Lists
    email_list = MarketingList(
        organization_id=org_id,
        name="Email Subscribers",
        description="All email newsletter subscribers",
        list_type="email",
        total_contacts=5000,
        active_contacts=4850,
        opted_out_contacts=150,
        created_by_id=user_id
    )
    db.add(email_list)
    
    customer_list = MarketingList(
        organization_id=org_id,
        name="Existing Customers",
        description="Current customer base for retention campaigns",
        list_type="customer",
        total_contacts=len(customers),
        active_contacts=len(customers),
        opted_out_contacts=0,
        created_by_id=user_id
    )
    db.add(customer_list)
    
    db.flush()
    
    # Create Campaigns
    campaigns_data = [
        {
            "name": "Summer Sale 2024",
            "campaign_type": CampaignType.EMAIL,
            "status": CampaignStatus.COMPLETED,
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() - timedelta(days=1),
            "budget": 5000, "target_audience_size": 10000,
            "objective": "Drive summer sales and clear inventory",
            "subject_line": "🌞 Summer Sale: Up to 30% Off Everything!",
            "sent_count": 9950, "delivered_count": 9850,
            "opened_count": 2955, "clicked_count": 590, "converted_count": 118,
            "revenue_generated": 24000
        },
        {
            "name": "Product Launch Campaign",
            "campaign_type": CampaignType.SOCIAL_MEDIA,
            "status": CampaignStatus.ACTIVE,
            "start_date": date.today() - timedelta(days=7),
            "end_date": date.today() + timedelta(days=23),
            "budget": 8000, "target_audience_size": 25000,
            "objective": "Launch new product line and build awareness",
            "sent_count": 0, "delivered_count": 0,
            "opened_count": 0, "clicked_count": 1200, "converted_count": 85,
            "revenue_generated": 12500
        },
        {
            "name": "Customer Retention Email Series",
            "campaign_type": CampaignType.EMAIL,
            "status": CampaignStatus.SCHEDULED,
            "start_date": date.today() + timedelta(days=5),
            "end_date": date.today() + timedelta(days=35),
            "budget": 3000, "target_audience_size": len(customers),
            "objective": "Improve customer retention and increase LTV",
            "subject_line": "We miss you! Here's a special offer",
            "sent_count": 0, "delivered_count": 0,
            "opened_count": 0, "clicked_count": 0, "converted_count": 0,
            "revenue_generated": 0
        }
    ]
    
    campaigns = []
    for i, campaign_data in enumerate(campaigns_data):
        campaign = Campaign(
            organization_id=org_id,
            campaign_number=f"CMP{str(i+1).zfill(6)}",
            assigned_to_id=user_id,
            created_by_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=35-i*5),
            **campaign_data
        )
        if campaign.status == CampaignStatus.COMPLETED:
            campaign.completed_at = datetime.utcnow() - timedelta(days=1)
        campaigns.append(campaign)
        db.add(campaign)
    
    db.flush()
    
    # Create Promotions
    promotions_data = [
        {
            "promotion_code": "SUMMER20",
            "name": "Summer Sale 20% Off",
            "promotion_type": PromotionType.PERCENTAGE_DISCOUNT,
            "is_active": True,
            "valid_from": date.today() - timedelta(days=30),
            "valid_until": date.today() + timedelta(days=30),
            "discount_percentage": 20.0,
            "minimum_purchase_amount": 100.0,
            "maximum_discount_amount": 500.0,
            "usage_limit_total": 1000,
            "current_usage_count": 250,
            "total_redemptions": 250,
            "total_discount_given": 12500.0,
            "campaign_id": campaigns[0].id
        },
        {
            "promotion_code": "NEWCUSTOMER50",
            "name": "New Customer $50 Off",
            "promotion_type": PromotionType.FIXED_AMOUNT_DISCOUNT,
            "is_active": True,
            "valid_from": date.today() - timedelta(days=60),
            "discount_amount": 50.0,
            "minimum_purchase_amount": 200.0,
            "usage_limit_per_customer": 1,
            "new_customers_only": True,
            "current_usage_count": 125,
            "total_redemptions": 125,
            "total_discount_given": 6250.0
        },
        {
            "promotion_code": "BUNDLE2024",
            "name": "Bundle Deal - Buy 2 Get 1 Free",
            "promotion_type": PromotionType.BUY_X_GET_Y,
            "is_active": True,
            "valid_from": date.today(),
            "valid_until": date.today() + timedelta(days=60),
            "buy_quantity": 2,
            "get_quantity": 1,
            "get_discount_percentage": 100.0,
            "usage_limit_total": 500,
            "current_usage_count": 45,
            "total_redemptions": 45,
            "total_discount_given": 3375.0
        }
    ]
    
    for i, promo_data in enumerate(promotions_data):
        promotion = Promotion(
            organization_id=org_id,
            created_by_id=user_id,
            created_at=datetime.utcnow() - timedelta(days=60-i*10),
            **promo_data
        )
        db.add(promotion)
    
    print(f"✅ Created {len(campaigns)} campaigns, {len(promotions_data)} promotions, and marketing lists")

def seed_service_desk_data(db: Session, org_id: int, user_id: int, customers: List[Customer]):
    """Seed enhanced Service Desk data - chatbot, surveys, channels, etc."""
    print("🔄 Seeding enhanced Service Desk data...")
    
    # Create Channel Configurations
    channels_data = [
        {
            "channel_type": "web_chat",
            "channel_name": "Website Live Chat",
            "is_active": True,
            "configuration": {
                "widget_color": "#1976d2",
                "welcome_message": "Hi! How can we help you today?",
                "office_hours": "9:00-17:00"
            },
            "bot_enabled": True,
            "auto_escalation_enabled": True,
            "escalation_threshold_minutes": 5,
            "business_hours": {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"}
            },
            "timezone": "UTC"
        },
        {
            "channel_type": "whatsapp",
            "channel_name": "WhatsApp Business",
            "is_active": True,
            "configuration": {
                "phone_number": "+1-555-SUPPORT",
                "api_key": "wa_demo_key",
                "webhook_url": "https://api.example.com/webhook/whatsapp"
            },
            "bot_enabled": True,
            "auto_escalation_enabled": True,
            "escalation_threshold_minutes": 10
        }
    ]
    
    for channel_data in channels_data:
        channel = ChannelConfiguration(
            organization_id=org_id,
            created_by_id=user_id,
            **channel_data
        )
        db.add(channel)
    
    # Create Survey Templates
    survey_templates_data = [
        {
            "name": "Post-Service Satisfaction Survey",
            "description": "Standard satisfaction survey sent after service completion",
            "template_type": "service_satisfaction",
            "questions": [
                {
                    "id": "q1",
                    "type": "rating",
                    "question": "How satisfied were you with our service?",
                    "scale": 5,
                    "required": True
                },
                {
                    "id": "q2",
                    "type": "rating",
                    "question": "How likely are you to recommend us to a friend?",
                    "scale": 10,
                    "required": True
                },
                {
                    "id": "q3",
                    "type": "text",
                    "question": "What could we improve?",
                    "required": False
                }
            ],
            "is_active": True,
            "trigger_event": "service_completion",
            "trigger_delay_hours": 2
        },
        {
            "name": "Product Feedback Survey",
            "description": "Collect feedback on product quality and features",
            "template_type": "product_feedback",
            "questions": [
                {
                    "id": "q1",
                    "type": "rating",
                    "question": "How would you rate the product quality?",
                    "scale": 5,
                    "required": True
                },
                {
                    "id": "q2",
                    "type": "multiple_choice",
                    "question": "Which feature do you use most?",
                    "options": ["Reporting", "Analytics", "Automation", "Integration"],
                    "required": True
                },
                {
                    "id": "q3",
                    "type": "text",
                    "question": "What new features would you like to see?",
                    "required": False
                }
            ],
            "is_active": True,
            "trigger_event": "product_purchase",
            "trigger_delay_hours": 24
        }
    ]
    
    survey_templates = []
    for template_data in survey_templates_data:
        template = SurveyTemplate(
            organization_id=org_id,
            created_by_id=user_id,
            **template_data
        )
        survey_templates.append(template)
        db.add(template)
    
    db.flush()
    
    # Create Chatbot Conversations
    conversations_data = [
        {
            "conversation_id": "conv_2024_001",
            "session_id": "sess_abc123",
            "customer_name": "Alice Johnson",
            "customer_email": "alice.johnson@email.com",
            "channel": "web_chat",
            "status": "resolved",
            "intent": "product_inquiry",
            "confidence_score": 0.92,
            "escalated_to_human": False,
            "resolved_by_bot": True,
            "resolution_category": "product_information",
            "customer_satisfaction": 5,
            "started_at": datetime.utcnow() - timedelta(hours=2),
            "ended_at": datetime.utcnow() - timedelta(hours=1, minutes=45)
        },
        {
            "conversation_id": "conv_2024_002",
            "session_id": "sess_def456",
            "customer_name": "Bob Smith",
            "customer_email": "bob.smith@company.com",
            "channel": "whatsapp",
            "status": "escalated",
            "intent": "technical_support",
            "confidence_score": 0.85,
            "escalated_to_human": True,
            "escalated_at": datetime.utcnow() - timedelta(minutes=30),
            "assigned_agent_id": user_id,
            "escalation_reason": "Complex technical issue requiring specialist",
            "resolved_by_bot": False,
            "started_at": datetime.utcnow() - timedelta(hours=1),
            "last_message_at": datetime.utcnow() - timedelta(minutes=5)
        }
    ]
    
    for conv_data in conversations_data:
        conversation = ChatbotConversation(
            organization_id=org_id,
            **conv_data
        )
        db.add(conversation)
    
    # Create Customer Surveys
    if customers and survey_templates:
        for i, customer in enumerate(customers[:2]):
            survey = CustomerSurvey(
                organization_id=org_id,
                template_id=survey_templates[0].id,
                customer_id=customer.id,
                survey_token=f"survey_token_{i+1}",
                status="completed",
                customer_email=customer.email,
                customer_name=customer.name,
                sent_at=datetime.utcnow() - timedelta(days=5),
                started_at=datetime.utcnow() - timedelta(days=4),
                completed_at=datetime.utcnow() - timedelta(days=4),
                responses={
                    "q1": 5 if i == 0 else 4,
                    "q2": 9 if i == 0 else 8,
                    "q3": "Great service!" if i == 0 else "Could be faster"
                },
                overall_rating=5 if i == 0 else 4,
                nps_score=9 if i == 0 else 8,
                comments="Excellent experience overall" if i == 0 else "Good but room for improvement"
            )
            db.add(survey)
    
    print(f"✅ Created channel configurations, survey templates, chatbot conversations, and customer surveys")

async def main():
    """Main seeding function"""
    print("🌱 Starting CRM, Marketing, and Service Desk data seeding...")
    
    db = SessionLocal()
    try:
        # Get first organization and user (assuming they exist)
        org = db.query(Organization).first()
        user = db.query(User).first()
        customers = db.query(Customer).limit(5).all()
        
        if not org or not user:
            print("❌ No organization or user found. Please ensure basic data exists.")
            return
        
        print(f"📊 Using organization: {org.name} (ID: {org.id})")
        print(f"👤 Using user: {user.first_name} {user.last_name} (ID: {user.id})")
        print(f"👥 Found {len(customers)} customers for linking")
        
        # Seed all modules
        seed_crm_data(db, org.id, user.id, customers)
        seed_marketing_data(db, org.id, user.id, customers)
        # seed_service_desk_data(db, org.id, user.id, customers)  # Commented out to prevent seeding sample service desk data
        
        # Commit all changes
        db.commit()
        print("✅ All sample data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())