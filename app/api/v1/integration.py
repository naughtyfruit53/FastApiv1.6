"""
Integration API endpoints for Slack, WhatsApp, Google Workspace
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.integration import Integration, IntegrationMessage, IntegrationWebhook, IntegrationWebhookEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class IntegrationCreate(BaseModel):
    """Schema for creating integration"""
    name: str
    provider: str = Field(..., description="slack, whatsapp, google_workspace, etc.")
    description: Optional[str] = None
    auth_type: str = Field(..., description="oauth2, api_key, webhook")
    access_token: Optional[str] = None
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class IntegrationUpdate(BaseModel):
    """Schema for updating integration"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    access_token: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    """Schema for integration response"""
    id: int
    organization_id: int
    name: str
    provider: str
    description: Optional[str]
    status: str
    enabled: bool
    workspace_id: Optional[str]
    workspace_name: Optional[str]
    total_messages_sent: int
    total_messages_received: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class IntegrationMessageCreate(BaseModel):
    """Schema for creating message"""
    integration_id: int
    direction: str = Field(..., description="inbound or outbound")
    message_type: str = Field(default="text", description="text, image, file, notification")
    content: Optional[str] = None
    subject: Optional[str] = None
    to_user: Optional[str] = None
    channel: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IntegrationMessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    organization_id: int
    integration_id: int
    direction: str
    message_type: str
    content: Optional[str]
    subject: Optional[str]
    from_user: Optional[str]
    to_user: Optional[str]
    channel: Optional[str]
    status: str
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class IntegrationWebhookCreate(BaseModel):
    """Schema for creating webhook"""
    integration_id: int
    webhook_url: str
    webhook_secret: Optional[str] = None
    event_types: Optional[List[str]] = None


class IntegrationWebhookResponse(BaseModel):
    """Schema for webhook response"""
    id: int
    organization_id: int
    integration_id: int
    webhook_url: str
    event_types: Optional[List[str]]
    active: bool
    verified: bool
    total_events_received: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Integration Endpoints
# ============================================================================

@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    auth: tuple = Depends(require_access("integration", "create")),
    db: Session = Depends(get_db)
):
    """
    Create a new integration.
    """
    current_user, org_id = auth
    
    try:
        integration = Integration(
            organization_id=org_id,
            name=integration_data.name,
            provider=integration_data.provider,
            description=integration_data.description,
            auth_type=integration_data.auth_type,
            access_token=integration_data.access_token,
            api_key=integration_data.api_key,
            webhook_url=integration_data.webhook_url,
            config=integration_data.config,
            settings=integration_data.settings,
            created_by=current_user.id,
            status="disconnected"
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        logger.info(f"User {current_user.id} created integration {integration.id} ({integration.name})")
        return integration
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create integration: {str(e)}"
        )


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    provider: Optional[str] = None,
    status: Optional[str] = None,
    auth: tuple = Depends(require_access("integration", "read")),
    db: Session = Depends(get_db)
):
    """
    List all integrations for the organization.
    """
    current_user, org_id = auth
    
    try:
        query = db.query(Integration).filter(
            Integration.organization_id == org_id
        )
        
        if provider:
            query = query.filter(Integration.provider == provider)
        
        if status:
            query = query.filter(Integration.status == status)
        
        integrations = query.order_by(desc(Integration.created_at)).offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.id} listed {len(integrations)} integrations")
        return integrations
        
    except Exception as e:
        logger.error(f"Error listing integrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list integrations: {str(e)}"
        )


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    auth: tuple = Depends(require_access("integration", "read")),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific integration.
    """
    current_user, org_id = auth
    
    try:
        integration = db.query(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.organization_id == org_id
            )
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        return integration
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration: {str(e)}"
        )


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    auth: tuple = Depends(require_access("integration", "update")),
    db: Session = Depends(get_db)
):
    """
    Update an integration.
    """
    current_user, org_id = auth
    
    try:
        integration = db.query(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.organization_id == org_id
            )
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        # Update fields
        update_data = integration_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(integration, field, value)
        
        db.commit()
        db.refresh(integration)
        
        logger.info(f"User {current_user.id} updated integration {integration.id}")
        return integration
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration: {str(e)}"
        )


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    auth: tuple = Depends(require_access("integration", "delete")),
    db: Session = Depends(get_db)
):
    """
    Delete an integration.
    """
    current_user, org_id = auth
    
    try:
        integration = db.query(Integration).filter(
            and_(
                Integration.id == integration_id,
                Integration.organization_id == org_id
            )
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        db.delete(integration)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted integration {integration_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting integration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete integration: {str(e)}"
        )


# ============================================================================
# Integration Message Endpoints
# ============================================================================

@router.post("/messages", response_model=IntegrationMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: IntegrationMessageCreate,
    auth: tuple = Depends(require_access("integration", "create")),
    db: Session = Depends(get_db)
):
    """
    Send a message through an integration.
    """
    current_user, org_id = auth
    
    try:
        # Verify integration
        integration = db.query(Integration).filter(
            and_(
                Integration.id == message_data.integration_id,
                Integration.organization_id == org_id
            )
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        message = IntegrationMessage(
            organization_id=org_id,
            integration_id=message_data.integration_id,
            direction=message_data.direction,
            message_type=message_data.message_type,
            content=message_data.content,
            subject=message_data.subject,
            to_user=message_data.to_user,
            channel=message_data.channel,
            metadata=message_data.metadata,
            user_id=current_user.id,
            status="pending"
        )
        
        db.add(message)
        
        # Update integration stats
        if message_data.direction == "outbound":
            integration.total_messages_sent += 1
        else:
            integration.total_messages_received += 1
        
        integration.last_used_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        logger.info(f"User {current_user.id} sent message {message.id} via integration {integration.id}")
        
        # TODO: Actually send the message via the integration service
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/messages", response_model=List[IntegrationMessageResponse])
async def list_messages(
    integration_id: Optional[int] = None,
    direction: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("integration", "read")),
    db: Session = Depends(get_db)
):
    """
    List messages for integrations.
    """
    current_user, org_id = auth
    
    try:
        query = db.query(IntegrationMessage).filter(
            IntegrationMessage.organization_id == org_id
        )
        
        if integration_id:
            query = query.filter(IntegrationMessage.integration_id == integration_id)
        
        if direction:
            query = query.filter(IntegrationMessage.direction == direction)
        
        messages = query.order_by(desc(IntegrationMessage.created_at)).offset(skip).limit(limit).all()
        
        return messages
        
    except Exception as e:
        logger.error(f"Error listing messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list messages: {str(e)}"
        )


# ============================================================================
# Integration Webhook Endpoints
# ============================================================================

@router.post("/webhooks", response_model=IntegrationWebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: IntegrationWebhookCreate,
    auth: tuple = Depends(require_access("integration", "create")),
    db: Session = Depends(get_db)
):
    """
    Create a webhook for an integration.
    """
    current_user, org_id = auth
    
    try:
        # Verify integration
        integration = db.query(Integration).filter(
            and_(
                Integration.id == webhook_data.integration_id,
                Integration.organization_id == org_id
            )
        ).first()
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        webhook = IntegrationWebhook(
            organization_id=org_id,
            integration_id=webhook_data.integration_id,
            webhook_url=webhook_data.webhook_url,
            webhook_secret=webhook_data.webhook_secret,
            event_types=webhook_data.event_types,
            active=True,
            verified=False
        )
        
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        
        logger.info(f"Created webhook {webhook.id} for integration {integration.id}")
        return webhook
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create webhook: {str(e)}"
        )


@router.get("/webhooks", response_model=List[IntegrationWebhookResponse])
async def list_webhooks(
    integration_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("integration", "read")),
    db: Session = Depends(get_db)
):
    """
    List webhooks for integrations.
    """
    current_user, org_id = auth
    
    try:
        query = db.query(IntegrationWebhook).filter(
            IntegrationWebhook.organization_id == org_id
        )
        
        if integration_id:
            query = query.filter(IntegrationWebhook.integration_id == integration_id)
        
        webhooks = query.order_by(desc(IntegrationWebhook.created_at)).offset(skip).limit(limit).all()
        
        return webhooks
        
    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list webhooks: {str(e)}"
        )
