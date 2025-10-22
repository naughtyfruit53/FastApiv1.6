"""
A/B Testing Service for Model Version Comparison
"""

import logging
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.ab_testing import (
    ABTestExperiment, ABTestVariant, ABTestResult, ABTestAssignment,
    ExperimentStatus, VariantType
)
from app.models.user_models import User

logger = logging.getLogger(__name__)


class ABTestingService:
    """Service for managing A/B testing experiments"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # EXPERIMENT MANAGEMENT
    # ============================================================================
    
    def create_experiment(
        self,
        organization_id: int,
        created_by_id: int,
        experiment_name: str,
        description: Optional[str] = None,
        traffic_split: Optional[Dict[str, float]] = None
    ) -> ABTestExperiment:
        """Create a new A/B test experiment"""
        try:
            experiment = ABTestExperiment(
                organization_id=organization_id,
                created_by_id=created_by_id,
                experiment_name=experiment_name,
                description=description,
                status=ExperimentStatus.DRAFT,
                traffic_split=traffic_split or {"control": 50, "treatment": 50}
            )
            self.db.add(experiment)
            self.db.commit()
            self.db.refresh(experiment)
            
            logger.info(f"Created experiment {experiment.id} for org {organization_id}")
            return experiment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating experiment: {e}")
            raise
    
    def get_experiment(
        self,
        experiment_id: int,
        organization_id: int
    ) -> Optional[ABTestExperiment]:
        """Get an experiment by ID"""
        return self.db.query(ABTestExperiment).filter(
            and_(
                ABTestExperiment.id == experiment_id,
                ABTestExperiment.organization_id == organization_id
            )
        ).first()
    
    def list_experiments(
        self,
        organization_id: int,
        status: Optional[ExperimentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ABTestExperiment]:
        """List experiments for an organization"""
        query = self.db.query(ABTestExperiment).filter(
            ABTestExperiment.organization_id == organization_id
        )
        
        if status:
            query = query.filter(ABTestExperiment.status == status)
        
        return query.order_by(desc(ABTestExperiment.created_at)).offset(skip).limit(limit).all()
    
    def update_experiment(
        self,
        experiment_id: int,
        organization_id: int,
        **updates
    ) -> Optional[ABTestExperiment]:
        """Update an experiment"""
        try:
            experiment = self.get_experiment(experiment_id, organization_id)
            if not experiment:
                return None
            
            for key, value in updates.items():
                if hasattr(experiment, key):
                    setattr(experiment, key, value)
            
            self.db.commit()
            self.db.refresh(experiment)
            
            logger.info(f"Updated experiment {experiment_id}")
            return experiment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating experiment: {e}")
            raise
    
    def start_experiment(
        self,
        experiment_id: int,
        organization_id: int
    ) -> Optional[ABTestExperiment]:
        """Start an experiment"""
        try:
            experiment = self.get_experiment(experiment_id, organization_id)
            if not experiment:
                return None
            
            if experiment.status != ExperimentStatus.DRAFT:
                raise ValueError(f"Cannot start experiment in {experiment.status} status")
            
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(experiment)
            
            logger.info(f"Started experiment {experiment_id}")
            return experiment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting experiment: {e}")
            raise
    
    def pause_experiment(
        self,
        experiment_id: int,
        organization_id: int
    ) -> Optional[ABTestExperiment]:
        """Pause a running experiment"""
        return self.update_experiment(
            experiment_id,
            organization_id,
            status=ExperimentStatus.PAUSED
        )
    
    def complete_experiment(
        self,
        experiment_id: int,
        organization_id: int
    ) -> Optional[ABTestExperiment]:
        """Complete an experiment"""
        try:
            experiment = self.get_experiment(experiment_id, organization_id)
            if not experiment:
                return None
            
            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_date = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(experiment)
            
            logger.info(f"Completed experiment {experiment_id}")
            return experiment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error completing experiment: {e}")
            raise
    
    # ============================================================================
    # VARIANT MANAGEMENT
    # ============================================================================
    
    def create_variant(
        self,
        experiment_id: int,
        organization_id: int,
        variant_name: str,
        variant_type: VariantType,
        model_id: Optional[int] = None,
        model_version: Optional[str] = None,
        traffic_percentage: float = 50.0,
        variant_config: Optional[Dict[str, Any]] = None
    ) -> ABTestVariant:
        """Create a variant for an experiment"""
        try:
            # Verify experiment exists and belongs to organization
            experiment = self.get_experiment(experiment_id, organization_id)
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            variant = ABTestVariant(
                experiment_id=experiment_id,
                variant_name=variant_name,
                variant_type=variant_type,
                model_id=model_id,
                model_version=model_version,
                traffic_percentage=traffic_percentage,
                variant_config=variant_config
            )
            self.db.add(variant)
            self.db.commit()
            self.db.refresh(variant)
            
            logger.info(f"Created variant {variant.id} for experiment {experiment_id}")
            return variant
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating variant: {e}")
            raise
    
    def get_variants(
        self,
        experiment_id: int,
        organization_id: int
    ) -> List[ABTestVariant]:
        """Get all variants for an experiment"""
        experiment = self.get_experiment(experiment_id, organization_id)
        if not experiment:
            return []
        
        return self.db.query(ABTestVariant).filter(
            ABTestVariant.experiment_id == experiment_id
        ).all()
    
    # ============================================================================
    # ASSIGNMENT AND ROUTING
    # ============================================================================
    
    def assign_variant(
        self,
        experiment_id: int,
        organization_id: int,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[ABTestVariant]:
        """Assign a user/session to a variant"""
        try:
            # Check for existing assignment
            assignment = self._get_assignment(experiment_id, user_id, session_id)
            if assignment:
                assignment.last_seen_at = datetime.utcnow()
                self.db.commit()
                return assignment.variant
            
            # Get experiment and variants
            experiment = self.get_experiment(experiment_id, organization_id)
            if not experiment or experiment.status != ExperimentStatus.RUNNING:
                return None
            
            variants = self.get_variants(experiment_id, organization_id)
            if not variants:
                return None
            
            # Select variant based on traffic allocation
            selected_variant = self._select_variant(variants, user_id, session_id)
            
            # Create assignment
            assignment = ABTestAssignment(
                experiment_id=experiment_id,
                variant_id=selected_variant.id,
                user_id=user_id,
                session_id=session_id
            )
            self.db.add(assignment)
            self.db.commit()
            
            logger.info(f"Assigned variant {selected_variant.id} to user {user_id or session_id}")
            return selected_variant
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning variant: {e}")
            raise
    
    def _get_assignment(
        self,
        experiment_id: int,
        user_id: Optional[int],
        session_id: Optional[str]
    ) -> Optional[ABTestAssignment]:
        """Get existing assignment for user/session"""
        query = self.db.query(ABTestAssignment).filter(
            ABTestAssignment.experiment_id == experiment_id
        )
        
        if user_id:
            query = query.filter(ABTestAssignment.user_id == user_id)
        elif session_id:
            query = query.filter(ABTestAssignment.session_id == session_id)
        else:
            return None
        
        return query.first()
    
    def _select_variant(
        self,
        variants: List[ABTestVariant],
        user_id: Optional[int],
        session_id: Optional[str]
    ) -> ABTestVariant:
        """Select a variant based on traffic allocation"""
        # Use deterministic hashing for consistent assignment
        identifier = str(user_id) if user_id else (session_id or str(random.random()))
        hash_value = int(hashlib.md5(identifier.encode()).hexdigest(), 16)
        random_value = (hash_value % 100) + 1  # 1-100
        
        cumulative = 0
        for variant in variants:
            cumulative += variant.traffic_percentage
            if random_value <= cumulative:
                return variant
        
        # Fallback to first variant
        return variants[0]
    
    # ============================================================================
    # RESULT TRACKING
    # ============================================================================
    
    def record_result(
        self,
        experiment_id: int,
        variant_id: int,
        metric_name: str,
        metric_value: float,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        result_metadata: Optional[Dict[str, Any]] = None
    ) -> ABTestResult:
        """Record a result for a variant"""
        try:
            result = ABTestResult(
                experiment_id=experiment_id,
                variant_id=variant_id,
                user_id=user_id,
                session_id=session_id,
                metric_name=metric_name,
                metric_value=metric_value,
                result_metadata=result_metadata
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            logger.info(f"Recorded result for variant {variant_id}: {metric_name}={metric_value}")
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording result: {e}")
            raise
    
    def get_experiment_results(
        self,
        experiment_id: int,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get aggregated results for an experiment"""
        experiment = self.get_experiment(experiment_id, organization_id)
        if not experiment:
            return {}
        
        variants = self.get_variants(experiment_id, organization_id)
        
        results = {}
        for variant in variants:
            variant_results = self._get_variant_results(variant.id)
            results[variant.variant_name] = variant_results
        
        return {
            "experiment_id": experiment_id,
            "experiment_name": experiment.experiment_name,
            "status": experiment.status,
            "start_date": experiment.start_date,
            "end_date": experiment.end_date,
            "variants": results
        }
    
    def _get_variant_results(self, variant_id: int) -> Dict[str, Any]:
        """Get aggregated results for a variant"""
        # Get all results for this variant
        results = self.db.query(ABTestResult).filter(
            ABTestResult.variant_id == variant_id
        ).all()
        
        if not results:
            return {"sample_size": 0, "metrics": {}}
        
        # Aggregate by metric name
        metrics = {}
        for result in results:
            if result.metric_name not in metrics:
                metrics[result.metric_name] = []
            metrics[result.metric_name].append(result.metric_value)
        
        # Calculate statistics
        aggregated_metrics = {}
        for metric_name, values in metrics.items():
            aggregated_metrics[metric_name] = {
                "count": len(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "sum": sum(values)
            }
        
        return {
            "sample_size": len(set(r.user_id or r.session_id for r in results)),
            "metrics": aggregated_metrics
        }