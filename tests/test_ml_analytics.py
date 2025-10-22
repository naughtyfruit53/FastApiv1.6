"""
Test ML Analytics functionality
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
    PredictiveModelCreate, PredictiveModelUpdate,
    AnomalyDetectionModelCreate, AnomalyDetectionModelUpdate,
    ExternalDataSourceCreate, PredictionRequest,
    AnomalyResolutionRequest, AdvancedAnalyticsRequest
)
from app.models.ml_analytics import (
    PredictiveModelType, AnomalyType, DataSourceType
)


def test_ml_analytics_service_creation():
    """Test that ML Analytics service can be created"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    assert service.db == mock_db


def test_predictive_model_create_schema():
    """Test predictive model creation schema validation"""
    model_data = PredictiveModelCreate(
        model_name="test_sales_forecast",
        model_type="sales_forecast",
        algorithm="random_forest",
        description="Test sales forecasting model",
        hyperparameters={"n_estimators": 100, "max_depth": 10},
        feature_engineering={"normalize": True},
        training_config={"epochs": 100, "batch_size": 32},
        validation_split=0.2,
        test_split=0.1
    )
    
    assert model_data.model_name == "test_sales_forecast"
    assert model_data.model_type == "sales_forecast"
    assert model_data.algorithm == "random_forest"
    assert model_data.hyperparameters["n_estimators"] == 100
    assert model_data.validation_split == 0.2


def test_predictive_model_update_schema():
    """Test predictive model update schema"""
    update_data = PredictiveModelUpdate(
        model_name="updated_model_name",
        description="Updated description",
        is_active=True
    )
    
    assert update_data.model_name == "updated_model_name"
    assert update_data.is_active is True


def test_anomaly_detection_model_create_schema():
    """Test anomaly detection model creation schema"""
    model_data = AnomalyDetectionModelCreate(
        detection_name="revenue_anomaly_detection",
        anomaly_type="revenue_anomaly",
        algorithm="isolation_forest",
        description="Detect revenue anomalies",
        detection_config={"contamination": 0.1},
        threshold_config={"critical": 0.95, "high": 0.85},
        monitored_metrics=["daily_revenue", "transaction_count"],
        detection_frequency="hourly"
    )
    
    assert model_data.detection_name == "revenue_anomaly_detection"
    assert model_data.anomaly_type == "revenue_anomaly"
    assert model_data.algorithm == "isolation_forest"
    assert len(model_data.monitored_metrics) == 2


def test_external_data_source_create_schema():
    """Test external data source creation schema"""
    source_data = ExternalDataSourceCreate(
        source_name="google_analytics",
        source_type="api",
        description="Google Analytics integration",
        connection_config={"base_url": "https://analytics.google.com"},
        authentication_config={"type": "oauth2"},
        sync_frequency="hourly"
    )
    
    assert source_data.source_name == "google_analytics"
    assert source_data.source_type == "api"
    assert source_data.sync_frequency == "hourly"


def test_prediction_request_schema():
    """Test prediction request schema"""
    request = PredictionRequest(
        model_id=1,
        input_data={
            "historical_sales": 150000,
            "marketing_spend": 25000,
            "season": "Q4"
        },
        context_metadata={"source": "dashboard"}
    )
    
    assert request.model_id == 1
    assert request.input_data["historical_sales"] == 150000
    assert request.context_metadata["source"] == "dashboard"


def test_anomaly_resolution_request_schema():
    """Test anomaly resolution request schema"""
    resolution = AnomalyResolutionRequest(
        resolution_notes="Investigated and resolved",
        is_false_positive=False
    )
    
    assert resolution.resolution_notes == "Investigated and resolved"
    assert resolution.is_false_positive is False


def test_advanced_analytics_request_schema():
    """Test advanced analytics request schema"""
    request = AdvancedAnalyticsRequest(
        analysis_type="trend",
        data_source="sales_data",
        parameters={"metric": "revenue", "period": "monthly"},
        date_range={"start": "2024-01-01", "end": "2024-12-31"}
    )
    
    assert request.analysis_type == "trend"
    assert request.data_source == "sales_data"
    assert request.parameters["metric"] == "revenue"


@patch('app.services.ml_analytics_service.MLAnalyticsService.create_predictive_model')
def test_create_predictive_model_mock(mock_create):
    """Test creating a predictive model with mock"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    
    model_data = PredictiveModelCreate(
        model_name="test_model",
        model_type="sales_forecast",
        algorithm="random_forest",
        training_config={"epochs": 100},
        validation_split=0.2,
        test_split=0.1
    )
    
    mock_model = Mock()
    mock_model.id = 1
    mock_model.model_name = "test_model"
    mock_create.return_value = mock_model
    
    result = service.create_predictive_model(
        organization_id=1,
        model_data=model_data,
        created_by_id=1
    )
    
    assert result.id == 1
    assert result.model_name == "test_model"


@patch('app.services.ml_analytics_service.MLAnalyticsService.get_ml_analytics_dashboard')
def test_get_dashboard_mock(mock_get_dashboard):
    """Test getting ML analytics dashboard with mock"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    
    mock_dashboard = {
        "total_models": 5,
        "active_models": 3,
        "total_predictions": 1000,
        "total_anomalies_detected": 10,
        "unresolved_anomalies": 2,
        "active_data_sources": 4,
        "model_performance_summary": [],
        "recent_anomalies": [],
        "prediction_trends": {}
    }
    
    mock_get_dashboard.return_value = mock_dashboard
    
    result = service.get_ml_analytics_dashboard(organization_id=1)
    
    assert result["total_models"] == 5
    assert result["active_models"] == 3
    assert result["total_predictions"] == 1000
    assert result["unresolved_anomalies"] == 2


@patch('app.services.ml_analytics_service.MLAnalyticsService.make_prediction')
def test_make_prediction_mock(mock_make_prediction):
    """Test making a prediction with mock"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    
    prediction_request = PredictionRequest(
        model_id=1,
        input_data={"feature1": 100, "feature2": 200}
    )
    
    mock_result = {
        "prediction_id": 123,
        "model_id": 1,
        "predicted_value": {"result": 350},
        "confidence_score": 0.87,
        "prediction_timestamp": datetime.utcnow()
    }
    
    mock_make_prediction.return_value = mock_result
    
    result = service.make_prediction(
        organization_id=1,
        prediction_request=prediction_request,
        user_id=1
    )
    
    assert result["prediction_id"] == 123
    assert result["model_id"] == 1
    assert result["confidence_score"] == 0.87


def test_model_type_enums():
    """Test predictive model type enumerations"""
    assert PredictiveModelType.SALES_FORECAST.value == "sales_forecast"
    assert PredictiveModelType.DEMAND_PREDICTION.value == "demand_prediction"
    assert PredictiveModelType.CHURN_PREDICTION.value == "churn_prediction"
    assert PredictiveModelType.REVENUE_FORECAST.value == "revenue_forecast"


def test_anomaly_type_enums():
    """Test anomaly type enumerations"""
    assert AnomalyType.REVENUE_ANOMALY.value == "revenue_anomaly"
    assert AnomalyType.INVENTORY_ANOMALY.value == "inventory_anomaly"
    assert AnomalyType.TRANSACTION_ANOMALY.value == "transaction_anomaly"


def test_data_source_type_enums():
    """Test data source type enumerations"""
    assert DataSourceType.DATABASE.value == "database"
    assert DataSourceType.API.value == "api"
    assert DataSourceType.FILE_UPLOAD.value == "file_upload"
    assert DataSourceType.CLOUD_STORAGE.value == "cloud_storage"
    assert DataSourceType.STREAMING.value == "streaming"


@patch('app.services.ml_analytics_service.MLAnalyticsService.resolve_anomaly')
def test_resolve_anomaly_mock(mock_resolve):
    """Test resolving an anomaly with mock"""
    mock_db = Mock()
    service = MLAnalyticsService(mock_db)
    
    resolution_data = AnomalyResolutionRequest(
        resolution_notes="Investigated and resolved",
        is_false_positive=False
    )
    
    mock_anomaly = Mock()
    mock_anomaly.id = 1
    mock_anomaly.is_resolved = True
    mock_resolve.return_value = mock_anomaly
    
    result = service.resolve_anomaly(
        organization_id=1,
        anomaly_id=1,
        resolution_data=resolution_data,
        resolved_by_id=1
    )
    
    assert result.id == 1
    assert result.is_resolved is True


def test_validation_splits():
    """Test validation and test split constraints"""
    # Valid splits
    model_data = PredictiveModelCreate(
        model_name="test_model",
        model_type="sales_forecast",
        algorithm="random_forest",
        training_config={},
        validation_split=0.2,
        test_split=0.1
    )
    assert model_data.validation_split == 0.2
    assert model_data.test_split == 0.1


def test_hyperparameters_flexibility():
    """Test that hyperparameters can be flexible dictionaries"""
    model_data = PredictiveModelCreate(
        model_name="test_model",
        model_type="sales_forecast",
        algorithm="xgboost",
        training_config={},
        hyperparameters={
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "custom_param": "custom_value"
        }
    )
    
    assert len(model_data.hyperparameters) == 6
    assert model_data.hyperparameters["learning_rate"] == 0.01
    assert model_data.hyperparameters["custom_param"] == "custom_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
