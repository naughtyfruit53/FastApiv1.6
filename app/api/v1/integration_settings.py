# app/api/v1/integration_settings.py
"""
Integration Settings API endpoints - Unified integration management for organization settings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import User, Organization
from app.models.tally_models import TallyConfiguration, TallyLedgerMapping, TallyVoucherMapping, TallySyncLog, TallyErrorLog
from app.schemas.tally import (
    TallyConfigurationCreate, TallyConfigurationUpdate, TallyConfigurationResponse,
    TallyConnectionTest, TallyConnectionTestResponse, TallyIntegrationDashboard
)
from app.schemas.migration import IntegrationDashboardResponse, IntegrationHealthStatus
from app.services.tally_service import TallyIntegrationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Integration Permissions Management
@router.get("/permissions")
async def get_integration_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get integration permissions for current user"""
    # Check what integrations the user can manage
    permissions = {
        "can_manage_tally": current_user.is_super_admin,  # Only super admin by default
        "can_view_tally": current_user.is_super_admin,
        "can_manage_email": current_user.is_super_admin,
        "can_view_email": True,  # All users can view email status
        "can_manage_calendar": current_user.is_super_admin,
        "can_view_calendar": True,
        "can_manage_payments": current_user.is_super_admin,
        "can_view_payments": current_user.is_super_admin,
        "can_manage_zoho": current_user.is_super_admin,
        "can_view_zoho": current_user.is_super_admin,
        "can_manage_migration": current_user.is_super_admin,
        "can_view_migration": True
    }
    
    # TODO: Implement more granular RBAC permissions
    # This could be extended to allow super admins to grant specific permissions to other users
    
    return {"permissions": permissions}


@router.post("/permissions/grant")
async def grant_integration_permission(
    user_id: int,
    integration: str,
    permission_type: str,  # manage, view
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Grant integration permission to user (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Only organization super admins can grant integration permissions"
        )
    
    # Validate inputs
    valid_integrations = ['tally', 'email', 'calendar', 'payments', 'zoho', 'migration']
    valid_permissions = ['manage', 'view']
    
    if integration not in valid_integrations:
        raise HTTPException(status_code=400, detail=f"Invalid integration: {integration}")
    
    if permission_type not in valid_permissions:
        raise HTTPException(status_code=400, detail=f"Invalid permission type: {permission_type}")
    
    # Check if user exists in organization
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.organization_id == organization_id
        )
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")
    
    # TODO: Implement actual permission storage
    # For now, return success message
    return {
        "message": f"Granted {permission_type} permission for {integration} to user {user.email}",
        "user_id": user_id,
        "integration": integration,
        "permission_type": permission_type
    }


@router.delete("/permissions/revoke")
async def revoke_integration_permission(
    user_id: int,
    integration: str,
    permission_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Revoke integration permission from user (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Only organization super admins can revoke integration permissions"
        )
    
    # Validate inputs
    valid_integrations = ['tally', 'email', 'calendar', 'payments', 'zoho', 'migration']
    valid_permissions = ['manage', 'view']
    
    if integration not in valid_integrations:
        raise HTTPException(status_code=400, detail=f"Invalid integration: {integration}")
    
    if permission_type not in valid_permissions:
        raise HTTPException(status_code=400, detail=f"Invalid permission type: {permission_type}")
    
    # Check if user exists in organization
    user = db.query(User).filter(
        and_(
            User.id == user_id,
            User.organization_id == organization_id
        )
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in organization")
    
    # TODO: Implement actual permission removal
    return {
        "message": f"Revoked {permission_type} permission for {integration} from user {user.email}",
        "user_id": user_id,
        "integration": integration,
        "permission_type": permission_type
    }


# Tally Integration Settings (Moved from separate endpoint)
@router.get("/tally/configuration", response_model=Optional[TallyConfigurationResponse])
async def get_tally_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get Tally configuration for organization settings"""
    # Check permissions
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_view_tally"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view Tally configuration")
    
    config = db.query(TallyConfiguration).filter(
        TallyConfiguration.organization_id == organization_id
    ).first()
    
    return config


@router.post("/tally/configuration", response_model=TallyConfigurationResponse)
async def create_tally_configuration(
    config_data: TallyConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create Tally configuration in organization settings"""
    # Check permissions
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_manage_tally"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to manage Tally configuration")
    
    # Check if configuration already exists
    existing_config = db.query(TallyConfiguration).filter(
        TallyConfiguration.organization_id == organization_id
    ).first()
    
    if existing_config:
        raise HTTPException(status_code=400, detail="Tally configuration already exists for this organization")
    
    # Create configuration
    config = TallyConfiguration(
        organization_id=organization_id,
        **config_data.dict()
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    logger.info(f"Created Tally configuration for org {organization_id} by user {current_user.id}")
    return config


@router.put("/tally/configuration", response_model=TallyConfigurationResponse)
async def update_tally_configuration(
    config_update: TallyConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update Tally configuration in organization settings"""
    # Check permissions
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_manage_tally"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to manage Tally configuration")
    
    config = db.query(TallyConfiguration).filter(
        TallyConfiguration.organization_id == organization_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Tally configuration not found")
    
    # Update configuration
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    logger.info(f"Updated Tally configuration for org {organization_id} by user {current_user.id}")
    return config


@router.delete("/tally/configuration")
async def delete_tally_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete Tally configuration from organization settings"""
    # Check permissions
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_manage_tally"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to manage Tally configuration")
    
    config = db.query(TallyConfiguration).filter(
        TallyConfiguration.organization_id == organization_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Tally configuration not found")
    
    db.delete(config)
    db.commit()
    
    logger.info(f"Deleted Tally configuration for org {organization_id} by user {current_user.id}")
    return {"message": "Tally configuration deleted successfully"}


@router.post("/tally/test-connection", response_model=TallyConnectionTestResponse)
async def test_tally_connection(
    connection_test: TallyConnectionTest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Test Tally connection from organization settings"""
    # Check permissions
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_manage_tally"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to test Tally connection")
    
    tally_service = TallyIntegrationService()
    result = await tally_service.test_tally_connection(connection_test)
    
    return result


# Unified Integration Dashboard
@router.get("/dashboard", response_model=IntegrationDashboardResponse)
async def get_integrations_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get unified integrations dashboard"""
    permissions = await get_integration_permissions_internal(current_user)
    
    # Get Tally integration status
    tally_status = await get_tally_integration_health(db, organization_id, permissions["can_view_tally"])
    
    # Get other integration statuses (placeholder implementations)
    email_status = IntegrationHealthStatus(
        integration_name="Email",
        status="healthy",
        last_sync_at=datetime.utcnow() - timedelta(minutes=5),
        sync_frequency="Real-time",
        error_count=0,
        configuration_valid=True,
        performance_metrics={"avg_response_time": "50ms"}
    )
    
    calendar_status = IntegrationHealthStatus(
        integration_name="Calendar",
        status="healthy",
        last_sync_at=datetime.utcnow() - timedelta(minutes=2),
        sync_frequency="Every 5 minutes",
        error_count=0,
        configuration_valid=True,
        performance_metrics={"sync_success_rate": "99.9%"}
    )
    
    payment_status = IntegrationHealthStatus(
        integration_name="Payments",
        status="disabled",
        configuration_valid=False,
        performance_metrics={}
    )
    
    zoho_status = IntegrationHealthStatus(
        integration_name="Zoho",
        status="disabled",
        configuration_valid=False,
        performance_metrics={}
    )
    
    # Get migration statistics
    from app.services.migration_service import MigrationService
    migration_service = MigrationService(db)
    
    # Simple migration stats
    migration_stats = {
        "total_jobs": 0,
        "active_jobs": 0,
        "completed_jobs": 0,
        "failed_jobs": 0,
        "total_records_migrated": 0,
        "success_rate": 0.0,
        "average_processing_time": 0.0,
        "most_used_source_types": {},
        "recent_activity": []
    }
    
    system_health = {
        "database_status": "healthy",
        "api_response_time": "45ms",
        "last_backup": datetime.utcnow() - timedelta(hours=6),
        "storage_usage": "45%"
    }
    
    return IntegrationDashboardResponse(
        tally_integration=tally_status,
        email_integration=email_status,
        calendar_integration=calendar_status,
        payment_integration=payment_status,
        zoho_integration=zoho_status,
        migration_statistics=migration_stats,
        system_health=system_health
    )


# Email Integration Settings (Placeholder)
@router.get("/email/status")
async def get_email_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get email integration status"""
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_view_email"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view email integration")
    
    return {
        "status": "healthy",
        "smtp_configured": True,
        "imap_configured": True,
        "last_email_sent": datetime.utcnow() - timedelta(minutes=5),
        "daily_email_count": 45,
        "monthly_quota": 10000,
        "quota_used": 450
    }


# Calendar Integration Settings (Placeholder)
@router.get("/calendar/status")
async def get_calendar_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get calendar integration status"""
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_view_calendar"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view calendar integration")
    
    return {
        "status": "healthy",
        "google_calendar_connected": True,
        "outlook_calendar_connected": False,
        "last_sync": datetime.utcnow() - timedelta(minutes=2),
        "events_synced_today": 12,
        "sync_errors": 0
    }


# Payment Integration Settings (Placeholder)
@router.get("/payments/status")
async def get_payment_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get payment integration status"""
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_view_payments"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view payment integration")
    
    return {
        "status": "disabled",
        "razorpay_configured": False,
        "stripe_configured": False,
        "paypal_configured": False,
        "last_transaction": None,
        "monthly_volume": 0
    }


# Zoho Integration Settings (Placeholder)
@router.get("/zoho/status")
async def get_zoho_integration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get Zoho integration status"""
    permissions = await get_integration_permissions_internal(current_user)
    if not permissions["can_view_zoho"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view Zoho integration")
    
    return {
        "status": "disabled",
        "zoho_crm_connected": False,
        "zoho_books_connected": False,
        "zoho_inventory_connected": False,
        "last_sync": None,
        "sync_errors": 0
    }


# Helper Functions
async def get_integration_permissions_internal(user: User) -> Dict[str, bool]:
    """Internal helper to get integration permissions"""
    return {
        "can_manage_tally": user.is_super_admin,
        "can_view_tally": user.is_super_admin,
        "can_manage_email": user.is_super_admin,
        "can_view_email": True,
        "can_manage_calendar": user.is_super_admin,
        "can_view_calendar": True,
        "can_manage_payments": user.is_super_admin,
        "can_view_payments": user.is_super_admin,
        "can_manage_zoho": user.is_super_admin,
        "can_view_zoho": user.is_super_admin,
        "can_manage_migration": user.is_super_admin,
        "can_view_migration": True
    }


async def get_tally_integration_health(db: Session, organization_id: int, can_view: bool) -> IntegrationHealthStatus:
    """Get Tally integration health status"""
    if not can_view:
        return IntegrationHealthStatus(
            integration_name="Tally",
            status="disabled",
            configuration_valid=False,
            performance_metrics={}
        )
    
    # Get Tally configuration
    config = db.query(TallyConfiguration).filter(
        TallyConfiguration.organization_id == organization_id
    ).first()
    
    if not config:
        return IntegrationHealthStatus(
            integration_name="Tally",
            status="disabled",
            configuration_valid=False,
            performance_metrics={}
        )
    
    # Get recent sync status
    recent_sync = db.query(TallySyncLog).filter(
        TallySyncLog.organization_id == organization_id
    ).order_by(desc(TallySyncLog.created_at)).first()
    
    # Get error count
    error_count = db.query(TallyErrorLog).filter(
        and_(
            TallyErrorLog.organization_id == organization_id,
            TallyErrorLog.created_at >= datetime.utcnow() - timedelta(days=1)
        )
    ).count()
    
    # Determine status
    status = "healthy"
    if error_count > 10:
        status = "error"
    elif error_count > 5:
        status = "warning"
    elif not config.is_enabled:
        status = "disabled"
    
    return IntegrationHealthStatus(
        integration_name="Tally",
        status=status,
        last_sync_at=recent_sync.created_at if recent_sync else None,
        sync_frequency="Manual/On-demand",
        error_count=error_count,
        last_error=None,  # TODO: Get last error message
        configuration_valid=True,
        performance_metrics={
            "last_sync_duration": "30s",
            "records_synced": recent_sync.processed_items if recent_sync else 0
        }
    )