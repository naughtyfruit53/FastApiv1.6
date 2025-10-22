"""
Enhanced Integration Models for Slack, WhatsApp, and Google Workspace
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any

from app.core.database import Base


class IntegrationProvider(PyEnum):
    """Integration providers"""
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    GOOGLE_WORKSPACE = "google_workspace"
    MICROSOFT_TEAMS = "microsoft_teams"
    TELEGRAM = "telegram"
    EMAIL = "email"


class IntegrationConnectionStatus(PyEnum):
    """Connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"
    TESTING = "testing"


class Integration(Base):
    """
    Integration configurations for external services.
    Supports Slack, WhatsApp, Google Workspace, and other communication platforms.
    """
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_integration_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Integration identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Connection status
    status: Mapped[str] = mapped_column(String(50), default="disconnected", nullable=False, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Authentication (encrypted in production)
    auth_type: Mapped[str] = mapped_column(String(50), nullable=False)  # oauth2, api_key, webhook
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Should be encrypted
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Should be encrypted
    api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Should be encrypted
    api_secret: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Should be encrypted
    webhook_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Token management
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_token_refresh: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Channel/Workspace information (provider-specific)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Slack workspace
    workspace_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    channel_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # WhatsApp
    
    # Usage tracking
    total_messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_messages_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Management
    created_by: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_integration_creator_id"), 
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User", foreign_keys=[created_by])
    messages: Mapped[list["IntegrationMessage"]] = relationship(
        "IntegrationMessage", 
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    webhooks: Mapped[list["IntegrationWebhook"]] = relationship(
        "IntegrationWebhook", 
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_integration_org_provider', 'organization_id', 'provider'),
        Index('idx_integration_org_status', 'organization_id', 'status'),
        UniqueConstraint('organization_id', 'provider', 'name', name='uq_integration_org_provider_name'),
        {'extend_existing': True}
    )


class IntegrationMessage(Base):
    """
    Messages sent and received through integrations.
    Tracks communication history across all platforms.
    """
    __tablename__ = "integration_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_message_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Integration reference
    integration_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("integrations.id", name="fk_message_integration_id"), 
        nullable=False,
        index=True
    )
    
    # Message details
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # inbound, outbound
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)  # text, image, file, notification
    
    # Content
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    attachments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Sender/Recipient information
    from_user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Internal user reference (if applicable)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_message_user_id"), 
        nullable=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, sent, delivered, failed, read
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    integration: Mapped["Integration"] = relationship("Integration", back_populates="messages")
    user: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    __table_args__ = (
        Index('idx_message_org_integration', 'organization_id', 'integration_id'),
        Index('idx_message_external_id', 'external_id'),
        Index('idx_message_created', 'created_at'),
        Index('idx_message_status', 'status'),
        {'extend_existing': True}
    )


class IntegrationWebhook(Base):
    """
    Webhook configurations for integrations.
    Handles incoming events from external services.
    """
    __tablename__ = "integration_webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_webhook_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Integration reference
    integration_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("integrations.id", name="fk_webhook_integration_id"), 
        nullable=False,
        index=True
    )
    
    # Webhook details
    webhook_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    event_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Tracking
    total_events_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_event_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    integration: Mapped["Integration"] = relationship("Integration", back_populates="webhooks")
    events: Mapped[list["IntegrationWebhookEvent"]] = relationship(
        "IntegrationWebhookEvent", 
        back_populates="webhook",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_webhook_org_integration', 'organization_id', 'integration_id'),
        Index('idx_webhook_active', 'active'),
        {'extend_existing': True}
    )


class IntegrationWebhookEvent(Base):
    """
    Webhook event log.
    Tracks all incoming webhook events.
    """
    __tablename__ = "integration_webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_webhook_event_organization_id"), 
        nullable=False, 
        index=True
    )
    
    # Webhook reference
    webhook_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("integration_webhooks.id", name="fk_event_webhook_id"), 
        nullable=False,
        index=True
    )
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    headers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    webhook: Mapped["IntegrationWebhook"] = relationship("IntegrationWebhook", back_populates="events")
    
    __table_args__ = (
        Index('idx_webhook_event_org_webhook', 'organization_id', 'webhook_id'),
        Index('idx_webhook_event_processed', 'processed'),
        Index('idx_webhook_event_type', 'event_type'),
        {'extend_existing': True}
    )