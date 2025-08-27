# tests/test_service_analytics_simple.py

"""
Simple test suite for Service Analytics - focuses on core functionality
without complex database setup
"""

import pytest
from datetime import datetime, date, timedelta
from app.schemas.service_analytics import (
    ReportPeriod, MetricType, AnalyticsRequest, JobCompletionMetrics,
    TechnicianPerformanceMetrics, CustomerSatisfactionMetrics,
    JobVolumeMetrics, SLAComplianceMetrics, TimeSeriesDataPoint
)


class TestServiceAnalyticsSchemas:
    """Test Service Analytics Pydantic schemas"""
    
    def test_analytics_request_validation(self):
        """Test analytics request schema validation"""
        # Valid request
        request = AnalyticsRequest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            period=ReportPeriod.CUSTOM,
            technician_id=1,
            customer_id=1
        )
        
        assert request.period == ReportPeriod.CUSTOM
        assert request.technician_id == 1
        assert request.customer_id == 1
    
    def test_analytics_request_date_validation(self):
        """Test that end_date validation works"""
        from pydantic import ValidationError
        
        # This should not raise an error with correct dates
        try:
            request = AnalyticsRequest(
                start_date="2024-01-01",
                end_date="2024-01-31",
                period=ReportPeriod.CUSTOM
            )
            assert True  # If we get here, validation passed
        except ValidationError:
            assert False, "Valid dates should not raise ValidationError"
    
    def test_job_completion_metrics_schema(self):
        """Test job completion metrics schema"""
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
                TimeSeriesDataPoint(date="2024-01-01", value=10, label="10 completed")
            ]
        )
        
        assert metrics.total_jobs == 100
        assert metrics.completion_rate == 80.0
        assert len(metrics.completion_trend) == 1
        assert metrics.completion_trend[0].value == 10
    
    def test_technician_performance_metrics_schema(self):
        """Test technician performance metrics schema"""
        metrics = TechnicianPerformanceMetrics(
            technician_id=1,
            technician_name="John Doe",
            total_jobs_assigned=50,
            jobs_completed=45,
            jobs_in_progress=3,
            average_completion_time_hours=2.0,
            customer_rating_average=4.5,
            utilization_rate=85.0,
            efficiency_score=92.0
        )
        
        assert metrics.technician_id == 1
        assert metrics.technician_name == "John Doe"
        assert metrics.efficiency_score == 92.0
        assert metrics.customer_rating_average == 4.5
    
    def test_customer_satisfaction_metrics_schema(self):
        """Test customer satisfaction metrics schema"""
        metrics = CustomerSatisfactionMetrics(
            total_feedback_received=25,
            average_overall_rating=4.2,
            average_service_quality=4.1,
            average_technician_rating=4.5,
            average_timeliness_rating=3.8,
            average_communication_rating=4.3,
            satisfaction_distribution={"satisfied": 20, "neutral": 3, "dissatisfied": 2},
            nps_score=15.0,
            recommendation_rate=85.0,
            satisfaction_trend=[
                TimeSeriesDataPoint(date="2024-01-01", value=4.2, label="4.2 avg rating")
            ]
        )
        
        assert metrics.total_feedback_received == 25
        assert metrics.average_overall_rating == 4.2
        assert metrics.nps_score == 15.0
        assert metrics.recommendation_rate == 85.0
    
    def test_job_volume_metrics_schema(self):
        """Test job volume metrics schema"""
        metrics = JobVolumeMetrics(
            total_jobs=150,
            jobs_per_day_average=5.2,
            peak_day="2024-01-15",
            peak_day_count=12,
            volume_trend=[
                TimeSeriesDataPoint(date="2024-01-01", value=5, label="5 jobs")
            ],
            jobs_by_priority={"urgent": 10, "high": 25, "medium": 80, "low": 35},
            jobs_by_customer=[
                {"customer_id": 1, "customer_name": "Acme Corp", "job_count": 15},
                {"customer_id": 2, "customer_name": "Tech Solutions", "job_count": 12}
            ]
        )
        
        assert metrics.total_jobs == 150
        assert metrics.jobs_per_day_average == 5.2
        assert metrics.peak_day == "2024-01-15"
        assert len(metrics.jobs_by_customer) == 2
    
    def test_sla_compliance_metrics_schema(self):
        """Test SLA compliance metrics schema"""
        metrics = SLAComplianceMetrics(
            total_jobs_with_sla=100,
            sla_met_count=85,
            sla_breached_count=15,
            overall_compliance_rate=85.0,
            average_resolution_time_hours=4.5,
            compliance_by_priority={"urgent": 75.0, "high": 85.0, "medium": 90.0, "low": 95.0},
            compliance_trend=[
                TimeSeriesDataPoint(date="2024-01-01", value=85.0, label="85% compliance")
            ],
            breach_reasons={"delayed_start": 8, "parts_unavailable": 4, "technical_issues": 3}
        )
        
        assert metrics.total_jobs_with_sla == 100
        assert metrics.overall_compliance_rate == 85.0
        assert metrics.sla_met_count == 85
        assert metrics.sla_breached_count == 15
    
    def test_time_series_data_point_schema(self):
        """Test time series data point schema"""
        point = TimeSeriesDataPoint(
            date="2024-01-01",
            value=25,
            label="25 jobs completed"
        )
        
        assert point.date == "2024-01-01"
        assert point.value == 25
        assert point.label == "25 jobs completed"
    
    def test_report_period_enum(self):
        """Test report period enum values"""
        assert ReportPeriod.TODAY == "today"
        assert ReportPeriod.WEEK == "week"
        assert ReportPeriod.MONTH == "month"
        assert ReportPeriod.QUARTER == "quarter"
        assert ReportPeriod.YEAR == "year"
        assert ReportPeriod.CUSTOM == "custom"
    
    def test_metric_type_enum(self):
        """Test metric type enum values"""
        assert MetricType.JOB_COMPLETION == "job_completion"
        assert MetricType.TECHNICIAN_PERFORMANCE == "technician_performance"
        assert MetricType.CUSTOMER_SATISFACTION == "customer_satisfaction"
        assert MetricType.JOB_VOLUME == "job_volume"
        assert MetricType.SLA_COMPLIANCE == "sla_compliance"


class TestServiceAnalyticsLogic:
    """Test Service Analytics business logic without database"""
    
    def test_completion_rate_calculation(self):
        """Test completion rate calculation logic"""
        total_jobs = 100
        completed_jobs = 85
        completion_rate = (completed_jobs / total_jobs) * 100
        
        assert completion_rate == 85.0
    
    def test_efficiency_score_calculation(self):
        """Test efficiency score calculation logic"""
        # Simplified efficiency calculation
        completion_rate = 90.0  # 90% completion rate
        customer_rating = 4.5   # 4.5/5 = 90% satisfaction
        rating_percentage = (customer_rating / 5.0) * 100
        
        # Weighted average: 70% completion + 30% satisfaction
        efficiency_score = (completion_rate * 0.7) + (rating_percentage * 0.3)
        
        expected = (90.0 * 0.7) + (90.0 * 0.3)  # = 63 + 27 = 90
        assert efficiency_score == expected
    
    def test_nps_calculation(self):
        """Test Net Promoter Score calculation logic"""
        # Simplified NPS calculation
        total_responses = 100
        promoters = 60  # ratings 4-5
        detractors = 10  # ratings 1-2
        passives = 30   # rating 3
        
        nps = ((promoters - detractors) / total_responses) * 100
        assert nps == 50.0  # (60-10)/100 * 100 = 50
    
    def test_utilization_rate_calculation(self):
        """Test technician utilization rate calculation"""
        working_days = 20
        completed_jobs = 15
        
        # Simplified utilization (jobs per day)
        utilization_rate = min((completed_jobs / working_days) * 100, 100)
        
        expected = (15 / 20) * 100  # = 75%
        assert utilization_rate == expected
    
    def test_sla_compliance_calculation(self):
        """Test SLA compliance rate calculation"""
        total_sla_jobs = 50
        sla_met = 42
        sla_breached = 8
        
        compliance_rate = (sla_met / total_sla_jobs) * 100
        assert compliance_rate == 84.0
        assert sla_met + sla_breached == total_sla_jobs


if __name__ == "__main__":
    pytest.main([__file__])