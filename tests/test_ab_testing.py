"""
Tests for A/B Testing functionality
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.ab_testing import (
    ABTestExperiment,
    ABTestVariant,
    ABTestResult,
    ABTestAssignment,
    ExperimentStatus,
    VariantType,
)
from app.services.ab_testing_service import ABTestingService


@pytest.fixture
def ab_testing_service(db_session: Session):
    """Create an ABTestingService instance"""
    return ABTestingService(db_session)


@pytest.fixture
def sample_experiment(db_session: Session, sample_organization, sample_user):
    """Create a sample experiment"""
    experiment = ABTestExperiment(
        organization_id=sample_organization.id,
        created_by_id=sample_user.id,
        experiment_name="Test Experiment",
        description="Test experiment for unit testing",
        status=ExperimentStatus.DRAFT,
        traffic_split={"control": 50, "treatment": 50},
    )
    db_session.add(experiment)
    db_session.commit()
    db_session.refresh(experiment)
    return experiment


@pytest.fixture
def sample_variants(db_session: Session, sample_experiment):
    """Create sample variants"""
    control = ABTestVariant(
        experiment_id=sample_experiment.id,
        variant_name="Control",
        variant_type=VariantType.CONTROL,
        traffic_percentage=50.0,
        model_version="v1.0",
    )
    treatment = ABTestVariant(
        experiment_id=sample_experiment.id,
        variant_name="Treatment",
        variant_type=VariantType.TREATMENT,
        traffic_percentage=50.0,
        model_version="v2.0",
    )
    db_session.add(control)
    db_session.add(treatment)
    db_session.commit()
    db_session.refresh(control)
    db_session.refresh(treatment)
    return [control, treatment]


class TestABTestingService:
    """Test cases for ABTestingService"""

    def test_create_experiment(self, ab_testing_service, sample_organization, sample_user):
        """Test creating an experiment"""
        experiment = ab_testing_service.create_experiment(
            organization_id=sample_organization.id,
            created_by_id=sample_user.id,
            experiment_name="New Experiment",
            description="Test description",
            traffic_split={"control": 60, "treatment": 40},
        )

        assert experiment.id is not None
        assert experiment.experiment_name == "New Experiment"
        assert experiment.description == "Test description"
        assert experiment.status == ExperimentStatus.DRAFT
        assert experiment.traffic_split == {"control": 60, "treatment": 40}

    def test_get_experiment(self, ab_testing_service, sample_experiment, sample_organization):
        """Test getting an experiment"""
        experiment = ab_testing_service.get_experiment(
            sample_experiment.id, sample_organization.id
        )

        assert experiment is not None
        assert experiment.id == sample_experiment.id
        assert experiment.experiment_name == sample_experiment.experiment_name

    def test_list_experiments(
        self, ab_testing_service, sample_experiment, sample_organization
    ):
        """Test listing experiments"""
        experiments = ab_testing_service.list_experiments(
            organization_id=sample_organization.id
        )

        assert len(experiments) > 0
        assert any(exp.id == sample_experiment.id for exp in experiments)

    def test_list_experiments_by_status(
        self, ab_testing_service, sample_experiment, sample_organization
    ):
        """Test listing experiments filtered by status"""
        experiments = ab_testing_service.list_experiments(
            organization_id=sample_organization.id, status=ExperimentStatus.DRAFT
        )

        assert len(experiments) > 0
        assert all(exp.status == ExperimentStatus.DRAFT for exp in experiments)

    def test_start_experiment(self, ab_testing_service, sample_experiment, sample_organization):
        """Test starting an experiment"""
        started_exp = ab_testing_service.start_experiment(
            sample_experiment.id, sample_organization.id
        )

        assert started_exp is not None
        assert started_exp.status == ExperimentStatus.RUNNING
        assert started_exp.start_date is not None

    def test_pause_experiment(self, ab_testing_service, sample_experiment, sample_organization):
        """Test pausing an experiment"""
        # First start the experiment
        ab_testing_service.start_experiment(sample_experiment.id, sample_organization.id)

        # Then pause it
        paused_exp = ab_testing_service.pause_experiment(
            sample_experiment.id, sample_organization.id
        )

        assert paused_exp is not None
        assert paused_exp.status == ExperimentStatus.PAUSED

    def test_complete_experiment(
        self, ab_testing_service, sample_experiment, sample_organization
    ):
        """Test completing an experiment"""
        # First start the experiment
        ab_testing_service.start_experiment(sample_experiment.id, sample_organization.id)

        # Then complete it
        completed_exp = ab_testing_service.complete_experiment(
            sample_experiment.id, sample_organization.id
        )

        assert completed_exp is not None
        assert completed_exp.status == ExperimentStatus.COMPLETED
        assert completed_exp.end_date is not None

    def test_create_variant(
        self, ab_testing_service, sample_experiment, sample_organization
    ):
        """Test creating a variant"""
        variant = ab_testing_service.create_variant(
            experiment_id=sample_experiment.id,
            organization_id=sample_organization.id,
            variant_name="Test Variant",
            variant_type=VariantType.TREATMENT,
            traffic_percentage=30.0,
            model_version="v3.0",
        )

        assert variant.id is not None
        assert variant.variant_name == "Test Variant"
        assert variant.variant_type == VariantType.TREATMENT
        assert variant.traffic_percentage == 30.0

    def test_get_variants(
        self, ab_testing_service, sample_experiment, sample_variants, sample_organization
    ):
        """Test getting variants for an experiment"""
        variants = ab_testing_service.get_variants(
            sample_experiment.id, sample_organization.id
        )

        assert len(variants) == 2
        assert any(v.variant_type == VariantType.CONTROL for v in variants)
        assert any(v.variant_type == VariantType.TREATMENT for v in variants)

    def test_assign_variant(
        self, ab_testing_service, sample_experiment, sample_variants, sample_organization, sample_user
    ):
        """Test assigning a user to a variant"""
        # Start the experiment first
        ab_testing_service.start_experiment(sample_experiment.id, sample_organization.id)

        # Assign user
        variant = ab_testing_service.assign_variant(
            experiment_id=sample_experiment.id,
            organization_id=sample_organization.id,
            user_id=sample_user.id,
        )

        assert variant is not None
        assert variant.id in [v.id for v in sample_variants]

    def test_consistent_assignment(
        self, ab_testing_service, sample_experiment, sample_variants, sample_organization, sample_user
    ):
        """Test that users are consistently assigned to the same variant"""
        # Start the experiment
        ab_testing_service.start_experiment(sample_experiment.id, sample_organization.id)

        # Assign user multiple times
        variant1 = ab_testing_service.assign_variant(
            experiment_id=sample_experiment.id,
            organization_id=sample_organization.id,
            user_id=sample_user.id,
        )
        variant2 = ab_testing_service.assign_variant(
            experiment_id=sample_experiment.id,
            organization_id=sample_organization.id,
            user_id=sample_user.id,
        )

        # Should get the same variant
        assert variant1.id == variant2.id

    def test_record_result(
        self, ab_testing_service, sample_experiment, sample_variants, sample_user
    ):
        """Test recording a result"""
        result = ab_testing_service.record_result(
            experiment_id=sample_experiment.id,
            variant_id=sample_variants[0].id,
            metric_name="conversion_rate",
            metric_value=0.15,
            user_id=sample_user.id,
        )

        assert result.id is not None
        assert result.metric_name == "conversion_rate"
        assert result.metric_value == 0.15

    def test_get_experiment_results(
        self, ab_testing_service, sample_experiment, sample_variants, sample_organization, sample_user
    ):
        """Test getting aggregated experiment results"""
        # Record some results
        for i in range(5):
            ab_testing_service.record_result(
                experiment_id=sample_experiment.id,
                variant_id=sample_variants[0].id,
                metric_name="test_metric",
                metric_value=float(i),
                user_id=sample_user.id,
            )

        # Get results
        results = ab_testing_service.get_experiment_results(
            sample_experiment.id, sample_organization.id
        )

        assert results is not None
        assert "variants" in results
        assert "Control" in results["variants"]
        variant_results = results["variants"]["Control"]
        assert variant_results["sample_size"] > 0
        assert "metrics" in variant_results
        assert "test_metric" in variant_results["metrics"]


class TestABTestingModels:
    """Test cases for A/B Testing database models"""

    def test_experiment_creation(self, db_session, sample_organization, sample_user):
        """Test creating an experiment model"""
        experiment = ABTestExperiment(
            organization_id=sample_organization.id,
            created_by_id=sample_user.id,
            experiment_name="Model Test",
            description="Testing model creation",
            status=ExperimentStatus.DRAFT,
        )
        db_session.add(experiment)
        db_session.commit()
        db_session.refresh(experiment)

        assert experiment.id is not None
        assert experiment.created_at is not None

    def test_variant_creation(self, db_session, sample_experiment):
        """Test creating a variant model"""
        variant = ABTestVariant(
            experiment_id=sample_experiment.id,
            variant_name="Test Variant",
            variant_type=VariantType.CONTROL,
            traffic_percentage=50.0,
        )
        db_session.add(variant)
        db_session.commit()
        db_session.refresh(variant)

        assert variant.id is not None
        assert variant.created_at is not None

    def test_result_creation(self, db_session, sample_experiment, sample_variants):
        """Test creating a result model"""
        result = ABTestResult(
            experiment_id=sample_experiment.id,
            variant_id=sample_variants[0].id,
            metric_name="test_metric",
            metric_value=1.0,
        )
        db_session.add(result)
        db_session.commit()
        db_session.refresh(result)

        assert result.id is not None
        assert result.recorded_at is not None

    def test_assignment_creation(
        self, db_session, sample_experiment, sample_variants, sample_user
    ):
        """Test creating an assignment model"""
        assignment = ABTestAssignment(
            experiment_id=sample_experiment.id,
            variant_id=sample_variants[0].id,
            user_id=sample_user.id,
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        assert assignment.id is not None
        assert assignment.assigned_at is not None
