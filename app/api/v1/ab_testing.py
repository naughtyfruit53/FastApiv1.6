# app/api/v1/ab_testing.py

"""
A/B Testing API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.ab_testing_service import ABTestingService
from app.models.ab_testing import ExperimentStatus, VariantType

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class ExperimentCreate(BaseModel):
    """Schema for creating an experiment"""
    experiment_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    traffic_split: Optional[Dict[str, float]] = None


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment"""
    experiment_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    traffic_split: Optional[Dict[str, float]] = None
    status: Optional[ExperimentStatus] = None


class ExperimentResponse(BaseModel):
    """Schema for experiment response"""
    id: int
    organization_id: int
    experiment_name: str
    description: Optional[str]
    status: ExperimentStatus
    traffic_split: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VariantCreate(BaseModel):
    """Schema for creating a variant"""
    variant_name: str = Field(..., min_length=1, max_length=100)
    variant_type: VariantType
    model_id: Optional[int] = None
    model_version: Optional[str] = None
    traffic_percentage: float = Field(50.0, ge=0, le=100)
    variant_config: Optional[Dict[str, Any]] = None


class VariantResponse(BaseModel):
    """Schema for variant response"""
    id: int
    experiment_id: int
    variant_name: str
    variant_type: VariantType
    model_id: Optional[int]
    model_version: Optional[str]
    traffic_percentage: float
    variant_config: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssignmentRequest(BaseModel):
    """Schema for requesting variant assignment"""
    experiment_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    experiment_id: int
    variant: VariantResponse
    assigned: bool


class ResultCreate(BaseModel):
    """Schema for creating a result"""
    experiment_id: int
    variant_id: int
    metric_name: str
    metric_value: float
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    result_metadata: Optional[Dict[str, Any]] = None


class ResultResponse(BaseModel):
    """Schema for result response"""
    id: int
    experiment_id: int
    variant_id: int
    metric_name: str
    metric_value: float
    recorded_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# EXPERIMENT ENDPOINTS
# ============================================================================

@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(
    experiment_data: ExperimentCreate,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new A/B test experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    experiment = await service.create_experiment(
        organization_id=org_id,
        created_by_id=current_user.id,
        experiment_name=experiment_data.experiment_name,
        description=experiment_data.description,
        traffic_split=experiment_data.traffic_split
    )
    
    return ExperimentResponse.model_validate(experiment)


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    status: Optional[ExperimentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("ab_testing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List A/B test experiments"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    experiments = await service.list_experiments(
        organization_id=org_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return [ExperimentResponse.model_validate(exp) for exp in experiments]


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get an experiment by ID"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    experiment = await service.get_experiment(experiment_id, org_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return ExperimentResponse.model_validate(experiment)


@router.patch("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: int,
    experiment_data: ExperimentUpdate,
    auth: tuple = Depends(require_access("ab_testing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Update an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    updates = experiment_data.model_dump(exclude_unset=True)
    experiment = await service.update_experiment(
        experiment_id=experiment_id,
        organization_id=org_id,
        **updates
    )
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return ExperimentResponse.model_validate(experiment)


@router.post("/experiments/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Start an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    try:
        experiment = await service.start_experiment(experiment_id, org_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        return ExperimentResponse.model_validate(experiment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/experiments/{experiment_id}/pause", response_model=ExperimentResponse)
async def pause_experiment(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Pause an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    experiment = await service.pause_experiment(experiment_id, org_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return ExperimentResponse.model_validate(experiment)


@router.post("/experiments/{experiment_id}/complete", response_model=ExperimentResponse)
async def complete_experiment(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Complete an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    experiment = await service.complete_experiment(experiment_id, org_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return ExperimentResponse.model_validate(experiment)


# ============================================================================
# VARIANT ENDPOINTS
# ============================================================================

@router.post("/experiments/{experiment_id}/variants", response_model=VariantResponse)
async def create_variant(
    experiment_id: int,
    variant_data: VariantCreate,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a variant for an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    try:
        variant = await service.create_variant(
            experiment_id=experiment_id,
            organization_id=org_id,
            variant_name=variant_data.variant_name,
            variant_type=variant_data.variant_type,
            model_id=variant_data.model_id,
            model_version=variant_data.model_version,
            traffic_percentage=variant_data.traffic_percentage,
            variant_config=variant_data.variant_config
        )
        
        return VariantResponse.model_validate(variant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/experiments/{experiment_id}/variants", response_model=List[VariantResponse])
async def get_variants(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all variants for an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    variants = await service.get_variants(experiment_id, org_id)
    
    return [VariantResponse.model_validate(v) for v in variants]


# ============================================================================
# ASSIGNMENT ENDPOINTS
# ============================================================================

@router.post("/assign", response_model=AssignmentResponse)
async def assign_variant(
    assignment_data: AssignmentRequest,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Assign a user/session to a variant"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    variant = await service.assign_variant(
        experiment_id=assignment_data.experiment_id,
        organization_id=org_id,
        user_id=assignment_data.user_id or current_user.id,
        session_id=assignment_data.session_id
    )
    
    if not variant:
        raise HTTPException(status_code=404, detail="Experiment not found or not running")
    
    return AssignmentResponse(
        experiment_id=assignment_data.experiment_id,
        variant=VariantResponse.model_validate(variant),
        assigned=True
    )


# ============================================================================
# RESULT ENDPOINTS
# ============================================================================

@router.post("/results", response_model=ResultResponse)
async def record_result(
    result_data: ResultCreate,
    auth: tuple = Depends(require_access("ab_testing", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Record a result for a variant"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    result = await service.record_result(
        experiment_id=result_data.experiment_id,
        variant_id=result_data.variant_id,
        metric_name=result_data.metric_name,
        metric_value=result_data.metric_value,
        user_id=result_data.user_id or current_user.id,
        session_id=result_data.session_id,
        result_metadata=result_data.result_metadata
    )
    
    return ResultResponse.model_validate(result)


@router.get("/experiments/{experiment_id}/results")
async def get_experiment_results(
    experiment_id: int,
    auth: tuple = Depends(require_access("ab_testing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated results for an experiment"""
    current_user, org_id = auth
    service = ABTestingService(db)
    
    results = await service.get_experiment_results(experiment_id, org_id)
    
    if not results:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return results