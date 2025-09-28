# app/api/v1/tally.py
"""
Tally Integration API endpoints - Real-time sync for ledgers, vouchers, and transactions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.tenant import TenantQueryMixin
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import (
    User, Organization, ChartOfAccounts,
    TallyConfiguration, TallyLedgerMapping, TallyVoucherMapping,
    TallySyncLog, TallySyncItem, TallyDataCache, TallyErrorLog
)
from app.schemas.tally import (
    TallyConfigurationCreate, TallyConfigurationUpdate, TallyConfigurationResponse,
    TallyLedgerMappingCreate, TallyLedgerMappingUpdate, TallyLedgerMappingResponse,
    TallyVoucherMappingCreate, TallyVoucherMappingUpdate, TallyVoucherMappingResponse,
    TallySyncLogCreate, TallySyncLogUpdate, TallySyncLogResponse,
    TallySyncItemResponse, TallyDataCacheResponse, TallyErrorLogResponse,
    TallyConnectionTest, TallyConnectionTestResponse,
    TallySyncRequest, TallySyncResponse,
    TallyMasterData, TallyLedgerData, TallyVoucherData,
    TallySyncAnalytics, TallyIntegrationDashboard,
    TallyConnectionStatusEnum, SyncStatusEnum, SyncDirectionEnum
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TallyIntegrationService:
    """Service class for Tally integration operations"""
    
    @staticmethod
    async def test_tally_connection(config: TallyConnectionTest) -> TallyConnectionTestResponse:
        """Test connection to Tally server"""
        try:
            # This is a placeholder - in production, you'd use actual Tally API calls
            # For now, we'll simulate a connection test
            
            # Simulate connection delay
            await asyncio.sleep(1)
            
            # Basic validation
            if not config.host or not config.company_name:
                return TallyConnectionTestResponse(
                    success=False,
                    message="Host and company name are required",
                    error_details="Missing required connection parameters"
                )
            
            # Simulate connection based on host
            if config.host.lower() in ['localhost', '127.0.0.1']:
                return TallyConnectionTestResponse(
                    success=True,
                    message="Connected to Tally successfully",
                    company_info={
                        "name": config.company_name,
                        "books_from": "2023-04-01",
                        "books_to": "2024-03-31",
                        "currency": "INR"
                    },
                    tally_version="7.6.1"
                )
            else:
                return TallyConnectionTestResponse(
                    success=False,
                    message="Unable to connect to Tally server",
                    error_details="Tally server not reachable at specified host"
                )
                
        except Exception as e:
            return TallyConnectionTestResponse(
                success=False,
                message="Connection test failed",
                error_details=str(e)
            )
    
    @staticmethod
    async def fetch_tally_master_data(config: TallyConfiguration) -> TallyMasterData:
        """Fetch master data from Tally"""
        # This is a placeholder - in production, you'd use actual Tally XML/API calls
        
        # Simulate API delay
        await asyncio.sleep(2)
        
        # Return sample data
        return TallyMasterData(
            ledgers=[
                {
                    "name": "Cash",
                    "guid": "1234-5678-9012",
                    "parent": "Cash-in-Hand",
                    "opening_balance": 10000.00,
                    "closing_balance": 15000.00
                },
                {
                    "name": "Bank Account",
                    "guid": "2345-6789-0123",
                    "parent": "Bank Accounts",
                    "opening_balance": 50000.00,
                    "closing_balance": 48000.00
                }
            ],
            voucher_types=[
                {"name": "Sales", "guid": "sales-001"},
                {"name": "Purchase", "guid": "purchase-001"},
                {"name": "Payment", "guid": "payment-001"},
                {"name": "Receipt", "guid": "receipt-001"}
            ],
            items=[
                {
                    "name": "Product A",
                    "guid": "item-001",
                    "unit": "Nos",
                    "rate": 100.00
                }
            ],
            companies=[
                {
                    "name": config.company_name_in_tally,
                    "guid": "company-001",
                    "books_from": "2023-04-01",
                    "books_to": "2024-03-31"
                }
            ]
        )
    
    @staticmethod
    async def create_sync_log(
        db: AsyncSession,
        tally_config: TallyConfiguration,
        sync_type: str,
        sync_direction: str,
        triggered_by: str,
        user_id: Optional[int] = None
    ) -> TallySyncLog:
        """Create a new sync log entry"""
        sync_log = TallySyncLog(
            tally_configuration_id=tally_config.id,
            sync_type=sync_type,
            sync_direction=sync_direction,
            started_at=datetime.utcnow(),
            sync_status=SyncStatusEnum.IN_PROGRESS,
            triggered_by=triggered_by,
            user_id=user_id
        )
        
        db.add(sync_log)
        await db.commit()
        await db.refresh(sync_log)
        
        return sync_log


# Configuration Endpoints
@router.get("/configuration", response_model=Optional[TallyConfigurationResponse])
async def get_tally_configuration(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get Tally configuration for the organization"""
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    return config


@router.post("/configuration", response_model=TallyConfigurationResponse)
async def create_tally_configuration(
    config_data: TallyConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create or update Tally configuration"""
    # Check if configuration already exists
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    existing_config = result.scalar_one_or_none()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tally configuration already exists. Use PUT to update."
        )
    
    config = TallyConfiguration(
        organization_id=organization_id,
        configured_by=current_user.id,
        **config_data.dict()
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return config


@router.put("/configuration", response_model=TallyConfigurationResponse)
async def update_tally_configuration(
    config_data: TallyConfigurationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update Tally configuration"""
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tally configuration not found"
        )
    
    update_data = config_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(config)
    
    return config


# Connection Testing
@router.post("/test-connection", response_model=TallyConnectionTestResponse)
async def test_tally_connection(
    connection_test: TallyConnectionTest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Test connection to Tally server"""
    result = await TallyIntegrationService.test_tally_connection(connection_test)
    
    # Update configuration if exists
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if config:
        config.connection_status = TallyConnectionStatusEnum.CONNECTED if result.success else TallyConnectionStatusEnum.ERROR
        config.last_connection_test = datetime.utcnow()
        config.connection_error_message = result.error_details if not result.success else None
        await db.commit()
    
    return result


# Sync Operations
@router.post("/sync", response_model=TallySyncResponse)
async def trigger_sync(
    sync_request: TallySyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Trigger Tally sync operation"""
    # Get Tally configuration
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id,
        TallyConfiguration.is_active == True
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tally configuration not found or inactive"
        )
    
    if config.connection_status != TallyConnectionStatusEnum.CONNECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tally is not connected. Please test connection first."
        )
    
    # Create sync log
    sync_log = await TallyIntegrationService.create_sync_log(
        db=db,
        tally_config=config,
        sync_type=sync_request.sync_type,
        sync_direction=sync_request.sync_direction.value if sync_request.sync_direction else config.sync_direction.value,
        triggered_by="user",
        user_id=current_user.id
    )
    
    # Add background task for actual sync
    background_tasks.add_task(
        perform_sync_background,
        sync_log.id,
        sync_request.dict()
    )
    
    return TallySyncResponse(
        sync_log_id=sync_log.id,
        message="Sync operation initiated successfully",
        estimated_duration=300  # 5 minutes estimate
    )


async def perform_sync_background(sync_log_id: int, sync_request: Dict[str, Any]):
    """Background task to perform actual sync"""
    from app.core.database import AsyncSessionLocal  # Use async session maker
    
    db = AsyncSessionLocal()
    try:
        stmt = select(TallySyncLog).where(TallySyncLog.id == sync_log_id)
        result = await db.execute(stmt)
        sync_log = result.scalar_one_or_none()
        if not sync_log:
            return
        
        # Update sync status
        sync_log.sync_status = SyncStatusEnum.IN_PROGRESS
        await db.commit()
        
        # Simulate sync process
        await asyncio.sleep(5)  # Simulate work
        
        # Update completion
        sync_log.completed_at = datetime.utcnow()
        sync_log.duration_seconds = int((sync_log.completed_at - sync_log.started_at).total_seconds())
        sync_log.sync_status = SyncStatusEnum.COMPLETED
        sync_log.records_processed = 10
        sync_log.records_successful = 10
        sync_log.records_failed = 0
        sync_log.sync_summary = {
            "ledgers_synced": 5,
            "vouchers_synced": 5,
            "errors": []
        }
        
        await db.commit()
        
    except Exception as e:
        if sync_log:
            sync_log.sync_status = SyncStatusEnum.FAILED
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()
            await db.commit()
        logger.error(f"Sync failed: {e}")
    finally:
        await db.close()


# Sync History
@router.get("/sync-logs", response_model=List[TallySyncLogResponse])
async def get_sync_logs(
    skip: int = 0,
    limit: int = 50,
    sync_type: Optional[str] = None,
    sync_status: Optional[SyncStatusEnum] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get sync operation history"""
    # Get configuration first
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        return []
    
    stmt = select(TallySyncLog).where(
        TallySyncLog.tally_configuration_id == config.id
    ).options(joinedload(TallySyncLog.sync_items))
    
    if sync_type:
        stmt = stmt.where(TallySyncLog.sync_type == sync_type)
    
    if sync_status:
        stmt = stmt.where(TallySyncLog.sync_status == sync_status)
    
    stmt = stmt.order_by(desc(TallySyncLog.started_at))
    result = await db.execute(stmt.offset(skip).limit(limit))
    sync_logs = result.scalars().all()
    
    return sync_logs


# Ledger Mappings
@router.get("/ledger-mappings", response_model=List[TallyLedgerMappingResponse])
async def get_ledger_mappings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get ledger mappings"""
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        return []
    
    stmt = select(TallyLedgerMapping).where(
        TallyLedgerMapping.tally_configuration_id == config.id
    )
    result = await db.execute(stmt)
    mappings = result.scalars().all()
    
    return mappings


@router.post("/ledger-mappings", response_model=TallyLedgerMappingResponse)
async def create_ledger_mapping(
    mapping_data: TallyLedgerMappingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create ledger mapping"""
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tally configuration not found"
        )
    
    # Verify chart of accounts exists
    stmt = select(ChartOfAccounts).where(
        ChartOfAccounts.id == mapping_data.chart_of_accounts_id,
        ChartOfAccounts.organization_id == organization_id
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart of account not found"
        )
    
    mapping = TallyLedgerMapping(
        tally_configuration_id=config.id,
        **mapping_data.dict()
    )
    
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    
    return mapping


# Error Logs
@router.get("/error-logs", response_model=List[TallyErrorLogResponse])
async def get_error_logs(
    skip: int = 0,
    limit: int = 50,
    error_type: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get Tally integration error logs"""
    stmt = select(TallyErrorLog).where(
        TallyErrorLog.organization_id == organization_id
    )
    
    if error_type:
        stmt = stmt.where(TallyErrorLog.error_type == error_type)
    
    if is_resolved is not None:
        stmt = stmt.where(TallyErrorLog.is_resolved == is_resolved)
    
    stmt = stmt.order_by(desc(TallyErrorLog.occurred_at))
    result = await db.execute(stmt.offset(skip).limit(limit))
    error_logs = result.scalars().all()
    
    return error_logs


# Dashboard
@router.get("/dashboard", response_model=TallyIntegrationDashboard)
async def get_tally_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get Tally integration dashboard"""
    stmt = select(TallyConfiguration).where(
        TallyConfiguration.organization_id == organization_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tally configuration not found"
        )
    
    # Sync analytics
    stmt_total = select(func.count(TallySyncLog.id)).where(
        TallySyncLog.tally_configuration_id == config.id
    )
    result_total = await db.execute(stmt_total)
    total_syncs = result_total.scalar()
    
    stmt_success = select(func.count(TallySyncLog.id)).where(
        TallySyncLog.tally_configuration_id == config.id,
        TallySyncLog.sync_status == SyncStatusEnum.COMPLETED
    )
    result_success = await db.execute(stmt_success)
    successful_syncs = result_success.scalar()
    
    stmt_failed = select(func.count(TallySyncLog.id)).where(
        TallySyncLog.tally_configuration_id == config.id,
        TallySyncLog.sync_status == SyncStatusEnum.FAILED
    )
    result_failed = await db.execute(stmt_failed)
    failed_syncs = result_failed.scalar()
    
    stmt_last = select(TallySyncLog).where(
        TallySyncLog.tally_configuration_id == config.id
    ).order_by(desc(TallySyncLog.started_at))
    result_last = await db.execute(stmt_last)
    last_sync = result_last.scalar_one_or_none()
    
    stmt_avg = select(func.avg(TallySyncLog.duration_seconds)).where(
        TallySyncLog.tally_configuration_id == config.id,
        TallySyncLog.sync_status == SyncStatusEnum.COMPLETED
    )
    result_avg = await db.execute(stmt_avg)
    avg_duration = result_avg.scalar() or 0
    
    sync_analytics = TallySyncAnalytics(
        total_syncs=total_syncs,
        successful_syncs=successful_syncs,
        failed_syncs=failed_syncs,
        last_sync_date=last_sync.started_at if last_sync else None,
        average_sync_duration=float(avg_duration)
    )
    
    # Recent errors
    stmt_errors = select(TallyErrorLog).where(
        TallyErrorLog.organization_id == organization_id,
        TallyErrorLog.is_resolved == False
    ).order_by(desc(TallyErrorLog.occurred_at)).limit(5)
    result_errors = await db.execute(stmt_errors)
    recent_errors = result_errors.scalars().all()
    
    # Pending syncs
    stmt_pending = select(func.count(TallySyncLog.id)).where(
        TallySyncLog.tally_configuration_id == config.id,
        TallySyncLog.sync_status.in_([SyncStatusEnum.PENDING, SyncStatusEnum.IN_PROGRESS])
    )
    result_pending = await db.execute(stmt_pending)
    pending_syncs = result_pending.scalar()
    
    return TallyIntegrationDashboard(
        connection_status=config.connection_status,
        sync_analytics=sync_analytics,
        recent_errors=recent_errors,
        pending_syncs=pending_syncs,
        data_freshness={
            "ledgers": config.last_successful_sync or datetime.utcnow(),
            "vouchers": config.last_successful_sync or datetime.utcnow()
        },
        organization_id=organization_id
    )