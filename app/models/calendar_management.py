# app/models/calendar_management.py

"""
Calendar and Scheduler Models for task and appointment management
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date, time
from enum import Enum as PyEnum

from app.core.database import Base

class EventType(PyEnum):
    TASK = "task"
    APPOINTMENT = "appointment"
    MEETING = "meeting"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    PERSONAL = "personal"
    HOLIDAY = "holiday"

class RecurrenceType(PyEnum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class EventStatus(PyEnum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Event details
    event_type = Column(Enum(EventType), default=EventType.APPOINTMENT, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.SCHEDULED, nullable=False)
    
    # Timing
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False, index=True)
    all_day = Column(Boolean, default=False, nullable=False)
    timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    
    # Location and meeting details
    location = Column(String(255), nullable=True)
    meeting_url = Column(String(500), nullable=True)  # Video conference link
    meeting_id = Column(String(100), nullable=True)   # Meeting ID
    meeting_password = Column(String(100), nullable=True)
    
    # Recurrence
    recurrence_type = Column(Enum(RecurrenceType), default=RecurrenceType.NONE, nullable=False)
    recurrence_rule = Column(JSON, nullable=True)  # RRULE data for complex recurrence
    recurrence_end_date = Column(Date, nullable=True)
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Linked entities
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # Link to task
    
    # Additional fields
    color = Column(String(7), nullable=True)  # Hex color code
    is_private = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    
    # Google Calendar integration
    google_event_id = Column(String(255), nullable=True, index=True)
    google_calendar_id = Column(String(255), nullable=True)
    last_google_sync = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="calendar_events")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_events")
    task = relationship("Task", back_populates="calendar_events")
    attendees = relationship("EventAttendee", back_populates="event", cascade="all, delete-orphan")
    reminders = relationship("EventReminder", back_populates="event", cascade="all, delete-orphan")

class EventAttendee(Base):
    __tablename__ = "event_attendees"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Internal user
    
    # External attendee details (for non-users)
    external_email = Column(String(255), nullable=True)
    external_name = Column(String(255), nullable=True)
    
    # Attendance details
    response_status = Column(String(20), default="pending", nullable=False)  # pending, accepted, declined, tentative
    is_organizer = Column(Boolean, default=False, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    
    # Response tracking
    responded_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="attendees")
    user = relationship("User", back_populates="event_attendances")

class EventReminder(Base):
    __tablename__ = "event_reminders"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Reminder settings
    remind_before_minutes = Column(Integer, nullable=False)  # Minutes before event
    reminder_type = Column(String(20), default="notification", nullable=False)  # notification, email, sms
    message = Column(String(500), nullable=True)
    
    # Status
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="reminders")
    user = relationship("User", back_populates="event_reminders")

class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Calendar settings
    is_default = Column(Boolean, default=False, nullable=False)
    is_shared = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    
    # Relations
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Calendar integration
    google_calendar_id = Column(String(255), nullable=True, unique=True)
    is_google_calendar = Column(Boolean, default=False, nullable=False)
    google_sync_enabled = Column(Boolean, default=False, nullable=False)
    last_google_sync = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="calendars")
    owner = relationship("User", back_populates="owned_calendars")
    shares = relationship("CalendarShare", back_populates="calendar", cascade="all, delete-orphan")

class CalendarShare(Base):
    __tablename__ = "calendar_shares"

    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permission levels
    permission = Column(String(20), default="view", nullable=False)  # view, edit, admin
    can_create_events = Column(Boolean, default=False, nullable=False)
    can_edit_events = Column(Boolean, default=False, nullable=False)
    can_delete_events = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    shared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    calendar = relationship("Calendar", back_populates="shares")
    user = relationship("User", foreign_keys=[user_id], back_populates="calendar_shares")
    sharer = relationship("User", foreign_keys=[shared_by])

class GoogleCalendarIntegration(Base):
    __tablename__ = "google_calendar_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Google OAuth details
    google_email = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_direction = Column(String(20), default="bidirectional", nullable=False)  # import_only, export_only, bidirectional
    sync_calendar_ids = Column(JSON, nullable=True)  # Array of Google calendar IDs to sync
    
    # Sync status
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(20), default="pending", nullable=False)  # success, error, pending
    last_sync_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="google_calendar_integration")
    organization = relationship("Organization", back_populates="google_calendar_integrations")