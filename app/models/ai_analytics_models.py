"""
AI Analytics Models for Machine Learning and Predictive Analytics
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import enum


class ModelStatus(enum.Enum):
    """AI Model status enumeration"""
    DRAFT = "draft"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class PredictionType(enum.Enum):
    """Prediction type enumeration"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    FORECASTING = "forecasting"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"


class AIModel(Base):
    """
    Model for storing AI/ML model metadata and configurations
    """
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ai_model_organization_id"), nullable=False, index=True)
    
    # Model details
    model_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model_type: Mapped[PredictionType] = mapped_column(SQLEnum(PredictionType), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String, nullable=False, default="1.0.0")
    
    # Model configuration
    algorithm: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'random_forest', 'linear_regression', 'lstm'
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feature_columns: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    target_column: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Model status and performance
    status: Mapped[ModelStatus] = mapped_column(SQLEnum(ModelStatus), nullable=False, default=ModelStatus.DRAFT)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    performance_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Stores model performance data
    
    # Training metadata
    training_data_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Source table/view name
    training_data_filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    training_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    training_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    training_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Deployment metadata
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    model_file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Path to serialized model file
    model_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Usage and maintenance
    prediction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_prediction_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retraining_frequency_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    next_retraining_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_ai_model_created_by_id"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ai_model_updated_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])

    __table_args__ = (
        UniqueConstraint('organization_id', 'model_name', 'version', name='uq_ai_model_org_name_version'),
        Index('idx_ai_model_org_status', 'organization_id', 'status'),
        Index('idx_ai_model_org_type', 'organization_id', 'model_type'),
    )


class PredictionResult(Base):
    """
    Model for storing AI prediction results and outcomes
    """
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_prediction_result_organization_id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_models.id", name="fk_prediction_result_model_id"), nullable=False, index=True)
    
    # Prediction details
    prediction_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)  # UUID for tracking
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)  # Input features used for prediction
    prediction_output: Mapped[dict] = mapped_column(JSON, nullable=False)  # Model output/prediction
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context and metadata
    prediction_context: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g., 'sales_forecast', 'customer_churn'
    business_entity_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g., 'customer', 'product', 'order'
    business_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ID of the business entity
    
    # Validation and feedback
    actual_outcome: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Actual result for validation
    feedback_provided: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Human feedback on prediction quality
    
    # Usage tracking
    requested_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_prediction_result_requested_by_id"), nullable=True)
    api_endpoint: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # API endpoint used
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    prediction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    outcome_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    model: Mapped["AIModel"] = relationship("AIModel")
    requested_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[requested_by_id])

    __table_args__ = (
        Index('idx_prediction_result_org_model', 'organization_id', 'model_id'),
        Index('idx_prediction_result_org_context', 'organization_id', 'prediction_context'),
        Index('idx_prediction_result_org_timestamp', 'organization_id', 'prediction_timestamp'),
        Index('idx_prediction_result_entity', 'business_entity_type', 'business_entity_id'),
    )


class AnomalyDetection(Base):
    """
    Model for storing anomaly detection results and alerts
    """
    __tablename__ = "anomaly_detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_anomaly_detection_organization_id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_models.id", name="fk_anomaly_detection_model_id"), nullable=False, index=True)
    
    # Anomaly details
    anomaly_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # e.g., 'sales_drop', 'unusual_pattern'
    severity: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    threshold_used: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Data and context
    data_source: Mapped[str] = mapped_column(String, nullable=False)  # Source table/view
    data_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)  # Snapshot of data that triggered anomaly
    affected_metrics: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # List of metrics showing anomalies
    
    # Business context
    business_impact: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'revenue', 'customer', 'operational'
    estimated_impact_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Monetary impact estimate
    
    # Alert management
    alert_status: Mapped[str] = mapped_column(String, nullable=False, default="open")  # 'open', 'investigating', 'resolved', 'false_positive'
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_anomaly_detection_assigned_to_id"), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # When the anomalous data occurred

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    model: Mapped["AIModel"] = relationship("AIModel")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])

    __table_args__ = (
        Index('idx_anomaly_detection_org_type', 'organization_id', 'anomaly_type'),
        Index('idx_anomaly_detection_org_severity', 'organization_id', 'severity'),
        Index('idx_anomaly_detection_org_status', 'organization_id', 'alert_status'),
        Index('idx_anomaly_detection_org_detected', 'organization_id', 'detected_at'),
    )


class AIInsight(Base):
    """
    Model for storing AI-generated business insights and recommendations
    """
    __tablename__ = "ai_insights"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ai_insight_organization_id"), nullable=False, index=True)
    
    # Insight details
    insight_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # e.g., 'opportunity', 'risk', 'optimization'
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'sales', 'finance', 'operations', 'customer'
    
    # Insight source and confidence
    generated_by_model_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_models.id", name="fk_ai_insight_model_id"), nullable=True)
    data_sources: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # Source tables/modules
    confidence_level: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    
    # Business impact
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium")  # 'low', 'medium', 'high', 'urgent'
    potential_impact_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Estimated monetary impact
    implementation_effort: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'low', 'medium', 'high'
    
    # Recommendations and actions
    recommendations: Mapped[List[dict]] = mapped_column(JSON, nullable=True)  # List of recommended actions
    action_items: Mapped[List[dict]] = mapped_column(JSON, nullable=True)  # Specific action items
    
    # Insight status and feedback
    status: Mapped[str] = mapped_column(String, nullable=False, default="new")  # 'new', 'reviewing', 'implementing', 'completed', 'dismissed'
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ai_insight_assigned_to_id"), nullable=True)
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 1.0 to 5.0
    
    # Validity and expiration
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # User tracking
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ai_insight_reviewed_by_id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    generated_by_model: Mapped[Optional["AIModel"]] = relationship("AIModel", foreign_keys=[generated_by_model_id])
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    reviewed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by_id])

    __table_args__ = (
        Index('idx_ai_insight_org_type', 'organization_id', 'insight_type'),
        Index('idx_ai_insight_org_category', 'organization_id', 'category'),
        Index('idx_ai_insight_org_status', 'organization_id', 'status'),
        Index('idx_ai_insight_org_priority', 'organization_id', 'priority'),
        Index('idx_ai_insight_org_active', 'organization_id', 'is_active'),
    )


class ModelPerformanceMetric(Base):
    """
    Model for tracking AI model performance metrics over time
    """
    __tablename__ = "model_performance_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_model_performance_organization_id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_models.id", name="fk_model_performance_model_id"), nullable=False, index=True)
    
    # Performance metrics
    metric_name: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'accuracy', 'precision', 'recall', 'f1_score', etc.
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Baseline for comparison
    
    # Context
    evaluation_dataset: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Dataset used for evaluation
    evaluation_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    evaluation_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Additional metadata
    metric_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional metric details
    
    # Timestamps
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    model: Mapped["AIModel"] = relationship("AIModel")

    __table_args__ = (
        UniqueConstraint('model_id', 'metric_name', 'measured_at', name='uq_model_performance_metric_time'),
        Index('idx_model_performance_org_model', 'organization_id', 'model_id'),
        Index('idx_model_performance_model_metric', 'model_id', 'metric_name'),
        Index('idx_model_performance_org_measured', 'organization_id', 'measured_at'),
    )


class AutomationWorkflow(Base):
    """
    Model for storing intelligent automation workflows
    """
    __tablename__ = "automation_workflows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_automation_workflow_organization_id"), nullable=False, index=True)
    
    # Workflow details
    workflow_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workflow_type: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'ai_triggered', 'scheduled', 'event_driven'
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'finance', 'sales', 'operations', 'hr'
    
    # Trigger configuration
    trigger_conditions: Mapped[dict] = mapped_column(JSON, nullable=False)  # Conditions that trigger the workflow
    trigger_schedule: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Cron expression for scheduled workflows
    
    # Workflow definition
    workflow_steps: Mapped[List[dict]] = mapped_column(JSON, nullable=False)  # Ordered list of workflow steps
    ai_models_used: Mapped[List[int]] = mapped_column(JSON, nullable=True)  # List of AI model IDs used in workflow
    
    # Execution settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_approve: Mapped[bool] = mapped_column(Boolean, default=False)  # Auto-approve workflow actions
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Performance tracking
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    last_execution_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_execution_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_automation_workflow_created_by_id"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_automation_workflow_updated_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by_id])

    __table_args__ = (
        UniqueConstraint('organization_id', 'workflow_name', name='uq_automation_workflow_org_name'),
        Index('idx_automation_workflow_org_type', 'organization_id', 'workflow_type'),
        Index('idx_automation_workflow_org_category', 'organization_id', 'category'),
        Index('idx_automation_workflow_org_active', 'organization_id', 'is_active'),
    )