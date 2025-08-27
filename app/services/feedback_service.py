# app/services/feedback_service.py

"""
Service layer for customer feedback and service closure workflow
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status
from datetime import datetime
import json
import logging

from app.models import (
    CustomerFeedback, ServiceClosure, InstallationJob, CompletionRecord,
    Customer, User, Organization
)
from app.schemas.feedback import (
    CustomerFeedbackCreate, CustomerFeedbackUpdate, CustomerFeedbackFilter,
    ServiceClosureCreate, ServiceClosureUpdate, ServiceClosureFilter,
    FeedbackStatus, ClosureStatus, ClosureReason
)

logger = logging.getLogger(__name__)


class CustomerFeedbackService:
    """Service for customer feedback operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_feedback(
        self, 
        feedback_data: CustomerFeedbackCreate, 
        organization_id: int
    ) -> CustomerFeedback:
        """Create a new customer feedback record"""
        
        # Validate installation job exists and belongs to organization
        installation_job = self.db.query(InstallationJob).filter(
            and_(
                InstallationJob.id == feedback_data.installation_job_id,
                InstallationJob.organization_id == organization_id
            )
        ).first()
        
        if not installation_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation job not found"
            )
        
        # Validate customer belongs to organization
        customer = self.db.query(Customer).filter(
            and_(
                Customer.id == feedback_data.customer_id,
                Customer.organization_id == organization_id
            )
        ).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Check if feedback already exists for this job
        existing_feedback = self.db.query(CustomerFeedback).filter(
            and_(
                CustomerFeedback.installation_job_id == feedback_data.installation_job_id,
                CustomerFeedback.customer_id == feedback_data.customer_id,
                CustomerFeedback.organization_id == organization_id
            )
        ).first()
        
        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback already exists for this job"
            )
        
        # Serialize survey responses to JSON if provided
        survey_responses_json = None
        if feedback_data.survey_responses:
            survey_responses_json = json.dumps(feedback_data.survey_responses)
        
        # Create feedback record
        feedback = CustomerFeedback(
            organization_id=organization_id,
            installation_job_id=feedback_data.installation_job_id,
            customer_id=feedback_data.customer_id,
            completion_record_id=feedback_data.completion_record_id,
            overall_rating=feedback_data.overall_rating,
            service_quality_rating=feedback_data.service_quality_rating,
            technician_rating=feedback_data.technician_rating,
            timeliness_rating=feedback_data.timeliness_rating,
            communication_rating=feedback_data.communication_rating,
            feedback_comments=feedback_data.feedback_comments,
            improvement_suggestions=feedback_data.improvement_suggestions,
            survey_responses=survey_responses_json,
            would_recommend=feedback_data.would_recommend,
            satisfaction_level=feedback_data.satisfaction_level,
            follow_up_preferred=feedback_data.follow_up_preferred,
            preferred_contact_method=feedback_data.preferred_contact_method,
            feedback_status=FeedbackStatus.SUBMITTED
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        # Update completion record feedback status if linked
        if feedback_data.completion_record_id:
            completion_record = self.db.query(CompletionRecord).filter(
                CompletionRecord.id == feedback_data.completion_record_id
            ).first()
            if completion_record:
                completion_record.feedback_request_sent = True
                completion_record.feedback_request_sent_at = datetime.utcnow()
                self.db.commit()
        
        logger.info(f"Created customer feedback {feedback.id} for job {feedback_data.installation_job_id}")
        return feedback
    
    def get_feedback_by_id(self, feedback_id: int, organization_id: int) -> Optional[CustomerFeedback]:
        """Get feedback by ID"""
        return self.db.query(CustomerFeedback).filter(
            and_(
                CustomerFeedback.id == feedback_id,
                CustomerFeedback.organization_id == organization_id
            )
        ).first()
    
    def get_feedback_list(
        self, 
        organization_id: int, 
        filter_params: CustomerFeedbackFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomerFeedback]:
        """Get list of feedback with filters"""
        
        query = self.db.query(CustomerFeedback).filter(
            CustomerFeedback.organization_id == organization_id
        )
        
        # Apply filters
        if filter_params.feedback_status:
            query = query.filter(CustomerFeedback.feedback_status == filter_params.feedback_status)
        
        if filter_params.overall_rating:
            query = query.filter(CustomerFeedback.overall_rating == filter_params.overall_rating)
        
        if filter_params.customer_id:
            query = query.filter(CustomerFeedback.customer_id == filter_params.customer_id)
        
        if filter_params.installation_job_id:
            query = query.filter(CustomerFeedback.installation_job_id == filter_params.installation_job_id)
        
        if filter_params.satisfaction_level:
            query = query.filter(CustomerFeedback.satisfaction_level == filter_params.satisfaction_level)
        
        if filter_params.from_date:
            query = query.filter(CustomerFeedback.submitted_at >= filter_params.from_date)
        
        if filter_params.to_date:
            query = query.filter(CustomerFeedback.submitted_at <= filter_params.to_date)
        
        return query.order_by(desc(CustomerFeedback.submitted_at)).offset(skip).limit(limit).all()
    
    def update_feedback(
        self, 
        feedback_id: int, 
        feedback_update: CustomerFeedbackUpdate, 
        organization_id: int,
        updated_by_id: Optional[int] = None
    ) -> CustomerFeedback:
        """Update feedback record"""
        
        feedback = self.get_feedback_by_id(feedback_id, organization_id)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # Update fields
        update_data = feedback_update.model_dump(exclude_unset=True)
        
        # Handle survey responses serialization
        if 'survey_responses' in update_data and update_data['survey_responses']:
            update_data['survey_responses'] = json.dumps(update_data['survey_responses'])
        
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        # Set review information if status is being updated
        if feedback_update.feedback_status and updated_by_id:
            feedback.reviewed_by_id = updated_by_id
            feedback.reviewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(feedback)
        
        logger.info(f"Updated customer feedback {feedback_id}")
        return feedback


class ServiceClosureService:
    """Service for service closure workflow operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_closure(
        self, 
        closure_data: ServiceClosureCreate, 
        organization_id: int,
        created_by_id: int
    ) -> ServiceClosure:
        """Create a new service closure record"""
        
        # Validate installation job exists and belongs to organization
        installation_job = self.db.query(InstallationJob).filter(
            and_(
                InstallationJob.id == closure_data.installation_job_id,
                InstallationJob.organization_id == organization_id
            )
        ).first()
        
        if not installation_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation job not found"
            )
        
        # Check if closure already exists for this job
        existing_closure = self.db.query(ServiceClosure).filter(
            and_(
                ServiceClosure.installation_job_id == closure_data.installation_job_id,
                ServiceClosure.organization_id == organization_id
            )
        ).first()
        
        if existing_closure:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service closure already exists for this job"
            )
        
        # Check if completion record exists
        completion_record = None
        if closure_data.completion_record_id:
            completion_record = self.db.query(CompletionRecord).filter(
                CompletionRecord.id == closure_data.completion_record_id
            ).first()
        
        # Check if feedback exists and calculate metrics
        feedback_received = False
        minimum_rating_met = False
        if closure_data.customer_feedback_id:
            feedback = self.db.query(CustomerFeedback).filter(
                CustomerFeedback.id == closure_data.customer_feedback_id
            ).first()
            if feedback:
                feedback_received = True
                minimum_rating_met = feedback.overall_rating >= 3  # Configurable threshold
        
        # Create closure record
        closure = ServiceClosure(
            organization_id=organization_id,
            installation_job_id=closure_data.installation_job_id,
            completion_record_id=closure_data.completion_record_id,
            customer_feedback_id=closure_data.customer_feedback_id,
            closure_status=ClosureStatus.PENDING,
            closure_reason=closure_data.closure_reason,
            closure_notes=closure_data.closure_notes,
            requires_manager_approval=closure_data.requires_manager_approval,
            approval_notes=closure_data.approval_notes,
            final_closure_notes=closure_data.final_closure_notes,
            feedback_received=feedback_received,
            minimum_rating_met=minimum_rating_met,
            escalation_required=closure_data.escalation_required,
            escalation_reason=closure_data.escalation_reason,
            reopening_reason=closure_data.reopening_reason
        )
        
        self.db.add(closure)
        self.db.commit()
        self.db.refresh(closure)
        
        logger.info(f"Created service closure {closure.id} for job {closure_data.installation_job_id}")
        return closure
    
    def get_closure_by_id(self, closure_id: int, organization_id: int) -> Optional[ServiceClosure]:
        """Get closure by ID"""
        return self.db.query(ServiceClosure).filter(
            and_(
                ServiceClosure.id == closure_id,
                ServiceClosure.organization_id == organization_id
            )
        ).first()
    
    def get_closure_list(
        self, 
        organization_id: int, 
        filter_params: ServiceClosureFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[ServiceClosure]:
        """Get list of closures with filters"""
        
        query = self.db.query(ServiceClosure).filter(
            ServiceClosure.organization_id == organization_id
        )
        
        # Apply filters
        if filter_params.closure_status:
            query = query.filter(ServiceClosure.closure_status == filter_params.closure_status)
        
        if filter_params.closure_reason:
            query = query.filter(ServiceClosure.closure_reason == filter_params.closure_reason)
        
        if filter_params.requires_manager_approval is not None:
            query = query.filter(ServiceClosure.requires_manager_approval == filter_params.requires_manager_approval)
        
        if filter_params.feedback_received is not None:
            query = query.filter(ServiceClosure.feedback_received == filter_params.feedback_received)
        
        if filter_params.escalation_required is not None:
            query = query.filter(ServiceClosure.escalation_required == filter_params.escalation_required)
        
        if filter_params.approved_by_id:
            query = query.filter(ServiceClosure.approved_by_id == filter_params.approved_by_id)
        
        if filter_params.closed_by_id:
            query = query.filter(ServiceClosure.closed_by_id == filter_params.closed_by_id)
        
        if filter_params.from_date:
            query = query.filter(ServiceClosure.created_at >= filter_params.from_date)
        
        if filter_params.to_date:
            query = query.filter(ServiceClosure.created_at <= filter_params.to_date)
        
        return query.order_by(desc(ServiceClosure.created_at)).offset(skip).limit(limit).all()
    
    def approve_closure(
        self, 
        closure_id: int, 
        organization_id: int,
        approved_by_id: int,
        approval_notes: Optional[str] = None
    ) -> ServiceClosure:
        """Approve a service closure (manager action)"""
        
        closure = self.get_closure_by_id(closure_id, organization_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service closure not found"
            )
        
        if closure.closure_status != ClosureStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending closures can be approved"
            )
        
        closure.closure_status = ClosureStatus.APPROVED
        closure.approved_by_id = approved_by_id
        closure.approved_at = datetime.utcnow()
        if approval_notes:
            closure.approval_notes = approval_notes
        
        self.db.commit()
        self.db.refresh(closure)
        
        logger.info(f"Approved service closure {closure_id} by user {approved_by_id}")
        return closure
    
    def close_service(
        self, 
        closure_id: int, 
        organization_id: int,
        closed_by_id: int,
        final_closure_notes: Optional[str] = None
    ) -> ServiceClosure:
        """Finalize service closure (manager action)"""
        
        closure = self.get_closure_by_id(closure_id, organization_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service closure not found"
            )
        
        if closure.closure_status not in [ClosureStatus.PENDING, ClosureStatus.APPROVED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending or approved closures can be closed"
            )
        
        if closure.requires_manager_approval and not closure.approved_by_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager approval required before closing"
            )
        
        closure.closure_status = ClosureStatus.CLOSED
        closure.closed_by_id = closed_by_id
        closure.closed_at = datetime.utcnow()
        if final_closure_notes:
            closure.final_closure_notes = final_closure_notes
        
        self.db.commit()
        self.db.refresh(closure)
        
        logger.info(f"Closed service {closure_id} by user {closed_by_id}")
        return closure
    
    def reopen_service(
        self, 
        closure_id: int, 
        organization_id: int,
        reopened_by_id: int,
        reopening_reason: str
    ) -> ServiceClosure:
        """Reopen a closed service"""
        
        closure = self.get_closure_by_id(closure_id, organization_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service closure not found"
            )
        
        if closure.closure_status != ClosureStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only closed services can be reopened"
            )
        
        closure.closure_status = ClosureStatus.REOPENED
        closure.reopened_count += 1
        closure.last_reopened_at = datetime.utcnow()
        closure.last_reopened_by_id = reopened_by_id
        closure.reopening_reason = reopening_reason
        
        # Reset closure fields
        closure.closed_by_id = None
        closure.closed_at = None
        
        self.db.commit()
        self.db.refresh(closure)
        
        logger.info(f"Reopened service {closure_id} by user {reopened_by_id}")
        return closure