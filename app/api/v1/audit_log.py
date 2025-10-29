"""
Audit Log API endpoints
Provides audit log access and export functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.audit_log import AuditLog, AuditLogView, AuditLogExport

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry"""
    entity_type: str
    entity_id: Optional[int] = None
    entity_name: Optional[str] = None
    action: str
    action_description: Optional[str] = None
    actor_type: str = "user"
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    ai_agent_id: Optional[int] = None
    automation_workflow_id: Optional[int] = None
    triggered_by_automation: bool = False
    changes: Optional[Dict[str, Any]] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    severity: str = "info"
    compliance_tags: Optional[list] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    organization_id: Optional[int]
    entity_type: str
    entity_id: Optional[int]
    entity_name: Optional[str]
    action: str
    action_description: Optional[str]
    user_id: Optional[int]
    actor_type: str
    actor_id: Optional[int]
    actor_name: Optional[str]
    ai_agent_id: Optional[int]
    automation_workflow_id: Optional[int]
    triggered_by_automation: bool
    changes: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    success: bool
    severity: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogFilterRequest(BaseModel):
    """Schema for filtering audit logs"""
    entity_types: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    actor_types: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_ids: Optional[List[int]] = None
    ai_agent_ids: Optional[List[int]] = None
    triggered_by_automation: Optional[bool] = None
    success: Optional[bool] = None


class AuditLogExportRequest(BaseModel):
    """Schema for exporting audit logs"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
    format: str = Field(default="csv", description="Export format: csv, json, pdf")
    include_metadata: bool = True


class AuditLogExportResponse(BaseModel):
    """Schema for audit log export response"""
    id: int
    organization_id: int
    status: str
    record_count: Optional[int]
    file_path: Optional[str]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    log_data: AuditLogCreate,
    auth: tuple = Depends(require_access("audit_log", "create")),
    db: Session = Depends(get_db)
):
    """
    Create a new audit log entry.
    """
    try:
        audit_log = AuditLog(
            organization_id=org_id,
            entity_type=log_data.entity_type,
            entity_id=log_data.entity_id,
            entity_name=log_data.entity_name,
            action=log_data.action,
            action_description=log_data.action_description,
            user_id=current_user.id,
            actor_type=log_data.actor_type,
            actor_id=log_data.actor_id or current_user.id,
            actor_name=log_data.actor_name or current_user.username,
            ai_agent_id=log_data.ai_agent_id,
            automation_workflow_id=log_data.automation_workflow_id,
            triggered_by_automation=log_data.triggered_by_automation,
            changes=log_data.changes,
            old_values=log_data.old_values,
            new_values=log_data.new_values,
            context=log_data.context,
            metadata=log_data.metadata,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            request_method=log_data.request_method,
            request_path=log_data.request_path,
            success=log_data.success,
            error_message=log_data.error_message,
            severity=log_data.severity,
            compliance_tags=log_data.compliance_tags
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating audit log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit log: {str(e)}"
        )


@router.post("/query", response_model=List[AuditLogResponse])
async def query_audit_logs(
    filter_request: AuditLogFilterRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("audit_log", "read")),
    db: Session = Depends(get_db)
):
    """
    Query audit logs with filters.
    """
    try:
        query = db.query(AuditLog).filter(
            AuditLog.organization_id == org_id
        )
        
        # Apply filters
        if filter_request.entity_types:
            query = query.filter(AuditLog.entity_type.in_(filter_request.entity_types))
        
        if filter_request.actions:
            query = query.filter(AuditLog.action.in_(filter_request.actions))
        
        if filter_request.actor_types:
            query = query.filter(AuditLog.actor_type.in_(filter_request.actor_types))
        
        if filter_request.severity_levels:
            query = query.filter(AuditLog.severity.in_(filter_request.severity_levels))
        
        if filter_request.start_date:
            query = query.filter(AuditLog.timestamp >= filter_request.start_date)
        
        if filter_request.end_date:
            query = query.filter(AuditLog.timestamp <= filter_request.end_date)
        
        if filter_request.user_ids:
            query = query.filter(AuditLog.user_id.in_(filter_request.user_ids))
        
        if filter_request.ai_agent_ids:
            query = query.filter(AuditLog.ai_agent_id.in_(filter_request.ai_agent_ids))
        
        if filter_request.triggered_by_automation is not None:
            query = query.filter(AuditLog.triggered_by_automation == filter_request.triggered_by_automation)
        
        if filter_request.success is not None:
            query = query.filter(AuditLog.success == filter_request.success)
        
        logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.id} queried {len(logs)} audit logs")
        return logs
        
    except Exception as e:
        logger.error(f"Error querying audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query audit logs: {str(e)}"
        )


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    actor_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    auth: tuple = Depends(require_access("audit_log", "read")),
    db: Session = Depends(get_db)
):
    """
    List audit logs for the organization.
    """
    try:
        query = db.query(AuditLog).filter(
            AuditLog.organization_id == org_id
        )
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if actor_type:
            query = query.filter(AuditLog.actor_type == actor_type)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        return logs
        
    except Exception as e:
        logger.error(f"Error listing audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audit logs: {str(e)}"
        )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    auth: tuple = Depends(require_access("audit_log", "read")),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific audit log entry.
    """
    try:
        log = db.query(AuditLog).filter(
            and_(
                AuditLog.id == log_id,
                AuditLog.organization_id == org_id
            )
        ).first()
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found"
            )
        
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit log: {str(e)}"
        )


# ============================================================================
# Audit Log Statistics Endpoints
# ============================================================================

@router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365),
    auth: tuple = Depends(require_access("audit_log", "read")),
    db: Session = Depends(get_db)
):
    """
    Get audit log statistics for the organization.
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.organization_id == org_id,
                AuditLog.timestamp >= start_date
            )
        )
        
        total_logs = query.count()
        
        # Count by action
        action_counts = db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.organization_id == org_id,
                AuditLog.timestamp >= start_date
            )
        ).group_by(AuditLog.action).all()
        
        # Count by actor type
        actor_type_counts = db.query(
            AuditLog.actor_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            and_(
                AuditLog.organization_id == org_id,
                AuditLog.timestamp >= start_date
            )
        ).group_by(AuditLog.actor_type).all()
        
        # Count failures
        failed_count = query.filter(AuditLog.success == False).count()
        
        # Count automation-triggered
        automation_count = query.filter(AuditLog.triggered_by_automation == True).count()
        
        return {
            "period_days": days,
            "total_logs": total_logs,
            "failed_count": failed_count,
            "automation_triggered_count": automation_count,
            "success_rate": ((total_logs - failed_count) / total_logs * 100) if total_logs > 0 else 0,
            "actions": {action: count for action, count in action_counts},
            "actor_types": {actor_type: count for actor_type, count in actor_type_counts}
        }
        
    except Exception as e:
        logger.error(f"Error getting audit statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit statistics: {str(e)}"
        )


# ============================================================================
# Audit Log Export Endpoints
# ============================================================================

@router.post("/export", response_model=AuditLogExportResponse, status_code=status.HTTP_201_CREATED)
async def request_audit_log_export(
    export_request: AuditLogExportRequest,
    auth: tuple = Depends(require_access("audit_log", "create")),
    db: Session = Depends(get_db)
):
    """
    Request an audit log export.
    """
    try:
        export = AuditLogExport(
            organization_id=org_id,
            requested_by=current_user.id,
            start_date=export_request.start_date,
            end_date=export_request.end_date,
            filters=export_request.filters,
            format=export_request.format,
            include_metadata=export_request.include_metadata,
            status="pending"
        )
        
        db.add(export)
        db.commit()
        db.refresh(export)
        
        logger.info(f"User {current_user.id} requested audit log export {export.id}")
        
        # TODO: Trigger background job to generate export
        
        return export
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error requesting export: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request export: {str(e)}"
        )


@router.get("/exports", response_model=List[AuditLogExportResponse])
async def list_audit_log_exports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("audit_log", "read")),
    db: Session = Depends(get_db)
):
    """
    List audit log export requests.
    """
    try:
        exports = db.query(AuditLogExport).filter(
            AuditLogExport.organization_id == org_id
        ).order_by(desc(AuditLogExport.created_at)).offset(skip).limit(limit).all()
        
        return exports
        
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list exports: {str(e)}"
        )
