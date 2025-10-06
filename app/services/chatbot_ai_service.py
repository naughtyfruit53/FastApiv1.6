# app/services/chatbot_ai_service.py

"""
AI/NLP Service for Chatbot
Requirement 2: Add AI/NLP capabilities to chatbot module for natural language queries and responses
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatbotAIService:
    """
    AI-powered chatbot service with NLP capabilities.
    Provides intent detection, entity extraction, and intelligent responses.
    """
    
    def __init__(self):
        """Initialize the chatbot AI service"""
        self.intents = self._initialize_intents()
        self.entities = self._initialize_entities()
    
    def _initialize_intents(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize intent patterns and responses.
        In production, this would be loaded from a trained model or database.
        """
        return {
            "greeting": {
                "patterns": [
                    r"\b(hi|hello|hey|greetings)\b",
                    r"\bgood (morning|afternoon|evening)\b"
                ],
                "responses": [
                    "Hello! How can I assist you today?",
                    "Hi there! What can I help you with?",
                    "Greetings! How may I help you?"
                ],
                "confidence_threshold": 0.8
            },
            "voucher_inquiry": {
                "patterns": [
                    r"\b(voucher|invoice|bill|receipt)\b",
                    r"\bpurchase (order|voucher)\b",
                    r"\bsales (order|invoice)\b",
                    r"\b(po|so|pi)\b"
                ],
                "responses": [
                    "I can help you with vouchers. Are you looking to create, view, or search for a voucher?",
                    "I see you're asking about vouchers. Would you like to create a new one or find an existing voucher?"
                ],
                "confidence_threshold": 0.7
            },
            "customer_inquiry": {
                "patterns": [
                    r"\b(customer|client|party)\b",
                    r"\bvendor\b",
                    r"\bsupplier\b"
                ],
                "responses": [
                    "I can help with customer information. What would you like to know?",
                    "Let me assist you with customer details. What are you looking for?"
                ],
                "confidence_threshold": 0.7
            },
            "stock_inquiry": {
                "patterns": [
                    r"\b(stock|inventory|product)\b",
                    r"\bitem\b.*\b(available|quantity)\b",
                    r"\b(warehouse|godown)\b"
                ],
                "responses": [
                    "I can help you check stock levels. Which product are you interested in?",
                    "Let me look up inventory information for you. What item would you like to check?"
                ],
                "confidence_threshold": 0.7
            },
            "payment_inquiry": {
                "patterns": [
                    r"\b(payment|paid|due|outstanding)\b",
                    r"\baccount (payable|receivable)\b",
                    r"\bbalance\b"
                ],
                "responses": [
                    "I can help with payment information. Are you looking for outstanding balances or payment history?",
                    "Let me check payment details for you. What specific information do you need?"
                ],
                "confidence_threshold": 0.7
            },
            "report_inquiry": {
                "patterns": [
                    r"\b(report|summary|analysis)\b",
                    r"\b(sales|purchase) report\b",
                    r"\b(profit|loss|revenue)\b"
                ],
                "responses": [
                    "I can generate reports for you. What type of report would you like?",
                    "Let me help you with reports. Which report are you interested in?"
                ],
                "confidence_threshold": 0.7
            },
            "help": {
                "patterns": [
                    r"\b(help|assist|support)\b",
                    r"\bhow (do|can) (i|you)\b",
                    r"\bwhat (is|are)\b"
                ],
                "responses": [
                    "I'm here to help! I can assist with vouchers, customers, inventory, payments, and reports. What would you like to know?",
                    "I can help with various tasks. Try asking me about vouchers, stock, customers, or payments."
                ],
                "confidence_threshold": 0.6
            },
            "unknown": {
                "patterns": [],
                "responses": [
                    "I'm not sure I understand. Could you rephrase your question?",
                    "I didn't quite get that. Can you try asking in a different way?",
                    "I'm still learning! Could you provide more details about what you're looking for?"
                ],
                "confidence_threshold": 0.0
            }
        }
    
    def _initialize_entities(self) -> Dict[str, str]:
        """Initialize entity patterns for extraction"""
        return {
            "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            "amount": r"\b(?:rs\.?|₹)?\s*\d+(?:,\d{3})*(?:\.\d{2})?\b",
            "voucher_number": r"\b(?:po|so|pi|inv|grn)[/-]?\d+[/-]?\d*\b",
            "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
            "phone": r"\b(?:\+91)?[6-9]\d{9}\b"
        }
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect the intent of a user message using pattern matching.
        
        Args:
            message: User's message text
            
        Returns:
            Dict with intent, confidence, and matched patterns
        """
        message_lower = message.lower()
        
        best_intent = "unknown"
        best_confidence = 0.0
        matched_patterns = []
        
        for intent_name, intent_data in self.intents.items():
            if intent_name == "unknown":
                continue
                
            for pattern in intent_data["patterns"]:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    # Simple confidence scoring based on pattern length and specificity
                    confidence = min(0.9, len(pattern) / 50)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_name
                        matched_patterns.append(pattern)
        
        # Apply confidence threshold
        intent_config = self.intents.get(best_intent, {})
        threshold = intent_config.get("confidence_threshold", 0.5)
        
        if best_confidence < threshold:
            best_intent = "unknown"
            best_confidence = 0.3
        
        logger.info(f"Detected intent: {best_intent} (confidence: {best_confidence:.2f})")
        
        return {
            "intent": best_intent,
            "confidence": round(best_confidence, 2),
            "matched_patterns": matched_patterns
        }
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the message.
        
        Args:
            message: User's message text
            
        Returns:
            Dict of entity types and their extracted values
        """
        extracted = {}
        
        for entity_type, pattern in self.entities.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                extracted[entity_type] = matches
        
        if extracted:
            logger.info(f"Extracted entities: {extracted}")
        
        return extracted
    
    def generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered response to a user message.
        
        Args:
            message: User's message text
            context: Optional context from previous conversation
            
        Returns:
            Dict with response, intent, entities, and confidence
        """
        try:
            # Detect intent
            intent_result = self.detect_intent(message)
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]
            
            # Extract entities
            entities = self.extract_entities(message)
            
            # Get response template
            intent_config = self.intents.get(intent, self.intents["unknown"])
            responses = intent_config["responses"]
            
            # Select response (in production, this could be more sophisticated)
            import random
            response_text = random.choice(responses)
            
            # Add context-aware enhancement
            if context and context.get("previous_intent"):
                prev_intent = context["previous_intent"]
                if prev_intent == intent:
                    response_text = "Continuing on that topic... " + response_text
            
            # Format entities in response if relevant
            if entities:
                entity_info = ", ".join([f"{k}: {v[0]}" for k, v in entities.items()])
                response_text += f"\n\nI noticed: {entity_info}"
            
            return {
                "success": True,
                "response": response_text,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return {
                "success": False,
                "response": "I encountered an error processing your message. Please try again.",
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "error": str(e)
            }
    
    def suggest_actions(self, intent: str, entities: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """
        Suggest actionable items based on detected intent and entities.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            
        Returns:
            List of suggested actions
        """
        actions = []
        
        if intent == "voucher_inquiry":
            actions.append({
                "label": "Create New Voucher",
                "action": "navigate",
                "target": "/vouchers/create"
            })
            actions.append({
                "label": "View Voucher List",
                "action": "navigate",
                "target": "/vouchers"
            })
            
            if "voucher_number" in entities:
                voucher_num = entities["voucher_number"][0]
                actions.append({
                    "label": f"View Voucher {voucher_num}",
                    "action": "navigate",
                    "target": f"/vouchers/{voucher_num}"
                })
        
        elif intent == "customer_inquiry":
            actions.append({
                "label": "View Customers",
                "action": "navigate",
                "target": "/masters/customers"
            })
            actions.append({
                "label": "Add New Customer",
                "action": "navigate",
                "target": "/masters/customers/create"
            })
        
        elif intent == "stock_inquiry":
            actions.append({
                "label": "View Stock Levels",
                "action": "navigate",
                "target": "/inventory/stock"
            })
            actions.append({
                "label": "Stock Report",
                "action": "navigate",
                "target": "/reports/stock"
            })
        
        return actions


# Singleton instance
chatbot_ai_service = ChatbotAIService()
