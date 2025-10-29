"""
ML Analytics API endpoints for Advanced Machine Learning and Predictive Analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.services.ml_analytics_service import MLAnalyticsService
from app.schemas.ml_analytics import (
    PredictiveModelCreate, PredictiveModelUpdate, PredictiveModelResponse,
    AnomalyDetectionModelCreate, AnomalyDetectionModelUpdate, AnomalyDetectionModelResponse,
    AnomalyDetectionResultResponse, AnomalyResolutionRequest,
    ExternalDataSourceCreate, ExternalDataSourceUpdate, ExternalDataSourceResponse,
    PredictionRequest, PredictionResponse, PredictionHistoryResponse,
    MLAnalyticsDashboard, ModelTrainingRequest, ModelTrainingStatus,
    ModelDeploymentRequest, AdvancedAnalyticsRequest, AdvancedAnalyticsResponse,
    PredictiveModelTypeEnum, AnomalyTypeEnum, DataSourceTypeEnum, SeverityLevelEnum
)

router = APIRouter()


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard", response_model=MLAnalyticsDashboard)
async def get_ml_analytics_dashboard(
    auth: tuple = Depends(require_access("ml_analytics", "read")),
    db: Session = Depends(get_db)
):
    """Get ML analytics dashboard data"""
    current_user, org_id = auth
    
    service = MLAnalyticsService(db)
    dashboard_data = service.get_ml_analytics_dashboard(org_id)
    
    return MLAnalyticsDashboard(**dashboard_data)


# ============================================================================
# PREDICTIVE MODEL ENDPOINTS
# ============================================================================

@router.post("/models/predictive", response_model=PredictiveModelResponse, status_code=201)
async def create_predictive_model(
    model_data: PredictiveModelCreate,
    auth: tuple = Depends(require_access("ml_analytics", "create")),
    db: Session = Depends(get_db)
):
    """Create a new predictive model"""
    current_user, org_id = auth
    
    service = MLAnalyticsService(db)
    model = service.create_predictive_model(
        organization_id=org_id,
        model_data=model_data,
        created_by_id=current_user.id
    )
    
    return PredictiveModelResponse.from_orm(model)


@router.get("/models/predictive", response_model=List[PredictiveModelResponse])
async def get_predictive_models(
    model_type: Optional[PredictiveModelTypeEnum] = Query(None, description="Filter by model type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    auth: tuple = Depends(require_access("ml_analytics", "read")),
    db: Session = Depends(get_db)
):
    """Get all predictive models for the organization"""
    current_user, org_id = auth
    
    service = MLAnalyticsService(db)
    models = service.get_predictive_models(
        organization_id=organization_id,
        model_type=model_type,
        is_active=is_active
    )
    
    return [PredictiveModelResponse.from_orm(model) for model in models]


@router.get("/models/predictive/{model_id}", response_model=PredictiveModelResponse)
async def get_predictive_model(
    model_id: int = Path(..., description="Predictive model ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    model = service.get_predictive_model(organization_id, model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Predictive model not found")
    
    return PredictiveModelResponse.from_orm(model)


@router.put("/models/predictive/{model_id}", response_model=PredictiveModelResponse)
async def update_predictive_model(
    model_id: int,
    model_data: PredictiveModelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:update", db)
    
    service = MLAnalyticsService(db)
    model = service.update_predictive_model(
        organization_id=organization_id,
        model_id=model_id,
        model_data=model_data,
        updated_by_id=current_user.id
    )
    
    if not model:
        raise HTTPException(status_code=404, detail="Predictive model not found")
    
    return PredictiveModelResponse.from_orm(model)


@router.delete("/models/predictive/{model_id}", status_code=204)
async def delete_predictive_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:delete", db)
    
    service = MLAnalyticsService(db)
    success = service.delete_predictive_model(organization_id, model_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Predictive model not found")
    
    return None


@router.post("/models/predictive/{model_id}/train", response_model=ModelTrainingStatus)
async def train_predictive_model(
    model_id: int,
    training_request: ModelTrainingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:update", db)
    
    # TODO: Implement actual model training logic
    # This is a placeholder response
    return ModelTrainingStatus(
        model_id=model_id,
        status="training",
        progress=0.0,
        message="Model training started",
        started_at=datetime.utcnow()
    )


@router.post("/models/predictive/{model_id}/deploy", response_model=PredictiveModelResponse)
async def deploy_predictive_model(
    model_id: int,
    deployment_request: ModelDeploymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deploy a predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:update", db)
    
    service = MLAnalyticsService(db)
    model = service.get_predictive_model(organization_id, model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Predictive model not found")
    
    # Mark model as active (deployed)
    model.is_active = True
    model.deployed_at = datetime.utcnow()
    db.commit()
    db.refresh(model)
    
    return PredictiveModelResponse.from_orm(model)


# ============================================================================
# ANOMALY DETECTION ENDPOINTS
# ============================================================================

@router.post("/anomaly-detection/models", response_model=AnomalyDetectionModelResponse, status_code=201)
async def create_anomaly_detection_model(
    model_data: AnomalyDetectionModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new anomaly detection model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:create", db)
    
    service = MLAnalyticsService(db)
    model = service.create_anomaly_detection_model(
        organization_id=organization_id,
        model_data=model_data,
        created_by_id=current_user.id
    )
    
    return AnomalyDetectionModelResponse.from_orm(model)


@router.get("/anomaly-detection/models", response_model=List[AnomalyDetectionModelResponse])
async def get_anomaly_detection_models(
    anomaly_type: Optional[AnomalyTypeEnum] = Query(None, description="Filter by anomaly type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all anomaly detection models for the organization"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    models = service.get_anomaly_detection_models(
        organization_id=organization_id,
        anomaly_type=anomaly_type,
        is_active=is_active
    )
    
    return [AnomalyDetectionModelResponse.from_orm(model) for model in models]


@router.get("/anomaly-detection/results", response_model=List[AnomalyDetectionResultResponse])
async def get_anomaly_detection_results(
    model_id: Optional[int] = Query(None, description="Filter by model ID"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    severity: Optional[SeverityLevelEnum] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get anomaly detection results"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    results = service.get_anomaly_detection_results(
        organization_id=organization_id,
        model_id=model_id,
        is_resolved=is_resolved,
        severity=severity.value if severity else None,
        limit=limit
    )
    
    return [AnomalyDetectionResultResponse.from_orm(result) for result in results]


@router.post("/anomaly-detection/results/{anomaly_id}/resolve", response_model=AnomalyDetectionResultResponse)
async def resolve_anomaly(
    anomaly_id: int,
    resolution_data: AnomalyResolutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an anomaly"""
    PermissionChecker.require_permission(current_user, "ml_analytics:update", db)
    
    service = MLAnalyticsService(db)
    result = service.resolve_anomaly(
        organization_id=organization_id,
        anomaly_id=anomaly_id,
        resolution_data=resolution_data,
        resolved_by_id=current_user.id
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return AnomalyDetectionResultResponse.from_orm(result)


# ============================================================================
# EXTERNAL DATA SOURCE ENDPOINTS
# ============================================================================

@router.post("/data-sources", response_model=ExternalDataSourceResponse, status_code=201)
async def create_external_data_source(
    source_data: ExternalDataSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new external data source"""
    PermissionChecker.require_permission(current_user, "ml_analytics:create", db)
    
    service = MLAnalyticsService(db)
    source = service.create_external_data_source(
        organization_id=organization_id,
        source_data=source_data,
        created_by_id=current_user.id
    )
    
    return ExternalDataSourceResponse.from_orm(source)


@router.get("/data-sources", response_model=List[ExternalDataSourceResponse])
async def get_external_data_sources(
    source_type: Optional[DataSourceTypeEnum] = Query(None, description="Filter by source type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all external data sources for the organization"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    sources = service.get_external_data_sources(
        organization_id=organization_id,
        source_type=source_type,
        is_active=is_active
    )
    
    return [ExternalDataSourceResponse.from_orm(source) for source in sources]


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@router.post("/predictions", response_model=PredictionResponse)
async def make_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make a prediction using a predictive model"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    result = service.make_prediction(
        organization_id=organization_id,
        prediction_request=prediction_request,
        user_id=current_user.id
    )
    
    return PredictionResponse(**result)


@router.get("/predictions/history", response_model=List[PredictionHistoryResponse])
async def get_prediction_history(
    model_id: Optional[int] = Query(None, description="Filter by model ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction history"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    history = service.get_prediction_history(
        organization_id=organization_id,
        model_id=model_id,
        limit=limit
    )
    
    return [PredictionHistoryResponse.from_orm(record) for record in history]


# ============================================================================
# ADVANCED ANALYTICS ENDPOINTS
# ============================================================================

@router.post("/advanced-analytics", response_model=AdvancedAnalyticsResponse)
async def perform_advanced_analytics(
    analytics_request: AdvancedAnalyticsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform advanced analytics"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAnalyticsService(db)
    result = service.perform_advanced_analytics(
        organization_id=organization_id,
        request=analytics_request
    )
    
    return AdvancedAnalyticsResponse(**result)
