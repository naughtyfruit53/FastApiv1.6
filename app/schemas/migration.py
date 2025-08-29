# app/schemas/migration.py
"""
Migration & Data Import Schemas - Pydantic models for migration API
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class MigrationSourceTypeEnum(str, Enum):
    """Migration source types"""
    TALLY = "tally"
    ZOHO = "zoho"
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    MANUAL = "manual"


class MigrationDataTypeEnum(str, Enum):
    """Types of data being migrated"""
    LEDGERS = "ledgers"
    VOUCHERS = "vouchers"
    CONTACTS = "contacts"
    PRODUCTS = "products"
    CUSTOMERS = "customers"
    VENDORS = "vendors"
    STOCK = "stock"
    CHART_OF_ACCOUNTS = "chart_of_accounts"
    COMPANY_INFO = "company_info"


class MigrationJobStatusEnum(str, Enum):
    """Migration job status"""
    DRAFT = "draft"
    MAPPING = "mapping"
    VALIDATION = "validation"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class MigrationLogLevelEnum(str, Enum):
    """Migration log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Base Models
class MigrationJobBase(BaseModel):
    job_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    source_type: MigrationSourceTypeEnum
    data_types: List[MigrationDataTypeEnum]
    conflict_resolution_strategy: str = Field(default="skip", pattern="^(skip|update|create_new)$")
    import_config: Optional[Dict[str, Any]] = None


class MigrationJobCreate(MigrationJobBase):
    pass


class MigrationJobUpdate(BaseModel):
    job_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    conflict_resolution_strategy: Optional[str] = Field(None, pattern="^(skip|update|create_new)$")
    import_config: Optional[Dict[str, Any]] = None
    status: Optional[MigrationJobStatusEnum] = None


class MigrationJobResponse(MigrationJobBase):
    id: int
    organization_id: int
    created_by: int
    source_file_name: Optional[str] = None
    source_file_size: Optional[int] = None
    source_metadata: Optional[Dict[str, Any]] = None
    status: MigrationJobStatusEnum
    progress_percentage: float
    total_records: int
    processed_records: int
    success_records: int
    failed_records: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    can_rollback: bool

    class Config:
        from_attributes = True


# Data Mapping Models
class MigrationDataMappingBase(BaseModel):
    data_type: MigrationDataTypeEnum
    source_field: str = Field(..., min_length=1, max_length=200)
    target_field: str = Field(..., min_length=1, max_length=200)
    field_type: str = Field(..., pattern="^(string|number|date|boolean|json)$")
    is_required: bool = False
    default_value: Optional[str] = None
    transformation_rule: Optional[str] = None
    validation_rule: Optional[str] = None


class MigrationDataMappingCreate(MigrationDataMappingBase):
    migration_job_id: int


class MigrationDataMappingUpdate(BaseModel):
    target_field: Optional[str] = Field(None, min_length=1, max_length=200)
    field_type: Optional[str] = Field(None, pattern="^(string|number|date|boolean|json)$")
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    transformation_rule: Optional[str] = None
    validation_rule: Optional[str] = None


class MigrationDataMappingResponse(MigrationDataMappingBase):
    id: int
    migration_job_id: int
    organization_id: int
    sample_source_value: Optional[str] = None
    sample_target_value: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Migration Log Models
class MigrationLogBase(BaseModel):
    level: MigrationLogLevelEnum
    message: str
    source_record_id: Optional[str] = None
    target_record_id: Optional[int] = None
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    operation: Optional[str] = None
    data_type: Optional[MigrationDataTypeEnum] = None


class MigrationLogCreate(MigrationLogBase):
    migration_job_id: int


class MigrationLogResponse(MigrationLogBase):
    id: int
    migration_job_id: int
    organization_id: int
    stack_trace: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Migration Template Models
class MigrationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    source_type: MigrationSourceTypeEnum
    data_type: MigrationDataTypeEnum
    field_mappings: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None
    transformation_rules: Optional[Dict[str, Any]] = None


class MigrationTemplateCreate(MigrationTemplateBase):
    pass


class MigrationTemplateResponse(MigrationTemplateBase):
    id: int
    sample_data: Optional[Dict[str, Any]] = None
    is_system_template: bool
    is_active: bool
    version: str
    usage_count: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Migration Conflict Models
class MigrationConflictBase(BaseModel):
    data_type: MigrationDataTypeEnum
    source_record_id: str
    conflict_type: str = Field(..., pattern="^(duplicate|validation_error|data_mismatch)$")
    conflict_field: Optional[str] = None
    source_value: Dict[str, Any]
    existing_value: Optional[Dict[str, Any]] = None
    suggested_resolution: Optional[str] = Field(None, pattern="^(skip|update|create_new)$")


class MigrationConflictCreate(MigrationConflictBase):
    migration_job_id: int


class MigrationConflictResolve(BaseModel):
    resolution_action: str = Field(..., pattern="^(skip|update|create_new)$")
    resolution_notes: Optional[str] = None


class MigrationConflictResponse(MigrationConflictBase):
    id: int
    migration_job_id: int
    organization_id: int
    is_resolved: bool
    resolution_action: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# File Upload and Validation Models
class FileUploadResponse(BaseModel):
    """Response for file upload"""
    success: bool
    file_id: str
    file_name: str
    file_size: int
    detected_source_type: MigrationSourceTypeEnum
    detected_data_types: List[MigrationDataTypeEnum]
    preview_data: Optional[List[Dict[str, Any]]] = None
    total_records: int
    validation_errors: List[str] = []
    validation_warnings: List[str] = []


class DataValidationResponse(BaseModel):
    """Response for data validation"""
    is_valid: bool
    total_records: int
    validation_errors: List[Dict[str, Any]] = []
    validation_warnings: List[Dict[str, Any]] = []
    field_analysis: Dict[str, Any] = {}
    preview_data: List[Dict[str, Any]] = []


class FieldMappingPreview(BaseModel):
    """Field mapping preview"""
    source_fields: List[str]
    suggested_mappings: List[MigrationDataMappingBase]
    unmapped_fields: List[str]
    required_fields_missing: List[str]


class MigrationPreview(BaseModel):
    """Migration preview with conflict analysis"""
    total_records: int
    estimated_processing_time: int  # in seconds
    conflicts: List[MigrationConflictBase] = []
    validation_summary: DataValidationResponse
    impact_analysis: Dict[str, Any] = {}


class MigrationProgressResponse(BaseModel):
    """Migration progress response"""
    job_id: int
    status: MigrationJobStatusEnum
    progress_percentage: float
    processed_records: int
    total_records: int
    success_records: int
    failed_records: int
    current_operation: Optional[str] = None
    estimated_completion_time: Optional[datetime] = None
    recent_logs: List[MigrationLogResponse] = []


class MigrationSummaryResponse(BaseModel):
    """Migration completion summary"""
    job_id: int
    status: MigrationJobStatusEnum
    total_records: int
    success_records: int
    failed_records: int
    skipped_records: int
    duration_seconds: float
    created_entities: Dict[str, int] = {}  # entity_type -> count
    updated_entities: Dict[str, int] = {}  # entity_type -> count
    error_summary: Dict[str, int] = {}  # error_type -> count
    can_rollback: bool


class RollbackRequest(BaseModel):
    """Request for migration rollback"""
    confirm: bool = Field(..., description="Must be true to confirm rollback")
    reason: Optional[str] = None


class RollbackResponse(BaseModel):
    """Response for migration rollback"""
    success: bool
    message: str
    rolled_back_entities: Dict[str, int] = {}  # entity_type -> count
    rollback_summary: Dict[str, Any] = {}


# Bulk Operation Models
class BulkMigrationRequest(BaseModel):
    """Request for bulk migration operations"""
    migration_job_ids: List[int]
    operation: str = Field(..., pattern="^(start|cancel|rollback)$")
    confirm: bool = Field(..., description="Must be true to confirm bulk operation")


class BulkMigrationResponse(BaseModel):
    """Response for bulk migration operations"""
    total_jobs: int
    successful_jobs: List[int]
    failed_jobs: List[Dict[str, Any]]
    operation_summary: Dict[str, Any]


# Dashboard and Analytics Models
class MigrationStatistics(BaseModel):
    """Migration statistics for dashboard"""
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_records_migrated: int
    success_rate: float
    average_processing_time: float
    most_used_source_types: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class IntegrationHealthStatus(BaseModel):
    """Integration health status"""
    integration_name: str
    status: str = Field(..., pattern="^(healthy|warning|error|disabled)$")
    last_sync_at: Optional[datetime] = None
    sync_frequency: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None
    configuration_valid: bool = True
    performance_metrics: Dict[str, Any] = {}


class IntegrationDashboardResponse(BaseModel):
    """Unified integrations dashboard"""
    tally_integration: IntegrationHealthStatus
    email_integration: IntegrationHealthStatus
    calendar_integration: IntegrationHealthStatus
    payment_integration: IntegrationHealthStatus
    zoho_integration: IntegrationHealthStatus
    migration_statistics: MigrationStatistics
    system_health: Dict[str, Any] = {}


# Migration Wizard Models
class MigrationWizardStep(BaseModel):
    """Migration wizard step"""
    step_number: int
    step_name: str
    is_completed: bool
    is_current: bool
    can_skip: bool = False
    data: Optional[Dict[str, Any]] = None


class MigrationWizardState(BaseModel):
    """Migration wizard state"""
    job_id: int
    current_step: int
    total_steps: int
    steps: List[MigrationWizardStep]
    can_proceed: bool
    validation_errors: List[str] = []