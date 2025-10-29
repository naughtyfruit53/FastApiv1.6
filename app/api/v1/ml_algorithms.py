"""
ML Algorithms API endpoints for extended ML framework support
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db

from app.models.user_models import User
from app.services.ml_algorithms_service import MLAlgorithmsService
from app.models.ml_algorithms import MLFramework, AlgorithmCategory, TrainingStatus
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class AlgorithmConfigCreate(BaseModel):
    """Schema for creating algorithm configuration"""
    config_name: str = Field(..., description="Configuration name")
    framework: str = Field(..., description="ML framework (scikit_learn, catboost, lightgbm, tensorflow, pytorch)")
    algorithm_name: str = Field(..., description="Algorithm name")
    category: str = Field(..., description="Algorithm category (classification, regression, etc.)")
    hyperparameters: Dict[str, Any] = Field(..., description="Hyperparameters")
    preprocessing_config: Optional[Dict[str, Any]] = Field(None, description="Preprocessing configuration")
    description: Optional[str] = Field(None, description="Description")
    gpu_enabled: bool = Field(default=False, description="Enable GPU acceleration")


class AlgorithmConfigResponse(BaseModel):
    """Schema for algorithm configuration response"""
    id: int
    organization_id: int
    config_name: str
    framework: str
    algorithm_name: str
    category: str
    hyperparameters: Dict[str, Any]
    preprocessing_config: Optional[Dict[str, Any]] = None
    gpu_enabled: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ModelTrainingCreate(BaseModel):
    """Schema for creating model training"""
    training_name: str = Field(..., description="Training name")
    framework: str = Field(..., description="ML framework")
    algorithm_name: str = Field(..., description="Algorithm name")
    dataset_config: Dict[str, Any] = Field(..., description="Dataset configuration")
    training_params: Dict[str, Any] = Field(..., description="Training parameters")
    hyperparameters: Dict[str, Any] = Field(..., description="Hyperparameters")
    total_epochs: int = Field(..., description="Total epochs")
    algorithm_config_id: Optional[int] = Field(None, description="Reference to algorithm config")
    description: Optional[str] = Field(None, description="Description")
    gpu_used: bool = Field(default=False, description="Use GPU")


class ModelTrainingResponse(BaseModel):
    """Schema for model training response"""
    id: int
    organization_id: int
    training_name: str
    framework: str
    algorithm_name: str
    status: str
    progress: float
    current_epoch: int
    total_epochs: int
    best_score: Optional[float] = None
    training_metrics: Optional[Dict[str, Any]] = None
    validation_metrics: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    training_duration: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingDashboardResponse(BaseModel):
    """Schema for training dashboard"""
    total_trainings: int
    completed_trainings: int
    running_trainings: int
    recent_trainings: List[Dict[str, Any]]


class FrameworkAlgorithmsResponse(BaseModel):
    """Schema for framework algorithms"""
    framework: str
    algorithms: List[str]


# ============================================================================
# API ENDPOINTS - ALGORITHM CONFIGURATIONS
# ============================================================================

@router.post("/configs", response_model=AlgorithmConfigResponse, status_code=201)
async def create_algorithm_config(
    config_data: AlgorithmConfigCreate,
    auth: tuple = Depends(require_access("ml_algorithms", "create")),
    db: Session = Depends(get_db)
):
    """Create a new algorithm configuration"""
    PermissionChecker.require_permission(current_user, "ml_analytics:create", db)
    
    try:
        framework = MLFramework(config_data.framework)
        category = AlgorithmCategory(config_data.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    
    service = MLAlgorithmsService(db)
    config = service.create_algorithm_config(
        organization_id=org_id,
        config_name=config_data.config_name,
        framework=framework,
        algorithm_name=config_data.algorithm_name,
        category=category,
        hyperparameters=config_data.hyperparameters,
        preprocessing_config=config_data.preprocessing_config,
        description=config_data.description,
        gpu_enabled=config_data.gpu_enabled,
        created_by_id=current_user.id
    )
    
    return AlgorithmConfigResponse(
        id=config.id,
        organization_id=config.organization_id,
        config_name=config.config_name,
        framework=config.framework.value,
        algorithm_name=config.algorithm_name,
        category=config.category.value,
        hyperparameters=config.hyperparameters,
        preprocessing_config=config.preprocessing_config,
        gpu_enabled=config.gpu_enabled,
        is_active=config.is_active,
        created_at=config.created_at
    )


@router.get("/configs", response_model=List[AlgorithmConfigResponse])
async def get_algorithm_configs(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    category: Optional[str] = Query(None, description="Filter by category"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get all algorithm configurations"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    framework_enum = MLFramework(framework) if framework else None
    category_enum = AlgorithmCategory(category) if category else None
    
    service = MLAlgorithmsService(db)
    configs = service.get_algorithm_configs(
        organization_id=org_id,
        framework=framework_enum,
        category=category_enum
    )
    
    return [
        AlgorithmConfigResponse(
            id=config.id,
            organization_id=config.organization_id,
            config_name=config.config_name,
            framework=config.framework.value,
            algorithm_name=config.algorithm_name,
            category=config.category.value,
            hyperparameters=config.hyperparameters,
            preprocessing_config=config.preprocessing_config,
            gpu_enabled=config.gpu_enabled,
            is_active=config.is_active,
            created_at=config.created_at
        )
        for config in configs
    ]


@router.get("/configs/{config_id}", response_model=AlgorithmConfigResponse)
async def get_algorithm_config(
    config_id: int = Path(..., description="Configuration ID"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get a specific algorithm configuration"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAlgorithmsService(db)
    config = service.get_algorithm_config(org_id, config_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Algorithm configuration not found")
    
    return AlgorithmConfigResponse(
        id=config.id,
        organization_id=config.organization_id,
        config_name=config.config_name,
        framework=config.framework.value,
        algorithm_name=config.algorithm_name,
        category=config.category.value,
        hyperparameters=config.hyperparameters,
        preprocessing_config=config.preprocessing_config,
        gpu_enabled=config.gpu_enabled,
        is_active=config.is_active,
        created_at=config.created_at
    )


@router.delete("/configs/{config_id}")
async def delete_algorithm_config(
    config_id: int = Path(..., description="Configuration ID"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Delete an algorithm configuration"""
    PermissionChecker.require_permission(current_user, "ml_analytics:delete", db)
    
    service = MLAlgorithmsService(db)
    deleted = service.delete_algorithm_config(config_id, org_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Algorithm configuration not found")
    
    return {"message": "Algorithm configuration deleted successfully"}


# ============================================================================
# API ENDPOINTS - MODEL TRAINING
# ============================================================================

@router.get("/training/dashboard", response_model=TrainingDashboardResponse)
async def get_training_dashboard(
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get training dashboard data"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAlgorithmsService(db)
    dashboard_data = service.get_training_dashboard(org_id)
    
    return TrainingDashboardResponse(**dashboard_data)


@router.post("/training", response_model=ModelTrainingResponse, status_code=201)
async def create_model_training(
    training_data: ModelTrainingCreate,
    auth: tuple = Depends(require_access("ml_algorithms", "create")),
    db: Session = Depends(get_db)
):
    """Create a new model training session"""
    PermissionChecker.require_permission(current_user, "ml_analytics:create", db)
    
    try:
        framework = MLFramework(training_data.framework)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid framework: {str(e)}")
    
    service = MLAlgorithmsService(db)
    training = service.create_model_training(
        organization_id=org_id,
        training_name=training_data.training_name,
        framework=framework,
        algorithm_name=training_data.algorithm_name,
        dataset_config=training_data.dataset_config,
        training_params=training_data.training_params,
        hyperparameters=training_data.hyperparameters,
        total_epochs=training_data.total_epochs,
        algorithm_config_id=training_data.algorithm_config_id,
        description=training_data.description,
        gpu_used=training_data.gpu_used,
        created_by_id=current_user.id
    )
    
    return ModelTrainingResponse(
        id=training.id,
        organization_id=training.organization_id,
        training_name=training.training_name,
        framework=training.framework.value,
        algorithm_name=training.algorithm_name,
        status=training.status.value,
        progress=training.progress,
        current_epoch=training.current_epoch,
        total_epochs=training.total_epochs,
        best_score=training.best_score,
        training_metrics=training.training_metrics,
        validation_metrics=training.validation_metrics,
        started_at=training.started_at,
        completed_at=training.completed_at,
        training_duration=training.training_duration,
        error_message=training.error_message,
        created_at=training.created_at
    )


@router.get("/training", response_model=List[ModelTrainingResponse])
async def get_model_trainings(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    status: Optional[str] = Query(None, description="Filter by status"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get all model training sessions"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    framework_enum = MLFramework(framework) if framework else None
    status_enum = TrainingStatus(status) if status else None
    
    service = MLAlgorithmsService(db)
    trainings = service.get_model_trainings(
        organization_id=org_id,
        framework=framework_enum,
        status=status_enum
    )
    
    return [
        ModelTrainingResponse(
            id=training.id,
            organization_id=training.organization_id,
            training_name=training.training_name,
            framework=training.framework.value,
            algorithm_name=training.algorithm_name,
            status=training.status.value,
            progress=training.progress,
            current_epoch=training.current_epoch,
            total_epochs=training.total_epochs,
            best_score=training.best_score,
            training_metrics=training.training_metrics,
            validation_metrics=training.validation_metrics,
            started_at=training.started_at,
            completed_at=training.completed_at,
            training_duration=training.training_duration,
            error_message=training.error_message,
            created_at=training.created_at
        )
        for training in trainings
    ]


@router.get("/training/{training_id}", response_model=ModelTrainingResponse)
async def get_model_training(
    training_id: int = Path(..., description="Training ID"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get a specific model training session"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    service = MLAlgorithmsService(db)
    training = service.get_model_training(org_id, training_id)
    
    if not training:
        raise HTTPException(status_code=404, detail="Model training not found")
    
    return ModelTrainingResponse(
        id=training.id,
        organization_id=training.organization_id,
        training_name=training.training_name,
        framework=training.framework.value,
        algorithm_name=training.algorithm_name,
        status=training.status.value,
        progress=training.progress,
        current_epoch=training.current_epoch,
        total_epochs=training.total_epochs,
        best_score=training.best_score,
        training_metrics=training.training_metrics,
        validation_metrics=training.validation_metrics,
        started_at=training.started_at,
        completed_at=training.completed_at,
        training_duration=training.training_duration,
        error_message=training.error_message,
        created_at=training.created_at
    )


# ============================================================================
# API ENDPOINTS - FRAMEWORK UTILITIES
# ============================================================================

@router.get("/frameworks/{framework}/algorithms", response_model=FrameworkAlgorithmsResponse)
async def get_framework_algorithms(
    framework: str = Path(..., description="Framework name"),
    auth: tuple = Depends(require_access("ml_algorithms", "read")),
    db: Session = Depends(get_db)
):
    """Get available algorithms for a framework"""
    PermissionChecker.require_permission(current_user, "ml_analytics:read", db)
    
    try:
        framework_enum = MLFramework(framework)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid framework: {framework}")
    
    service = MLAlgorithmsService(db)
    algorithms = service.get_framework_algorithms(framework_enum)
    
    return FrameworkAlgorithmsResponse(
        framework=framework,
        algorithms=algorithms
    )
