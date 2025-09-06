"""
Pydantic schemas for AI Analytics API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from app.models.ai_analytics_models import ModelStatus, PredictionType


class ModelStatusEnum(str, Enum):
    """Model status enumeration for API"""
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class PredictionTypeEnum(str, Enum):
    """Prediction type enumeration for API"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    FORECASTING = "forecasting"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"


class SeverityLevel(str, Enum):
    """Severity level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightType(str, Enum):
    """Insight type enumeration"""
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    OPTIMIZATION = "optimization"
    TREND = "trend"
    RECOMMENDATION = "recommendation"


class Priority(str, Enum):
    """Priority level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# AI Model Schemas

class AIModelBase(BaseModel):
    """Base schema for AI models"""
    model_name: str = Field(..., description="Name of the AI model")
    model_type: PredictionTypeEnum = Field(..., description="Type of prediction model")
    description: Optional[str] = Field(None, description="Model description")
    algorithm: str = Field(..., description="Algorithm used (e.g., random_forest, linear_regression)")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    feature_columns: List[str] = Field(..., description="List of feature column names")
    target_column: Optional[str] = Field(None, description="Target column name for supervised learning")
    training_data_source: Optional[str] = Field(None, description="Source table/view for training data")
    training_data_filters: Optional[Dict[str, Any]] = Field(None, description="Filters applied to training data")
    retraining_frequency_days: Optional[int] = Field(None, ge=1, description="Days between retraining cycles")


class AIModelCreate(AIModelBase):
    """Schema for creating AI models"""
    pass


class AIModelUpdate(BaseModel):
    """Schema for updating AI models"""
    model_name: Optional[str] = None
    description: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    retraining_frequency_days: Optional[int] = None
    status: Optional[ModelStatusEnum] = None


class AIModelResponse(AIModelBase):
    """Schema for AI model responses"""
    id: int
    organization_id: int
    version: str
    status: ModelStatusEnum
    accuracy_score: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    training_started_at: Optional[datetime] = None
    training_completed_at: Optional[datetime] = None
    training_duration_seconds: Optional[float] = None
    deployed_at: Optional[datetime] = None
    prediction_count: int
    last_prediction_at: Optional[datetime] = None
    next_retraining_at: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Prediction Schemas

class PredictionRequest(BaseModel):
    """Schema for prediction requests"""
    model_id: int = Field(..., description="ID of the AI model to use")
    input_data: Dict[str, Any] = Field(..., description="Input features for prediction")
    prediction_context: Optional[str] = Field(None, description="Context of the prediction")
    business_entity_type: Optional[str] = Field(None, description="Type of business entity")
    business_entity_id: Optional[int] = Field(None, description="ID of the business entity")


class PredictionResponse(BaseModel):
    """Schema for prediction responses"""
    id: int
    prediction_id: str
    model_id: int
    prediction_output: Dict[str, Any]
    confidence_score: Optional[float] = None
    prediction_context: Optional[str] = None
    business_entity_type: Optional[str] = None
    business_entity_id: Optional[int] = None
    processing_time_ms: Optional[float] = None
    prediction_timestamp: datetime

    class Config:
        from_attributes = True


class PredictionFeedback(BaseModel):
    """Schema for prediction feedback"""
    prediction_id: str = Field(..., description="ID of the prediction")
    actual_outcome: Optional[Dict[str, Any]] = Field(None, description="Actual outcome observed")
    feedback_score: float = Field(..., ge=1.0, le=5.0, description="Feedback score (1-5)")
    feedback_comments: Optional[str] = Field(None, description="Additional feedback comments")


# Anomaly Detection Schemas

class AnomalyDetectionResponse(BaseModel):
    """Schema for anomaly detection responses"""
    id: int
    organization_id: int
    model_id: int
    anomaly_type: str
    severity: SeverityLevel
    anomaly_score: float
    threshold_used: float
    data_source: str
    data_snapshot: Dict[str, Any]
    affected_metrics: List[str]
    business_impact: Optional[str] = None
    estimated_impact_value: Optional[float] = None
    alert_status: str
    assigned_to_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    detected_at: datetime
    data_timestamp: datetime

    class Config:
        from_attributes = True


class AnomalyUpdateRequest(BaseModel):
    """Schema for updating anomaly alerts"""
    alert_status: str = Field(..., description="New alert status")
    assigned_to_id: Optional[int] = Field(None, description="User ID to assign the alert to")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


# AI Insights Schemas

class AIInsightBase(BaseModel):
    """Base schema for AI insights"""
    insight_type: InsightType = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    category: str = Field(..., description="Business category (sales, finance, operations, customer)")
    data_sources: List[str] = Field(..., description="Data sources used")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")
    priority: Priority = Field(..., description="Priority level")
    potential_impact_value: Optional[float] = Field(None, description="Estimated monetary impact")
    implementation_effort: Optional[str] = Field(None, description="Implementation effort level")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Recommended actions")
    action_items: Optional[List[Dict[str, Any]]] = Field(None, description="Specific action items")
    valid_from: datetime = Field(..., description="Insight validity start date")
    valid_until: Optional[datetime] = Field(None, description="Insight validity end date")


class AIInsightCreate(AIInsightBase):
    """Schema for creating AI insights"""
    generated_by_model_id: Optional[int] = Field(None, description="ID of the AI model that generated this insight")


class AIInsightUpdate(BaseModel):
    """Schema for updating AI insights"""
    status: Optional[str] = Field(None, description="Insight status")
    assigned_to_id: Optional[int] = Field(None, description="User ID to assign the insight to")
    user_feedback: Optional[str] = Field(None, description="User feedback")
    feedback_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Feedback rating (1-5)")


class AIInsightResponse(AIInsightBase):
    """Schema for AI insight responses"""
    id: int
    organization_id: int
    generated_by_model_id: Optional[int] = None
    status: str
    assigned_to_id: Optional[int] = None
    user_feedback: Optional[str] = None
    feedback_rating: Optional[float] = None
    is_active: bool
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Model Performance Schemas

class ModelPerformanceMetricResponse(BaseModel):
    """Schema for model performance metrics"""
    id: int
    model_id: int
    metric_name: str
    metric_value: float
    baseline_value: Optional[float] = None
    evaluation_dataset: Optional[str] = None
    evaluation_period_start: Optional[datetime] = None
    evaluation_period_end: Optional[datetime] = None
    sample_size: Optional[int] = None
    metric_metadata: Optional[Dict[str, Any]] = None
    measured_at: datetime

    class Config:
        from_attributes = True


class ModelPerformanceSummary(BaseModel):
    """Schema for model performance summary"""
    model_id: int
    model_name: str
    current_accuracy: Optional[float] = None
    accuracy_trend: Optional[str] = None  # 'improving', 'stable', 'declining'
    predictions_made: int
    last_prediction_at: Optional[datetime] = None
    performance_metrics: List[ModelPerformanceMetricResponse]


# Automation Workflow Schemas

class AutomationWorkflowBase(BaseModel):
    """Base schema for automation workflows"""
    workflow_name: str = Field(..., description="Name of the workflow")
    description: Optional[str] = Field(None, description="Workflow description")
    workflow_type: str = Field(..., description="Type of workflow (ai_triggered, scheduled, event_driven)")
    category: str = Field(..., description="Business category")
    trigger_conditions: Dict[str, Any] = Field(..., description="Conditions that trigger the workflow")
    trigger_schedule: Optional[str] = Field(None, description="Cron expression for scheduled workflows")
    workflow_steps: List[Dict[str, Any]] = Field(..., description="Ordered list of workflow steps")
    ai_models_used: Optional[List[int]] = Field(None, description="List of AI model IDs used")
    auto_approve: bool = Field(False, description="Auto-approve workflow actions")
    requires_human_approval: bool = Field(True, description="Requires human approval")


class AutomationWorkflowCreate(AutomationWorkflowBase):
    """Schema for creating automation workflows"""
    pass


class AutomationWorkflowUpdate(BaseModel):
    """Schema for updating automation workflows"""
    workflow_name: Optional[str] = None
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    trigger_schedule: Optional[str] = None
    workflow_steps: Optional[List[Dict[str, Any]]] = None
    ai_models_used: Optional[List[int]] = None
    is_active: Optional[bool] = None
    auto_approve: Optional[bool] = None
    requires_human_approval: Optional[bool] = None


class AutomationWorkflowResponse(AutomationWorkflowBase):
    """Schema for automation workflow responses"""
    id: int
    organization_id: int
    is_active: bool
    execution_count: int
    success_count: int
    last_execution_at: Optional[datetime] = None
    last_execution_status: Optional[str] = None
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dashboard and Analytics Schemas

class AIAnalyticsDashboard(BaseModel):
    """Schema for AI analytics dashboard"""
    total_models: int
    active_models: int
    models_in_training: int
    total_predictions_today: int
    total_predictions_week: int
    total_predictions_month: int
    average_model_accuracy: Optional[float] = None
    active_anomalies: int
    critical_anomalies: int
    active_insights: int
    high_priority_insights: int
    automation_workflows: int
    active_automations: int
    generated_at: datetime


class PredictiveAnalyticsRequest(BaseModel):
    """Schema for predictive analytics requests"""
    prediction_type: str = Field(..., description="Type of prediction (revenue_forecast, customer_churn, etc.)")
    historical_days: int = Field(90, ge=30, le=365, description="Days of historical data to use")
    forecast_days: Optional[int] = Field(30, ge=1, le=180, description="Days to forecast into the future")
    include_confidence_intervals: bool = Field(True, description="Include confidence intervals in results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters for the analysis")


class PredictiveAnalyticsResponse(BaseModel):
    """Schema for predictive analytics responses"""
    prediction_type: str
    forecast_data: List[Dict[str, Any]]
    confidence_intervals: Optional[List[Dict[str, Any]]] = None
    model_accuracy: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None
    data_quality_score: Optional[float] = None
    recommendations: List[str]
    generated_at: datetime
    valid_until: Optional[datetime] = None


# Training and Deployment Schemas

class ModelTrainingRequest(BaseModel):
    """Schema for model training requests"""
    training_data_filters: Optional[Dict[str, Any]] = Field(None, description="Filters for training data")
    validation_split: float = Field(0.2, ge=0.1, le=0.4, description="Validation data split ratio")
    hyperparameter_tuning: bool = Field(True, description="Enable hyperparameter tuning")
    cross_validation: bool = Field(True, description="Enable cross-validation")


class ModelDeploymentRequest(BaseModel):
    """Schema for model deployment requests"""
    deployment_name: Optional[str] = Field(None, description="Custom deployment name")
    auto_scaling: bool = Field(True, description="Enable auto-scaling")
    monitoring_enabled: bool = Field(True, description="Enable performance monitoring")


class ModelTrainingStatus(BaseModel):
    """Schema for model training status"""
    model_id: int
    status: ModelStatusEnum
    progress_percentage: Optional[float] = None
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    training_logs: Optional[List[str]] = None
    current_metrics: Optional[Dict[str, float]] = None


# Error and Validation Schemas

class AIAnalyticsError(BaseModel):
    """Schema for AI analytics errors"""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    model_id: Optional[int] = None
    prediction_id: Optional[str] = None


class ValidationError(BaseModel):
    """Schema for validation errors"""
    field: str
    message: str
    invalid_value: Optional[Any] = None