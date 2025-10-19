# Revised: app/api/notifications.py

"""
Notification API endpoints for Service CRM integration.

Provides CRUD operations for notification templates, sending notifications,
and viewing notification logs with full organization-level isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin
from app.core.org_restrictions import require_current_organization_id
from app.models import User, NotificationTemplate, NotificationLog
from app.schemas.base import (
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateInDB,
    NotificationLogInDB, NotificationSendRequest, BulkNotificationRequest,
    NotificationSendResponse, BulkNotificationResponse,
    NotificationPreferenceCreate, NotificationPreferenceUpdate, NotificationPreferenceInDB
)
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
notification_service = NotificationService()


# Notification Template Endpoints

@router.get("/templates", response_model=List[NotificationTemplateInDB])
async def get_notification_templates(
    channel: Optional[str] = Query(None, description="Filter by notification channel"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification templates for the current organization."""
    
    org_id = require_current_organization_id(current_user)
    
    templates = await notification_service.get_templates(
        db=db,
        organization_id=org_id,
        channel=channel,
        template_type=template_type,
        is_active=is_active
    )
    
    logger.info(f"Retrieved {len(templates)} notification templates for organization {org_id}")
    return templates


@router.post("/templates", response_model=NotificationTemplateInDB)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new notification template."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate channel
    valid_channels = ["email", "sms", "push", "in_app"]
    if template_data.channel not in valid_channels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel. Must be one of: {valid_channels}"
        )
    
    # Validate template type
    valid_types = ["appointment_reminder", "service_completion", "follow_up", "marketing", "system"]
    if template_data.template_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template type. Must be one of: {valid_types}"
        )
    
    try:
        template = await notification_service.create_template(
            db=db,
            template_data=template_data,
            organization_id=org_id,
            created_by=current_user.id
        )
        return template
    except Exception as e:
        logger.error(f"Failed to create notification template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification template"
        )


@router.get("/templates/{template_id}", response_model=NotificationTemplateInDB)
async def get_notification_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific notification template."""
    
    org_id = require_current_organization_id(current_user)
    
    template = await notification_service.get_template(db, template_id, org_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=NotificationTemplateInDB)
async def update_notification_template(
    template_id: int,
    update_data: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a notification template."""
    
    org_id = require_current_organization_id(current_user)
    
    # Convert to dict and filter out None values
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    template = await notification_service.update_template(db, template_id, org_id, update_dict)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    return template


@router.delete("/templates/{template_id}")
async def delete_notification_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a notification template."""
    
    org_id = require_current_organization_id(current_user)
    
    success = await notification_service.delete_template(db, template_id, org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    return {"message": "Notification template deleted successfully"}


# Notification Sending Endpoints

@router.post("/send", response_model=NotificationSendResponse)
async def send_notification(
    request: NotificationSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a single notification."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate channel
    valid_channels = ["email", "sms", "push", "in_app"]
    if request.channel not in valid_channels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel. Must be one of: {valid_channels}"
        )
    
    # Validate recipient type
    valid_recipient_types = ["customer", "user"]
    if request.recipient_type not in valid_recipient_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recipient type. Must be one of: {valid_recipient_types}"
        )
    
    try:
        notification_log = await notification_service.send_notification(
            db=db,
            request=request,
            organization_id=org_id,
            created_by=current_user.id
        )
        
        if not notification_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send notification. Check recipient information."
            )
        
        return NotificationSendResponse(
            notification_id=notification_log.id,
            status=notification_log.status,
            message="Notification sent successfully" if notification_log.status == "sent" else "Notification queued"
        )
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )


@router.post("/send-bulk", response_model=BulkNotificationResponse)
async def send_bulk_notification(
    request: BulkNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send notifications to multiple recipients."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate channel
    valid_channels = ["email", "sms", "push", "in_app"]
    if request.channel not in valid_channels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel. Must be one of: {valid_channels}"
        )
    
    # Validate recipient type
    valid_recipient_types = ["customers", "segment", "users"]
    if request.recipient_type not in valid_recipient_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recipient type. Must be one of: {valid_recipient_types}"
        )
    
    # Validate recipient specification
    if request.recipient_type in ["customers", "users"] and not request.recipient_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipient_ids is required for customers/users recipient type"
        )
    
    if request.recipient_type == "segment" and not request.segment_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="segment_name is required for segment recipient type"
        )
    
    try:
        results = await notification_service.send_bulk_notification(
            db=db,
            request=request,
            organization_id=org_id,
            created_by=current_user.id
        )
        
        return BulkNotificationResponse(**results)
        
    except Exception as e:
        logger.error(f"Failed to send bulk notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send bulk notification"
        )


# Notification Log Endpoints

@router.get("/logs", response_model=List[NotificationLogInDB])
async def get_notification_logs(
    recipient_type: Optional[str] = Query(None, description="Filter by recipient type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification logs for the current organization."""
    
    org_id = require_current_organization_id(current_user)
    
    logs = await notification_service.get_notification_logs(
        db=db,
        organization_id=org_id,
        recipient_type=recipient_type,
        status=status,
        channel=channel,
        limit=limit,
        offset=offset
    )
    
    logger.info(f"Retrieved {len(logs)} notification logs for organization {org_id}")
    return logs


@router.get("/logs/{log_id}", response_model=NotificationLogInDB)
async def get_notification_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific notification log."""
    
    org_id = require_current_organization_id(current_user)
    
    log = (await db.execute(
        select(NotificationLog).filter(
            NotificationLog.id == log_id,
            NotificationLog.organization_id == org_id
        )
    )).scalars().first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification log not found"
        )
    
    return log


# Analytics and Statistics

@router.get("/analytics/summary")
async def get_notification_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification analytics summary."""
    
    org_id = require_current_organization_id(current_user)
    
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get overall statistics
    total_sent = (await db.execute(
        select(func.count(NotificationLog.id)).filter(
            and_(
                NotificationLog.organization_id == org_id,
                NotificationLog.created_at >= start_date
            )
        )
    )).scalar()
    
    # Get status breakdown
    status_stats = (await db.execute(
        select(
            NotificationLog.status,
            func.count(NotificationLog.id).label("count")
        ).filter(
            and_(
                NotificationLog.organization_id == org_id,
                NotificationLog.created_at >= start_date
            )
        ).group_by(NotificationLog.status)
    )).all()
    
    # Get channel breakdown
    channel_stats = (await db.execute(
        select(
            NotificationLog.channel,
            func.count(NotificationLog.id).label("count")
        ).filter(
            and_(
                NotificationLog.organization_id == org_id,
                NotificationLog.created_at >= start_date
            )
        ).group_by(NotificationLog.channel)
    )).all()
    
    return {
        "period_days": days,
        "total_notifications": total_sent,
        "status_breakdown": {stat.status: stat.count for stat in status_stats},
        "channel_breakdown": {stat.channel: stat.count for stat in channel_stats}
    }


# Template Testing

@router.post("/templates/{template_id}/test")
async def test_notification_template(
    template_id: int,
    test_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test a notification template with sample data."""
    
    org_id = require_current_organization_id(current_user)
    
    template = await notification_service.get_template(db, template_id, org_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    # Get sample variables from test_data or use defaults
    variables = test_data.get("variables", {
        "customer_name": "John Doe",
        "appointment_date": "2024-01-15 10:00 AM",
        "service_type": "AC Repair"
    })
    
    # Substitute variables in template content
    test_subject = template.subject
    test_content = template.body
    
    if test_subject:
        test_subject = await notification_service.substitute_variables(test_subject, variables)
    if test_content:
        test_content = await notification_service.substitute_variables(test_content, variables)
    
    return {
        "template_id": template_id,
        "template_name": template.name,
        "channel": template.channel,
        "test_subject": test_subject,
        "test_content": test_content,
        "variables_used": variables
    }


# User Preference Endpoints

@router.get("/preferences/{subject_type}/{subject_id}", response_model=List[NotificationPreferenceInDB])
async def get_user_notification_preferences(
    subject_type: str,
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification preferences for a user or customer."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate subject type
    valid_subject_types = ["user", "customer"]
    if subject_type not in valid_subject_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subject type. Must be one of: {valid_subject_types}"
        )
    
    preferences = await notification_service.get_user_preferences(
        db=db,
        organization_id=org_id,
        subject_type=subject_type,
        subject_id=subject_id
    )
    
    return preferences


@router.post("/preferences", response_model=NotificationPreferenceInDB)
async def create_notification_preference(
    preference_data: NotificationPreferenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create or update a notification preference."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate subject type
    valid_subject_types = ["user", "customer"]
    if preference_data.subject_type not in valid_subject_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subject type. Must be one of: {valid_subject_types}"
        )
    
    # Validate channel
    valid_channels = ["email", "sms", "push", "in_app"]
    if preference_data.channel not in valid_channels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel. Must be one of: {valid_channels}"
        )
    
    # Validate notification type
    valid_types = ["appointment_reminder", "service_completion", "follow_up", "marketing", "system", "job_assignment", "job_update", "feedback_request", "sla_breach"]
    if preference_data.notification_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification type. Must be one of: {valid_types}"
        )
    
    try:
        preference = await notification_service.create_user_preference(
            db=db,
            organization_id=org_id,
            preference_data=preference_data.dict()
        )
        return preference
    except Exception as e:
        logger.error(f"Failed to create notification preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification preference"
        )


@router.put("/preferences/{preference_id}", response_model=NotificationPreferenceInDB)
async def update_notification_preference(
    preference_id: int,
    update_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a notification preference."""
    
    org_id = require_current_organization_id(current_user)
    
    preference = await notification_service.update_user_preference(
        db=db,
        preference_id=preference_id,
        organization_id=org_id,
        update_data=update_data.dict(exclude_unset=True)
    )
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification preference not found"
        )
    
    return preference


# Event Trigger Endpoints

@router.post("/trigger")
async def trigger_automated_notifications(
    trigger_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger automated notifications based on events."""
    
    org_id = require_current_organization_id(current_user)
    
    # Validate required fields
    if "trigger_event" not in trigger_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trigger_event is required"
        )
    
    # Validate trigger event
    valid_events = [
        "job_assignment", "job_update", "job_completion", 
        "feedback_request", "sla_breach", "appointment_reminder",
        "service_completion", "follow_up"
    ]
    if trigger_data["trigger_event"] not in valid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid trigger event. Must be one of: {valid_events}"
        )
    
    try:
        notification_logs = await notification_service.trigger_automated_notifications(
            db=db,
            trigger_event=trigger_data["trigger_event"],
            organization_id=org_id,
            context_data=trigger_data.get("context_data", {})
        )
        
        return {
            "triggered_notifications": len(notification_logs),
            "notification_ids": [log.id for log in notification_logs],
            "message": f"Successfully triggered {len(notification_logs)} notifications"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger automated notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger automated notifications"
        )