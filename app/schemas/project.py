# app/schemas/project.py

"""
Project Management Schemas for comprehensive project lifecycle management
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectType(str, Enum):
    INTERNAL = "internal"
    CLIENT = "client"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"


class MilestoneStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


class ResourceType(str, Enum):
    HUMAN = "human"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    BUDGET = "budget"


# Base Schemas
class ProjectBase(BaseModel):
    project_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: ProjectType = ProjectType.INTERNAL
    priority: ProjectPriority = ProjectPriority.MEDIUM
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    budget: Optional[float] = Field(None, ge=0)
    client_id: Optional[int] = None
    project_manager_id: int
    is_billable: bool = False
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class ProjectCreate(ProjectBase):
    company_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    budget: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    client_id: Optional[int] = None
    project_manager_id: Optional[int] = None
    is_billable: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    status: ProjectStatus
    actual_cost: float
    progress_percentage: float
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ProjectWithDetails(ProjectResponse):
    client_name: Optional[str] = None
    project_manager_name: Optional[str] = None
    creator_name: Optional[str] = None
    total_milestones: int = 0
    completed_milestones: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    total_time_logged: float = 0  # in hours


# Milestone Schemas
class MilestoneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: date
    assigned_to: Optional[int] = None
    dependencies: Optional[List[int]] = None


class MilestoneCreate(MilestoneBase):
    project_id: int


class MilestoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[MilestoneStatus] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    assigned_to: Optional[int] = None
    dependencies: Optional[List[int]] = None


class MilestoneResponse(MilestoneBase):
    id: int
    organization_id: int
    project_id: int
    status: MilestoneStatus
    completion_date: Optional[date]
    progress_percentage: float
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MilestoneWithDetails(MilestoneResponse):
    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None
    dependent_milestones: Optional[List["MilestoneResponse"]] = None


# Resource Schemas
class ResourceBase(BaseModel):
    resource_type: ResourceType
    resource_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    allocated_quantity: float = Field(..., gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[float] = Field(None, ge=0)
    allocation_start_date: Optional[date] = None
    allocation_end_date: Optional[date] = None
    user_id: Optional[int] = None


class ResourceCreate(ResourceBase):
    project_id: int


class ResourceUpdate(BaseModel):
    resource_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    allocated_quantity: Optional[float] = Field(None, gt=0)
    used_quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[float] = Field(None, ge=0)
    total_cost: Optional[float] = Field(None, ge=0)
    allocation_start_date: Optional[date] = None
    allocation_end_date: Optional[date] = None
    user_id: Optional[int] = None


class ResourceResponse(ResourceBase):
    id: int
    organization_id: int
    project_id: int
    used_quantity: float
    total_cost: float
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceWithDetails(ResourceResponse):
    project_name: Optional[str] = None
    user_name: Optional[str] = None
    creator_name: Optional[str] = None
    utilization_percentage: Optional[float] = None


# Document Schemas
class DocumentBase(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    document_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    version: str = Field(default="1.0", max_length=20)
    is_public: bool = False
    tags: Optional[List[str]] = None


class DocumentCreate(DocumentBase):
    project_id: int


class DocumentUpdate(BaseModel):
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    document_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=20)
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class DocumentResponse(DocumentBase):
    id: int
    organization_id: int
    project_id: int
    file_path: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentWithDetails(DocumentResponse):
    project_name: Optional[str] = None
    uploader_name: Optional[str] = None
    download_url: Optional[str] = None


# Time Log Schemas
class TimeLogBase(BaseModel):
    description: str = Field(..., min_length=1)
    work_type: Optional[str] = Field(None, max_length=100)
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_billable: bool = True
    hourly_rate: Optional[float] = Field(None, ge=0)
    task_id: Optional[int] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v


class TimeLogCreate(TimeLogBase):
    project_id: int


class TimeLogUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    work_type: Optional[str] = Field(None, max_length=100)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_billable: Optional[bool] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    billable_amount: Optional[float] = Field(None, ge=0)
    task_id: Optional[int] = None


class TimeLogResponse(TimeLogBase):
    id: int
    organization_id: int
    project_id: int
    user_id: int
    billable_amount: Optional[float]
    is_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeLogWithDetails(TimeLogResponse):
    project_name: Optional[str] = None
    user_name: Optional[str] = None
    task_title: Optional[str] = None
    approver_name: Optional[str] = None


# Dashboard and Analytics Schemas
class ProjectDashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    overdue_projects: int
    total_budget: float
    actual_cost: float
    budget_utilization_percentage: float
    average_progress_percentage: float
    projects_by_status: Dict[str, int]
    projects_by_type: Dict[str, int]
    upcoming_milestones: List[MilestoneResponse]
    recent_activities: List[Dict[str, Any]]


class ProjectFilter(BaseModel):
    status: Optional[ProjectStatus] = None
    project_type: Optional[ProjectType] = None
    priority: Optional[ProjectPriority] = None
    project_manager_id: Optional[int] = None
    client_id: Optional[int] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    is_billable: Optional[bool] = None
    search: Optional[str] = None


class ProjectList(BaseModel):
    projects: List[ProjectWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


# Bulk Operations
class BulkProjectUpdate(BaseModel):
    project_ids: List[int] = Field(..., min_items=1)
    updates: ProjectUpdate


class ProjectStatusBulkUpdate(BaseModel):
    project_ids: List[int] = Field(..., min_items=1)
    status: ProjectStatus


class TimeLogApproval(BaseModel):
    time_log_ids: List[int] = Field(..., min_items=1)
    approved: bool = True
    comments: Optional[str] = None


# Export Schemas
class ProjectExportRequest(BaseModel):
    project_ids: Optional[List[int]] = None
    filters: Optional[ProjectFilter] = None
    include_milestones: bool = True
    include_tasks: bool = True
    include_time_logs: bool = True
    include_resources: bool = True
    include_documents: bool = False
    format: str = Field(default="excel", pattern="^(excel|csv|pdf)$")


# Update forward references
MilestoneWithDetails.model_rebuild()