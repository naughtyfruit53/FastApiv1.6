"""
Chatbot API endpoints for natural language interaction
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from chatbot"""
    message: str
    actions: Optional[List[Dict[str, Any]]] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None


@router.post("/process", response_model=ChatResponse)
async def process_chat_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process a chat message using NLP/AI backend
    
    Currently uses rule-based processing. Can be enhanced with:
    - OpenAI API integration
    - Custom trained models
    - Intent classification
    - Entity extraction
    """
    try:
        message = chat_message.message.lower().strip()
        
        # Navigation intents
        if any(word in message for word in ['open', 'go to', 'navigate', 'show']):
            if 'vendor' in message:
                return ChatResponse(
                    message="I can take you to the Vendors page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Vendors',
                        'data': {'path': '/vendors'}
                    }],
                    intent='navigate_vendors',
                    confidence=0.9
                )
            elif 'customer' in message:
                return ChatResponse(
                    message="I can take you to the Customers page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Customers',
                        'data': {'path': '/customers'}
                    }],
                    intent='navigate_customers',
                    confidence=0.9
                )
            elif 'purchase order' in message or 'po' in message:
                return ChatResponse(
                    message="I can take you to the Purchase Orders page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Purchase Orders',
                        'data': {'path': '/vouchers/purchase-orders'}
                    }],
                    intent='navigate_purchase_orders',
                    confidence=0.9
                )
            elif 'product' in message or 'inventory' in message:
                return ChatResponse(
                    message="I can take you to the Products page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Products',
                        'data': {'path': '/products'}
                    }],
                    intent='navigate_products',
                    confidence=0.9
                )
        
        # Create/add intents
        if any(word in message for word in ['add', 'create', 'new']):
            if 'vendor' in message:
                return ChatResponse(
                    message="I can help you create a new vendor. Would you like to go to the vendor creation page?",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Create Vendor',
                        'data': {'path': '/vendors?action=create'}
                    }],
                    intent='create_vendor',
                    confidence=0.85
                )
            elif 'customer' in message:
                return ChatResponse(
                    message="I can help you create a new customer.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Create Customer',
                        'data': {'path': '/customers?action=create'}
                    }],
                    intent='create_customer',
                    confidence=0.85
                )
            elif 'product' in message:
                return ChatResponse(
                    message="I can help you create a new product.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Create Product',
                        'data': {'path': '/products?action=create'}
                    }],
                    intent='create_product',
                    confidence=0.85
                )
        
        # Low stock intent
        if 'low stock' in message or 'low-stock' in message or 'inventory alert' in message:
            return ChatResponse(
                message="I can show you items with low stock levels.",
                actions=[{
                    'type': 'navigate',
                    'label': 'View Low Stock Items',
                    'data': {'path': '/inventory?filter=low-stock'}
                }],
                intent='view_low_stock',
                confidence=0.95
            )
        
        # Reports intent
        if 'report' in message:
            return ChatResponse(
                message="I can help you with reports. What type of report would you like?",
                actions=[
                    {
                        'type': 'navigate',
                        'label': 'Sales Report',
                        'data': {'path': '/reports/sales'}
                    },
                    {
                        'type': 'navigate',
                        'label': 'Purchase Report',
                        'data': {'path': '/reports/purchase'}
                    },
                    {
                        'type': 'navigate',
                        'label': 'Inventory Report',
                        'data': {'path': '/reports/inventory'}
                    }
                ],
                intent='generate_report',
                confidence=0.8
            )
        
        # Default response
        return ChatResponse(
            message="I'm not sure I understand. Try asking me to:\n" +
                    "• Open a page (e.g., 'open vendors')\n" +
                    "• Add something (e.g., 'add new vendor')\n" +
                    "• View low stock items\n" +
                    "• Repeat a purchase order\n" +
                    "• Generate a report",
            intent='unknown',
            confidence=0.0
        )
        
    except Exception as e:
        logger.error(f"Chatbot processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/suggestions")
async def get_chat_suggestions(
    current_user: User = Depends(get_current_active_user)
):
    """Get chat suggestions based on context"""
    return {
        "suggestions": [
            "Show me low stock items",
            "Open purchase orders",
            "Create new vendor",
            "Generate sales report",
            "Go to customers page"
        ]
    }
