"""
Test AI Analytics functionality
"""

import os
import sys
import pytest
from unittest.mock import Mock

# Set dummy DATABASE_URL to avoid connection requirement during testing
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'

from app.services.ai_analytics_service import AIAnalyticsService
from app.schemas.ai_analytics import AIModelCreate, PredictionRequest
from app.models.ai_analytics_models import ModelStatus, PredictionType


def test_ai_analytics_service_creation():
    """Test that AI Analytics service can be created"""
    mock_db = Mock()
    service = AIAnalyticsService(mock_db)
    assert service.db == mock_db


def test_ai_model_create_schema():
    """Test AI model creation schema validation"""
    model_data = AIModelCreate(
        model_name="test_sales_forecast",
        model_type="forecasting",
        algorithm="linear_regression",
        feature_columns=["revenue", "orders", "customers"],
        target_column="next_month_revenue",
        description="Sales forecasting model for next month revenue prediction"
    )
    
    assert model_data.model_name == "test_sales_forecast"
    assert model_data.model_type == "forecasting"
    assert model_data.algorithm == "linear_regression"
    assert len(model_data.feature_columns) == 3
    assert model_data.target_column == "next_month_revenue"


def test_prediction_request_schema():
    """Test prediction request schema validation"""
    prediction_request = PredictionRequest(
        model_id=1,
        input_data={
            "revenue": 100000.0,
            "orders": 150,
            "customers": 75
        },
        prediction_context="monthly_forecast",
        business_entity_type="organization",
        business_entity_id=1
    )
    
    assert prediction_request.model_id == 1
    assert prediction_request.input_data["revenue"] == 100000.0
    assert prediction_request.prediction_context == "monthly_forecast"


def test_ai_analytics_dashboard_data_structure():
    """Test AI analytics dashboard data structure"""
    mock_db = Mock()
    service = AIAnalyticsService(mock_db)
    
    # Mock database queries
    mock_db.query.return_value.filter.return_value.count.return_value = 5
    mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.scalar.return_value = 0.85
    
    dashboard_data = service.get_ai_analytics_dashboard(1)
    
    expected_keys = [
        "total_models", "active_models", "models_in_training",
        "total_predictions_today", "total_predictions_week", "total_predictions_month",
        "average_model_accuracy", "active_anomalies", "critical_anomalies",
        "active_insights", "high_priority_insights", "automation_workflows",
        "active_automations", "generated_at"
    ]
    
    for key in expected_keys:
        assert key in dashboard_data


def test_model_status_enum():
    """Test model status enumeration values"""
    assert ModelStatus.DRAFT.value == "draft"
    assert ModelStatus.TRAINING.value == "training"
    assert ModelStatus.TRAINED.value == "trained"
    assert ModelStatus.DEPLOYED.value == "deployed"
    assert ModelStatus.DEPRECATED.value == "deprecated"
    assert ModelStatus.FAILED.value == "failed"


def test_prediction_type_enum():
    """Test prediction type enumeration values"""
    assert PredictionType.CLASSIFICATION.value == "classification"
    assert PredictionType.REGRESSION.value == "regression"
    assert PredictionType.FORECASTING.value == "forecasting"
    assert PredictionType.ANOMALY_DETECTION.value == "anomaly_detection"
    assert PredictionType.CLUSTERING.value == "clustering"
    assert PredictionType.RECOMMENDATION.value == "recommendation"


if __name__ == "__main__":
    # Run basic tests
    test_ai_analytics_service_creation()
    test_ai_model_create_schema()
    test_prediction_request_schema()
    test_model_status_enum()
    test_prediction_type_enum()
    print("✓ All AI Analytics tests passed!")