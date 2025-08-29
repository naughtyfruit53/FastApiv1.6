# app/schemas/task_schemas.py

"""
Pydantic schemas for Task Management system
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Base schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.NORMAL
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    project_id: Optional[int]
    created_by: int
    assigned_to: Optional[int]
    actual_hours: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class TaskWithDetails(TaskResponse):
    # Relations
    creator: Optional[Dict[str, Any]] = None
    assignee: Optional[Dict[str, Any]] = None
    project: Optional[Dict[str, Any]] = None
    comments_count: int = 0
    attachments_count: int = 0
    time_logs_count: int = 0

# Task Project schemas
class TaskProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')

class TaskProjectCreate(TaskProjectBase):
    pass

class TaskProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')

class TaskProjectResponse(TaskProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

class TaskProjectWithDetails(TaskProjectResponse):
    creator: Optional[Dict[str, Any]] = None
    tasks_count: int = 0
    members_count: int = 0
    tasks: Optional[List[TaskResponse]] = None
    members: Optional[List[Dict[str, Any]]] = None

# Task Project Member schemas
class TaskProjectMemberBase(BaseModel):
    role: str = Field(default="member", regex=r'^(member|admin|viewer)$')

class TaskProjectMemberCreate(TaskProjectMemberBase):
    user_id: int

class TaskProjectMemberUpdate(BaseModel):
    role: Optional[str] = Field(None, regex=r'^(member|admin|viewer)$')

class TaskProjectMemberResponse(TaskProjectMemberBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    user_id: int
    added_at: datetime

class TaskProjectMemberWithDetails(TaskProjectMemberResponse):
    user: Optional[Dict[str, Any]] = None
    project: Optional[Dict[str, Any]] = None

# Task Comment schemas
class TaskCommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class TaskCommentCreate(TaskCommentBase):
    pass

class TaskCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class TaskCommentResponse(TaskCommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class TaskCommentWithDetails(TaskCommentResponse):
    user: Optional[Dict[str, Any]] = None

# Task Attachment schemas
class TaskAttachmentBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)

class TaskAttachmentCreate(TaskAttachmentBase):
    pass

class TaskAttachmentResponse(TaskAttachmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_at: datetime

class TaskAttachmentWithDetails(TaskAttachmentResponse):
    user: Optional[Dict[str, Any]] = None

# Task Time Log schemas
class TaskTimeLogBase(BaseModel):
    description: Optional[str] = Field(None, max_length=255)
    hours: int = Field(..., ge=1)  # Minutes
    work_date: datetime

class TaskTimeLogCreate(TaskTimeLogBase):
    pass

class TaskTimeLogUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=255)
    hours: Optional[int] = Field(None, ge=1)
    work_date: Optional[datetime] = None

class TaskTimeLogResponse(TaskTimeLogBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    logged_at: datetime

class TaskTimeLogWithDetails(TaskTimeLogResponse):
    user: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None

# Task Reminder schemas
class TaskReminderBase(BaseModel):
    remind_at: datetime
    message: Optional[str] = Field(None, max_length=255)

class TaskReminderCreate(TaskReminderBase):
    user_id: Optional[int] = None  # If None, remind task assignee

class TaskReminderUpdate(BaseModel):
    remind_at: Optional[datetime] = None
    message: Optional[str] = Field(None, max_length=255)

class TaskReminderResponse(TaskReminderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

class TaskReminderWithDetails(TaskReminderResponse):
    user: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None

# Dashboard and analytics schemas
class TaskDashboardStats(BaseModel):
    total_tasks: int = 0
    todo_tasks: int = 0
    in_progress_tasks: int = 0
    review_tasks: int = 0
    done_tasks: int = 0
    cancelled_tasks: int = 0
    overdue_tasks: int = 0
    due_today_tasks: int = 0
    due_this_week_tasks: int = 0
    assigned_to_me: int = 0
    created_by_me: int = 0

class TaskFilter(BaseModel):
    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    assigned_to: Optional[List[int]] = None
    created_by: Optional[List[int]] = None
    project_id: Optional[List[int]] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None

class TaskList(BaseModel):
    tasks: List[TaskWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int