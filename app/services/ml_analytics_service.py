"""
ML Analytics Service for Advanced Machine Learning and Predictive Analytics
Provides predictive modeling, anomaly detection, and external data integration
"""

import logging
import uuid
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, and_, or_

from app.models.ml_analytics import (
    PredictiveModel, AnomalyDetectionModel, AnomalyDetectionResult,
    ExternalDataSource, PredictionHistory,
    PredictiveModelType, AnomalyType, DataSourceType
)
from app.models.user_models import User, Organization
from app.schemas.ml_analytics import (
    PredictiveModelCreate, PredictiveModelUpdate,
    AnomalyDetectionModelCreate, AnomalyDetectionModelUpdate,
    ExternalDataSourceCreate, ExternalDataSourceUpdate,
    PredictionRequest, AnomalyResolutionRequest,
    ModelTrainingRequest, AdvancedAnalyticsRequest
)

logger = logging.getLogger(__name__)


class MLAnalyticsService:
    """Service for advanced ML analytics operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # PREDICTIVE MODEL MANAGEMENT
    # ============================================================================
    
    def create_predictive_model(
        self,
        organization_id: int,
        model_data: PredictiveModelCreate,
        created_by_id: int
    ) -> PredictiveModel:
        """Create a new predictive model"""
        try:
            # Check if model name already exists
            existing_model = self.db.query(PredictiveModel).filter(
                and_(
                    PredictiveModel.organization_id == organization_id,
                    PredictiveModel.model_name == model_data.model_name
                )
            ).first()
            
            if existing_model:
                raise ValueError(f"Model with name '{model_data.model_name}' already exists")
            
            # Create new predictive model
            model = PredictiveModel(
                organization_id=organization_id,
                model_name=model_data.model_name,
                model_type=model_data.model_type,
                description=model_data.description,
                algorithm=model_data.algorithm,
                hyperparameters=model_data.hyperparameters,
                feature_engineering=model_data.feature_engineering,
                training_config=model_data.training_config,
                validation_split=model_data.validation_split,
                test_split=model_data.test_split,
                created_by_id=created_by_id,
                is_active=False
            )
            
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Created predictive model '{model_data.model_name}' for organization {organization_id}")
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating predictive model: {str(e)}")
            raise
    
    def get_predictive_models(
        self,
        organization_id: int,
        model_type: Optional[PredictiveModelType] = None,
        is_active: Optional[bool] = None
    ) -> List[PredictiveModel]:
        """Get predictive models for an organization"""
        query = self.db.query(PredictiveModel).filter(
            PredictiveModel.organization_id == organization_id
        )
        
        if model_type:
            query = query.filter(PredictiveModel.model_type == model_type)
        if is_active is not None:
            query = query.filter(PredictiveModel.is_active == is_active)
            
        return query.order_by(desc(PredictiveModel.created_at)).all()
    
    def get_predictive_model(self, organization_id: int, model_id: int) -> Optional[PredictiveModel]:
        """Get a specific predictive model"""
        return self.db.query(PredictiveModel).filter(
            and_(
                PredictiveModel.organization_id == organization_id,
                PredictiveModel.id == model_id
            )
        ).first()
    
    def update_predictive_model(
        self,
        organization_id: int,
        model_id: int,
        model_data: PredictiveModelUpdate,
        updated_by_id: int
    ) -> Optional[PredictiveModel]:
        """Update a predictive model"""
        try:
            model = self.get_predictive_model(organization_id, model_id)
            if not model:
                return None
            
            update_dict = model_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(model, key, value)
            
            model.updated_by_id = updated_by_id
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Updated predictive model {model_id} for organization {organization_id}")
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating predictive model: {str(e)}")
            raise
    
    def delete_predictive_model(self, organization_id: int, model_id: int) -> bool:
        """Delete a predictive model"""
        try:
            model = self.get_predictive_model(organization_id, model_id)
            if not model:
                return False
            
            self.db.delete(model)
            self.db.commit()
            
            logger.info(f"Deleted predictive model {model_id} for organization {organization_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting predictive model: {str(e)}")
            raise
    
    # ============================================================================
    # ANOMALY DETECTION
    # ============================================================================
    
    def create_anomaly_detection_model(
        self,
        organization_id: int,
        model_data: AnomalyDetectionModelCreate,
        created_by_id: int
    ) -> AnomalyDetectionModel:
        """Create a new anomaly detection model"""
        try:
            # Check if detection name already exists
            existing_model = self.db.query(AnomalyDetectionModel).filter(
                and_(
                    AnomalyDetectionModel.organization_id == organization_id,
                    AnomalyDetectionModel.detection_name == model_data.detection_name
                )
            ).first()
            
            if existing_model:
                raise ValueError(f"Anomaly detection with name '{model_data.detection_name}' already exists")
            
            # Create new anomaly detection model
            model = AnomalyDetectionModel(
                organization_id=organization_id,
                detection_name=model_data.detection_name,
                anomaly_type=model_data.anomaly_type,
                description=model_data.description,
                algorithm=model_data.algorithm,
                detection_config=model_data.detection_config,
                threshold_config=model_data.threshold_config,
                monitored_metrics=model_data.monitored_metrics,
                detection_frequency=model_data.detection_frequency,
                created_by_id=created_by_id,
                is_active=True
            )
            
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Created anomaly detection model '{model_data.detection_name}' for organization {organization_id}")
            return model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating anomaly detection model: {str(e)}")
            raise
    
    def get_anomaly_detection_models(
        self,
        organization_id: int,
        anomaly_type: Optional[AnomalyType] = None,
        is_active: Optional[bool] = None
    ) -> List[AnomalyDetectionModel]:
        """Get anomaly detection models for an organization"""
        query = self.db.query(AnomalyDetectionModel).filter(
            AnomalyDetectionModel.organization_id == organization_id
        )
        
        if anomaly_type:
            query = query.filter(AnomalyDetectionModel.anomaly_type == anomaly_type)
        if is_active is not None:
            query = query.filter(AnomalyDetectionModel.is_active == is_active)
            
        return query.order_by(desc(AnomalyDetectionModel.created_at)).all()
    
    def get_anomaly_detection_results(
        self,
        organization_id: int,
        model_id: Optional[int] = None,
        is_resolved: Optional[bool] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[AnomalyDetectionResult]:
        """Get anomaly detection results"""
        query = self.db.query(AnomalyDetectionResult).filter(
            AnomalyDetectionResult.organization_id == organization_id
        )
        
        if model_id:
            query = query.filter(AnomalyDetectionResult.anomaly_model_id == model_id)
        if is_resolved is not None:
            query = query.filter(AnomalyDetectionResult.is_resolved == is_resolved)
        if severity:
            query = query.filter(AnomalyDetectionResult.severity == severity)
            
        return query.order_by(desc(AnomalyDetectionResult.detected_at)).limit(limit).all()
    
    def resolve_anomaly(
        self,
        organization_id: int,
        anomaly_id: int,
        resolution_data: AnomalyResolutionRequest,
        resolved_by_id: int
    ) -> Optional[AnomalyDetectionResult]:
        """Resolve an anomaly"""
        try:
            anomaly = self.db.query(AnomalyDetectionResult).filter(
                and_(
                    AnomalyDetectionResult.organization_id == organization_id,
                    AnomalyDetectionResult.id == anomaly_id
                )
            ).first()
            
            if not anomaly:
                return None
            
            anomaly.is_resolved = True
            anomaly.resolved_at = datetime.utcnow()
            anomaly.resolved_by_id = resolved_by_id
            anomaly.resolution_notes = resolution_data.resolution_notes
            anomaly.is_false_positive = resolution_data.is_false_positive
            anomaly.false_positive_reason = resolution_data.false_positive_reason
            
            self.db.commit()
            self.db.refresh(anomaly)
            
            logger.info(f"Resolved anomaly {anomaly_id} for organization {organization_id}")
            return anomaly
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resolving anomaly: {str(e)}")
            raise
    
    # ============================================================================
    # EXTERNAL DATA SOURCES
    # ============================================================================
    
    def create_external_data_source(
        self,
        organization_id: int,
        source_data: ExternalDataSourceCreate,
        created_by_id: int
    ) -> ExternalDataSource:
        """Create a new external data source"""
        try:
            # Check if source name already exists
            existing_source = self.db.query(ExternalDataSource).filter(
                and_(
                    ExternalDataSource.organization_id == organization_id,
                    ExternalDataSource.source_name == source_data.source_name
                )
            ).first()
            
            if existing_source:
                raise ValueError(f"Data source with name '{source_data.source_name}' already exists")
            
            # Create new external data source
            source = ExternalDataSource(
                organization_id=organization_id,
                source_name=source_data.source_name,
                source_type=source_data.source_type,
                description=source_data.description,
                connection_config=source_data.connection_config,
                authentication_config=source_data.authentication_config,
                data_schema=source_data.data_schema,
                field_mapping=source_data.field_mapping,
                sync_frequency=source_data.sync_frequency,
                created_by_id=created_by_id,
                is_active=True,
                sync_status="pending"
            )
            
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
            
            logger.info(f"Created external data source '{source_data.source_name}' for organization {organization_id}")
            return source
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating external data source: {str(e)}")
            raise
    
    def get_external_data_sources(
        self,
        organization_id: int,
        source_type: Optional[DataSourceType] = None,
        is_active: Optional[bool] = None
    ) -> List[ExternalDataSource]:
        """Get external data sources for an organization"""
        query = self.db.query(ExternalDataSource).filter(
            ExternalDataSource.organization_id == organization_id
        )
        
        if source_type:
            query = query.filter(ExternalDataSource.source_type == source_type)
        if is_active is not None:
            query = query.filter(ExternalDataSource.is_active == is_active)
            
        return query.order_by(desc(ExternalDataSource.created_at)).all()
    
    # ============================================================================
    # PREDICTIONS
    # ============================================================================
    
    def make_prediction(
        self,
        organization_id: int,
        prediction_request: PredictionRequest,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make a prediction using a predictive model"""
        try:
            model = self.get_predictive_model(organization_id, prediction_request.model_id)
            if not model:
                raise ValueError(f"Model {prediction_request.model_id} not found")
            
            if not model.is_active:
                raise ValueError(f"Model {prediction_request.model_id} is not active")
            
            # TODO: Implement actual prediction logic based on model algorithm
            # For now, return a mock prediction
            predicted_value = {
                "prediction": "mock_value",
                "details": "This is a mock prediction. Implement actual ML logic here."
            }
            confidence_score = 0.85
            
            # Store prediction history
            prediction_history = PredictionHistory(
                organization_id=organization_id,
                model_id=model.id,
                prediction_timestamp=datetime.utcnow(),
                input_data=prediction_request.input_data,
                predicted_value=predicted_value,
                confidence_score=confidence_score,
                user_id=user_id,
                context_metadata=prediction_request.context_metadata
            )
            
            self.db.add(prediction_history)
            
            # Update model statistics
            model.prediction_count += 1
            model.last_prediction_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(prediction_history)
            
            logger.info(f"Made prediction using model {model.id} for organization {organization_id}")
            
            return {
                "prediction_id": prediction_history.id,
                "model_id": model.id,
                "predicted_value": predicted_value,
                "confidence_score": confidence_score,
                "prediction_timestamp": prediction_history.prediction_timestamp
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_prediction_history(
        self,
        organization_id: int,
        model_id: Optional[int] = None,
        limit: int = 100
    ) -> List[PredictionHistory]:
        """Get prediction history"""
        query = self.db.query(PredictionHistory).filter(
            PredictionHistory.organization_id == organization_id
        )
        
        if model_id:
            query = query.filter(PredictionHistory.model_id == model_id)
            
        return query.order_by(desc(PredictionHistory.prediction_timestamp)).limit(limit).all()
    
    # ============================================================================
    # DASHBOARD AND ANALYTICS
    # ============================================================================
    
    def get_ml_analytics_dashboard(self, organization_id: int) -> Dict[str, Any]:
        """Get ML analytics dashboard data"""
        try:
            # Count total and active models
            total_models = self.db.query(func.count(PredictiveModel.id)).filter(
                PredictiveModel.organization_id == organization_id
            ).scalar() or 0
            
            active_models = self.db.query(func.count(PredictiveModel.id)).filter(
                and_(
                    PredictiveModel.organization_id == organization_id,
                    PredictiveModel.is_active == True
                )
            ).scalar() or 0
            
            # Count total predictions
            total_predictions = self.db.query(func.count(PredictionHistory.id)).filter(
                PredictionHistory.organization_id == organization_id
            ).scalar() or 0
            
            # Count anomalies
            total_anomalies = self.db.query(func.count(AnomalyDetectionResult.id)).filter(
                AnomalyDetectionResult.organization_id == organization_id
            ).scalar() or 0
            
            unresolved_anomalies = self.db.query(func.count(AnomalyDetectionResult.id)).filter(
                and_(
                    AnomalyDetectionResult.organization_id == organization_id,
                    AnomalyDetectionResult.is_resolved == False
                )
            ).scalar() or 0
            
            # Count active data sources
            active_data_sources = self.db.query(func.count(ExternalDataSource.id)).filter(
                and_(
                    ExternalDataSource.organization_id == organization_id,
                    ExternalDataSource.is_active == True
                )
            ).scalar() or 0
            
            # Get model performance summary
            models = self.get_predictive_models(organization_id)
            model_performance_summary = [
                {
                    "model_id": model.id,
                    "model_name": model.model_name,
                    "model_type": model.model_type.value,
                    "accuracy_score": model.accuracy_score,
                    "prediction_count": model.prediction_count,
                    "is_active": model.is_active
                }
                for model in models[:10]  # Top 10 models
            ]
            
            # Get recent anomalies
            recent_anomalies = self.get_anomaly_detection_results(
                organization_id=organization_id,
                limit=10
            )
            
            # Get prediction trends (mock data for now)
            prediction_trends = {
                "daily_predictions": [],
                "model_usage": [],
                "accuracy_trends": []
            }
            
            return {
                "total_models": total_models,
                "active_models": active_models,
                "total_predictions": total_predictions,
                "total_anomalies_detected": total_anomalies,
                "unresolved_anomalies": unresolved_anomalies,
                "active_data_sources": active_data_sources,
                "model_performance_summary": model_performance_summary,
                "recent_anomalies": [self._anomaly_to_dict(a) for a in recent_anomalies],
                "prediction_trends": prediction_trends
            }
            
        except Exception as e:
            logger.error(f"Error getting ML analytics dashboard: {str(e)}")
            raise
    
    def _anomaly_to_dict(self, anomaly: AnomalyDetectionResult) -> Dict[str, Any]:
        """Convert anomaly result to dictionary"""
        return {
            "id": anomaly.id,
            "organization_id": anomaly.organization_id,
            "anomaly_model_id": anomaly.anomaly_model_id,
            "detected_at": anomaly.detected_at.isoformat() if anomaly.detected_at else None,
            "severity": anomaly.severity,
            "anomaly_score": anomaly.anomaly_score,
            "affected_data": anomaly.affected_data,
            "is_resolved": anomaly.is_resolved,
            "created_at": anomaly.created_at.isoformat() if anomaly.created_at else None
        }
    
    def perform_advanced_analytics(
        self,
        organization_id: int,
        request: AdvancedAnalyticsRequest
    ) -> Dict[str, Any]:
        """Perform advanced analytics based on request"""
        try:
            # TODO: Implement actual advanced analytics logic
            # This is a placeholder implementation
            
            results = {
                "analysis_type": request.analysis_type,
                "data_source": request.data_source,
                "summary": "Mock advanced analytics results"
            }
            
            insights = [
                {
                    "insight_type": "trend",
                    "description": "This is a mock insight",
                    "confidence": 0.85
                }
            ]
            
            return {
                "analysis_type": request.analysis_type,
                "results": results,
                "insights": insights,
                "visualizations": {},
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error performing advanced analytics: {str(e)}")
            raise
