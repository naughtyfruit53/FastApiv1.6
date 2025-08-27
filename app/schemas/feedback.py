# app/schemas/feedback.py

"""
Pydantic schemas for customer feedback and service closure workflow
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Customer Feedback Enums
class FeedbackStatus(str, Enum):
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    RESPONDED = "responded"
    CLOSED = "closed"


class SatisfactionLevel(str, Enum):
    VERY_SATISFIED = "very_satisfied"
    SATISFIED = "satisfied"
    NEUTRAL = "neutral"
    DISSATISFIED = "dissatisfied"
    VERY_DISSATISFIED = "very_dissatisfied"


class ContactMethod(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"


# Customer Feedback Schemas
class CustomerFeedbackBase(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5, description="Overall rating from 1 to 5")
    service_quality_rating: Optional[int] = Field(None, ge=1, le=5, description="Service quality rating from 1 to 5")
    technician_rating: Optional[int] = Field(None, ge=1, le=5, description="Technician rating from 1 to 5")
    timeliness_rating: Optional[int] = Field(None, ge=1, le=5, description="Timeliness rating from 1 to 5")
    communication_rating: Optional[int] = Field(None, ge=1, le=5, description="Communication rating from 1 to 5")
    feedback_comments: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    survey_responses: Optional[Dict[str, Any]] = None  # Will be serialized as JSON
    would_recommend: Optional[bool] = None
    satisfaction_level: Optional[SatisfactionLevel] = None
    follow_up_preferred: bool = False
    preferred_contact_method: Optional[ContactMethod] = None


class CustomerFeedbackCreate(CustomerFeedbackBase):
    installation_job_id: int
    customer_id: int
    completion_record_id: Optional[int] = None


class CustomerFeedbackUpdate(BaseModel):
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    service_quality_rating: Optional[int] = Field(None, ge=1, le=5)
    technician_rating: Optional[int] = Field(None, ge=1, le=5)
    timeliness_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comments: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    survey_responses: Optional[Dict[str, Any]] = None
    would_recommend: Optional[bool] = None
    satisfaction_level: Optional[SatisfactionLevel] = None
    follow_up_preferred: Optional[bool] = None
    preferred_contact_method: Optional[ContactMethod] = None
    feedback_status: Optional[FeedbackStatus] = None
    response_notes: Optional[str] = None


class CustomerFeedbackInDB(CustomerFeedbackBase):
    id: int
    organization_id: int
    installation_job_id: int
    customer_id: int
    completion_record_id: Optional[int] = None
    feedback_status: FeedbackStatus
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    response_notes: Optional[str] = None
    submitted_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Service Closure Enums
class ClosureStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    CLOSED = "closed"
    REOPENED = "reopened"


class ClosureReason(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CUSTOMER_REQUEST = "customer_request"
    NO_SHOW = "no_show"


# Service Closure Schemas
class ServiceClosureBase(BaseModel):
    closure_reason: Optional[ClosureReason] = None
    closure_notes: Optional[str] = None
    requires_manager_approval: bool = True
    approval_notes: Optional[str] = None
    final_closure_notes: Optional[str] = None
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    reopening_reason: Optional[str] = None


class ServiceClosureCreate(ServiceClosureBase):
    installation_job_id: int
    completion_record_id: Optional[int] = None
    customer_feedback_id: Optional[int] = None


class ServiceClosureUpdate(BaseModel):
    closure_status: Optional[ClosureStatus] = None
    closure_reason: Optional[ClosureReason] = None
    closure_notes: Optional[str] = None
    requires_manager_approval: Optional[bool] = None
    approval_notes: Optional[str] = None
    final_closure_notes: Optional[str] = None
    feedback_received: Optional[bool] = None
    minimum_rating_met: Optional[bool] = None
    escalation_required: Optional[bool] = None
    escalation_reason: Optional[str] = None
    reopening_reason: Optional[str] = None


class ServiceClosureInDB(ServiceClosureBase):
    id: int
    organization_id: int
    installation_job_id: int
    completion_record_id: Optional[int] = None
    customer_feedback_id: Optional[int] = None
    closure_status: ClosureStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    closed_by_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    feedback_received: bool
    minimum_rating_met: bool
    reopened_count: int
    last_reopened_at: Optional[datetime] = None
    last_reopened_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Filter schemas
class CustomerFeedbackFilter(BaseModel):
    feedback_status: Optional[FeedbackStatus] = None
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    customer_id: Optional[int] = None
    installation_job_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    satisfaction_level: Optional[SatisfactionLevel] = None


class ServiceClosureFilter(BaseModel):
    closure_status: Optional[ClosureStatus] = None
    closure_reason: Optional[ClosureReason] = None
    requires_manager_approval: Optional[bool] = None
    feedback_received: Optional[bool] = None
    escalation_required: Optional[bool] = None
    approved_by_id: Optional[int] = None
    closed_by_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None