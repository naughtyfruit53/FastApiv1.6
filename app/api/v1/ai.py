"""
AI Agent API endpoints for chatbot operations and business intelligence
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.services.ai_service import AIService, IntentClassifier, BusinessAdvisor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class IntentClassificationRequest(BaseModel):
    """Request for intent classification"""
    message: str = Field(..., description="User message to classify")


class IntentClassificationResponse(BaseModel):
    """Response from intent classification"""
    intent: str
    confidence: float
    entities: Dict[str, Any]


class BusinessAdviceRequest(BaseModel):
    """Request for business advice"""
    category: str = Field(..., description="Advice category (inventory, cash_flow, sales, customer_retention)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class BusinessAdviceResponse(BaseModel):
    """Response with business advice"""
    category: str
    recommendations: List[Dict[str, Any]]


# ============================================================================
# INTENT CLASSIFICATION ENDPOINTS
# ============================================================================

@router.post("/intent/classify", response_model=IntentClassificationResponse)
async def classify_intent(
    request: IntentClassificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Classify user intent from a message
    
    Uses NLP-based intent classification to determine what the user wants to do
    """
    try:
        intent_classifier = IntentClassifier()
        
        # Classify intent
        intent, confidence = intent_classifier.classify_intent(request.message)
        
        # Extract entities
        entities = intent_classifier.extract_entities(request.message)
        
        return IntentClassificationResponse(
            intent=intent,
            confidence=confidence,
            entities=entities
        )
        
    except Exception as e:
        logger.error(f"Error classifying intent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to classify intent: {str(e)}"
        )


@router.get("/intent/patterns")
async def get_intent_patterns(
    current_user: User = Depends(get_current_active_user)
):
    """Get available intent patterns and their keywords"""
    return {
        "patterns": IntentClassifier.INTENT_PATTERNS
    }


# ============================================================================
# BUSINESS ADVICE ENDPOINTS
# ============================================================================

@router.post("/advice", response_model=BusinessAdviceResponse)
async def get_business_advice(
    request: BusinessAdviceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get business advice for a specific category
    
    Categories:
    - inventory: Inventory management advice
    - cash_flow: Cash flow management advice
    - sales: Sales growth strategies
    - customer_retention: Customer retention strategies
    """
    try:
        business_advisor = BusinessAdvisor(db)
        
        advice_methods = {
            'inventory': business_advisor.get_inventory_advice,
            'cash_flow': business_advisor.get_cash_flow_advice,
            'sales': business_advisor.get_sales_growth_advice,
            'customer_retention': business_advisor.get_customer_retention_advice
        }
        
        if request.category not in advice_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid advice category. Must be one of: {', '.join(advice_methods.keys())}"
            )
        
        advice = advice_methods[request.category](current_user.organization_id)
        
        return BusinessAdviceResponse(**advice)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business advice: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get business advice: {str(e)}"
        )


@router.get("/advice/categories")
async def get_advice_categories(
    current_user: User = Depends(get_current_active_user)
):
    """Get available business advice categories"""
    return {
        "categories": [
            {
                "id": "inventory",
                "name": "Inventory Management",
                "description": "Get advice on managing stock levels, reorder points, and inventory optimization"
            },
            {
                "id": "cash_flow",
                "name": "Cash Flow Management",
                "description": "Learn strategies for managing receivables, payables, and maintaining healthy cash flow"
            },
            {
                "id": "sales",
                "name": "Sales Growth",
                "description": "Discover strategies to increase revenue, convert leads, and grow your customer base"
            },
            {
                "id": "customer_retention",
                "name": "Customer Retention",
                "description": "Learn techniques to keep customers happy and reduce churn"
            }
        ]
    }


# ============================================================================
# NAVIGATION ASSISTANCE ENDPOINTS
# ============================================================================

@router.get("/navigation/suggestions")
async def get_navigation_suggestions(
    query: Optional[str] = Query(None, description="Search query for navigation"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get navigation suggestions based on query or user context
    
    Returns relevant pages and actions the user might want to navigate to
    """
    # Define navigation structure
    navigation_items = [
        {"path": "/dashboard", "label": "Dashboard", "category": "overview", "keywords": ["dashboard", "home", "overview"]},
        {"path": "/customers", "label": "Customers", "category": "crm", "keywords": ["customer", "client", "contact"]},
        {"path": "/vendors", "label": "Vendors", "category": "procurement", "keywords": ["vendor", "supplier"]},
        {"path": "/products", "label": "Products", "category": "inventory", "keywords": ["product", "item", "sku"]},
        {"path": "/inventory", "label": "Inventory", "category": "inventory", "keywords": ["inventory", "stock", "warehouse"]},
        {"path": "/crm", "label": "CRM", "category": "crm", "keywords": ["crm", "lead", "opportunity", "prospect"]},
        {"path": "/sales", "label": "Sales", "category": "sales", "keywords": ["sales", "order", "invoice"]},
        {"path": "/purchase", "label": "Purchase", "category": "procurement", "keywords": ["purchase", "procurement"]},
        {"path": "/analytics", "label": "Analytics", "category": "analytics", "keywords": ["analytics", "analysis", "insights"]},
        {"path": "/reports", "label": "Reports", "category": "reporting", "keywords": ["report", "statement", "summary"]},
        {"path": "/hr", "label": "Human Resources", "category": "hr", "keywords": ["hr", "employee", "payroll"]},
        {"path": "/finance", "label": "Finance", "category": "finance", "keywords": ["finance", "account", "ledger"]},
    ]
    
    if query:
        # Filter based on query
        query_lower = query.lower()
        relevant_items = [
            item for item in navigation_items
            if any(keyword in query_lower for keyword in item["keywords"])
            or query_lower in item["label"].lower()
        ]
        return {"suggestions": relevant_items[:10]}
    
    # Return most common navigation items
    return {"suggestions": navigation_items[:10]}


@router.get("/navigation/quickactions")
async def get_quick_actions(
    context: Optional[str] = Query(None, description="Current page context"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get contextual quick actions based on current page or context
    """
    quick_actions = [
        {
            "id": "create_customer",
            "label": "Create Customer",
            "icon": "person_add",
            "action": {"type": "navigate", "path": "/customers?action=create"}
        },
        {
            "id": "create_invoice",
            "label": "Create Invoice",
            "icon": "receipt",
            "action": {"type": "navigate", "path": "/vouchers/Sales-Vouchers/sales-voucher"}
        },
        {
            "id": "view_inventory",
            "label": "Check Inventory",
            "icon": "inventory",
            "action": {"type": "navigate", "path": "/inventory"}
        },
        {
            "id": "view_reports",
            "label": "View Reports",
            "icon": "analytics",
            "action": {"type": "navigate", "path": "/reports"}
        },
        {
            "id": "create_purchase_order",
            "label": "Create Purchase Order",
            "icon": "shopping_cart",
            "action": {"type": "navigate", "path": "/vouchers/Purchase-Vouchers/purchase-order"}
        }
    ]
    
    return {"quick_actions": quick_actions}


# ============================================================================
# AGENT TASK EXECUTION ENDPOINTS
# ============================================================================

@router.post("/agent/execute")
async def execute_agent_task(
    task: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute an AI agent task
    
    Tasks can include:
    - Data retrieval and analysis
    - Report generation
    - Workflow automation
    - Business intelligence queries
    """
    try:
        task_type = task.get("type")
        
        if task_type == "analyze_data":
            # Placeholder for data analysis
            return {
                "status": "completed",
                "result": {
                    "analysis": "Data analysis completed",
                    "insights": []
                }
            }
        
        elif task_type == "generate_report":
            # Placeholder for report generation
            return {
                "status": "completed",
                "result": {
                    "report_url": "/reports/generated/12345",
                    "format": "pdf"
                }
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task type: {task_type}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )


# ============================================================================
# SMART INSIGHTS ENDPOINTS
# ============================================================================

@router.get("/insights/smart")
async def get_smart_insights(
    category: Optional[str] = Query(None, description="Insight category filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get smart business insights powered by AI
    
    Returns actionable insights based on organization data
    """
    try:
        # Placeholder insights - would be generated from actual data analysis
        insights = [
            {
                "category": "inventory",
                "priority": "high",
                "title": "Low Stock Alert",
                "message": "5 items are below reorder level. Consider placing purchase orders.",
                "action": "view_low_stock",
                "action_label": "View Items",
                "generated_at": datetime.utcnow().isoformat()
            },
            {
                "category": "finance",
                "priority": "medium",
                "title": "Outstanding Receivables",
                "message": "₹2.5L in payments pending from customers for >30 days.",
                "action": "view_receivables",
                "action_label": "Send Reminders",
                "generated_at": datetime.utcnow().isoformat()
            },
            {
                "category": "sales",
                "priority": "low",
                "title": "Sales Opportunity",
                "message": "3 quotations are pending customer response. Follow up recommended.",
                "action": "view_quotations",
                "action_label": "View Quotations",
                "generated_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Filter by category if provided
        if category:
            insights = [i for i in insights if i["category"] == category]
        
        return {"insights": insights}
        
    except Exception as e:
        logger.error(f"Error getting smart insights: {str(e)}")
        return {"insights": []}


@router.get("/insights/recommendations")
async def get_recommendations(
    context: Optional[str] = Query(None, description="Context for recommendations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized recommendations for the user
    """
    recommendations = [
        "Consider offering early payment discounts to improve cash flow",
        "Set up automatic reorder alerts for critical inventory items",
        "Review and optimize your pricing based on current market trends",
        "Implement a customer loyalty program to increase retention",
        "Schedule regular follow-ups with prospects to improve conversion rates"
    ]
    
    return {"recommendations": recommendations}


# ============================================================================
# CHATBOT CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/chatbot/config")
async def get_chatbot_config(
    current_user: User = Depends(get_current_active_user)
):
    """Get chatbot configuration and capabilities"""
    return {
        "capabilities": [
            "intent_classification",
            "business_advice",
            "navigation_assistance",
            "voucher_creation_guidance",
            "lead_management",
            "tax_gst_queries",
            "inventory_queries",
            "payment_queries"
        ],
        "supported_languages": ["en"],
        "max_message_length": 1000,
        "session_timeout_minutes": 30,
        "features": {
            "context_awareness": True,
            "multi_turn_conversation": True,
            "quick_actions": True,
            "smart_suggestions": True
        }
    }


@router.get("/chatbot/health")
async def chatbot_health_check():
    """Check chatbot service health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
