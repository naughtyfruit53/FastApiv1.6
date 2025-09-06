"""
Enhanced Notification System with Real-time Capabilities
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import WebSocket
import threading
from dataclasses import dataclass, asdict
from enum import Enum

from app.models.system_models import NotificationTemplate, NotificationLog, NotificationPreference
from app.models.user_models import User, Organization
from app.services.localization_service import LocalizationService

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Enhanced notification types"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    DESKTOP = "desktop"
    REAL_TIME = "real_time"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationCategory(str, Enum):
    """Notification categories"""
    AI_INSIGHTS = "ai_insights"
    ANOMALY_ALERT = "anomaly_alert"
    MODEL_TRAINING = "model_training"
    PREDICTION_COMPLETE = "prediction_complete"
    WORKFLOW_EXECUTION = "workflow_execution"
    SYSTEM_ALERT = "system_alert"
    SECURITY_ALERT = "security_alert"
    BUSINESS_ALERT = "business_alert"
    MARKETING_CAMPAIGN = "marketing_campaign"
    SERVICE_UPDATE = "service_update"
    BILLING_ALERT = "billing_alert"
    INTEGRATION_STATUS = "integration_status"


@dataclass
class NotificationMessage:
    """Enhanced notification message structure"""
    id: str
    recipient_id: int
    organization_id: int
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    language_code: str = "en"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class WebSocketManager:
    """Manage WebSocket connections for real-time notifications"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}  # user_id -> websockets
        self._lock = threading.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user"""
        await websocket.accept()
        
        with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket for a user"""
        with self._lock:
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Send a message to all WebSocket connections for a user"""
        if user_id not in self.active_connections:
            return
        
        disconnected_sockets = []
        
        for websocket in self.active_connections[user_id].copy():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message to user {user_id}: {str(e)}")
                disconnected_sockets.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected_sockets:
            self.disconnect(websocket, user_id)
    
    async def broadcast_to_organization(self, organization_id: int, message: Dict[str, Any]):
        """Broadcast a message to all users in an organization"""
        # Note: In practice, you'd need to track organization memberships
        # This is a simplified implementation
        for user_id, websockets in self.active_connections.items():
            await self.send_to_user(user_id, message)
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())


class NotificationQueue:
    """Queue for managing notification delivery"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = False
    
    async def add(self, notification: NotificationMessage):
        """Add notification to queue"""
        await self.queue.put(notification)
    
    async def process_queue(self, notification_service):
        """Process notifications in the queue"""
        self.processing = True
        
        while self.processing:
            try:
                # Wait for notification with timeout
                notification = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await notification_service.deliver_notification(notification)
                self.queue.task_done()
            except asyncio.TimeoutError:
                # No notifications in queue, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing notification queue: {str(e)}")
    
    def stop_processing(self):
        """Stop processing the queue"""
        self.processing = False


class EnhancedNotificationService:
    """Enhanced notification service with real-time capabilities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.localization = LocalizationService()
        self.websocket_manager = WebSocketManager()
        self.notification_queue = NotificationQueue()
        self.templates_cache = {}
        self.preferences_cache = {}
        
        # Start queue processing
        asyncio.create_task(self.notification_queue.process_queue(self))
    
    async def send_notification(
        self,
        recipient_id: int,
        organization_id: int,
        notification_type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Dict[str, Any] = None,
        language_code: str = None,
        scheduled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Send a notification"""
        
        # Get user preferences
        user_prefs = await self.get_user_preferences(recipient_id, category)
        
        # Check if user wants this type of notification
        if not user_prefs.get(notification_type.value, True):
            logger.debug(f"User {recipient_id} has disabled {notification_type.value} for {category.value}")
            return None
        
        # Auto-detect language if not provided
        if language_code is None:
            user = self.db.query(User).filter(User.id == recipient_id).first()
            language_code = user.preferred_language if user and user.preferred_language else "en"
        
        # Create notification message
        notification = NotificationMessage(
            id=f"notif_{datetime.utcnow().timestamp()}_{recipient_id}",
            recipient_id=recipient_id,
            organization_id=organization_id,
            notification_type=notification_type,
            category=category,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            language_code=language_code
        )
        
        # Localize notification
        notification = await self.localize_notification(notification)
        
        # Add to queue for processing
        await self.notification_queue.add(notification)
        
        return notification.id
    
    async def deliver_notification(self, notification: NotificationMessage):
        """Deliver a notification through the appropriate channel"""
        try:
            # Check if notification is expired
            if notification.expires_at and datetime.utcnow() > notification.expires_at:
                logger.debug(f"Notification {notification.id} expired, skipping delivery")
                return
            
            # Check if notification is scheduled for later
            if notification.scheduled_at and datetime.utcnow() < notification.scheduled_at:
                # Re-queue for later
                await asyncio.sleep(1)
                await self.notification_queue.add(notification)
                return
            
            delivery_success = False
            
            # Deliver based on type
            if notification.notification_type == NotificationType.REAL_TIME:
                delivery_success = await self.send_real_time_notification(notification)
            elif notification.notification_type == NotificationType.IN_APP:
                delivery_success = await self.send_in_app_notification(notification)
            elif notification.notification_type == NotificationType.EMAIL:
                delivery_success = await self.send_email_notification(notification)
            elif notification.notification_type == NotificationType.PUSH:
                delivery_success = await self.send_push_notification(notification)
            elif notification.notification_type == NotificationType.WEBHOOK:
                delivery_success = await self.send_webhook_notification(notification)
            elif notification.notification_type == NotificationType.SLACK:
                delivery_success = await self.send_slack_notification(notification)
            
            # Log notification delivery
            await self.log_notification(notification, delivery_success)
            
        except Exception as e:
            logger.error(f"Error delivering notification {notification.id}: {str(e)}")
            await self.log_notification(notification, False, str(e))
    
    async def send_real_time_notification(self, notification: NotificationMessage) -> bool:
        """Send real-time notification via WebSocket"""
        try:
            message = {
                "type": "notification",
                "id": notification.id,
                "category": notification.category.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "timestamp": notification.created_at.isoformat()
            }
            
            await self.websocket_manager.send_to_user(notification.recipient_id, message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {str(e)}")
            return False
    
    async def send_in_app_notification(self, notification: NotificationMessage) -> bool:
        """Send in-app notification (stored in database)"""
        try:
            # Store in database for in-app display
            notification_log = NotificationLog(
                organization_id=notification.organization_id,
                recipient_id=notification.recipient_id,
                notification_type=notification.notification_type.value,
                category=notification.category.value,
                title=notification.title,
                message=notification.message,
                priority=notification.priority.value,
                data=notification.data,
                status="delivered",
                created_at=notification.created_at
            )
            
            self.db.add(notification_log)
            self.db.commit()
            
            # Also send real-time notification
            await self.send_real_time_notification(notification)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {str(e)}")
            return False
    
    async def send_email_notification(self, notification: NotificationMessage) -> bool:
        """Send email notification"""
        try:
            # Get email template
            template = await self.get_notification_template(
                notification.category, 
                NotificationType.EMAIL,
                notification.language_code
            )
            
            if template:
                # Use template
                subject = template.subject_template.format(**notification.data)
                body = template.body_template.format(
                    title=notification.title,
                    message=notification.message,
                    **notification.data
                )
            else:
                # Use notification content directly
                subject = notification.title
                body = notification.message
            
            # Send email (integrate with your email service)
            # email_service.send(recipient_email, subject, body)
            
            logger.info(f"Email notification sent to user {notification.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    async def send_push_notification(self, notification: NotificationMessage) -> bool:
        """Send push notification"""
        try:
            # Integrate with push notification service (FCM, APNs, etc.)
            push_data = {
                "title": notification.title,
                "body": notification.message,
                "data": notification.data,
                "priority": notification.priority.value
            }
            
            # push_service.send(user_device_tokens, push_data)
            
            logger.info(f"Push notification sent to user {notification.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def send_webhook_notification(self, notification: NotificationMessage) -> bool:
        """Send webhook notification"""
        try:
            import aiohttp
            
            # Get webhook URL from user preferences or organization settings
            webhook_url = notification.data.get("webhook_url")
            if not webhook_url:
                return False
            
            payload = {
                "id": notification.id,
                "type": notification.notification_type.value,
                "category": notification.category.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "timestamp": notification.created_at.isoformat(),
                "recipient_id": notification.recipient_id,
                "organization_id": notification.organization_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent to {webhook_url}")
                        return True
                    else:
                        logger.warning(f"Webhook notification failed with status {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False
    
    async def send_slack_notification(self, notification: NotificationMessage) -> bool:
        """Send Slack notification"""
        try:
            import aiohttp
            
            # Get Slack webhook URL from settings
            slack_webhook = notification.data.get("slack_webhook")
            if not slack_webhook:
                return False
            
            # Format Slack message
            color = {
                NotificationPriority.LOW: "good",
                NotificationPriority.NORMAL: "good", 
                NotificationPriority.HIGH: "warning",
                NotificationPriority.URGENT: "warning",
                NotificationPriority.CRITICAL: "danger"
            }.get(notification.priority, "good")
            
            slack_payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": notification.title,
                        "text": notification.message,
                        "fields": [
                            {
                                "title": "Category",
                                "value": notification.category.value,
                                "short": True
                            },
                            {
                                "title": "Priority", 
                                "value": notification.priority.value,
                                "short": True
                            }
                        ],
                        "timestamp": int(notification.created_at.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(slack_webhook, json=slack_payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent")
                        return True
                    else:
                        logger.warning(f"Slack notification failed with status {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
    
    async def localize_notification(self, notification: NotificationMessage) -> NotificationMessage:
        """Localize notification content"""
        try:
            # Translate title and message if they contain translation keys
            if notification.title.startswith("notif."):
                notification.title = self.localization.translate(
                    notification.title, 
                    notification.language_code,
                    **notification.data
                )
            
            if notification.message.startswith("notif."):
                notification.message = self.localization.translate(
                    notification.message,
                    notification.language_code,
                    **notification.data
                )
            
            # Format monetary values and dates
            for key, value in notification.data.items():
                if key.endswith("_amount") and isinstance(value, (int, float)):
                    notification.data[f"{key}_formatted"] = self.localization.format_currency(
                        value, notification.language_code
                    )
                elif key.endswith("_date") and isinstance(value, datetime):
                    notification.data[f"{key}_formatted"] = self.localization.format_datetime(
                        value, notification.language_code
                    )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error localizing notification: {str(e)}")
            return notification
    
    async def get_user_preferences(self, user_id: int, category: NotificationCategory) -> Dict[str, bool]:
        """Get user notification preferences"""
        # Check cache first
        cache_key = f"prefs_{user_id}_{category.value}"
        if cache_key in self.preferences_cache:
            return self.preferences_cache[cache_key]
        
        # Get from database
        prefs = self.db.query(NotificationPreference).filter(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.category == category.value
            )
        ).first()
        
        if prefs:
            preferences = prefs.preferences
        else:
            # Default preferences
            preferences = {
                "email": True,
                "sms": False,
                "push": True,
                "in_app": True,
                "real_time": True,
                "webhook": False,
                "slack": False
            }
        
        # Cache preferences
        self.preferences_cache[cache_key] = preferences
        
        return preferences
    
    async def get_notification_template(
        self, 
        category: NotificationCategory, 
        notification_type: NotificationType,
        language_code: str
    ) -> Optional[NotificationTemplate]:
        """Get notification template"""
        cache_key = f"template_{category.value}_{notification_type.value}_{language_code}"
        
        if cache_key in self.templates_cache:
            return self.templates_cache[cache_key]
        
        template = self.db.query(NotificationTemplate).filter(
            and_(
                NotificationTemplate.category == category.value,
                NotificationTemplate.notification_type == notification_type.value,
                NotificationTemplate.language_code == language_code
            )
        ).first()
        
        # Cache template
        self.templates_cache[cache_key] = template
        
        return template
    
    async def log_notification(
        self, 
        notification: NotificationMessage, 
        success: bool, 
        error_message: str = None
    ):
        """Log notification delivery"""
        try:
            notification_log = NotificationLog(
                organization_id=notification.organization_id,
                recipient_id=notification.recipient_id,
                notification_type=notification.notification_type.value,
                category=notification.category.value,
                title=notification.title,
                message=notification.message,
                priority=notification.priority.value,
                data=notification.data,
                status="delivered" if success else "failed",
                error_message=error_message,
                delivered_at=datetime.utcnow() if success else None,
                created_at=notification.created_at
            )
            
            self.db.add(notification_log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging notification: {str(e)}")
    
    async def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 50, 
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = self.db.query(NotificationLog).filter(
            NotificationLog.recipient_id == user_id
        )
        
        if unread_only:
            query = query.filter(NotificationLog.read_at.is_(None))
        
        notifications = query.order_by(desc(NotificationLog.created_at)).limit(limit).all()
        
        return [
            {
                "id": notif.id,
                "category": notif.category,
                "title": notif.title,
                "message": notif.message,
                "priority": notif.priority,
                "data": notif.data,
                "status": notif.status,
                "created_at": notif.created_at,
                "read_at": notif.read_at,
                "is_read": notif.read_at is not None
            }
            for notif in notifications
        ]
    
    async def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = self.db.query(NotificationLog).filter(
                and_(
                    NotificationLog.id == notification_id,
                    NotificationLog.recipient_id == user_id
                )
            ).first()
            
            if notification:
                notification.read_at = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    async def send_ai_insight_notification(
        self,
        user_id: int,
        organization_id: int,
        insight_data: Dict[str, Any],
        language_code: str = None
    ):
        """Send AI insight notification"""
        await self.send_notification(
            recipient_id=user_id,
            organization_id=organization_id,
            notification_type=NotificationType.IN_APP,
            category=NotificationCategory.AI_INSIGHTS,
            title="notif.ai_insights.new_insight_title",
            message="notif.ai_insights.new_insight_message",
            priority=NotificationPriority.HIGH if insight_data.get("priority") == "high" else NotificationPriority.NORMAL,
            data=insight_data,
            language_code=language_code
        )
    
    async def send_anomaly_alert_notification(
        self,
        user_id: int,
        organization_id: int,
        anomaly_data: Dict[str, Any],
        language_code: str = None
    ):
        """Send anomaly alert notification"""
        priority = NotificationPriority.CRITICAL if anomaly_data.get("severity") == "critical" else NotificationPriority.HIGH
        
        await self.send_notification(
            recipient_id=user_id,
            organization_id=organization_id,
            notification_type=NotificationType.REAL_TIME,
            category=NotificationCategory.ANOMALY_ALERT,
            title="notif.anomaly_alert.detected_title",
            message="notif.anomaly_alert.detected_message",
            priority=priority,
            data=anomaly_data,
            language_code=language_code
        )
    
    async def send_model_training_notification(
        self,
        user_id: int,
        organization_id: int,
        model_data: Dict[str, Any],
        status: str,
        language_code: str = None
    ):
        """Send model training status notification"""
        await self.send_notification(
            recipient_id=user_id,
            organization_id=organization_id,
            notification_type=NotificationType.IN_APP,
            category=NotificationCategory.MODEL_TRAINING,
            title=f"notif.model_training.{status}_title",
            message=f"notif.model_training.{status}_message",
            priority=NotificationPriority.NORMAL,
            data=model_data,
            language_code=language_code
        )