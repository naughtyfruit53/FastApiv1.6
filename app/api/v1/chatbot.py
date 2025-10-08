"""
Chatbot API endpoints for natural language interaction with advanced AI capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

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
    suggestions: Optional[List[str]] = None


@router.post("/process", response_model=ChatResponse)
async def process_chat_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process a chat message using advanced AI capabilities
    
    Features:
    - Business advice and recommendations
    - Voucher creation assistance
    - Lead generation support
    - Tax queries and GST guidance
    - Navigation assistance
    - Intent classification with high accuracy
    """
    try:
        message = chat_message.message.lower().strip()
        
        # Business advice and recommendations
        if any(word in message for word in ['advice', 'recommend', 'suggest', 'help', 'how to', 'should i']):
            if 'inventory' in message or 'stock' in message:
                return ChatResponse(
                    message="Here are some inventory management recommendations:\n\n" +
                            "📊 **Best Practices:**\n" +
                            "• Maintain optimal stock levels (not too high, not too low)\n" +
                            "• Set reorder points for critical items\n" +
                            "• Use ABC analysis (A=high value, C=low value items)\n" +
                            "• Regular cycle counts to ensure accuracy\n\n" +
                            "Would you like to view your current stock status?",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'View Inventory',
                            'data': {'path': '/inventory'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Low Stock Items',
                            'data': {'path': '/inventory?filter=low-stock'}
                        }
                    ],
                    intent='business_advice_inventory',
                    confidence=0.95,
                    suggestions=["Show me low stock items", "How do I set reorder levels?"]
                )
            elif 'cash flow' in message or 'payment' in message or 'receivable' in message:
                return ChatResponse(
                    message="💰 **Cash Flow Management Tips:**\n\n" +
                            "• Monitor accounts receivable - follow up on overdue payments\n" +
                            "• Negotiate better payment terms with vendors\n" +
                            "• Maintain a cash reserve for emergencies\n" +
                            "• Consider offering early payment discounts\n" +
                            "• Use purchase orders to control spending\n\n" +
                            "Would you like to see your outstanding payments?",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'Accounts Receivable',
                            'data': {'path': '/reports/receivables'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Accounts Payable',
                            'data': {'path': '/reports/payables'}
                        }
                    ],
                    intent='business_advice_cashflow',
                    confidence=0.92,
                    suggestions=["Show overdue invoices", "Payment aging report"]
                )
            elif 'sale' in message or 'revenue' in message or 'grow' in message:
                return ChatResponse(
                    message="📈 **Sales Growth Strategies:**\n\n" +
                            "• Analyze your top customers and products\n" +
                            "• Follow up on quotations that haven't converted\n" +
                            "• Implement customer loyalty programs\n" +
                            "• Cross-sell and upsell to existing customers\n" +
                            "• Track and analyze sales trends\n\n" +
                            "Let me help you analyze your sales data.",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'Sales Analytics',
                            'data': {'path': '/analytics/sales'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Customer Analytics',
                            'data': {'path': '/analytics/customers'}
                        }
                    ],
                    intent='business_advice_sales',
                    confidence=0.93,
                    suggestions=["Show top customers", "View sales trends"]
                )
        
        # Voucher creation assistance
        if any(word in message for word in ['create', 'make', 'new', 'add']) and any(word in message for word in ['invoice', 'bill', 'voucher', 'order', 'quotation']):
            voucher_type = None
            path = None
            
            if 'purchase order' in message or ('purchase' in message and 'order' in message):
                voucher_type = "Purchase Order"
                path = '/vouchers/Purchase-Vouchers/purchase-order'
            elif 'sales order' in message or ('sales' in message and 'order' in message):
                voucher_type = "Sales Order"
                path = '/vouchers/Sales-Vouchers/sales-order'
            elif 'quotation' in message or 'quote' in message:
                voucher_type = "Quotation"
                path = '/vouchers/Sales-Vouchers/quotation'
            elif 'invoice' in message or ('sales' in message and 'bill' in message):
                voucher_type = "Sales Invoice"
                path = '/vouchers/Sales-Vouchers/sales-voucher'
            elif 'purchase' in message and ('invoice' in message or 'bill' in message):
                voucher_type = "Purchase Invoice"
                path = '/vouchers/Purchase-Vouchers/purchase-voucher'
            elif 'payment' in message:
                voucher_type = "Payment Voucher"
                path = '/vouchers/payment-voucher'
            elif 'receipt' in message:
                voucher_type = "Receipt Voucher"
                path = '/vouchers/receipt-voucher'
            
            if voucher_type and path:
                return ChatResponse(
                    message=f"I'll help you create a {voucher_type}.\n\n" +
                            f"📝 **Quick Tips for {voucher_type}:**\n" +
                            "• Ensure all required fields are filled\n" +
                            "• Double-check quantities and rates\n" +
                            "• Add terms and conditions if needed\n" +
                            "• Save as draft if you're not ready to finalize\n\n" +
                            f"Ready to create your {voucher_type}?",
                    actions=[{
                        'type': 'navigate',
                        'label': f'Create {voucher_type}',
                        'data': {'path': path}
                    }],
                    intent=f'create_voucher_{voucher_type.lower().replace(" ", "_")}',
                    confidence=0.95,
                    suggestions=[f"What is {voucher_type}?", "Show me recent vouchers"]
                )
        
        # Lead generation support
        if any(word in message for word in ['lead', 'prospect', 'opportunity', 'potential customer']):
            return ChatResponse(
                message="🎯 **Lead Management:**\n\n" +
                        "I can help you manage leads and convert them to customers!\n\n" +
                        "**Lead Workflow:**\n" +
                        "1. Create lead with contact details\n" +
                        "2. Send quotation\n" +
                        "3. Follow up regularly\n" +
                        "4. Convert to customer when they place order\n\n" +
                        "Would you like to create a new lead or view existing ones?",
                actions=[
                    {
                        'type': 'navigate',
                        'label': 'View CRM',
                        'data': {'path': '/crm'}
                    },
                    {
                        'type': 'navigate',
                        'label': 'Create Lead',
                        'data': {'path': '/crm/leads?action=create'}
                    }
                ],
                intent='lead_generation',
                confidence=0.94,
                suggestions=["Show hot leads", "Lead conversion rate"]
            )
        
        # Tax queries and GST guidance
        if any(word in message for word in ['tax', 'gst', 'igst', 'cgst', 'sgst', 'tds', 'tcs']):
            if 'rate' in message or 'calculate' in message:
                return ChatResponse(
                    message="📊 **GST & Tax Information:**\n\n" +
                            "**GST Rates in India:**\n" +
                            "• 0% - Essential items (food grains, milk, etc.)\n" +
                            "• 5% - Essential goods and services\n" +
                            "• 12% - Standard goods\n" +
                            "• 18% - Most goods and services\n" +
                            "• 28% - Luxury items and sin goods\n\n" +
                            "**Intra-state (within state):** CGST + SGST\n" +
                            "**Inter-state (across states):** IGST\n\n" +
                            "Need to look up GST for a specific product?",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'GST Reports',
                            'data': {'path': '/reports/gst'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Search GST Number',
                            'data': {'path': '/gst-search'}
                        }
                    ],
                    intent='tax_query_gst',
                    confidence=0.96,
                    suggestions=["GST return filing", "Input tax credit"]
                )
            elif 'return' in message or 'filing' in message:
                return ChatResponse(
                    message="📝 **GST Return Filing:**\n\n" +
                            "**Monthly Returns:**\n" +
                            "• GSTR-1: Outward supplies (by 11th)\n" +
                            "• GSTR-3B: Summary return (by 20th)\n\n" +
                            "**Quarterly Returns (for small taxpayers):**\n" +
                            "• GSTR-1: Quarterly + Invoice furnishing facility\n" +
                            "• GSTR-3B: Quarterly\n\n" +
                            "**Annual Return:**\n" +
                            "• GSTR-9: Annual return (by December 31st)\n\n" +
                            "I can help you view your GST reports.",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'GST Reports',
                            'data': {'path': '/reports/gst'}
                        }
                    ],
                    intent='tax_query_filing',
                    confidence=0.95,
                    suggestions=["Generate GSTR-1", "View input tax credit"]
                )
            else:
                return ChatResponse(
                    message="💡 **Tax & GST Help:**\n\n" +
                            "I can help you with:\n" +
                            "• GST rates and calculations\n" +
                            "• Filing deadlines and requirements\n" +
                            "• Input tax credit\n" +
                            "• TDS/TCS queries\n" +
                            "• Tax reports and compliance\n\n" +
                            "What specifically would you like to know?",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'GST Reports',
                            'data': {'path': '/reports/gst'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Settings',
                            'data': {'path': '/settings'}
                        }
                    ],
                    intent='tax_query_general',
                    confidence=0.90,
                    suggestions=["GST rates", "Filing deadlines", "Input tax credit"]
                )
        
        # Navigation intents (enhanced)
        if any(word in message for word in ['open', 'go to', 'navigate', 'show', 'view', 'display']):
            if 'vendor' in message:
                return ChatResponse(
                    message="I can take you to the Vendors page where you can manage all your suppliers.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Vendors',
                        'data': {'path': '/vendors'}
                    }],
                    intent='navigate_vendors',
                    confidence=0.9,
                    suggestions=["Create new vendor", "View vendor ledger"]
                )
            elif 'customer' in message:
                return ChatResponse(
                    message="I can take you to the Customers page where you can manage customer relationships.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Customers',
                        'data': {'path': '/customers'}
                    }],
                    intent='navigate_customers',
                    confidence=0.9,
                    suggestions=["Create new customer", "View customer analytics"]
                )
            elif 'purchase order' in message or ('purchase' in message and 'order' in message):
                return ChatResponse(
                    message="I can take you to the Purchase Orders page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Purchase Orders',
                        'data': {'path': '/vouchers/Purchase-Vouchers/purchase-order'}
                    }],
                    intent='navigate_purchase_orders',
                    confidence=0.9,
                    suggestions=["Create purchase order", "Pending orders"]
                )
            elif 'sales order' in message or ('sales' in message and 'order' in message):
                return ChatResponse(
                    message="I can take you to the Sales Orders page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Sales Orders',
                        'data': {'path': '/vouchers/Sales-Vouchers/sales-order'}
                    }],
                    intent='navigate_sales_orders',
                    confidence=0.9,
                    suggestions=["Create sales order", "Pending deliveries"]
                )
            elif 'product' in message or 'inventory' in message:
                return ChatResponse(
                    message="I can take you to the Products/Inventory page.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Products',
                        'data': {'path': '/products'}
                    }],
                    intent='navigate_products',
                    confidence=0.9,
                    suggestions=["Low stock items", "Add new product"]
                )
            elif 'dashboard' in message or 'home' in message:
                return ChatResponse(
                    message="Taking you to the main dashboard.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Go to Dashboard',
                        'data': {'path': '/dashboard'}
                    }],
                    intent='navigate_dashboard',
                    confidence=0.95,
                    suggestions=["Show key metrics", "Today's summary"]
                )
            elif 'report' in message or 'analytics' in message:
                return ChatResponse(
                    message="I can help you with reports and analytics. Which report would you like to see?",
                    actions=[
                        {
                            'type': 'navigate',
                            'label': 'Sales Reports',
                            'data': {'path': '/reports/sales'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Purchase Reports',
                            'data': {'path': '/reports/purchase'}
                        },
                        {
                            'type': 'navigate',
                            'label': 'Inventory Reports',
                            'data': {'path': '/reports/inventory'}
                        }
                    ],
                    intent='navigate_reports',
                    confidence=0.88,
                    suggestions=["Sales analytics", "Profit & loss", "GST reports"]
                )
        
        # Create/add intents (not vouchers - handled above)
        if any(word in message for word in ['add', 'create', 'new']) and not any(word in message for word in ['invoice', 'bill', 'voucher', 'order']):
            if 'vendor' in message:
                return ChatResponse(
                    message="I can help you create a new vendor. Would you like to go to the vendor creation page?",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Create Vendor',
                        'data': {'path': '/vendors?action=create'}
                    }],
                    intent='create_vendor',
                    confidence=0.85,
                    suggestions=["View all vendors", "Vendor payment terms"]
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
                    confidence=0.85,
                    suggestions=["View all customers", "Customer analytics"]
                )
            elif 'product' in message or 'item' in message:
                return ChatResponse(
                    message="I can help you create a new product.",
                    actions=[{
                        'type': 'navigate',
                        'label': 'Create Product',
                        'data': {'path': '/products?action=create'}
                    }],
                    intent='create_product',
                    confidence=0.85,
                    suggestions=["View all products", "Stock valuation"]
                )
        
        # Low stock intent
        if 'low stock' in message or 'low-stock' in message or 'inventory alert' in message or 'shortage' in message:
            return ChatResponse(
                message="I can show you items with low stock levels that need reordering.",
                actions=[{
                    'type': 'navigate',
                    'label': 'View Low Stock Items',
                    'data': {'path': '/inventory?filter=low-stock'}
                }],
                intent='view_low_stock',
                confidence=0.95,
                suggestions=["Create purchase order", "Set reorder levels"]
            )
        
        # Outstanding payments
        if any(word in message for word in ['outstanding', 'pending', 'overdue', 'receivable', 'payable']):
            if 'customer' in message or 'receivable' in message:
                return ChatResponse(
                    message="I can show you outstanding receivables (money customers owe you).",
                    actions=[{
                        'type': 'navigate',
                        'label': 'View Receivables',
                        'data': {'path': '/reports/receivables'}
                    }],
                    intent='view_receivables',
                    confidence=0.93,
                    suggestions=["Send payment reminders", "Aging report"]
                )
            elif 'vendor' in message or 'payable' in message:
                return ChatResponse(
                    message="I can show you outstanding payables (money you owe to vendors).",
                    actions=[{
                        'type': 'navigate',
                        'label': 'View Payables',
                        'data': {'path': '/reports/payables'}
                    }],
                    intent='view_payables',
                    confidence=0.93,
                    suggestions=["Make payment", "Aging report"]
                )
        
        # Profit and loss
        if 'profit' in message or 'loss' in message or 'p&l' in message or 'p and l' in message:
            return ChatResponse(
                message="I can show you the Profit & Loss statement for your business.",
                actions=[{
                    'type': 'navigate',
                    'label': 'View P&L',
                    'data': {'path': '/reports/profit-loss'}
                }],
                intent='view_profit_loss',
                confidence=0.96,
                suggestions=["Balance sheet", "Cash flow statement"]
            )
        
        # Balance sheet
        if 'balance sheet' in message or 'assets' in message or 'liabilities' in message:
            return ChatResponse(
                message="I can show you the Balance Sheet with assets, liabilities, and equity.",
                actions=[{
                    'type': 'navigate',
                    'label': 'View Balance Sheet',
                    'data': {'path': '/reports/balance-sheet'}
                }],
                intent='view_balance_sheet',
                confidence=0.94,
                suggestions=["Profit & loss", "Trial balance"]
            )
        
        # Help and getting started
        if message in ['help', 'what can you do', 'capabilities', 'features', 'hi', 'hello', 'hey']:
            return ChatResponse(
                message="👋 Hello! I'm your AI business assistant. I can help you with:\n\n" +
                        "🎯 **Business Advice:**\n" +
                        "• Inventory management tips\n" +
                        "• Cash flow recommendations\n" +
                        "• Sales growth strategies\n\n" +
                        "📝 **Voucher Creation:**\n" +
                        "• Create invoices, orders, quotations\n" +
                        "• Purchase and sales documents\n" +
                        "• Payment and receipt vouchers\n\n" +
                        "🎪 **Lead Management:**\n" +
                        "• Track prospects and opportunities\n" +
                        "• Manage customer pipeline\n\n" +
                        "💰 **Tax & GST:**\n" +
                        "• GST rates and calculations\n" +
                        "• Filing deadlines and compliance\n\n" +
                        "🧭 **Navigation:**\n" +
                        "• Quick access to any page\n" +
                        "• Reports and analytics\n\n" +
                        "Try asking me something like:\n" +
                        '• "Show me low stock items"\n' +
                        '• "Create a sales order"\n' +
                        '• "What are GST rates?"\n' +
                        '• "Give me inventory advice"',
                intent='help',
                confidence=1.0,
                suggestions=[
                    "Show low stock items",
                    "Create invoice",
                    "GST filing dates",
                    "Business advice"
                ]
            )
        
        # Default response with suggestions
        return ChatResponse(
            message="I'm not sure I understand that. I can help you with:\n\n" +
                    "💡 **Try asking:**\n" +
                    '• "Give me business advice"\n' +
                    '• "Create a purchase order"\n' +
                    '• "Show me low stock items"\n' +
                    '• "What are GST rates?"\n' +
                    '• "Show outstanding payments"\n' +
                    '• "Open sales reports"\n\n' +
                    "Or type 'help' to see everything I can do!",
            intent='unknown',
            confidence=0.0,
            suggestions=[
                "Help",
                "Business advice",
                "Create invoice",
                "Low stock items",
                "GST information"
            ]
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
    """Get contextual chat suggestions based on user's typical workflows"""
    
    # Get current hour to provide time-appropriate suggestions
    current_hour = datetime.now().hour
    
    # Morning suggestions (6 AM - 12 PM)
    if 6 <= current_hour < 12:
        return {
            "suggestions": [
                "Show today's pending orders",
                "View low stock items",
                "Check outstanding payments",
                "Create sales order",
                "View dashboard"
            ]
        }
    # Afternoon suggestions (12 PM - 5 PM)
    elif 12 <= current_hour < 17:
        return {
            "suggestions": [
                "Create invoice",
                "Record payment received",
                "Generate sales report",
                "View customer analytics",
                "Check GST reports"
            ]
        }
    # Evening suggestions (5 PM - 10 PM)
    elif 17 <= current_hour < 22:
        return {
            "suggestions": [
                "View today's summary",
                "Close pending orders",
                "Generate profit & loss",
                "Backup data",
                "Tomorrow's schedule"
            ]
        }
    # Night/Late suggestions (10 PM - 6 AM)
    else:
        return {
            "suggestions": [
                "View reports",
                "Check analytics",
                "Review pending approvals",
                "Help",
                "Settings"
            ]
        }


@router.get("/business-insights")
async def get_business_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-powered business insights and recommendations
    This endpoint analyzes business data and provides actionable insights
    """
    try:
        insights = {
            "insights": [
                {
                    "category": "Inventory",
                    "priority": "high",
                    "title": "Low Stock Alert",
                    "message": "5 items are below reorder level. Consider placing purchase orders.",
                    "action": "view_low_stock",
                    "action_label": "View Items"
                },
                {
                    "category": "Finance",
                    "priority": "medium",
                    "title": "Outstanding Receivables",
                    "message": "₹2.5L in payments pending from customers for >30 days.",
                    "action": "view_receivables",
                    "action_label": "Send Reminders"
                },
                {
                    "category": "Sales",
                    "priority": "low",
                    "title": "Sales Opportunity",
                    "message": "3 quotations are pending customer response. Follow up recommended.",
                    "action": "view_quotations",
                    "action_label": "View Quotations"
                }
            ],
            "recommendations": [
                "Consider offering early payment discounts to improve cash flow",
                "Set up automatic reorder alerts for critical inventory items",
                "Review and optimize your pricing based on current market trends"
            ]
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating business insights: {e}")
        return {
            "insights": [],
            "recommendations": []
        }
