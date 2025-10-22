"""
AutoML Models for automatic model selection and hyperparameter tuning
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
import enum


class AutoMLTaskType(enum.Enum):
    """Types of AutoML tasks"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TIME_SERIES = "time_series"
    CLUSTERING = "clustering"


class AutoMLStatus(enum.Enum):
    """Status of AutoML run"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutoMLFramework(enum.Enum):
    """AutoML frameworks supported"""
    AUTO_SKLEARN = "auto_sklearn"
    TPOT = "tpot"
    H2O = "h2o"
    AUTOKERAS = "autokeras"
    OPTUNA = "optuna"


class AutoMLRun(Base):
    """
    Model for storing AutoML runs with automatic model selection and hyperparameter tuning
    """
    __tablename__ = "automl_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_automl_run_org_id"), nullable=False, index=True)
    
    # Run identification
    run_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    task_type: Mapped[AutoMLTaskType] = mapped_column(SQLEnum(AutoMLTaskType), nullable=False, index=True)
    framework: Mapped[AutoMLFramework] = mapped_column(SQLEnum(AutoMLFramework), nullable=False, default=AutoMLFramework.OPTUNA)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration
    target_column: Mapped[str] = mapped_column(String, nullable=False)
    feature_columns: Mapped[list] = mapped_column(JSON, nullable=False)
    metric: Mapped[str] = mapped_column(String, nullable=False)  # accuracy, f1, rmse, etc.
    time_budget: Mapped[int] = mapped_column(Integer, default=3600)  # seconds
    max_trials: Mapped[int] = mapped_column(Integer, default=100)
    
    # Data configuration
    dataset_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dataset_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    train_test_split: Mapped[float] = mapped_column(Float, default=0.2)
    cross_validation_folds: Mapped[int] = mapped_column(Integer, default=5)
    
    # Run status
    status: Mapped[AutoMLStatus] = mapped_column(SQLEnum(AutoMLStatus), nullable=False, default=AutoMLStatus.PENDING, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_trial: Mapped[int] = mapped_column(Integer, default=0)
    
    # Results
    best_model_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    best_model_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    best_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    best_model_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # All trials history
    trials_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    leaderboard: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Top N models
    
    # Execution details
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_automl_run_created_by"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])


class AutoMLModelCandidate(Base):
    """
    Model for storing individual model candidates evaluated during AutoML
    """
    __tablename__ = "automl_model_candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    automl_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("automl_runs.id", name="fk_automl_candidate_run_id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_automl_candidate_org_id"), nullable=False, index=True)
    
    # Model details
    trial_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Performance metrics
    score: Mapped[float] = mapped_column(Float, nullable=False)
    training_time: Mapped[float] = mapped_column(Float, nullable=False)  # seconds
    evaluation_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Model artifacts
    model_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    automl_run: Mapped["AutoMLRun"] = relationship("AutoMLRun")
    organization: Mapped["Organization"] = relationship("Organization")
