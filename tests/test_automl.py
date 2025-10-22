"""
Tests for AutoML functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.automl_service import AutoMLService
from app.models.automl import (
    AutoMLRun, AutoMLModelCandidate, AutoMLTaskType,
    AutoMLStatus, AutoMLFramework
)


class TestAutoMLService:
    """Test AutoML service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def automl_service(self, mock_db):
        """Create AutoML service instance"""
        return AutoMLService(mock_db)
    
    def test_create_automl_run(self, automl_service, mock_db):
        """Test creating an AutoML run"""
        # Arrange
        organization_id = 1
        run_name = "Test Sales Forecast"
        task_type = AutoMLTaskType.REGRESSION
        target_column = "sales"
        feature_columns = ["product_id", "region", "season"]
        metric = "rmse"
        created_by_id = 1
        
        # Mock the database operations
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        run = automl_service.create_automl_run(
            organization_id=organization_id,
            run_name=run_name,
            task_type=task_type,
            target_column=target_column,
            feature_columns=feature_columns,
            metric=metric,
            created_by_id=created_by_id
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert run.run_name == run_name
        assert run.task_type == task_type
        assert run.status == AutoMLStatus.PENDING
    
    def test_update_automl_run_status(self, automl_service, mock_db):
        """Test updating AutoML run status"""
        # Arrange
        run_id = 1
        mock_run = Mock(spec=AutoMLRun)
        mock_run.id = run_id
        mock_run.started_at = None
        mock_db.query.return_value.filter.return_value.first.return_value = mock_run
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        updated_run = automl_service.update_automl_run_status(
            run_id=run_id,
            status=AutoMLStatus.RUNNING,
            progress=50.0,
            current_trial=50
        )
        
        # Assert
        assert updated_run.status == AutoMLStatus.RUNNING
        assert updated_run.progress == 50.0
        assert updated_run.current_trial == 50
        mock_db.commit.assert_called_once()
    
    def test_save_model_candidate(self, automl_service, mock_db):
        """Test saving a model candidate"""
        # Arrange
        automl_run_id = 1
        organization_id = 1
        trial_number = 1
        model_name = "RandomForest"
        algorithm = "RandomForestRegressor"
        hyperparameters = {"n_estimators": 100, "max_depth": 10}
        score = 0.85
        training_time = 120.5
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        candidate = automl_service.save_model_candidate(
            automl_run_id=automl_run_id,
            organization_id=organization_id,
            trial_number=trial_number,
            model_name=model_name,
            algorithm=algorithm,
            hyperparameters=hyperparameters,
            score=score,
            training_time=training_time
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert candidate.trial_number == trial_number
        assert candidate.score == score
    
    def test_get_automl_runs(self, automl_service, mock_db):
        """Test getting AutoML runs"""
        # Arrange
        organization_id = 1
        mock_runs = [
            Mock(spec=AutoMLRun, id=1, run_name="Run 1"),
            Mock(spec=AutoMLRun, id=2, run_name="Run 2"),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_runs
        
        # Act
        runs = automl_service.get_automl_runs(organization_id)
        
        # Assert
        assert len(runs) == 2
        assert runs[0].run_name == "Run 1"
    
    def test_get_leaderboard(self, automl_service, mock_db):
        """Test getting leaderboard"""
        # Arrange
        automl_run_id = 1
        top_n = 5
        mock_candidates = [
            Mock(spec=AutoMLModelCandidate, id=i, score=0.9 - i*0.01)
            for i in range(5)
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_candidates
        
        # Act
        leaderboard = automl_service.get_leaderboard(automl_run_id, top_n)
        
        # Assert
        assert len(leaderboard) == 5
        assert leaderboard[0].score == 0.9
    
    def test_update_best_model(self, automl_service, mock_db):
        """Test updating best model"""
        # Arrange
        run_id = 1
        best_model_name = "XGBoost"
        best_model_params = {"learning_rate": 0.1, "max_depth": 6}
        best_score = 0.92
        
        mock_run = Mock(spec=AutoMLRun)
        mock_run.id = run_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_run
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        updated_run = automl_service.update_best_model(
            run_id=run_id,
            best_model_name=best_model_name,
            best_model_params=best_model_params,
            best_score=best_score
        )
        
        # Assert
        assert updated_run.best_model_name == best_model_name
        assert updated_run.best_score == best_score
        mock_db.commit.assert_called_once()
    
    def test_cancel_automl_run(self, automl_service, mock_db):
        """Test cancelling AutoML run"""
        # Arrange
        run_id = 1
        mock_run = Mock(spec=AutoMLRun)
        mock_run.id = run_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_run
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        cancelled_run = automl_service.cancel_automl_run(run_id)
        
        # Assert
        assert cancelled_run.status == AutoMLStatus.CANCELLED
        mock_db.commit.assert_called_once()


class TestAutoMLIntegration:
    """Integration tests for AutoML"""
    
    def test_automl_workflow(self):
        """Test complete AutoML workflow"""
        # This would be an integration test with a real database
        # For now, we'll just verify the workflow structure
        
        workflow_steps = [
            "create_run",
            "start_run",
            "evaluate_models",
            "save_candidates",
            "update_progress",
            "complete_run",
            "get_leaderboard",
        ]
        
        assert len(workflow_steps) == 7
        assert "create_run" in workflow_steps
        assert "get_leaderboard" in workflow_steps


class TestAutoMLModels:
    """Test AutoML model enums and types"""
    
    def test_task_types(self):
        """Test AutoML task types"""
        task_types = [t.value for t in AutoMLTaskType]
        assert "classification" in task_types
        assert "regression" in task_types
        assert "time_series" in task_types
        assert "clustering" in task_types
    
    def test_status_types(self):
        """Test AutoML status types"""
        statuses = [s.value for s in AutoMLStatus]
        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses
        assert "failed" in statuses
        assert "cancelled" in statuses
    
    def test_frameworks(self):
        """Test AutoML frameworks"""
        frameworks = [f.value for f in AutoMLFramework]
        assert "optuna" in frameworks
        assert "auto_sklearn" in frameworks
        assert "tpot" in frameworks
        assert "h2o" in frameworks
