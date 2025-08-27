# app/schemas/customer_analytics.py

"""
Pydantic schemas for Customer Analytics API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class InteractionType(str, Enum):
    """Valid interaction types"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    SUPPORT_TICKET = "support_ticket"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"


class InteractionStatus(str, Enum):
    """Valid interaction statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SegmentName(str, Enum):
    """Common segment names"""
    VIP = "vip"
    PREMIUM = "premium"
    REGULAR = "regular"
    NEW = "new"
    HIGH_VALUE = "high_value"
    AT_RISK = "at_risk"


# Response Models

class InteractionMetricsResponse(BaseModel):
    """Interaction metrics breakdown"""
    total_count: int = Field(..., description="Total number of interactions")
    last_interaction_date: Optional[datetime] = Field(None, description="Date of last interaction")
    by_type: Dict[str, int] = Field(default_factory=dict, description="Interaction count by type")
    by_status: Dict[str, int] = Field(default_factory=dict, description="Interaction count by status")


class CustomerSegmentInfo(BaseModel):
    """Customer segment information"""
    segment_name: str = Field(..., description="Name of the segment")
    segment_value: Optional[float] = Field(None, description="Numeric value associated with segment")
    assigned_date: datetime = Field(..., description="Date when segment was assigned")
    description: Optional[str] = Field(None, description="Segment description")


class RecentInteraction(BaseModel):
    """Recent interaction summary"""
    interaction_type: str = Field(..., description="Type of interaction")
    subject: str = Field(..., description="Interaction subject")
    status: str = Field(..., description="Current status")
    interaction_date: datetime = Field(..., description="Date of interaction")


class CustomerAnalyticsResponse(BaseModel):
    """Complete customer analytics response"""
    customer_id: int = Field(..., description="Customer ID")
    customer_name: str = Field(..., description="Customer name")
    total_interactions: int = Field(..., description="Total number of interactions")
    last_interaction_date: Optional[datetime] = Field(None, description="Date of last interaction")
    interaction_types: Dict[str, int] = Field(default_factory=dict, description="Breakdown by interaction type")
    interaction_status: Dict[str, int] = Field(default_factory=dict, description="Breakdown by status")
    segments: List[CustomerSegmentInfo] = Field(default_factory=list, description="Current segment memberships")
    recent_interactions: List[RecentInteraction] = Field(default_factory=list, description="Recent interactions")
    calculated_at: datetime = Field(..., description="Timestamp when analytics were calculated")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ActivityTimelineEntry(BaseModel):
    """Daily activity timeline entry"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    interaction_count: int = Field(..., description="Number of interactions on this date")


class SegmentAnalyticsResponse(BaseModel):
    """Segment analytics response"""
    segment_name: str = Field(..., description="Name of the segment")
    total_customers: int = Field(..., description="Total customers in segment")
    total_interactions: int = Field(..., description="Total interactions for segment")
    avg_interactions_per_customer: float = Field(..., description="Average interactions per customer")
    interaction_distribution: Dict[str, int] = Field(default_factory=dict, description="Interaction type distribution")
    activity_timeline: List[ActivityTimelineEntry] = Field(default_factory=list, description="Activity timeline")
    calculated_at: datetime = Field(..., description="Timestamp when analytics were calculated")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrganizationAnalyticsSummary(BaseModel):
    """Organization-wide analytics summary"""
    organization_id: int = Field(..., description="Organization ID")
    total_customers: int = Field(..., description="Total active customers")
    total_interactions: int = Field(..., description="Total interactions")
    segment_distribution: Dict[str, int] = Field(default_factory=dict, description="Customer distribution by segment")
    interaction_trends: List[ActivityTimelineEntry] = Field(default_factory=list, description="Interaction trends")
    calculated_at: datetime = Field(..., description="Timestamp when analytics were calculated")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request Models

class CustomerAnalyticsRequest(BaseModel):
    """Request parameters for customer analytics"""
    include_recent_interactions: bool = Field(True, description="Include recent interactions in response")
    recent_interactions_limit: int = Field(5, ge=1, le=20, description="Number of recent interactions to include")

    @validator('recent_interactions_limit')
    def validate_limit(cls, v):
        if v < 1 or v > 20:
            raise ValueError('recent_interactions_limit must be between 1 and 20')
        return v


class SegmentAnalyticsRequest(BaseModel):
    """Request parameters for segment analytics"""
    include_timeline: bool = Field(True, description="Include activity timeline")
    timeline_days: int = Field(30, ge=7, le=365, description="Number of days for timeline")

    @validator('timeline_days')
    def validate_timeline_days(cls, v):
        if v < 7 or v > 365:
            raise ValueError('timeline_days must be between 7 and 365')
        return v


class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_customers: int = Field(..., description="Total active customers")
    total_interactions_today: int = Field(..., description="Interactions today")
    total_interactions_week: int = Field(..., description="Interactions this week")
    total_interactions_month: int = Field(..., description="Interactions this month")
    top_segments: List[Dict[str, Any]] = Field(default_factory=list, description="Top segments by customer count")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity summary")
    calculated_at: datetime = Field(..., description="Timestamp when metrics were calculated")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Error response models

class AnalyticsErrorResponse(BaseModel):
    """Error response for analytics endpoints"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str = Field(..., description="Field name with validation error")
    message: str = Field(..., description="Validation error message")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(default="Request validation failed", description="Error message")
    details: List[ValidationErrorDetail] = Field(default_factory=list, description="Validation error details")