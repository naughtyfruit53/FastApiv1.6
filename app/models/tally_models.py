# app/models/tally_models.py
"""
Tally Integration Models - Real-time sync for ledgers, vouchers, and transactions
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class TallyConnectionStatus(enum.Enum):
    """Tally connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"


class SyncDirection(enum.Enum):
    """Sync direction options"""
    BIDIRECTIONAL = "bidirectional"
    TO_TALLY = "to_tally"
    FROM_TALLY = "from_tally"


class SyncStatus(enum.Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class TallyConfiguration(Base):
    """Tally integration configuration"""
    __tablename__ = "tally_configuration"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, unique=True, index=True)
    
    # Connection details
    tally_server_host = Column(String(100), nullable=False, default="localhost")
    tally_server_port = Column(Integer, nullable=False, default=9000)
    company_name_in_tally = Column(String(200), nullable=False)
    
    # Authentication (if required)
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)  # Encrypted
    
    # Sync configuration
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL, nullable=False)
    auto_sync_enabled = Column(Boolean, default=False, nullable=False)
    sync_interval_minutes = Column(Integer, default=30, nullable=False)
    
    # Sync options
    sync_masters = Column(Boolean, default=True, nullable=False)  # Ledgers, Items, etc.
    sync_vouchers = Column(Boolean, default=True, nullable=False)  # Transactions
    sync_reports = Column(Boolean, default=False, nullable=False)  # Pull reports
    
    # Field mappings (JSON configuration)
    field_mappings = Column(JSON, nullable=True)
    ledger_mappings = Column(JSON, nullable=True)
    voucher_type_mappings = Column(JSON, nullable=True)
    
    # Connection status
    connection_status = Column(Enum(TallyConnectionStatus), default=TallyConnectionStatus.DISCONNECTED, nullable=False)
    last_connection_test = Column(DateTime, nullable=True)
    connection_error_message = Column(Text, nullable=True)
    
    # Last sync information
    last_sync_datetime = Column(DateTime, nullable=True)
    last_successful_sync = Column(DateTime, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    configured_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="tally_configuration")
    sync_logs = relationship("TallySyncLog", back_populates="tally_configuration")
    ledger_mappings_rel = relationship("TallyLedgerMapping", back_populates="tally_configuration")
    voucher_mappings_rel = relationship("TallyVoucherMapping", back_populates="tally_configuration")


class TallyLedgerMapping(Base):
    """Mapping between ERP ledgers and Tally ledgers"""
    __tablename__ = "tally_ledger_mappings"

    id = Column(Integer, primary_key=True, index=True)
    tally_configuration_id = Column(Integer, ForeignKey("tally_configuration.id"), nullable=False, index=True)
    chart_of_accounts_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    
    # Tally ledger details
    tally_ledger_name = Column(String(200), nullable=False, index=True)
    tally_ledger_guid = Column(String(100), nullable=True, index=True)  # Tally GUID if available
    tally_parent_ledger = Column(String(200), nullable=True)
    
    # Mapping configuration
    is_bidirectional = Column(Boolean, default=True, nullable=False)
    erp_to_tally_only = Column(Boolean, default=False, nullable=False)
    tally_to_erp_only = Column(Boolean, default=False, nullable=False)
    
    # Sync status
    last_synced = Column(DateTime, nullable=True)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tally_configuration = relationship("TallyConfiguration", back_populates="ledger_mappings_rel")
    chart_of_accounts = relationship("ChartOfAccounts")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tally_configuration_id', 'chart_of_accounts_id', name='uq_tally_ledger_mapping'),
        Index('idx_tally_ledger_name', 'tally_ledger_name'),
    )


class TallyVoucherMapping(Base):
    """Mapping between ERP vouchers and Tally voucher types"""
    __tablename__ = "tally_voucher_mappings"

    id = Column(Integer, primary_key=True, index=True)
    tally_configuration_id = Column(Integer, ForeignKey("tally_configuration.id"), nullable=False, index=True)
    
    # ERP voucher type
    erp_voucher_type = Column(String(50), nullable=False, index=True)  # purchase_voucher, sales_voucher, etc.
    
    # Tally voucher type
    tally_voucher_type = Column(String(100), nullable=False, index=True)
    tally_voucher_type_guid = Column(String(100), nullable=True)
    
    # Mapping configuration
    is_active = Column(Boolean, default=True, nullable=False)
    field_mappings = Column(JSON, nullable=True)  # Field-level mappings
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tally_configuration = relationship("TallyConfiguration", back_populates="voucher_mappings_rel")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tally_configuration_id', 'erp_voucher_type', name='uq_tally_voucher_mapping'),
        Index('idx_tally_voucher_type', 'tally_voucher_type'),
    )


class TallySyncLog(Base):
    """Log of sync operations with Tally"""
    __tablename__ = "tally_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    tally_configuration_id = Column(Integer, ForeignKey("tally_configuration.id"), nullable=False, index=True)
    
    # Sync operation details
    sync_type = Column(String(50), nullable=False, index=True)  # ledgers, vouchers, full_sync, etc.
    sync_direction = Column(String(20), nullable=False, index=True)  # to_tally, from_tally, bidirectional
    
    # Timing
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Status and results
    sync_status = Column(Enum(SyncStatus), nullable=False, index=True)
    records_processed = Column(Integer, default=0, nullable=False)
    records_successful = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    
    # Details
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    sync_summary = Column(JSON, nullable=True)  # Detailed results
    
    # Metadata
    triggered_by = Column(String(50), nullable=False, index=True)  # user, system, schedule
    user_id = Column(Integer, ForeignKey("platform_users.id"), nullable=True)

    # Relationships
    tally_configuration = relationship("TallyConfiguration", back_populates="sync_logs")
    sync_items = relationship("TallySyncItem", back_populates="sync_log", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index('idx_sync_log_type_status', 'sync_type', 'sync_status'),
        Index('idx_sync_log_started', 'started_at'),
    )


class TallySyncItem(Base):
    """Individual items in sync operation"""
    __tablename__ = "tally_sync_items"

    id = Column(Integer, primary_key=True, index=True)
    sync_log_id = Column(Integer, ForeignKey("tally_sync_logs.id"), nullable=False, index=True)
    
    # Item identification
    entity_type = Column(String(50), nullable=False, index=True)  # ledger, voucher, etc.
    entity_id = Column(Integer, nullable=True, index=True)  # ERP entity ID
    entity_reference = Column(String(100), nullable=True, index=True)  # ERP entity reference
    
    # Tally identification
    tally_guid = Column(String(100), nullable=True, index=True)
    tally_reference = Column(String(100), nullable=True, index=True)
    
    # Sync details
    sync_direction = Column(String(20), nullable=False, index=True)
    sync_status = Column(Enum(SyncStatus), nullable=False, index=True)
    
    # Results
    error_message = Column(Text, nullable=True)
    before_data = Column(JSON, nullable=True)  # Data before sync
    after_data = Column(JSON, nullable=True)  # Data after sync
    
    # Timing
    processed_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    sync_log = relationship("TallySyncLog", back_populates="sync_items")
    
    # Constraints
    __table_args__ = (
        Index('idx_sync_item_entity', 'entity_type', 'entity_id'),
        Index('idx_sync_item_tally', 'tally_guid'),
    )


class TallyDataCache(Base):
    """Cache for Tally data to improve sync performance"""
    __tablename__ = "tally_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Data identification
    data_type = Column(String(50), nullable=False, index=True)  # ledgers, voucher_types, companies
    data_key = Column(String(200), nullable=False, index=True)  # Unique identifier
    
    # Cached data
    data_content = Column(JSON, nullable=False)
    data_hash = Column(String(64), nullable=True, index=True)  # For change detection
    
    # Cache metadata
    cached_at = Column(DateTime, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    
    # Tally metadata
    tally_last_modified = Column(DateTime, nullable=True)
    tally_version = Column(String(50), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="tally_data_cache")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'data_type', 'data_key', name='uq_tally_cache'),
        Index('idx_tally_cache_expires', 'expires_at'),
        Index('idx_tally_cache_hash', 'data_hash'),
    )


class TallyErrorLog(Base):
    """Error log for Tally integration issues"""
    __tablename__ = "tally_error_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Error details
    error_type = Column(String(50), nullable=False, index=True)  # connection, sync, mapping, etc.
    error_code = Column(String(20), nullable=True, index=True)
    error_message = Column(Text, nullable=False)
    
    # Context
    operation = Column(String(100), nullable=True)  # What was being done
    entity_type = Column(String(50), nullable=True)  # What entity was involved
    entity_reference = Column(String(100), nullable=True)
    
    # Technical details
    stack_trace = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Resolution
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(Integer, ForeignKey("platform_users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Metadata
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String(20), default="error", nullable=False, index=True)  # error, warning, critical

    # Relationships
    organization = relationship("Organization", back_populates="tally_error_logs")
    
    # Constraints
    __table_args__ = (
        Index('idx_tally_error_type_severity', 'error_type', 'severity'),
        Index('idx_tally_error_resolved', 'is_resolved'),
    )