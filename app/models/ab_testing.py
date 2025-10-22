"""
A/B Testing Models for Model Version Comparison
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime
import enum


class ExperimentStatus(str, enum.Enum):
    """Status of an A/B testing experiment"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VariantType(str, enum.Enum):
    """Type of variant in an experiment"""
    CONTROL = "control"
    TREATMENT = "treatment"


class ABTestExperiment(Base):
    """
    Model for A/B testing experiments.
    Manages experiments for comparing model versions.
    """
    __tablename__ = "ab_test_experiments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_ab_test_org_id"), 
        nullable=False, 
        index=True
    )
    experiment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ExperimentStatus] = mapped_column(
        SQLEnum(ExperimentStatus), 
        default=ExperimentStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Experiment configuration
    traffic_split: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # e.g., {"control": 50, "treatment": 50}
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_ab_test_created_by"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    variants: Mapped[List["ABTestVariant"]] = relationship("ABTestVariant", back_populates="experiment", cascade="all, delete-orphan")
    results: Mapped[List["ABTestResult"]] = relationship("ABTestResult", back_populates="experiment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_ab_test_org_status', 'organization_id', 'status'),
        Index('idx_ab_test_dates', 'start_date', 'end_date'),
    )


class ABTestVariant(Base):
    """
    Model for A/B test variants.
    Represents different model versions being tested.
    """
    __tablename__ = "ab_test_variants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ab_test_experiments.id", name="fk_variant_experiment_id"), 
        nullable=False, 
        index=True
    )
    variant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_type: Mapped[VariantType] = mapped_column(
        SQLEnum(VariantType), 
        nullable=False
    )
    
    # Model configuration
    model_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("ai_models.id", name="fk_variant_model_id"), 
        nullable=True
    )
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    variant_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Traffic allocation
    traffic_percentage: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    experiment: Mapped["ABTestExperiment"] = relationship("ABTestExperiment", back_populates="variants")
    model: Mapped[Optional["AIModel"]] = relationship("AIModel", foreign_keys=[model_id])
    
    __table_args__ = (
        Index('idx_variant_experiment', 'experiment_id'),
    )


class ABTestResult(Base):
    """
    Model for storing A/B test results.
    Tracks metrics and outcomes for each variant.
    """
    __tablename__ = "ab_test_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ab_test_experiments.id", name="fk_result_experiment_id"), 
        nullable=False, 
        index=True
    )
    variant_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ab_test_variants.id", name="fk_result_variant_id"), 
        nullable=False, 
        index=True
    )
    
    # User tracking
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_result_user_id"), 
        nullable=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Result metrics
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Additional data
    result_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    experiment: Mapped["ABTestExperiment"] = relationship("ABTestExperiment", back_populates="results")
    variant: Mapped["ABTestVariant"] = relationship("ABTestVariant")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_result_experiment_variant', 'experiment_id', 'variant_id'),
        Index('idx_result_recorded_at', 'recorded_at'),
    )


class ABTestAssignment(Base):
    """
    Model for tracking user assignments to variants.
    Ensures consistent user experience across sessions.
    """
    __tablename__ = "ab_test_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    experiment_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ab_test_experiments.id", name="fk_assignment_experiment_id"), 
        nullable=False, 
        index=True
    )
    variant_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("ab_test_variants.id", name="fk_assignment_variant_id"), 
        nullable=False
    )
    
    # User identification
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_assignment_user_id"), 
        nullable=True,
        index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Assignment metadata
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    experiment: Mapped["ABTestExperiment"] = relationship("ABTestExperiment")
    variant: Mapped["ABTestVariant"] = relationship("ABTestVariant")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_assignment_experiment_user', 'experiment_id', 'user_id'),
        Index('idx_assignment_experiment_session', 'experiment_id', 'session_id'),
    )