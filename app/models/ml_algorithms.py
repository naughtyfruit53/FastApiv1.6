"""
ML Algorithms Models for extended machine learning algorithm support
Includes CatBoost, LightGBM, TensorFlow, PyTorch support
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
import enum


class MLFramework(enum.Enum):
    """Supported ML frameworks"""
    SCIKIT_LEARN = "scikit_learn"
    CATBOOST = "catboost"
    LIGHTGBM = "lightgbm"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    XGBOOST = "xgboost"


class AlgorithmCategory(enum.Enum):
    """Categories of ML algorithms"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"
    TIME_SERIES = "time_series"


class TrainingStatus(enum.Enum):
    """Status of model training"""
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"


class MLAlgorithmConfig(Base):
    """
    Model for storing ML algorithm configurations
    """
    __tablename__ = "ml_algorithm_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ml_algorithm_config_org_id"), nullable=False, index=True)
    
    # Algorithm identification
    config_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    framework: Mapped[MLFramework] = mapped_column(SQLEnum(MLFramework), nullable=False, index=True)
    algorithm_name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[AlgorithmCategory] = mapped_column(SQLEnum(AlgorithmCategory), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configuration
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    preprocessing_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Framework-specific settings
    framework_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gpu_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    device_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_ml_algorithm_config_created_by"), nullable=False)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_ml_algorithm_config_updated_by"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])


class MLModelTraining(Base):
    """
    Model for tracking ML model training sessions
    """
    __tablename__ = "ml_model_trainings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_ml_model_training_org_id"), nullable=False, index=True)
    algorithm_config_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ml_algorithm_configs.id", name="fk_ml_model_training_config_id"), nullable=True, index=True)
    
    # Training identification
    training_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    framework: Mapped[MLFramework] = mapped_column(SQLEnum(MLFramework), nullable=False, index=True)
    algorithm_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Training configuration
    dataset_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    training_params: Mapped[dict] = mapped_column(JSON, nullable=False)
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Status and progress
    status: Mapped[TrainingStatus] = mapped_column(SQLEnum(TrainingStatus), nullable=False, default=TrainingStatus.PENDING, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_epoch: Mapped[int] = mapped_column(Integer, default=0)
    total_epochs: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Performance metrics
    training_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    validation_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    test_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Best model tracking
    best_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    best_epoch: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    best_model_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Training history
    training_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    loss_curve: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Model artifacts
    model_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    checkpoint_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Execution details
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    training_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # seconds
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Resource usage
    gpu_used: Mapped[bool] = mapped_column(Boolean, default=False)
    resource_usage: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    training_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_ml_model_training_created_by"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    algorithm_config: Mapped[Optional["MLAlgorithmConfig"]] = relationship("MLAlgorithmConfig")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])