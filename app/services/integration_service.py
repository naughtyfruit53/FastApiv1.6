"""
Integration Service Layer
Business logic for managing integrations with external services
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.integration import (
    Integration, 
    IntegrationMessage, 
    IntegrationWebhook, 
    IntegrationWebhookEvent
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Service for managing integrations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_integration(
        self,
        organization_id: int,
        created_by: int,
        name: str,
        provider: str,
        auth_type: str,
        **kwargs
    ) -> Integration:
        """
        Create a new integration.
        
        Args:
            organization_id: Organization ID
            created_by: User ID who created the integration
            name: Integration name
            provider: Provider name (slack, whatsapp, google_workspace, etc.)
            auth_type: Authentication type
            **kwargs: Additional integration properties
            
        Returns:
            Created integration
        """
        integration = Integration(
            organization_id=organization_id,
            created_by=created_by,
            name=name,
            provider=provider,
            auth_type=auth_type,
            status="disconnected",
            **kwargs
        )
        
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Created integration {integration.id} ({name}) for organization {organization_id}")
        return integration
    
    def get_integration(self, integration_id: int, organization_id: int) -> Optional[Integration]:
        """
        Get an integration by ID.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            
        Returns:
            Integration or None
        """
        return self.db.query(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.organization_id == organization_id
            )
        ).first()
    
    def list_integrations(
        self,
        organization_id: int,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Integration]:
        """
        List integrations for an organization.
        
        Args:
            organization_id: Organization ID
            provider: Filter by provider
            status: Filter by status
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of integrations
        """
        query = self.db.query(Integration).filter(
            Integration.organization_id == organization_id
        )
        
        if provider:
            query = query.filter(Integration.provider == provider)
        
        if status:
            query = query.filter(Integration.status == status)
        
        return query.order_by(desc(Integration.created_at)).offset(skip).limit(limit).all()
    
    def update_integration(
        self,
        integration_id: int,
        organization_id: int,
        **kwargs
    ) -> Optional[Integration]:
        """
        Update an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            **kwargs: Fields to update
            
        Returns:
            Updated integration or None
        """
        integration = self.get_integration(integration_id, organization_id)
        if not integration:
            return None
        
        for key, value in kwargs.items():
            if hasattr(integration, key) and value is not None:
                setattr(integration, key, value)
        
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Updated integration {integration_id}")
        return integration
    
    def delete_integration(self, integration_id: int, organization_id: int) -> bool:
        """
        Delete an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            
        Returns:
            True if deleted, False if not found
        """
        integration = self.get_integration(integration_id, organization_id)
        if not integration:
            return False
        
        self.db.delete(integration)
        self.db.commit()
        
        logger.info(f"Deleted integration {integration_id}")
        return True
    
    def connect_integration(
        self,
        integration_id: int,
        organization_id: int,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None
    ) -> Optional[Integration]:
        """
        Mark an integration as connected.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            access_token: Access token
            refresh_token: Refresh token
            token_expires_at: Token expiration time
            
        Returns:
            Updated integration or None
        """
        integration = self.get_integration(integration_id, organization_id)
        if not integration:
            return None
        
        integration.status = "connected"
        integration.enabled = True
        integration.last_connected_at = datetime.utcnow()
        
        if access_token:
            integration.access_token = access_token
        if refresh_token:
            integration.refresh_token = refresh_token
        if token_expires_at:
            integration.token_expires_at = token_expires_at
        
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Connected integration {integration_id}")
        return integration
    
    def disconnect_integration(self, integration_id: int, organization_id: int) -> Optional[Integration]:
        """
        Disconnect an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            
        Returns:
            Updated integration or None
        """
        integration = self.get_integration(integration_id, organization_id)
        if not integration:
            return None
        
        integration.status = "disconnected"
        integration.enabled = False
        
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Disconnected integration {integration_id}")
        return integration
    
    def send_message(
        self,
        integration_id: int,
        organization_id: int,
        user_id: int,
        message_type: str,
        content: Optional[str] = None,
        subject: Optional[str] = None,
        to_user: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IntegrationMessage:
        """
        Send a message through an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            user_id: User ID
            message_type: Message type
            content: Message content
            subject: Message subject
            to_user: Recipient
            channel: Channel/group
            metadata: Additional metadata
            
        Returns:
            Created message record
        """
        message = IntegrationMessage(
            organization_id=organization_id,
            integration_id=integration_id,
            user_id=user_id,
            direction="outbound",
            message_type=message_type,
            content=content,
            subject=subject,
            to_user=to_user,
            channel=channel,
            metadata=metadata,
            status="pending"
        )
        
        self.db.add(message)
        
        # Update integration statistics
        integration = self.get_integration(integration_id, organization_id)
        if integration:
            integration.total_messages_sent += 1
            integration.last_used_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        logger.info(f"Created outbound message {message.id} for integration {integration_id}")
        
        # TODO: Actually send the message via the provider's API
        
        return message
    
    def receive_message(
        self,
        integration_id: int,
        organization_id: int,
        external_id: str,
        message_type: str,
        content: Optional[str] = None,
        from_user: Optional[str] = None,
        from_user_id: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IntegrationMessage:
        """
        Record a received message from an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            external_id: External message ID
            message_type: Message type
            content: Message content
            from_user: Sender name
            from_user_id: Sender ID
            channel: Channel/group
            metadata: Additional metadata
            
        Returns:
            Created message record
        """
        message = IntegrationMessage(
            organization_id=organization_id,
            integration_id=integration_id,
            external_id=external_id,
            direction="inbound",
            message_type=message_type,
            content=content,
            from_user=from_user,
            from_user_id=from_user_id,
            channel=channel,
            metadata=metadata,
            status="received"
        )
        
        self.db.add(message)
        
        # Update integration statistics
        integration = self.get_integration(integration_id, organization_id)
        if integration:
            integration.total_messages_received += 1
            integration.last_used_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        logger.info(f"Created inbound message {message.id} for integration {integration_id}")
        return message
    
    def create_webhook(
        self,
        integration_id: int,
        organization_id: int,
        webhook_url: str,
        webhook_secret: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> IntegrationWebhook:
        """
        Create a webhook for an integration.
        
        Args:
            integration_id: Integration ID
            organization_id: Organization ID
            webhook_url: Webhook URL
            webhook_secret: Webhook secret for verification
            event_types: List of event types to subscribe to
            
        Returns:
            Created webhook
        """
        webhook = IntegrationWebhook(
            organization_id=organization_id,
            integration_id=integration_id,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret,
            event_types=event_types,
            active=True,
            verified=False
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        
        logger.info(f"Created webhook {webhook.id} for integration {integration_id}")
        return webhook
    
    def process_webhook_event(
        self,
        webhook_id: int,
        organization_id: int,
        event_type: str,
        event_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> IntegrationWebhookEvent:
        """
        Process a webhook event.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID
            event_type: Event type
            event_id: External event ID
            payload: Event payload
            headers: Request headers
            
        Returns:
            Created webhook event
        """
        event = IntegrationWebhookEvent(
            organization_id=organization_id,
            webhook_id=webhook_id,
            event_type=event_type,
            event_id=event_id,
            payload=payload,
            headers=headers,
            processed=False
        )
        
        self.db.add(event)
        
        # Update webhook statistics
        webhook = self.db.query(IntegrationWebhook).filter(
            IntegrationWebhook.id == webhook_id
        ).first()
        
        if webhook:
            webhook.total_events_received += 1
            webhook.last_event_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(event)
        
        logger.info(f"Created webhook event {event.id} for webhook {webhook_id}")
        return event
