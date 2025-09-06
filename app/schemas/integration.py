# app/schemas/integration.py

"""
Enhanced External Integration Schemas for comprehensive third-party system connectivity
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class IntegrationType(str, Enum):
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


class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    TESTING = "testing"
    MAINTENANCE = "maintenance"


class AuthType(str, Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    OAUTH1 = "oauth1"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class SyncDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"


class MappingType(str, Enum):
    FIELD = "field"
    TRANSFORMATION = "transformation"
    CONDITIONAL = "conditional"
    STATIC = "static"


# External Integration Schemas
class ExternalIntegrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=100)
    integration_type: IntegrationType
    version: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    endpoint_url: Optional[str] = Field(None, max_length=1000)
    auth_type: AuthType
    auth_config: Optional[Dict[str, Any]] = None
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    auto_sync_enabled: bool = False
    sync_interval_minutes: Optional[int] = Field(None, gt=0)
    rate_limit_per_minute: Optional[int] = Field(None, gt=0)
    batch_size: int = Field(default=100, gt=0, le=1000)
    retry_count: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)

    @validator('endpoint_url')
    def validate_endpoint_url(cls, v):
        if v:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(v):
                raise ValueError('Invalid endpoint URL format')
        return v


class ExternalIntegrationCreate(ExternalIntegrationBase):
    company_id: Optional[int] = None


class ExternalIntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    provider: Optional[str] = Field(None, min_length=1, max_length=100)
    integration_type: Optional[IntegrationType] = None
    version: Optional[str] = Field(None, max_length=50)
    status: Optional[IntegrationStatus] = None
    description: Optional[str] = None
    endpoint_url: Optional[str] = Field(None, max_length=1000)
    auth_type: Optional[AuthType] = None
    auth_config: Optional[Dict[str, Any]] = None
    sync_direction: Optional[SyncDirection] = None
    auto_sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = Field(None, gt=0)
    rate_limit_per_minute: Optional[int] = Field(None, gt=0)
    batch_size: Optional[int] = Field(None, gt=0, le=1000)
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)


class ExternalIntegrationResponse(ExternalIntegrationBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    status: IntegrationStatus
    last_sync_at: Optional[datetime]
    next_sync_at: Optional[datetime]
    total_syncs: int
    successful_syncs: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExternalIntegrationWithDetails(ExternalIntegrationResponse):
    creator_name: Optional[str] = None
    success_rate_percentage: Optional[float] = None
    mapping_count: int = 0
    recent_sync_count: int = 0
    error_count: int = 0
    health_status: Optional[str] = None


# Integration Mapping Schemas
class IntegrationMappingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: str = Field(..., min_length=1, max_length=100)
    source_field: str = Field(..., min_length=1, max_length=255)
    source_path: Optional[str] = Field(None, max_length=500)
    target_field: str = Field(..., min_length=1, max_length=255)
    target_path: Optional[str] = Field(None, max_length=500)
    mapping_type: MappingType = MappingType.FIELD
    transformation_rule: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    is_required: bool = False
    validation_rules: Optional[Dict[str, Any]] = None
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    is_key_field: bool = False


class IntegrationMappingCreate(IntegrationMappingBase):
    integration_id: int


class IntegrationMappingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    entity_type: Optional[str] = Field(None, min_length=1, max_length=100)
    source_field: Optional[str] = Field(None, min_length=1, max_length=255)
    source_path: Optional[str] = Field(None, max_length=500)
    target_field: Optional[str] = Field(None, min_length=1, max_length=255)
    target_path: Optional[str] = Field(None, max_length=500)
    mapping_type: Optional[MappingType] = None
    transformation_rule: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    is_required: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None
    sync_direction: Optional[SyncDirection] = None
    is_key_field: Optional[bool] = None


class IntegrationMappingResponse(IntegrationMappingBase):
    id: int
    organization_id: int
    integration_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationMappingWithDetails(IntegrationMappingResponse):
    integration_name: Optional[str] = None
    creator_name: Optional[str] = None


# Integration Sync Job Schemas
class IntegrationSyncJobBase(BaseModel):
    job_name: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(..., min_length=1, max_length=100)
    entity_type: Optional[str] = Field(None, max_length=100)
    sync_direction: SyncDirection
    batch_size: int = Field(default=100, gt=0, le=1000)
    job_parameters: Optional[Dict[str, Any]] = None


class IntegrationSyncJobCreate(IntegrationSyncJobBase):
    integration_id: int


class IntegrationSyncJobUpdate(BaseModel):
    status: Optional[SyncStatus] = None
    can_cancel: Optional[bool] = None


class IntegrationSyncJobResponse(IntegrationSyncJobBase):
    id: int
    organization_id: int
    integration_id: int
    status: SyncStatus
    progress_percentage: float
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    skipped_records: int
    started_at: datetime
    completed_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    result_summary: Optional[Dict[str, Any]]
    error_summary: Optional[str]
    triggered_by: int
    can_cancel: bool

    class Config:
        from_attributes = True


class IntegrationSyncJobWithDetails(IntegrationSyncJobResponse):
    integration_name: Optional[str] = None
    triggered_by_name: Optional[str] = None
    duration_minutes: Optional[float] = None
    records_per_minute: Optional[float] = None


# Integration Sync Record Schemas
class IntegrationSyncRecordResponse(BaseModel):
    id: int
    organization_id: int
    sync_job_id: int
    entity_type: str
    local_id: Optional[str]
    external_id: Optional[str]
    operation: str
    sync_direction: SyncDirection
    status: SyncStatus
    error_message: Optional[str]
    validation_errors: Optional[Dict[str, Any]]
    processed_at: datetime
    source_data: Optional[Dict[str, Any]]
    target_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Integration Log Schemas
class IntegrationLogResponse(BaseModel):
    id: int
    organization_id: int
    integration_id: int
    log_level: str
    message: str
    category: str
    operation: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[str]
    error_code: Optional[str]
    logged_at: datetime
    user_id: Optional[int]
    session_id: Optional[str]

    class Config:
        from_attributes = True


class IntegrationLogWithDetails(IntegrationLogResponse):
    integration_name: Optional[str] = None
    user_name: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


# Data Transformation Rule Schemas
class DataTransformationRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    entity_type: str = Field(..., min_length=1, max_length=100)
    rule_type: str = Field(..., min_length=1, max_length=100)
    conditions: Optional[Dict[str, Any]] = None
    transformation_script: Optional[str] = None
    lookup_table: Optional[Dict[str, Any]] = None
    is_active: bool = True
    execution_order: int = Field(default=0, ge=0)


class DataTransformationRuleCreate(DataTransformationRuleBase):
    integration_id: int


class DataTransformationRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    entity_type: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_type: Optional[str] = Field(None, min_length=1, max_length=100)
    conditions: Optional[Dict[str, Any]] = None
    transformation_script: Optional[str] = None
    lookup_table: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    execution_order: Optional[int] = Field(None, ge=0)


class DataTransformationRuleResponse(DataTransformationRuleBase):
    id: int
    organization_id: int
    integration_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataTransformationRuleWithDetails(DataTransformationRuleResponse):
    integration_name: Optional[str] = None
    creator_name: Optional[str] = None


# Integration Schedule Schemas
class IntegrationScheduleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True
    cron_expression: str = Field(..., min_length=1, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    job_type: str = Field(..., min_length=1, max_length=100)
    entity_types: Optional[List[str]] = None
    sync_direction: SyncDirection
    job_parameters: Optional[Dict[str, Any]] = None

    @validator('cron_expression')
    def validate_cron_expression(cls, v):
        # Basic cron validation - in a real implementation, use a cron library
        parts = v.split()
        if len(parts) != 5:
            raise ValueError('Cron expression must have 5 parts: minute hour day month weekday')
        return v


class IntegrationScheduleCreate(IntegrationScheduleBase):
    integration_id: int


class IntegrationScheduleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    job_type: Optional[str] = Field(None, min_length=1, max_length=100)
    entity_types: Optional[List[str]] = None
    sync_direction: Optional[SyncDirection] = None
    job_parameters: Optional[Dict[str, Any]] = None


class IntegrationScheduleResponse(IntegrationScheduleBase):
    id: int
    organization_id: int
    integration_id: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    run_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationScheduleWithDetails(IntegrationScheduleResponse):
    integration_name: Optional[str] = None
    creator_name: Optional[str] = None
    last_run_status: Optional[str] = None


# Dashboard and Analytics Schemas
class IntegrationDashboardStats(BaseModel):
    total_integrations: int
    active_integrations: int
    failed_integrations: int
    total_syncs_today: int
    successful_syncs_today: int
    sync_success_rate: float
    data_volume_today: int
    average_sync_time_minutes: float
    integrations_by_type: Dict[str, int]
    integrations_by_status: Dict[str, int]
    recent_sync_jobs: List[IntegrationSyncJobResponse]
    failed_syncs: List[IntegrationSyncJobResponse]


class IntegrationHealthCheck(BaseModel):
    integration_id: int
    integration_name: str
    status: IntegrationStatus
    last_sync_status: Optional[str]
    connection_test: bool
    authentication_test: bool
    data_flow_test: bool
    health_score: float  # 0-100
    issues: List[str]
    recommendations: List[str]


# Filter Schemas
class ExternalIntegrationFilter(BaseModel):
    status: Optional[IntegrationStatus] = None
    integration_type: Optional[IntegrationType] = None
    provider: Optional[str] = None
    created_by: Optional[int] = None
    sync_direction: Optional[SyncDirection] = None
    auto_sync_enabled: Optional[bool] = None
    search: Optional[str] = None


class IntegrationSyncJobFilter(BaseModel):
    integration_id: Optional[int] = None
    status: Optional[SyncStatus] = None
    job_type: Optional[str] = None
    entity_type: Optional[str] = None
    triggered_by: Optional[int] = None
    started_from: Optional[datetime] = None
    started_to: Optional[datetime] = None
    search: Optional[str] = None


class IntegrationLogFilter(BaseModel):
    integration_id: Optional[int] = None
    log_level: Optional[str] = None
    category: Optional[str] = None
    operation: Optional[str] = None
    entity_type: Optional[str] = None
    logged_from: Optional[datetime] = None
    logged_to: Optional[datetime] = None
    user_id: Optional[int] = None
    search: Optional[str] = None


# List Response Schemas
class ExternalIntegrationList(BaseModel):
    integrations: List[ExternalIntegrationWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class IntegrationSyncJobList(BaseModel):
    sync_jobs: List[IntegrationSyncJobWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class IntegrationLogList(BaseModel):
    logs: List[IntegrationLogWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


# Bulk Operations
class BulkIntegrationUpdate(BaseModel):
    integration_ids: List[int] = Field(..., min_items=1)
    status: Optional[IntegrationStatus] = None
    auto_sync_enabled: Optional[bool] = None


class BulkSyncJobAction(BaseModel):
    job_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., pattern="^(cancel|retry)$")


# Test and Validation Schemas
class IntegrationTestRequest(BaseModel):
    test_type: str = Field(..., pattern="^(connection|authentication|sync)$")
    entity_type: Optional[str] = None
    sample_data: Optional[Dict[str, Any]] = None


class IntegrationTestResponse(BaseModel):
    success: bool
    test_type: str
    status_code: Optional[int]
    response_time_ms: Optional[float]
    error_message: Optional[str]
    test_data: Optional[Dict[str, Any]]
    recommendations: List[str]


class MappingValidationRequest(BaseModel):
    source_data: Dict[str, Any]
    entity_type: str


class MappingValidationResponse(BaseModel):
    is_valid: bool
    mapped_data: Optional[Dict[str, Any]]
    validation_errors: List[str]
    warnings: List[str]
    missing_required_fields: List[str]


# Import/Export Schemas
class IntegrationExportRequest(BaseModel):
    integration_ids: Optional[List[int]] = None
    include_mappings: bool = True
    include_schedules: bool = True
    include_transformation_rules: bool = True
    include_logs: bool = False
    log_days: int = Field(default=7, ge=1, le=90)
    format: str = Field(default="json", pattern="^(json|excel|csv)$")


class IntegrationImportRequest(BaseModel):
    integration_data: Dict[str, Any]
    overwrite_existing: bool = False
    validate_only: bool = False


class IntegrationImportResponse(BaseModel):
    success: bool
    imported_integrations: List[int]
    validation_errors: List[str]
    warnings: List[str]
    summary: Dict[str, int]