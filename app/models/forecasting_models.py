"""
Forecasting Models - Multi-year forecasting, ML predictions, and driver-based modeling
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from decimal import Decimal
import enum
from typing import Optional, Dict, List

from .base import Base


class ForecastMethodType(enum.Enum):
    """Forecasting method types"""
    HISTORICAL_TREND = "historical_trend"
    LINEAR_REGRESSION = "linear_regression"
    TIME_SERIES = "time_series"
    ARIMA = "arima"
    DRIVER_BASED = "driver_based"
    ML_ENSEMBLE = "ml_ensemble"
    MANUAL = "manual"


class ForecastFrequency(enum.Enum):
    """Forecast frequency options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class ForecastStatus(enum.Enum):
    """Forecast status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FinancialForecast(Base):
    """Master financial forecast model"""
    __tablename__ = "financial_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Forecast identification
    forecast_name: Mapped[str] = mapped_column(String(200), nullable=False)
    forecast_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # revenue, expenses, cash_flow, etc.
    forecast_method: Mapped[ForecastMethodType] = mapped_column(Enum(ForecastMethodType), nullable=False, index=True)
    
    # Time period
    base_period_start: Mapped[date] = mapped_column(Date, nullable=False)  # Historical data start
    base_period_end: Mapped[date] = mapped_column(Date, nullable=False)    # Historical data end
    forecast_start: Mapped[date] = mapped_column(Date, nullable=False)     # Forecast start
    forecast_end: Mapped[date] = mapped_column(Date, nullable=False)       # Forecast end
    frequency: Mapped[ForecastFrequency] = mapped_column(Enum(ForecastFrequency), nullable=False)
    
    # Model configuration
    model_parameters: Mapped[Dict] = mapped_column(JSON, nullable=False)   # ML model parameters
    business_drivers: Mapped[Dict] = mapped_column(JSON, nullable=False)   # Key business drivers
    historical_data: Mapped[Dict] = mapped_column(JSON, nullable=False)    # Historical data used
    
    # Forecast results
    forecast_data: Mapped[Dict] = mapped_column(JSON, nullable=False)      # Projected values
    confidence_intervals: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # Upper/lower bounds
    
    # Model performance
    accuracy_metrics: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # MAE, RMSE, etc.
    last_validation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    validation_period_accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # %
    
    # Status and approval
    status: Mapped[ForecastStatus] = mapped_column(Enum(ForecastStatus), default=ForecastStatus.DRAFT, nullable=False)
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Is this the baseline forecast?
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])
    forecast_versions: Mapped[List["ForecastVersion"]] = relationship("ForecastVersion", back_populates="financial_forecast")
    driver_models: Mapped[List["BusinessDriverModel"]] = relationship("BusinessDriverModel", back_populates="financial_forecast")
    
    __table_args__ = (
        Index('idx_forecast_org_type', 'organization_id', 'forecast_type'),
        Index('idx_forecast_method_status', 'forecast_method', 'status'),
    )


class ForecastVersion(Base):
    """Version control for forecasts"""
    __tablename__ = "forecast_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    financial_forecast_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_forecasts.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Version details
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    version_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    change_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Snapshot of forecast data at this version
    forecast_snapshot: Mapped[Dict] = mapped_column(JSON, nullable=False)
    model_parameters_snapshot: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Version metadata
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    financial_forecast: Mapped["FinancialForecast"] = relationship("FinancialForecast", back_populates="forecast_versions")
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_forecast_version_current', 'financial_forecast_id', 'is_current'),
        UniqueConstraint('financial_forecast_id', 'version_number', name='uq_forecast_version'),
    )


class BusinessDriverModel(Base):
    """Business driver models for driver-based forecasting"""
    __tablename__ = "business_driver_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    financial_forecast_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_forecasts.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Driver details
    driver_name: Mapped[str] = mapped_column(String(200), nullable=False)
    driver_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # operational, financial, market
    driver_type: Mapped[str] = mapped_column(String(50), nullable=False)  # volume, price, rate, index
    
    # Driver data
    historical_values: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Historical driver values
    projected_values: Mapped[Dict] = mapped_column(JSON, nullable=False)   # Forecasted driver values
    correlation_metrics: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # Correlation with other drivers
    
    # Model relationship
    impact_formula: Mapped[str] = mapped_column(Text, nullable=False)  # How this driver impacts the forecast
    elasticity: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)  # % change impact
    
    # External data source
    data_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    external_api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_sync_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    financial_forecast: Mapped["FinancialForecast"] = relationship("FinancialForecast", back_populates="driver_models")
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_driver_forecast_category', 'financial_forecast_id', 'driver_category'),
    )


class MLForecastModel(Base):
    """Machine Learning forecast models and their metadata"""
    __tablename__ = "ml_forecast_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Model identification
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # linear_regression, random_forest, etc.
    target_variable: Mapped[str] = mapped_column(String(100), nullable=False)  # What we're predicting
    
    # Model configuration
    features: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # Input features
    hyperparameters: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Model hyperparameters
    preprocessing_steps: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Data preprocessing
    
    # Training data
    training_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    training_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    training_data_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Model performance
    training_accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # %
    validation_accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # %
    test_accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # %
    
    # Performance metrics
    mae: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)  # Mean Absolute Error
    rmse: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)  # Root Mean Square Error
    mape: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # Mean Absolute Percentage Error
    
    # Feature importance
    feature_importance: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    
    # Model storage
    model_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Path to serialized model
    model_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Metadata
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    predictions: Mapped[List["MLPrediction"]] = relationship("MLPrediction", back_populates="ml_model")
    
    __table_args__ = (
        Index('idx_ml_model_org_type', 'organization_id', 'model_type'),
        Index('idx_ml_model_active_prod', 'is_active', 'is_production'),
    )


class MLPrediction(Base):
    """ML model predictions and their metadata"""
    __tablename__ = "ml_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ml_model_id: Mapped[int] = mapped_column(Integer, ForeignKey("ml_forecast_models.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Prediction details
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)  # Date the prediction is for
    predicted_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # 0-100%
    
    # Prediction intervals
    lower_bound: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    upper_bound: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Input features used for this prediction
    input_features: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Actual vs predicted (for model validation)
    actual_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    prediction_error: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Metadata
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ml_model: Mapped["MLForecastModel"] = relationship("MLForecastModel", back_populates="predictions")
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        Index('idx_prediction_model_date', 'ml_model_id', 'prediction_date'),
    )


class RiskAnalysis(Base):
    """Risk analysis and early warning signals"""
    __tablename__ = "risk_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Risk identification
    risk_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # financial, operational, market
    risk_name: Mapped[str] = mapped_column(String(200), nullable=False)
    risk_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Risk metrics
    probability: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100%
    impact_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 1-10 scale
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # Calculated risk score
    
    # Financial impact
    potential_financial_impact: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Risk indicators
    key_indicators: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Metrics to monitor
    threshold_values: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Alert thresholds
    current_indicator_values: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    
    # Alert status
    alert_level: Mapped[str] = mapped_column(String(20), default="low", nullable=False)  # low, medium, high, critical
    is_active_alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Mitigation
    mitigation_strategies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mitigation_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    risk_events: Mapped[List["RiskEvent"]] = relationship("RiskEvent", back_populates="risk_analysis")
    
    __table_args__ = (
        Index('idx_risk_org_category', 'organization_id', 'risk_category'),
        Index('idx_risk_alert_level', 'alert_level', 'is_active_alert'),
    )


class RiskEvent(Base):
    """Risk events and incident tracking"""
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    risk_analysis_id: Mapped[int] = mapped_column(Integer, ForeignKey("risk_analysis.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Event details
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    event_description: Mapped[str] = mapped_column(Text, nullable=False)
    severity_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, critical
    
    # Financial impact
    actual_financial_impact: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    recovery_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Response
    response_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolution_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, in_progress, resolved
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reported_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    risk_analysis: Mapped["RiskAnalysis"] = relationship("RiskAnalysis", back_populates="risk_events")
    organization: Mapped["Organization"] = relationship("Organization")
    reported_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_risk_event_date_severity', 'event_date', 'severity_level'),
    )


class AutomatedInsight(Base):
    """AI-generated business insights and recommendations"""
    __tablename__ = "automated_insights"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Insight details
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # trend, anomaly, opportunity, risk
    insight_category: Mapped[str] = mapped_column(String(100), nullable=False)  # financial, operational, market
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # AI analysis
    data_sources: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # What data was analyzed
    analysis_method: Mapped[str] = mapped_column(String(100), nullable=False)  # Statistical method used
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-100%
    
    # Impact assessment
    importance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 1-10 scale
    potential_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Supporting data
    supporting_metrics: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    visualization_data: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    
    # Status and feedback
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False)  # new, reviewed, acted_upon, dismissed
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    usefulness_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 rating
    
    # Metadata
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # When insight becomes stale
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    reviewed_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_insight_org_type', 'organization_id', 'insight_type'),
        Index('idx_insight_status_generated', 'status', 'generated_at'),
        Index('idx_insight_importance', 'importance_score', 'confidence_score'),
    )