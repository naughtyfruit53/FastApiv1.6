"""
AI Analytics Service for Machine Learning and Predictive Analytics
"""

import logging
import uuid
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, and_, or_

from app.models.ai_analytics_models import (
    AIModel, PredictionResult, AnomalyDetection, AIInsight, 
    ModelPerformanceMetric, AutomationWorkflow, ModelStatus, PredictionType
)
from app.models.analytics_models import CustomerAnalytics, SalesAnalytics, ServiceAnalytics
from app.models.user_models import User, Organization
from app.schemas.ai_analytics import (
    AIModelCreate, PredictionRequest, AIInsightCreate, 
    PredictiveAnalyticsRequest, ModelTrainingRequest
)

logger = logging.getLogger(__name__)


class AIAnalyticsService:
    """Service for AI-powered analytics and machine learning operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # AI MODEL MANAGEMENT
    # ============================================================================
    
    def create_ai_model(
        self, 
        organization_id: int, 
        model_data: AIModelCreate, 
        created_by_id: int
    ) -> AIModel:
        """Create a new AI model"""
        try:
            # Check if model name already exists for this organization
            existing_model = self.db.query(AIModel).filter(
                and_(
                    AIModel.organization_id == organization_id,
                    AIModel.model_name == model_data.model_name
                )
            ).first()
            
            if existing_model:
                raise ValueError(f"Model with name '{model_data.model_name}' already exists")
            
            # Create new AI model
            ai_model = AIModel(
                organization_id=organization_id,
                model_name=model_data.model_name,
                model_type=model_data.model_type,
                description=model_data.description,
                algorithm=model_data.algorithm,
                hyperparameters=model_data.hyperparameters,
                feature_columns=model_data.feature_columns,
                target_column=model_data.target_column,
                training_data_source=model_data.training_data_source,
                training_data_filters=model_data.training_data_filters,
                retraining_frequency_days=model_data.retraining_frequency_days,
                created_by_id=created_by_id,
                status=ModelStatus.DRAFT
            )
            
            self.db.add(ai_model)
            self.db.commit()
            self.db.refresh(ai_model)
            
            logger.info(f"Created AI model '{model_data.model_name}' for organization {organization_id}")
            return ai_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating AI model: {str(e)}")
            raise
    
    def get_ai_models(
        self, 
        organization_id: int, 
        status: Optional[ModelStatus] = None,
        model_type: Optional[PredictionType] = None
    ) -> List[AIModel]:
        """Get AI models for an organization"""
        query = self.db.query(AIModel).filter(AIModel.organization_id == organization_id)
        
        if status:
            query = query.filter(AIModel.status == status)
        if model_type:
            query = query.filter(AIModel.model_type == model_type)
            
        return query.order_by(desc(AIModel.created_at)).all()
    
    def get_ai_model(self, organization_id: int, model_id: int) -> Optional[AIModel]:
        """Get a specific AI model"""
        return self.db.query(AIModel).filter(
            and_(
                AIModel.organization_id == organization_id,
                AIModel.id == model_id
            )
        ).first()
    
    def train_model(
        self, 
        organization_id: int, 
        model_id: int, 
        training_request: ModelTrainingRequest
    ) -> Dict[str, Any]:
        """Train an AI model (placeholder implementation)"""
        try:
            model = self.get_ai_model(organization_id, model_id)
            if not model:
                raise ValueError(f"Model {model_id} not found")
            
            if model.status not in [ModelStatus.DRAFT, ModelStatus.FAILED]:
                raise ValueError(f"Model is in {model.status} status and cannot be trained")
            
            # Update model status to training
            model.status = ModelStatus.TRAINING
            model.training_started_at = datetime.utcnow()
            
            # In a real implementation, this would trigger actual ML training
            # For now, we'll simulate training completion
            training_duration = 300  # 5 minutes simulation
            
            # Simulate training completion
            model.status = ModelStatus.TRAINED
            model.training_completed_at = datetime.utcnow()
            model.training_duration_seconds = training_duration
            model.accuracy_score = 0.85  # Simulated accuracy
            model.performance_metrics = {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85,
                "training_samples": 10000,
                "validation_samples": 2000
            }
            
            self.db.commit()
            
            # Log performance metrics
            self._log_performance_metrics(model.id, model.performance_metrics)
            
            logger.info(f"Model {model_id} training completed successfully")
            
            return {
                "model_id": model_id,
                "status": "completed",
                "accuracy": model.accuracy_score,
                "training_duration_seconds": training_duration,
                "performance_metrics": model.performance_metrics
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error training model {model_id}: {str(e)}")
            # Update model status to failed
            if 'model' in locals():
                model.status = ModelStatus.FAILED
                self.db.commit()
            raise
    
    def deploy_model(self, organization_id: int, model_id: int) -> Dict[str, Any]:
        """Deploy a trained model to production"""
        try:
            model = self.get_ai_model(organization_id, model_id)
            if not model:
                raise ValueError(f"Model {model_id} not found")
            
            if model.status != ModelStatus.TRAINED:
                raise ValueError(f"Model must be trained before deployment")
            
            # Update model status to deployed
            model.status = ModelStatus.DEPLOYED
            model.deployed_at = datetime.utcnow()
            
            # Set next retraining date if frequency is specified
            if model.retraining_frequency_days:
                model.next_retraining_at = datetime.utcnow() + timedelta(
                    days=model.retraining_frequency_days
                )
            
            self.db.commit()
            
            logger.info(f"Model {model_id} deployed successfully")
            
            return {
                "model_id": model_id,
                "status": "deployed",
                "deployed_at": model.deployed_at,
                "next_retraining_at": model.next_retraining_at
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deploying model {model_id}: {str(e)}")
            raise
    
    # ============================================================================
    # PREDICTION SERVICES
    # ============================================================================
    
    def make_prediction(
        self, 
        organization_id: int, 
        prediction_request: PredictionRequest,
        user_id: Optional[int] = None
    ) -> PredictionResult:
        """Make a prediction using a deployed AI model"""
        try:
            model = self.get_ai_model(organization_id, prediction_request.model_id)
            if not model:
                raise ValueError(f"Model {prediction_request.model_id} not found")
            
            if model.status != ModelStatus.DEPLOYED:
                raise ValueError(f"Model is not deployed (status: {model.status})")
            
            # Generate prediction ID
            prediction_id = str(uuid.uuid4())
            
            # Simulate prediction (in real implementation, this would use actual ML model)
            prediction_output = self._simulate_prediction(model, prediction_request.input_data)
            
            # Create prediction result record
            prediction_result = PredictionResult(
                organization_id=organization_id,
                model_id=model.id,
                prediction_id=prediction_id,
                input_data=prediction_request.input_data,
                prediction_output=prediction_output,
                confidence_score=prediction_output.get("confidence", 0.8),
                prediction_context=prediction_request.prediction_context,
                business_entity_type=prediction_request.business_entity_type,
                business_entity_id=prediction_request.business_entity_id,
                requested_by_id=user_id,
                processing_time_ms=25.5  # Simulated processing time
            )
            
            self.db.add(prediction_result)
            
            # Update model usage statistics
            model.prediction_count += 1
            model.last_prediction_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(prediction_result)
            
            logger.info(f"Prediction made using model {model.id}")
            return prediction_result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_prediction_results(
        self, 
        organization_id: int,
        model_id: Optional[int] = None,
        limit: int = 100
    ) -> List[PredictionResult]:
        """Get prediction results for an organization"""
        query = self.db.query(PredictionResult).filter(
            PredictionResult.organization_id == organization_id
        )
        
        if model_id:
            query = query.filter(PredictionResult.model_id == model_id)
        
        return query.order_by(desc(PredictionResult.prediction_timestamp)).limit(limit).all()
    
    # ============================================================================
    # ANOMALY DETECTION
    # ============================================================================
    
    def detect_anomalies(
        self, 
        organization_id: int,
        data_source: str,
        time_range_hours: int = 24
    ) -> List[AnomalyDetection]:
        """Detect anomalies in business data"""
        try:
            # Get data for anomaly detection
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            anomalies = []
            
            # Check for sales anomalies
            if data_source in ["sales", "all"]:
                sales_anomalies = self._detect_sales_anomalies(
                    organization_id, start_time, end_time
                )
                anomalies.extend(sales_anomalies)
            
            # Check for service anomalies
            if data_source in ["service", "all"]:
                service_anomalies = self._detect_service_anomalies(
                    organization_id, start_time, end_time
                )
                anomalies.extend(service_anomalies)
            
            # Check for customer behavior anomalies
            if data_source in ["customer", "all"]:
                customer_anomalies = self._detect_customer_anomalies(
                    organization_id, start_time, end_time
                )
                anomalies.extend(customer_anomalies)
            
            logger.info(f"Detected {len(anomalies)} anomalies for organization {organization_id}")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    def get_active_anomalies(
        self, 
        organization_id: int,
        severity: Optional[str] = None
    ) -> List[AnomalyDetection]:
        """Get active anomalies for an organization"""
        query = self.db.query(AnomalyDetection).filter(
            and_(
                AnomalyDetection.organization_id == organization_id,
                AnomalyDetection.alert_status == "open"
            )
        )
        
        if severity:
            query = query.filter(AnomalyDetection.severity == severity)
        
        return query.order_by(desc(AnomalyDetection.detected_at)).all()
    
    # ============================================================================
    # AI INSIGHTS GENERATION
    # ============================================================================
    
    def generate_insights(
        self, 
        organization_id: int,
        categories: Optional[List[str]] = None
    ) -> List[AIInsight]:
        """Generate AI-powered business insights"""
        try:
            insights = []
            
            # Generate sales insights
            if not categories or "sales" in categories:
                sales_insights = self._generate_sales_insights(organization_id)
                insights.extend(sales_insights)
            
            # Generate customer insights
            if not categories or "customer" in categories:
                customer_insights = self._generate_customer_insights(organization_id)
                insights.extend(customer_insights)
            
            # Generate operational insights
            if not categories or "operations" in categories:
                operational_insights = self._generate_operational_insights(organization_id)
                insights.extend(operational_insights)
            
            # Save insights to database
            for insight in insights:
                self.db.add(insight)
            
            self.db.commit()
            
            logger.info(f"Generated {len(insights)} insights for organization {organization_id}")
            return insights
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating insights: {str(e)}")
            raise
    
    def get_active_insights(
        self, 
        organization_id: int,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[AIInsight]:
        """Get active insights for an organization"""
        query = self.db.query(AIInsight).filter(
            and_(
                AIInsight.organization_id == organization_id,
                AIInsight.is_active == True,
                AIInsight.status.in_(["new", "reviewing", "implementing"])
            )
        )
        
        if priority:
            query = query.filter(AIInsight.priority == priority)
        if category:
            query = query.filter(AIInsight.category == category)
        
        return query.order_by(desc(AIInsight.created_at)).all()
    
    # ============================================================================
    # PREDICTIVE ANALYTICS
    # ============================================================================
    
    def generate_predictive_analytics(
        self, 
        organization_id: int,
        request: PredictiveAnalyticsRequest
    ) -> Dict[str, Any]:
        """Generate predictive analytics based on historical data"""
        try:
            if request.prediction_type == "revenue_forecast":
                return self._forecast_revenue(organization_id, request)
            elif request.prediction_type == "customer_churn":
                return self._predict_customer_churn(organization_id, request)
            elif request.prediction_type == "service_demand":
                return self._forecast_service_demand(organization_id, request)
            elif request.prediction_type == "inventory_optimization":
                return self._optimize_inventory(organization_id, request)
            else:
                raise ValueError(f"Unsupported prediction type: {request.prediction_type}")
                
        except Exception as e:
            logger.error(f"Error generating predictive analytics: {str(e)}")
            raise
    
    # ============================================================================
    # DASHBOARD AND REPORTING
    # ============================================================================
    
    def get_ai_analytics_dashboard(self, organization_id: int) -> Dict[str, Any]:
        """Get comprehensive AI analytics dashboard data"""
        try:
            # Model statistics
            total_models = self.db.query(AIModel).filter(
                AIModel.organization_id == organization_id
            ).count()
            
            active_models = self.db.query(AIModel).filter(
                and_(
                    AIModel.organization_id == organization_id,
                    AIModel.status == ModelStatus.DEPLOYED
                )
            ).count()
            
            models_in_training = self.db.query(AIModel).filter(
                and_(
                    AIModel.organization_id == organization_id,
                    AIModel.status == ModelStatus.TRAINING
                )
            ).count()
            
            # Prediction statistics
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=7)
            month_start = today - timedelta(days=30)
            
            predictions_today = self.db.query(PredictionResult).filter(
                and_(
                    PredictionResult.organization_id == organization_id,
                    func.date(PredictionResult.prediction_timestamp) == today
                )
            ).count()
            
            predictions_week = self.db.query(PredictionResult).filter(
                and_(
                    PredictionResult.organization_id == organization_id,
                    func.date(PredictionResult.prediction_timestamp) >= week_start
                )
            ).count()
            
            predictions_month = self.db.query(PredictionResult).filter(
                and_(
                    PredictionResult.organization_id == organization_id,
                    func.date(PredictionResult.prediction_timestamp) >= month_start
                )
            ).count()
            
            # Anomaly statistics
            active_anomalies = self.db.query(AnomalyDetection).filter(
                and_(
                    AnomalyDetection.organization_id == organization_id,
                    AnomalyDetection.alert_status == "open"
                )
            ).count()
            
            critical_anomalies = self.db.query(AnomalyDetection).filter(
                and_(
                    AnomalyDetection.organization_id == organization_id,
                    AnomalyDetection.alert_status == "open",
                    AnomalyDetection.severity == "critical"
                )
            ).count()
            
            # Insight statistics
            active_insights = self.db.query(AIInsight).filter(
                and_(
                    AIInsight.organization_id == organization_id,
                    AIInsight.is_active == True,
                    AIInsight.status.in_(["new", "reviewing", "implementing"])
                )
            ).count()
            
            high_priority_insights = self.db.query(AIInsight).filter(
                and_(
                    AIInsight.organization_id == organization_id,
                    AIInsight.is_active == True,
                    AIInsight.priority.in_(["high", "urgent"])
                )
            ).count()
            
            # Automation statistics
            total_workflows = self.db.query(AutomationWorkflow).filter(
                AutomationWorkflow.organization_id == organization_id
            ).count()
            
            active_workflows = self.db.query(AutomationWorkflow).filter(
                and_(
                    AutomationWorkflow.organization_id == organization_id,
                    AutomationWorkflow.is_active == True
                )
            ).count()
            
            # Calculate average model accuracy
            avg_accuracy_result = self.db.query(func.avg(AIModel.accuracy_score)).filter(
                and_(
                    AIModel.organization_id == organization_id,
                    AIModel.accuracy_score.isnot(None)
                )
            ).scalar()
            avg_accuracy = float(avg_accuracy_result) if avg_accuracy_result else None
            
            return {
                "total_models": total_models,
                "active_models": active_models,
                "models_in_training": models_in_training,
                "total_predictions_today": predictions_today,
                "total_predictions_week": predictions_week,
                "total_predictions_month": predictions_month,
                "average_model_accuracy": avg_accuracy,
                "active_anomalies": active_anomalies,
                "critical_anomalies": critical_anomalies,
                "active_insights": active_insights,
                "high_priority_insights": high_priority_insights,
                "automation_workflows": total_workflows,
                "active_automations": active_workflows,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting AI analytics dashboard: {str(e)}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _simulate_prediction(self, model: AIModel, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate prediction output (placeholder for actual ML prediction)"""
        if model.model_type == PredictionType.CLASSIFICATION:
            return {
                "prediction": "positive",
                "probability": 0.85,
                "confidence": 0.82,
                "class_probabilities": {"positive": 0.85, "negative": 0.15}
            }
        elif model.model_type == PredictionType.REGRESSION:
            return {
                "prediction": 1250.75,
                "confidence": 0.78,
                "prediction_interval": [1100.50, 1401.00]
            }
        elif model.model_type == PredictionType.FORECASTING:
            forecast_periods = 7  # 7-day forecast
            forecast_values = [1200 + i * 50 + np.random.normal(0, 20) for i in range(forecast_periods)]
            return {
                "forecast": forecast_values,
                "confidence": 0.75,
                "trend": "increasing",
                "seasonality": "weekly"
            }
        else:
            return {
                "prediction": "simulated_result",
                "confidence": 0.80
            }
    
    def _log_performance_metrics(self, model_id: int, metrics: Dict[str, Any]):
        """Log model performance metrics"""
        try:
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    performance_metric = ModelPerformanceMetric(
                        organization_id=self.db.query(AIModel).filter(AIModel.id == model_id).first().organization_id,
                        model_id=model_id,
                        metric_name=metric_name,
                        metric_value=float(metric_value)
                    )
                    self.db.add(performance_metric)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging performance metrics: {str(e)}")
    
    def _detect_sales_anomalies(
        self, 
        organization_id: int, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect sales-related anomalies"""
        # Placeholder implementation - would use actual anomaly detection algorithms
        return []
    
    def _detect_service_anomalies(
        self, 
        organization_id: int, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect service-related anomalies"""
        # Placeholder implementation
        return []
    
    def _detect_customer_anomalies(
        self, 
        organization_id: int, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect customer behavior anomalies"""
        # Placeholder implementation
        return []
    
    def _generate_sales_insights(self, organization_id: int) -> List[AIInsight]:
        """Generate sales-related insights"""
        # Placeholder implementation
        return []
    
    def _generate_customer_insights(self, organization_id: int) -> List[AIInsight]:
        """Generate customer-related insights"""
        # Placeholder implementation
        return []
    
    def _generate_operational_insights(self, organization_id: int) -> List[AIInsight]:
        """Generate operational insights"""
        # Placeholder implementation
        return []
    
    def _forecast_revenue(
        self, 
        organization_id: int, 
        request: PredictiveAnalyticsRequest
    ) -> Dict[str, Any]:
        """Generate revenue forecast"""
        # Placeholder implementation
        return {
            "prediction_type": "revenue_forecast",
            "forecast_data": [],
            "model_accuracy": 0.85,
            "recommendations": ["Increase marketing spend in Q2", "Focus on customer retention"],
            "generated_at": datetime.utcnow()
        }
    
    def _predict_customer_churn(
        self, 
        organization_id: int, 
        request: PredictiveAnalyticsRequest
    ) -> Dict[str, Any]:
        """Predict customer churn"""
        # Placeholder implementation
        return {
            "prediction_type": "customer_churn",
            "forecast_data": [],
            "model_accuracy": 0.78,
            "recommendations": ["Implement retention campaigns", "Improve customer service"],
            "generated_at": datetime.utcnow()
        }
    
    def _forecast_service_demand(
        self, 
        organization_id: int, 
        request: PredictiveAnalyticsRequest
    ) -> Dict[str, Any]:
        """Forecast service demand"""
        # Placeholder implementation
        return {
            "prediction_type": "service_demand",
            "forecast_data": [],
            "model_accuracy": 0.82,
            "recommendations": ["Increase technician capacity", "Optimize scheduling"],
            "generated_at": datetime.utcnow()
        }
    
    def _optimize_inventory(
        self, 
        organization_id: int, 
        request: PredictiveAnalyticsRequest
    ) -> Dict[str, Any]:
        """Optimize inventory levels"""
        # Placeholder implementation
        return {
            "prediction_type": "inventory_optimization",
            "forecast_data": [],
            "model_accuracy": 0.89,
            "recommendations": ["Reduce stock for item A", "Increase stock for item B"],
            "generated_at": datetime.utcnow()
        }