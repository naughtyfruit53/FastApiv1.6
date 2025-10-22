"""
Explainability Service for SHAP and LIME model interpretability
"""

import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.explainability import (
    ModelExplainability, PredictionExplanation, ExplainabilityReport,
    ExplainabilityMethod, ExplainabilityScope
)
from app.models.user_models import User, Organization

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """Service for model explainability operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # MODEL EXPLAINABILITY MANAGEMENT
    # ============================================================================
    
    def create_model_explainability(
        self,
        organization_id: int,
        model_id: int,
        model_type: str,
        model_name: str,
        method: ExplainabilityMethod,
        scope: ExplainabilityScope,
        config: Dict[str, Any],
        description: Optional[str] = None,
        created_by_id: int = None
    ) -> ModelExplainability:
        """Create a new model explainability configuration"""
        try:
            explainability = ModelExplainability(
                organization_id=organization_id,
                model_id=model_id,
                model_type=model_type,
                model_name=model_name,
                method=method,
                scope=scope,
                config=config,
                description=description,
                created_by_id=created_by_id,
                cache_expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.db.add(explainability)
            self.db.commit()
            self.db.refresh(explainability)
            
            logger.info(f"Created model explainability for model '{model_name}' (ID: {model_id})")
            return explainability
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating model explainability: {str(e)}")
            raise
    
    def get_model_explainability(
        self,
        organization_id: int,
        model_id: int,
        model_type: str,
        method: Optional[ExplainabilityMethod] = None
    ) -> Optional[ModelExplainability]:
        """Get explainability configuration for a model"""
        query = self.db.query(ModelExplainability).filter(
            and_(
                ModelExplainability.organization_id == organization_id,
                ModelExplainability.model_id == model_id,
                ModelExplainability.model_type == model_type
            )
        )
        
        if method:
            query = query.filter(ModelExplainability.method == method)
        
        return query.first()
    
    def update_explainability_results(
        self,
        explainability_id: int,
        feature_importance: Optional[Dict[str, Any]] = None,
        shap_values: Optional[Dict[str, Any]] = None,
        lime_explanation: Optional[Dict[str, Any]] = None,
        visualization_data: Optional[Dict[str, Any]] = None,
        top_features: Optional[List[Dict[str, Any]]] = None,
        computation_time: Optional[float] = None
    ) -> ModelExplainability:
        """Update explainability results"""
        explainability = self.db.query(ModelExplainability).filter(
            ModelExplainability.id == explainability_id
        ).first()
        
        if not explainability:
            raise ValueError(f"Model explainability {explainability_id} not found")
        
        if feature_importance is not None:
            explainability.feature_importance = feature_importance
        if shap_values is not None:
            explainability.shap_values = shap_values
        if lime_explanation is not None:
            explainability.lime_explanation = lime_explanation
        if visualization_data is not None:
            explainability.visualization_data = visualization_data
        if top_features is not None:
            explainability.top_features = top_features
        if computation_time is not None:
            explainability.computation_time = computation_time
        
        self.db.commit()
        self.db.refresh(explainability)
        
        return explainability
    
    # ============================================================================
    # PREDICTION EXPLANATIONS
    # ============================================================================
    
    def create_prediction_explanation(
        self,
        organization_id: int,
        model_explainability_id: int,
        input_features: Dict[str, Any],
        predicted_value: float,
        method: ExplainabilityMethod,
        shap_values: Optional[Dict[str, Any]] = None,
        lime_explanation: Optional[Dict[str, Any]] = None,
        feature_contributions: Optional[Dict[str, Any]] = None,
        prediction_id: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> PredictionExplanation:
        """Create a prediction explanation"""
        try:
            explanation = PredictionExplanation(
                organization_id=organization_id,
                model_explainability_id=model_explainability_id,
                prediction_id=prediction_id,
                input_features=input_features,
                predicted_value=predicted_value,
                confidence_score=confidence_score,
                method=method,
                shap_values=shap_values,
                lime_explanation=lime_explanation,
                feature_contributions=feature_contributions
            )
            
            # Extract top positive and negative features
            if feature_contributions:
                sorted_features = sorted(
                    feature_contributions.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
                explanation.top_positive_features = [
                    {"feature": k, "contribution": v}
                    for k, v in sorted_features if v > 0
                ][:5]
                
                explanation.top_negative_features = [
                    {"feature": k, "contribution": v}
                    for k, v in sorted_features if v < 0
                ][:5]
            
            self.db.add(explanation)
            self.db.commit()
            self.db.refresh(explanation)
            
            logger.info(f"Created prediction explanation for model explainability {model_explainability_id}")
            return explanation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating prediction explanation: {str(e)}")
            raise
    
    def get_prediction_explanations(
        self,
        organization_id: int,
        model_explainability_id: int,
        limit: int = 100
    ) -> List[PredictionExplanation]:
        """Get prediction explanations"""
        return self.db.query(PredictionExplanation).filter(
            and_(
                PredictionExplanation.organization_id == organization_id,
                PredictionExplanation.model_explainability_id == model_explainability_id
            )
        ).order_by(desc(PredictionExplanation.created_at)).limit(limit).all()
    
    # ============================================================================
    # EXPLAINABILITY REPORTS
    # ============================================================================
    
    def create_explainability_report(
        self,
        organization_id: int,
        report_name: str,
        report_type: str,
        model_ids: List[int],
        summary: Dict[str, Any],
        feature_analysis: Optional[Dict[str, Any]] = None,
        model_comparisons: Optional[Dict[str, Any]] = None,
        visualizations: Optional[List[Dict[str, Any]]] = None,
        key_insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        description: Optional[str] = None,
        created_by_id: int = None
    ) -> ExplainabilityReport:
        """Create an explainability report"""
        try:
            report = ExplainabilityReport(
                organization_id=organization_id,
                report_name=report_name,
                report_type=report_type,
                description=description,
                model_ids=model_ids,
                summary=summary,
                feature_analysis=feature_analysis,
                model_comparisons=model_comparisons,
                visualizations=visualizations or [],
                key_insights=key_insights or [],
                recommendations=recommendations or [],
                created_by_id=created_by_id
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Created explainability report '{report_name}' for organization {organization_id}")
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating explainability report: {str(e)}")
            raise
    
    def get_explainability_reports(
        self,
        organization_id: int,
        report_type: Optional[str] = None
    ) -> List[ExplainabilityReport]:
        """Get explainability reports"""
        query = self.db.query(ExplainabilityReport).filter(
            ExplainabilityReport.organization_id == organization_id
        )
        
        if report_type:
            query = query.filter(ExplainabilityReport.report_type == report_type)
        
        return query.order_by(desc(ExplainabilityReport.created_at)).all()
    
    def get_explainability_report(
        self,
        organization_id: int,
        report_id: int
    ) -> Optional[ExplainabilityReport]:
        """Get a specific explainability report"""
        return self.db.query(ExplainabilityReport).filter(
            and_(
                ExplainabilityReport.id == report_id,
                ExplainabilityReport.organization_id == organization_id
            )
        ).first()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def compute_shap_values(
        self,
        model: Any,
        data: np.ndarray,
        background_data: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Compute SHAP values for a model (stub implementation)
        In production, this would use the actual SHAP library
        """
        try:
            # This is a placeholder - actual implementation would use shap library
            num_features = data.shape[1] if len(data.shape) > 1 else len(data)
            
            shap_values = {
                "values": np.random.randn(num_features).tolist(),
                "base_value": 0.5,
                "data": data.tolist() if hasattr(data, 'tolist') else data
            }
            
            return shap_values
            
        except Exception as e:
            logger.error(f"Error computing SHAP values: {str(e)}")
            raise
    
    def compute_lime_explanation(
        self,
        model: Any,
        instance: np.ndarray,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """
        Compute LIME explanation for a prediction (stub implementation)
        In production, this would use the actual LIME library
        """
        try:
            # This is a placeholder - actual implementation would use lime library
            num_features = len(instance)
            
            lime_explanation = {
                "intercept": 0.5,
                "prediction_local": 0.7,
                "feature_weights": {
                    feature_names[i]: np.random.randn()
                    for i in range(min(num_features, len(feature_names)))
                }
            }
            
            return lime_explanation
            
        except Exception as e:
            logger.error(f"Error computing LIME explanation: {str(e)}")
            raise
    
    def get_explainability_dashboard(
        self,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get explainability dashboard data"""
        total_explainability = self.db.query(ModelExplainability).filter(
            ModelExplainability.organization_id == organization_id
        ).count()
        
        total_explanations = self.db.query(PredictionExplanation).filter(
            PredictionExplanation.organization_id == organization_id
        ).count()
        
        total_reports = self.db.query(ExplainabilityReport).filter(
            ExplainabilityReport.organization_id == organization_id
        ).count()
        
        recent_reports = self.get_explainability_reports(organization_id)[:5]
        
        return {
            "total_models_with_explainability": total_explainability,
            "total_prediction_explanations": total_explanations,
            "total_reports": total_reports,
            "recent_reports": [
                {
                    "id": report.id,
                    "report_name": report.report_name,
                    "report_type": report.report_type,
                    "model_count": len(report.model_ids),
                    "generated_at": report.generated_at.isoformat() if report.generated_at else None
                }
                for report in recent_reports
            ]
        }
