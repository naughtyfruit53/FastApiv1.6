# app/services/customer_analytics_service.py

"""
Customer Analytics Service

Provides analytics and insights for customer data including:
- Customer interaction metrics
- Segment analysis
- Performance indicators
- Multi-tenant isolation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.models import Customer, CustomerInteraction, CustomerSegment
from app.core.tenant import TenantQueryMixin
import logging

logger = logging.getLogger(__name__)


class CustomerAnalyticsService:
    """Service for calculating customer analytics and insights"""
    
    def __init__(self, db: Session, organization_id: int):
        """
        Initialize analytics service for a specific organization
        
        Args:
            db: Database session
            organization_id: Organization ID for multi-tenant isolation
        """
        self.db = db
        self.organization_id = organization_id
    
    def get_customer_metrics(self, customer_id: int) -> Dict[str, Any]:
        """
        Calculate key metrics for a specific customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dict containing customer metrics including:
            - total_interactions: Total number of interactions
            - last_interaction_date: Date of last interaction
            - interaction_types: Breakdown by interaction type
            - segments: Current segment memberships
            - recent_interactions: Recent interaction summary
        """
        logger.info(f"Calculating metrics for customer {customer_id} in org {self.organization_id}")
        
        # Verify customer belongs to organization
        customer = TenantQueryMixin.filter_by_tenant(
            self.db.query(Customer), Customer, self.organization_id
        ).filter(Customer.id == customer_id).first()
        
        if not customer:
            logger.warning(f"Customer {customer_id} not found in organization {self.organization_id}")
            return {}
        
        # Calculate interaction metrics
        interaction_metrics = self._calculate_interaction_metrics(customer_id)
        
        # Get current segments
        segment_info = self._get_customer_segments(customer_id)
        
        # Get recent interactions summary
        recent_interactions = self._get_recent_interactions(customer_id, limit=5)
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.name,
            "total_interactions": interaction_metrics["total_count"],
            "last_interaction_date": interaction_metrics["last_interaction_date"],
            "interaction_types": interaction_metrics["by_type"],
            "interaction_status": interaction_metrics["by_status"],
            "segments": segment_info,
            "recent_interactions": recent_interactions,
            "calculated_at": datetime.utcnow()
        }
    
    def get_segment_analytics(self, segment_name: str) -> Dict[str, Any]:
        """
        Calculate analytics for all customers in a specific segment
        
        Args:
            segment_name: Name of the segment to analyze
            
        Returns:
            Dict containing segment-wide analytics
        """
        logger.info(f"Calculating segment analytics for '{segment_name}' in org {self.organization_id}")
        
        # Get all customers in the segment
        segment_customers = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerSegment), CustomerSegment, self.organization_id
        ).filter(
            and_(
                CustomerSegment.segment_name == segment_name,
                CustomerSegment.is_active == True
            )
        ).all()
        
        if not segment_customers:
            return {
                "segment_name": segment_name,
                "total_customers": 0,
                "analytics": {}
            }
        
        customer_ids = [seg.customer_id for seg in segment_customers]
        
        # Calculate aggregated metrics
        total_interactions = self._get_segment_interaction_count(customer_ids)
        interaction_distribution = self._get_segment_interaction_distribution(customer_ids)
        activity_timeline = self._get_segment_activity_timeline(customer_ids)
        
        return {
            "segment_name": segment_name,
            "total_customers": len(customer_ids),
            "total_interactions": total_interactions,
            "avg_interactions_per_customer": total_interactions / len(customer_ids) if customer_ids else 0,
            "interaction_distribution": interaction_distribution,
            "activity_timeline": activity_timeline,
            "calculated_at": datetime.utcnow()
        }
    
    def get_organization_analytics_summary(self) -> Dict[str, Any]:
        """
        Get high-level analytics summary for the entire organization
        
        Returns:
            Dict containing organization-wide analytics
        """
        logger.info(f"Calculating organization analytics summary for org {self.organization_id}")
        
        # Customer counts by segment
        segment_distribution = self._get_segment_distribution()
        
        # Interaction trends
        interaction_trends = self._get_interaction_trends()
        
        # Overall metrics
        total_customers = TenantQueryMixin.filter_by_tenant(
            self.db.query(Customer), Customer, self.organization_id
        ).filter(Customer.is_active == True).count()
        
        total_interactions = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).count()
        
        return {
            "organization_id": self.organization_id,
            "total_customers": total_customers,
            "total_interactions": total_interactions,
            "segment_distribution": segment_distribution,
            "interaction_trends": interaction_trends,
            "calculated_at": datetime.utcnow()
        }
    
    # Private helper methods
    
    def _calculate_interaction_metrics(self, customer_id: int) -> Dict[str, Any]:
        """Calculate interaction metrics for a customer"""
        interactions_query = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(CustomerInteraction.customer_id == customer_id)
        
        # Total count
        total_count = interactions_query.count()
        
        # Last interaction date
        last_interaction = interactions_query.order_by(
            desc(CustomerInteraction.interaction_date)
        ).first()
        last_interaction_date = last_interaction.interaction_date if last_interaction else None
        
        # By type
        by_type = {}
        type_results = interactions_query.with_entities(
            CustomerInteraction.interaction_type,
            func.count(CustomerInteraction.id)
        ).group_by(CustomerInteraction.interaction_type).all()
        
        for interaction_type, count in type_results:
            by_type[interaction_type] = count
        
        # By status
        by_status = {}
        status_results = interactions_query.with_entities(
            CustomerInteraction.status,
            func.count(CustomerInteraction.id)
        ).group_by(CustomerInteraction.status).all()
        
        for status, count in status_results:
            by_status[status] = count
        
        return {
            "total_count": total_count,
            "last_interaction_date": last_interaction_date,
            "by_type": by_type,
            "by_status": by_status
        }
    
    def _get_customer_segments(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get current segment memberships for a customer"""
        segments = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerSegment), CustomerSegment, self.organization_id
        ).filter(
            and_(
                CustomerSegment.customer_id == customer_id,
                CustomerSegment.is_active == True
            )
        ).all()
        
        return [
            {
                "segment_name": seg.segment_name,
                "segment_value": seg.segment_value,
                "assigned_date": seg.assigned_date,
                "description": seg.segment_description
            }
            for seg in segments
        ]
    
    def _get_recent_interactions(self, customer_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent interactions for a customer"""
        interactions = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(CustomerInteraction.customer_id == customer_id).order_by(
            desc(CustomerInteraction.interaction_date)
        ).limit(limit).all()
        
        return [
            {
                "interaction_type": interaction.interaction_type,
                "subject": interaction.subject,
                "status": interaction.status,
                "interaction_date": interaction.interaction_date
            }
            for interaction in interactions
        ]
    
    def _get_segment_interaction_count(self, customer_ids: List[int]) -> int:
        """Get total interaction count for customers in segment"""
        return TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(CustomerInteraction.customer_id.in_(customer_ids)).count()
    
    def _get_segment_interaction_distribution(self, customer_ids: List[int]) -> Dict[str, int]:
        """Get interaction type distribution for segment"""
        results = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(CustomerInteraction.customer_id.in_(customer_ids)).with_entities(
            CustomerInteraction.interaction_type,
            func.count(CustomerInteraction.id)
        ).group_by(CustomerInteraction.interaction_type).all()
        
        return {interaction_type: count for interaction_type, count in results}
    
    def _get_segment_activity_timeline(self, customer_ids: List[int], days: int = 30) -> List[Dict[str, Any]]:
        """Get daily interaction counts for segment over specified days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(
            and_(
                CustomerInteraction.customer_id.in_(customer_ids),
                CustomerInteraction.interaction_date >= start_date
            )
        ).with_entities(
            func.date(CustomerInteraction.interaction_date).label('date'),
            func.count(CustomerInteraction.id).label('count')
        ).group_by(func.date(CustomerInteraction.interaction_date)).all()
        
        return [
            {
                "date": str(date),
                "interaction_count": count
            }
            for date, count in results
        ]
    
    def _get_segment_distribution(self) -> Dict[str, int]:
        """Get distribution of customers across segments"""
        results = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerSegment), CustomerSegment, self.organization_id
        ).filter(CustomerSegment.is_active == True).with_entities(
            CustomerSegment.segment_name,
            func.count(func.distinct(CustomerSegment.customer_id))
        ).group_by(CustomerSegment.segment_name).all()
        
        return {segment_name: count for segment_name, count in results}
    
    def _get_interaction_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get interaction trends over specified days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = TenantQueryMixin.filter_by_tenant(
            self.db.query(CustomerInteraction), CustomerInteraction, self.organization_id
        ).filter(CustomerInteraction.interaction_date >= start_date).with_entities(
            func.date(CustomerInteraction.interaction_date).label('date'),
            func.count(CustomerInteraction.id).label('count')
        ).group_by(func.date(CustomerInteraction.interaction_date)).all()
        
        return [
            {
                "date": str(date),
                "interaction_count": count
            }
            for date, count in results
        ]