# app/schemas/tally.py
"""
Tally Integration Schemas - Real-time sync for ledgers, vouchers, and transactions
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TallyConnectionStatusEnum(str, Enum):
    """Tally connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"


class SyncDirectionEnum(str, Enum):
    """Sync direction options"""
    BIDIRECTIONAL = "bidirectional"
    TO_TALLY = "to_tally"
    FROM_TALLY = "from_tally"


class SyncStatusEnum(str, Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# Tally Configuration Schemas
class TallyConfigurationBase(BaseModel):
    tally_server_host: str = Field("localhost", description="Tally server host")
    tally_server_port: int = Field(9000, description="Tally server port")
    company_name_in_tally: str = Field(..., description="Company name in Tally")
    username: Optional[str] = Field(None, description="Username (if required)")
    password: Optional[str] = Field(None, description="Password (if required)")
    sync_direction: SyncDirectionEnum = Field(SyncDirectionEnum.BIDIRECTIONAL, description="Sync direction")
    auto_sync_enabled: bool = Field(False, description="Auto sync enabled")
    sync_interval_minutes: int = Field(30, description="Sync interval in minutes")
    sync_masters: bool = Field(True, description="Sync masters (ledgers, items)")
    sync_vouchers: bool = Field(True, description="Sync vouchers (transactions)")
    sync_reports: bool = Field(False, description="Sync reports")
    field_mappings: Optional[Dict[str, Any]] = Field(None, description="Field mappings")
    ledger_mappings: Optional[Dict[str, Any]] = Field(None, description="Ledger mappings")
    voucher_type_mappings: Optional[Dict[str, Any]] = Field(None, description="Voucher type mappings")


class TallyConfigurationCreate(TallyConfigurationBase):
    pass


class TallyConfigurationUpdate(BaseModel):
    tally_server_host: Optional[str] = None
    tally_server_port: Optional[int] = None
    company_name_in_tally: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    sync_direction: Optional[SyncDirectionEnum] = None
    auto_sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    sync_masters: Optional[bool] = None
    sync_vouchers: Optional[bool] = None
    sync_reports: Optional[bool] = None
    field_mappings: Optional[Dict[str, Any]] = None
    ledger_mappings: Optional[Dict[str, Any]] = None
    voucher_type_mappings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TallyConfigurationResponse(TallyConfigurationBase):
    id: int
    organization_id: int
    connection_status: TallyConnectionStatusEnum
    last_connection_test: Optional[datetime]
    connection_error_message: Optional[str]
    last_sync_datetime: Optional[datetime]
    last_successful_sync: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Tally Ledger Mapping Schemas
class TallyLedgerMappingBase(BaseModel):
    chart_of_accounts_id: int = Field(..., description="Chart of accounts ID")
    tally_ledger_name: str = Field(..., description="Tally ledger name")
    tally_ledger_guid: Optional[str] = Field(None, description="Tally ledger GUID")
    tally_parent_ledger: Optional[str] = Field(None, description="Tally parent ledger")
    is_bidirectional: bool = Field(True, description="Is bidirectional sync")
    erp_to_tally_only: bool = Field(False, description="ERP to Tally only")
    tally_to_erp_only: bool = Field(False, description="Tally to ERP only")


class TallyLedgerMappingCreate(TallyLedgerMappingBase):
    pass


class TallyLedgerMappingUpdate(BaseModel):
    tally_ledger_name: Optional[str] = None
    tally_ledger_guid: Optional[str] = None
    tally_parent_ledger: Optional[str] = None
    is_bidirectional: Optional[bool] = None
    erp_to_tally_only: Optional[bool] = None
    tally_to_erp_only: Optional[bool] = None


class TallyLedgerMappingResponse(TallyLedgerMappingBase):
    id: int
    tally_configuration_id: int
    last_synced: Optional[datetime]
    sync_status: SyncStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Tally Voucher Mapping Schemas
class TallyVoucherMappingBase(BaseModel):
    erp_voucher_type: str = Field(..., description="ERP voucher type")
    tally_voucher_type: str = Field(..., description="Tally voucher type")
    tally_voucher_type_guid: Optional[str] = Field(None, description="Tally voucher type GUID")
    is_active: bool = Field(True, description="Is active")
    field_mappings: Optional[Dict[str, Any]] = Field(None, description="Field-level mappings")


class TallyVoucherMappingCreate(TallyVoucherMappingBase):
    pass


class TallyVoucherMappingUpdate(BaseModel):
    tally_voucher_type: Optional[str] = None
    tally_voucher_type_guid: Optional[str] = None
    is_active: Optional[bool] = None
    field_mappings: Optional[Dict[str, Any]] = None


class TallyVoucherMappingResponse(TallyVoucherMappingBase):
    id: int
    tally_configuration_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Tally Sync Log Schemas
class TallySyncItemBase(BaseModel):
    entity_type: str = Field(..., description="Entity type")
    entity_id: Optional[int] = Field(None, description="ERP entity ID")
    entity_reference: Optional[str] = Field(None, description="ERP entity reference")
    tally_guid: Optional[str] = Field(None, description="Tally GUID")
    tally_reference: Optional[str] = Field(None, description="Tally reference")
    sync_direction: str = Field(..., description="Sync direction")
    sync_status: SyncStatusEnum = Field(..., description="Sync status")
    error_message: Optional[str] = Field(None, description="Error message")
    before_data: Optional[Dict[str, Any]] = Field(None, description="Data before sync")
    after_data: Optional[Dict[str, Any]] = Field(None, description="Data after sync")


class TallySyncItemResponse(TallySyncItemBase):
    id: int
    sync_log_id: int
    processed_at: datetime
    
    class Config:
        from_attributes = True


class TallySyncLogBase(BaseModel):
    sync_type: str = Field(..., description="Sync type")
    sync_direction: str = Field(..., description="Sync direction")
    started_at: datetime = Field(..., description="Started at")
    completed_at: Optional[datetime] = Field(None, description="Completed at")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    sync_status: SyncStatusEnum = Field(..., description="Sync status")
    records_processed: int = Field(0, description="Records processed")
    records_successful: int = Field(0, description="Records successful")
    records_failed: int = Field(0, description="Records failed")
    error_message: Optional[str] = Field(None, description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    sync_summary: Optional[Dict[str, Any]] = Field(None, description="Sync summary")
    triggered_by: str = Field(..., description="Triggered by")


class TallySyncLogCreate(TallySyncLogBase):
    pass


class TallySyncLogUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    sync_status: Optional[SyncStatusEnum] = None
    records_processed: Optional[int] = None
    records_successful: Optional[int] = None
    records_failed: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    sync_summary: Optional[Dict[str, Any]] = None


class TallySyncLogResponse(TallySyncLogBase):
    id: int
    tally_configuration_id: int
    sync_items: List[TallySyncItemResponse] = []
    
    class Config:
        from_attributes = True


# Tally Data Cache Schemas
class TallyDataCacheBase(BaseModel):
    data_type: str = Field(..., description="Data type")
    data_key: str = Field(..., description="Data key")
    data_content: Dict[str, Any] = Field(..., description="Data content")
    data_hash: Optional[str] = Field(None, description="Data hash")
    expires_at: Optional[datetime] = Field(None, description="Expires at")
    tally_last_modified: Optional[datetime] = Field(None, description="Tally last modified")
    tally_version: Optional[str] = Field(None, description="Tally version")


class TallyDataCacheCreate(TallyDataCacheBase):
    pass


class TallyDataCacheUpdate(BaseModel):
    data_content: Optional[Dict[str, Any]] = None
    data_hash: Optional[str] = None
    expires_at: Optional[datetime] = None
    tally_last_modified: Optional[datetime] = None
    tally_version: Optional[str] = None


class TallyDataCacheResponse(TallyDataCacheBase):
    id: int
    organization_id: int
    cached_at: datetime
    access_count: int
    last_accessed: Optional[datetime]
    
    class Config:
        from_attributes = True


# Tally Error Log Schemas
class TallyErrorLogBase(BaseModel):
    error_type: str = Field(..., description="Error type")
    error_code: Optional[str] = Field(None, description="Error code")
    error_message: str = Field(..., description="Error message")
    operation: Optional[str] = Field(None, description="Operation")
    entity_type: Optional[str] = Field(None, description="Entity type")
    entity_reference: Optional[str] = Field(None, description="Entity reference")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    severity: str = Field("error", description="Severity")


class TallyErrorLogCreate(TallyErrorLogBase):
    pass


class TallyErrorLogUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class TallyErrorLogResponse(TallyErrorLogBase):
    id: int
    organization_id: int
    is_resolved: bool
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    occurred_at: datetime
    
    class Config:
        from_attributes = True


# Tally Integration Operations Schemas
class TallyConnectionTest(BaseModel):
    """Schema for testing Tally connection"""
    host: str = Field(..., description="Tally server host")
    port: int = Field(..., description="Tally server port")
    company_name: str = Field(..., description="Company name in Tally")
    username: Optional[str] = Field(None, description="Username")
    password: Optional[str] = Field(None, description="Password")


class TallyConnectionTestResponse(BaseModel):
    """Response for Tally connection test"""
    success: bool = Field(..., description="Connection successful")
    message: str = Field(..., description="Connection message")
    company_info: Optional[Dict[str, Any]] = Field(None, description="Company information")
    tally_version: Optional[str] = Field(None, description="Tally version")
    error_details: Optional[str] = Field(None, description="Error details")


class TallySyncRequest(BaseModel):
    """Request to trigger Tally sync"""
    sync_type: str = Field(..., description="Sync type (ledgers, vouchers, full_sync)")
    sync_direction: Optional[SyncDirectionEnum] = Field(None, description="Sync direction")
    entity_ids: Optional[List[int]] = Field(None, description="Specific entity IDs to sync")
    force_sync: bool = Field(False, description="Force sync even if recently synced")


class TallySyncResponse(BaseModel):
    """Response for Tally sync request"""
    sync_log_id: int = Field(..., description="Sync log ID")
    message: str = Field(..., description="Sync message")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")


class TallyMasterData(BaseModel):
    """Schema for Tally master data"""
    ledgers: List[Dict[str, Any]] = Field(default_factory=list, description="Ledger data")
    voucher_types: List[Dict[str, Any]] = Field(default_factory=list, description="Voucher type data")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Item data")
    companies: List[Dict[str, Any]] = Field(default_factory=list, description="Company data")


class TallyLedgerData(BaseModel):
    """Schema for Tally ledger data"""
    name: str = Field(..., description="Ledger name")
    guid: Optional[str] = Field(None, description="Ledger GUID")
    parent: Optional[str] = Field(None, description="Parent ledger")
    alias: Optional[str] = Field(None, description="Alias")
    opening_balance: Optional[float] = Field(None, description="Opening balance")
    closing_balance: Optional[float] = Field(None, description="Closing balance")
    is_revenue: Optional[bool] = Field(None, description="Is revenue ledger")
    is_deemedpositive: Optional[bool] = Field(None, description="Is deemed positive")


class TallyVoucherData(BaseModel):
    """Schema for Tally voucher data"""
    guid: Optional[str] = Field(None, description="Voucher GUID")
    voucher_type: str = Field(..., description="Voucher type")
    voucher_number: str = Field(..., description="Voucher number")
    date: str = Field(..., description="Voucher date")
    narration: Optional[str] = Field(None, description="Narration")
    amount: float = Field(..., description="Amount")
    ledger_entries: List[Dict[str, Any]] = Field(default_factory=list, description="Ledger entries")


# Tally Analytics Schemas
class TallySyncAnalytics(BaseModel):
    """Analytics for Tally sync operations"""
    total_syncs: int = Field(..., description="Total sync operations")
    successful_syncs: int = Field(..., description="Successful syncs")
    failed_syncs: int = Field(..., description="Failed syncs")
    last_sync_date: Optional[datetime] = Field(None, description="Last sync date")
    average_sync_duration: Optional[float] = Field(None, description="Average sync duration")
    sync_frequency: Dict[str, int] = Field(default_factory=dict, description="Sync frequency by type")
    error_frequency: Dict[str, int] = Field(default_factory=dict, description="Error frequency by type")


class TallyIntegrationDashboard(BaseModel):
    """Dashboard data for Tally integration"""
    connection_status: TallyConnectionStatusEnum = Field(..., description="Connection status")
    sync_analytics: TallySyncAnalytics = Field(..., description="Sync analytics")
    recent_errors: List[TallyErrorLogResponse] = Field(default_factory=list, description="Recent errors")
    pending_syncs: int = Field(..., description="Pending syncs")
    data_freshness: Dict[str, datetime] = Field(default_factory=dict, description="Data freshness by type")
    organization_id: int = Field(..., description="Organization ID")


# Added missing schema for TallyConfig to match usage in settings_routes.py
class TallyConfig(BaseModel):
    """Simple Tally configuration schema for organization settings"""
    enabled: bool = Field(False, description="Enable Tally integration")
    host: str = Field("localhost", description="Tally server host")
    port: int = Field(9000, description="Tally server port")
    company_name: str = Field("", description="Company name in Tally")
    sync_frequency: str = Field("manual", description="Sync frequency (manual, daily, etc.)")
    last_sync: Optional[datetime] = Field(None, description="Last sync timestamp")

    class Config:
        from_attributes = True