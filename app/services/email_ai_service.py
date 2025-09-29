# app/services/email_ai_service.py

"""
AI-powered Email Analysis Service
Provides email summaries, draft suggestions, and intelligent categorization
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class EmailAIService:
    """AI service for email content analysis and assistance"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Lazy initialization of database session"""
        if self.db is None:
            from app.core.database import SessionLocal
            self.db = SessionLocal()
        return self.db
        # In a real implementation, you would initialize your AI/ML models here
        # For now, we'll use rule-based approaches with hooks for future AI integration
    
    def generate_email_summary(self, email_id: int) -> Dict[str, Any]:
        """
        Generate an AI-powered summary of an email
        
        Args:
            email_id: ID of the email to summarize
            
        Returns:
            Dict containing summary and key information
        """
        try:
            from app.models.email import Email
            
            db = self._get_db()
            email = db.query(Email).filter(Email.id == email_id).first()
            if not email:
                return {"success": False, "error": "Email not found"}
            
            # Extract email content
            content = f"{email.subject or ''}\n\n{email.body_text or ''}"
            
            # Generate summary using rule-based approach (placeholder for AI)
            summary = self._generate_rule_based_summary(content)
            
            # Extract key entities and topics
            entities = self._extract_entities(content)
            sentiment = self._analyze_sentiment(content)
            category = self._categorize_email(email)
            
            return {
                "success": True,
                "summary": summary,
                "entities": entities,
                "sentiment": sentiment,
                "category": category,
                "key_points": self._extract_key_points(content),
                "urgency_level": self._assess_urgency(email),
                "requires_response": self._requires_response(content)
            }
            
        except Exception as e:
            logger.error(f"Error generating email summary: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_reply_suggestions(self, email_id: int, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI-powered reply suggestions for an email
        
        Args:
            email_id: ID of the email to reply to
            context: Optional context or instructions for the reply
            
        Returns:
            Dict containing reply suggestions
        """
        try:
            email = self.db.query(Email).filter(Email.id == email_id).first()
            if not email:
                return {"success": False, "error": "Email not found"}
            
            # Analyze the original email
            content = f"{email.subject or ''}\n\n{email.body_text or ''}"
            email_type = self._classify_email_type(content)
            tone = self._analyze_tone(content)
            
            # Generate appropriate reply suggestions
            suggestions = []
            
            if email_type == "question":
                suggestions = self._generate_question_replies(content, tone)
            elif email_type == "request":
                suggestions = self._generate_request_replies(content, tone)
            elif email_type == "complaint":
                suggestions = self._generate_complaint_replies(content, tone)
            elif email_type == "meeting":
                suggestions = self._generate_meeting_replies(content, tone)
            else:
                suggestions = self._generate_generic_replies(content, tone)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "email_type": email_type,
                "recommended_tone": tone,
                "original_sender": email.sender_name
            }
            
        except Exception as e:
            logger.error(f"Error generating reply suggestions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def categorize_email_batch(self, email_ids: List[int]) -> Dict[str, Any]:
        """
        Categorize multiple emails using AI
        
        Args:
            email_ids: List of email IDs to categorize
            
        Returns:
            Dict containing categorization results
        """
        try:
            results = []
            
            emails = self.db.query(Email).filter(Email.id.in_(email_ids)).all()
            
            for email in emails:
                category = self._categorize_email(email)
                confidence = self._calculate_category_confidence(email, category)
                
                results.append({
                    "email_id": email.id,
                    "category": category,
                    "confidence": confidence,
                    "subject": email.subject
                })
            
            return {
                "success": True,
                "categorized_emails": results,
                "total_processed": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error in batch categorization: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def extract_action_items(self, email_id: int) -> Dict[str, Any]:
        """
        Extract action items and tasks from email content
        
        Args:
            email_id: ID of the email to analyze
            
        Returns:
            Dict containing extracted action items
        """
        try:
            email = self.db.query(Email).filter(Email.id == email_id).first()
            if not email:
                return {"success": False, "error": "Email not found"}
            
            content = f"{email.subject or ''}\n\n{email.body_text or ''}"
            
            # Extract action items using pattern matching
            action_items = self._extract_action_patterns(content)
            deadlines = self._extract_deadline_patterns(content)
            priorities = self._extract_priority_indicators(content)
            
            return {
                "success": True,
                "action_items": action_items,
                "deadlines": deadlines,
                "priorities": priorities,
                "suggested_tasks": self._convert_to_task_suggestions(action_items, deadlines, priorities)
            }
            
        except Exception as e:
            logger.error(f"Error extracting action items: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_rule_based_summary(self, content: str) -> str:
        """Generate a rule-based summary (placeholder for AI implementation)"""
        if not content.strip():
            return "No content to summarize."
        
        # Simple extractive summary - take first and key sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return content[:300] + ("..." if len(content) > 300 else "")
        
        # Take first sentence and sentences with key indicators
        key_indicators = ['important', 'urgent', 'please', 'need', 'request', 'deadline', 'asap']
        summary_sentences = [sentences[0]]  # Always include first sentence
        
        for sentence in sentences[1:]:
            if any(indicator in sentence.lower() for indicator in key_indicators):
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 3:
                    break
        
        summary = '. '.join(summary_sentences)
        return summary[:300] + ("..." if len(summary) > 300 else "")
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from email content"""
        entities = {
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content),
            "phone_numbers": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content),
            "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        }
        return entities
    
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of email content"""
        # Simple rule-based sentiment analysis
        positive_words = ['thank', 'great', 'excellent', 'good', 'happy', 'pleased', 'wonderful']
        negative_words = ['problem', 'issue', 'urgent', 'complaint', 'disappointed', 'sorry', 'concern']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _categorize_email(self, email) -> str:
        """Categorize email based on content and metadata"""
        subject = (email.subject or '').lower()
        content = (email.body_text or '').lower()
        
        # ERP-specific categories
        if any(word in subject + content for word in ['invoice', 'payment', 'bill', 'receipt']):
            return "finance"
        elif any(word in subject + content for word in ['order', 'purchase', 'delivery', 'shipment']):
            return "procurement"
        elif any(word in subject + content for word in ['meeting', 'call', 'appointment', 'schedule']):
            return "meeting"
        elif any(word in subject + content for word in ['support', 'help', 'issue', 'problem']):
            return "support"
        elif any(word in subject + content for word in ['project', 'task', 'deadline', 'milestone']):
            return "project"
        elif any(word in subject + content for word in ['hr', 'leave', 'employee', 'payroll']):
            return "hr"
        else:
            return "general"
    
    def _assess_urgency(self, email) -> str:
        """Assess urgency level of email"""
        subject = (email.subject or '').lower()
        content = (email.body_text or '').lower()
        
        urgent_indicators = ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'deadline']
        high_indicators = ['important', 'priority', 'soon', 'needed']
        
        if any(indicator in subject + content for indicator in urgent_indicators):
            return "urgent"
        elif any(indicator in subject + content for indicator in high_indicators):
            return "high"
        else:
            return "normal"
    
    def _requires_response(self, content: str) -> bool:
        """Determine if email requires a response"""
        content_lower = content.lower()
        response_indicators = [
            '?', 'please reply', 'let me know', 'confirm', 'respond', 'feedback',
            'thoughts', 'opinion', 'what do you think', 'please advise'
        ]
        return any(indicator in content_lower for indicator in response_indicators)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from email content"""
        # Look for bullet points, numbered lists, and sentences with key indicators
        key_points = []
        
        # Find bullet points and numbered lists
        bullet_pattern = r'^[\s]*[•\-\*\d+\.]\s+(.+)$'
        for match in re.finditer(bullet_pattern, content, re.MULTILINE):
            key_points.append(match.group(1).strip())
        
        # If no bullet points, look for sentences with key indicators
        if not key_points:
            sentences = re.split(r'[.!?]+', content)
            key_indicators = ['important', 'note', 'please', 'need', 'must', 'should']
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in key_indicators):
                    key_points.append(sentence.strip())
                    if len(key_points) >= 5:  # Limit to 5 key points
                        break
        
        return key_points[:5]  # Return max 5 key points
    
    def _classify_email_type(self, content: str) -> str:
        """Classify the type of email"""
        content_lower = content.lower()
        
        if '?' in content:
            return "question"
        elif any(word in content_lower for word in ['please', 'request', 'need', 'could you']):
            return "request"
        elif any(word in content_lower for word in ['meeting', 'call', 'schedule', 'appointment']):
            return "meeting"
        elif any(word in content_lower for word in ['complaint', 'issue', 'problem', 'dissatisfied']):
            return "complaint"
        else:
            return "informational"
    
    def _analyze_tone(self, content: str) -> str:
        """Analyze the tone of the email"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['please', 'thank you', 'appreciate']):
            return "polite"
        elif any(word in content_lower for word in ['urgent', 'asap', 'immediately']):
            return "urgent"
        elif any(word in content_lower for word in ['disappointed', 'concerned', 'unacceptable']):
            return "concerned"
        else:
            return "neutral"
    
    def _generate_question_replies(self, content: str, tone: str) -> List[Dict[str, str]]:
        """Generate reply suggestions for questions"""
        return [
            {
                "type": "acknowledge",
                "subject": "Re: Your Question",
                "body": "Thank you for your question. I'll look into this and get back to you shortly."
            },
            {
                "type": "request_clarification",
                "subject": "Re: Your Question - Need Clarification",
                "body": "Thank you for your email. Could you please provide a bit more detail about..."
            },
            {
                "type": "provide_info",
                "subject": "Re: Your Question",
                "body": "Thank you for reaching out. Here's the information you requested..."
            }
        ]
    
    def _generate_request_replies(self, content: str, tone: str) -> List[Dict[str, str]]:
        """Generate reply suggestions for requests"""
        return [
            {
                "type": "acknowledge",
                "subject": "Re: Your Request - Received",
                "body": "Thank you for your request. I've received it and will process it shortly."
            },
            {
                "type": "timeline",
                "subject": "Re: Your Request - Timeline",
                "body": "Thank you for your request. I expect to have this completed by [DATE]."
            },
            {
                "type": "approve",
                "subject": "Re: Your Request - Approved",
                "body": "Your request has been approved. I'll proceed with the next steps."
            }
        ]
    
    def _generate_complaint_replies(self, content: str, tone: str) -> List[Dict[str, str]]:
        """Generate reply suggestions for complaints"""
        return [
            {
                "type": "apologize",
                "subject": "Re: Your Concern - Our Apologies",
                "body": "I sincerely apologize for the inconvenience you've experienced. Let me look into this immediately."
            },
            {
                "type": "investigate",
                "subject": "Re: Your Concern - Under Investigation",
                "body": "Thank you for bringing this to my attention. I'm investigating the matter and will provide an update soon."
            },
            {
                "type": "escalate",
                "subject": "Re: Your Concern - Escalated",
                "body": "I understand your frustration. I'm escalating this to ensure it receives proper attention."
            }
        ]
    
    def _generate_meeting_replies(self, content: str, tone: str) -> List[Dict[str, str]]:
        """Generate reply suggestions for meeting-related emails"""
        return [
            {
                "type": "accept",
                "subject": "Re: Meeting Request - Accepted",
                "body": "Thank you for the meeting invitation. I'll be there at the scheduled time."
            },
            {
                "type": "suggest_time",
                "subject": "Re: Meeting Request - Alternative Time",
                "body": "Thank you for the invitation. Could we possibly schedule this for [ALTERNATIVE TIME]?"
            },
            {
                "type": "request_agenda",
                "subject": "Re: Meeting Request - Agenda Request",
                "body": "Looking forward to the meeting. Could you share the agenda in advance?"
            }
        ]
    
    def _generate_generic_replies(self, content: str, tone: str) -> List[Dict[str, str]]:
        """Generate generic reply suggestions"""
        return [
            {
                "type": "acknowledge",
                "subject": "Re: Your Email",
                "body": "Thank you for your email. I've received it and will respond accordingly."
            },
            {
                "type": "follow_up",
                "subject": "Re: Your Email - Following Up",
                "body": "Thank you for your email. I'll follow up on this and get back to you."
            }
        ]
    
    def _calculate_category_confidence(self, email, category: str) -> float:
        """Calculate confidence score for email categorization"""
        # Simple confidence calculation based on keyword matches
        content = f"{email.subject or ''} {email.body_text or ''}".lower()
        
        category_keywords = {
            "finance": ["invoice", "payment", "bill", "receipt", "financial"],
            "procurement": ["order", "purchase", "delivery", "shipment", "vendor"],
            "meeting": ["meeting", "call", "appointment", "schedule", "calendar"],
            "support": ["support", "help", "issue", "problem", "bug"],
            "project": ["project", "task", "deadline", "milestone", "deliverable"],
            "hr": ["hr", "leave", "employee", "payroll", "benefits"]
        }
        
        keywords = category_keywords.get(category, [])
        matches = sum(1 for keyword in keywords if keyword in content)
        
        if matches == 0:
            return 0.5  # Default confidence for general category
        
        return min(0.9, 0.5 + (matches * 0.1))  # Max confidence of 0.9
    
    def _extract_action_patterns(self, content: str) -> List[str]:
        """Extract action items from content"""
        action_patterns = [
            r'(?:please|need to|must|should)\s+([^.!?]+)',
            r'(?:action item|todo|task):\s*([^.!?]+)',
            r'(?:follow up|followup)\s+(?:on|with)\s+([^.!?]+)'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                action = match.group(1).strip()
                if len(action) > 10:  # Filter out very short matches
                    actions.append(action)
        
        return actions[:10]  # Limit to 10 actions
    
    def _extract_deadline_patterns(self, content: str) -> List[str]:
        """Extract deadlines from content"""
        deadline_patterns = [
            r'(?:by|before|deadline|due)\s+(\w+\s+\d{1,2}(?:,\s+\d{4})?)',
            r'(?:by|before|deadline|due)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:asap|immediately|urgent)',
            r'(?:end of|eod|eow|eom)'
        ]
        
        deadlines = []
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                deadline = match.group(0).strip()
                deadlines.append(deadline)
        
        return deadlines
    
    def _extract_priority_indicators(self, content: str) -> str:
        """Extract priority level from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['urgent', 'critical', 'asap', 'emergency']):
            return "urgent"
        elif any(word in content_lower for word in ['important', 'high priority', 'priority']):
            return "high"
        elif any(word in content_lower for word in ['low priority', 'when convenient']):
            return "low"
        else:
            return "normal"
    
    def _convert_to_task_suggestions(self, actions: List[str], deadlines: List[str], priority: str) -> List[Dict[str, Any]]:
        """Convert extracted information to task suggestions"""
        suggestions = []
        
        for i, action in enumerate(actions):
            task = {
                "title": action[:100],  # Limit title length
                "description": action,
                "priority": priority,
                "due_date": deadlines[i] if i < len(deadlines) else None
            }
            suggestions.append(task)
        
        return suggestions
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

# Global email AI service instance
email_ai_service = EmailAIService()