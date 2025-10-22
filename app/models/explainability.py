"""
Explainability Models for SHAP and LIME model interpretability
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
import enum


class ExplainabilityMethod(enum.Enum):
    """Methods for model explainability"""
    SHAP = "shap"
    LIME = "lime"
    FEATURE_IMPORTANCE = "feature_importance"
    PARTIAL_DEPENDENCE = "partial_dependence"
    ICE_PLOT = "ice_plot"


class ExplainabilityScope(enum.Enum):
    """Scope of explainability analysis"""
    GLOBAL = "global"  # Overall model behavior
    LOCAL = "local"    # Individual prediction explanation
    COHORT = "cohort"  # Group of predictions


class ModelExplainability(Base):
    """
    Model for storing model explainability configurations and results
    """
    __tablename__ = "model_explainability"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_model_explainability_org_id"), nullable=False, index=True)
    
    # Model reference
    model_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # References various model tables
    model_type: Mapped[str] = mapped_column(String, nullable=False)  # predictive_model, automl_run, etc.
    model_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Explainability configuration
    method: Mapped[ExplainabilityMethod] = mapped_column(SQLEnum(ExplainabilityMethod), nullable=False, index=True)
    scope: Mapped[ExplainabilityScope] = mapped_column(SQLEnum(ExplainabilityScope), nullable=False, index=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Analysis description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Results
    feature_importance: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    lime_explanation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    visualization_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Summary statistics
    top_features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    feature_correlations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    is_cached: Mapped[bool] = mapped_column(Boolean, default=True)
    cache_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    computation_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # seconds
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_model_explainability_created_by"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])


class PredictionExplanation(Base):
    """
    Model for storing individual prediction explanations
    """
    __tablename__ = "prediction_explanations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_prediction_explanation_org_id"), nullable=False, index=True)
    model_explainability_id: Mapped[int] = mapped_column(Integer, ForeignKey("model_explainability.id", name="fk_prediction_explanation_explainability_id"), nullable=False, index=True)
    
    # Prediction reference
    prediction_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    # Input data
    input_features: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Prediction details
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Explanation results
    method: Mapped[ExplainabilityMethod] = mapped_column(SQLEnum(ExplainabilityMethod), nullable=False)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    lime_explanation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    feature_contributions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Top contributing features
    top_positive_features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    top_negative_features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Visualization
    visualization_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    model_explainability: Mapped["ModelExplainability"] = relationship("ModelExplainability")


class ExplainabilityReport(Base):
    """
    Model for storing comprehensive explainability reports
    """
    __tablename__ = "explainability_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_explainability_report_org_id"), nullable=False, index=True)
    
    # Report identification
    report_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String, nullable=False)  # global_summary, feature_analysis, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Model references
    model_ids: Mapped[list] = mapped_column(JSON, nullable=False)  # List of model IDs analyzed
    
    # Report content
    summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    feature_analysis: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    model_comparisons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    visualizations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Key findings
    key_insights: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Report metadata
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    report_format: Mapped[str] = mapped_column(String, default="json")  # json, pdf, html
    report_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # User tracking
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_explainability_report_created_by"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
