"""
AutoML API endpoints for automatic model selection and hyperparameter tuning
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import PermissionChecker
from app.models.user_models import User
from app.services.automl_service import AutoMLService
from app.models.automl import AutoMLTaskType, AutoMLStatus, AutoMLFramework
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class AutoMLRunCreate(BaseModel):
    """Schema for creating AutoML run"""
    run_name: str = Field(..., description="Name of the AutoML run")
    task_type: str = Field(..., description="Type of ML task: classification, regression, time_series, clustering")
    target_column: str = Field(..., description="Target column name")
    feature_columns: List[str] = Field(..., description="List of feature column names")
    metric: str = Field(..., description="Optimization metric (accuracy, f1, rmse, etc.)")
    framework: str = Field(default="optuna", description="AutoML framework to use")
    time_budget: int = Field(default=3600, description="Time budget in seconds")
    max_trials: int = Field(default=100, description="Maximum number of trials")
    dataset_config: Optional[Dict[str, Any]] = Field(None, description="Dataset configuration")
    description: Optional[str] = Field(None, description="Run description")


class AutoMLRunResponse(BaseModel):
    """Schema for AutoML run response"""
    id: int
    organization_id: int
    run_name: str
    task_type: str
    framework: str
    status: str
    progress: float
    current_trial: int
    best_model_name: Optional[str] = None
    best_score: Optional[float] = None
    target_column: str
    feature_columns: List[str]
    metric: str
    time_budget: int
    max_trials: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AutoMLDashboardResponse(BaseModel):
    """Schema for AutoML dashboard"""
    total_runs: int
    completed_runs: int
    running_runs: int
    recent_runs: List[Dict[str, Any]]


class AutoMLModelCandidateResponse(BaseModel):
    """Schema for AutoML model candidate"""
    id: int
    trial_number: int
    model_name: str
    algorithm: str
    score: float
    training_time: float
    evaluation_metrics: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=AutoMLDashboardResponse)
async def get_automl_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AutoML dashboard data"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = AutoMLService(db)
    dashboard_data = service.get_automl_dashboard(current_user.organization_id)
    
    return AutoMLDashboardResponse(**dashboard_data)


@router.post("/runs", response_model=AutoMLRunResponse, status_code=201)
async def create_automl_run(
    run_data: AutoMLRunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AutoML run"""
    PermissionChecker.require_permission(current_user, "ml_analytics:create", db)
    
    try:
        task_type = AutoMLTaskType(run_data.task_type)
        framework = AutoMLFramework(run_data.framework)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    
    service = AutoMLService(db)
    run = service.create_automl_run(
        organization_id=current_user.organization_id,
        run_name=run_data.run_name,
        task_type=task_type,
        target_column=run_data.target_column,
        feature_columns=run_data.feature_columns,
        metric=run_data.metric,
        framework=framework,
        time_budget=run_data.time_budget,
        max_trials=run_data.max_trials,
        dataset_config=run_data.dataset_config,
        description=run_data.description,
        created_by_id=current_user.id
    )
    
    return AutoMLRunResponse(
        id=run.id,
        organization_id=run.organization_id,
        run_name=run.run_name,
        task_type=run.task_type.value,
        framework=run.framework.value,
        status=run.status.value,
        progress=run.progress,
        current_trial=run.current_trial,
        best_model_name=run.best_model_name,
        best_score=run.best_score,
        target_column=run.target_column,
        feature_columns=run.feature_columns,
        metric=run.metric,
        time_budget=run.time_budget,
        max_trials=run.max_trials,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_message=run.error_message,
        created_at=run.created_at
    )


@router.get("/runs", response_model=List[AutoMLRunResponse])
async def get_automl_runs(
    status: Optional[str] = Query(None, description="Filter by status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all AutoML runs for the organization"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    status_enum = AutoMLStatus(status) if status else None
    task_type_enum = AutoMLTaskType(task_type) if task_type else None
    
    service = AutoMLService(db)
    runs = service.get_automl_runs(
        organization_id=current_user.organization_id,
        status=status_enum,
        task_type=task_type_enum
    )
    
    return [
        AutoMLRunResponse(
            id=run.id,
            organization_id=run.organization_id,
            run_name=run.run_name,
            task_type=run.task_type.value,
            framework=run.framework.value,
            status=run.status.value,
            progress=run.progress,
            current_trial=run.current_trial,
            best_model_name=run.best_model_name,
            best_score=run.best_score,
            target_column=run.target_column,
            feature_columns=run.feature_columns,
            metric=run.metric,
            time_budget=run.time_budget,
            max_trials=run.max_trials,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
            created_at=run.created_at
        )
        for run in runs
    ]


@router.get("/runs/{run_id}", response_model=AutoMLRunResponse)
async def get_automl_run(
    run_id: int = Path(..., description="AutoML run ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific AutoML run"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = AutoMLService(db)
    run = service.get_automl_run(current_user.organization_id, run_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="AutoML run not found")
    
    return AutoMLRunResponse(
        id=run.id,
        organization_id=run.organization_id,
        run_name=run.run_name,
        task_type=run.task_type.value,
        framework=run.framework.value,
        status=run.status.value,
        progress=run.progress,
        current_trial=run.current_trial,
        best_model_name=run.best_model_name,
        best_score=run.best_score,
        target_column=run.target_column,
        feature_columns=run.feature_columns,
        metric=run.metric,
        time_budget=run.time_budget,
        max_trials=run.max_trials,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_message=run.error_message,
        created_at=run.created_at
    )


@router.get("/runs/{run_id}/leaderboard", response_model=List[AutoMLModelCandidateResponse])
async def get_automl_leaderboard(
    run_id: int = Path(..., description="AutoML run ID"),
    top_n: int = Query(10, description="Number of top models to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard for AutoML run"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = AutoMLService(db)
    candidates = service.get_leaderboard(run_id, top_n)
    
    return [AutoMLModelCandidateResponse.from_orm(candidate) for candidate in candidates]


@router.post("/runs/{run_id}/cancel")
async def cancel_automl_run(
    run_id: int = Path(..., description="AutoML run ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a running AutoML run"""
    PermissionChecker.require_permission(current_user, "ml_analytics:update", db)
    
    service = AutoMLService(db)
    run = service.cancel_automl_run(run_id)
    
    return {
        "message": "AutoML run cancelled successfully",
        "run_id": run.id,
        "status": run.status.value
    }
