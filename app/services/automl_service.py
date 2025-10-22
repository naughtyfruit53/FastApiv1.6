"""
AutoML Service for automatic model selection and hyperparameter tuning
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.automl import (
    AutoMLRun, AutoMLModelCandidate, AutoMLTaskType, 
    AutoMLStatus, AutoMLFramework
)
from app.models.user_models import User, Organization

logger = logging.getLogger(__name__)


class AutoMLService:
    """Service for AutoML operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_automl_run(
        self,
        organization_id: int,
        run_name: str,
        task_type: AutoMLTaskType,
        target_column: str,
        feature_columns: List[str],
        metric: str,
        framework: AutoMLFramework = AutoMLFramework.OPTUNA,
        time_budget: int = 3600,
        max_trials: int = 100,
        dataset_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        created_by_id: int = None
    ) -> AutoMLRun:
        """Create a new AutoML run"""
        try:
            run = AutoMLRun(
                organization_id=organization_id,
                run_name=run_name,
                task_type=task_type,
                framework=framework,
                description=description,
                target_column=target_column,
                feature_columns=feature_columns,
                metric=metric,
                time_budget=time_budget,
                max_trials=max_trials,
                dataset_config=dataset_config or {},
                status=AutoMLStatus.PENDING,
                created_by_id=created_by_id
            )
            
            self.db.add(run)
            self.db.commit()
            self.db.refresh(run)
            
            logger.info(f"Created AutoML run '{run_name}' for organization {organization_id}")
            return run
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating AutoML run: {str(e)}")
            raise
    
    def get_automl_runs(
        self,
        organization_id: int,
        status: Optional[AutoMLStatus] = None,
        task_type: Optional[AutoMLTaskType] = None
    ) -> List[AutoMLRun]:
        """Get AutoML runs for an organization"""
        query = self.db.query(AutoMLRun).filter(
            AutoMLRun.organization_id == organization_id
        )
        
        if status:
            query = query.filter(AutoMLRun.status == status)
        if task_type:
            query = query.filter(AutoMLRun.task_type == task_type)
        
        return query.order_by(desc(AutoMLRun.created_at)).all()
    
    def get_automl_run(
        self,
        organization_id: int,
        run_id: int
    ) -> Optional[AutoMLRun]:
        """Get a specific AutoML run"""
        return self.db.query(AutoMLRun).filter(
            and_(
                AutoMLRun.id == run_id,
                AutoMLRun.organization_id == organization_id
            )
        ).first()
    
    def update_automl_run_status(
        self,
        run_id: int,
        status: AutoMLStatus,
        progress: Optional[float] = None,
        current_trial: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> AutoMLRun:
        """Update AutoML run status"""
        run = self.db.query(AutoMLRun).filter(AutoMLRun.id == run_id).first()
        if not run:
            raise ValueError(f"AutoML run {run_id} not found")
        
        run.status = status
        if progress is not None:
            run.progress = progress
        if current_trial is not None:
            run.current_trial = current_trial
        if error_message:
            run.error_message = error_message
        
        if status == AutoMLStatus.RUNNING and not run.started_at:
            run.started_at = datetime.utcnow()
        elif status in [AutoMLStatus.COMPLETED, AutoMLStatus.FAILED, AutoMLStatus.CANCELLED]:
            run.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(run)
        
        return run
    
    def save_model_candidate(
        self,
        automl_run_id: int,
        organization_id: int,
        trial_number: int,
        model_name: str,
        algorithm: str,
        hyperparameters: Dict[str, Any],
        score: float,
        training_time: float,
        evaluation_metrics: Optional[Dict[str, Any]] = None,
        feature_importance: Optional[Dict[str, Any]] = None
    ) -> AutoMLModelCandidate:
        """Save a model candidate evaluated during AutoML"""
        try:
            candidate = AutoMLModelCandidate(
                automl_run_id=automl_run_id,
                organization_id=organization_id,
                trial_number=trial_number,
                model_name=model_name,
                algorithm=algorithm,
                hyperparameters=hyperparameters,
                score=score,
                training_time=training_time,
                evaluation_metrics=evaluation_metrics or {},
                feature_importance=feature_importance
            )
            
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            
            return candidate
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving model candidate: {str(e)}")
            raise
    
    def update_best_model(
        self,
        run_id: int,
        best_model_name: str,
        best_model_params: Dict[str, Any],
        best_score: float,
        best_model_path: Optional[str] = None
    ) -> AutoMLRun:
        """Update the best model for an AutoML run"""
        run = self.db.query(AutoMLRun).filter(AutoMLRun.id == run_id).first()
        if not run:
            raise ValueError(f"AutoML run {run_id} not found")
        
        run.best_model_name = best_model_name
        run.best_model_params = best_model_params
        run.best_score = best_score
        if best_model_path:
            run.best_model_path = best_model_path
        
        self.db.commit()
        self.db.refresh(run)
        
        return run
    
    def get_leaderboard(
        self,
        automl_run_id: int,
        top_n: int = 10
    ) -> List[AutoMLModelCandidate]:
        """Get top N models from AutoML run"""
        return self.db.query(AutoMLModelCandidate).filter(
            AutoMLModelCandidate.automl_run_id == automl_run_id
        ).order_by(desc(AutoMLModelCandidate.score)).limit(top_n).all()
    
    def get_automl_dashboard(
        self,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get AutoML dashboard data"""
        total_runs = self.db.query(AutoMLRun).filter(
            AutoMLRun.organization_id == organization_id
        ).count()
        
        completed_runs = self.db.query(AutoMLRun).filter(
            and_(
                AutoMLRun.organization_id == organization_id,
                AutoMLRun.status == AutoMLStatus.COMPLETED
            )
        ).count()
        
        running_runs = self.db.query(AutoMLRun).filter(
            and_(
                AutoMLRun.organization_id == organization_id,
                AutoMLRun.status == AutoMLStatus.RUNNING
            )
        ).count()
        
        recent_runs = self.get_automl_runs(organization_id)[:5]
        
        return {
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "running_runs": running_runs,
            "recent_runs": [
                {
                    "id": run.id,
                    "run_name": run.run_name,
                    "task_type": run.task_type.value,
                    "status": run.status.value,
                    "best_score": run.best_score,
                    "created_at": run.created_at.isoformat() if run.created_at else None
                }
                for run in recent_runs
            ]
        }
    
    def start_automl_run(
        self,
        run_id: int,
        dataset: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Start AutoML run (stub for actual training logic)
        In production, this would trigger background training
        """
        run = self.db.query(AutoMLRun).filter(AutoMLRun.id == run_id).first()
        if not run:
            raise ValueError(f"AutoML run {run_id} not found")
        
        self.update_automl_run_status(run_id, AutoMLStatus.RUNNING, progress=0.0, current_trial=0)
        
        return {
            "run_id": run_id,
            "status": "started",
            "message": "AutoML training initiated"
        }
    
    def cancel_automl_run(
        self,
        run_id: int
    ) -> AutoMLRun:
        """Cancel a running AutoML run"""
        return self.update_automl_run_status(run_id, AutoMLStatus.CANCELLED)
