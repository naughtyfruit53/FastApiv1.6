"""
AI Analytics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import PermissionChecker
from app.models.user_models import User
from app.services.ai_analytics_service import AIAnalyticsService
from app.schemas.ai_analytics import (
    AIModelCreate, AIModelUpdate, AIModelResponse,
    PredictionRequest, PredictionResponse, PredictionFeedback,
    AnomalyDetectionResponse, AnomalyUpdateRequest,
    AIInsightCreate, AIInsightUpdate, AIInsightResponse,
    ModelPerformanceSummary, ModelPerformanceMetricResponse,
    AutomationWorkflowCreate, AutomationWorkflowUpdate, AutomationWorkflowResponse,
    AIAnalyticsDashboard, PredictiveAnalyticsRequest, PredictiveAnalyticsResponse,
    ModelTrainingRequest, ModelDeploymentRequest, ModelTrainingStatus,
    ModelStatusEnum, PredictionTypeEnum, SeverityLevel
)

router = APIRouter()

@router.get("/dashboard", response_model=AIAnalyticsDashboard)
async def get_ai_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI analytics dashboard data"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    dashboard_data = service.get_ai_analytics_dashboard(current_user.organization_id)
    
    return AIAnalyticsDashboard(**dashboard_data)

# ============================================================================
# AI MODEL MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/models", response_model=AIModelResponse)
async def create_ai_model(
    model_data: AIModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI model"""
    PermissionChecker.require_permission(current_user, "ai_analytics:create", db)
    
    service = AIAnalyticsService(db)
    model = service.create_ai_model(
        organization_id=current_user.organization_id,
        model_data=model_data,
        created_by_id=current_user.id
    )
    
    return AIModelResponse.from_orm(model)

@router.get("/models", response_model=List[AIModelResponse])
async def get_ai_models(
    status: Optional[ModelStatusEnum] = Query(None, description="Filter by model status"),
    model_type: Optional[PredictionTypeEnum] = Query(None, description="Filter by model type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI models for the organization"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    models = service.get_ai_models(
        organization_id=current_user.organization_id,
        status=status,
        model_type=model_type
    )
    
    return [AIModelResponse.from_orm(model) for model in models]

@router.get("/models/{model_id}", response_model=AIModelResponse)
async def get_ai_model(
    model_id: int = Path(..., description="AI model ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific AI model"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    model = service.get_ai_model(current_user.organization_id, model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    return AIModelResponse.from_orm(model)

@router.put("/models/{model_id}", response_model=AIModelResponse)
async def update_ai_model(
    model_id: int,
    update_data: AIModelUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an AI model"""
    PermissionChecker.require_permission(current_user, "ai_analytics:update", db)
    
    service = AIAnalyticsService(db)
    model = service.get_ai_model(current_user.organization_id, model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Update model fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(model, field, value)
    
    model.updated_by_id = current_user.id
    db.commit()
    db.refresh(model)
    
    return AIModelResponse.from_orm(model)

@router.post("/models/{model_id}/train")
async def train_ai_model(
    model_id: int,
    training_request: ModelTrainingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train an AI model"""
    PermissionChecker.require_permission(current_user, "ai_analytics:manage", db)
    
    service = AIAnalyticsService(db)
    
    try:
        result = service.train_model(
            organization_id=current_user.organization_id,
            model_id=model_id,
            training_request=training_request
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/models/{model_id}/deploy")
async def deploy_ai_model(
    model_id: int,
    deployment_request: ModelDeploymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deploy an AI model to production"""
    PermissionChecker.require_permission(current_user, "ai_analytics:manage", db)
    
    service = AIAnalyticsService(db)
    
    try:
        result = service.deploy_model(
            organization_id=current_user.organization_id,
            model_id=model_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models/{model_id}/performance", response_model=ModelPerformanceSummary)
async def get_model_performance(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get model performance metrics"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    model = service.get_ai_model(current_user.organization_id, model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Get performance metrics
    from app.models.ai_analytics_models import ModelPerformanceMetric
    metrics = db.query(ModelPerformanceMetric).filter(
        ModelPerformanceMetric.model_id == model_id
    ).order_by(ModelPerformanceMetric.measured_at.desc()).limit(10).all()
    
    # Determine accuracy trend (simplified)
    accuracy_trend = "stable"
    if len(metrics) >= 2:
        recent_accuracy = metrics[0].metric_value if metrics[0].metric_name == "accuracy" else None
        older_accuracy = metrics[-1].metric_value if metrics[-1].metric_name == "accuracy" else None
        if recent_accuracy and older_accuracy:
            if recent_accuracy > older_accuracy * 1.05:
                accuracy_trend = "improving"
            elif recent_accuracy < older_accuracy * 0.95:
                accuracy_trend = "declining"
    
    return ModelPerformanceSummary(
        model_id=model.id,
        model_name=model.model_name,
        current_accuracy=model.accuracy_score,
        accuracy_trend=accuracy_trend,
        predictions_made=model.prediction_count,
        last_prediction_at=model.last_prediction_at,
        performance_metrics=[ModelPerformanceMetricResponse.from_orm(metric) for metric in metrics]
    )

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@router.post("/predict", response_model=PredictionResponse)
async def make_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make a prediction using a deployed AI model"""
    PermissionChecker.require_permission(current_user, "ai_analytics:predict", db)
    
    service = AIAnalyticsService(db)
    
    try:
        prediction_result = service.make_prediction(
            organization_id=current_user.organization_id,
            prediction_request=prediction_request,
            user_id=current_user.id
        )
        return PredictionResponse.from_orm(prediction_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions(
    model_id: Optional[int] = Query(None, description="Filter by model ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction results"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    predictions = service.get_prediction_results(
        organization_id=current_user.organization_id,
        model_id=model_id,
        limit=limit
    )
    
    return [PredictionResponse.from_orm(prediction) for prediction in predictions]

@router.post("/predictions/{prediction_id}/feedback")
async def submit_prediction_feedback(
    prediction_id: str,
    feedback: PredictionFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a prediction"""
    PermissionChecker.require_permission(current_user, "ai_analytics:feedback", db)
    
    from app.models.ai_analytics_models import PredictionResult
    
    prediction = db.query(PredictionResult).filter(
        PredictionResult.prediction_id == prediction_id,
        PredictionResult.organization_id == current_user.organization_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Update prediction with feedback
    prediction.actual_outcome = feedback.actual_outcome
    prediction.feedback_provided = True
    prediction.feedback_score = feedback.feedback_score
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}

# ============================================================================
# ANOMALY DETECTION ENDPOINTS
# ============================================================================

@router.post("/anomalies/detect")
async def detect_anomalies(
    data_source: str = Query(..., description="Data source to analyze (sales, service, customer, all)"),
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect anomalies in business data"""
    PermissionChecker.require_permission(current_user, "ai_analytics:detect", db)
    
    service = AIAnalyticsService(db)
    anomalies = service.detect_anomalies(
        organization_id=current_user.organization_id,
        data_source=data_source,
        time_range_hours=time_range_hours
    )
    
    return [AnomalyDetectionResponse.from_orm(anomaly) for anomaly in anomalies]

@router.get("/anomalies", response_model=List[AnomalyDetectionResponse])
async def get_anomalies(
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active anomalies"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    anomalies = service.get_active_anomalies(
        organization_id=current_user.organization_id,
        severity=severity
    )
    
    return [AnomalyDetectionResponse.from_orm(anomaly) for anomaly in anomalies]

@router.put("/anomalies/{anomaly_id}")
async def update_anomaly(
    anomaly_id: int,
    update_request: AnomalyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an anomaly alert"""
    PermissionChecker.require_permission(current_user, "ai_analytics:manage", db)
    
    from app.models.ai_analytics_models import AnomalyDetection
    
    anomaly = db.query(AnomalyDetection).filter(
        AnomalyDetection.id == anomaly_id,
        AnomalyDetection.organization_id == current_user.organization_id
    ).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    # Update anomaly
    anomaly.alert_status = update_request.alert_status
    if update_request.assigned_to_id:
        anomaly.assigned_to_id = update_request.assigned_to_id
    if update_request.resolution_notes:
        anomaly.resolution_notes = update_request.resolution_notes
    
    if update_request.alert_status == "resolved":
        anomaly.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Anomaly updated successfully"}

# ============================================================================
# AI INSIGHTS ENDPOINTS
# ============================================================================

@router.post("/insights/generate")
async def generate_insights(
    categories: Optional[List[str]] = Query(None, description="Categories to generate insights for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered business insights"""
    PermissionChecker.require_permission(current_user, "ai_analytics:generate", db)
    
    service = AIAnalyticsService(db)
    insights = service.generate_insights(
        organization_id=current_user.organization_id,
        categories=categories
    )
    
    return [AIInsightResponse.from_orm(insight) for insight in insights]

@router.get("/insights", response_model=List[AIInsightResponse])
async def get_insights(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active AI insights"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    service = AIAnalyticsService(db)
    insights = service.get_active_insights(
        organization_id=current_user.organization_id,
        priority=priority,
        category=category
    )
    
    return [AIInsightResponse.from_orm(insight) for insight in insights]

@router.put("/insights/{insight_id}")
async def update_insight(
    insight_id: int,
    update_request: AIInsightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an AI insight"""
    PermissionChecker.require_permission(current_user, "ai_analytics:manage", db)
    
    from app.models.ai_analytics_models import AIInsight
    
    insight = db.query(AIInsight).filter(
        AIInsight.id == insight_id,
        AIInsight.organization_id == current_user.organization_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    # Update insight
    for field, value in update_request.dict(exclude_unset=True).items():
        setattr(insight, field, value)
    
    if update_request.status:
        insight.reviewed_by_id = current_user.id
        insight.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Insight updated successfully"}

# ============================================================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ============================================================================

@router.post("/predictive", response_model=PredictiveAnalyticsResponse)
async def generate_predictive_analytics(
    request: PredictiveAnalyticsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate predictive analytics"""
    PermissionChecker.require_permission(current_user, "ai_analytics:predict", db)
    
    service = AIAnalyticsService(db)
    
    try:
        result = service.generate_predictive_analytics(
            organization_id=current_user.organization_id,
            request=request
        )
        return PredictiveAnalyticsResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# AUTOMATION WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/workflows", response_model=AutomationWorkflowResponse)
async def create_automation_workflow(
    workflow_data: AutomationWorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an automation workflow"""
    PermissionChecker.require_permission(current_user, "ai_analytics:automation", db)
    
    from app.models.ai_analytics_models import AutomationWorkflow
    
    workflow = AutomationWorkflow(
        organization_id=current_user.organization_id,
        workflow_name=workflow_data.workflow_name,
        description=workflow_data.description,
        workflow_type=workflow_data.workflow_type,
        category=workflow_data.category,
        trigger_conditions=workflow_data.trigger_conditions,
        trigger_schedule=workflow_data.trigger_schedule,
        workflow_steps=workflow_data.workflow_steps,
        ai_models_used=workflow_data.ai_models_used,
        auto_approve=workflow_data.auto_approve,
        requires_human_approval=workflow_data.requires_human_approval,
        created_by_id=current_user.id
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return AutomationWorkflowResponse.from_orm(workflow)

@router.get("/workflows", response_model=List[AutomationWorkflowResponse])
async def get_automation_workflows(
    workflow_type: Optional[str] = Query(None, description="Filter by workflow type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get automation workflows"""
    PermissionChecker.require_permission(current_user, "ai_analytics:read", db)
    
    from app.models.ai_analytics_models import AutomationWorkflow
    
    query = db.query(AutomationWorkflow).filter(
        AutomationWorkflow.organization_id == current_user.organization_id
    )
    
    if workflow_type:
        query = query.filter(AutomationWorkflow.workflow_type == workflow_type)
    if is_active is not None:
        query = query.filter(AutomationWorkflow.is_active == is_active)
    
    workflows = query.order_by(AutomationWorkflow.created_at.desc()).all()
    
    return [AutomationWorkflowResponse.from_orm(workflow) for workflow in workflows]