# app/services/dispatch_service.py

"""
Dispatch service for managing dispatch orders and installation jobs
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timezone
import logging

from app.models import DispatchOrder, DispatchItem, InstallationJob, InstallationTask, CompletionRecord, User
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)


class DispatchNumberService:
    """Service for generating dispatch and installation job numbers"""
    
    @staticmethod
    def generate_dispatch_order_number(db: Session, organization_id: int) -> str:
        """Generate a unique dispatch order number"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        prefix = "DO"
        
        # Get the latest dispatch order number for this prefix, fiscal year, and organization
        latest_order = db.query(DispatchOrder).filter(
            DispatchOrder.organization_id == organization_id,
            DispatchOrder.order_number.like(f"{prefix}/{fiscal_year}/%")
        ).order_by(DispatchOrder.order_number.desc()).first()
        
        if latest_order:
            # Extract sequence number and increment
            try:
                last_sequence = int(latest_order.order_number.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        return f"{prefix}/{fiscal_year}/{next_sequence:05d}"
    
    @staticmethod
    def generate_installation_job_number(db: Session, organization_id: int) -> str:
        """Generate a unique installation job number"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        prefix = "IJ"
        
        # Get the latest installation job number for this prefix, fiscal year, and organization
        latest_job = db.query(InstallationJob).filter(
            InstallationJob.organization_id == organization_id,
            InstallationJob.job_number.like(f"{prefix}/{fiscal_year}/%")
        ).order_by(InstallationJob.job_number.desc()).first()
        
        if latest_job:
            # Extract sequence number and increment
            try:
                last_sequence = int(latest_job.job_number.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        return f"{prefix}/{fiscal_year}/{next_sequence:05d}"


class DispatchService:
    """Service for dispatch order business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_dispatch_order(
        self,
        organization_id: int,
        customer_id: int,
        delivery_address: str,
        items: List[dict],
        created_by_id: int,
        ticket_id: Optional[int] = None,
        **kwargs
    ) -> DispatchOrder:
        """Create a new dispatch order with items"""
        
        # Generate order number
        order_number = DispatchNumberService.generate_dispatch_order_number(
            self.db, organization_id
        )
        
        # Create dispatch order
        dispatch_order = DispatchOrder(
            organization_id=organization_id,
            order_number=order_number,
            customer_id=customer_id,
            ticket_id=ticket_id,
            delivery_address=delivery_address,
            created_by_id=created_by_id,
            **kwargs
        )
        
        self.db.add(dispatch_order)
        self.db.flush()  # Get the ID
        
        # Create dispatch items
        for item_data in items:
            dispatch_item = DispatchItem(
                dispatch_order_id=dispatch_order.id,
                **item_data
            )
            self.db.add(dispatch_item)
        
        self.db.commit()
        self.db.refresh(dispatch_order)
        
        logger.info(f"Created dispatch order {order_number} for organization {organization_id}")
        return dispatch_order
    
    def update_dispatch_status(
        self,
        dispatch_order_id: int,
        status: str,
        updated_by_id: int,
        **kwargs
    ) -> DispatchOrder:
        """Update dispatch order status"""
        
        dispatch_order = self.db.query(DispatchOrder).filter(
            DispatchOrder.id == dispatch_order_id
        ).first()
        
        if not dispatch_order:
            raise ValueError(f"Dispatch order {dispatch_order_id} not found")
        
        dispatch_order.status = status
        dispatch_order.updated_by_id = updated_by_id
        
        # Update specific date fields based on status
        if status == "in_transit" and not dispatch_order.dispatch_date:
            dispatch_order.dispatch_date = datetime.now(timezone.utc)
        elif status == "delivered" and not dispatch_order.actual_delivery_date:
            dispatch_order.actual_delivery_date = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(dispatch_order, key):
                setattr(dispatch_order, key, value)
        
        self.db.commit()
        self.db.refresh(dispatch_order)
        
        logger.info(f"Updated dispatch order {dispatch_order.order_number} status to {status}")
        return dispatch_order


class InstallationJobService:
    """Service for installation job business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_installation_job(
        self,
        organization_id: int,
        dispatch_order_id: int,
        customer_id: int,
        installation_address: str,
        created_by_id: int,
        **kwargs
    ) -> InstallationJob:
        """Create a new installation job"""
        
        # Generate job number
        job_number = DispatchNumberService.generate_installation_job_number(
            self.db, organization_id
        )
        
        # Create installation job
        installation_job = InstallationJob(
            organization_id=organization_id,
            job_number=job_number,
            dispatch_order_id=dispatch_order_id,
            customer_id=customer_id,
            installation_address=installation_address,
            created_by_id=created_by_id,
            **kwargs
        )
        
        self.db.add(installation_job)
        self.db.commit()
        self.db.refresh(installation_job)
        
        logger.info(f"Created installation job {job_number} for organization {organization_id}")
        return installation_job
    
    def assign_technician(
        self,
        job_id: int,
        technician_id: int,
        updated_by_id: int
    ) -> InstallationJob:
        """Assign a technician to an installation job"""
        
        job = self.db.query(InstallationJob).filter(
            InstallationJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError(f"Installation job {job_id} not found")
        
        # Verify technician exists and belongs to the same organization
        technician = self.db.query(User).filter(
            User.id == technician_id,
            User.organization_id == job.organization_id
        ).first()
        
        if not technician:
            raise ValueError(f"Technician {technician_id} not found in organization")
        
        job.assigned_technician_id = technician_id
        job.updated_by_id = updated_by_id
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Assigned technician {technician_id} to installation job {job.job_number}")
        return job
    
    def update_job_status(
        self,
        job_id: int,
        status: str,
        updated_by_id: int,
        **kwargs
    ) -> InstallationJob:
        """Update installation job status"""
        
        job = self.db.query(InstallationJob).filter(
            InstallationJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError(f"Installation job {job_id} not found")
        
        job.status = status
        job.updated_by_id = updated_by_id
        
        # Update specific timestamp fields based on status
        if status == "in_progress" and not job.actual_start_time:
            job.actual_start_time = datetime.now(timezone.utc)
        elif status == "completed" and not job.actual_end_time:
            job.actual_end_time = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Updated installation job {job.job_number} status to {status}")
        return job


class InstallationTaskService:
    """Service for installation task business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_task_number(self, organization_id: int) -> str:
        """Generate a unique task number"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        prefix = "IT"
        
        # Import here to avoid circular imports
        from app.models.base import InstallationTask
        
        # Get the latest task number for this prefix, fiscal year, and organization
        latest_task = self.db.query(InstallationTask).filter(
            InstallationTask.organization_id == organization_id,
            InstallationTask.task_number.like(f"{prefix}/{fiscal_year}/%")
        ).order_by(InstallationTask.task_number.desc()).first()
        
        if latest_task:
            # Extract sequence number and increment
            try:
                last_sequence = int(latest_task.task_number.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        return f"{prefix}/{fiscal_year}/{next_sequence:05d}"
    
    def create_installation_task(
        self,
        organization_id: int,
        installation_job_id: int,
        title: str,
        created_by_id: int,
        **kwargs
    ):
        """Create a new installation task"""
        from app.models.base import InstallationTask
        
        # Generate task number
        task_number = self.generate_task_number(organization_id)
        
        # Create installation task
        task = InstallationTask(
            organization_id=organization_id,
            installation_job_id=installation_job_id,
            task_number=task_number,
            title=title,
            created_by_id=created_by_id,
            **kwargs
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Created installation task {task.task_number} for job {installation_job_id}")
        return task
    
    def update_task_status(
        self,
        task_id: int,
        status: str,
        updated_by_id: int,
        **kwargs
    ):
        """Update installation task status with automatic timing"""
        from app.models.base import InstallationTask
        
        task = self.db.query(InstallationTask).filter(
            InstallationTask.id == task_id
        ).first()
        
        if not task:
            raise ValueError(f"Installation task {task_id} not found")
        
        # Update status
        task.status = status
        task.updated_by_id = updated_by_id
        
        # Auto-update timing based on status
        if status == "in_progress" and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        elif status == "completed" and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Updated installation task {task.task_number} status to {status}")
        return task
    
    def assign_technician(
        self,
        task_id: int,
        technician_id: int,
        updated_by_id: int
    ):
        """Assign a technician to an installation task"""
        from app.models.base import InstallationTask
        
        task = self.db.query(InstallationTask).filter(
            InstallationTask.id == task_id
        ).first()
        
        if not task:
            raise ValueError(f"Installation task {task_id} not found")
        
        # Verify technician belongs to same organization
        technician = self.db.query(User).filter(
            User.id == technician_id,
            User.organization_id == task.organization_id
        ).first()
        
        if not technician:
            raise ValueError(f"Technician {technician_id} not found in organization")
        
        task.assigned_technician_id = technician_id
        task.updated_by_id = updated_by_id
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Assigned technician {technician_id} to task {task.task_number}")
        return task


class CompletionRecordService:
    """Service for completion record business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_completion_record(
        self,
        organization_id: int,
        installation_job_id: int,
        completed_by_id: int,
        completion_date: datetime,
        work_performed: str,
        **kwargs
    ):
        """Create a completion record for an installation job"""
        from app.models.base import CompletionRecord, InstallationJob
        
        # Verify installation job exists and belongs to organization
        job = self.db.query(InstallationJob).filter(
            InstallationJob.id == installation_job_id,
            InstallationJob.organization_id == organization_id
        ).first()
        
        if not job:
            raise ValueError(f"Installation job {installation_job_id} not found")
        
        # Verify technician is assigned to the job
        if job.assigned_technician_id != completed_by_id:
            raise ValueError("Only the assigned technician can mark the job as complete")
        
        # Check if completion record already exists
        existing_record = self.db.query(CompletionRecord).filter(
            CompletionRecord.installation_job_id == installation_job_id
        ).first()
        
        if existing_record:
            raise ValueError("Completion record already exists for this job")
        
        # Calculate duration if start and end times provided
        total_duration_minutes = None
        if kwargs.get('actual_start_time') and kwargs.get('actual_end_time'):
            start_time = kwargs['actual_start_time']
            end_time = kwargs['actual_end_time']
            duration = end_time - start_time
            total_duration_minutes = int(duration.total_seconds() / 60)
        
        # Create completion record
        completion_record = CompletionRecord(
            organization_id=organization_id,
            installation_job_id=installation_job_id,
            completed_by_id=completed_by_id,
            completion_date=completion_date,
            work_performed=work_performed,
            total_duration_minutes=total_duration_minutes,
            **kwargs
        )
        
        self.db.add(completion_record)
        
        # Update installation job status to completed
        job.status = "completed"
        if completion_record.actual_start_time:
            job.actual_start_time = completion_record.actual_start_time
        if completion_record.actual_end_time:
            job.actual_end_time = completion_record.actual_end_time
        if completion_record.work_performed:
            job.completion_notes = completion_record.work_performed
        if completion_record.customer_feedback_notes:
            job.customer_feedback = completion_record.customer_feedback_notes
        if completion_record.customer_rating:
            job.customer_rating = completion_record.customer_rating
        
        self.db.commit()
        self.db.refresh(completion_record)
        
        logger.info(f"Created completion record for installation job {job.job_number}")
        
        # TODO: Trigger customer feedback workflow here
        # This is the integration point for the next phase
        self._trigger_customer_feedback_workflow(completion_record)
        
        return completion_record
    
    def update_completion_record(
        self,
        completion_record_id: int,
        organization_id: int,
        **kwargs
    ):
        """Update a completion record"""
        from app.models.base import CompletionRecord
        
        completion_record = self.db.query(CompletionRecord).filter(
            CompletionRecord.id == completion_record_id,
            CompletionRecord.organization_id == organization_id
        ).first()
        
        if not completion_record:
            raise ValueError(f"Completion record {completion_record_id} not found")
        
        # Recalculate duration if times are updated
        if 'actual_start_time' in kwargs or 'actual_end_time' in kwargs:
            start_time = kwargs.get('actual_start_time', completion_record.actual_start_time)
            end_time = kwargs.get('actual_end_time', completion_record.actual_end_time)
            
            if start_time and end_time:
                duration = end_time - start_time
                kwargs['total_duration_minutes'] = int(duration.total_seconds() / 60)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(completion_record, key):
                setattr(completion_record, key, value)
        
        self.db.commit()
        self.db.refresh(completion_record)
        
        logger.info(f"Updated completion record {completion_record_id}")
        return completion_record
    
    def _trigger_customer_feedback_workflow(self, completion_record):
        """Trigger customer feedback workflow (now implemented)"""
        try:
            # Set feedback request flag
            completion_record.feedback_request_sent = True
            completion_record.feedback_request_sent_at = datetime.now(timezone.utc)
            self.db.commit()
            
            # Import here to avoid circular imports
            from app.services.email_service import EmailService
            
            # Send feedback request email to customer
            if hasattr(completion_record, 'installation_job') and completion_record.installation_job:
                job = completion_record.installation_job
                if hasattr(job, 'customer') and job.customer:
                    customer = job.customer
                    
                    # Create feedback request email
                    email_service = EmailService(self.db)
                    
                    feedback_url = f"/feedback/submit?job_id={job.id}&completion_id={completion_record.id}"
                    
                    email_body = f"""
                    Dear {customer.company_name or customer.contact_person},
                    
                    We hope you're satisfied with the service completed on {completion_record.completion_date.strftime('%Y-%m-%d')}.
                    
                    We would greatly appreciate your feedback to help us improve our services.
                    
                    Please click the link below to submit your feedback:
                    {feedback_url}
                    
                    Thank you for your time!
                    
                    Best regards,
                    Service Team
                    """
                    
                    try:
                        email_service.send_email(
                            to_email=customer.email,
                            subject="Service Feedback Request",
                            body=email_body,
                            organization_id=completion_record.organization_id
                        )
                        logger.info(f"Feedback request email sent to customer {customer.id} for completion {completion_record.id}")
                    except Exception as e:
                        logger.error(f"Failed to send feedback request email: {e}")
                        # Don't fail the completion if email fails
            
            logger.info(f"Triggered customer feedback workflow for completion record {completion_record.id}")
            
        except Exception as e:
            logger.error(f"Error triggering customer feedback workflow: {e}")
            # Don't fail the completion if feedback workflow fails