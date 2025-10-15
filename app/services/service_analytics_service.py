"""
Service Analytics Service

Provides comprehensive analytics and insights for Service CRM including:
- Job completion metrics
- Technician performance analytics
- Customer satisfaction tracking
- Job volume trends
- SLA compliance monitoring
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case, extract
from app.models import (
    InstallationJob, InstallationTask, CompletionRecord, CustomerFeedback,
    ServiceClosure, User, Customer,
    Ticket, SLAPolicy, SLATracking
)
from app.schemas.service_analytics import (
    MetricType, ReportPeriod, JobCompletionMetrics, TechnicianPerformanceMetrics,
    CustomerSatisfactionMetrics, JobVolumeMetrics, SLAComplianceMetrics,
    AnalyticsDashboard, TimeSeriesDataPoint
)
from app.core.tenant import TenantQueryMixin
import logging

logger = logging.getLogger(__name__)


class ServiceAnalyticsService:
    """Service for calculating Service CRM analytics and insights"""
    
    def __init__(self, db: Session, organization_id: int):
        """
        Initialize analytics service for a specific organization
        
        Args:
            db: Database session
            organization_id: Organization ID for multi-tenant isolation
        """
        self.db = db
        self.organization_id = organization_id
    
    def get_date_range(self, period: ReportPeriod, start_date: Optional[date] = None, 
                      end_date: Optional[date] = None) -> Tuple[date, date]:
        """
        Calculate date range based on period or custom dates
        
        Args:
            period: Predefined period
            start_date: Custom start date
            end_date: Custom end date
            
        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()
        
        if period == ReportPeriod.CUSTOM and start_date and end_date:
            return start_date, end_date
        elif period == ReportPeriod.TODAY:
            return today, today
        elif period == ReportPeriod.WEEK:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif period == ReportPeriod.MONTH:
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return start, end
        elif period == ReportPeriod.QUARTER:
            quarter = (today.month - 1) // 3 + 1
            start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            if quarter == 4:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=quarter * 3 + 1, day=1) - timedelta(days=1)
            return start, end
        elif period == ReportPeriod.YEAR:
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return start, end
        else:
            # Default to current month
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return start, end
    
    def get_job_completion_metrics(self, start_date: date, end_date: date,
                                 technician_id: Optional[int] = None,
                                 customer_id: Optional[int] = None) -> JobCompletionMetrics:
        """
        Calculate job completion metrics for the specified period
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            technician_id: Optional filter by technician
            customer_id: Optional filter by customer
            
        Returns:
            JobCompletionMetrics object
        """
        logger.info(f"Calculating job completion metrics for org {self.organization_id}")
        
        # Base query for jobs in the date range
        query = TenantQueryMixin.filter_by_tenant(
            self.db.query(InstallationJob), InstallationJob, self.organization_id
        ).filter(
            InstallationJob.created_at >= start_date,
            InstallationJob.created_at <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.filter(InstallationJob.assigned_technician_id == technician_id)
        if customer_id:
            query = query.filter(InstallationJob.customer_id == customer_id)
        
        # Get all jobs
        jobs = query.all()
        total_jobs = len(jobs)
        
        if total_jobs == 0:
            return JobCompletionMetrics(
                total_jobs=0,
                completed_jobs=0,
                pending_jobs=0,
                cancelled_jobs=0,
                completion_rate=0.0,
                on_time_completion_rate=0.0,
                jobs_by_status={},
                completion_trend=[]
            )
        
        # Calculate status counts
        status_counts = {}
        completed_jobs = 0
        pending_jobs = 0
        cancelled_jobs = 0
        total_completion_time = 0
        completed_count_for_time = 0
        on_time_count = 0
        
        for job in jobs:
            status = job.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status == "completed":
                completed_jobs += 1
                
                # Calculate completion time if both start and end times exist
                if job.actual_start_time and job.actual_end_time:
                    completion_time = (job.actual_end_time - job.actual_start_time).total_seconds() / 3600
                    total_completion_time += completion_time
                    completed_count_for_time += 1
                
                # Check if completed on time (scheduled_date vs actual_end_time)
                if job.scheduled_date and job.actual_end_time:
                    # Consider on-time if completed within the scheduled day
                    scheduled_date_end = job.scheduled_date.date() + timedelta(days=1)
                    if job.actual_end_time.date() <= scheduled_date_end:
                        on_time_count += 1
                        
            elif status in ["scheduled", "in_progress", "rescheduled"]:
                pending_jobs += 1
            elif status == "cancelled":
                cancelled_jobs += 1
        
        completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        average_completion_time = (total_completion_time / completed_count_for_time) if completed_count_for_time > 0 else None
        on_time_completion_rate = (on_time_count / completed_jobs * 100) if completed_jobs > 0 else 0
        
        # Generate completion trend (daily completion counts)
        completion_trend = self._get_completion_trend(start_date, end_date, technician_id, customer_id)
        
        return JobCompletionMetrics(
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            pending_jobs=pending_jobs,
            cancelled_jobs=cancelled_jobs,
            completion_rate=completion_rate,
            average_completion_time_hours=average_completion_time,
            on_time_completion_rate=on_time_completion_rate,
            jobs_by_status=status_counts,
            completion_trend=completion_trend
        )
    
    def get_technician_performance_metrics(self, start_date: date, end_date: date) -> List[TechnicianPerformanceMetrics]:
        """
        Calculate performance metrics for all technicians
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of TechnicianPerformanceMetrics objects
        """
        logger.info(f"Calculating technician performance metrics for org {self.organization_id}")
        
        # Get all technicians who had jobs in the period
        technician_query = self.db.query(
            User.id,
            User.full_name,
            func.count(InstallationJob.id).label('total_jobs'),
            func.sum(case((InstallationJob.status == 'completed', 1), else_=0)).label('completed_jobs'),
            func.sum(case((InstallationJob.status == 'in_progress', 1), else_=0)).label('in_progress_jobs'),
            func.avg(
                case(
                    (
                        and_(
                            InstallationJob.actual_start_time.isnot(None),
                            InstallationJob.actual_end_time.isnot(None)
                        ),
                        func.extract('epoch', InstallationJob.actual_end_time - InstallationJob.actual_start_time) / 3600
                    ),
                    else_=None
                )
            ).label('avg_completion_time')
        ).join(
            InstallationJob, User.id == InstallationJob.assigned_technician_id
        ).filter(
            InstallationJob.organization_id == self.organization_id,
            InstallationJob.created_at >= start_date,
            InstallationJob.created_at <= end_date + timedelta(days=1)
        ).group_by(User.id, User.full_name)
        
        technician_data = technician_query.all()
        
        performance_metrics = []
        
        for tech_data in technician_data:
            technician_id = tech_data.id
            
            # Get average customer rating for this technician
            avg_rating_query = self.db.query(
                func.avg(CustomerFeedback.technician_rating)
            ).join(
                InstallationJob, CustomerFeedback.installation_job_id == InstallationJob.id
            ).filter(
                InstallationJob.organization_id == self.organization_id,
                InstallationJob.assigned_technician_id == technician_id,
                CustomerFeedback.submitted_at >= start_date,
                CustomerFeedback.submitted_at <= end_date + timedelta(days=1),
                CustomerFeedback.technician_rating.isnot(None)
            )
            
            avg_rating = avg_rating_query.scalar()
            
            # Calculate utilization rate (simplified: completed jobs / total possible working days)
            working_days = (end_date - start_date).days + 1
            completed_jobs = tech_data.completed_jobs or 0
            utilization_rate = min((completed_jobs / max(working_days, 1)) * 100, 100)
            
            # Calculate efficiency score (combination of completion rate and customer satisfaction)
            completion_rate = (completed_jobs / tech_data.total_jobs * 100) if tech_data.total_jobs > 0 else 0
            rating_score = (avg_rating / 5 * 100) if avg_rating else 50  # Default to 50% if no ratings
            efficiency_score = (completion_rate * 0.7 + rating_score * 0.3)  # Weighted average
            
            performance_metrics.append(TechnicianPerformanceMetrics(
                technician_id=technician_id,
                technician_name=tech_data.full_name or f"Technician {technician_id}",
                total_jobs_assigned=tech_data.total_jobs,
                jobs_completed=completed_jobs,
                jobs_in_progress=tech_data.in_progress_jobs or 0,
                average_completion_time_hours=tech_data.avg_completion_time,
                customer_rating_average=avg_rating,
                utilization_rate=utilization_rate,
                efficiency_score=efficiency_score
            ))
        
        return performance_metrics
    
    def get_customer_satisfaction_metrics(self, start_date: date, end_date: date,
                                        technician_id: Optional[int] = None,
                                        customer_id: Optional[int] = None) -> CustomerSatisfactionMetrics:
        """
        Calculate customer satisfaction metrics
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            technician_id: Optional filter by technician
            customer_id: Optional filter by customer
            
        Returns:
            CustomerSatisfactionMetrics object
        """
        logger.info(f"Calculating customer satisfaction metrics for org {self.organization_id}")
        
        # Base query for feedback in the date range
        query = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerFeedback), CustomerFeedback, self.organization_id
        ).filter(
            CustomerFeedback.submitted_at >= start_date,
            CustomerFeedback.submitted_at <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.join(InstallationJob).filter(
                InstallationJob.assigned_technician_id == technician_id
            )
        if customer_id:
            query = query.filter(CustomerFeedback.customer_id == customer_id)
        
        feedback_records = query.all()
        total_feedback = len(feedback_records)
        
        if total_feedback == 0:
            return CustomerSatisfactionMetrics(
                total_feedback_received=0,
                average_overall_rating=0.0,
                satisfaction_distribution={},
                satisfaction_trend=[]
            )
        
        # Calculate averages
        overall_ratings = [f.overall_rating for f in feedback_records if f.overall_rating]
        service_quality_ratings = [f.service_quality_rating for f in feedback_records if f.service_quality_rating]
        technician_ratings = [f.technician_rating for f in feedback_records if f.technician_rating]
        timeliness_ratings = [f.timeliness_rating for f in feedback_records if f.timeliness_rating]
        communication_ratings = [f.communication_rating for f in feedback_records if f.communication_rating]
        
        avg_overall = sum(overall_ratings) / len(overall_ratings) if overall_ratings else 0
        avg_service_quality = sum(service_quality_ratings) / len(service_quality_ratings) if service_quality_ratings else None
        avg_technician = sum(technician_ratings) / len(technician_ratings) if technician_ratings else None
        avg_timeliness = sum(timeliness_ratings) / len(timeliness_ratings) if timeliness_ratings else None
        avg_communication = sum(communication_ratings) / len(communication_ratings) if communication_ratings else None
        
        # Calculate satisfaction distribution
        satisfaction_distribution = {}
        for rating in overall_ratings:
            if rating >= 4:
                category = "satisfied"
            elif rating >= 3:
                category = "neutral"
            else:
                category = "dissatisfied"
            satisfaction_distribution[category] = satisfaction_distribution.get(category, 0) + 1
        
        # Calculate NPS score and recommendation rate
        nps_score = None
        recommendation_rate = None
        
        recommendations = [f.would_recommend for f in feedback_records if f.would_recommend is not None]
        if recommendations:
            recommendation_rate = sum(recommendations) / len(recommendations) * 100
            
            # NPS calculation (simplified: 4-5 stars = promoters, 1-2 stars = detractors)
            promoters = len([r for r in overall_ratings if r >= 4])
            detractors = len([r for r in overall_ratings if r <= 2])
            nps_score = ((promoters - detractors) / len(overall_ratings)) * 100 if overall_ratings else 0
        
        # Generate satisfaction trend
        satisfaction_trend = self._get_satisfaction_trend(start_date, end_date, technician_id, customer_id)
        
        return CustomerSatisfactionMetrics(
            total_feedback_received=total_feedback,
            average_overall_rating=avg_overall,
            average_service_quality=avg_service_quality,
            average_technician_rating=avg_technician,
            average_timeliness_rating=avg_timeliness,
            average_communication_rating=avg_communication,
            satisfaction_distribution=satisfaction_distribution,
            nps_score=nps_score,
            recommendation_rate=recommendation_rate,
            satisfaction_trend=satisfaction_trend
        )
    
    def get_job_volume_metrics(self, start_date: date, end_date: date,
                             technician_id: Optional[int] = None,
                             customer_id: Optional[int] = None) -> JobVolumeMetrics:
        """
        Calculate job volume metrics
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            technician_id: Optional filter by technician
            customer_id: Optional filter by customer
            
        Returns:
            JobVolumeMetrics object
        """
        logger.info(f"Calculating job volume metrics for org {self.organization_id}")
        
        # Base query for jobs in the date range
        query = TenantQueryMixin.filter_by_tenant(
            self.db.query(InstallationJob), InstallationJob, self.organization_id
        ).filter(
            InstallationJob.created_at >= start_date,
            InstallationJob.created_at <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.filter(InstallationJob.assigned_technician_id == technician_id)
        if customer_id:
            query = query.filter(InstallationJob.customer_id == customer_id)
        
        jobs = query.all()
        total_jobs = len(jobs)
        
        if total_jobs == 0:
            return JobVolumeMetrics(
                total_jobs=0,
                jobs_per_day_average=0.0,
                volume_trend=[],
                jobs_by_priority={},
                jobs_by_customer=[]
            )
        
        # Calculate jobs per day average
        days = (end_date - start_date).days + 1
        jobs_per_day_average = total_jobs / days
        
        # Find peak day
        daily_counts = {}
        for job in jobs:
            job_date = job.created_at.date()
            daily_counts[job_date] = daily_counts.get(job_date, 0) + 1
        
        peak_day = None
        peak_day_count = 0
        if daily_counts:
            peak_day = max(daily_counts, key=daily_counts.get)
            peak_day_count = daily_counts[peak_day]
        
        # Calculate jobs by priority
        jobs_by_priority = {}
        for job in jobs:
            priority = job.priority
            jobs_by_priority[priority] = jobs_by_priority.get(priority, 0) + 1
        
        # Calculate top customers by job volume
        customer_counts = {}
        for job in jobs:
            customer_id = job.customer_id
            customer_counts[customer_id] = customer_counts.get(customer_id, 0) + 1
        
        # Get customer names for top customers
        top_customer_ids = sorted(customer_counts.keys(), key=lambda x: customer_counts[x], reverse=True)[:10]
        jobs_by_customer = []
        
        if top_customer_ids:
            customers = self.db.query(Customer).filter(Customer.id.in_(top_customer_ids)).all()
            customer_names = {c.id: c.name for c in customers}
            
            jobs_by_customer = [
                {
                    "customer_id": customer_id,
                    "customer_name": customer_names.get(customer_id, f"Customer {customer_id}"),
                    "job_count": customer_counts[customer_id]
                }
                for customer_id in top_customer_ids
            ]
        
        # Generate volume trend
        volume_trend = self._get_volume_trend(start_date, end_date, technician_id, customer_id)
        
        return JobVolumeMetrics(
            total_jobs=total_jobs,
            jobs_per_day_average=jobs_per_day_average,
            peak_day=peak_day,
            peak_day_count=peak_day_count,
            volume_trend=volume_trend,
            jobs_by_priority=jobs_by_priority,
            jobs_by_customer=jobs_by_customer
        )
    
    def get_sla_compliance_metrics(self, start_date: date, end_date: date,
                                 technician_id: Optional[int] = None,
                                 customer_id: Optional[int] = None) -> SLAComplianceMetrics:
        """
        Calculate SLA compliance metrics
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            technician_id: Optional filter by technician
            customer_id: Optional filter by customer
            
        Returns:
            SLAComplianceMetrics object
        """
        logger.info(f"Calculating SLA compliance metrics for org {self.organization_id}")
        
        # Note: This requires SLA tracking data from the existing SLA module
        # For now, provide a basic implementation that can be enhanced
        
        return SLAComplianceMetrics(
            total_jobs_with_sla=0,
            sla_met_count=0,
            sla_breached_count=0,
            overall_compliance_rate=0.0,
            compliance_by_priority={},
            compliance_trend=[],
            breach_reasons={}
        )
    
    def get_analytics_dashboard(self, period: ReportPeriod = ReportPeriod.MONTH,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              technician_id: Optional[int] = None,
                              customer_id: Optional[int] = None) -> AnalyticsDashboard:
        """
        Generate complete analytics dashboard
        
        Args:
            period: Report period
            start_date: Custom start date
            end_date: Custom end date
            technician_id: Optional filter by technician
            customer_id: Optional filter by customer
            
        Returns:
            AnalyticsDashboard object with all metrics
        """
        logger.info(f"Generating analytics dashboard for org {self.organization_id}")
        
        # Calculate date range
        date_start, date_end = self.get_date_range(period, start_date, end_date)
        
        # Get all metrics
        job_completion = self.get_job_completion_metrics(date_start, date_end, technician_id, customer_id)
        technician_performance = self.get_technician_performance_metrics(date_start, date_end)
        customer_satisfaction = self.get_customer_satisfaction_metrics(date_start, date_end, technician_id, customer_id)
        job_volume = self.get_job_volume_metrics(date_start, date_end, technician_id, customer_id)
        sla_compliance = self.get_sla_compliance_metrics(date_start, date_end, technician_id, customer_id)
        
        return AnalyticsDashboard(
            organization_id=self.organization_id,
            report_period=period,
            start_date=date_start,
            end_date=date_end,
            job_completion=job_completion,
            technician_performance=technician_performance,
            customer_satisfaction=customer_satisfaction,
            job_volume=job_volume,
            sla_compliance=sla_compliance,
            generated_at=datetime.utcnow()
        )
    
    def _get_completion_trend(self, start_date: date, end_date: date,
                            technician_id: Optional[int] = None,
                            customer_id: Optional[int] = None) -> List[TimeSeriesDataPoint]:
        """Generate daily completion trend data"""
        query = self.db.query(
            func.date(InstallationJob.actual_end_time).label('completion_date'),
            func.count(InstallationJob.id).label('completion_count')
        ).filter(
            InstallationJob.organization_id == self.organization_id,
            InstallationJob.status == 'completed',
            InstallationJob.actual_end_time >= start_date,
            InstallationJob.actual_end_time <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.filter(InstallationJob.assigned_technician_id == technician_id)
        if customer_id:
            query = query.filter(InstallationJob.customer_id == customer_id)
        
        results = query.group_by(func.date(InstallationJob.actual_end_time)).all()
        
        # Create data points for all dates in range
        data_points = []
        current_date = start_date
        completion_data = {result.completion_date: result.completion_count for result in results}
        
        while current_date <= end_date:
            count = completion_data.get(current_date, 0)
            data_points.append(TimeSeriesDataPoint(
                date=current_date,
                value=count,
                label=f"{count} completed"
            ))
            current_date += timedelta(days=1)
        
        return data_points
    
    def _get_satisfaction_trend(self, start_date: date, end_date: date,
                              technician_id: Optional[int] = None,
                              customer_id: Optional[int] = None) -> List[TimeSeriesDataPoint]:
        """Generate daily satisfaction trend data"""
        query = self.db.query(
            func.date(CustomerFeedback.submitted_at).label('feedback_date'),
            func.avg(CustomerFeedback.overall_rating).label('avg_rating')
        ).filter(
            CustomerFeedback.organization_id == self.organization_id,
            CustomerFeedback.submitted_at >= start_date,
            CustomerFeedback.submitted_at <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.join(InstallationJob).filter(
                InstallationJob.assigned_technician_id == technician_id
            )
        if customer_id:
            query = query.filter(CustomerFeedback.customer_id == customer_id)
        
        results = query.group_by(func.date(CustomerFeedback.submitted_at)).all()
        
        # Create data points
        data_points = []
        for result in results:
            if result.avg_rating is not None:
                data_points.append(TimeSeriesDataPoint(
                    date=result.feedback_date,
                    value=round(result.avg_rating, 2),
                    label=f"{result.avg_rating:.2f} avg rating"
                ))
        
        return data_points
    
    def _get_volume_trend(self, start_date: date, end_date: date,
                         technician_id: Optional[int] = None,
                         customer_id: Optional[int] = None) -> List[TimeSeriesDataPoint]:
        """Generate daily job volume trend data"""
        query = self.db.query(
            func.date(InstallationJob.created_at).label('creation_date'),
            func.count(InstallationJob.id).label('job_count')
        ).filter(
            InstallationJob.organization_id == self.organization_id,
            InstallationJob.created_at >= start_date,
            InstallationJob.created_at <= end_date + timedelta(days=1)
        )
        
        if technician_id:
            query = query.filter(InstallationJob.assigned_technician_id == technician_id)
        if customer_id:
            query = query.filter(InstallationJob.customer_id == customer_id)
        
        results = query.group_by(func.date(InstallationJob.created_at)).all()
        
        # Create data points for all dates in range
        data_points = []
        current_date = start_date
        volume_data = {result.creation_date: result.job_count for result in results}
        
        while current_date <= end_date:
            count = volume_data.get(current_date, 0)
            data_points.append(TimeSeriesDataPoint(
                date=current_date,
                value=count,
                label=f"{count} jobs"
            ))
            current_date += timedelta(days=1)
        
        return data_points


def get_service_analytics_service(db: Session, organization_id: int) -> ServiceAnalyticsService:
    """Dependency function to get ServiceAnalyticsService instance"""
    return ServiceAnalyticsService(db, organization_id)