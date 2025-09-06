# app/models/api_gateway_models.py

"""
API Gateway Management Models for unified API access control and monitoring
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base


class APIKeyStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class RateLimitType(PyEnum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"


class AccessLevel(PyEnum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    FULL_ACCESS = "full_access"


class LogLevel(PyEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class WebhookStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class APIKey(Base):
    """API keys for external system access"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Key identification
    key_name = Column(String(255), nullable=False, index=True)
    api_key = Column(String(500), nullable=False, unique=True, index=True)  # Encrypted API key
    key_prefix = Column(String(20), nullable=False, index=True)  # First few chars for identification
    
    # Access control
    status = Column(Enum(APIKeyStatus), default=APIKeyStatus.ACTIVE, nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.READ_ONLY, nullable=False)
    
    # Permissions
    allowed_endpoints = Column(JSON, nullable=True)  # List of allowed endpoint patterns
    restricted_endpoints = Column(JSON, nullable=True)  # List of restricted endpoint patterns
    allowed_methods = Column(JSON, nullable=True)  # Allowed HTTP methods
    
    # Rate limiting
    rate_limit_requests = Column(Integer, nullable=True, default=1000)
    rate_limit_type = Column(Enum(RateLimitType), default=RateLimitType.PER_HOUR, nullable=False)
    current_usage = Column(Integer, default=0, nullable=False)
    
    # IP restrictions
    allowed_ips = Column(JSON, nullable=True)  # List of allowed IP addresses/ranges
    
    # Validity
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
    company = relationship("Company", back_populates="api_keys")
    creator = relationship("User")
    
    usage_logs = relationship("APIUsageLog", back_populates="api_key", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'key_name', name='uq_api_key_org_name'),
        Index('idx_api_key_org_status', 'organization_id', 'status'),
        Index('idx_api_key_org_access_level', 'organization_id', 'access_level'),
        Index('idx_api_key_prefix', 'key_prefix'),
    )


class APIUsageLog(Base):
    """API usage tracking and monitoring"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)  # Nullable for unauthenticated requests
    
    # Request details
    endpoint = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    request_ip = Column(String(45), nullable=False, index=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Request data
    request_headers = Column(JSON, nullable=True)
    request_body_size = Column(Integer, nullable=True)
    
    # Response details
    status_code = Column(Integer, nullable=False, index=True)
    response_size = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=False)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    request_id = Column(String(100), nullable=True, index=True)  # Unique request identifier
    
    # Relationships
    api_key = relationship("APIKey", back_populates="usage_logs")
    
    __table_args__ = (
        Index('idx_api_usage_org_timestamp', 'organization_id', 'timestamp'),
        Index('idx_api_usage_org_endpoint', 'organization_id', 'endpoint'),
        Index('idx_api_usage_org_status', 'organization_id', 'status_code'),
        Index('idx_api_usage_org_api_key', 'organization_id', 'api_key_id'),
    )


class APIEndpoint(Base):
    """API endpoint configuration and metadata"""
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Endpoint identification
    path = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_public = Column(Boolean, default=False)  # Public endpoints don't require API key
    requires_auth = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    
    # Rate limiting (overrides global settings)
    rate_limit_requests = Column(Integer, nullable=True)
    rate_limit_type = Column(Enum(RateLimitType), nullable=True)
    
    # Versioning
    version = Column(String(20), default="v1")
    
    # Documentation
    documentation_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'path', 'method', name='uq_api_endpoint_org_path_method'),
        Index('idx_api_endpoint_org_public', 'organization_id', 'is_public'),
        Index('idx_api_endpoint_org_deprecated', 'organization_id', 'is_deprecated'),
        Index('idx_api_endpoint_org_version', 'organization_id', 'version'),
    )


class Webhook(Base):
    """Webhook configurations for external system notifications"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Webhook identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    url = Column(String(1000), nullable=False)
    status = Column(Enum(WebhookStatus), default=WebhookStatus.ACTIVE, nullable=False)
    
    # Security
    secret_key = Column(String(255), nullable=True)  # For webhook signature verification
    
    # Event filters
    events = Column(JSON, nullable=False)  # List of events to trigger webhook
    entity_types = Column(JSON, nullable=True)  # Filter by entity types
    
    # Headers and authentication
    headers = Column(JSON, nullable=True)  # Custom headers to send
    auth_type = Column(String(50), nullable=True)  # bearer, basic, api_key, etc.
    auth_config = Column(JSON, nullable=True)  # Authentication configuration
    
    # Retry configuration
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)
    timeout_seconds = Column(Integer, default=30, nullable=False)
    
    # Success criteria
    success_status_codes = Column(JSON, nullable=True)  # List of HTTP status codes considered success
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="webhooks")
    company = relationship("Company", back_populates="webhooks")
    creator = relationship("User")
    
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_webhook_org_name'),
        Index('idx_webhook_org_status', 'organization_id', 'status'),
        Index('idx_webhook_org_events', 'organization_id'),  # For JSON queries on events
    )


class WebhookDelivery(Base):
    """Webhook delivery attempts and results"""
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    
    # Delivery details
    event_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    
    # Request details
    request_url = Column(String(1000), nullable=False)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(Text, nullable=True)
    
    # Response details
    response_status_code = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Delivery status
    is_successful = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Retry information
    attempt_number = Column(Integer, default=1, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)
    
    # Metadata
    delivered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")
    
    __table_args__ = (
        Index('idx_webhook_delivery_org_webhook', 'organization_id', 'webhook_id'),
        Index('idx_webhook_delivery_org_event', 'organization_id', 'event_type'),
        Index('idx_webhook_delivery_org_delivered', 'organization_id', 'delivered_at'),
        Index('idx_webhook_delivery_org_successful', 'organization_id', 'is_successful'),
    )


class RateLimitRule(Base):
    """Custom rate limiting rules for specific endpoints or API keys"""
    __tablename__ = "rate_limit_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Rule identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Rule target
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)  # Specific API key
    endpoint_pattern = Column(String(500), nullable=True)  # Endpoint pattern (e.g., /api/v1/*)
    method = Column(String(10), nullable=True)  # Specific HTTP method
    
    # Rate limit configuration
    requests_limit = Column(Integer, nullable=False)
    time_window_type = Column(Enum(RateLimitType), nullable=False)
    time_window_value = Column(Integer, default=1, nullable=False)  # Number of time units
    
    # Rule behavior
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority rules apply first
    
    # Actions when limit exceeded
    block_request = Column(Boolean, default=True, nullable=False)
    send_warning = Column(Boolean, default=False, nullable=False)
    custom_message = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    api_key = relationship("APIKey")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_rate_limit_rule_org_name'),
        Index('idx_rate_limit_rule_org_api_key', 'organization_id', 'api_key_id'),
        Index('idx_rate_limit_rule_org_active', 'organization_id', 'is_active'),
        Index('idx_rate_limit_rule_org_priority', 'organization_id', 'priority'),
    )


class APIError(Base):
    """API error tracking and monitoring"""
    __tablename__ = "api_errors"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    
    # Error details
    error_code = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    
    # Request context
    endpoint = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    request_ip = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Error classification
    error_type = Column(String(100), nullable=False, index=True)  # validation, authentication, server, etc.
    severity = Column(Enum(LogLevel), default=LogLevel.ERROR, nullable=False)
    
    # Resolution
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Metadata
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Relationships
    api_key = relationship("APIKey")
    resolver = relationship("User")
    
    __table_args__ = (
        Index('idx_api_error_org_occurred', 'organization_id', 'occurred_at'),
        Index('idx_api_error_org_type', 'organization_id', 'error_type'),
        Index('idx_api_error_org_severity', 'organization_id', 'severity'),
        Index('idx_api_error_org_resolved', 'organization_id', 'is_resolved'),
    )