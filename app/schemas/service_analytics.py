# app/schemas/service_analytics.py

"""
Pydantic schemas for Service Analytics API endpoints
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class MetricType(str, Enum):
    """Types of analytics metrics"""
    JOB_COMPLETION = "job_completion"
    TECHNICIAN_PERFORMANCE = "technician_performance"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    JOB_VOLUME = "job_volume"
    SLA_COMPLIANCE = "sla_compliance"


class ReportPeriod(str, Enum):
    """Report time periods"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


class JobStatus(str, Enum):
    """Job completion statuses"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


# Request Models
class AnalyticsRequest(BaseModel):
    """Base request for analytics data"""
    start_date: Optional[datetime.date] = Field(None, description="Start date for analytics period")
    end_date: Optional[datetime.date] = Field(None, description="End date for analytics period")
    period: Optional[ReportPeriod] = Field(ReportPeriod.MONTH, description="Predefined period")
    technician_id: Optional[int] = Field(None, description="Filter by specific technician")
    customer_id: Optional[int] = Field(None, description="Filter by specific customer")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ReportConfigurationRequest(BaseModel):
    """Request for creating/updating report configurations"""
    name: str = Field(..., description="Report configuration name")
    description: Optional[str] = Field(None, description="Report description")
    metric_types: List[MetricType] = Field(..., description="Types of metrics to include")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Default filters")
    schedule_enabled: bool = Field(False, description="Enable scheduled generation")
    schedule_frequency: Optional[str] = Field(None, description="Schedule frequency (daily, weekly, monthly)")
    email_recipient: List[str] = Field(default_factory=list, description="Email recipients for scheduled reports")
    is_active: bool = Field(True, description="Whether configuration is active")


# Response Models
class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series"""
    date: datetime.date = Field(..., description="Date of the data point")
    value: Union[int, float] = Field(..., description="Metric value")
    label: Optional[str] = Field(None, description="Optional label for the data point")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JobCompletionMetrics(BaseModel):
    """Job completion analytics"""
    total_jobs: int = Field(..., description="Total number of jobs")
    completed_jobs: int = Field(..., description="Number of completed jobs")
    pending_jobs: int = Field(..., description="Number of pending jobs")
    cancelled_jobs: int = Field(..., description="Number of cancelled jobs")
    completion_rate: float = Field(..., description="Job completion rate as percentage")
    average_completion_time_hours: Optional[float] = Field(None, description="Average completion time in hours")
    on_time_completion_rate: float = Field(..., description="On-time completion rate as percentage")
    jobs_by_status: Dict[str, int] = Field(default_factory=dict, description="Job count by status")
    completion_trend: List[TimeSeriesDataPoint] = Field(default_factory=list, description="Completion trend over time")


class TechnicianPerformanceMetrics(BaseModel):
    """Individual technician performance metrics"""
    technician_id: int = Field(..., description="Technician ID")
    technician_name: str = Field(..., description="Technician name")
    total_jobs_assigned: int = Field(..., description="Total jobs assigned")
    jobs_completed: int = Field(..., description="Jobs completed")
    jobs_in_progress: int = Field(..., description="Jobs currently in progress")
    average_completion_time_hours: Optional[float] = Field(None, description="Average completion time")
    customer_rating_average: Optional[float] = Field(None, description="Average customer rating")
    utilization_rate: float = Field(..., description="Technician utilization rate as percentage")
    efficiency_score: float = Field(..., description="Efficiency score based on multiple factors")


class CustomerSatisfactionMetrics(BaseModel):
    """Customer satisfaction analytics"""
    total_feedback_received: int = Field(..., description="Total feedback responses")
    average_overall_rating: float = Field(..., description="Average overall rating")
    average_service_quality: Optional[float] = Field(None, description="Average service quality rating")
    average_technician_rating: Optional[float] = Field(None, description="Average technician rating")
    average_timeliness_rating: Optional[float] = Field(None, description="Average timeliness rating")
    average_communication_rating: Optional[float] = Field(None, description="Average communication rating")
    satisfaction_distribution: Dict[str, int] = Field(default_factory=dict, description="Rating distribution")
    nps_score: Optional[float] = Field(None, description="Net Promoter Score")
    recommendation_rate: Optional[float] = Field(None, description="Percentage who would recommend")
    satisfaction_trend: List[TimeSeriesDataPoint] = Field(default_factory=list, description="Satisfaction trend over time")


class JobVolumeMetrics(BaseModel):
    """Job volume analytics"""
    total_jobs: int = Field(..., description="Total number of jobs")
    jobs_per_day_average: float = Field(..., description="Average jobs per day")
    peak_day: Optional[datetime.date] = Field(None, description="Day with highest job volume")
    peak_day_count: int = Field(0, description="Job count on peak day")
    volume_trend: List[TimeSeriesDataPoint] = Field(default_factory=list, description="Job volume trend over time")
    jobs_by_priority: Dict[str, int] = Field(default_factory=dict, description="Job distribution by priority")
    jobs_by_customer: List[Dict[str, Any]] = Field(default_factory=list, description="Top customers by job volume")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SLAComplianceMetrics(BaseModel):
    """SLA compliance analytics"""
    total_jobs_with_sla: int = Field(..., description="Total jobs with SLA requirements")
    sla_met_count: int = Field(..., description="Number of jobs meeting SLA")
    sla_breached_count: int = Field(..., description="Number of jobs breaching SLA")
    overall_compliance_rate: float = Field(..., description="Overall SLA compliance rate as percentage")
    average_resolution_time_hours: Optional[float] = Field(None, description="Average resolution time")
    compliance_by_priority: Dict[str, float] = Field(default_factory=dict, description="Compliance rate by priority")
    compliance_trend: List[TimeSeriesDataPoint] = Field(default_factory=list, description="Compliance trend over time")
    breach_reasons: Dict[str, int] = Field(default_factory=dict, description="Common reasons for SLA breaches")


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data"""
    organization_id: int = Field(..., description="Organization ID")
    report_period: ReportPeriod = Field(..., description="Report period")
    start_date: datetime.date = Field(..., description="Report start date")
    end_date: datetime.date = Field(..., description="Report end date")
    job_completion: JobCompletionMetrics = Field(..., description="Job completion metrics")
    technician_performance: List[TechnicianPerformanceMetrics] = Field(default_factory=list, description="Technician performance data")
    customer_satisfaction: CustomerSatisfactionMetrics = Field(..., description="Customer satisfaction metrics")
    job_volume: JobVolumeMetrics = Field(..., description="Job volume metrics")
    sla_compliance: SLAComplianceMetrics = Field(..., description="SLA compliance metrics")
    generated_at: datetime = Field(..., description="Timestamp when dashboard was generated")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ReportConfiguration(BaseModel):
    """Report configuration details"""
    id: int = Field(..., description="Configuration ID")
    organization_id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    metric_types: List[MetricType] = Field(..., description="Metric types included")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Default filters")
    schedule_enabled: bool = Field(..., description="Whether scheduled generation is enabled")
    schedule_frequency: Optional[str] = Field(None, description="Schedule frequency")
    email_recipients: List[str] = Field(default_factory=list, description="Email recipients")
    is_active: bool = Field(..., description="Whether configuration is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    """Request for exporting analytics data"""
    format: str = Field("csv", description="Export format (csv, excel)")
    metric_types: List[MetricType] = Field(..., description="Metrics to export")
    filters: AnalyticsRequest = Field(..., description="Filters to apply")
    include_raw_data: bool = Field(False, description="Include raw data in export")


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