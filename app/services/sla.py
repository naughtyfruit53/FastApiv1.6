# app/services/sla.py

"""
Service layer for SLA Management in Service CRM.
Handles business logic for SLA policies, tracking, and escalation.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from fastapi import Depends

from app.core.database import get_db
from app.models import SLAPolicy, SLATracking, Ticket, Organization
from app.schemas.sla import (
    SLAPolicyCreate, SLAPolicyUpdate, SLATrackingCreate, SLATrackingUpdate,
    SLAMetrics, SLAStatusEnum
)
import logging

logger = logging.getLogger(__name__)


class SLAService:
    """Service for managing SLA policies and tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # SLA Policy Management
    def create_policy(self, policy_data: SLAPolicyCreate, organization_id: int, created_by_id: Optional[int] = None) -> SLAPolicy:
        """Create a new SLA policy"""
        # Check if name already exists in organization
        existing = self.db.query(SLAPolicy).filter(
            and_(
                SLAPolicy.organization_id == organization_id,
                SLAPolicy.name == policy_data.name
            )
        ).first()
        
        if existing:
            raise ValueError(f"SLA policy with name '{policy_data.name}' already exists")
        
        # If this is set as default, remove default from other policies
        if policy_data.is_default:
            self.db.query(SLAPolicy).filter(
                and_(
                    SLAPolicy.organization_id == organization_id,
                    SLAPolicy.is_default == True
                )
            ).update({"is_default": False})
        
        policy = SLAPolicy(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **policy_data.model_dump()
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        logger.info(f"Created SLA policy {policy.id} '{policy.name}' for organization {organization_id}")
        return policy
    
    def get_policies(self, organization_id: int, is_active: Optional[bool] = None) -> List[SLAPolicy]:
        """Get SLA policies for an organization"""
        query = self.db.query(SLAPolicy).filter(SLAPolicy.organization_id == organization_id)
        
        if is_active is not None:
            query = query.filter(SLAPolicy.is_active == is_active)
        
        return query.order_by(SLAPolicy.is_default.desc(), SLAPolicy.name).all()
    
    def get_policy(self, policy_id: int, organization_id: int) -> Optional[SLAPolicy]:
        """Get a specific SLA policy"""
        return self.db.query(SLAPolicy).filter(
            and_(
                SLAPolicy.id == policy_id,
                SLAPolicy.organization_id == organization_id
            )
        ).first()
    
    def update_policy(self, policy_id: int, organization_id: int, policy_data: SLAPolicyUpdate) -> Optional[SLAPolicy]:
        """Update an SLA policy"""
        policy = self.get_policy(policy_id, organization_id)
        if not policy:
            return None
        
        update_data = policy_data.model_dump(exclude_unset=True)
        
        # Handle default policy logic
        if update_data.get("is_default") is True:
            self.db.query(SLAPolicy).filter(
                and_(
                    SLAPolicy.organization_id == organization_id,
                    SLAPolicy.id != policy_id,
                    SLAPolicy.is_default == True
                )
            ).update({"is_default": False})
        
        # Check name uniqueness if name is being updated
        if "name" in update_data and update_data["name"] != policy.name:
            existing = self.db.query(SLAPolicy).filter(
                and_(
                    SLAPolicy.organization_id == organization_id,
                    SLAPolicy.name == update_data["name"],
                    SLAPolicy.id != policy_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"SLA policy with name '{update_data['name']}' already exists")
        
        for field, value in update_data.items():
            setattr(policy, field, value)
        
        policy.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(policy)
        
        logger.info(f"Updated SLA policy {policy.id} for organization {organization_id}")
        return policy
    
    def delete_policy(self, policy_id: int, organization_id: int) -> bool:
        """Delete an SLA policy (only if not in use)"""
        policy = self.get_policy(policy_id, organization_id)
        if not policy:
            return False
        
        # Check if policy is in use
        tracking_count = self.db.query(SLATracking).filter(SLATracking.policy_id == policy_id).count()
        if tracking_count > 0:
            raise ValueError(f"Cannot delete SLA policy '{policy.name}' as it is currently tracking {tracking_count} tickets")
        
        self.db.delete(policy)
        self.db.commit()
        
        logger.info(f"Deleted SLA policy {policy_id} for organization {organization_id}")
        return True
    
    # SLA Policy Matching
    def find_matching_policy(self, ticket: Ticket) -> Optional[SLAPolicy]:
        """Find the best matching SLA policy for a ticket"""
        # Start with policies for the organization
        query = self.db.query(SLAPolicy).filter(
            and_(
                SLAPolicy.organization_id == ticket.organization_id,
                SLAPolicy.is_active == True
            )
        )
        
        # Try to find exact matches first
        exact_match = query.filter(
            and_(
                or_(SLAPolicy.priority == ticket.priority, SLAPolicy.priority.is_(None)),
                or_(SLAPolicy.ticket_type == ticket.ticket_type, SLAPolicy.ticket_type.is_(None)),
                # Add customer tier matching if customer has tier information
                SLAPolicy.customer_tier.is_(None)  # For now, match policies without customer tier
            )
        ).order_by(
            # Prioritize more specific matches
            SLAPolicy.priority.is_(None).asc(),  # Prefer policies with specific priority
            SLAPolicy.ticket_type.is_(None).asc(),  # Prefer policies with specific ticket type
            SLAPolicy.is_default.desc()  # Then prefer default policies
        ).first()
        
        if exact_match:
            return exact_match
        
        # Fall back to default policy
        default_policy = query.filter(SLAPolicy.is_default == True).first()
        if default_policy:
            return default_policy
        
        logger.warning(f"No matching SLA policy found for ticket {ticket.id}")
        return None
    
    # SLA Tracking Management
    def create_tracking(self, ticket_id: int, organization_id: int, force_recreate: bool = False) -> Optional[SLATracking]:
        """Create SLA tracking for a ticket"""
        # Check if tracking already exists
        existing = self.db.query(SLATracking).filter(SLATracking.ticket_id == ticket_id).first()
        if existing and not force_recreate:
            logger.info(f"SLA tracking already exists for ticket {ticket_id}")
            return existing
        
        # Get the ticket
        ticket = self.db.query(Ticket).filter(
            and_(
                Ticket.id == ticket_id,
                Ticket.organization_id == organization_id
            )
        ).first()
        
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found in organization {organization_id}")
            return None
        
        # Find matching policy
        policy = self.find_matching_policy(ticket)
        if not policy:
            logger.error(f"No SLA policy found for ticket {ticket_id}")
            return None
        
        # Calculate deadlines based on ticket creation time
        created_at = ticket.created_at
        response_deadline = created_at + timedelta(hours=policy.response_time_hours)
        resolution_deadline = created_at + timedelta(hours=policy.resolution_time_hours)
        
        # Remove existing tracking if force recreate
        if existing and force_recreate:
            self.db.delete(existing)
            self.db.flush()
        
        # Create new tracking
        tracking = SLATracking(
            organization_id=organization_id,
            ticket_id=ticket_id,
            policy_id=policy.id,
            response_deadline=response_deadline,
            resolution_deadline=resolution_deadline
        )
        
        self.db.add(tracking)
        self.db.commit()
        self.db.refresh(tracking)
        
        logger.info(f"Created SLA tracking {tracking.id} for ticket {ticket_id} with policy {policy.id}")
        return tracking
    
    def update_tracking(self, tracking_id: int, organization_id: int, tracking_data: SLATrackingUpdate) -> Optional[SLATracking]:
        """Update SLA tracking"""
        tracking = self.db.query(SLATracking).filter(
            and_(
                SLATracking.id == tracking_id,
                SLATracking.organization_id == organization_id
            )
        ).first()
        
        if not tracking:
            return None
        
        update_data = tracking_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(tracking, field, value)
        
        # Recalculate breach hours if response/resolution times are updated
        if "first_response_at" in update_data:
            tracking.response_breach_hours = self._calculate_breach_hours(
                tracking.response_deadline, 
                tracking.first_response_at
            )
            tracking.response_status = SLAStatusEnum.MET if tracking.response_breach_hours <= 0 else SLAStatusEnum.BREACHED
        
        if "resolved_at" in update_data:
            tracking.resolution_breach_hours = self._calculate_breach_hours(
                tracking.resolution_deadline,
                tracking.resolved_at
            )
            tracking.resolution_status = SLAStatusEnum.MET if tracking.resolution_breach_hours <= 0 else SLAStatusEnum.BREACHED
        
        tracking.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tracking)
        
        logger.info(f"Updated SLA tracking {tracking_id}")
        return tracking
    
    def get_tracking(self, ticket_id: int, organization_id: int) -> Optional[SLATracking]:
        """Get SLA tracking for a ticket"""
        return self.db.query(SLATracking).filter(
            and_(
                SLATracking.ticket_id == ticket_id,
                SLATracking.organization_id == organization_id
            )
        ).first()
    
    def get_breached_slas(self, organization_id: int, limit: int = 50) -> List[SLATracking]:
        """Get tickets with breached SLAs"""
        return self.db.query(SLATracking).filter(
            and_(
                SLATracking.organization_id == organization_id,
                or_(
                    SLATracking.response_status == SLAStatusEnum.BREACHED,
                    SLATracking.resolution_status == SLAStatusEnum.BREACHED
                )
            )
        ).order_by(desc(SLATracking.created_at)).limit(limit).all()
    
    def get_escalation_candidates(self, organization_id: int) -> List[SLATracking]:
        """Get tickets that should be escalated"""
        now = datetime.utcnow()
        
        # Find tracking records where escalation is enabled and threshold is reached
        return self.db.query(SLATracking).join(SLAPolicy).filter(
            and_(
                SLATracking.organization_id == organization_id,
                SLAPolicy.escalation_enabled == True,
                SLATracking.escalation_triggered == False,
                or_(
                    # Response escalation
                    and_(
                        SLATracking.response_status == SLAStatusEnum.PENDING,
                        SLATracking.first_response_at.is_(None),
                        now >= (SLATracking.response_deadline - 
                                func.cast(SLAPolicy.response_time_hours * (100 - SLAPolicy.escalation_threshold_percent) / 100, func.Interval))
                    ),
                    # Resolution escalation
                    and_(
                        SLATracking.resolution_status == SLAStatusEnum.PENDING,
                        SLATracking.resolved_at.is_(None),
                        now >= (SLATracking.resolution_deadline - 
                                func.cast(SLAPolicy.resolution_time_hours * (100 - SLAPolicy.escalation_threshold_percent) / 100, func.Interval))
                    )
                )
            )
        ).all()
    
    def trigger_escalation(self, tracking_id: int, organization_id: int) -> Optional[SLATracking]:
        """Trigger escalation for an SLA tracking record"""
        tracking = self.db.query(SLATracking).filter(
            and_(
                SLATracking.id == tracking_id,
                SLATracking.organization_id == organization_id
            )
        ).first()
        
        if not tracking:
            return None
        
        tracking.escalation_triggered = True
        tracking.escalation_triggered_at = datetime.utcnow()
        tracking.escalation_level += 1
        tracking.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tracking)
        
        logger.info(f"Triggered escalation for SLA tracking {tracking_id}, level {tracking.escalation_level}")
        return tracking
    
    # SLA Metrics and Analytics
    def get_sla_metrics(self, organization_id: int, start_date: datetime, end_date: datetime) -> SLAMetrics:
        """Calculate SLA metrics for a date range"""
        # Base query for tracking records in the date range
        base_query = self.db.query(SLATracking).filter(
            and_(
                SLATracking.organization_id == organization_id,
                SLATracking.created_at >= start_date,
                SLATracking.created_at <= end_date
            )
        )
        
        total_tickets = base_query.count()
        
        if total_tickets == 0:
            return SLAMetrics(
                total_tickets=0,
                response_sla_met=0,
                resolution_sla_met=0,
                response_sla_breached=0,
                resolution_sla_breached=0,
                escalated_tickets=0,
                response_sla_percentage=0,
                resolution_sla_percentage=0
            )
        
        # Calculate metrics
        response_met = base_query.filter(SLATracking.response_status == SLAStatusEnum.MET).count()
        resolution_met = base_query.filter(SLATracking.resolution_status == SLAStatusEnum.MET).count()
        response_breached = base_query.filter(SLATracking.response_status == SLAStatusEnum.BREACHED).count()
        resolution_breached = base_query.filter(SLATracking.resolution_status == SLAStatusEnum.BREACHED).count()
        escalated = base_query.filter(SLATracking.escalation_triggered == True).count()
        
        # Calculate averages for completed tickets
        avg_response_query = base_query.filter(SLATracking.first_response_at.isnot(None))
        avg_resolution_query = base_query.filter(SLATracking.resolved_at.isnot(None))
        
        avg_response_time = None
        avg_resolution_time = None
        
        if avg_response_query.count() > 0:
            response_times = [(tracking.first_response_at - self.db.query(Ticket).filter(Ticket.id == tracking.ticket_id).first().created_at).total_seconds() / 3600 
                             for tracking in avg_response_query.all()]
            avg_response_time = sum(response_times) / len(response_times)
        
        if avg_resolution_query.count() > 0:
            resolution_times = [(tracking.resolved_at - self.db.query(Ticket).filter(Ticket.id == tracking.ticket_id).first().created_at).total_seconds() / 3600 
                               for tracking in avg_resolution_query.all()]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return SLAMetrics(
            total_tickets=total_tickets,
            response_sla_met=response_met,
            resolution_sla_met=resolution_met,
            response_sla_breached=response_breached,
            resolution_sla_breached=resolution_breached,
            escalated_tickets=escalated,
            avg_response_time_hours=avg_response_time,
            avg_resolution_time_hours=avg_resolution_time,
            response_sla_percentage=(response_met / total_tickets) * 100,
            resolution_sla_percentage=(resolution_met / total_tickets) * 100
        )
    
    # Helper methods
    def _calculate_breach_hours(self, deadline: datetime, completed_at: Optional[datetime]) -> Optional[float]:
        """Calculate breach hours (negative = met SLA, positive = breached SLA)"""
        if completed_at is None:
            return None
        
        diff = completed_at - deadline
        return diff.total_seconds() / 3600  # Convert to hours
    
    def process_ticket_response(self, ticket_id: int, organization_id: int, response_time: datetime) -> Optional[SLATracking]:
        """Process first response for a ticket and update SLA tracking"""
        tracking = self.get_tracking(ticket_id, organization_id)
        if not tracking or tracking.first_response_at is not None:
            return tracking
        
        update_data = SLATrackingUpdate(first_response_at=response_time)
        return self.update_tracking(tracking.id, organization_id, update_data)
    
    def process_ticket_resolution(self, ticket_id: int, organization_id: int, resolution_time: datetime) -> Optional[SLATracking]:
        """Process ticket resolution and update SLA tracking"""
        tracking = self.get_tracking(ticket_id, organization_id)
        if not tracking or tracking.resolved_at is not None:
            return tracking
        
        update_data = SLATrackingUpdate(resolved_at=resolution_time)
        return self.update_tracking(tracking.id, organization_id, update_data)


def get_sla_service(db: Session = Depends(get_db)) -> SLAService:
    """Dependency to get SLA service instance"""
    return SLAService(db)