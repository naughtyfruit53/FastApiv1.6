"""
ML Algorithms Service for extended ML framework support
Supports CatBoost, LightGBM, TensorFlow, PyTorch
"""

import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.ml_algorithms import (
    MLAlgorithmConfig, MLModelTraining, MLFramework,
    AlgorithmCategory, TrainingStatus
)
from app.models.user_models import User, Organization

logger = logging.getLogger(__name__)


class MLAlgorithmsService:
    """Service for ML algorithms operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # ALGORITHM CONFIGURATION MANAGEMENT
    # ============================================================================
    
    def create_algorithm_config(
        self,
        organization_id: int,
        config_name: str,
        framework: MLFramework,
        algorithm_name: str,
        category: AlgorithmCategory,
        hyperparameters: Dict[str, Any],
        preprocessing_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        gpu_enabled: bool = False,
        created_by_id: int = None
    ) -> MLAlgorithmConfig:
        """Create a new ML algorithm configuration"""
        try:
            config = MLAlgorithmConfig(
                organization_id=organization_id,
                config_name=config_name,
                framework=framework,
                algorithm_name=algorithm_name,
                category=category,
                description=description,
                hyperparameters=hyperparameters,
                preprocessing_config=preprocessing_config or {},
                gpu_enabled=gpu_enabled,
                created_by_id=created_by_id
            )
            
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            
            logger.info(f"Created algorithm config '{config_name}' for organization {organization_id}")
            return config
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating algorithm config: {str(e)}")
            raise
    
    def get_algorithm_configs(
        self,
        organization_id: int,
        framework: Optional[MLFramework] = None,
        category: Optional[AlgorithmCategory] = None,
        is_active: bool = True
    ) -> List[MLAlgorithmConfig]:
        """Get algorithm configurations for an organization"""
        query = self.db.query(MLAlgorithmConfig).filter(
            MLAlgorithmConfig.organization_id == organization_id
        )
        
        if framework:
            query = query.filter(MLAlgorithmConfig.framework == framework)
        if category:
            query = query.filter(MLAlgorithmConfig.category == category)
        if is_active is not None:
            query = query.filter(MLAlgorithmConfig.is_active == is_active)
        
        return query.order_by(desc(MLAlgorithmConfig.created_at)).all()
    
    def get_algorithm_config(
        self,
        organization_id: int,
        config_id: int
    ) -> Optional[MLAlgorithmConfig]:
        """Get a specific algorithm configuration"""
        return self.db.query(MLAlgorithmConfig).filter(
            and_(
                MLAlgorithmConfig.id == config_id,
                MLAlgorithmConfig.organization_id == organization_id
            )
        ).first()
    
    def update_algorithm_config(
        self,
        config_id: int,
        organization_id: int,
        **kwargs
    ) -> MLAlgorithmConfig:
        """Update an algorithm configuration"""
        config = self.get_algorithm_config(organization_id, config_id)
        if not config:
            raise ValueError(f"Algorithm config {config_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def delete_algorithm_config(
        self,
        config_id: int,
        organization_id: int
    ) -> bool:
        """Delete an algorithm configuration"""
        config = self.get_algorithm_config(organization_id, config_id)
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        
        return True
    
    # ============================================================================
    # MODEL TRAINING MANAGEMENT
    # ============================================================================
    
    def create_model_training(
        self,
        organization_id: int,
        training_name: str,
        framework: MLFramework,
        algorithm_name: str,
        dataset_config: Dict[str, Any],
        training_params: Dict[str, Any],
        hyperparameters: Dict[str, Any],
        total_epochs: int,
        algorithm_config_id: Optional[int] = None,
        description: Optional[str] = None,
        gpu_used: bool = False,
        created_by_id: int = None
    ) -> MLModelTraining:
        """Create a new model training session"""
        try:
            training = MLModelTraining(
                organization_id=organization_id,
                algorithm_config_id=algorithm_config_id,
                training_name=training_name,
                framework=framework,
                algorithm_name=algorithm_name,
                description=description,
                dataset_config=dataset_config,
                training_params=training_params,
                hyperparameters=hyperparameters,
                total_epochs=total_epochs,
                status=TrainingStatus.PENDING,
                gpu_used=gpu_used,
                created_by_id=created_by_id
            )
            
            self.db.add(training)
            self.db.commit()
            self.db.refresh(training)
            
            logger.info(f"Created model training '{training_name}' for organization {organization_id}")
            return training
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating model training: {str(e)}")
            raise
    
    def get_model_trainings(
        self,
        organization_id: int,
        framework: Optional[MLFramework] = None,
        status: Optional[TrainingStatus] = None
    ) -> List[MLModelTraining]:
        """Get model training sessions for an organization"""
        query = self.db.query(MLModelTraining).filter(
            MLModelTraining.organization_id == organization_id
        )
        
        if framework:
            query = query.filter(MLModelTraining.framework == framework)
        if status:
            query = query.filter(MLModelTraining.status == status)
        
        return query.order_by(desc(MLModelTraining.created_at)).all()
    
    def get_model_training(
        self,
        organization_id: int,
        training_id: int
    ) -> Optional[MLModelTraining]:
        """Get a specific model training session"""
        return self.db.query(MLModelTraining).filter(
            and_(
                MLModelTraining.id == training_id,
                MLModelTraining.organization_id == organization_id
            )
        ).first()
    
    def update_training_progress(
        self,
        training_id: int,
        progress: float,
        current_epoch: int,
        training_metrics: Optional[Dict[str, Any]] = None,
        validation_metrics: Optional[Dict[str, Any]] = None
    ) -> MLModelTraining:
        """Update training progress"""
        training = self.db.query(MLModelTraining).filter(
            MLModelTraining.id == training_id
        ).first()
        
        if not training:
            raise ValueError(f"Model training {training_id} not found")
        
        training.progress = progress
        training.current_epoch = current_epoch
        
        if training_metrics:
            training.training_metrics = training_metrics
        if validation_metrics:
            training.validation_metrics = validation_metrics
        
        self.db.commit()
        self.db.refresh(training)
        
        return training
    
    def update_training_status(
        self,
        training_id: int,
        status: TrainingStatus,
        error_message: Optional[str] = None
    ) -> MLModelTraining:
        """Update training status"""
        training = self.db.query(MLModelTraining).filter(
            MLModelTraining.id == training_id
        ).first()
        
        if not training:
            raise ValueError(f"Model training {training_id} not found")
        
        training.status = status
        
        if status == TrainingStatus.TRAINING and not training.started_at:
            training.started_at = datetime.utcnow()
        elif status in [TrainingStatus.COMPLETED, TrainingStatus.FAILED]:
            training.completed_at = datetime.utcnow()
            if training.started_at:
                duration = (training.completed_at - training.started_at).total_seconds()
                training.training_duration = duration
        
        if error_message:
            training.error_message = error_message
        
        self.db.commit()
        self.db.refresh(training)
        
        return training
    
    def get_framework_algorithms(
        self,
        framework: MLFramework
    ) -> List[str]:
        """Get available algorithms for a framework"""
        algorithms_map = {
            MLFramework.SCIKIT_LEARN: [
                "RandomForest", "GradientBoosting", "LogisticRegression",
                "SVM", "KNN", "DecisionTree"
            ],
            MLFramework.CATBOOST: [
                "CatBoostClassifier", "CatBoostRegressor"
            ],
            MLFramework.LIGHTGBM: [
                "LGBMClassifier", "LGBMRegressor", "LGBMRanker"
            ],
            MLFramework.TENSORFLOW: [
                "Sequential", "FunctionalAPI", "CustomModel"
            ],
            MLFramework.PYTORCH: [
                "Sequential", "CustomModule", "Transformer"
            ],
            MLFramework.XGBOOST: [
                "XGBClassifier", "XGBRegressor", "XGBRanker"
            ]
        }
        
        return algorithms_map.get(framework, [])
    
    def get_training_dashboard(
        self,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get training dashboard data"""
        total_trainings = self.db.query(MLModelTraining).filter(
            MLModelTraining.organization_id == organization_id
        ).count()
        
        completed_trainings = self.db.query(MLModelTraining).filter(
            and_(
                MLModelTraining.organization_id == organization_id,
                MLModelTraining.status == TrainingStatus.COMPLETED
            )
        ).count()
        
        running_trainings = self.db.query(MLModelTraining).filter(
            and_(
                MLModelTraining.organization_id == organization_id,
                MLModelTraining.status == TrainingStatus.TRAINING
            )
        ).count()
        
        recent_trainings = self.get_model_trainings(organization_id)[:5]
        
        return {
            "total_trainings": total_trainings,
            "completed_trainings": completed_trainings,
            "running_trainings": running_trainings,
            "recent_trainings": [
                {
                    "id": training.id,
                    "training_name": training.training_name,
                    "framework": training.framework.value,
                    "status": training.status.value,
                    "progress": training.progress,
                    "created_at": training.created_at.isoformat() if training.created_at else None
                }
                for training in recent_trainings
            ]
        }
