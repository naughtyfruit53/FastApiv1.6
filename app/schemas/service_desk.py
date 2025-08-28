# app/schemas/service_desk.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class TicketStatusEnum(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TicketPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketTypeEnum(str, Enum):
    SUPPORT = "support"
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    COMPLAINT = "complaint"

class ChatbotConversationStatusEnum(str, Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

class MessageTypeEnum(str, Enum):
    USER = "user"
    BOT = "bot"
    AGENT = "agent"
    SYSTEM = "system"

class SurveyStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    EXPIRED = "expired"

# Enhanced Ticket Schemas
class TicketBase(BaseModel):
    title: str = Field(..., description="Ticket title")
    description: Optional[str] = Field(None, description="Ticket description")
    status: TicketStatusEnum = Field(TicketStatusEnum.OPEN, description="Ticket status")
    priority: TicketPriorityEnum = Field(TicketPriorityEnum.MEDIUM, description="Ticket priority")
    ticket_type: TicketTypeEnum = Field(TicketTypeEnum.SUPPORT, description="Ticket type")
    customer_id: int = Field(..., description="Customer ID")
    assigned_to_id: Optional[int] = Field(None, description="Assigned technician/user ID")
    resolution: Optional[str] = Field(None, description="Ticket resolution")
    due_date: Optional[datetime] = Field(None, description="Due date")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    actual_hours: Optional[float] = Field(None, ge=0, description="Actual hours")
    customer_rating: Optional[int] = Field(None, ge=1, le=5, description="Customer rating (1-5)")
    customer_feedback: Optional[str] = Field(None, description="Customer feedback")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatusEnum] = None
    priority: Optional[TicketPriorityEnum] = None
    ticket_type: Optional[TicketTypeEnum] = None
    assigned_to_id: Optional[int] = None
    resolution: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    customer_rating: Optional[int] = Field(None, ge=1, le=5)
    customer_feedback: Optional[str] = None

class TicketInDB(TicketBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    ticket_number: str
    created_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Ticket(TicketInDB):
    pass

# Chatbot Conversation Schemas
class ChatbotConversationBase(BaseModel):
    customer_id: Optional[int] = Field(None, description="Customer ID")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    customer_name: Optional[str] = Field(None, description="Customer name")
    channel: str = Field(..., description="Communication channel")
    channel_user_id: Optional[str] = Field(None, description="Channel user ID")
    status: ChatbotConversationStatusEnum = Field(ChatbotConversationStatusEnum.ACTIVE, description="Conversation status")
    intent: Optional[str] = Field(None, description="Detected intent")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    escalated_to_human: bool = Field(False, description="Escalated to human")
    assigned_agent_id: Optional[int] = Field(None, description="Assigned agent ID")
    escalation_reason: Optional[str] = Field(None, description="Escalation reason")
    resolved_by_bot: bool = Field(False, description="Resolved by bot")
    resolution_category: Optional[str] = Field(None, description="Resolution category")
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Customer satisfaction (1-5)")
    ticket_id: Optional[int] = Field(None, description="Related ticket ID")

class ChatbotConversationCreate(ChatbotConversationBase):
    pass

class ChatbotConversationUpdate(BaseModel):
    status: Optional[ChatbotConversationStatusEnum] = None
    intent: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    escalated_to_human: Optional[bool] = None
    assigned_agent_id: Optional[int] = None
    escalation_reason: Optional[str] = None
    resolved_by_bot: Optional[bool] = None
    resolution_category: Optional[str] = None
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    ticket_id: Optional[int] = None

class ChatbotConversationInDB(ChatbotConversationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    conversation_id: str
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None

class ChatbotConversation(ChatbotConversationInDB):
    pass

# Chatbot Message Schemas
class ChatbotMessageBase(BaseModel):
    conversation_id: int = Field(..., description="Conversation ID")
    message_type: MessageTypeEnum = Field(..., description="Message type")
    content: str = Field(..., description="Message content")
    message_format: str = Field("text", description="Message format")
    sender_id: Optional[str] = Field(None, description="Sender ID")
    agent_id: Optional[int] = Field(None, description="Agent ID")
    intent_detected: Optional[str] = Field(None, description="Detected intent")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    entities_extracted: Optional[Dict[str, Any]] = Field(None, description="Named entities and structured data extracted from user messages using NLP. Contains person names, locations, organizations, dates, product names, issue categories, sentiment scores, and other relevant semantic information for automated processing.")
    is_read: bool = Field(False, description="Is message read")

class ChatbotMessageCreate(ChatbotMessageBase):
    pass

class ChatbotMessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

class ChatbotMessageInDB(ChatbotMessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    read_at: Optional[datetime] = None
    created_at: datetime

class ChatbotMessage(ChatbotMessageInDB):
    pass

# Survey Template Schemas
class SurveyTemplateBase(BaseModel):
    name: str = Field(..., description="Survey template name")
    description: Optional[str] = Field(None, description="Survey description")
    template_type: str = Field(..., description="Survey template type")
    questions: List[Dict[str, Any]] = Field(..., description="Survey questions")
    is_active: bool = Field(True, description="Is template active")
    trigger_event: str = Field(..., description="Trigger event")
    trigger_delay_hours: int = Field(0, ge=0, description="Trigger delay in hours")

class SurveyTemplateCreate(SurveyTemplateBase):
    pass

class SurveyTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    trigger_event: Optional[str] = None
    trigger_delay_hours: Optional[int] = Field(None, ge=0)

class SurveyTemplateInDB(SurveyTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class SurveyTemplate(SurveyTemplateInDB):
    pass

# Customer Survey Schemas
class CustomerSurveyBase(BaseModel):
    template_id: int = Field(..., description="Survey template ID")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    ticket_id: Optional[int] = Field(None, description="Ticket ID")
    status: SurveyStatusEnum = Field(SurveyStatusEnum.PENDING, description="Survey status")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_name: Optional[str] = Field(None, description="Customer name")
    responses: Optional[Dict[str, Any]] = Field(None, description="Survey responses")
    overall_rating: Optional[int] = Field(None, ge=1, le=5, description="Overall rating")
    nps_score: Optional[int] = Field(None, ge=-100, le=100, description="NPS score")
    comments: Optional[str] = Field(None, description="Additional comments")

class CustomerSurveyCreate(CustomerSurveyBase):
    pass

class CustomerSurveyUpdate(BaseModel):
    status: Optional[SurveyStatusEnum] = None
    responses: Optional[Dict[str, Any]] = None
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    nps_score: Optional[int] = Field(None, ge=-100, le=100)
    comments: Optional[str] = None

class CustomerSurveyInDB(CustomerSurveyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    survey_token: str
    sent_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

class CustomerSurvey(CustomerSurveyInDB):
    pass

# Channel Configuration Schemas
class ChannelConfigurationBase(BaseModel):
    channel_type: str = Field(..., description="Channel type")
    channel_name: str = Field(..., description="Channel name")
    is_active: bool = Field(True, description="Is channel active")
    configuration: Dict[str, Any] = Field(..., description="Channel configuration")
    bot_enabled: bool = Field(True, description="Is bot enabled")
    auto_escalation_enabled: bool = Field(True, description="Is auto escalation enabled")
    escalation_threshold_minutes: int = Field(10, ge=0, description="Escalation threshold in minutes")
    business_hours: Optional[Dict[str, Any]] = Field(None, description="Business hours")
    timezone: str = Field("UTC", description="Timezone")

class ChannelConfigurationCreate(ChannelConfigurationBase):
    pass

class ChannelConfigurationUpdate(BaseModel):
    channel_name: Optional[str] = None
    is_active: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None
    bot_enabled: Optional[bool] = None
    auto_escalation_enabled: Optional[bool] = None
    escalation_threshold_minutes: Optional[int] = Field(None, ge=0)
    business_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None

class ChannelConfigurationInDB(ChannelConfigurationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ChannelConfiguration(ChannelConfigurationInDB):
    pass

# SLA Management Schemas (Enhanced from existing)
class SLAPolicyBase(BaseModel):
    name: str = Field(..., description="SLA policy name")
    description: Optional[str] = Field(None, description="SLA policy description")
    priority: Optional[str] = Field(None, description="Applicable priority")
    ticket_type: Optional[str] = Field(None, description="Applicable ticket type")
    customer_tier: Optional[str] = Field(None, description="Applicable customer tier")
    response_time_hours: float = Field(..., gt=0, description="Response time in hours")
    resolution_time_hours: float = Field(..., gt=0, description="Resolution time in hours")
    escalation_enabled: bool = Field(True, description="Is escalation enabled")
    escalation_threshold_percent: float = Field(80.0, ge=0, le=100, description="Escalation threshold percentage")
    is_active: bool = Field(True, description="Is policy active")
    is_default: bool = Field(False, description="Is default policy")

class SLAPolicyCreate(SLAPolicyBase):
    pass

class SLAPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    ticket_type: Optional[str] = None
    customer_tier: Optional[str] = None
    response_time_hours: Optional[float] = Field(None, gt=0)
    resolution_time_hours: Optional[float] = Field(None, gt=0)
    escalation_enabled: Optional[bool] = None
    escalation_threshold_percent: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class SLAPolicyInDB(SLAPolicyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class SLAPolicy(SLAPolicyInDB):
    pass

# Service Desk Analytics Schemas
class ServiceDeskAnalytics(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    tickets_by_priority: Dict[str, int]
    tickets_by_type: Dict[str, int]
    average_resolution_time_hours: float
    average_response_time_hours: float
    sla_compliance_rate: float
    customer_satisfaction_score: float
    first_contact_resolution_rate: float
    escalation_rate: float
    agent_performance: List[Dict[str, Any]]
    period_start: date
    period_end: date

class ChatbotAnalytics(BaseModel):
    total_conversations: int
    resolved_by_bot: int
    escalated_to_human: int
    bot_resolution_rate: float
    average_conversation_duration_minutes: float
    most_common_intents: List[Dict[str, Any]]
    customer_satisfaction_scores: Dict[int, int]  # rating -> count
    channels_performance: Dict[str, Dict[str, Any]]
    period_start: date
    period_end: date

class SurveyAnalytics(BaseModel):
    total_surveys_sent: int
    total_surveys_completed: int
    response_rate: float
    average_rating: float
    nps_score: float
    ratings_distribution: Dict[int, int]  # rating -> count
    most_common_feedback_themes: List[Dict[str, Any]]
    surveys_by_template: Dict[str, Dict[str, Any]]
    period_start: date
    period_end: date

# Escalation and Workflow Schemas
class TicketEscalationRequest(BaseModel):
    ticket_id: int = Field(..., description="Ticket ID")
    escalation_reason: str = Field(..., description="Escalation reason")
    escalate_to_id: Optional[int] = Field(None, description="Escalate to user ID")
    priority_override: Optional[TicketPriorityEnum] = Field(None, description="Priority override")
    notes: Optional[str] = Field(None, description="Escalation notes")

class TicketEscalationResponse(BaseModel):
    success: bool
    ticket_id: int
    escalated_to: Optional[str] = None
    new_priority: Optional[str] = None
    message: str

class BulkTicketUpdate(BaseModel):
    ticket_ids: List[int] = Field(..., description="List of ticket IDs")
    updates: Dict[str, Any] = Field(..., description="Updates to apply")
    reason: Optional[str] = Field(None, description="Reason for bulk update")

class BulkTicketResponse(BaseModel):
    success: bool
    updated_count: int
    failed_count: int
    errors: List[str]
    warnings: List[str]

# Integration Schemas
class ChatbotIntentTrainingData(BaseModel):
    intent: str = Field(..., description="Intent name")
    examples: List[str] = Field(..., description="Training examples")
    responses: List[str] = Field(..., description="Bot responses")

class ChatbotTrainingRequest(BaseModel):
    training_data: List[ChatbotIntentTrainingData] = Field(..., description="Training data")
    model_version: Optional[str] = Field(None, description="Model version")

class ChatbotTrainingResponse(BaseModel):
    success: bool
    model_version: str
    training_accuracy: Optional[float] = None
    message: str