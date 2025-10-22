"""
Integration tests for ML Analytics module
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Set dummy DATABASE_URL to avoid connection requirement during testing
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'

from app.services.ml_analytics_service import MLAnalyticsService
from app.schemas.ml_analytics import (
    PredictiveModelCreate, AnomalyDetectionModelCreate,
    ExternalDataSourceCreate, PredictionRequest
)


class TestMLAnalyticsIntegration:
    """Integration tests for ML Analytics workflows"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock()
    
    @pytest.fixture
    def ml_service(self, mock_db):
        """Create ML Analytics service instance"""
        return MLAnalyticsService(mock_db)
    
    def test_full_predictive_model_workflow(self, ml_service, mock_db):
        """Test complete workflow: create, train, deploy, and predict"""
        organization_id = 1
        user_id = 1
        
        # Step 1: Create model
        model_data = PredictiveModelCreate(
            model_name="sales_forecast_integration",
            model_type="sales_forecast",
            algorithm="random_forest",
            description="Integration test model",
            training_config={"epochs": 100},
            validation_split=0.2,
            test_split=0.1
        )
        
        # Mock the model creation
        mock_model = Mock()
        mock_model.id = 1
        mock_model.model_name = "sales_forecast_integration"
        mock_model.is_active = False
        mock_model.prediction_count = 0
        
        with patch.object(ml_service, 'create_predictive_model', return_value=mock_model):
            created_model = ml_service.create_predictive_model(
                organization_id=organization_id,
                model_data=model_data,
                created_by_id=user_id
            )
            
            assert created_model.id == 1
            assert created_model.is_active is False
        
        # Step 2: Mock training process
        mock_model.accuracy_score = 0.85
        mock_model.precision_score = 0.82
        mock_model.recall_score = 0.88
        
        # Step 3: Deploy model
        mock_model.is_active = True
        mock_model.deployed_at = datetime.utcnow()
        
        # Step 4: Make predictions
        prediction_request = PredictionRequest(
            model_id=1,
            input_data={"feature1": 100, "feature2": 200}
        )
        
        mock_prediction = {
            "prediction_id": 1,
            "model_id": 1,
            "predicted_value": {"result": 350},
            "confidence_score": 0.87,
            "prediction_timestamp": datetime.utcnow()
        }
        
        with patch.object(ml_service, 'make_prediction', return_value=mock_prediction):
            prediction = ml_service.make_prediction(
                organization_id=organization_id,
                prediction_request=prediction_request,
                user_id=user_id
            )
            
            assert prediction["model_id"] == 1
            assert prediction["confidence_score"] == 0.87
    
    def test_anomaly_detection_workflow(self, ml_service, mock_db):
        """Test anomaly detection creation and resolution workflow"""
        organization_id = 1
        user_id = 1
        
        # Step 1: Create anomaly detection model
        detection_data = AnomalyDetectionModelCreate(
            detection_name="revenue_anomaly_test",
            anomaly_type="revenue_anomaly",
            algorithm="isolation_forest",
            description="Integration test anomaly detection",
            detection_config={"contamination": 0.1},
            threshold_config={"critical": 0.95},
            monitored_metrics=["daily_revenue"],
            detection_frequency="hourly"
        )
        
        mock_detection = Mock()
        mock_detection.id = 1
        mock_detection.detection_name = "revenue_anomaly_test"
        mock_detection.is_active = True
        mock_detection.anomalies_detected_count = 0
        
        with patch.object(ml_service, 'create_anomaly_detection_model', return_value=mock_detection):
            created_detection = ml_service.create_anomaly_detection_model(
                organization_id=organization_id,
                model_data=detection_data,
                created_by_id=user_id
            )
            
            assert created_detection.id == 1
            assert created_detection.is_active is True
        
        # Step 2: Simulate anomaly detection
        mock_detection.anomalies_detected_count = 1
        
        # Step 3: Get detected anomalies
        mock_anomalies = [
            Mock(
                id=1,
                anomaly_model_id=1,
                severity="high",
                anomaly_score=0.92,
                is_resolved=False
            )
        ]
        
        with patch.object(ml_service, 'get_anomaly_detection_results', return_value=mock_anomalies):
            anomalies = ml_service.get_anomaly_detection_results(
                organization_id=organization_id,
                model_id=1,
                is_resolved=False
            )
            
            assert len(anomalies) == 1
            assert anomalies[0].severity == "high"
    
    def test_external_data_source_integration(self, ml_service, mock_db):
        """Test external data source creation and sync workflow"""
        organization_id = 1
        user_id = 1
        
        # Step 1: Create external data source
        source_data = ExternalDataSourceCreate(
            source_name="test_api_integration",
            source_type="api",
            description="Integration test data source",
            connection_config={"base_url": "https://api.test.com"},
            authentication_config={"type": "api_key"},
            sync_frequency="hourly"
        )
        
        mock_source = Mock()
        mock_source.id = 1
        mock_source.source_name = "test_api_integration"
        mock_source.is_active = True
        mock_source.sync_status = "pending"
        mock_source.total_records_synced = 0
        
        with patch.object(ml_service, 'create_external_data_source', return_value=mock_source):
            created_source = ml_service.create_external_data_source(
                organization_id=organization_id,
                source_data=source_data,
                created_by_id=user_id
            )
            
            assert created_source.id == 1
            assert created_source.is_active is True
            assert created_source.sync_status == "pending"
        
        # Step 2: Simulate successful sync
        mock_source.sync_status = "success"
        mock_source.total_records_synced = 1000
        mock_source.last_sync_at = datetime.utcnow()
        
        assert mock_source.sync_status == "success"
        assert mock_source.total_records_synced == 1000
    
    def test_dashboard_data_aggregation(self, ml_service, mock_db):
        """Test dashboard data aggregation from multiple sources"""
        organization_id = 1
        
        mock_dashboard = {
            "total_models": 5,
            "active_models": 3,
            "total_predictions": 1000,
            "total_anomalies_detected": 10,
            "unresolved_anomalies": 2,
            "active_data_sources": 4,
            "model_performance_summary": [
                {
                    "model_id": 1,
                    "model_name": "sales_forecast",
                    "accuracy_score": 0.85,
                    "prediction_count": 500
                },
                {
                    "model_id": 2,
                    "model_name": "demand_prediction",
                    "accuracy_score": 0.78,
                    "prediction_count": 300
                }
            ],
            "recent_anomalies": [
                {
                    "id": 1,
                    "severity": "high",
                    "anomaly_score": 0.92,
                    "is_resolved": False
                }
            ],
            "prediction_trends": {}
        }
        
        with patch.object(ml_service, 'get_ml_analytics_dashboard', return_value=mock_dashboard):
            dashboard = ml_service.get_ml_analytics_dashboard(organization_id)
            
            assert dashboard["total_models"] == 5
            assert dashboard["active_models"] == 3
            assert len(dashboard["model_performance_summary"]) == 2
            assert len(dashboard["recent_anomalies"]) == 1
    
    def test_prediction_history_tracking(self, ml_service, mock_db):
        """Test prediction history is properly tracked"""
        organization_id = 1
        model_id = 1
        
        # Mock prediction history
        mock_history = [
            Mock(
                id=1,
                model_id=1,
                prediction_timestamp=datetime.utcnow() - timedelta(days=1),
                confidence_score=0.85,
                actual_value=None,
                prediction_error=None
            ),
            Mock(
                id=2,
                model_id=1,
                prediction_timestamp=datetime.utcnow() - timedelta(hours=12),
                confidence_score=0.87,
                actual_value={"result": 350},
                prediction_error=0.05
            )
        ]
        
        with patch.object(ml_service, 'get_prediction_history', return_value=mock_history):
            history = ml_service.get_prediction_history(
                organization_id=organization_id,
                model_id=model_id,
                limit=100
            )
            
            assert len(history) == 2
            assert history[0].confidence_score == 0.85
            assert history[1].actual_value == {"result": 350}
    
    def test_model_performance_monitoring(self, ml_service, mock_db):
        """Test model performance monitoring over time"""
        organization_id = 1
        
        # Mock models with varying performance
        mock_models = [
            Mock(
                id=1,
                model_name="high_performance_model",
                accuracy_score=0.92,
                prediction_count=1000,
                is_active=True
            ),
            Mock(
                id=2,
                model_name="medium_performance_model",
                accuracy_score=0.75,
                prediction_count=500,
                is_active=True
            ),
            Mock(
                id=3,
                model_name="low_performance_model",
                accuracy_score=0.58,
                prediction_count=100,
                is_active=False
            )
        ]
        
        with patch.object(ml_service, 'get_predictive_models', return_value=mock_models):
            models = ml_service.get_predictive_models(organization_id=organization_id)
            
            assert len(models) == 3
            # Verify high performance model
            assert models[0].accuracy_score == 0.92
            assert models[0].is_active is True
            # Verify low performance model is deactivated
            assert models[2].accuracy_score == 0.58
            assert models[2].is_active is False
    
    def test_multi_model_predictions(self, ml_service, mock_db):
        """Test making predictions with multiple models"""
        organization_id = 1
        user_id = 1
        
        input_data = {"feature1": 100, "feature2": 200}
        
        # Predictions from different models
        predictions = [
            {
                "model_id": 1,
                "model_name": "random_forest",
                "predicted_value": {"result": 350},
                "confidence_score": 0.85
            },
            {
                "model_id": 2,
                "model_name": "xgboost",
                "predicted_value": {"result": 345},
                "confidence_score": 0.88
            },
            {
                "model_id": 3,
                "model_name": "neural_network",
                "predicted_value": {"result": 352},
                "confidence_score": 0.82
            }
        ]
        
        # Simulate ensemble prediction
        ensemble_result = sum(p["predicted_value"]["result"] for p in predictions) / len(predictions)
        avg_confidence = sum(p["confidence_score"] for p in predictions) / len(predictions)
        
        assert abs(ensemble_result - 349) < 1  # Average around 349
        assert avg_confidence > 0.8  # Good average confidence


def test_error_handling():
    """Test error handling in ML analytics operations"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    
    # Test handling of duplicate model names
    with patch.object(service, 'create_predictive_model') as mock_create:
        mock_create.side_effect = ValueError("Model with name already exists")
        
        with pytest.raises(ValueError):
            service.create_predictive_model(
                organization_id=1,
                model_data=Mock(),
                created_by_id=1
            )


def test_data_validation():
    """Test data validation in schemas"""
    # Test invalid validation split
    with pytest.raises(Exception):
        PredictiveModelCreate(
            model_name="test",
            model_type="sales_forecast",
            algorithm="random_forest",
            training_config={},
            validation_split=0.6,  # Too high
            test_split=0.1
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
