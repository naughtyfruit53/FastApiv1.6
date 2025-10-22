"""
Pydantic schemas for ML Analytics API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class PredictiveModelTypeEnum(str, Enum):
    """Types of predictive models"""
    SALES_FORECAST = "sales_forecast"
    DEMAND_PREDICTION = "demand_prediction"
    CHURN_PREDICTION = "churn_prediction"
    REVENUE_FORECAST = "revenue_forecast"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    PRICE_OPTIMIZATION = "price_optimization"
    LEAD_SCORING = "lead_scoring"


class AnomalyTypeEnum(str, Enum):
    """Types of anomaly detection"""
    REVENUE_ANOMALY = "revenue_anomaly"
    INVENTORY_ANOMALY = "inventory_anomaly"
    TRANSACTION_ANOMALY = "transaction_anomaly"
    CUSTOMER_BEHAVIOR_ANOMALY = "customer_behavior_anomaly"
    OPERATIONAL_ANOMALY = "operational_anomaly"
    QUALITY_ANOMALY = "quality_anomaly"


class DataSourceTypeEnum(str, Enum):
    """External data source types"""
    DATABASE = "database"
    API = "api"
    FILE_UPLOAD = "file_upload"
    CLOUD_STORAGE = "cloud_storage"
    STREAMING = "streaming"


class SeverityLevelEnum(str, Enum):
    """Severity levels for anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Predictive Model Schemas

class PredictiveModelBase(BaseModel):
    """Base schema for predictive models"""
    model_name: str = Field(..., description="Name of the predictive model")
    model_type: PredictiveModelTypeEnum = Field(..., description="Type of predictive model")
    description: Optional[str] = Field(None, description="Model description")
    algorithm: str = Field(..., description="ML algorithm (e.g., random_forest, xgboost, lstm)")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")
    feature_engineering: Optional[Dict[str, Any]] = Field(None, description="Feature transformation rules")
    training_config: Dict[str, Any] = Field(..., description="Training configuration")
    validation_split: float = Field(0.2, ge=0.1, le=0.5, description="Validation data split ratio")
    test_split: float = Field(0.1, ge=0.05, le=0.3, description="Test data split ratio")


class PredictiveModelCreate(PredictiveModelBase):
    """Schema for creating predictive models"""
    pass


class PredictiveModelUpdate(BaseModel):
    """Schema for updating predictive models"""
    model_name: Optional[str] = None
    description: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PredictiveModelResponse(PredictiveModelBase):
    """Schema for predictive model responses"""
    id: int
    organization_id: int
    version: str
    accuracy_score: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2_score: Optional[float] = None
    is_active: bool
    deployed_at: Optional[datetime] = None
    prediction_count: int
    last_prediction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Anomaly Detection Schemas

class AnomalyDetectionModelBase(BaseModel):
    """Base schema for anomaly detection models"""
    detection_name: str = Field(..., description="Name of the anomaly detection configuration")
    anomaly_type: AnomalyTypeEnum = Field(..., description="Type of anomaly to detect")
    description: Optional[str] = Field(None, description="Detection description")
    algorithm: str = Field(..., description="Detection algorithm (e.g., isolation_forest, one_class_svm)")
    detection_config: Dict[str, Any] = Field(..., description="Detection configuration parameters")
    threshold_config: Dict[str, Any] = Field(..., description="Threshold settings")
    monitored_metrics: List[str] = Field(..., description="List of metrics to monitor")
    detection_frequency: str = Field(..., description="Detection frequency (hourly, daily, weekly)")


class AnomalyDetectionModelCreate(AnomalyDetectionModelBase):
    """Schema for creating anomaly detection models"""
    pass


class AnomalyDetectionModelUpdate(BaseModel):
    """Schema for updating anomaly detection models"""
    detection_name: Optional[str] = None
    description: Optional[str] = None
    detection_config: Optional[Dict[str, Any]] = None
    threshold_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AnomalyDetectionModelResponse(AnomalyDetectionModelBase):
    """Schema for anomaly detection model responses"""
    id: int
    organization_id: int
    is_active: bool
    last_detection_at: Optional[datetime] = None
    anomalies_detected_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnomalyDetectionResultResponse(BaseModel):
    """Schema for anomaly detection result responses"""
    id: int
    organization_id: int
    anomaly_model_id: int
    detected_at: datetime
    severity: SeverityLevelEnum
    anomaly_score: float
    affected_data: Dict[str, Any]
    expected_range: Optional[Dict[str, Any]] = None
    actual_value: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    root_cause_analysis: Optional[str] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    is_false_positive: bool
    false_positive_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnomalyResolutionRequest(BaseModel):
    """Schema for resolving anomalies"""
    resolution_notes: str = Field(..., description="Notes about the resolution")
    is_false_positive: bool = Field(False, description="Mark as false positive")
    false_positive_reason: Optional[str] = Field(None, description="Reason for false positive")


# External Data Source Schemas

class ExternalDataSourceBase(BaseModel):
    """Base schema for external data sources"""
    source_name: str = Field(..., description="Name of the external data source")
    source_type: DataSourceTypeEnum = Field(..., description="Type of data source")
    description: Optional[str] = Field(None, description="Data source description")
    connection_config: Dict[str, Any] = Field(..., description="Connection configuration")
    authentication_config: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")
    data_schema: Optional[Dict[str, Any]] = Field(None, description="Data schema definition")
    field_mapping: Optional[Dict[str, Any]] = Field(None, description="Field mappings")
    sync_frequency: str = Field(..., description="Sync frequency (realtime, hourly, daily, weekly)")


class ExternalDataSourceCreate(ExternalDataSourceBase):
    """Schema for creating external data sources"""
    pass


class ExternalDataSourceUpdate(BaseModel):
    """Schema for updating external data sources"""
    source_name: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    sync_frequency: Optional[str] = None
    is_active: Optional[bool] = None


class ExternalDataSourceResponse(ExternalDataSourceBase):
    """Schema for external data source responses"""
    id: int
    organization_id: int
    is_active: bool
    sync_status: str
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    total_records_synced: int
    last_sync_duration_seconds: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Prediction Schemas

class PredictionRequest(BaseModel):
    """Schema for making predictions"""
    model_id: int = Field(..., description="ID of the predictive model to use")
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    context_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context metadata")


class PredictionResponse(BaseModel):
    """Schema for prediction responses"""
    prediction_id: int
    model_id: int
    predicted_value: Dict[str, Any]
    confidence_score: Optional[float] = None
    prediction_timestamp: datetime

    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    """Schema for prediction history responses"""
    id: int
    organization_id: int
    model_id: int
    prediction_timestamp: datetime
    input_data: Dict[str, Any]
    predicted_value: Dict[str, Any]
    confidence_score: Optional[float] = None
    actual_value: Optional[Dict[str, Any]] = None
    prediction_error: Optional[float] = None
    context_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard and Analytics Schemas

class MLAnalyticsDashboard(BaseModel):
    """Schema for ML analytics dashboard"""
    total_models: int
    active_models: int
    total_predictions: int
    total_anomalies_detected: int
    unresolved_anomalies: int
    active_data_sources: int
    model_performance_summary: List[Dict[str, Any]]
    recent_anomalies: List[AnomalyDetectionResultResponse]
    prediction_trends: Dict[str, Any]


class ModelTrainingRequest(BaseModel):
    """Schema for training model requests"""
    model_id: int = Field(..., description="ID of the model to train")
    training_parameters: Optional[Dict[str, Any]] = Field(None, description="Override training parameters")


class ModelTrainingStatus(BaseModel):
    """Schema for model training status"""
    model_id: int
    status: str  # training, completed, failed
    progress: float
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class ModelDeploymentRequest(BaseModel):
    """Schema for deploying models"""
    model_id: int = Field(..., description="ID of the model to deploy")
    deployment_config: Optional[Dict[str, Any]] = Field(None, description="Deployment configuration")


class AdvancedAnalyticsRequest(BaseModel):
    """Schema for advanced analytics requests"""
    analysis_type: str = Field(..., description="Type of analysis (trend, correlation, segmentation)")
    data_source: str = Field(..., description="Data source for analysis")
    parameters: Dict[str, Any] = Field(..., description="Analysis parameters")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for analysis")


class AdvancedAnalyticsResponse(BaseModel):
    """Schema for advanced analytics responses"""
    analysis_type: str
    results: Dict[str, Any]
    insights: List[Dict[str, Any]]
    visualizations: Optional[Dict[str, Any]] = None
    generated_at: datetime
