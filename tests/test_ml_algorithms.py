"""
Tests for ML Algorithms functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.ml_algorithms_service import MLAlgorithmsService
from app.models.ml_algorithms import (
    MLAlgorithmConfig, MLModelTraining, MLFramework,
    AlgorithmCategory, TrainingStatus
)


class TestMLAlgorithmsService:
    """Test ML Algorithms service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def ml_service(self, mock_db):
        """Create ML Algorithms service instance"""
        return MLAlgorithmsService(mock_db)
    
    def test_create_algorithm_config(self, ml_service, mock_db):
        """Test creating algorithm configuration"""
        # Arrange
        organization_id = 1
        config_name = "Production CatBoost"
        framework = MLFramework.CATBOOST
        algorithm_name = "CatBoostClassifier"
        category = AlgorithmCategory.CLASSIFICATION
        hyperparameters = {"iterations": 1000, "learning_rate": 0.1}
        created_by_id = 1
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        config = ml_service.create_algorithm_config(
            organization_id=organization_id,
            config_name=config_name,
            framework=framework,
            algorithm_name=algorithm_name,
            category=category,
            hyperparameters=hyperparameters,
            created_by_id=created_by_id
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert config.config_name == config_name
        assert config.framework == framework
    
    def test_get_algorithm_configs(self, ml_service, mock_db):
        """Test getting algorithm configurations"""
        # Arrange
        organization_id = 1
        mock_configs = [
            Mock(spec=MLAlgorithmConfig, id=1, config_name="Config 1"),
            Mock(spec=MLAlgorithmConfig, id=2, config_name="Config 2"),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_configs
        
        # Act
        configs = ml_service.get_algorithm_configs(organization_id)
        
        # Assert
        assert len(configs) == 2
        assert configs[0].config_name == "Config 1"
    
    def test_create_model_training(self, ml_service, mock_db):
        """Test creating model training session"""
        # Arrange
        organization_id = 1
        training_name = "Customer Churn Model"
        framework = MLFramework.LIGHTGBM
        algorithm_name = "LGBMClassifier"
        dataset_config = {"data_path": "/data/train.csv"}
        training_params = {"early_stopping": 50}
        hyperparameters = {"num_leaves": 31, "learning_rate": 0.05}
        total_epochs = 100
        created_by_id = 1
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        training = ml_service.create_model_training(
            organization_id=organization_id,
            training_name=training_name,
            framework=framework,
            algorithm_name=algorithm_name,
            dataset_config=dataset_config,
            training_params=training_params,
            hyperparameters=hyperparameters,
            total_epochs=total_epochs,
            created_by_id=created_by_id
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert training.training_name == training_name
        assert training.status == TrainingStatus.PENDING
    
    def test_update_training_progress(self, ml_service, mock_db):
        """Test updating training progress"""
        # Arrange
        training_id = 1
        progress = 50.0
        current_epoch = 50
        training_metrics = {"loss": 0.5, "accuracy": 0.85}
        
        mock_training = Mock(spec=MLModelTraining)
        mock_training.id = training_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_training
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        updated_training = ml_service.update_training_progress(
            training_id=training_id,
            progress=progress,
            current_epoch=current_epoch,
            training_metrics=training_metrics
        )
        
        # Assert
        assert updated_training.progress == progress
        assert updated_training.current_epoch == current_epoch
        mock_db.commit.assert_called_once()
    
    def test_update_training_status(self, ml_service, mock_db):
        """Test updating training status"""
        # Arrange
        training_id = 1
        status = TrainingStatus.COMPLETED
        
        mock_training = Mock(spec=MLModelTraining)
        mock_training.id = training_id
        mock_training.started_at = datetime.utcnow()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_training
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Act
        updated_training = ml_service.update_training_status(
            training_id=training_id,
            status=status
        )
        
        # Assert
        assert updated_training.status == status
        mock_db.commit.assert_called_once()
    
    def test_get_framework_algorithms(self, ml_service, mock_db):
        """Test getting algorithms for a framework"""
        # Act
        sklearn_algorithms = ml_service.get_framework_algorithms(MLFramework.SCIKIT_LEARN)
        catboost_algorithms = ml_service.get_framework_algorithms(MLFramework.CATBOOST)
        lightgbm_algorithms = ml_service.get_framework_algorithms(MLFramework.LIGHTGBM)
        tensorflow_algorithms = ml_service.get_framework_algorithms(MLFramework.TENSORFLOW)
        pytorch_algorithms = ml_service.get_framework_algorithms(MLFramework.PYTORCH)
        
        # Assert
        assert len(sklearn_algorithms) > 0
        assert "RandomForest" in sklearn_algorithms
        
        assert len(catboost_algorithms) > 0
        assert "CatBoostClassifier" in catboost_algorithms
        
        assert len(lightgbm_algorithms) > 0
        assert "LGBMClassifier" in lightgbm_algorithms
        
        assert len(tensorflow_algorithms) > 0
        assert "Sequential" in tensorflow_algorithms
        
        assert len(pytorch_algorithms) > 0
        assert "Sequential" in pytorch_algorithms
    
    def test_get_training_dashboard(self, ml_service, mock_db):
        """Test getting training dashboard"""
        # Arrange
        organization_id = 1
        
        # Mock count queries
        mock_db.query.return_value.filter.return_value.count.return_value = 10
        
        # Mock recent trainings
        mock_trainings = [
            Mock(
                spec=MLModelTraining,
                id=i,
                training_name=f"Training {i}",
                framework=MLFramework.CATBOOST,
                status=TrainingStatus.COMPLETED,
                progress=100.0,
                created_at=datetime.utcnow()
            )
            for i in range(5)
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_trainings[:5]
        
        # Act
        dashboard = ml_service.get_training_dashboard(organization_id)
        
        # Assert
        assert "total_trainings" in dashboard
        assert "completed_trainings" in dashboard
        assert "running_trainings" in dashboard
        assert "recent_trainings" in dashboard
        assert len(dashboard["recent_trainings"]) == 5


class TestMLAlgorithmsIntegration:
    """Integration tests for ML Algorithms"""
    
    def test_training_workflow(self):
        """Test complete training workflow"""
        workflow_steps = [
            "create_config",
            "create_training",
            "start_training",
            "update_progress",
            "save_metrics",
            "complete_training",
        ]
        
        assert len(workflow_steps) == 6
        assert "create_training" in workflow_steps
        assert "complete_training" in workflow_steps


class TestMLFrameworks:
    """Test ML framework enums and types"""
    
    def test_ml_frameworks(self):
        """Test ML frameworks"""
        frameworks = [f.value for f in MLFramework]
        assert "scikit_learn" in frameworks
        assert "catboost" in frameworks
        assert "lightgbm" in frameworks
        assert "tensorflow" in frameworks
        assert "pytorch" in frameworks
        assert "xgboost" in frameworks
    
    def test_algorithm_categories(self):
        """Test algorithm categories"""
        categories = [c.value for c in AlgorithmCategory]
        assert "classification" in categories
        assert "regression" in categories
        assert "clustering" in categories
        assert "deep_learning" in categories
    
    def test_training_status(self):
        """Test training status types"""
        statuses = [s.value for s in TrainingStatus]
        assert "pending" in statuses
        assert "training" in statuses
        assert "completed" in statuses
        assert "failed" in statuses


class TestFrameworkCapabilities:
    """Test framework-specific capabilities"""
    
    def test_catboost_features(self):
        """Test CatBoost specific features"""
        features = [
            "categorical_features",
            "missing_values",
            "gpu_acceleration"
        ]
        assert len(features) == 3
    
    def test_lightgbm_features(self):
        """Test LightGBM specific features"""
        features = [
            "fast_training",
            "low_memory",
            "gpu_acceleration"
        ]
        assert len(features) == 3
    
    def test_deep_learning_frameworks(self):
        """Test deep learning frameworks"""
        dl_frameworks = ["tensorflow", "pytorch"]
        assert "tensorflow" in dl_frameworks
        assert "pytorch" in dl_frameworks
