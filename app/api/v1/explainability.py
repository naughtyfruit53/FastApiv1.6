"""
Explainability API endpoints for SHAP and LIME model interpretability
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.services.explainability_service import ExplainabilityService
from app.models.explainability import ExplainabilityMethod, ExplainabilityScope
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ModelExplainabilityCreate(BaseModel):
    """Schema for creating model explainability"""
    model_id: int = Field(..., description="Model ID")
    model_type: str = Field(..., description="Model type (predictive_model, automl_run, etc.)")
    model_name: str = Field(..., description="Model name")
    method: str = Field(..., description="Explainability method (shap, lime, feature_importance)")
    scope: str = Field(..., description="Scope (global, local, cohort)")
    config: Dict[str, Any] = Field(..., description="Explainability configuration")
    description: Optional[str] = Field(None, description="Description")


class ModelExplainabilityResponse(BaseModel):
    """Schema for model explainability response"""
    id: int
    organization_id: int
    model_id: int
    model_type: str
    model_name: str
    method: str
    scope: str
    config: Dict[str, Any]
    feature_importance: Optional[Dict[str, Any]] = None
    shap_values: Optional[Dict[str, Any]] = None
    lime_explanation: Optional[Dict[str, Any]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    top_features: Optional[List[Dict[str, Any]]] = None
    computation_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionExplanationCreate(BaseModel):
    """Schema for creating prediction explanation"""
    model_explainability_id: int = Field(..., description="Model explainability ID")
    input_features: Dict[str, Any] = Field(..., description="Input features")
    predicted_value: float = Field(..., description="Predicted value")
    method: str = Field(..., description="Explainability method")
    shap_values: Optional[Dict[str, Any]] = Field(None, description="SHAP values")
    lime_explanation: Optional[Dict[str, Any]] = Field(None, description="LIME explanation")
    feature_contributions: Optional[Dict[str, Any]] = Field(None, description="Feature contributions")
    prediction_id: Optional[str] = Field(None, description="Prediction ID")
    confidence_score: Optional[float] = Field(None, description="Confidence score")


class PredictionExplanationResponse(BaseModel):
    """Schema for prediction explanation response"""
    id: int
    organization_id: int
    model_explainability_id: int
    prediction_id: Optional[str] = None
    input_features: Dict[str, Any]
    predicted_value: float
    confidence_score: Optional[float] = None
    method: str
    shap_values: Optional[Dict[str, Any]] = None
    lime_explanation: Optional[Dict[str, Any]] = None
    feature_contributions: Optional[Dict[str, Any]] = None
    top_positive_features: Optional[List[Dict[str, Any]]] = None
    top_negative_features: Optional[List[Dict[str, Any]]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExplainabilityReportCreate(BaseModel):
    """Schema for creating explainability report"""
    report_name: str = Field(..., description="Report name")
    report_type: str = Field(..., description="Report type")
    model_ids: List[int] = Field(..., description="List of model IDs")
    summary: Dict[str, Any] = Field(..., description="Report summary")
    feature_analysis: Optional[Dict[str, Any]] = Field(None, description="Feature analysis")
    model_comparisons: Optional[Dict[str, Any]] = Field(None, description="Model comparisons")
    visualizations: Optional[List[Dict[str, Any]]] = Field(None, description="Visualizations")
    key_insights: Optional[List[str]] = Field(None, description="Key insights")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")
    description: Optional[str] = Field(None, description="Description")


class ExplainabilityReportResponse(BaseModel):
    """Schema for explainability report response"""
    id: int
    organization_id: int
    report_name: str
    report_type: str
    model_ids: List[int]
    summary: Dict[str, Any]
    feature_analysis: Optional[Dict[str, Any]] = None
    model_comparisons: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    key_insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    generated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ExplainabilityDashboardResponse(BaseModel):
    """Schema for explainability dashboard"""
    total_models_with_explainability: int
    total_prediction_explanations: int
    total_reports: int
    recent_reports: List[Dict[str, Any]]


# ============================================================================
# API ENDPOINTS - MODEL EXPLAINABILITY
# ============================================================================

@router.get("/dashboard", response_model=ExplainabilityDashboardResponse)
async def get_explainability_dashboard(
    auth: tuple = Depends(require_access("explainability", "read")),
    db: Session = Depends(get_db)
):
    """Get explainability dashboard data"""
    current_user, org_id = auth
    
    service = ExplainabilityService(db)
    dashboard_data = service.get_explainability_dashboard(org_id)
    
    return ExplainabilityDashboardResponse(**dashboard_data)


@router.post("/models", response_model=ModelExplainabilityResponse, status_code=201)
async def create_model_explainability(
    explainability_data: ModelExplainabilityCreate,
    auth: tuple = Depends(require_access("explainability", "create")),
    db: Session = Depends(get_db)
):
    """Create model explainability configuration"""
    current_user, org_id = auth

    
    try:
        method = ExplainabilityMethod(explainability_data.method)
        scope = ExplainabilityScope(explainability_data.scope)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
    
    service = ExplainabilityService(db)
    explainability = service.create_model_explainability(
        organization_id=current_user.organization_id,
        model_id=explainability_data.model_id,
        model_type=explainability_data.model_type,
        model_name=explainability_data.model_name,
        method=method,
        scope=scope,
        config=explainability_data.config,
        description=explainability_data.description,
        created_by_id=current_user.id
    )
    
    return ModelExplainabilityResponse(
        id=explainability.id,
        organization_id=explainability.organization_id,
        model_id=explainability.model_id,
        model_type=explainability.model_type,
        model_name=explainability.model_name,
        method=explainability.method.value,
        scope=explainability.scope.value,
        config=explainability.config,
        feature_importance=explainability.feature_importance,
        shap_values=explainability.shap_values,
        lime_explanation=explainability.lime_explanation,
        visualization_data=explainability.visualization_data,
        top_features=explainability.top_features,
        computation_time=explainability.computation_time,
        created_at=explainability.created_at
    )


@router.get("/models/{model_id}/{model_type}", response_model=ModelExplainabilityResponse)
async def get_model_explainability(
    model_id: int = Path(..., description="Model ID"),
    model_type: str = Path(..., description="Model type"),
    method: Optional[str] = Query(None, description="Filter by method"),
    auth: tuple = Depends(require_access("explainability", "read")),
    db: Session = Depends(get_db)
):
    """Get model explainability configuration"""
    current_user, org_id = auth

    
    method_enum = ExplainabilityMethod(method) if method else None
    
    service = ExplainabilityService(db)
    explainability = service.get_model_explainability(
        organization_id=current_user.organization_id,
        model_id=model_id,
        model_type=model_type,
        method=method_enum
    )
    
    if not explainability:
        raise HTTPException(status_code=404, detail="Model explainability not found")
    
    return ModelExplainabilityResponse(
        id=explainability.id,
        organization_id=explainability.organization_id,
        model_id=explainability.model_id,
        model_type=explainability.model_type,
        model_name=explainability.model_name,
        method=explainability.method.value,
        scope=explainability.scope.value,
        config=explainability.config,
        feature_importance=explainability.feature_importance,
        shap_values=explainability.shap_values,
        lime_explanation=explainability.lime_explanation,
        visualization_data=explainability.visualization_data,
        top_features=explainability.top_features,
        computation_time=explainability.computation_time,
        created_at=explainability.created_at
    )


# ============================================================================
# API ENDPOINTS - PREDICTION EXPLANATIONS
# ============================================================================

@router.post("/predictions", response_model=PredictionExplanationResponse, status_code=201)
async def create_prediction_explanation(
    explanation_data: PredictionExplanationCreate,
    auth: tuple = Depends(require_access("explainability", "create")),
    db: Session = Depends(get_db)
):
    """Create a prediction explanation"""
    current_user, org_id = auth

    
    try:
        method = ExplainabilityMethod(explanation_data.method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid method: {str(e)}")
    
    service = ExplainabilityService(db)
    explanation = service.create_prediction_explanation(
        organization_id=current_user.organization_id,
        model_explainability_id=explanation_data.model_explainability_id,
        input_features=explanation_data.input_features,
        predicted_value=explanation_data.predicted_value,
        method=method,
        shap_values=explanation_data.shap_values,
        lime_explanation=explanation_data.lime_explanation,
        feature_contributions=explanation_data.feature_contributions,
        prediction_id=explanation_data.prediction_id,
        confidence_score=explanation_data.confidence_score
    )
    
    return PredictionExplanationResponse(
        id=explanation.id,
        organization_id=explanation.organization_id,
        model_explainability_id=explanation.model_explainability_id,
        prediction_id=explanation.prediction_id,
        input_features=explanation.input_features,
        predicted_value=explanation.predicted_value,
        confidence_score=explanation.confidence_score,
        method=explanation.method.value,
        shap_values=explanation.shap_values,
        lime_explanation=explanation.lime_explanation,
        feature_contributions=explanation.feature_contributions,
        top_positive_features=explanation.top_positive_features,
        top_negative_features=explanation.top_negative_features,
        visualization_data=explanation.visualization_data,
        created_at=explanation.created_at
    )


@router.get("/predictions/{explainability_id}", response_model=List[PredictionExplanationResponse])
async def get_prediction_explanations(
    explainability_id: int = Path(..., description="Model explainability ID"),
    limit: int = Query(100, description="Maximum number of results"),
    auth: tuple = Depends(require_access("explainability", "read")),
    db: Session = Depends(get_db)
):
    """Get prediction explanations for a model"""
    current_user, org_id = auth

    
    service = ExplainabilityService(db)
    explanations = service.get_prediction_explanations(
        organization_id=current_user.organization_id,
        model_explainability_id=explainability_id,
        limit=limit
    )
    
    return [
        PredictionExplanationResponse(
            id=exp.id,
            organization_id=exp.organization_id,
            model_explainability_id=exp.model_explainability_id,
            prediction_id=exp.prediction_id,
            input_features=exp.input_features,
            predicted_value=exp.predicted_value,
            confidence_score=exp.confidence_score,
            method=exp.method.value,
            shap_values=exp.shap_values,
            lime_explanation=exp.lime_explanation,
            feature_contributions=exp.feature_contributions,
            top_positive_features=exp.top_positive_features,
            top_negative_features=exp.top_negative_features,
            visualization_data=exp.visualization_data,
            created_at=exp.created_at
        )
        for exp in explanations
    ]


# ============================================================================
# API ENDPOINTS - EXPLAINABILITY REPORTS
# ============================================================================

@router.post("/reports", response_model=ExplainabilityReportResponse, status_code=201)
async def create_explainability_report(
    report_data: ExplainabilityReportCreate,
    auth: tuple = Depends(require_access("explainability", "create")),
    db: Session = Depends(get_db)
):
    """Create an explainability report"""
    current_user, org_id = auth

    
    service = ExplainabilityService(db)
    report = service.create_explainability_report(
        organization_id=current_user.organization_id,
        report_name=report_data.report_name,
        report_type=report_data.report_type,
        model_ids=report_data.model_ids,
        summary=report_data.summary,
        feature_analysis=report_data.feature_analysis,
        model_comparisons=report_data.model_comparisons,
        visualizations=report_data.visualizations,
        key_insights=report_data.key_insights,
        recommendations=report_data.recommendations,
        description=report_data.description,
        created_by_id=current_user.id
    )
    
    return ExplainabilityReportResponse(
        id=report.id,
        organization_id=report.organization_id,
        report_name=report.report_name,
        report_type=report.report_type,
        model_ids=report.model_ids,
        summary=report.summary,
        feature_analysis=report.feature_analysis,
        model_comparisons=report.model_comparisons,
        visualizations=report.visualizations,
        key_insights=report.key_insights,
        recommendations=report.recommendations,
        generated_at=report.generated_at,
        created_at=report.created_at
    )


@router.get("/reports", response_model=List[ExplainabilityReportResponse])
async def get_explainability_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    auth: tuple = Depends(require_access("explainability", "read")),
    db: Session = Depends(get_db)
):
    """Get explainability reports"""
    current_user, org_id = auth

    
    service = ExplainabilityService(db)
    reports = service.get_explainability_reports(
        organization_id=current_user.organization_id,
        report_type=report_type
    )
    
    return [
        ExplainabilityReportResponse(
            id=report.id,
            organization_id=report.organization_id,
            report_name=report.report_name,
            report_type=report.report_type,
            model_ids=report.model_ids,
            summary=report.summary,
            feature_analysis=report.feature_analysis,
            model_comparisons=report.model_comparisons,
            visualizations=report.visualizations,
            key_insights=report.key_insights,
            recommendations=report.recommendations,
            generated_at=report.generated_at,
            created_at=report.created_at
        )
        for report in reports
    ]


@router.get("/reports/{report_id}", response_model=ExplainabilityReportResponse)
async def get_explainability_report(
    report_id: int = Path(..., description="Report ID"),
    auth: tuple = Depends(require_access("explainability", "read")),
    db: Session = Depends(get_db)
):
    """Get a specific explainability report"""
    current_user, org_id = auth

    
    service = ExplainabilityService(db)
    report = service.get_explainability_report(
        organization_id=current_user.organization_id,
        report_id=report_id
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Explainability report not found")
    
    return ExplainabilityReportResponse(
        id=report.id,
        organization_id=report.organization_id,
        report_name=report.report_name,
        report_type=report.report_type,
        model_ids=report.model_ids,
        summary=report.summary,
        feature_analysis=report.feature_analysis,
        model_comparisons=report.model_comparisons,
        visualizations=report.visualizations,
        key_insights=report.key_insights,
        recommendations=report.recommendations,
        generated_at=report.generated_at,
        created_at=report.created_at
    )
