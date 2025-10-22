"""
ML Analytics Models for Advanced Machine Learning and Predictive Analytics
Extends AI Analytics with specific focus on predictive modeling, anomaly detection,
and external data source integration.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import enum


class PredictiveModelType(enum.Enum):
    """Types of predictive models"""
    SALES_FORECAST = "sales_forecast"
    DEMAND_PREDICTION = "demand_prediction"
    CHURN_PREDICTION = "churn_prediction"
    REVENUE_FORECAST = "revenue_forecast"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    PRICE_OPTIMIZATION = "price_optimization"
    LEAD_SCORING = "lead_scoring"


class AnomalyType(enum.Enum):
    """Types of anomaly detection"""
    REVENUE_ANOMALY = "revenue_anomaly"
    INVENTORY_ANOMALY = "inventory_anomaly"
    TRANSACTION_ANOMALY = "transaction_anomaly"
    CUSTOMER_BEHAVIOR_ANOMALY = "customer_behavior_anomaly"
    OPERATIONAL_ANOMALY = "operational_anomaly"
    QUALITY_ANOMALY = "quality_anomaly"


class DataSourceType(enum.Enum):
    """External data source types"""
    DATABASE = "database"
    API = "api"
    FILE_UPLOAD = "file_upload"
    CLOUD_STORAGE = "cloud_storage"
    STREAMING = "streaming"


class PredictiveModel(Base):
    """
    Model for storing predictive ML models with advanced analytics capabilities
    """
    __tablename__ = "predictive_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_predictive_model_org_id"), nullable=False, index=True)
    
    # Model identification
    model_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model_type: Mapped[PredictiveModelType] = mapped_column(SQLEnum(PredictiveModelType), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String, nullable=False, default="1.0.0")
    
    # Model configuration
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feature_engineering: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Feature transformation rules
    
    # Training configuration
    training_config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Training parameters
    validation_split: Mapped[float] = mapped_column(Float, default=0.2)
    test_split: Mapped[float] = mapped_column(Float, default=0.1)
    
    # Performance metrics
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mean Absolute Error
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Root Mean Square Error
    r2_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # R-squared
    
    # Deployment and usage
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    prediction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_prediction_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Model artifacts
    model_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_predictive_model_created_by"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_predictive_model_updated_by"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])

    __table_args__ = (
        UniqueConstraint('organization_id', 'model_name', 'version', name='uq_predictive_model_org_name_version'),
        Index('idx_predictive_model_org_type', 'organization_id', 'model_type'),
        Index('idx_predictive_model_active', 'organization_id', 'is_active'),
    )


class AnomalyDetectionModel(Base):
    """
    Model for anomaly detection configurations and results
    """
    __tablename__ = "anomaly_detection_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_anomaly_model_org_id"), nullable=False, index=True)
    
    # Detection configuration
    detection_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    anomaly_type: Mapped[AnomalyType] = mapped_column(SQLEnum(AnomalyType), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Algorithm configuration
    algorithm: Mapped[str] = mapped_column(String, nullable=False)  # isolation_forest, one_class_svm, etc.
    detection_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    threshold_config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Threshold settings
    
    # Monitoring settings
    monitored_metrics: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    detection_frequency: Mapped[str] = mapped_column(String, nullable=False)  # hourly, daily, weekly
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_detection_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    anomalies_detected_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_anomaly_model_created_by"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_anomaly_model_updated_by"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])

    __table_args__ = (
        UniqueConstraint('organization_id', 'detection_name', name='uq_anomaly_model_org_name'),
        Index('idx_anomaly_model_org_type', 'organization_id', 'anomaly_type'),
        Index('idx_anomaly_model_active', 'organization_id', 'is_active'),
    )


class AnomalyDetectionResult(Base):
    """
    Model for storing detected anomalies
    """
    __tablename__ = "anomaly_detection_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_anomaly_result_org_id"), nullable=False, index=True)
    anomaly_model_id: Mapped[int] = mapped_column(Integer, ForeignKey("anomaly_detection_models.id", name="fk_anomaly_result_model_id"), nullable=False, index=True)
    
    # Anomaly details
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)  # low, medium, high, critical
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Data details
    affected_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_range: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actual_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Context
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    root_cause_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_anomaly_result_resolved_by"), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # False positive tracking
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    false_positive_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    anomaly_model: Mapped["AnomalyDetectionModel"] = relationship("AnomalyDetectionModel")
    resolved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by_id])

    __table_args__ = (
        Index('idx_anomaly_result_org_detected', 'organization_id', 'detected_at'),
        Index('idx_anomaly_result_resolved', 'organization_id', 'is_resolved'),
        Index('idx_anomaly_result_severity', 'organization_id', 'severity'),
    )


class ExternalDataSource(Base):
    """
    Model for managing external data sources for analytics
    """
    __tablename__ = "external_data_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_external_data_source_org_id"), nullable=False, index=True)
    
    # Source identification
    source_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[DataSourceType] = mapped_column(SQLEnum(DataSourceType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Connection configuration
    connection_config: Mapped[dict] = mapped_column(JSON, nullable=False)  # Connection details
    authentication_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Auth credentials (encrypted)
    
    # Data mapping
    data_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Schema definition
    field_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Field mappings
    
    # Sync configuration
    sync_frequency: Mapped[str] = mapped_column(String, nullable=False)  # realtime, hourly, daily, weekly
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_status: Mapped[str] = mapped_column(String, default="pending")  # pending, syncing, success, failed
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metrics
    total_records_synced: Mapped[int] = mapped_column(Integer, default=0)
    last_sync_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_external_data_source_created_by"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_external_data_source_updated_by"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])

    __table_args__ = (
        UniqueConstraint('organization_id', 'source_name', name='uq_external_data_source_org_name'),
        Index('idx_external_data_source_org_type', 'organization_id', 'source_type'),
        Index('idx_external_data_source_active', 'organization_id', 'is_active'),
    )


class PredictionHistory(Base):
    """
    Model for storing prediction history for analysis and monitoring
    """
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_prediction_history_org_id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("predictive_models.id", name="fk_prediction_history_model_id"), nullable=False, index=True)
    
    # Prediction details
    prediction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    predicted_value: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Actual outcome (for model validation)
    actual_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    prediction_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_prediction_history_user_id"), nullable=True)
    context_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    model: Mapped["PredictiveModel"] = relationship("PredictiveModel")
    user: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index('idx_prediction_history_org_timestamp', 'organization_id', 'prediction_timestamp'),
        Index('idx_prediction_history_model_timestamp', 'model_id', 'prediction_timestamp'),
    )