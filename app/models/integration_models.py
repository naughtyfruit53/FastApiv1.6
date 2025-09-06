# app/models/integration_models.py

"""
Enhanced External Integration Models for comprehensive third-party system connectivity
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base


class IntegrationType(PyEnum):
    ERP = "erp"
    CRM = "crm"
    ECOMMERCE = "ecommerce"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    ACCOUNTING = "accounting"
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    HR = "hr"
    MARKETING = "marketing"


class IntegrationStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    TESTING = "testing"
    MAINTENANCE = "maintenance"


class AuthType(PyEnum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    OAUTH1 = "oauth1"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class SyncDirection(PyEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(PyEnum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


class MappingType(PyEnum):
    FIELD = "field"
    TRANSFORMATION = "transformation"
    CONDITIONAL = "conditional"
    STATIC = "static"


class ExternalIntegration(Base):
    """External system integration configurations"""
    __tablename__ = "external_integrations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    # Integration identification
    name = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)  # salesforce, quickbooks, shopify, etc.
    integration_type = Column(Enum(IntegrationType), nullable=False)
    version = Column(String(50), nullable=True)
    
    # Configuration
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.INACTIVE, nullable=False)
    description = Column(Text, nullable=True)
    
    # Connection details
    endpoint_url = Column(String(1000), nullable=True)
    auth_type = Column(Enum(AuthType), nullable=False)
    auth_config = Column(JSON, nullable=True)  # Encrypted authentication configuration
    
    # Settings
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL, nullable=False)
    auto_sync_enabled = Column(Boolean, default=False, nullable=False)
    sync_interval_minutes = Column(Integer, nullable=True)  # For automatic syncing
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)
    batch_size = Column(Integer, default=100, nullable=False)
    
    # Error handling
    retry_count = Column(Integer, default=3, nullable=False)
    timeout_seconds = Column(Integer, default=30, nullable=False)
    
    # Metadata
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    total_syncs = Column(Integer, default=0, nullable=False)
    successful_syncs = Column(Integer, default=0, nullable=False)
    
    # Management
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="external_integrations")
    company = relationship("Company", back_populates="external_integrations")
    creator = relationship("User")
    
    mappings = relationship("IntegrationMapping", back_populates="integration", cascade="all, delete-orphan")
    sync_jobs = relationship("IntegrationSyncJob", back_populates="integration", cascade="all, delete-orphan")
    logs = relationship("IntegrationLog", back_populates="integration", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_integration_org_name'),
        Index('idx_integration_org_provider', 'organization_id', 'provider'),
        Index('idx_integration_org_type', 'organization_id', 'integration_type'),
        Index('idx_integration_org_status', 'organization_id', 'status'),
    )


class IntegrationMapping(Base):
    """Field mapping configurations for data synchronization"""
    __tablename__ = "integration_mappings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(Integer, ForeignKey("external_integrations.id"), nullable=False)
    
    # Mapping identification
    name = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False, index=True)  # customer, product, order, etc.
    
    # Source configuration
    source_field = Column(String(255), nullable=False)
    source_path = Column(String(500), nullable=True)  # JSON path for nested fields
    
    # Target configuration
    target_field = Column(String(255), nullable=False)
    target_path = Column(String(500), nullable=True)
    
    # Mapping configuration
    mapping_type = Column(Enum(MappingType), default=MappingType.FIELD, nullable=False)
    transformation_rule = Column(JSON, nullable=True)  # Transformation logic
    default_value = Column(Text, nullable=True)
    
    # Validation
    is_required = Column(Boolean, default=False, nullable=False)
    validation_rules = Column(JSON, nullable=True)
    
    # Behavior
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL, nullable=False)
    is_key_field = Column(Boolean, default=False, nullable=False)  # Primary identifier field
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="mappings")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('integration_id', 'entity_type', 'source_field', 'target_field', name='uq_mapping_integration_entity_fields'),
        Index('idx_mapping_org_integration', 'organization_id', 'integration_id'),
        Index('idx_mapping_org_entity', 'organization_id', 'entity_type'),
        Index('idx_mapping_org_key_field', 'organization_id', 'is_key_field'),
    )


class IntegrationSyncJob(Base):
    """Synchronization job tracking and management"""
    __tablename__ = "integration_sync_jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(Integer, ForeignKey("external_integrations.id"), nullable=False)
    
    # Job identification
    job_name = Column(String(255), nullable=False)
    job_type = Column(String(100), nullable=False, index=True)  # full_sync, incremental, entity_specific
    entity_type = Column(String(100), nullable=True, index=True)
    
    # Job configuration
    sync_direction = Column(Enum(SyncDirection), nullable=False)
    batch_size = Column(Integer, default=100, nullable=False)
    
    # Job status
    status = Column(Enum(SyncStatus), default=SyncStatus.IN_PROGRESS, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Statistics
    total_records = Column(Integer, default=0, nullable=False)
    processed_records = Column(Integer, default=0, nullable=False)
    successful_records = Column(Integer, default=0, nullable=False)
    failed_records = Column(Integer, default=0, nullable=False)
    skipped_records = Column(Integer, default=0, nullable=False)
    
    # Timeline
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Results
    result_summary = Column(JSON, nullable=True)
    error_summary = Column(Text, nullable=True)
    
    # Configuration
    job_parameters = Column(JSON, nullable=True)  # Job-specific parameters
    
    # Management
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    can_cancel = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="sync_jobs")
    triggered_by_user = relationship("User")
    
    records = relationship("IntegrationSyncRecord", back_populates="sync_job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sync_job_org_integration', 'organization_id', 'integration_id'),
        Index('idx_sync_job_org_status', 'organization_id', 'status'),
        Index('idx_sync_job_org_started', 'organization_id', 'started_at'),
        Index('idx_sync_job_org_type', 'organization_id', 'job_type'),
    )


class IntegrationSyncRecord(Base):
    """Individual record synchronization tracking"""
    __tablename__ = "integration_sync_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    sync_job_id = Column(Integer, ForeignKey("integration_sync_jobs.id"), nullable=False)
    
    # Record identification
    entity_type = Column(String(100), nullable=False, index=True)
    local_id = Column(String(100), nullable=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    
    # Sync details
    operation = Column(String(50), nullable=False)  # create, update, delete, skip
    sync_direction = Column(Enum(SyncDirection), nullable=False)
    status = Column(Enum(SyncStatus), nullable=False)
    
    # Data
    source_data = Column(JSON, nullable=True)  # Original data
    target_data = Column(JSON, nullable=True)  # Transformed data
    
    # Results
    error_message = Column(Text, nullable=True)
    validation_errors = Column(JSON, nullable=True)
    
    # Timeline
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sync_job = relationship("IntegrationSyncJob", back_populates="records")
    
    __table_args__ = (
        Index('idx_sync_record_org_job', 'organization_id', 'sync_job_id'),
        Index('idx_sync_record_org_entity', 'organization_id', 'entity_type'),
        Index('idx_sync_record_org_status', 'organization_id', 'status'),
        Index('idx_sync_record_org_local', 'organization_id', 'local_id'),
        Index('idx_sync_record_org_external', 'organization_id', 'external_id'),
    )


class IntegrationLog(Base):
    """Integration activity and error logging"""
    __tablename__ = "integration_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(Integer, ForeignKey("external_integrations.id"), nullable=False)
    
    # Log details
    log_level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # auth, sync, config, etc.
    
    # Context
    operation = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)
    
    # Technical details
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    error_code = Column(String(100), nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Metadata
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Relationships
    integration = relationship("ExternalIntegration", back_populates="logs")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_integration_log_org_integration', 'organization_id', 'integration_id'),
        Index('idx_integration_log_org_level', 'organization_id', 'log_level'),
        Index('idx_integration_log_org_category', 'organization_id', 'category'),
        Index('idx_integration_log_org_logged', 'organization_id', 'logged_at'),
    )


class DataTransformationRule(Base):
    """Data transformation rules for complex mapping scenarios"""
    __tablename__ = "data_transformation_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(Integer, ForeignKey("external_integrations.id"), nullable=False)
    
    # Rule identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    entity_type = Column(String(100), nullable=False, index=True)
    rule_type = Column(String(100), nullable=False)  # format, validate, calculate, lookup, etc.
    
    # Conditions
    conditions = Column(JSON, nullable=True)  # When to apply this rule
    
    # Transformation logic
    transformation_script = Column(Text, nullable=True)  # Custom transformation code
    lookup_table = Column(JSON, nullable=True)  # Static lookup mappings
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    execution_order = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('integration_id', 'name', name='uq_transformation_rule_integration_name'),
        Index('idx_transformation_rule_org_integration', 'organization_id', 'integration_id'),
        Index('idx_transformation_rule_org_entity', 'organization_id', 'entity_type'),
        Index('idx_transformation_rule_org_active', 'organization_id', 'is_active'),
    )


class IntegrationSchedule(Base):
    """Scheduled synchronization configurations"""
    __tablename__ = "integration_schedules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant fields
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(Integer, ForeignKey("external_integrations.id"), nullable=False)
    
    # Schedule identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule configuration
    is_active = Column(Boolean, default=True, nullable=False)
    cron_expression = Column(String(100), nullable=False)  # Cron-style schedule
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Job configuration
    job_type = Column(String(100), nullable=False)  # full_sync, incremental, etc.
    entity_types = Column(JSON, nullable=True)  # Specific entities to sync
    sync_direction = Column(Enum(SyncDirection), nullable=False)
    
    # Parameters
    job_parameters = Column(JSON, nullable=True)
    
    # Execution tracking
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    integration = relationship("ExternalIntegration")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('integration_id', 'name', name='uq_integration_schedule_integration_name'),
        Index('idx_integration_schedule_org_integration', 'organization_id', 'integration_id'),
        Index('idx_integration_schedule_org_active', 'organization_id', 'is_active'),
        Index('idx_integration_schedule_org_next_run', 'organization_id', 'next_run_at'),
    )