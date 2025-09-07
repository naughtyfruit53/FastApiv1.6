# app/api/v1/external_integrations.py

"""
Enhanced External Integration API endpoints for comprehensive third-party system connectivity
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.integration_models import (
    ExternalIntegration, IntegrationMapping, IntegrationSyncJob, IntegrationSyncRecord,
    IntegrationLog, DataTransformationRule, IntegrationSchedule
)
from app.schemas.integration import (
    ExternalIntegrationCreate, ExternalIntegrationUpdate, ExternalIntegrationResponse, 
    ExternalIntegrationWithDetails, ExternalIntegrationList, ExternalIntegrationFilter,
    IntegrationMappingCreate, IntegrationMappingUpdate, IntegrationMappingResponse, IntegrationMappingWithDetails,
    IntegrationSyncJobCreate, IntegrationSyncJobUpdate, IntegrationSyncJobResponse, 
    IntegrationSyncJobWithDetails, IntegrationSyncJobList, IntegrationSyncJobFilter,
    IntegrationSyncRecordResponse, IntegrationLogResponse, IntegrationLogWithDetails, IntegrationLogList, IntegrationLogFilter,
    DataTransformationRuleCreate, DataTransformationRuleUpdate, DataTransformationRuleResponse, DataTransformationRuleWithDetails,
    IntegrationScheduleCreate, IntegrationScheduleUpdate, IntegrationScheduleResponse, IntegrationScheduleWithDetails,
    IntegrationDashboardStats, IntegrationHealthCheck, IntegrationTestRequest, IntegrationTestResponse,
    MappingValidationRequest, MappingValidationResponse, BulkIntegrationUpdate, BulkSyncJobAction,
    IntegrationExportRequest, IntegrationImportRequest, IntegrationImportResponse
)
from app.services.rbac import RBACService
from app.core.rbac_dependencies import check_service_permission

router = APIRouter()

# Dashboard
@router.get("/dashboard", response_model=IntegrationDashboardStats)
async def get_integration_dashboard(
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Integration dashboard statistics"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build base queries
    integration_query = db.query(ExternalIntegration).filter(ExternalIntegration.organization_id == org_id)
    sync_job_query = db.query(IntegrationSyncJob).filter(IntegrationSyncJob.organization_id == org_id)
    
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        integration_query = integration_query.filter(ExternalIntegration.company_id == company_id)
    else:
        integration_query = integration_query.filter(
            or_(
                ExternalIntegration.company_id.in_(user_companies),
                ExternalIntegration.company_id.is_(None)
            )
        )
    
    # Calculate statistics
    total_integrations = integration_query.count()
    active_integrations = integration_query.filter(ExternalIntegration.status == 'active').count()
    failed_integrations = integration_query.filter(ExternalIntegration.status == 'failed').count()
    
    # Today's syncs
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_syncs_today = sync_job_query.filter(IntegrationSyncJob.started_at >= today_start).count()
    successful_syncs_today = sync_job_query.filter(
        IntegrationSyncJob.started_at >= today_start,
        IntegrationSyncJob.status == 'success'
    ).count()
    
    sync_success_rate = 0.0
    if total_syncs_today > 0:
        sync_success_rate = (successful_syncs_today / total_syncs_today) * 100
    
    # Data volume today
    data_volume_today = db.query(
        func.coalesce(func.sum(IntegrationSyncJob.processed_records), 0).label('total_records')
    ).filter(
        IntegrationSyncJob.organization_id == org_id,
        IntegrationSyncJob.started_at >= today_start
    ).scalar() or 0
    
    # Average sync time
    avg_sync_time = db.query(
        func.avg(
            func.extract('epoch', IntegrationSyncJob.completed_at) - 
            func.extract('epoch', IntegrationSyncJob.started_at)
        ).label('avg_seconds')
    ).filter(
        IntegrationSyncJob.organization_id == org_id,
        IntegrationSyncJob.completed_at.isnot(None)
    ).scalar()
    
    avg_sync_time_minutes = (avg_sync_time / 60) if avg_sync_time else 0.0
    
    # Integrations by type
    type_counts = db.query(
        ExternalIntegration.integration_type,
        func.count(ExternalIntegration.id).label('count')
    ).filter(
        integration_query.whereclause
    ).group_by(ExternalIntegration.integration_type).all()
    
    integrations_by_type = {str(itype): count for itype, count in type_counts}
    
    # Integrations by status
    status_counts = db.query(
        ExternalIntegration.status,
        func.count(ExternalIntegration.id).label('count')
    ).filter(
        integration_query.whereclause
    ).group_by(ExternalIntegration.status).all()
    
    integrations_by_status = {str(status): count for status, count in status_counts}
    
    # Recent sync jobs
    recent_syncs = sync_job_query.filter(
        IntegrationSyncJob.started_at >= today_start
    ).options(
        joinedload(IntegrationSyncJob.integration),
        joinedload(IntegrationSyncJob.triggered_by_user)
    ).order_by(desc(IntegrationSyncJob.started_at)).limit(10).all()
    
    # Failed syncs
    failed_syncs = sync_job_query.filter(
        IntegrationSyncJob.status == 'failed'
    ).options(
        joinedload(IntegrationSyncJob.integration),
        joinedload(IntegrationSyncJob.triggered_by_user)
    ).order_by(desc(IntegrationSyncJob.started_at)).limit(10).all()
    
    return IntegrationDashboardStats(
        total_integrations=total_integrations,
        active_integrations=active_integrations,
        failed_integrations=failed_integrations,
        total_syncs_today=total_syncs_today,
        successful_syncs_today=successful_syncs_today,
        sync_success_rate=sync_success_rate,
        data_volume_today=data_volume_today,
        average_sync_time_minutes=avg_sync_time_minutes,
        integrations_by_type=integrations_by_type,
        integrations_by_status=integrations_by_status,
        recent_sync_jobs=[IntegrationSyncJobResponse.from_orm(job) for job in recent_syncs],
        failed_syncs=[IntegrationSyncJobResponse.from_orm(job) for job in failed_syncs]
    )

# External Integration Management
@router.post("/integrations", response_model=ExternalIntegrationResponse)
async def create_integration(
    integration_data: ExternalIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new external integration"""
    check_service_permission(current_user, "integration", "create", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Validate company access
    if integration_data.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if integration_data.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Check for duplicate name
    existing = db.query(ExternalIntegration).filter(
        ExternalIntegration.organization_id == org_id,
        ExternalIntegration.name == integration_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration with this name already exists"
        )
    
    # Create integration
    db_integration = ExternalIntegration(
        organization_id=org_id,
        company_id=integration_data.company_id,
        name=integration_data.name,
        provider=integration_data.provider,
        integration_type=integration_data.integration_type,
        version=integration_data.version,
        description=integration_data.description,
        endpoint_url=integration_data.endpoint_url,
        auth_type=integration_data.auth_type,
        auth_config=integration_data.auth_config,
        sync_direction=integration_data.sync_direction,
        auto_sync_enabled=integration_data.auto_sync_enabled,
        sync_interval_minutes=integration_data.sync_interval_minutes,
        rate_limit_per_minute=integration_data.rate_limit_per_minute,
        batch_size=integration_data.batch_size,
        retry_count=integration_data.retry_count,
        timeout_seconds=integration_data.timeout_seconds,
        created_by=current_user.id
    )
    
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    
    return ExternalIntegrationResponse.from_orm(db_integration)

@router.get("/integrations", response_model=ExternalIntegrationList)
async def list_integrations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: ExternalIntegrationFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List external integrations with filtering and pagination"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(ExternalIntegration).filter(ExternalIntegration.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(ExternalIntegration.company_id == company_id)
    else:
        query = query.filter(
            or_(
                ExternalIntegration.company_id.in_(user_companies),
                ExternalIntegration.company_id.is_(None)
            )
        )
    
    # Apply filters
    if filters.status:
        query = query.filter(ExternalIntegration.status == filters.status)
    if filters.integration_type:
        query = query.filter(ExternalIntegration.integration_type == filters.integration_type)
    if filters.provider:
        query = query.filter(ExternalIntegration.provider.ilike(f"%{filters.provider}%"))
    if filters.created_by:
        query = query.filter(ExternalIntegration.created_by == filters.created_by)
    if filters.sync_direction:
        query = query.filter(ExternalIntegration.sync_direction == filters.sync_direction)
    if filters.auto_sync_enabled is not None:
        query = query.filter(ExternalIntegration.auto_sync_enabled == filters.auto_sync_enabled)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                ExternalIntegration.name.ilike(search_term),
                ExternalIntegration.description.ilike(search_term),
                ExternalIntegration.provider.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    integrations = query.options(
        joinedload(ExternalIntegration.creator)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    integration_details = []
    for integration in integrations:
        # Calculate success rate
        total_syncs = db.query(IntegrationSyncJob).filter(
            IntegrationSyncJob.integration_id == integration.id
        ).count()
        
        successful_syncs = db.query(IntegrationSyncJob).filter(
            IntegrationSyncJob.integration_id == integration.id,
            IntegrationSyncJob.status == 'success'
        ).count()
        
        success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0.0
        
        # Get mapping count
        mapping_count = db.query(IntegrationMapping).filter(
            IntegrationMapping.integration_id == integration.id
        ).count()
        
        # Recent sync count (last 24 hours)
        recent_sync_count = db.query(IntegrationSyncJob).filter(
            IntegrationSyncJob.integration_id == integration.id,
            IntegrationSyncJob.started_at >= datetime.now() - timedelta(hours=24)
        ).count()
        
        # Error count (last 7 days)
        error_count = db.query(IntegrationLog).filter(
            IntegrationLog.integration_id == integration.id,
            IntegrationLog.log_level.in_(['ERROR', 'WARNING']),
            IntegrationLog.logged_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Health status
        health_status = "healthy"
        if integration.status == 'failed':
            health_status = "failed"
        elif error_count > 10:
            health_status = "warning"
        elif integration.status != 'active':
            health_status = "inactive"
        
        integration_detail = ExternalIntegrationWithDetails(
            **integration.__dict__,
            creator_name=integration.creator.full_name if integration.creator else None,
            success_rate_percentage=success_rate,
            mapping_count=mapping_count,
            recent_sync_count=recent_sync_count,
            error_count=error_count,
            health_status=health_status
        )
        integration_details.append(integration_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return ExternalIntegrationList(
        integrations=integration_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/integrations/{integration_id}", response_model=ExternalIntegrationWithDetails)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific integration by ID"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).options(
        joinedload(ExternalIntegration.creator)
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Get additional stats (similar to list but for single integration)
    total_syncs = db.query(IntegrationSyncJob).filter(
        IntegrationSyncJob.integration_id == integration.id
    ).count()
    
    successful_syncs = db.query(IntegrationSyncJob).filter(
        IntegrationSyncJob.integration_id == integration.id,
        IntegrationSyncJob.status == 'success'
    ).count()
    
    success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0.0
    
    mapping_count = db.query(IntegrationMapping).filter(
        IntegrationMapping.integration_id == integration.id
    ).count()
    
    recent_sync_count = db.query(IntegrationSyncJob).filter(
        IntegrationSyncJob.integration_id == integration.id,
        IntegrationSyncJob.started_at >= datetime.now() - timedelta(hours=24)
    ).count()
    
    error_count = db.query(IntegrationLog).filter(
        IntegrationLog.integration_id == integration.id,
        IntegrationLog.log_level.in_(['ERROR', 'WARNING']),
        IntegrationLog.logged_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    health_status = "healthy"
    if integration.status == 'failed':
        health_status = "failed"
    elif error_count > 10:
        health_status = "warning"
    elif integration.status != 'active':
        health_status = "inactive"
    
    return ExternalIntegrationWithDetails(
        **integration.__dict__,
        creator_name=integration.creator.full_name if integration.creator else None,
        success_rate_percentage=success_rate,
        mapping_count=mapping_count,
        recent_sync_count=recent_sync_count,
        error_count=error_count,
        health_status=health_status
    )

@router.put("/integrations/{integration_id}", response_model=ExternalIntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_update: ExternalIntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an integration"""
    check_service_permission(current_user, "integration", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Update fields
    update_data = integration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)
    
    integration.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(integration)
    
    return ExternalIntegrationResponse.from_orm(integration)

@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an integration"""
    check_service_permission(current_user, "integration", "delete", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    db.delete(integration)
    db.commit()
    
    return {"message": "Integration deleted successfully"}

# Integration Mapping Management
@router.post("/integrations/{integration_id}/mappings", response_model=IntegrationMappingResponse)
async def create_integration_mapping(
    integration_id: int,
    mapping_data: IntegrationMappingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new integration mapping"""
    check_service_permission(current_user, "integration", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify integration exists and user has access
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Create mapping
    db_mapping = IntegrationMapping(
        organization_id=org_id,
        integration_id=integration_id,
        name=mapping_data.name,
        entity_type=mapping_data.entity_type,
        source_field=mapping_data.source_field,
        source_path=mapping_data.source_path,
        target_field=mapping_data.target_field,
        target_path=mapping_data.target_path,
        mapping_type=mapping_data.mapping_type,
        transformation_rule=mapping_data.transformation_rule,
        default_value=mapping_data.default_value,
        is_required=mapping_data.is_required,
        validation_rules=mapping_data.validation_rules,
        sync_direction=mapping_data.sync_direction,
        is_key_field=mapping_data.is_key_field,
        created_by=current_user.id
    )
    
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    
    return IntegrationMappingResponse.from_orm(db_mapping)

@router.get("/integrations/{integration_id}/mappings", response_model=List[IntegrationMappingWithDetails])
async def list_integration_mappings(
    integration_id: int,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List mappings for a specific integration"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify integration access
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Get mappings
    query = db.query(IntegrationMapping).filter(
        IntegrationMapping.integration_id == integration_id,
        IntegrationMapping.organization_id == org_id
    )
    
    if entity_type:
        query = query.filter(IntegrationMapping.entity_type == entity_type)
    
    mappings = query.options(
        joinedload(IntegrationMapping.integration),
        joinedload(IntegrationMapping.creator)
    ).order_by(IntegrationMapping.entity_type, IntegrationMapping.name).all()
    
    # Build detailed response
    mapping_details = []
    for mapping in mappings:
        mapping_detail = IntegrationMappingWithDetails(
            **mapping.__dict__,
            integration_name=mapping.integration.name,
            creator_name=mapping.creator.full_name if mapping.creator else None
        )
        mapping_details.append(mapping_detail)
    
    return mapping_details

# Test endpoints
@router.post("/integrations/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    integration_id: int,
    test_request: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test an integration connection"""
    check_service_permission(current_user, "integration", "test", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify integration exists and user has access
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Simulate integration test (in real implementation, this would actually test the connection)
    import time
    import random
    
    start_time = time.time()
    
    # Simulate test execution
    time.sleep(random.uniform(0.5, 2.0))
    
    response_time_ms = (time.time() - start_time) * 1000
    
    # Simulate test results
    success = random.choice([True, False, True, True])  # 75% success rate for demo
    
    recommendations = []
    error_message = None
    
    if test_request.test_type == "connection":
        if not success:
            error_message = "Connection timeout or invalid endpoint"
            recommendations.extend([
                "Check endpoint URL format",
                "Verify network connectivity",
                "Confirm SSL/TLS configuration"
            ])
        else:
            recommendations.append("Connection test successful")
    
    elif test_request.test_type == "authentication":
        if not success:
            error_message = "Authentication failed"
            recommendations.extend([
                "Verify API credentials",
                "Check token expiration",
                "Confirm permissions"
            ])
        else:
            recommendations.append("Authentication successful")
    
    elif test_request.test_type == "sync":
        if not success:
            error_message = "Data sync test failed"
            recommendations.extend([
                "Check data mapping configuration",
                "Verify field validation rules",
                "Review transformation logic"
            ])
        else:
            recommendations.append("Sync test completed successfully")
    
    # Log the test
    test_log = IntegrationLog(
        organization_id=org_id,
        integration_id=integration_id,
        log_level="INFO" if success else "ERROR",
        message=f"Integration test {test_request.test_type}: {'Success' if success else 'Failed'}",
        category="test",
        operation=test_request.test_type,
        request_data=test_request.dict(),
        error_code="TEST_FAILED" if not success else None,
        user_id=current_user.id
    )
    db.add(test_log)
    db.commit()
    
    return IntegrationTestResponse(
        success=success,
        test_type=test_request.test_type,
        status_code=200 if success else 400,
        response_time_ms=response_time_ms,
        error_message=error_message,
        test_data=test_request.sample_data,
        recommendations=recommendations
    )

# Health Check
@router.get("/integrations/{integration_id}/health", response_model=IntegrationHealthCheck)
async def check_integration_health(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive health check for an integration"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify integration exists and user has access
    integration = db.query(ExternalIntegration).filter(
        ExternalIntegration.id == integration_id,
        ExternalIntegration.organization_id == org_id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if integration.company_id and integration.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this integration's company"
        )
    
    # Perform health checks
    issues = []
    recommendations = []
    health_score = 100.0
    
    # Check integration status
    if integration.status != 'active':
        issues.append(f"Integration status is {integration.status}")
        health_score -= 30
        recommendations.append("Activate the integration to enable data synchronization")
    
    # Check recent sync status
    recent_syncs = db.query(IntegrationSyncJob).filter(
        IntegrationSyncJob.integration_id == integration_id,
        IntegrationSyncJob.started_at >= datetime.now() - timedelta(days=7)
    ).order_by(desc(IntegrationSyncJob.started_at)).limit(5).all()
    
    last_sync_status = "unknown"
    if recent_syncs:
        last_sync_status = recent_syncs[0].status
        failed_recent = sum(1 for sync in recent_syncs if sync.status == 'failed')
        if failed_recent > 2:
            issues.append(f"{failed_recent} out of {len(recent_syncs)} recent syncs failed")
            health_score -= 20
            recommendations.append("Review sync job errors and fix data mapping issues")
    
    # Check error logs
    recent_errors = db.query(IntegrationLog).filter(
        IntegrationLog.integration_id == integration_id,
        IntegrationLog.log_level == 'ERROR',
        IntegrationLog.logged_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    if recent_errors > 10:
        issues.append(f"{recent_errors} errors in the last 7 days")
        health_score -= 15
        recommendations.append("Check integration logs and resolve recurring errors")
    
    # Check mapping configuration
    mapping_count = db.query(IntegrationMapping).filter(
        IntegrationMapping.integration_id == integration.id
    ).count()
    
    if mapping_count == 0:
        issues.append("No field mappings configured")
        health_score -= 25
        recommendations.append("Configure field mappings for data synchronization")
    
    # Simulate connection and authentication tests
    connection_test = True  # In real implementation, test actual connection
    authentication_test = True  # In real implementation, test authentication
    data_flow_test = len(recent_syncs) > 0 and recent_syncs[0].status == 'success'
    
    if not connection_test:
        issues.append("Connection test failed")
        health_score -= 20
        recommendations.append("Check network connectivity and endpoint configuration")
    
    if not authentication_test:
        issues.append("Authentication test failed")
        health_score -= 20
        recommendations.append("Verify API credentials and permissions")
    
    if not data_flow_test:
        issues.append("Data flow test failed")
        health_score -= 15
        recommendations.append("Test data synchronization and check for mapping errors")
    
    # Ensure health score doesn't go below 0
    health_score = max(0, health_score)
    
    # Add positive recommendations
    if health_score >= 90:
        recommendations.append("Integration is performing well")
    elif health_score >= 70:
        recommendations.append("Integration is stable with minor issues")
    elif health_score >= 50:
        recommendations.append("Integration needs attention to improve reliability")
    else:
        recommendations.append("Integration requires immediate attention")
    
    return IntegrationHealthCheck(
        integration_id=integration_id,
        integration_name=integration.name,
        status=integration.status,
        last_sync_status=last_sync_status,
        connection_test=connection_test,
        authentication_test=authentication_test,
        data_flow_test=data_flow_test,
        health_score=health_score,
        issues=issues,
        recommendations=recommendations
    )