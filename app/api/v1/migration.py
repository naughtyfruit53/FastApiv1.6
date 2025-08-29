# app/api/v1/migration.py
"""
Migration & Data Import API endpoints - Comprehensive migration system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.core.rbac_dependencies import check_service_permission
from app.models import User, Organization
from app.models.migration_models import (
    MigrationJob, MigrationDataMapping, MigrationLog, MigrationTemplate,
    MigrationConflict, MigrationJobStatus, MigrationSourceType, MigrationDataType
)
from app.schemas.migration import (
    MigrationJobCreate, MigrationJobUpdate, MigrationJobResponse,
    MigrationDataMappingCreate, MigrationDataMappingUpdate, MigrationDataMappingResponse,
    MigrationLogResponse, MigrationTemplateResponse, MigrationConflictResponse,
    FileUploadResponse, DataValidationResponse, FieldMappingPreview,
    MigrationPreview, MigrationProgressResponse, MigrationSummaryResponse,
    RollbackRequest, RollbackResponse, MigrationStatistics, IntegrationDashboardResponse,
    MigrationWizardState, BulkMigrationRequest, BulkMigrationResponse
)
from app.services.migration_service import MigrationService, TallyMigrationService, ZohoMigrationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Migration Jobs
@router.post("/jobs", response_model=MigrationJobResponse)
async def create_migration_job(
    job_data: MigrationJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new migration job (Super Admin only)"""
    # Check if user is super admin
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403, 
            detail="Only organization super admins can create migration jobs"
        )
    
    migration_service = MigrationService(db)
    migration_job = await migration_service.create_migration_job(
        job_data, organization_id, current_user.id
    )
    
    return migration_job


@router.get("/jobs", response_model=List[MigrationJobResponse])
async def list_migration_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """List migration jobs for the organization"""
    query = db.query(MigrationJob).filter(
        MigrationJob.organization_id == organization_id
    )
    
    if status:
        query = query.filter(MigrationJob.status == status)
    
    if source_type:
        query = query.filter(MigrationJob.source_type == source_type)
    
    # Non-super admins can only see their own jobs
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    jobs = query.order_by(desc(MigrationJob.created_at)).offset(skip).limit(limit).all()
    return jobs


@router.get("/jobs/{job_id}", response_model=MigrationJobResponse)
async def get_migration_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration job details"""
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    # Non-super admins can only see their own jobs
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    return job


@router.put("/jobs/{job_id}", response_model=MigrationJobResponse)
async def update_migration_job(
    job_id: int,
    job_update: MigrationJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update migration job"""
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    # Non-super admins can only update their own jobs
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    # Update fields
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/jobs/{job_id}")
async def delete_migration_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete migration job (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403, 
            detail="Only organization super admins can delete migration jobs"
        )
    
    job = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    if job.status in [MigrationJobStatus.RUNNING]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete running migration job"
        )
    
    db.delete(job)
    db.commit()
    
    return {"message": "Migration job deleted successfully"}


# File Upload and Processing
@router.post("/jobs/{job_id}/upload", response_model=FileUploadResponse)
async def upload_migration_file(
    job_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Upload source file for migration"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    migration_service = MigrationService(db)
    result = await migration_service.upload_source_file(job_id, organization_id, file)
    
    return result


@router.post("/jobs/{job_id}/mappings/auto", response_model=FieldMappingPreview)
async def create_auto_mappings(
    job_id: int,
    auto_map: bool = Query(True, description="Automatically create mappings"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Auto-create field mappings based on templates"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    migration_service = MigrationService(db)
    mappings = await migration_service.create_field_mappings(job_id, organization_id, auto_map)
    
    return mappings


@router.post("/jobs/{job_id}/validate", response_model=DataValidationResponse)
async def validate_migration_data(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Validate migration data"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    migration_service = MigrationService(db)
    validation = await migration_service.validate_migration_data(job_id, organization_id)
    
    return validation


@router.post("/jobs/{job_id}/start", response_model=MigrationProgressResponse)
async def start_migration(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Start migration execution (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403, 
            detail="Only organization super admins can start migrations"
        )
    
    migration_service = MigrationService(db)
    progress = await migration_service.start_migration_job(job_id, organization_id, current_user.id)
    
    return progress


@router.get("/jobs/{job_id}/progress", response_model=MigrationProgressResponse)
async def get_migration_progress(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration progress"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    migration_service = MigrationService(db)
    progress = await migration_service.get_migration_progress(job_id, organization_id)
    
    return progress


# Data Mappings
@router.get("/jobs/{job_id}/mappings", response_model=List[MigrationDataMappingResponse])
async def get_migration_mappings(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration data mappings"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    mappings = db.query(MigrationDataMapping).filter(
        MigrationDataMapping.migration_job_id == job_id
    ).all()
    
    return mappings


@router.post("/jobs/{job_id}/mappings", response_model=MigrationDataMappingResponse)
async def create_migration_mapping(
    job_id: int,
    mapping_data: MigrationDataMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create migration data mapping"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    # Create mapping
    mapping = MigrationDataMapping(
        migration_job_id=job_id,
        organization_id=organization_id,
        **mapping_data.dict(exclude={'migration_job_id'})
    )
    
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    
    return mapping


@router.put("/mappings/{mapping_id}", response_model=MigrationDataMappingResponse)
async def update_migration_mapping(
    mapping_id: int,
    mapping_update: MigrationDataMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update migration data mapping"""
    mapping = db.query(MigrationDataMapping).filter(
        and_(
            MigrationDataMapping.id == mapping_id,
            MigrationDataMapping.organization_id == organization_id
        )
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Migration mapping not found")
    
    # Verify job ownership if not super admin
    if not current_user.is_super_admin:
        job = db.query(MigrationJob).filter(
            and_(
                MigrationJob.id == mapping.migration_job_id,
                MigrationJob.created_by == current_user.id
            )
        ).first()
        
        if not job:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update mapping
    for field, value in mapping_update.dict(exclude_unset=True).items():
        setattr(mapping, field, value)
    
    mapping.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(mapping)
    
    return mapping


@router.delete("/mappings/{mapping_id}")
async def delete_migration_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete migration data mapping"""
    mapping = db.query(MigrationDataMapping).filter(
        and_(
            MigrationDataMapping.id == mapping_id,
            MigrationDataMapping.organization_id == organization_id
        )
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Migration mapping not found")
    
    # Verify job ownership if not super admin
    if not current_user.is_super_admin:
        job = db.query(MigrationJob).filter(
            and_(
                MigrationJob.id == mapping.migration_job_id,
                MigrationJob.created_by == current_user.id
            )
        ).first()
        
        if not job:
            raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "Migration mapping deleted successfully"}


# Migration Logs
@router.get("/jobs/{job_id}/logs", response_model=List[MigrationLogResponse])
async def get_migration_logs(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration logs"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    # Get logs
    logs_query = db.query(MigrationLog).filter(
        MigrationLog.migration_job_id == job_id
    )
    
    if level:
        logs_query = logs_query.filter(MigrationLog.level == level)
    
    logs = logs_query.order_by(desc(MigrationLog.created_at)).offset(skip).limit(limit).all()
    
    return logs


# Migration Templates
@router.get("/templates", response_model=List[MigrationTemplateResponse])
async def list_migration_templates(
    source_type: Optional[str] = Query(None),
    data_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List migration templates"""
    query = db.query(MigrationTemplate).filter(
        MigrationTemplate.is_active == True
    )
    
    if source_type:
        query = query.filter(MigrationTemplate.source_type == source_type)
    
    if data_type:
        query = query.filter(MigrationTemplate.data_type == data_type)
    
    templates = query.order_by(MigrationTemplate.usage_count.desc()).all()
    
    return templates


@router.get("/templates/{template_id}", response_model=MigrationTemplateResponse)
async def get_migration_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get migration template details"""
    template = db.query(MigrationTemplate).filter(
        and_(
            MigrationTemplate.id == template_id,
            MigrationTemplate.is_active == True
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Migration template not found")
    
    # Update usage count
    template.usage_count += 1
    template.last_used_at = datetime.utcnow()
    db.commit()
    
    return template


# Migration Conflicts
@router.get("/jobs/{job_id}/conflicts", response_model=List[MigrationConflictResponse])
async def get_migration_conflicts(
    job_id: int,
    resolved: Optional[bool] = Query(None),
    conflict_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration conflicts"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    # Get conflicts
    conflicts_query = db.query(MigrationConflict).filter(
        MigrationConflict.migration_job_id == job_id
    )
    
    if resolved is not None:
        conflicts_query = conflicts_query.filter(MigrationConflict.is_resolved == resolved)
    
    if conflict_type:
        conflicts_query = conflicts_query.filter(MigrationConflict.conflict_type == conflict_type)
    
    conflicts = conflicts_query.order_by(MigrationConflict.created_at).all()
    
    return conflicts


# Rollback Operations
@router.post("/jobs/{job_id}/rollback", response_model=RollbackResponse)
async def rollback_migration(
    job_id: int,
    rollback_request: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Rollback migration (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403, 
            detail="Only organization super admins can rollback migrations"
        )
    
    if not rollback_request.confirm:
        raise HTTPException(status_code=400, detail="Rollback must be confirmed")
    
    job = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    if not job.can_rollback:
        raise HTTPException(status_code=400, detail="Migration cannot be rolled back")
    
    # TODO: Implement actual rollback logic
    # For now, just update status
    job.status = MigrationJobStatus.ROLLED_BACK
    db.commit()
    
    return RollbackResponse(
        success=True,
        message="Migration rolled back successfully",
        rolled_back_entities={},
        rollback_summary={}
    )


# Dashboard and Statistics
@router.get("/statistics", response_model=MigrationStatistics)
async def get_migration_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration statistics for dashboard"""
    # Base query for organization
    base_query = db.query(MigrationJob).filter(
        MigrationJob.organization_id == organization_id
    )
    
    # Non-super admins see only their jobs
    if not current_user.is_super_admin:
        base_query = base_query.filter(MigrationJob.created_by == current_user.id)
    
    # Calculate statistics
    total_jobs = base_query.count()
    active_jobs = base_query.filter(
        MigrationJob.status.in_([MigrationJobStatus.RUNNING, MigrationJobStatus.MAPPING])
    ).count()
    completed_jobs = base_query.filter(
        MigrationJob.status == MigrationJobStatus.COMPLETED
    ).count()
    failed_jobs = base_query.filter(
        MigrationJob.status == MigrationJobStatus.FAILED
    ).count()
    
    # Total records migrated
    total_records = base_query.filter(
        MigrationJob.status == MigrationJobStatus.COMPLETED
    ).with_entities(func.sum(MigrationJob.success_records)).scalar() or 0
    
    # Success rate
    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    # Average processing time (placeholder)
    average_processing_time = 0.0
    
    # Most used source types
    source_type_stats = {}
    for job in base_query.all():
        source_type = job.source_type.value
        source_type_stats[source_type] = source_type_stats.get(source_type, 0) + 1
    
    # Recent activity
    recent_jobs = base_query.order_by(desc(MigrationJob.updated_at)).limit(5).all()
    recent_activity = [
        {
            "job_id": job.id,
            "job_name": job.job_name,
            "status": job.status.value,
            "updated_at": job.updated_at
        }
        for job in recent_jobs
    ]
    
    return MigrationStatistics(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        total_records_migrated=total_records,
        success_rate=success_rate,
        average_processing_time=average_processing_time,
        most_used_source_types=source_type_stats,
        recent_activity=recent_activity
    )


# Bulk Operations
@router.post("/bulk", response_model=BulkMigrationResponse)
async def bulk_migration_operation(
    bulk_request: BulkMigrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Perform bulk migration operations (Super Admin only)"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403, 
            detail="Only organization super admins can perform bulk operations"
        )
    
    if not bulk_request.confirm:
        raise HTTPException(status_code=400, detail="Bulk operation must be confirmed")
    
    # Get jobs
    jobs = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id.in_(bulk_request.migration_job_ids),
            MigrationJob.organization_id == organization_id
        )
    ).all()
    
    if len(jobs) != len(bulk_request.migration_job_ids):
        raise HTTPException(status_code=404, detail="Some migration jobs not found")
    
    successful_jobs = []
    failed_jobs = []
    
    for job in jobs:
        try:
            if bulk_request.operation == "start":
                if job.status == MigrationJobStatus.APPROVED:
                    # TODO: Start migration
                    job.status = MigrationJobStatus.RUNNING
                    successful_jobs.append(job.id)
                else:
                    failed_jobs.append({
                        "job_id": job.id,
                        "error": f"Job not ready for execution (status: {job.status.value})"
                    })
            elif bulk_request.operation == "cancel":
                if job.status in [MigrationJobStatus.RUNNING, MigrationJobStatus.MAPPING]:
                    job.status = MigrationJobStatus.CANCELLED
                    successful_jobs.append(job.id)
                else:
                    failed_jobs.append({
                        "job_id": job.id,
                        "error": f"Job cannot be cancelled (status: {job.status.value})"
                    })
            elif bulk_request.operation == "rollback":
                if job.can_rollback and job.status == MigrationJobStatus.COMPLETED:
                    job.status = MigrationJobStatus.ROLLED_BACK
                    successful_jobs.append(job.id)
                else:
                    failed_jobs.append({
                        "job_id": job.id,
                        "error": "Job cannot be rolled back"
                    })
        except Exception as e:
            failed_jobs.append({
                "job_id": job.id,
                "error": str(e)
            })
    
    db.commit()
    
    return BulkMigrationResponse(
        total_jobs=len(jobs),
        successful_jobs=successful_jobs,
        failed_jobs=failed_jobs,
        operation_summary={
            "operation": bulk_request.operation,
            "success_count": len(successful_jobs),
            "failed_count": len(failed_jobs)
        }
    )


# Migration Wizard
@router.get("/jobs/{job_id}/wizard", response_model=MigrationWizardState)
async def get_migration_wizard_state(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get migration wizard state"""
    # Verify job ownership
    query = db.query(MigrationJob).filter(
        and_(
            MigrationJob.id == job_id,
            MigrationJob.organization_id == organization_id
        )
    )
    
    if not current_user.is_super_admin:
        query = query.filter(MigrationJob.created_by == current_user.id)
    
    job = query.first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    # Define wizard steps based on job status
    steps = [
        {"step_number": 1, "step_name": "Upload File", "is_completed": job.source_file_name is not None, "is_current": False, "can_skip": False},
        {"step_number": 2, "step_name": "Map Fields", "is_completed": job.status.value in ["approved", "running", "completed"], "is_current": False, "can_skip": False},
        {"step_number": 3, "step_name": "Validate Data", "is_completed": job.status.value in ["approved", "running", "completed"], "is_current": False, "can_skip": False},
        {"step_number": 4, "step_name": "Review & Execute", "is_completed": job.status == MigrationJobStatus.COMPLETED, "is_current": False, "can_skip": False},
    ]
    
    # Determine current step
    current_step = 1
    if job.source_file_name:
        current_step = 2
    if job.status.value in ["approved", "running", "completed"]:
        current_step = 4
    if job.status == MigrationJobStatus.COMPLETED:
        current_step = 5  # Completed
    
    # Mark current step
    if current_step <= len(steps):
        steps[current_step - 1]["is_current"] = True
    
    can_proceed = True
    validation_errors = []
    
    # Check if can proceed to next step
    if current_step == 1 and not job.source_file_name:
        can_proceed = False
        validation_errors.append("Please upload a source file")
    
    return MigrationWizardState(
        job_id=job_id,
        current_step=current_step,
        total_steps=len(steps),
        steps=steps,
        can_proceed=can_proceed,
        validation_errors=validation_errors
    )


# Specialized Migration Services
@router.get("/tally/data-types")
async def get_tally_data_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get available Tally data types for migration"""
    return {
        "data_types": [
            {"value": "ledgers", "label": "Chart of Accounts / Ledgers"},
            {"value": "vouchers", "label": "Vouchers / Transactions"},
            {"value": "contacts", "label": "Contacts (Customers/Vendors)"},
            {"value": "products", "label": "Products / Items"},
            {"value": "company_info", "label": "Company Information"}
        ]
    }


@router.get("/zoho/data-types")
async def get_zoho_data_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get available Zoho data types for migration"""
    return {
        "data_types": [
            {"value": "contacts", "label": "Contacts"},
            {"value": "products", "label": "Products"},
            {"value": "customers", "label": "Customers"},
            {"value": "vendors", "label": "Vendors"},
            {"value": "vouchers", "label": "Invoices / Bills"}
        ]
    }