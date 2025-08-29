# app/schemas/calendar_schemas.py

"""
Pydantic schemas for Calendar and Scheduler system
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class EventType(str, Enum):
    TASK = "task"
    APPOINTMENT = "appointment"
    MEETING = "meeting"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    PERSONAL = "personal"
    HOLIDAY = "holiday"

class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

# Calendar Event schemas
class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: EventType = EventType.APPOINTMENT
    status: EventStatus = EventStatus.SCHEDULED
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool = False
    timezone: str = "Asia/Kolkata"
    location: Optional[str] = Field(None, max_length=255)
    meeting_url: Optional[str] = Field(None, max_length=500)
    meeting_id: Optional[str] = Field(None, max_length=100)
    meeting_password: Optional[str] = Field(None, max_length=100)
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_rule: Optional[Dict[str, Any]] = None
    recurrence_end_date: Optional[date] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_private: bool = False
    priority: str = Field(default="normal", regex=r'^(low|normal|high|urgent)$')
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class CalendarEventCreate(CalendarEventBase):
    task_id: Optional[int] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    all_day: Optional[bool] = None
    timezone: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    meeting_url: Optional[str] = Field(None, max_length=500)
    meeting_id: Optional[str] = Field(None, max_length=100)
    meeting_password: Optional[str] = Field(None, max_length=100)
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_rule: Optional[Dict[str, Any]] = None
    recurrence_end_date: Optional[date] = None
    task_id: Optional[int] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_private: Optional[bool] = None
    priority: Optional[str] = Field(None, regex=r'^(low|normal|high|urgent)$')
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class CalendarEventResponse(CalendarEventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by: int
    task_id: Optional[int]
    google_event_id: Optional[str]
    google_calendar_id: Optional[str]
    last_google_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class CalendarEventWithDetails(CalendarEventResponse):
    creator: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None
    attendees: Optional[List[Dict[str, Any]]] = None
    reminders: Optional[List[Dict[str, Any]]] = None

# Event Attendee schemas
class EventAttendeeBase(BaseModel):
    external_email: Optional[str] = Field(None, max_length=255)
    external_name: Optional[str] = Field(None, max_length=255)
    response_status: str = Field(default="pending", regex=r'^(pending|accepted|declined|tentative)$')
    is_organizer: bool = False
    is_required: bool = True
    notes: Optional[str] = None

class EventAttendeeCreate(EventAttendeeBase):
    user_id: Optional[int] = None  # For internal users

class EventAttendeeUpdate(BaseModel):
    response_status: Optional[str] = Field(None, regex=r'^(pending|accepted|declined|tentative)$')
    notes: Optional[str] = None

class EventAttendeeResponse(EventAttendeeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    event_id: int
    user_id: Optional[int]
    responded_at: Optional[datetime]
    created_at: datetime

class EventAttendeeWithDetails(EventAttendeeResponse):
    user: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None

# Event Reminder schemas
class EventReminderBase(BaseModel):
    remind_before_minutes: int = Field(..., ge=1)
    reminder_type: str = Field(default="notification", regex=r'^(notification|email|sms)$')
    message: Optional[str] = Field(None, max_length=500)

class EventReminderCreate(EventReminderBase):
    user_id: Optional[int] = None  # If None, remind event creator

class EventReminderUpdate(BaseModel):
    remind_before_minutes: Optional[int] = Field(None, ge=1)
    reminder_type: Optional[str] = Field(None, regex=r'^(notification|email|sms)$')
    message: Optional[str] = Field(None, max_length=500)

class EventReminderResponse(EventReminderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    event_id: int
    user_id: int
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

class EventReminderWithDetails(EventReminderResponse):
    user: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None

# Calendar schemas
class CalendarBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_default: bool = False
    is_shared: bool = False
    is_visible: bool = True

class CalendarCreate(CalendarBase):
    pass

class CalendarUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    is_default: Optional[bool] = None
    is_shared: Optional[bool] = None
    is_visible: Optional[bool] = None

class CalendarResponse(CalendarBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    owner_id: int
    google_calendar_id: Optional[str]
    is_google_calendar: bool
    google_sync_enabled: bool
    last_google_sync: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class CalendarWithDetails(CalendarResponse):
    owner: Optional[Dict[str, Any]] = None
    shares: Optional[List[Dict[str, Any]]] = None
    events_count: int = 0

# Calendar Share schemas
class CalendarShareBase(BaseModel):
    permission: str = Field(default="view", regex=r'^(view|edit|admin)$')
    can_create_events: bool = False
    can_edit_events: bool = False
    can_delete_events: bool = False

class CalendarShareCreate(CalendarShareBase):
    user_id: int

class CalendarShareUpdate(BaseModel):
    permission: Optional[str] = Field(None, regex=r'^(view|edit|admin)$')
    can_create_events: Optional[bool] = None
    can_edit_events: Optional[bool] = None
    can_delete_events: Optional[bool] = None

class CalendarShareResponse(CalendarShareBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    calendar_id: int
    user_id: int
    shared_at: datetime
    shared_by: int

class CalendarShareWithDetails(CalendarShareResponse):
    user: Optional[Dict[str, Any]] = None
    calendar: Optional[Dict[str, Any]] = None
    sharer: Optional[Dict[str, Any]] = None

# Google Calendar Integration schemas
class GoogleCalendarIntegrationBase(BaseModel):
    google_email: str = Field(..., max_length=255)
    sync_enabled: bool = True
    sync_direction: str = Field(default="bidirectional", regex=r'^(import_only|export_only|bidirectional)$')
    sync_calendar_ids: Optional[List[str]] = None

class GoogleCalendarIntegrationCreate(GoogleCalendarIntegrationBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

class GoogleCalendarIntegrationUpdate(BaseModel):
    sync_enabled: Optional[bool] = None
    sync_direction: Optional[str] = Field(None, regex=r'^(import_only|export_only|bidirectional)$')
    sync_calendar_ids: Optional[List[str]] = None

class GoogleCalendarIntegrationResponse(GoogleCalendarIntegrationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    organization_id: int
    token_expires_at: Optional[datetime]
    last_sync_at: Optional[datetime]
    last_sync_status: str
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime

class GoogleCalendarIntegrationWithDetails(GoogleCalendarIntegrationResponse):
    user: Optional[Dict[str, Any]] = None

# Dashboard and analytics schemas
class CalendarDashboardStats(BaseModel):
    total_events: int = 0
    today_events: int = 0
    this_week_events: int = 0
    this_month_events: int = 0
    upcoming_events: int = 0
    overdue_events: int = 0
    my_events: int = 0
    shared_events: int = 0

class CalendarFilter(BaseModel):
    event_type: Optional[List[EventType]] = None
    status: Optional[List[EventStatus]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    calendar_ids: Optional[List[int]] = None
    created_by: Optional[List[int]] = None
    search: Optional[str] = None

class CalendarEventList(BaseModel):
    events: List[CalendarEventWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int

# Calendar view schemas
class CalendarViewRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    calendar_ids: Optional[List[int]] = None
    view_type: str = Field(default="month", regex=r'^(day|week|month|year)$')

class CalendarViewResponse(BaseModel):
    events: List[CalendarEventWithDetails]
    start_date: datetime
    end_date: datetime
    view_type: str