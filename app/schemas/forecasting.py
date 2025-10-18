# app/schemas/forecasting.py
"""
Forecasting Schemas - Request/Response models for ML forecasting and scenario analysis
"""

from pydantic import BaseModel, Field, validator, SkipValidation
from typing import Optional, Dict, List, Any, Union
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from app.models.forecasting_models import ForecastMethodType, ForecastFrequency, ForecastStatus

# Base forecasting schemas
class FinancialForecastBase(BaseModel):
    forecast_name: str = Field(..., description="Name of the forecast")
    forecast_type: str = Field(..., description="Type of forecast (revenue, expenses, cash_flow, etc.)")
    forecast_method: ForecastMethodType = Field(..., description="Forecasting method")
    base_period_start: SkipValidation[date] = Field(..., description="Historical data period start")
    base_period_end: SkipValidation[date] = Field(..., description="Historical data period end")
    forecast_start: SkipValidation[date] = Field(..., description="Forecast period start")
    forecast_end: SkipValidation[date] = Field(..., description="Forecast period end")
    frequency: ForecastFrequency = Field(..., description="Forecast frequency")
    model_parameters: Dict[str, Any] = Field(..., description="Model parameters and configuration")
    business_drivers: Dict[str, Any] = Field(..., description="Key business drivers")

class FinancialForecastCreate(FinancialForecastBase):
    historical_data: Dict[str, Any] = Field(..., description="Historical data for training")

class FinancialForecastUpdate(BaseModel):
    forecast_name: Optional[str] = None
    model_parameters: Optional[Dict[str, Any]] = None
    business_drivers: Optional[Dict[str, Any]] = None
    status: Optional[ForecastStatus] = None
    is_baseline: Optional[bool] = None

class FinancialForecastResponse(FinancialForecastBase):
    id: int
    organization_id: int
    historical_data: Dict[str, Any]
    forecast_data: Dict[str, Any]
    confidence_intervals: Optional[Dict[str, Any]]
    accuracy_metrics: Optional[Dict[str, Any]]
    last_validation_date: Optional[SkipValidation[date]]
    validation_period_accuracy: Optional[Decimal]
    status: ForecastStatus
    is_baseline: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True

# Business driver schemas
class BusinessDriverBase(BaseModel):
    driver_name: str = Field(..., description="Name of the business driver")
    driver_category: str = Field(..., description="Category (operational, financial, market)")
    driver_type: str = Field(..., description="Type (volume, price, rate, index)")
    impact_formula: str = Field(..., description="Formula for how this driver impacts the forecast")
    elasticity: Optional[Decimal] = Field(None, description="Elasticity coefficient")
    data_source: Optional[str] = Field(None, description="External data source")
    external_api_endpoint: Optional[str] = Field(None, description="API endpoint for external data")

class BusinessDriverCreate(BusinessDriverBase):
    financial_forecast_id: int = Field(..., description="Associated forecast ID")
    historical_values: Dict[str, Any] = Field(..., description="Historical driver values")
    projected_values: Dict[str, Any] = Field(..., description="Projected driver values")

class BusinessDriverUpdate(BaseModel):
    driver_name: Optional[str] = None
    historical_values: Optional[Dict[str, Any]] = None
    projected_values: Optional[Dict[str, Any]] = None
    impact_formula: Optional[str] = None
    elasticity: Optional[Decimal] = None
    is_active: Optional[bool] = None

class BusinessDriverResponse(BusinessDriverBase):
    id: int
    financial_forecast_id: int
    organization_id: int
    historical_values: Dict[str, Any]
    projected_values: Dict[str, Any]
    correlation_metrics: Optional[Dict[str, Any]]
    last_sync_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# ML Model schemas
class MLModelConfiguration(BaseModel):
    model_type: str = Field(..., description="Type of ML model (linear_regression, random_forest, etc.)")
    features: List[str] = Field(..., description="List of input features")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    preprocessing_steps: Dict[str, Any] = Field(default_factory=dict, description="Data preprocessing configuration")
    cross_validation_folds: int = Field(default=5, ge=2, le=10, description="Number of CV folds")
    test_size: float = Field(default=0.2, ge=0.1, le=0.5, description="Test set size")

class MLForecastModelBase(BaseModel):
    model_name: str = Field(..., description="ML model name")
    model_type: str = Field(..., description="Type of ML model")
    target_variable: str = Field(..., description="Target variable being predicted")
    features: List[str] = Field(..., description="Input features")
    hyperparameters: Dict[str, Any] = Field(..., description="Model hyperparameters")
    preprocessing_steps: Dict[str, Any] = Field(..., description="Data preprocessing steps")
    training_period_start: SkipValidation[date] = Field(..., description="Training data start date")
    training_period_end: SkipValidation[date] = Field(..., description="Training data end date")

class MLForecastModelCreate(MLForecastModelBase):
    training_data: Dict[str, Any] = Field(..., description="Training dataset")

class MLForecastModelResponse(MLForecastModelBase):
    id: int
    organization_id: int
    training_data_size: int
    training_accuracy: Optional[Decimal]
    validation_accuracy: Optional[Decimal]
    test_accuracy: Optional[Decimal]
    mae: Optional[Decimal]
    rmse: Optional[Decimal]
    mape: Optional[Decimal]
    feature_importance: Optional[Dict[str, Any]]
    model_file_path: Optional[str]
    model_version: str
    is_active: bool
    is_production: bool
    trained_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Prediction schemas
class PredictionRequest(BaseModel):
    model_id: int = Field(..., description="ML model ID to use for prediction")
    prediction_date: SkipValidation[date] = Field(..., description="Date to predict for")
    input_features: Dict[str, Any] = Field(..., description="Input feature values")
    include_confidence: bool = Field(default=True, description="Include confidence intervals")

class MLPredictionResponse(BaseModel):
    id: int
    ml_model_id: int
    organization_id: int
    prediction_date: SkipValidation[date]
    predicted_value: Decimal
    confidence_score: Optional[Decimal]
    lower_bound: Optional[Decimal]
    upper_bound: Optional[Decimal]
    input_features: Dict[str, Any]
    actual_value: Optional[Decimal]
    prediction_error: Optional[Decimal]
    predicted_at: datetime

    class Config:
        from_attributes = True

# Risk Analysis schemas
class RiskAnalysisBase(BaseModel):
    risk_category: str = Field(..., description="Risk category (financial, operational, market)")
    risk_name: str = Field(..., description="Name of the risk")
    risk_description: Optional[str] = Field(None, description="Detailed risk description")
    probability: Decimal = Field(..., ge=0, le=100, description="Risk probability (0-100%)")
    impact_score: Decimal = Field(..., ge=1, le=10, description="Risk impact score (1-10)")
    potential_financial_impact: Optional[Decimal] = Field(None, description="Potential financial impact")
    key_indicators: Dict[str, Any] = Field(..., description="Key risk indicators to monitor")
    threshold_values: Dict[str, Any] = Field(..., description="Alert threshold values")
    mitigation_strategies: Optional[str] = Field(None, description="Risk mitigation strategies")

class RiskAnalysisCreate(RiskAnalysisBase):
    pass

class RiskAnalysisUpdate(BaseModel):
    risk_description: Optional[str] = None
    probability: Optional[Decimal] = None
    impact_score: Optional[Decimal] = None
    potential_financial_impact: Optional[Decimal] = None
    key_indicators: Optional[Dict[str, Any]] = None
    threshold_values: Optional[Dict[str, Any]] = None
    current_indicator_values: Optional[Dict[str, Any]] = None
    alert_level: Optional[str] = None
    mitigation_strategies: Optional[str] = None
    mitigation_status: Optional[str] = None

class RiskAnalysisResponse(RiskAnalysisBase):
    id: int
    organization_id: int
    risk_score: Decimal
    current_indicator_values: Optional[Dict[str, Any]]
    alert_level: str
    is_active_alert: bool
    mitigation_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_assessed_at: Optional[datetime]
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Risk Event schemas
class RiskEventBase(BaseModel):
    event_description: str = Field(..., description="Description of the risk event")
    severity_level: str = Field(..., description="Severity level (low, medium, high, critical)")
    actual_financial_impact: Optional[Decimal] = Field(None, description="Actual financial impact")
    recovery_cost: Optional[Decimal] = Field(None, description="Cost of recovery")
    response_actions: Optional[str] = Field(None, description="Response actions taken")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned from the event")

class RiskEventCreate(RiskEventBase):
    risk_analysis_id: int = Field(..., description="Associated risk analysis ID")
    event_date: SkipValidation[date] = Field(..., description="Date of the risk event")

class RiskEventUpdate(BaseModel):
    event_description: Optional[str] = None
    severity_level: Optional[str] = None
    actual_financial_impact: Optional[Decimal] = None
    recovery_cost: Optional[Decimal] = None
    response_actions: Optional[str] = None
    resolution_date: Optional[SkipValidation[date]] = None
    lessons_learned: Optional[str] = None
    status: Optional[str] = None

class RiskEventResponse(RiskEventBase):
    id: int
    risk_analysis_id: int
    organization_id: int
    event_date: SkipValidation[date]
    resolution_date: Optional[SkipValidation[date]]
    status: str
    created_at: datetime
    updated_at: datetime
    reported_by_id: Optional[int]

    class Config:
        from_attributes = True

# Automated Insights schemas
class AutomatedInsightBase(BaseModel):
    insight_type: str = Field(..., description="Type of insight (trend, anomaly, opportunity, risk)")
    insight_category: str = Field(..., description="Category (financial, operational, market)")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    analysis_method: str = Field(..., description="Analysis method used")
    confidence_score: Decimal = Field(..., ge=0, le=100, description="Confidence score (0-100%)")
    importance_score: Decimal = Field(..., ge=1, le=10, description="Importance score (1-10)")
    potential_impact: Optional[str] = Field(None, description="Potential impact description")
    recommended_actions: Optional[str] = Field(None, description="Recommended actions")

class AutomatedInsightCreate(AutomatedInsightBase):
    data_sources: List[str] = Field(..., description="Data sources analyzed")
    supporting_metrics: Optional[Dict[str, Any]] = Field(None, description="Supporting metrics")
    visualization_data: Optional[Dict[str, Any]] = Field(None, description="Data for visualizations")
    expires_at: Optional[datetime] = Field(None, description="When insight becomes stale")

class AutomatedInsightUpdate(BaseModel):
    status: Optional[str] = None
    user_feedback: Optional[str] = None
    usefulness_rating: Optional[int] = Field(None, ge=1, le=5, description="Usefulness rating (1-5)")

class AutomatedInsightResponse(AutomatedInsightBase):
    id: int
    organization_id: int
    data_sources: List[str]
    supporting_metrics: Optional[Dict[str, Any]]
    visualization_data: Optional[Dict[str, Any]]
    status: str
    user_feedback: Optional[str]
    usefulness_rating: Optional[int]
    generated_at: datetime
    expires_at: Optional[datetime]
    reviewed_by_id: Optional[int]
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Forecast version schemas
class ForecastVersionResponse(BaseModel):
    id: int
    financial_forecast_id: int
    organization_id: int
    version_number: str
    version_name: Optional[str]
    change_description: Optional[str]
    forecast_snapshot: Dict[str, Any]
    model_parameters_snapshot: Dict[str, Any]
    is_current: bool
    created_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Complex forecasting requests
class MultiVariateForecastRequest(BaseModel):
    forecast_name: str = Field(..., description="Name for the forecast")
    target_variables: List[str] = Field(..., description="Variables to forecast")
    predictor_variables: List[str] = Field(..., description="Predictor variables")
    forecast_horizon: int = Field(..., ge=1, le=60, description="Forecast horizon in periods")
    frequency: ForecastFrequency = Field(..., description="Forecast frequency")
    model_type: str = Field(default="auto", description="Model type (auto, var, lstm, etc.)")
    include_seasonality: bool = Field(default=True, description="Include seasonal components")
    include_trend: bool = Field(default=True, description="Include trend components")
    confidence_level: float = Field(default=0.95, ge=0.8, le=0.99, description="Confidence level for intervals")

class ScenarioForecastRequest(BaseModel):
    base_forecast_id: int = Field(..., description="Base forecast to create scenarios from")
    scenarios: List[Dict[str, Any]] = Field(..., description="List of scenario definitions")
    include_monte_carlo: bool = Field(default=False, description="Include Monte Carlo simulation")
    monte_carlo_iterations: int = Field(default=1000, ge=100, le=10000, description="Monte Carlo iterations")

class SensitivityAnalysisRequest(BaseModel):
    forecast_id: int = Field(..., description="Forecast to analyze")
    sensitivity_variables: List[str] = Field(..., description="Variables to test sensitivity for")
    variation_range: Dict[str, float] = Field(..., description="Variation range for each variable (±%)")
    steps: int = Field(default=10, ge=5, le=50, description="Number of steps in sensitivity analysis")

class ForecastAccuracyReport(BaseModel):
    forecast_id: int
    actual_vs_predicted: Dict[str, Any]
    accuracy_metrics: Dict[str, Decimal]
    error_analysis: Dict[str, Any]
    recommendations: List[str]
    analysis_period: str
    generated_at: datetime

class EarlyWarningSignal(BaseModel):
    signal_type: str = Field(..., description="Type of warning signal")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    description: str = Field(..., description="Signal description")
    affected_metrics: List[str] = Field(..., description="Affected business metrics")
    threshold_breach: Dict[str, Any] = Field(..., description="Threshold breach details")
    recommended_actions: List[str] = Field(..., description="Recommended immediate actions")
    confidence_score: Decimal = Field(..., description="Confidence in the signal")
    triggered_at: datetime = Field(..., description="When the signal was triggered")

class ForecastDashboardData(BaseModel):
    active_forecasts: int
    forecast_accuracy_avg: Decimal
    recent_predictions: List[Dict[str, Any]]
    risk_alerts: List[Dict[str, Any]]
    key_insights: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    trend_analysis: Dict[str, Any]