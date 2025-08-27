# app/schemas/sla.py

"""
Pydantic schemas for SLA Management in Service CRM.
Handles validation for SLA policies and tracking.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class SLAStatusEnum(str, Enum):
    """SLA status enumeration"""
    PENDING = "pending"
    MET = "met"
    BREACHED = "breached"


# SLA Policy Schemas
class SLAPolicyBase(BaseModel):
    """Base SLA policy schema with common fields"""
    name: str = Field(..., description="SLA policy name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Policy description")
    priority: Optional[str] = Field(None, description="Applicable priority level (null = all)")
    ticket_type: Optional[str] = Field(None, description="Applicable ticket type (null = all)")
    customer_tier: Optional[str] = Field(None, description="Applicable customer tier (null = all)")
    response_time_hours: float = Field(..., description="Response time in hours", gt=0)
    resolution_time_hours: float = Field(..., description="Resolution time in hours", gt=0)
    escalation_enabled: bool = Field(True, description="Whether escalation is enabled")
    escalation_threshold_percent: float = Field(80.0, description="Escalation threshold percentage", ge=0, le=100)
    is_active: bool = Field(True, description="Whether the policy is active")
    is_default: bool = Field(False, description="Whether this is the default policy")


class SLAPolicyCreate(SLAPolicyBase):
    """Schema for creating SLA policies"""
    pass


class SLAPolicyUpdate(BaseModel):
    """Schema for updating SLA policies"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
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
    """Schema for SLA policy with database fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


class SLAPolicyResponse(SLAPolicyInDB):
    """Schema for SLA policy API responses"""
    pass


# SLA Tracking Schemas
class SLATrackingBase(BaseModel):
    """Base SLA tracking schema"""
    response_deadline: datetime = Field(..., description="Response deadline")
    resolution_deadline: datetime = Field(..., description="Resolution deadline")
    first_response_at: Optional[datetime] = Field(None, description="When first response was made")
    resolved_at: Optional[datetime] = Field(None, description="When ticket was resolved")
    response_status: SLAStatusEnum = Field(SLAStatusEnum.PENDING, description="Response SLA status")
    resolution_status: SLAStatusEnum = Field(SLAStatusEnum.PENDING, description="Resolution SLA status")
    escalation_triggered: bool = Field(False, description="Whether escalation was triggered")
    escalation_triggered_at: Optional[datetime] = Field(None, description="When escalation was triggered")
    escalation_level: int = Field(0, description="Current escalation level", ge=0)
    response_breach_hours: Optional[float] = Field(None, description="Response breach in hours (negative = met)")
    resolution_breach_hours: Optional[float] = Field(None, description="Resolution breach in hours (negative = met)")


class SLATrackingCreate(BaseModel):
    """Schema for creating SLA tracking (internal use)"""
    ticket_id: int
    policy_id: int
    response_deadline: datetime
    resolution_deadline: datetime


class SLATrackingUpdate(BaseModel):
    """Schema for updating SLA tracking"""
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_status: Optional[SLAStatusEnum] = None
    resolution_status: Optional[SLAStatusEnum] = None
    escalation_triggered: Optional[bool] = None
    escalation_triggered_at: Optional[datetime] = None
    escalation_level: Optional[int] = Field(None, ge=0)
    response_breach_hours: Optional[float] = None
    resolution_breach_hours: Optional[float] = None


class SLATrackingInDB(SLATrackingBase):
    """Schema for SLA tracking with database fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    ticket_id: int
    policy_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SLATrackingResponse(SLATrackingInDB):
    """Schema for SLA tracking API responses"""
    pass


# Combined Schemas for API responses
class SLATrackingWithPolicy(SLATrackingResponse):
    """SLA tracking with associated policy details"""
    policy: SLAPolicyResponse


class TicketWithSLA(BaseModel):
    """Ticket information with SLA tracking"""
    model_config = ConfigDict(from_attributes=True)
    
    ticket_id: int
    ticket_number: str
    title: str
    status: str
    priority: str
    ticket_type: str
    created_at: datetime
    due_date: Optional[datetime] = None
    sla_tracking: Optional[SLATrackingWithPolicy] = None


# SLA Dashboard/Analytics Schemas
class SLAMetrics(BaseModel):
    """SLA performance metrics"""
    total_tickets: int = Field(..., description="Total tickets tracked")
    response_sla_met: int = Field(..., description="Tickets meeting response SLA")
    resolution_sla_met: int = Field(..., description="Tickets meeting resolution SLA")
    response_sla_breached: int = Field(..., description="Tickets with response SLA breach")
    resolution_sla_breached: int = Field(..., description="Tickets with resolution SLA breach")
    escalated_tickets: int = Field(..., description="Total escalated tickets")
    avg_response_time_hours: Optional[float] = Field(None, description="Average response time")
    avg_resolution_time_hours: Optional[float] = Field(None, description="Average resolution time")
    response_sla_percentage: float = Field(..., description="Response SLA compliance percentage")
    resolution_sla_percentage: float = Field(..., description="Resolution SLA compliance percentage")


class SLADashboard(BaseModel):
    """SLA dashboard data"""
    organization_id: int
    period_start: datetime
    period_end: datetime
    metrics: SLAMetrics
    top_breached_policies: List[SLAPolicyResponse] = Field(default_factory=list)
    escalated_tickets: List[TicketWithSLA] = Field(default_factory=list)


# SLA Policy Assignment Schema
class SLAPolicyAssignment(BaseModel):
    """Schema for assigning SLA policy to a ticket"""
    ticket_id: int
    policy_id: int
    force_reassign: bool = Field(False, description="Force reassignment if SLA already exists")


class SLAPolicyAssignmentResponse(BaseModel):
    """Response for SLA policy assignment"""
    ticket_id: int
    policy_id: int
    sla_tracking_id: int
    message: str