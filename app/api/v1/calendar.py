# app/api/v1/calendar.py

"""
Calendar and Scheduler API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user  # Fixed import to use get_current_active_user as get_current_user
from app.models import User, Organization, CalendarEvent, EventAttendee, EventReminder, Calendar, CalendarShare, GoogleCalendarIntegration
from app.schemas.calendar_schemas import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse, CalendarEventWithDetails,
    CalendarEventList, CalendarFilter, CalendarDashboardStats, CalendarViewRequest, CalendarViewResponse,
    EventAttendeeCreate, EventAttendeeUpdate, EventAttendeeResponse, EventAttendeeWithDetails,
    EventReminderCreate, EventReminderUpdate, EventReminderResponse, EventReminderWithDetails,
    CalendarCreate, CalendarUpdate, CalendarResponse, CalendarWithDetails,
    CalendarShareCreate, CalendarShareUpdate, CalendarShareResponse, CalendarShareWithDetails,
    GoogleCalendarIntegrationCreate, GoogleCalendarIntegrationUpdate, GoogleCalendarIntegrationResponse
)

router = APIRouter()

# Calendar Dashboard
@router.get("/dashboard", response_model=CalendarDashboardStats)
async def get_calendar_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar dashboard statistics for current user's organization"""
    org_id = current_user.organization_id
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)
    month_end = today_start + timedelta(days=30)
    
    # Base query for user's organization
    base_query = db.query(CalendarEvent).filter(CalendarEvent.organization_id == org_id)
    
    # Total events
    total_events = base_query.count()
    
    # Today's events
    today_events = base_query.filter(
        and_(
            CalendarEvent.start_datetime >= today_start,
            CalendarEvent.start_datetime < today_end
        )
    ).count()
    
    # This week's events
    this_week_events = base_query.filter(
        and_(
            CalendarEvent.start_datetime >= today_start,
            CalendarEvent.start_datetime < week_end
        )
    ).count()
    
    # This month's events
    this_month_events = base_query.filter(
        and_(
            CalendarEvent.start_datetime >= today_start,
            CalendarEvent.start_datetime < month_end
        )
    ).count()
    
    # Upcoming events (future events)
    upcoming_events = base_query.filter(
        CalendarEvent.start_datetime > now
    ).count()
    
    # Overdue events (past events that are not completed)
    overdue_events = base_query.filter(
        and_(
            CalendarEvent.end_datetime < now,
            CalendarEvent.status.notin_(["completed", "cancelled"])
        )
    ).count()
    
    # My events (created by or attending)
    attendee_subquery = db.query(EventAttendee.event_id).filter(
        EventAttendee.user_id == current_user.id
    ).subquery()
    
    my_events = base_query.filter(
        or_(
            CalendarEvent.created_by == current_user.id,
            CalendarEvent.id.in_(attendee_subquery)
        )
    ).count()
    
    # Shared events (events in shared calendars)
    shared_calendar_subquery = db.query(CalendarShare.calendar_id).filter(
        CalendarShare.user_id == current_user.id
    ).subquery()
    
    shared_events = base_query.join(Calendar).filter(
        Calendar.id.in_(shared_calendar_subquery)
    ).count()
    
    return CalendarDashboardStats(
        total_events=total_events,
        today_events=today_events,
        this_week_events=this_week_events,
        this_month_events=this_month_events,
        upcoming_events=upcoming_events,
        overdue_events=overdue_events,
        my_events=my_events,
        shared_events=shared_events
    )

# Calendar Events
@router.get("/events", response_model=CalendarEventList)
async def get_calendar_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    event_type: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    calendar_ids: Optional[List[int]] = Query(None),
    created_by: Optional[List[int]] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("start_datetime", regex=r"^(start_datetime|created_at|title|priority)$"),
    sort_order: str = Query("asc", regex=r"^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of calendar events with filtering and sorting"""
    org_id = current_user.organization_id
    
    # Base query with eager loading
    query = db.query(CalendarEvent).filter(CalendarEvent.organization_id == org_id).options(
        joinedload(CalendarEvent.creator),
        joinedload(CalendarEvent.task),
        joinedload(CalendarEvent.attendees),
        joinedload(CalendarEvent.reminders)
    )
    
    # Apply filters
    if start_date:
        query = query.filter(CalendarEvent.start_datetime >= start_date)
    
    if end_date:
        query = query.filter(CalendarEvent.end_datetime <= end_date)
    
    if event_type:
        query = query.filter(CalendarEvent.event_type.in_(event_type))
    
    if status:
        query = query.filter(CalendarEvent.status.in_(status))
    
    if created_by:
        query = query.filter(CalendarEvent.created_by.in_(created_by))
    
    if search:
        search_filter = or_(
            CalendarEvent.title.contains(search),
            CalendarEvent.description.contains(search),
            CalendarEvent.location.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    sort_column = getattr(CalendarEvent, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    # Convert to response models with details
    event_details = []
    for event in events:
        event_dict = {
            **event.__dict__,
            "creator": {"id": event.creator.id, "full_name": event.creator.full_name} if event.creator else None,
            "task": {"id": event.task.id, "title": event.task.title} if event.task else None,
            "attendees": [
                {
                    "id": attendee.id,
                    "user_id": attendee.user_id,
                    "external_email": attendee.external_email,
                    "external_name": attendee.external_name,
                    "response_status": attendee.response_status,
                    "is_organizer": attendee.is_organizer
                }
                for attendee in event.attendees
            ] if event.attendees else [],
            "reminders": [
                {
                    "id": reminder.id,
                    "remind_before_minutes": reminder.remind_before_minutes,
                    "reminder_type": reminder.reminder_type,
                    "is_sent": reminder.is_sent
                }
                for reminder in event.reminders
            ] if event.reminders else []
        }
        event_details.append(CalendarEventWithDetails(**event_dict))
    
    return CalendarEventList(
        events=event_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.post("/events", response_model=CalendarEventResponse)
async def create_calendar_event(
    event_data: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar event"""
    # Validate end time is after start time
    if event_data.end_datetime <= event_data.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Verify task exists in same organization if provided
    if event_data.task_id:
        task = db.query(Task).filter(
            and_(
                Task.id == event_data.task_id,
                Task.organization_id == current_user.organization_id
            )
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in your organization"
            )
    
    # Create event
    event = CalendarEvent(
        **event_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by=current_user.id
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return CalendarEventResponse.model_validate(event)

@router.get("/events/{event_id}", response_model=CalendarEventWithDetails)
async def get_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific calendar event by ID"""
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.organization_id == current_user.organization_id
        )
    ).options(
        joinedload(CalendarEvent.creator),
        joinedload(CalendarEvent.task),
        joinedload(CalendarEvent.attendees).joinedload(EventAttendee.user),
        joinedload(CalendarEvent.reminders).joinedload(EventReminder.user)
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    
    # Convert to response model with details
    event_dict = {
        **event.__dict__,
        "creator": {"id": event.creator.id, "full_name": event.creator.full_name} if event.creator else None,
        "task": {"id": event.task.id, "title": event.task.title} if event.task else None,
        "attendees": [
            {
                "id": attendee.id,
                "user_id": attendee.user_id,
                "external_email": attendee.external_email,
                "external_name": attendee.external_name,
                "response_status": attendee.response_status,
                "is_organizer": attendee.is_organizer,
                "user": {"id": attendee.user.id, "full_name": attendee.user.full_name} if attendee.user else None
            }
            for attendee in event.attendees
        ] if event.attendees else [],
        "reminders": [
            {
                "id": reminder.id,
                "remind_before_minutes": reminder.remind_before_minutes,
                "reminder_type": reminder.reminder_type,
                "is_sent": reminder.is_sent,
                "user": {"id": reminder.user.id, "full_name": reminder.user.full_name} if reminder.user else None
            }
            for reminder in event.reminders
        ] if event.reminders else []
    }
    
    return CalendarEventWithDetails(**event_dict)

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a calendar event"""
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.organization_id == current_user.organization_id
        )
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    
    # Check if user can edit (creator or has calendar permissions)
    if event.created_by != current_user.id and current_user.role not in ["org_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this event"
        )
    
    # Validate end time is after start time if both are provided
    update_data = event_data.model_dump(exclude_unset=True)
    start_time = update_data.get("start_datetime", event.start_datetime)
    end_time = update_data.get("end_datetime", event.end_datetime)
    
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Verify task exists in same organization if provided
    if "task_id" in update_data and update_data["task_id"]:
        task = db.query(Task).filter(
            and_(
                Task.id == update_data["task_id"],
                Task.organization_id == current_user.organization_id
            )
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found in your organization"
            )
    
    # Update event fields
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return CalendarEventResponse.model_validate(event)

@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar event"""
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.organization_id == current_user.organization_id
        )
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    
    # Check if user can delete (creator or admin)
    if event.created_by != current_user.id and current_user.role not in ["org_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this event"
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": "Calendar event deleted successfully"}

# Calendar view endpoint
@router.post("/view", response_model=CalendarViewResponse)
async def get_calendar_view(
    view_request: CalendarViewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events for a specific view (day, week, month, year)"""
    org_id = current_user.organization_id
    
    # Query events in the specified date range
    query = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.organization_id == org_id,
            CalendarEvent.start_datetime >= view_request.start_date,
            CalendarEvent.start_datetime <= view_request.end_date
        )
    ).options(
        joinedload(CalendarEvent.creator),
        joinedload(CalendarEvent.task),
        joinedload(CalendarEvent.attendees),
        joinedload(CalendarEvent.reminders)
    )
    
    # Filter by calendar IDs if provided
    if view_request.calendar_ids:
        # Join with calendars table to filter by calendar IDs
        # For now, we'll assume all events belong to default calendar
        pass
    
    events = query.order_by(CalendarEvent.start_datetime).all()
    
    # Convert to response models with details
    event_details = []
    for event in events:
        event_dict = {
            **event.__dict__,
            "creator": {"id": event.creator.id, "full_name": event.creator.full_name} if event.creator else None,
            "task": {"id": event.task.id, "title": event.task.title} if event.task else None,
            "attendees": [
                {
                    "id": attendee.id,
                    "user_id": attendee.user_id,
                    "external_email": attendee.external_email,
                    "external_name": attendee.external_name,
                    "response_status": attendee.response_status,
                    "is_organizer": attendee.is_organizer
                }
                for attendee in event.attendees
            ] if event.attendees else [],
            "reminders": [
                {
                    "id": reminder.id,
                    "remind_before_minutes": reminder.remind_before_minutes,
                    "reminder_type": reminder.reminder_type,
                    "is_sent": reminder.is_sent
                }
                for reminder in event.reminders
            ] if event.reminders else []
        }
        event_details.append(CalendarEventWithDetails(**event_dict))
    
    return CalendarViewResponse(
        events=event_details,
        start_date=view_request.start_date,
        end_date=view_request.end_date,
        view_type=view_request.view_type
    )

# Event Attendees
@router.post("/events/{event_id}/attendees", response_model=EventAttendeeResponse)
async def add_event_attendee(
    event_id: int,
    attendee_data: EventAttendeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an attendee to a calendar event"""
    # Verify event exists and user has access
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.organization_id == current_user.organization_id
        )
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    
    # Verify user exists in same organization if provided
    if attendee_data.user_id:
        user = db.query(User).filter(
            and_(
                User.id == attendee_data.user_id,
                User.organization_id == current_user.organization_id
            )
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your organization"
            )
    
    # Check if attendee already exists
    existing_attendee = db.query(EventAttendee).filter(
        and_(
            EventAttendee.event_id == event_id,
            or_(
                EventAttendee.user_id == attendee_data.user_id,
                EventAttendee.external_email == attendee_data.external_email
            )
        )
    ).first()
    
    if existing_attendee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendee already exists for this event"
        )
    
    # Create attendee
    attendee = EventAttendee(
        **attendee_data.model_dump(),
        event_id=event_id
    )
    
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    
    return EventAttendeeResponse.model_validate(attendee)

@router.get("/events/{event_id}/attendees", response_model=List[EventAttendeeWithDetails])
async def get_event_attendees(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all attendees for a calendar event"""
    # Verify event exists and user has access
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.organization_id == current_user.organization_id
        )
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )
    
    attendees = db.query(EventAttendee).filter(
        EventAttendee.event_id == event_id
    ).options(
        joinedload(EventAttendee.user)
    ).all()
    
    attendee_details = []
    for attendee in attendees:
        attendee_dict = {
            **attendee.__dict__,
            "user": {"id": attendee.user.id, "full_name": attendee.user.full_name} if attendee.user else None,
            "event": {"id": event.id, "title": event.title}
        }
        attendee_details.append(EventAttendeeWithDetails(**attendee_dict))
    
    return attendee_details

# Calendars management
@router.get("/calendars", response_model=List[CalendarWithDetails])
async def get_calendars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all calendars for current user's organization"""
    calendars = db.query(Calendar).filter(
        Calendar.organization_id == current_user.organization_id
    ).options(
        joinedload(Calendar.owner),
        joinedload(Calendar.shares)
    ).all()
    
    calendar_details = []
    for calendar in calendars:
        # Count events in this calendar (placeholder - would need calendar_id in events)
        events_count = 0
        
        calendar_dict = {
            **calendar.__dict__,
            "owner": {"id": calendar.owner.id, "full_name": calendar.owner.full_name} if calendar.owner else None,
            "shares": [
                {
                    "id": share.id,
                    "user_id": share.user_id,
                    "permission": share.permission
                }
                for share in calendar.shares
            ] if calendar.shares else [],
            "events_count": events_count
        }
        calendar_details.append(CalendarWithDetails(**calendar_dict))
    
    return calendar_details

@router.post("/calendars", response_model=CalendarResponse)
async def create_calendar(
    calendar_data: CalendarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar"""
    calendar = Calendar(
        **calendar_data.model_dump(),
        organization_id=current_user.organization_id,
        owner_id=current_user.id
    )
    
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    
    return CalendarResponse.model_validate(calendar)