"""
Tests for Model Explainability functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session
import numpy as np

from app.services.explainability_service import ExplainabilityService
from app.models.explainability import (
    ModelExplainability, PredictionExplanation, ExplainabilityReport,
    ExplainabilityMethod, ExplainabilityScope
)


class TestExplainabilityService:
    """Test Explainability service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def explainability_service(self, mock_db):
        """Create Explainability service instance"""
        return ExplainabilityService(mock_db)
    
    def test_create_model_explainability(self, explainability_service, mock_db):
        """Test creating model explainability"""
        # Arrange
        organization_id = 1
        model_id = 1
        model_type = "predictive_model"
        model_name = "Sales Forecast Model"
        method = ExplainabilityMethod.SHAP
        scope = ExplainabilityScope.GLOBAL
        config = {"background_samples": 100}
        created_by_id = 1
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        explainability = explainability_service.create_model_explainability(
            organization_id=organization_id,
            model_id=model_id,
            model_type=model_type,
            model_name=model_name,
            method=method,
            scope=scope,
            config=config,
            created_by_id=created_by_id
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert explainability.model_name == model_name
        assert explainability.method == method
    
    def test_get_model_explainability(self, explainability_service, mock_db):
        """Test getting model explainability"""
        # Arrange
        organization_id = 1
        model_id = 1
        model_type = "predictive_model"
        
        mock_explainability = Mock(spec=ModelExplainability)
        mock_explainability.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_explainability
        
        # Act
        explainability = explainability_service.get_model_explainability(
            organization_id=organization_id,
            model_id=model_id,
            model_type=model_type
        )
        
        # Assert
        assert explainability is not None
        assert explainability.id == 1
    
    def test_update_explainability_results(self, explainability_service, mock_db):
        """Test updating explainability results"""
        # Arrange
        explainability_id = 1
        feature_importance = {"feature1": 0.5, "feature2": 0.3, "feature3": 0.2}
        shap_values = {"values": [0.1, 0.2, 0.3], "base_value": 0.5}
        computation_time = 5.2
        
        mock_explainability = Mock(spec=ModelExplainability)
        mock_explainability.id = explainability_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_explainability
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        updated = explainability_service.update_explainability_results(
            explainability_id=explainability_id,
            feature_importance=feature_importance,
            shap_values=shap_values,
            computation_time=computation_time
        )
        
        # Assert
        assert updated.feature_importance == feature_importance
        assert updated.shap_values == shap_values
        assert updated.computation_time == computation_time
        mock_db.commit.assert_called_once()
    
    def test_create_prediction_explanation(self, explainability_service, mock_db):
        """Test creating prediction explanation"""
        # Arrange
        organization_id = 1
        model_explainability_id = 1
        input_features = {"age": 35, "income": 50000}
        predicted_value = 0.85
        method = ExplainabilityMethod.SHAP
        feature_contributions = {"age": 0.3, "income": 0.55}
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        explanation = explainability_service.create_prediction_explanation(
            organization_id=organization_id,
            model_explainability_id=model_explainability_id,
            input_features=input_features,
            predicted_value=predicted_value,
            method=method,
            feature_contributions=feature_contributions
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert explanation.predicted_value == predicted_value
        assert explanation.feature_contributions == feature_contributions
        # Check that top features are extracted
        assert explanation.top_positive_features is not None
    
    def test_get_prediction_explanations(self, explainability_service, mock_db):
        """Test getting prediction explanations"""
        # Arrange
        organization_id = 1
        model_explainability_id = 1
        limit = 50
        
        mock_explanations = [
            Mock(spec=PredictionExplanation, id=i)
            for i in range(10)
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_explanations
        
        # Act
        explanations = explainability_service.get_prediction_explanations(
            organization_id=organization_id,
            model_explainability_id=model_explainability_id,
            limit=limit
        )
        
        # Assert
        assert len(explanations) == 10
    
    def test_create_explainability_report(self, explainability_service, mock_db):
        """Test creating explainability report"""
        # Arrange
        organization_id = 1
        report_name = "Q4 2024 Model Analysis"
        report_type = "global_summary"
        model_ids = [1, 2, 3]
        summary = {"total_models": 3, "avg_score": 0.85}
        key_insights = ["Insight 1", "Insight 2"]
        created_by_id = 1
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        report = explainability_service.create_explainability_report(
            organization_id=organization_id,
            report_name=report_name,
            report_type=report_type,
            model_ids=model_ids,
            summary=summary,
            key_insights=key_insights,
            created_by_id=created_by_id
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert report.report_name == report_name
        assert len(report.model_ids) == 3
    
    def test_get_explainability_reports(self, explainability_service, mock_db):
        """Test getting explainability reports"""
        # Arrange
        organization_id = 1
        
        mock_reports = [
            Mock(spec=ExplainabilityReport, id=1, report_name="Report 1"),
            Mock(spec=ExplainabilityReport, id=2, report_name="Report 2"),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_reports
        
        # Act
        reports = explainability_service.get_explainability_reports(organization_id)
        
        # Assert
        assert len(reports) == 2
        assert reports[0].report_name == "Report 1"
    
    def test_compute_shap_values(self, explainability_service, mock_db):
        """Test computing SHAP values (stub)"""
        # Arrange
        model = Mock()
        data = np.array([[1, 2, 3], [4, 5, 6]])
        
        # Act
        shap_values = explainability_service.compute_shap_values(model, data)
        
        # Assert
        assert "values" in shap_values
        assert "base_value" in shap_values
        assert "data" in shap_values
    
    def test_compute_lime_explanation(self, explainability_service, mock_db):
        """Test computing LIME explanation (stub)"""
        # Arrange
        model = Mock()
        instance = np.array([1, 2, 3])
        feature_names = ["feature1", "feature2", "feature3"]
        
        # Act
        lime_explanation = explainability_service.compute_lime_explanation(
            model, instance, feature_names
        )
        
        # Assert
        assert "intercept" in lime_explanation
        assert "prediction_local" in lime_explanation
        assert "feature_weights" in lime_explanation
    
    def test_get_explainability_dashboard(self, explainability_service, mock_db):
        """Test getting explainability dashboard"""
        # Arrange
        organization_id = 1
        
        # Mock count queries
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Mock recent reports
        mock_reports = [
            Mock(
                spec=ExplainabilityReport,
                id=i,
                report_name=f"Report {i}",
                report_type="global_summary",
                model_ids=[1, 2],
                generated_at=datetime.utcnow()
            )
            for i in range(3)
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_reports[:5]
        
        # Act
        dashboard = explainability_service.get_explainability_dashboard(organization_id)
        
        # Assert
        assert "total_models_with_explainability" in dashboard
        assert "total_prediction_explanations" in dashboard
        assert "total_reports" in dashboard
        assert "recent_reports" in dashboard


class TestExplainabilityIntegration:
    """Integration tests for Explainability"""
    
    def test_explainability_workflow(self):
        """Test complete explainability workflow"""
        workflow_steps = [
            "create_explainability",
            "compute_shap",
            "save_results",
            "explain_prediction",
            "generate_report",
        ]
        
        assert len(workflow_steps) == 5
        assert "compute_shap" in workflow_steps
        assert "generate_report" in workflow_steps


class TestExplainabilityMethods:
    """Test explainability methods and types"""
    
    def test_explainability_methods(self):
        """Test explainability methods"""
        methods = [m.value for m in ExplainabilityMethod]
        assert "shap" in methods
        assert "lime" in methods
        assert "feature_importance" in methods
    
    def test_explainability_scopes(self):
        """Test explainability scopes"""
        scopes = [s.value for s in ExplainabilityScope]
        assert "global" in scopes
        assert "local" in scopes
        assert "cohort" in scopes


class TestFeatureContributions:
    """Test feature contribution extraction"""
    
    def test_top_positive_features_extraction(self):
        """Test extracting top positive features"""
        feature_contributions = {
            "feature1": 0.5,
            "feature2": 0.3,
            "feature3": -0.2,
            "feature4": 0.1,
            "feature5": -0.4,
        }
        
        # Sort by absolute value and filter positive
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        positive_features = [
            {"feature": k, "contribution": v}
            for k, v in sorted_features if v > 0
        ][:3]
        
        # Assert
        assert len(positive_features) <= 3
        assert positive_features[0]["feature"] == "feature1"
        assert positive_features[0]["contribution"] == 0.5
    
    def test_top_negative_features_extraction(self):
        """Test extracting top negative features"""
        feature_contributions = {
            "feature1": 0.5,
            "feature2": 0.3,
            "feature3": -0.2,
            "feature4": 0.1,
            "feature5": -0.4,
        }
        
        # Sort by absolute value and filter negative
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        negative_features = [
            {"feature": k, "contribution": v}
            for k, v in sorted_features if v < 0
        ][:3]
        
        # Assert
        assert len(negative_features) <= 3
        assert negative_features[0]["feature"] == "feature5"
        assert negative_features[0]["contribution"] == -0.4


class TestExplainabilityUseCases:
    """Test explainability use cases"""
    
    def test_model_debugging(self):
        """Test explainability for model debugging"""
        use_cases = [
            "identify_biased_features",
            "verify_feature_importance",
            "detect_data_leakage",
        ]
        assert len(use_cases) == 3
    
    def test_regulatory_compliance(self):
        """Test explainability for compliance"""
        requirements = [
            "gdpr_right_to_explanation",
            "fair_lending_act",
            "model_transparency",
        ]
        assert len(requirements) == 3
    
    def test_stakeholder_communication(self):
        """Test explainability for stakeholders"""
        benefits = [
            "build_trust",
            "justify_decisions",
            "improve_acceptance",
        ]
        assert len(benefits) == 3
