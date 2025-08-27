# tests/test_service_analytics.py

"""
Test suite for Service Analytics API and service layer
"""

import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.base import (
    Organization, User, Customer, InstallationJob, CompletionRecord, 
    CustomerFeedback, ServiceAnalyticsEvent, AnalyticsSummary
)
from app.services.service_analytics_service import ServiceAnalyticsService
from app.schemas.service_analytics import ReportPeriod, MetricType


# Test fixtures
@pytest.fixture
def db_session():
    """Create a test database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_organization(db_session: Session):
    """Create a test organization"""
    org = Organization(
        name="Test Analytics Org",
        subdomain="test-analytics",
        primary_email="test@analytics.com",
        primary_phone="1234567890",
        address1="Test Address",
        city="Test City",
        state="Test State",
        pin_code="123456"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_technician(db_session: Session, test_organization: Organization):
    """Create a test technician user"""
    technician = User(
        email="technician@test.com",
        hashed_password="hashed_password",
        full_name="Test Technician",
        organization_id=test_organization.id,
        is_active=True
    )
    db_session.add(technician)
    db_session.commit()
    db_session.refresh(technician)
    return technician


@pytest.fixture
def test_customer(db_session: Session, test_organization: Organization):
    """Create a test customer"""
    customer = Customer(
        name="Test Customer",
        email="customer@test.com",
        phone="9876543210",
        organization_id=test_organization.id,
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_installation_jobs(db_session: Session, test_organization: Organization, 
                          test_technician: User, test_customer: Customer):
    """Create test installation jobs with various statuses"""
    jobs = []
    
    # Completed job
    completed_job = InstallationJob(
        organization_id=test_organization.id,
        job_number="JOB-001",
        customer_id=test_customer.id,
        assigned_technician_id=test_technician.id,
        status="completed",
        priority="medium",
        installation_address="Test Address 1",
        scheduled_date=datetime.utcnow() - timedelta(days=2),
        actual_start_time=datetime.utcnow() - timedelta(days=2, hours=2),
        actual_end_time=datetime.utcnow() - timedelta(days=2, hours=1),
        created_at=datetime.utcnow() - timedelta(days=3)
    )
    jobs.append(completed_job)
    
    # In progress job
    in_progress_job = InstallationJob(
        organization_id=test_organization.id,
        job_number="JOB-002",
        customer_id=test_customer.id,
        assigned_technician_id=test_technician.id,
        status="in_progress",
        priority="high",
        installation_address="Test Address 2",
        scheduled_date=datetime.utcnow(),
        actual_start_time=datetime.utcnow() - timedelta(hours=1),
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    jobs.append(in_progress_job)
    
    # Cancelled job
    cancelled_job = InstallationJob(
        organization_id=test_organization.id,
        job_number="JOB-003",
        customer_id=test_customer.id,
        assigned_technician_id=test_technician.id,
        status="cancelled",
        priority="low",
        installation_address="Test Address 3",
        scheduled_date=datetime.utcnow() + timedelta(days=1),
        created_at=datetime.utcnow() - timedelta(hours=12)
    )
    jobs.append(cancelled_job)
    
    for job in jobs:
        db_session.add(job)
    
    db_session.commit()
    for job in jobs:
        db_session.refresh(job)
    
    return jobs


@pytest.fixture
def test_completion_records(db_session: Session, test_installation_jobs: list, test_technician: User):
    """Create test completion records"""
    records = []
    
    # Only for completed jobs
    completed_jobs = [job for job in test_installation_jobs if job.status == "completed"]
    
    for job in completed_jobs:
        record = CompletionRecord(
            organization_id=job.organization_id,
            installation_job_id=job.id,
            completed_by_id=test_technician.id,
            completion_status="completed",
            completion_date=job.actual_end_time,
            actual_start_time=job.actual_start_time,
            actual_end_time=job.actual_end_time,
            total_duration_minutes=60,  # 1 hour
            work_performed="Installation completed successfully",
            quality_check_passed=True,
            customer_present=True,
            customer_signature_received=True,
            feedback_request_sent=True,
            feedback_request_sent_at=job.actual_end_time + timedelta(minutes=30)
        )
        records.append(record)
        db_session.add(record)
    
    db_session.commit()
    for record in records:
        db_session.refresh(record)
    
    return records


@pytest.fixture
def test_customer_feedback(db_session: Session, test_installation_jobs: list, test_customer: Customer):
    """Create test customer feedback"""
    feedback_records = []
    
    # Only for completed jobs
    completed_jobs = [job for job in test_installation_jobs if job.status == "completed"]
    
    for job in completed_jobs:
        feedback = CustomerFeedback(
            organization_id=job.organization_id,
            installation_job_id=job.id,
            customer_id=test_customer.id,
            overall_rating=4,
            service_quality_rating=4,
            technician_rating=5,
            timeliness_rating=3,
            communication_rating=4,
            feedback_comments="Good service overall",
            would_recommend=True,
            satisfaction_level="satisfied",
            feedback_status="submitted",
            submitted_at=job.actual_end_time + timedelta(hours=2)
        )
        feedback_records.append(feedback)
        db_session.add(feedback)
    
    db_session.commit()
    for feedback in feedback_records:
        db_session.refresh(feedback)
    
    return feedback_records


# Service Layer Tests
class TestServiceAnalyticsService:
    """Test the ServiceAnalyticsService class"""
    
    def test_get_date_range_today(self, db_session: Session, test_organization: Organization):
        """Test date range calculation for today"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        start_date, end_date = service.get_date_range(ReportPeriod.TODAY)
        
        today = date.today()
        assert start_date == today
        assert end_date == today
    
    def test_get_date_range_week(self, db_session: Session, test_organization: Organization):
        """Test date range calculation for week"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        start_date, end_date = service.get_date_range(ReportPeriod.WEEK)
        
        today = date.today()
        expected_start = today - timedelta(days=today.weekday())
        expected_end = expected_start + timedelta(days=6)
        
        assert start_date == expected_start
        assert end_date == expected_end
    
    def test_get_date_range_custom(self, db_session: Session, test_organization: Organization):
        """Test date range calculation for custom dates"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        custom_start = date(2024, 1, 1)
        custom_end = date(2024, 1, 31)
        
        start_date, end_date = service.get_date_range(
            ReportPeriod.CUSTOM, custom_start, custom_end
        )
        
        assert start_date == custom_start
        assert end_date == custom_end
    
    def test_get_job_completion_metrics(self, db_session: Session, test_organization: Organization,
                                      test_installation_jobs: list):
        """Test job completion metrics calculation"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        
        # Use a date range that includes all test jobs
        start_date = date.today() - timedelta(days=7)
        end_date = date.today() + timedelta(days=1)
        
        metrics = service.get_job_completion_metrics(start_date, end_date)
        
        assert metrics.total_jobs == 3  # We created 3 test jobs
        assert metrics.completed_jobs == 1  # 1 completed job
        assert metrics.pending_jobs == 1  # 1 in progress job  
        assert metrics.cancelled_jobs == 1  # 1 cancelled job
        assert metrics.completion_rate == 33.33  # 1/3 * 100
        assert metrics.average_completion_time_hours == 1.0  # 1 hour duration
        assert "completed" in metrics.jobs_by_status
        assert "in_progress" in metrics.jobs_by_status
        assert "cancelled" in metrics.jobs_by_status
    
    def test_get_technician_performance_metrics(self, db_session: Session, test_organization: Organization,
                                              test_installation_jobs: list, test_technician: User):
        """Test technician performance metrics calculation"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        
        start_date = date.today() - timedelta(days=7)
        end_date = date.today() + timedelta(days=1)
        
        metrics = service.get_technician_performance_metrics(start_date, end_date)
        
        assert len(metrics) == 1  # We have 1 technician
        tech_metric = metrics[0]
        assert tech_metric.technician_id == test_technician.id
        assert tech_metric.technician_name == test_technician.full_name
        assert tech_metric.total_jobs_assigned == 3
        assert tech_metric.jobs_completed == 1
        assert tech_metric.jobs_in_progress == 1
        assert tech_metric.utilization_rate > 0
        assert tech_metric.efficiency_score > 0
    
    def test_get_customer_satisfaction_metrics(self, db_session: Session, test_organization: Organization,
                                             test_customer_feedback: list):
        """Test customer satisfaction metrics calculation"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        
        start_date = date.today() - timedelta(days=7)
        end_date = date.today() + timedelta(days=1)
        
        metrics = service.get_customer_satisfaction_metrics(start_date, end_date)
        
        assert metrics.total_feedback_received == 1  # We created 1 feedback record
        assert metrics.average_overall_rating == 4.0
        assert metrics.average_service_quality == 4.0
        assert metrics.average_technician_rating == 5.0
        assert metrics.average_timeliness_rating == 3.0
        assert metrics.average_communication_rating == 4.0
        assert "satisfied" in metrics.satisfaction_distribution
        assert metrics.recommendation_rate == 100.0  # 100% would recommend
        assert metrics.nps_score > 0  # Positive NPS score
    
    def test_get_job_volume_metrics(self, db_session: Session, test_organization: Organization,
                                   test_installation_jobs: list):
        """Test job volume metrics calculation"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        
        start_date = date.today() - timedelta(days=7)
        end_date = date.today() + timedelta(days=1)
        
        metrics = service.get_job_volume_metrics(start_date, end_date)
        
        assert metrics.total_jobs == 3
        assert metrics.jobs_per_day_average > 0
        assert len(metrics.volume_trend) > 0
        assert "medium" in metrics.jobs_by_priority
        assert "high" in metrics.jobs_by_priority
        assert "low" in metrics.jobs_by_priority
        assert len(metrics.jobs_by_customer) == 1  # We have 1 customer
    
    def test_get_analytics_dashboard(self, db_session: Session, test_organization: Organization,
                                   test_installation_jobs: list, test_customer_feedback: list):
        """Test complete analytics dashboard generation"""
        service = ServiceAnalyticsService(db_session, test_organization.id)
        
        dashboard = service.get_analytics_dashboard(ReportPeriod.WEEK)
        
        assert dashboard.organization_id == test_organization.id
        assert dashboard.report_period == ReportPeriod.WEEK
        assert dashboard.job_completion.total_jobs > 0
        assert len(dashboard.technician_performance) > 0
        assert dashboard.customer_satisfaction.total_feedback_received > 0
        assert dashboard.job_volume.total_jobs > 0
        assert dashboard.generated_at is not None


# API Endpoint Tests
class TestServiceAnalyticsAPI:
    """Test the Service Analytics API endpoints"""
    
    def test_get_analytics_dashboard_unauthorized(self, test_client: TestClient):
        """Test dashboard endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/dashboard")
        assert response.status_code == 401
    
    def test_get_job_completion_metrics_unauthorized(self, test_client: TestClient):
        """Test job completion metrics endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/job-completion")
        assert response.status_code == 401
    
    def test_get_technician_performance_unauthorized(self, test_client: TestClient):
        """Test technician performance endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/technician-performance")
        assert response.status_code == 401
    
    def test_get_customer_satisfaction_unauthorized(self, test_client: TestClient):
        """Test customer satisfaction endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/customer-satisfaction")
        assert response.status_code == 401
    
    def test_get_job_volume_unauthorized(self, test_client: TestClient):
        """Test job volume endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/job-volume")
        assert response.status_code == 401
    
    def test_get_sla_compliance_unauthorized(self, test_client: TestClient):
        """Test SLA compliance endpoint without authentication"""
        response = test_client.get("/api/v1/service-analytics/organizations/1/analytics/sla-compliance")
        assert response.status_code == 401


# Model Tests
class TestAnalyticsModels:
    """Test analytics database models"""
    
    def test_service_analytics_event_creation(self, db_session: Session, test_organization: Organization,
                                            test_installation_jobs: list, test_technician: User):
        """Test creating a service analytics event"""
        job = test_installation_jobs[0]
        
        event = ServiceAnalyticsEvent(
            organization_id=test_organization.id,
            event_type="job_completed",
            event_category="completion",
            installation_job_id=job.id,
            technician_id=test_technician.id,
            customer_id=job.customer_id,
            event_data={"completion_time": 60, "quality_score": 5},
            metric_value=60.0,
            event_timestamp=datetime.utcnow()
        )
        
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        
        assert event.id is not None
        assert event.organization_id == test_organization.id
        assert event.event_type == "job_completed"
        assert event.event_category == "completion"
        assert event.metric_value == 60.0
    
    def test_analytics_summary_creation(self, db_session: Session, test_organization: Organization):
        """Test creating an analytics summary"""
        summary = AnalyticsSummary(
            organization_id=test_organization.id,
            summary_type="daily",
            summary_date=date.today(),
            total_jobs=10,
            completed_jobs=8,
            pending_jobs=1,
            cancelled_jobs=1,
            average_completion_time_hours=2.5,
            total_feedback_received=7,
            average_overall_rating=4.2,
            sla_met_count=6,
            sla_breached_count=2,
            sla_compliance_rate=75.0
        )
        
        db_session.add(summary)
        db_session.commit()
        db_session.refresh(summary)
        
        assert summary.id is not None
        assert summary.organization_id == test_organization.id
        assert summary.summary_type == "daily"
        assert summary.total_jobs == 10
        assert summary.completed_jobs == 8
        assert summary.average_completion_time_hours == 2.5
        assert summary.sla_compliance_rate == 75.0


# Schema Validation Tests
class TestAnalyticsSchemas:
    """Test analytics Pydantic schemas"""
    
    def test_analytics_request_validation(self):
        """Test analytics request schema validation"""
        from app.schemas.service_analytics import AnalyticsRequest
        
        # Valid request
        request = AnalyticsRequest(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            period=ReportPeriod.CUSTOM,
            technician_id=1,
            customer_id=1
        )
        
        assert request.start_date == date(2024, 1, 1)
        assert request.end_date == date(2024, 1, 31)
        assert request.period == ReportPeriod.CUSTOM
    
    def test_analytics_request_date_validation(self):
        """Test that end_date must be after start_date"""
        from app.schemas.service_analytics import AnalyticsRequest
        from pydantic import ValidationError
        
        # Invalid request: end_date before start_date
        with pytest.raises(ValidationError):
            AnalyticsRequest(
                start_date=date(2024, 1, 31),
                end_date=date(2024, 1, 1),
                period=ReportPeriod.CUSTOM
            )
    
    def test_job_completion_metrics_schema(self):
        """Test job completion metrics schema"""
        from app.schemas.service_analytics import JobCompletionMetrics, TimeSeriesDataPoint
        
        metrics = JobCompletionMetrics(
            total_jobs=100,
            completed_jobs=80,
            pending_jobs=15,
            cancelled_jobs=5,
            completion_rate=80.0,
            average_completion_time_hours=2.5,
            on_time_completion_rate=75.0,
            jobs_by_status={"completed": 80, "pending": 15, "cancelled": 5},
            completion_trend=[
                TimeSeriesDataPoint(date=date.today(), value=10, label="10 completed")
            ]
        )
        
        assert metrics.total_jobs == 100
        assert metrics.completion_rate == 80.0
        assert len(metrics.completion_trend) == 1
        assert metrics.completion_trend[0].value == 10


if __name__ == "__main__":
    pytest.main([__file__])