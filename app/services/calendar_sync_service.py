# app/services/calendar_sync_service.py

"""
Calendar Sync Service for .ics parsing and ERP integration
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from icalendar import Calendar, Event as ICalEvent
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CalendarSyncService:
    """Service for parsing .ics files and syncing with ERP calendar/tasks"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Lazy initialization of database session"""
        if self.db is None:
            from app.core.database import SessionLocal
            self.db = SessionLocal()
        return self.db
    
    def parse_ics_attachment(self, attachment_id: int, organization_id: int) -> Dict[str, Any]:
        """
        Parse .ics file from email attachment and extract calendar events
        
        Args:
            attachment_id: Email attachment ID containing .ics file
            organization_id: Organization ID for multi-tenant support
            
        Returns:
            Dict containing parsed events and sync status
        """
        try:
            from app.models.email import EmailAttachment
            
            # Get attachment from database
            db = self._get_db()
            attachment = db.query(EmailAttachment).filter(
                EmailAttachment.id == attachment_id
            ).first()
            
            if not attachment:
                return {"success": False, "error": "Attachment not found"}
            
            if not attachment.filename.lower().endswith('.ics'):
                return {"success": False, "error": "File is not an .ics calendar file"}
            
            # Parse .ics content
            cal = Calendar.from_ical(attachment.file_data)
            events = []
            tasks = []
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event_data = self._parse_calendar_event(component, organization_id)
                    if event_data:
                        events.append(event_data)
                elif component.name == "VTODO":
                    task_data = self._parse_calendar_task(component, organization_id)
                    if task_data:
                        tasks.append(task_data)
            
            return {
                "success": True,
                "events": events,
                "tasks": tasks,
                "total_parsed": len(events) + len(tasks)
            }
            
        except Exception as e:
            logger.error(f"Error parsing .ics attachment {attachment_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_calendar_event(self, component: ICalEvent, organization_id: int) -> Optional[Dict[str, Any]]:
        """Parse individual calendar event from .ics component"""
        try:
            from app.models.calendar_management import EventType, EventStatus
            
            # Extract basic event data
            summary = str(component.get('SUMMARY', ''))
            description = str(component.get('DESCRIPTION', ''))
            location = str(component.get('LOCATION', ''))
            
            # Handle datetime fields
            dtstart = component.get('DTSTART')
            dtend = component.get('DTEND')
            
            start_datetime = None
            end_datetime = None
            all_day = False
            
            if dtstart:
                if hasattr(dtstart.dt, 'date'):
                    # Date only (all-day event)
                    start_datetime = datetime.combine(dtstart.dt, datetime.min.time())
                    all_day = True
                else:
                    # DateTime
                    start_datetime = dtstart.dt
            
            if dtend:
                if hasattr(dtend.dt, 'date'):
                    end_datetime = datetime.combine(dtend.dt, datetime.min.time())
                else:
                    end_datetime = dtend.dt
            
            # Determine event type based on content
            event_type = self._determine_event_type(summary, description)
            
            return {
                "title": summary,
                "description": description,
                "location": location,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "all_day": all_day,
                "event_type": event_type,
                "status": EventStatus.SCHEDULED,
                "organization_id": organization_id,
                "external_id": str(component.get('UID', '')),
                "recurrence_rule": str(component.get('RRULE', '')) if component.get('RRULE') else None
            }
            
        except Exception as e:
            logger.error(f"Error parsing calendar event: {str(e)}")
            return None
    
    def _parse_calendar_task(self, component, organization_id: int) -> Optional[Dict[str, Any]]:
        """Parse individual task from .ics VTODO component"""
        try:
            from app.models.task_management import TaskStatus, TaskPriority
            
            summary = str(component.get('SUMMARY', ''))
            description = str(component.get('DESCRIPTION', ''))
            
            # Task priority mapping
            priority_map = {
                1: "urgent",
                2: "high", 
                3: "normal",
                4: "low",
                5: "low"
            }
            
            priority_val = component.get('PRIORITY', 3)
            priority = priority_map.get(int(priority_val), "normal")
            
            # Due date
            due_date = None
            due_dt = component.get('DUE')
            if due_dt:
                due_date = due_dt.dt if hasattr(due_dt.dt, 'date') else datetime.combine(due_dt.dt, datetime.min.time())
            
            # Task status
            status_map = {
                'NEEDS-ACTION': "todo",
                'IN-PROCESS': "in_progress",
                'COMPLETED': "done",
                'CANCELLED': "cancelled"
            }
            
            task_status = str(component.get('STATUS', 'NEEDS-ACTION'))
            status = status_map.get(task_status, "todo")
            
            return {
                "title": summary,
                "description": description,
                "priority": priority,
                "status": status,
                "due_date": due_date,
                "organization_id": organization_id,
                "external_id": str(component.get('UID', ''))
            }
            
        except Exception as e:
            logger.error(f"Error parsing calendar task: {str(e)}")
            return None
    
    def _determine_event_type(self, summary: str, description: str) -> str:
        """Determine event type based on content analysis"""
        from app.models.calendar_management import EventType
        
        content = f"{summary} {description}".lower()
        
        if any(word in content for word in ['meeting', 'call', 'conference', 'sync', 'standup']):
            return "meeting"
        elif any(word in content for word in ['appointment', 'visit', 'demo', 'presentation']):
            return "appointment"
        elif any(word in content for word in ['deadline', 'due', 'submission', 'delivery']):
            return "deadline"
        elif any(word in content for word in ['reminder', 'follow-up', 'check']):
            return "reminder"
        elif any(word in content for word in ['holiday', 'vacation', 'off', 'leave']):
            return "holiday"
        else:
            return "appointment"
    
    def sync_events_to_database(self, events: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
        """Sync parsed events to calendar_events table"""
        try:
            created_events = []
            updated_events = []
            
            for event_data in events:
                # Check if event already exists by external_id
                existing_event = None
                if event_data.get('external_id'):
                    existing_event = self.db.query(CalendarEvent).filter(
                        CalendarEvent.external_id == event_data['external_id'],
                        CalendarEvent.organization_id == event_data['organization_id']
                    ).first()
                
                if existing_event:
                    # Update existing event
                    for key, value in event_data.items():
                        if hasattr(existing_event, key) and key != 'id':
                            setattr(existing_event, key, value)
                    existing_event.updated_at = datetime.utcnow()
                    updated_events.append(existing_event.id)
                else:
                    # Create new event
                    event_data['created_by'] = user_id
                    new_event = CalendarEvent(**event_data)
                    self.db.add(new_event)
                    self.db.flush()
                    created_events.append(new_event.id)
            
            self.db.commit()
            
            return {
                "success": True,
                "created_events": len(created_events),
                "updated_events": len(updated_events),
                "event_ids": created_events + updated_events
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing events to database: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def sync_tasks_to_database(self, tasks: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
        """Sync parsed tasks to tasks table"""
        try:
            created_tasks = []
            updated_tasks = []
            
            for task_data in tasks:
                # Check if task already exists by external_id
                existing_task = None
                if task_data.get('external_id'):
                    existing_task = self.db.query(Task).filter(
                        Task.external_id == task_data['external_id'],
                        Task.organization_id == task_data['organization_id']
                    ).first()
                
                if existing_task:
                    # Update existing task
                    for key, value in task_data.items():
                        if hasattr(existing_task, key) and key != 'id':
                            setattr(existing_task, key, value)
                    existing_task.updated_at = datetime.utcnow()
                    updated_tasks.append(existing_task.id)
                else:
                    # Create new task
                    task_data['created_by'] = user_id
                    task_data['assigned_to'] = user_id  # Auto-assign to importing user
                    new_task = Task(**task_data)
                    self.db.add(new_task)
                    self.db.flush()
                    created_tasks.append(new_task.id)
            
            self.db.commit()
            
            return {
                "success": True,
                "created_tasks": len(created_tasks),
                "updated_tasks": len(updated_tasks),
                "task_ids": created_tasks + updated_tasks
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing tasks to database: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_ics_for_tasks(self, task_ids: List[int], organization_id: int) -> Optional[str]:
        """Generate .ics file content for specified tasks"""
        try:
            cal = Calendar()
            cal.add('prodid', '-//TRITIQ ERP//Task Export//EN')
            cal.add('version', '2.0')
            
            tasks = self.db.query(Task).filter(
                Task.id.in_(task_ids),
                Task.organization_id == organization_id
            ).all()
            
            for task in tasks:
                todo = Calendar()
                todo.add('uid', f"task-{task.id}@tritiq-erp.com")
                todo.add('summary', task.title)
                todo.add('description', task.description or '')
                todo.add('status', self._map_task_status_to_ics(task.status))
                todo.add('priority', self._map_task_priority_to_ics(task.priority))
                
                if task.due_date:
                    todo.add('due', task.due_date)
                
                todo.add('created', task.created_at)
                todo.add('last-modified', task.updated_at)
                
                cal.add_component(todo)
            
            return cal.to_ical().decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating .ics for tasks: {str(e)}")
            return None
    
    def _map_task_status_to_ics(self, status: str) -> str:
        """Map internal task status to .ics VTODO status"""
        status_map = {
            "todo": 'NEEDS-ACTION',
            "in_progress": 'IN-PROCESS',
            "done": 'COMPLETED',
            "cancelled": 'CANCELLED',
            "review": 'IN-PROCESS'
        }
        return status_map.get(status, 'NEEDS-ACTION')
    
    def _map_task_priority_to_ics(self, priority: str) -> int:
        """Map internal task priority to .ics priority (1-9 scale)"""
        priority_map = {
            "urgent": 1,
            "high": 2,
            "normal": 5,
            "low": 8
        }
        return priority_map.get(priority, 5)
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

# Global calendar sync service instance
calendar_sync_service = CalendarSyncService()