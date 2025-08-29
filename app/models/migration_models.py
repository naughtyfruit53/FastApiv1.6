# app/models/migration_models.py
"""
Migration & Data Import Models - Comprehensive migration system for multiple data sources
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class MigrationSourceType(enum.Enum):
    """Migration source types"""
    TALLY = "tally"
    ZOHO = "zoho"
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    MANUAL = "manual"


class MigrationDataType(enum.Enum):
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


class MigrationJobStatus(enum.Enum):
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


class MigrationJob(Base):
    """Migration job tracking"""
    __tablename__ = "migration_jobs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    job_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(MigrationSourceType), nullable=False)
    data_types = Column(JSON, nullable=False)  # List of MigrationDataType values
    
    # Source file information
    source_file_name = Column(String(500), nullable=True)
    source_file_path = Column(String(1000), nullable=True)
    source_file_size = Column(Integer, nullable=True)
    source_metadata = Column(JSON, nullable=True)  # Source-specific metadata
    
    # Job configuration
    import_config = Column(JSON, nullable=True)  # Import settings and preferences
    conflict_resolution_strategy = Column(String(50), default="skip")  # skip, update, create_new
    
    # Status and progress
    status = Column(Enum(MigrationJobStatus), nullable=False, default=MigrationJobStatus.DRAFT)
    progress_percentage = Column(Float, default=0.0)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    success_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Rollback information
    can_rollback = Column(Boolean, default=True)
    rollback_data = Column(JSON, nullable=True)  # Data needed for rollback
    
    # Relationships
    organization = relationship("Organization", back_populates="migration_jobs")
    created_by_user = relationship("User", foreign_keys=[created_by])
    data_mappings = relationship("MigrationDataMapping", back_populates="migration_job", cascade="all, delete-orphan")
    logs = relationship("MigrationLog", back_populates="migration_job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_migration_job_org_status', 'organization_id', 'status'),
        Index('idx_migration_job_created_by', 'created_by'),
    )


class MigrationDataMapping(Base):
    """Data field mapping for migration"""
    __tablename__ = "migration_data_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Mapping details
    data_type = Column(Enum(MigrationDataType), nullable=False)
    source_field = Column(String(200), nullable=False)
    target_field = Column(String(200), nullable=False)
    field_type = Column(String(50), nullable=False)  # string, number, date, boolean, etc.
    
    # Mapping configuration
    is_required = Column(Boolean, default=False)
    default_value = Column(String(500), nullable=True)
    transformation_rule = Column(String(1000), nullable=True)  # JSON string with transformation logic
    validation_rule = Column(String(1000), nullable=True)  # Validation rules
    
    # Sample data for preview
    sample_source_value = Column(String(500), nullable=True)
    sample_target_value = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    migration_job = relationship("MigrationJob", back_populates="data_mappings")
    organization = relationship("Organization")
    
    __table_args__ = (
        Index('idx_migration_mapping_job', 'migration_job_id'),
        Index('idx_migration_mapping_type', 'data_type'),
        UniqueConstraint('migration_job_id', 'data_type', 'source_field', name='uq_migration_mapping'),
    )


class MigrationLogLevel(enum.Enum):
    """Migration log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MigrationLog(Base):
    """Migration operation logs"""
    __tablename__ = "migration_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Log details
    level = Column(Enum(MigrationLogLevel), nullable=False, default=MigrationLogLevel.INFO)
    message = Column(Text, nullable=False)
    source_record_id = Column(String(100), nullable=True)  # Reference to source record
    target_record_id = Column(Integer, nullable=True)  # Reference to created/updated record
    
    # Error details
    error_code = Column(String(50), nullable=True)
    error_details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Context
    operation = Column(String(100), nullable=True)  # create, update, validate, etc.
    data_type = Column(Enum(MigrationDataType), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    migration_job = relationship("MigrationJob", back_populates="logs")
    organization = relationship("Organization")
    
    __table_args__ = (
        Index('idx_migration_log_job', 'migration_job_id'),
        Index('idx_migration_log_level', 'level'),
        Index('idx_migration_log_created', 'created_at'),
    )


class MigrationTemplate(Base):
    """Predefined migration templates"""
    __tablename__ = "migration_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(MigrationSourceType), nullable=False)
    data_type = Column(Enum(MigrationDataType), nullable=False)
    
    # Template configuration
    field_mappings = Column(JSON, nullable=False)  # Predefined field mappings
    validation_rules = Column(JSON, nullable=True)  # Validation rules
    transformation_rules = Column(JSON, nullable=True)  # Data transformation rules
    sample_data = Column(JSON, nullable=True)  # Sample data for preview
    
    # Template metadata
    is_system_template = Column(Boolean, default=True)  # System vs user-created
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_migration_template_source_data', 'source_type', 'data_type'),
        Index('idx_migration_template_active', 'is_active'),
    )


class MigrationConflict(Base):
    """Conflict resolution tracking"""
    __tablename__ = "migration_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Conflict details
    data_type = Column(Enum(MigrationDataType), nullable=False)
    source_record_id = Column(String(100), nullable=False)
    conflict_type = Column(String(50), nullable=False)  # duplicate, validation_error, data_mismatch
    conflict_field = Column(String(200), nullable=True)
    
    # Conflict data
    source_value = Column(JSON, nullable=False)  # Source record data
    existing_value = Column(JSON, nullable=True)  # Existing record data (if duplicate)
    suggested_resolution = Column(String(50), nullable=True)  # skip, update, create_new
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolution_action = Column(String(50), nullable=True)  # Action taken
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    migration_job = relationship("MigrationJob")
    organization = relationship("Organization")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    
    __table_args__ = (
        Index('idx_migration_conflict_job', 'migration_job_id'),
        Index('idx_migration_conflict_resolved', 'is_resolved'),
    )