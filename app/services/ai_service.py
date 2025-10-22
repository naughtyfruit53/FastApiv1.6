"""
AI Service for NLP, Chatbot, Intent Classification, and Business Advice
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Intent classification for chatbot messages"""
    
    # Define intent patterns with keywords and weights
    INTENT_PATTERNS = {
        'business_advice': {
            'keywords': ['advice', 'recommend', 'suggest', 'help', 'how to', 'should i', 'best practice', 'tip'],
            'weight': 0.9
        },
        'create_voucher': {
            'keywords': ['create', 'make', 'new', 'add', 'generate', 'invoice', 'bill', 'voucher', 'order', 'quotation'],
            'weight': 0.95
        },
        'navigate': {
            'keywords': ['open', 'go to', 'navigate', 'show', 'view', 'display', 'take me'],
            'weight': 0.85
        },
        'query_info': {
            'keywords': ['what', 'when', 'where', 'who', 'how', 'why', 'tell me', 'show me'],
            'weight': 0.75
        },
        'tax_gst': {
            'keywords': ['tax', 'gst', 'igst', 'cgst', 'sgst', 'tds', 'tcs', 'filing', 'return'],
            'weight': 0.9
        },
        'lead_management': {
            'keywords': ['lead', 'prospect', 'opportunity', 'potential customer', 'convert'],
            'weight': 0.85
        },
        'report_analytics': {
            'keywords': ['report', 'analytics', 'analysis', 'dashboard', 'metrics', 'kpi', 'performance'],
            'weight': 0.8
        },
        'inventory_stock': {
            'keywords': ['inventory', 'stock', 'low stock', 'shortage', 'reorder', 'warehouse'],
            'weight': 0.85
        },
        'payment_finance': {
            'keywords': ['payment', 'receivable', 'payable', 'outstanding', 'pending', 'overdue', 'cash flow'],
            'weight': 0.85
        },
        'greeting': {
            'keywords': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'help'],
            'weight': 0.7
        }
    }
    
    @classmethod
    def classify_intent(cls, message: str) -> Tuple[str, float]:
        """
        Classify user intent from message
        
        Args:
            message: User input message
            
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        message = message.lower().strip()
        
        # Special case for exact greeting matches
        if message in ['hi', 'hello', 'hey', 'help']:
            return ('greeting', 1.0)
        
        # Calculate scores for each intent
        intent_scores = {}
        
        for intent, config in cls.INTENT_PATTERNS.items():
            score = 0.0
            keyword_matches = 0
            
            for keyword in config['keywords']:
                if keyword in message:
                    keyword_matches += 1
                    # Weight longer keywords higher
                    score += config['weight'] * (len(keyword.split()) / 2.0)
            
            if keyword_matches > 0:
                # Normalize by number of keywords
                intent_scores[intent] = min(score / keyword_matches, 1.0)
        
        if not intent_scores:
            return ('unknown', 0.0)
        
        # Return intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent
    
    @classmethod
    def extract_entities(cls, message: str) -> Dict[str, Any]:
        """
        Extract entities from message (voucher types, amounts, dates, etc.)
        
        Args:
            message: User input message
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        message_lower = message.lower()
        
        # Extract voucher types
        voucher_types = {
            'purchase order': 'purchase_order',
            'sales order': 'sales_order',
            'quotation': 'quotation',
            'invoice': 'invoice',
            'payment': 'payment',
            'receipt': 'receipt',
            'delivery challan': 'delivery_challan'
        }
        
        for voucher_phrase, voucher_type in voucher_types.items():
            if voucher_phrase in message_lower:
                entities['voucher_type'] = voucher_type
                break
        
        # Extract module references
        modules = ['sales', 'purchase', 'inventory', 'crm', 'hr', 'finance', 'manufacturing']
        for module in modules:
            if module in message_lower:
                entities['module'] = module
        
        # Extract action types
        if any(word in message_lower for word in ['create', 'new', 'add', 'make']):
            entities['action'] = 'create'
        elif any(word in message_lower for word in ['view', 'show', 'display', 'list']):
            entities['action'] = 'view'
        elif any(word in message_lower for word in ['update', 'edit', 'modify']):
            entities['action'] = 'update'
        
        return entities


class BusinessAdvisor:
    """Business advice and recommendation generation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_inventory_advice(self, organization_id: int) -> Dict[str, Any]:
        """Generate inventory management advice"""
        advice = {
            'category': 'inventory',
            'recommendations': [
                {
                    'title': 'Maintain Optimal Stock Levels',
                    'description': 'Keep inventory balanced - not too high (tying up capital) and not too low (risking stockouts)',
                    'priority': 'high',
                    'actionable_steps': [
                        'Review current stock levels monthly',
                        'Analyze fast-moving vs slow-moving items',
                        'Set min/max stock levels for each item'
                    ]
                },
                {
                    'title': 'Implement ABC Analysis',
                    'description': 'Categorize inventory based on value and turnover',
                    'priority': 'medium',
                    'actionable_steps': [
                        'A items: High value, tight control (20% items, 80% value)',
                        'B items: Moderate value, moderate control',
                        'C items: Low value, simple controls (80% items, 20% value)'
                    ]
                },
                {
                    'title': 'Set Reorder Points',
                    'description': 'Automate reordering to prevent stockouts',
                    'priority': 'high',
                    'actionable_steps': [
                        'Calculate lead time for each supplier',
                        'Set reorder point = (average daily usage × lead time) + safety stock',
                        'Enable automatic purchase order generation'
                    ]
                },
                {
                    'title': 'Regular Cycle Counts',
                    'description': 'Ensure inventory accuracy through regular counting',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Schedule daily counts for A items',
                        'Weekly counts for B items',
                        'Monthly counts for C items'
                    ]
                }
            ]
        }
        
        return advice
    
    def get_cash_flow_advice(self, organization_id: int) -> Dict[str, Any]:
        """Generate cash flow management advice"""
        advice = {
            'category': 'cash_flow',
            'recommendations': [
                {
                    'title': 'Monitor Accounts Receivable',
                    'description': 'Stay on top of customer payments to maintain healthy cash flow',
                    'priority': 'high',
                    'actionable_steps': [
                        'Send invoices immediately after delivery',
                        'Follow up on payments 3 days before due date',
                        'Implement late payment penalties',
                        'Offer early payment discounts (2/10 net 30)'
                    ]
                },
                {
                    'title': 'Negotiate Payment Terms',
                    'description': 'Optimize payment terms with suppliers',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Request longer payment terms from suppliers',
                        'Maintain good relationships for better terms',
                        'Consider bulk discounts for early payment'
                    ]
                },
                {
                    'title': 'Maintain Cash Reserve',
                    'description': 'Keep emergency funds for unexpected situations',
                    'priority': 'high',
                    'actionable_steps': [
                        'Target 3-6 months of operating expenses',
                        'Set up automatic transfers to savings',
                        'Review and adjust reserve quarterly'
                    ]
                },
                {
                    'title': 'Use Purchase Orders',
                    'description': 'Control spending and improve budgeting',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Require PO approval for all purchases',
                        'Track commitments against budget',
                        'Review PO aging regularly'
                    ]
                }
            ]
        }
        
        return advice
    
    def get_sales_growth_advice(self, organization_id: int) -> Dict[str, Any]:
        """Generate sales growth strategies"""
        advice = {
            'category': 'sales',
            'recommendations': [
                {
                    'title': 'Analyze Top Performers',
                    'description': 'Understand what drives your best results',
                    'priority': 'high',
                    'actionable_steps': [
                        'Identify top 20% of customers contributing 80% revenue',
                        'Analyze top-selling products and their margins',
                        'Study successful sales patterns and replicate'
                    ]
                },
                {
                    'title': 'Follow Up on Quotations',
                    'description': 'Convert pending quotations to orders',
                    'priority': 'high',
                    'actionable_steps': [
                        'Call prospects within 2 days of quote',
                        'Address objections and concerns',
                        'Offer limited-time incentives',
                        'Track conversion rates by product/customer'
                    ]
                },
                {
                    'title': 'Implement Loyalty Programs',
                    'description': 'Reward and retain existing customers',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Create tiered loyalty program',
                        'Offer exclusive benefits to top customers',
                        'Provide referral bonuses',
                        'Celebrate customer anniversaries'
                    ]
                },
                {
                    'title': 'Cross-sell and Upsell',
                    'description': 'Increase revenue from existing customers',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Identify complementary products',
                        'Train sales team on upselling techniques',
                        'Create product bundles',
                        'Track and reward successful cross-sells'
                    ]
                }
            ]
        }
        
        return advice
    
    def get_customer_retention_advice(self, organization_id: int) -> Dict[str, Any]:
        """Generate customer retention strategies"""
        advice = {
            'category': 'customer_retention',
            'recommendations': [
                {
                    'title': 'Regular Communication',
                    'description': 'Stay connected with customers consistently',
                    'priority': 'high',
                    'actionable_steps': [
                        'Send monthly newsletters with value',
                        'Quarterly business review calls',
                        'Birthday and anniversary wishes',
                        'Product update notifications'
                    ]
                },
                {
                    'title': 'Collect and Act on Feedback',
                    'description': 'Show customers you value their input',
                    'priority': 'high',
                    'actionable_steps': [
                        'Send satisfaction surveys after transactions',
                        'Implement Net Promoter Score (NPS) tracking',
                        'Act quickly on negative feedback',
                        'Share improvements based on feedback'
                    ]
                },
                {
                    'title': 'Proactive Support',
                    'description': 'Solve problems before they escalate',
                    'priority': 'medium',
                    'actionable_steps': [
                        'Monitor customer health scores',
                        'Reach out if usage drops',
                        'Provide educational resources',
                        'Assign dedicated account managers'
                    ]
                }
            ]
        }
        
        return advice


class AIService:
    """Main AI service coordinating NLP, chatbot, and business intelligence"""
    
    def __init__(self, db: Session):
        self.db = db
        self.intent_classifier = IntentClassifier()
        self.business_advisor = BusinessAdvisor(db)
    
    def process_chat_message(
        self, 
        message: str, 
        organization_id: int,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process chat message and generate intelligent response
        
        Args:
            message: User's chat message
            organization_id: Organization ID
            user_id: User ID (optional)
            context: Additional context (optional)
            
        Returns:
            Dictionary with response, intent, actions, and suggestions
        """
        try:
            # Classify intent
            intent, confidence = self.intent_classifier.classify_intent(message)
            
            # Extract entities
            entities = self.intent_classifier.extract_entities(message)
            
            # Generate response based on intent
            response = self._generate_response(
                intent=intent,
                confidence=confidence,
                entities=entities,
                message=message,
                organization_id=organization_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                'message': 'I encountered an error processing your request. Please try again.',
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _generate_response(
        self,
        intent: str,
        confidence: float,
        entities: Dict[str, Any],
        message: str,
        organization_id: int
    ) -> Dict[str, Any]:
        """Generate response based on classified intent"""
        
        if intent == 'business_advice':
            return self._handle_business_advice(entities, organization_id)
        elif intent == 'create_voucher':
            return self._handle_voucher_creation(entities)
        elif intent == 'navigate':
            return self._handle_navigation(entities, message)
        elif intent == 'tax_gst':
            return self._handle_tax_query(entities, message)
        elif intent == 'lead_management':
            return self._handle_lead_query(entities)
        elif intent == 'inventory_stock':
            return self._handle_inventory_query(entities, organization_id)
        elif intent == 'payment_finance':
            return self._handle_payment_query(entities, organization_id)
        elif intent == 'greeting':
            return self._handle_greeting()
        else:
            return self._handle_unknown_intent()
    
    def _handle_business_advice(self, entities: Dict[str, Any], organization_id: int) -> Dict[str, Any]:
        """Handle business advice requests"""
        
        module = entities.get('module', 'general')
        
        if 'inventory' in module or 'stock' in module:
            advice = self.business_advisor.get_inventory_advice(organization_id)
            return {
                'message': '📊 **Inventory Management Best Practices:**\n\n' +
                          '\n\n'.join([
                              f"**{rec['title']}**\n{rec['description']}\n" +
                              '\n'.join([f"• {step}" for step in rec['actionable_steps']])
                              for rec in advice['recommendations'][:2]
                          ]),
                'intent': 'business_advice_inventory',
                'confidence': 0.95,
                'actions': [
                    {'type': 'navigate', 'label': 'View Inventory', 'data': {'path': '/inventory'}},
                    {'type': 'navigate', 'label': 'Low Stock Items', 'data': {'path': '/inventory?filter=low-stock'}}
                ],
                'suggestions': ['Show me low stock items', 'How do I set reorder levels?']
            }
        
        elif any(word in module for word in ['cash', 'payment', 'finance']):
            advice = self.business_advisor.get_cash_flow_advice(organization_id)
            return {
                'message': '💰 **Cash Flow Management Tips:**\n\n' +
                          '\n\n'.join([
                              f"**{rec['title']}**\n{rec['description']}\n" +
                              '\n'.join([f"• {step}" for step in rec['actionable_steps']])
                              for rec in advice['recommendations'][:2]
                          ]),
                'intent': 'business_advice_cashflow',
                'confidence': 0.92,
                'actions': [
                    {'type': 'navigate', 'label': 'Accounts Receivable', 'data': {'path': '/reports/receivables'}},
                    {'type': 'navigate', 'label': 'Accounts Payable', 'data': {'path': '/reports/payables'}}
                ],
                'suggestions': ['Show overdue invoices', 'Payment aging report']
            }
        
        elif 'sales' in module:
            advice = self.business_advisor.get_sales_growth_advice(organization_id)
            return {
                'message': '📈 **Sales Growth Strategies:**\n\n' +
                          '\n\n'.join([
                              f"**{rec['title']}**\n{rec['description']}\n" +
                              '\n'.join([f"• {step}" for step in rec['actionable_steps']])
                              for rec in advice['recommendations'][:2]
                          ]),
                'intent': 'business_advice_sales',
                'confidence': 0.93,
                'actions': [
                    {'type': 'navigate', 'label': 'Sales Analytics', 'data': {'path': '/analytics/sales'}},
                    {'type': 'navigate', 'label': 'Customer Analytics', 'data': {'path': '/analytics/customers'}}
                ],
                'suggestions': ['Show top customers', 'View sales trends']
            }
        
        else:
            # General business advice
            return {
                'message': '💡 **General Business Advice:**\n\n' +
                          '**Focus Areas for Growth:**\n' +
                          '• **Revenue:** Increase sales through customer retention and acquisition\n' +
                          '• **Profitability:** Optimize costs and improve margins\n' +
                          '• **Cash Flow:** Manage receivables and payables effectively\n' +
                          '• **Efficiency:** Automate processes and reduce waste\n\n' +
                          'What specific area would you like advice on?',
                'intent': 'business_advice_general',
                'confidence': 0.85,
                'actions': [
                    {'type': 'navigate', 'label': 'Dashboard', 'data': {'path': '/dashboard'}},
                    {'type': 'navigate', 'label': 'Analytics', 'data': {'path': '/analytics'}}
                ],
                'suggestions': ['Inventory advice', 'Sales strategies', 'Cash flow tips']
            }
    
    def _handle_voucher_creation(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voucher creation requests"""
        
        voucher_type = entities.get('voucher_type')
        
        voucher_routes = {
            'purchase_order': ('/vouchers/Purchase-Vouchers/purchase-order', 'Purchase Order'),
            'sales_order': ('/vouchers/Sales-Vouchers/sales-order', 'Sales Order'),
            'quotation': ('/vouchers/Pre-Sales-Voucher/quotation', 'Quotation'),
            'invoice': ('/vouchers/Sales-Vouchers/sales-voucher', 'Sales Invoice'),
            'payment': ('/vouchers/Financial-Vouchers/payment-voucher', 'Payment Voucher'),
            'receipt': ('/vouchers/Financial-Vouchers/receipt-voucher', 'Receipt Voucher')
        }
        
        if voucher_type and voucher_type in voucher_routes:
            path, name = voucher_routes[voucher_type]
            return {
                'message': f"I'll help you create a {name}.\n\n" +
                          f"📝 **Quick Tips for {name}:**\n" +
                          '• Ensure all required fields are filled\n' +
                          '• Double-check quantities and rates\n' +
                          '• Add terms and conditions if needed\n' +
                          '• Save as draft if you\'re not ready to finalize',
                'intent': f'create_voucher_{voucher_type}',
                'confidence': 0.95,
                'actions': [
                    {'type': 'navigate', 'label': f'Create {name}', 'data': {'path': path}}
                ],
                'suggestions': [f'What is {name}?', 'Show me recent vouchers']
            }
        
        # Generic voucher creation response
        return {
            'message': '📝 **Create Voucher:**\n\n' +
                      'Which type of voucher would you like to create?\n\n' +
                      '**Sales:**\n• Quotation\n• Sales Order\n• Sales Invoice\n\n' +
                      '**Purchase:**\n• Purchase Order\n• Purchase Invoice\n\n' +
                      '**Financial:**\n• Payment Voucher\n• Receipt Voucher',
            'intent': 'create_voucher_general',
            'confidence': 0.85,
            'actions': [
                {'type': 'navigate', 'label': 'Sales Vouchers', 'data': {'path': '/vouchers/Sales-Vouchers'}},
                {'type': 'navigate', 'label': 'Purchase Vouchers', 'data': {'path': '/vouchers/Purchase-Vouchers'}}
            ],
            'suggestions': ['Create sales order', 'Create purchase order', 'Create invoice']
        }
    
    def _handle_navigation(self, entities: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle navigation requests"""
        
        # Navigation mapping
        nav_map = {
            'dashboard': '/dashboard',
            'customer': '/customers',
            'vendor': '/vendors',
            'product': '/products',
            'inventory': '/inventory',
            'sales': '/sales',
            'purchase': '/purchase',
            'crm': '/crm',
            'hr': '/hr',
            'analytics': '/analytics',
            'report': '/reports'
        }
        
        message_lower = message.lower()
        
        for keyword, path in nav_map.items():
            if keyword in message_lower:
                return {
                    'message': f"I can take you to the {keyword.title()} page.",
                    'intent': f'navigate_{keyword}',
                    'confidence': 0.9,
                    'actions': [
                        {'type': 'navigate', 'label': f'Go to {keyword.title()}', 'data': {'path': path}}
                    ],
                    'suggestions': [f'Show {keyword} analytics', f'Create new {keyword}']
                }
        
        return {
            'message': 'Where would you like to go? I can help you navigate to:\n\n' +
                      '• Dashboard\n• Customers/Vendors\n• Products/Inventory\n' +
                      '• Sales/Purchase\n• CRM\n• Reports & Analytics',
            'intent': 'navigate_general',
            'confidence': 0.75,
            'actions': [
                {'type': 'navigate', 'label': 'Dashboard', 'data': {'path': '/dashboard'}}
            ],
            'suggestions': ['Show dashboard', 'Go to customers', 'Open reports']
        }
    
    def _handle_tax_query(self, entities: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle tax and GST queries"""
        return {
            'message': '📊 **GST & Tax Information:**\n\n' +
                      '**GST Rates in India:**\n' +
                      '• 0% - Essential items (food grains, milk, etc.)\n' +
                      '• 5% - Essential goods and services\n' +
                      '• 12% - Standard goods\n' +
                      '• 18% - Most goods and services\n' +
                      '• 28% - Luxury items\n\n' +
                      '**Types:**\n' +
                      '• Intra-state: CGST + SGST\n' +
                      '• Inter-state: IGST',
            'intent': 'tax_query_gst',
            'confidence': 0.96,
            'actions': [
                {'type': 'navigate', 'label': 'GST Reports', 'data': {'path': '/reports/gst'}}
            ],
            'suggestions': ['GST return filing', 'Input tax credit', 'Filing deadlines']
        }
    
    def _handle_lead_query(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lead management queries"""
        return {
            'message': '🎯 **Lead Management:**\n\n' +
                      'I can help you manage leads and convert them to customers!\n\n' +
                      '**Lead Workflow:**\n' +
                      '1. Create lead with contact details\n' +
                      '2. Send quotation\n' +
                      '3. Follow up regularly\n' +
                      '4. Convert to customer when they place order',
            'intent': 'lead_generation',
            'confidence': 0.94,
            'actions': [
                {'type': 'navigate', 'label': 'View CRM', 'data': {'path': '/crm'}},
                {'type': 'navigate', 'label': 'Create Lead', 'data': {'path': '/crm/leads?action=create'}}
            ],
            'suggestions': ['Show hot leads', 'Lead conversion rate', 'Create new lead']
        }
    
    def _handle_inventory_query(self, entities: Dict[str, Any], organization_id: int) -> Dict[str, Any]:
        """Handle inventory queries"""
        return {
            'message': '📦 **Inventory Management:**\n\n' +
                      'I can help you with:\n' +
                      '• Low stock items\n' +
                      '• Stock valuation\n' +
                      '• Warehouse management\n' +
                      '• Inventory reports\n\n' +
                      'What would you like to check?',
            'intent': 'inventory_query',
            'confidence': 0.9,
            'actions': [
                {'type': 'navigate', 'label': 'View Inventory', 'data': {'path': '/inventory'}},
                {'type': 'navigate', 'label': 'Low Stock Items', 'data': {'path': '/inventory?filter=low-stock'}}
            ],
            'suggestions': ['Show low stock', 'Stock valuation', 'Warehouse status']
        }
    
    def _handle_payment_query(self, entities: Dict[str, Any], organization_id: int) -> Dict[str, Any]:
        """Handle payment and finance queries"""
        return {
            'message': '💰 **Payment & Finance:**\n\n' +
                      'I can show you:\n' +
                      '• Outstanding receivables\n' +
                      '• Accounts payable\n' +
                      '• Payment aging\n' +
                      '• Cash flow summary',
            'intent': 'payment_query',
            'confidence': 0.9,
            'actions': [
                {'type': 'navigate', 'label': 'Receivables', 'data': {'path': '/reports/receivables'}},
                {'type': 'navigate', 'label': 'Payables', 'data': {'path': '/reports/payables'}}
            ],
            'suggestions': ['Show overdue payments', 'Aging report', 'Cash flow']
        }
    
    def _handle_greeting(self) -> Dict[str, Any]:
        """Handle greeting messages"""
        return {
            'message': '👋 Hello! I\'m your AI business assistant. I can help you with:\n\n' +
                      '🎯 **Business Advice:** Get recommendations for inventory, sales, cash flow\n' +
                      '📝 **Create Vouchers:** Invoices, orders, quotations\n' +
                      '🎪 **Lead Management:** Track prospects and opportunities\n' +
                      '💰 **Tax & GST:** Rates, filing, compliance\n' +
                      '🧭 **Navigation:** Quick access to any page\n\n' +
                      'Try asking me something like:\n' +
                      '• "Show me low stock items"\n' +
                      '• "Create a sales order"\n' +
                      '• "Give me inventory advice"',
            'intent': 'greeting',
            'confidence': 1.0,
            'actions': [],
            'suggestions': [
                'Business advice',
                'Create invoice',
                'Show low stock',
                'GST information'
            ]
        }
    
    def _handle_unknown_intent(self) -> Dict[str, Any]:
        """Handle unknown intents"""
        return {
            'message': 'I\'m not sure I understand that. I can help you with:\n\n' +
                      '💡 **Try asking:**\n' +
                      '• "Give me business advice"\n' +
                      '• "Create a purchase order"\n' +
                      '• "Show me low stock items"\n' +
                      '• "What are GST rates?"\n' +
                      '• "Show outstanding payments"\n\n' +
                      'Or type "help" to see everything I can do!',
            'intent': 'unknown',
            'confidence': 0.0,
            'actions': [],
            'suggestions': [
                'Help',
                'Business advice',
                'Create invoice',
                'Low stock items'
            ]
        }
    
    def get_contextual_suggestions(
        self,
        organization_id: int,
        time_of_day: Optional[str] = None
    ) -> List[str]:
        """Get contextual suggestions based on time and organization context"""
        
        current_hour = datetime.now().hour
        
        # Morning suggestions (6 AM - 12 PM)
        if 6 <= current_hour < 12:
            return [
                "Show today's pending orders",
                "View low stock items",
                "Check outstanding payments",
                "Create sales order",
                "View dashboard"
            ]
        # Afternoon suggestions (12 PM - 5 PM)
        elif 12 <= current_hour < 17:
            return [
                "Create invoice",
                "Record payment received",
                "Generate sales report",
                "View customer analytics",
                "Check GST reports"
            ]
        # Evening suggestions (5 PM - 10 PM)
        elif 17 <= current_hour < 22:
            return [
                "View today's summary",
                "Close pending orders",
                "Generate profit & loss",
                "Review pending approvals",
                "Tomorrow's schedule"
            ]
        # Night/Late suggestions (10 PM - 6 AM)
        else:
            return [
                "View reports",
                "Check analytics",
                "Review pending approvals",
                "Help",
                "Settings"
            ]
