# app/schemas/dispatch.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.base import BaseSchema


class DispatchOrderStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class DispatchItemStatus(str, Enum):
    PENDING = "pending"
    PACKED = "packed"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"


class InstallationJobStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class InstallationJobPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# DispatchItem Schemas
class DispatchItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0, description="Quantity must be greater than 0")
    unit: str
    description: Optional[str] = None
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    status: DispatchItemStatus = DispatchItemStatus.PENDING


class DispatchItemCreate(DispatchItemBase):
    pass


class DispatchItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[float] = Field(None, gt=0, description="Quantity must be greater than 0")
    unit: Optional[str] = None
    description: Optional[str] = None
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    status: Optional[DispatchItemStatus] = None


class DispatchItemInDB(DispatchItemBase, BaseSchema):
    dispatch_order_id: int
    
    class Config:
        from_attributes = True


# DispatchOrder Schemas
class DispatchOrderBase(BaseModel):
    customer_id: int
    ticket_id: Optional[int] = None
    status: DispatchOrderStatus = DispatchOrderStatus.PENDING
    dispatch_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    delivery_address: str
    delivery_contact_person: Optional[str] = None
    delivery_contact_number: Optional[str] = None
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_name: Optional[str] = None


class DispatchOrderCreate(DispatchOrderBase):
    items: List[DispatchItemCreate] = []

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
        return v


class DispatchOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    status: Optional[DispatchOrderStatus] = None
    dispatch_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_contact_person: Optional[str] = None
    delivery_contact_number: Optional[str] = None
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_name: Optional[str] = None


class DispatchOrderInDB(DispatchOrderBase, BaseSchema):
    order_number: str
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    items: List[DispatchItemInDB] = []
    
    class Config:
        from_attributes = True


# InstallationJob Schemas
class InstallationJobBase(BaseModel):
    customer_id: int
    ticket_id: Optional[int] = None
    status: InstallationJobStatus = InstallationJobStatus.SCHEDULED
    priority: InstallationJobPriority = InstallationJobPriority.MEDIUM
    scheduled_date: Optional[datetime] = None
    estimated_duration_hours: Optional[float] = Field(None, gt=0, description="Duration must be greater than 0")
    installation_address: str
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    installation_notes: Optional[str] = None
    assigned_technician_id: Optional[int] = None


class InstallationJobCreate(InstallationJobBase):
    dispatch_order_id: int


class InstallationJobUpdate(BaseModel):
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    status: Optional[InstallationJobStatus] = None
    priority: Optional[InstallationJobPriority] = None
    scheduled_date: Optional[datetime] = None
    estimated_duration_hours: Optional[float] = Field(None, gt=0, description="Duration must be greater than 0")
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    installation_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    installation_notes: Optional[str] = None
    completion_notes: Optional[str] = None
    customer_feedback: Optional[str] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")
    assigned_technician_id: Optional[int] = None


class InstallationJobInDB(InstallationJobBase, BaseSchema):
    job_number: str
    dispatch_order_id: int
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    completion_notes: Optional[str] = None
    customer_feedback: Optional[str] = None
    customer_rating: Optional[int] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Installation Schedule Prompt Response
class InstallationSchedulePromptResponse(BaseModel):
    create_installation_schedule: bool
    installation_job: Optional[InstallationJobCreate] = None

    @validator('installation_job')
    def validate_installation_job(cls, v, values):
        if values.get('create_installation_schedule') and not v:
            raise ValueError('Installation job details required when creating schedule')
        return v


# List/Filter Schemas
class DispatchOrderFilter(BaseModel):
    status: Optional[DispatchOrderStatus] = None
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class InstallationJobFilter(BaseModel):
    status: Optional[InstallationJobStatus] = None
    priority: Optional[InstallationJobPriority] = None
    customer_id: Optional[int] = None
    assigned_technician_id: Optional[int] = None
    dispatch_order_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


# Installation Task Enums and Schemas
class InstallationTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class InstallationTaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class InstallationTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: InstallationTaskStatus = InstallationTaskStatus.PENDING
    priority: InstallationTaskPriority = InstallationTaskPriority.MEDIUM
    estimated_duration_minutes: Optional[int] = Field(None, gt=0, description="Duration must be greater than 0")
    sequence_order: int = Field(1, ge=1, description="Sequence order must be >= 1")
    assigned_technician_id: Optional[int] = None
    work_notes: Optional[str] = None
    completion_notes: Optional[str] = None
    depends_on_task_id: Optional[int] = None


class InstallationTaskCreate(InstallationTaskBase):
    installation_job_id: int


class InstallationTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InstallationTaskStatus] = None
    priority: Optional[InstallationTaskPriority] = None
    estimated_duration_minutes: Optional[int] = Field(None, gt=0, description="Duration must be greater than 0")
    sequence_order: Optional[int] = Field(None, ge=1, description="Sequence order must be >= 1")
    assigned_technician_id: Optional[int] = None
    work_notes: Optional[str] = None
    completion_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    depends_on_task_id: Optional[int] = None


class InstallationTaskInDB(InstallationTaskBase, BaseSchema):
    task_number: str
    installation_job_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Completion Record Enums and Schemas
class CompletionStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


class CompletionRecordBase(BaseModel):
    completion_status: CompletionStatus = CompletionStatus.PENDING
    completion_date: datetime
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    work_performed: str = Field(..., description="Required completion notes")
    issues_encountered: Optional[str] = None
    resolution_notes: Optional[str] = None
    materials_used: Optional[str] = None
    parts_replaced: Optional[str] = None
    quality_check_passed: bool = False
    verification_notes: Optional[str] = None
    photos_attached: bool = False
    customer_present: bool = True
    customer_signature_received: bool = False
    customer_feedback_notes: Optional[str] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class CompletionRecordCreate(CompletionRecordBase):
    installation_job_id: int


class CompletionRecordUpdate(BaseModel):
    completion_status: Optional[CompletionStatus] = None
    completion_date: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    work_performed: Optional[str] = None
    issues_encountered: Optional[str] = None
    resolution_notes: Optional[str] = None
    materials_used: Optional[str] = None
    parts_replaced: Optional[str] = None
    quality_check_passed: Optional[bool] = None
    verification_notes: Optional[str] = None
    photos_attached: Optional[bool] = None
    customer_present: Optional[bool] = None
    customer_signature_received: Optional[bool] = None
    customer_feedback_notes: Optional[str] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None


class CompletionRecordInDB(CompletionRecordBase, BaseSchema):
    installation_job_id: int
    completed_by_id: int
    total_duration_minutes: Optional[int] = None
    feedback_request_sent: bool = False
    feedback_request_sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Enhanced Installation Job with Tasks and Completion
class InstallationJobWithDetails(InstallationJobInDB):
    tasks: List[InstallationTaskInDB] = []
    completion_record: Optional[CompletionRecordInDB] = None
    
    class Config:
        from_attributes = True


# Filter schemas for new models
class InstallationTaskFilter(BaseModel):
    status: Optional[InstallationTaskStatus] = None
    priority: Optional[InstallationTaskPriority] = None
    installation_job_id: Optional[int] = None
    assigned_technician_id: Optional[int] = None


class CompletionRecordFilter(BaseModel):
    completion_status: Optional[CompletionStatus] = None
    completed_by_id: Optional[int] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5)
    follow_up_required: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None