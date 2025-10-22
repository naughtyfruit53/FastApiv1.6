"""
Streaming Analytics Service for Real-Time Data Processing
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from app.models.streaming_analytics import (
    StreamingDataSource, StreamingEvent, LivePrediction, 
    StreamingAlert, StreamingMetric,
    StreamStatus, AlertSeverity, AlertStatus
)
from app.models.user_models import User

logger = logging.getLogger(__name__)


class StreamingAnalyticsService:
    """Service for managing real-time streaming analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================================================
    # DATA SOURCE MANAGEMENT
    # ============================================================================
    
    def create_data_source(
        self,
        organization_id: int,
        created_by_id: int,
        source_name: str,
        source_type: str,
        connection_config: Dict[str, Any],
        description: Optional[str] = None
    ) -> StreamingDataSource:
        """Create a new streaming data source"""
        try:
            data_source = StreamingDataSource(
                organization_id=organization_id,
                created_by_id=created_by_id,
                source_name=source_name,
                source_type=source_type,
                connection_config=connection_config,
                description=description,
                status=StreamStatus.ACTIVE,
                is_active=True
            )
            self.db.add(data_source)
            self.db.commit()
            self.db.refresh(data_source)
            
            logger.info(f"Created data source {data_source.id} for org {organization_id}")
            return data_source
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating data source: {e}")
            raise
    
    def get_data_source(
        self,
        source_id: int,
        organization_id: int
    ) -> Optional[StreamingDataSource]:
        """Get a data source by ID"""
        return self.db.query(StreamingDataSource).filter(
            and_(
                StreamingDataSource.id == source_id,
                StreamingDataSource.organization_id == organization_id
            )
        ).first()
    
    def list_data_sources(
        self,
        organization_id: int,
        status: Optional[StreamStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StreamingDataSource]:
        """List data sources for an organization"""
        query = self.db.query(StreamingDataSource).filter(
            StreamingDataSource.organization_id == organization_id
        )
        
        if status:
            query = query.filter(StreamingDataSource.status == status)
        
        return query.order_by(desc(StreamingDataSource.created_at)).offset(skip).limit(limit).all()
    
    def update_data_source(
        self,
        source_id: int,
        organization_id: int,
        **updates
    ) -> Optional[StreamingDataSource]:
        """Update a data source"""
        try:
            data_source = self.get_data_source(source_id, organization_id)
            if not data_source:
                return None
            
            for key, value in updates.items():
                if hasattr(data_source, key):
                    setattr(data_source, key, value)
            
            self.db.commit()
            self.db.refresh(data_source)
            
            logger.info(f"Updated data source {source_id}")
            return data_source
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating data source: {e}")
            raise
    
    def update_data_source_stats(
        self,
        source_id: int,
        organization_id: int,
        increment_messages: bool = False,
        increment_errors: bool = False
    ) -> Optional[StreamingDataSource]:
        """Update data source statistics"""
        try:
            data_source = self.get_data_source(source_id, organization_id)
            if not data_source:
                return None
            
            if increment_messages:
                data_source.message_count += 1
                data_source.last_message_at = datetime.utcnow()
            
            if increment_errors:
                data_source.error_count += 1
            
            self.db.commit()
            self.db.refresh(data_source)
            
            return data_source
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating data source stats: {e}")
            raise
    
    # ============================================================================
    # EVENT INGESTION
    # ============================================================================
    
    def ingest_event(
        self,
        data_source_id: int,
        organization_id: int,
        event_type: str,
        event_data: Dict[str, Any],
        event_timestamp: Optional[datetime] = None
    ) -> StreamingEvent:
        """Ingest a streaming event"""
        try:
            event = StreamingEvent(
                data_source_id=data_source_id,
                organization_id=organization_id,
                event_type=event_type,
                event_data=event_data,
                event_timestamp=event_timestamp or datetime.utcnow(),
                processed=False
            )
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            # Update data source stats
            self.update_data_source_stats(data_source_id, organization_id, increment_messages=True)
            
            logger.info(f"Ingested event {event.id} from source {data_source_id}")
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ingesting event: {e}")
            raise
    
    def get_recent_events(
        self,
        organization_id: int,
        data_source_id: Optional[int] = None,
        event_type: Optional[str] = None,
        minutes: int = 60,
        limit: int = 100
    ) -> List[StreamingEvent]:
        """Get recent streaming events"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        query = self.db.query(StreamingEvent).filter(
            and_(
                StreamingEvent.organization_id == organization_id,
                StreamingEvent.event_timestamp >= cutoff_time
            )
        )
        
        if data_source_id:
            query = query.filter(StreamingEvent.data_source_id == data_source_id)
        
        if event_type:
            query = query.filter(StreamingEvent.event_type == event_type)
        
        return query.order_by(desc(StreamingEvent.event_timestamp)).limit(limit).all()
    
    def mark_event_processed(
        self,
        event_id: int,
        organization_id: int
    ) -> Optional[StreamingEvent]:
        """Mark an event as processed"""
        try:
            event = self.db.query(StreamingEvent).filter(
                and_(
                    StreamingEvent.id == event_id,
                    StreamingEvent.organization_id == organization_id
                )
            ).first()
            
            if not event:
                return None
            
            event.processed = True
            event.processed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(event)
            
            return event
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking event as processed: {e}")
            raise
    
    # ============================================================================
    # LIVE PREDICTIONS
    # ============================================================================
    
    def record_live_prediction(
        self,
        organization_id: int,
        prediction_type: str,
        input_data: Dict[str, Any],
        prediction_result: Dict[str, Any],
        model_id: Optional[int] = None,
        confidence_score: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> LivePrediction:
        """Record a live prediction"""
        try:
            prediction = LivePrediction(
                organization_id=organization_id,
                model_id=model_id,
                prediction_type=prediction_type,
                input_data=input_data,
                prediction_result=prediction_result,
                confidence_score=confidence_score,
                context=context
            )
            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)
            
            logger.info(f"Recorded live prediction {prediction.id} for org {organization_id}")
            return prediction
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording live prediction: {e}")
            raise
    
    def get_recent_predictions(
        self,
        organization_id: int,
        prediction_type: Optional[str] = None,
        model_id: Optional[int] = None,
        minutes: int = 60,
        limit: int = 100
    ) -> List[LivePrediction]:
        """Get recent live predictions"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        query = self.db.query(LivePrediction).filter(
            and_(
                LivePrediction.organization_id == organization_id,
                LivePrediction.predicted_at >= cutoff_time
            )
        )
        
        if prediction_type:
            query = query.filter(LivePrediction.prediction_type == prediction_type)
        
        if model_id:
            query = query.filter(LivePrediction.model_id == model_id)
        
        return query.order_by(desc(LivePrediction.predicted_at)).limit(limit).all()
    
    # ============================================================================
    # ALERTING
    # ============================================================================
    
    def create_alert(
        self,
        organization_id: int,
        alert_type: str,
        alert_title: str,
        alert_message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        data_source_id: Optional[int] = None,
        alert_data: Optional[Dict[str, Any]] = None
    ) -> StreamingAlert:
        """Create a streaming alert"""
        try:
            alert = StreamingAlert(
                organization_id=organization_id,
                data_source_id=data_source_id,
                alert_type=alert_type,
                alert_title=alert_title,
                alert_message=alert_message,
                severity=severity,
                status=AlertStatus.OPEN,
                alert_data=alert_data
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Created alert {alert.id} for org {organization_id}")
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating alert: {e}")
            raise
    
    def get_alerts(
        self,
        organization_id: int,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StreamingAlert]:
        """Get alerts for an organization"""
        query = self.db.query(StreamingAlert).filter(
            StreamingAlert.organization_id == organization_id
        )
        
        if status:
            query = query.filter(StreamingAlert.status == status)
        
        if severity:
            query = query.filter(StreamingAlert.severity == severity)
        
        return query.order_by(desc(StreamingAlert.triggered_at)).offset(skip).limit(limit).all()
    
    def acknowledge_alert(
        self,
        alert_id: int,
        organization_id: int,
        acknowledged_by_id: int
    ) -> Optional[StreamingAlert]:
        """Acknowledge an alert"""
        try:
            alert = self.db.query(StreamingAlert).filter(
                and_(
                    StreamingAlert.id == alert_id,
                    StreamingAlert.organization_id == organization_id
                )
            ).first()
            
            if not alert:
                return None
            
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by_id = acknowledged_by_id
            alert.acknowledged_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Acknowledged alert {alert_id}")
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error acknowledging alert: {e}")
            raise
    
    def resolve_alert(
        self,
        alert_id: int,
        organization_id: int,
        resolved_by_id: int,
        resolution_notes: Optional[str] = None
    ) -> Optional[StreamingAlert]:
        """Resolve an alert"""
        try:
            alert = self.db.query(StreamingAlert).filter(
                and_(
                    StreamingAlert.id == alert_id,
                    StreamingAlert.organization_id == organization_id
                )
            ).first()
            
            if not alert:
                return None
            
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by_id = resolved_by_id
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = resolution_notes
            
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Resolved alert {alert_id}")
            return alert
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resolving alert: {e}")
            raise
    
    # ============================================================================
    # METRICS
    # ============================================================================
    
    def record_metric(
        self,
        organization_id: int,
        metric_name: str,
        metric_value: float,
        aggregation_type: str,
        time_window: str,
        window_start: datetime,
        window_end: datetime,
        data_source_id: Optional[int] = None,
        dimensions: Optional[Dict[str, Any]] = None
    ) -> StreamingMetric:
        """Record a streaming metric"""
        try:
            metric = StreamingMetric(
                organization_id=organization_id,
                data_source_id=data_source_id,
                metric_name=metric_name,
                metric_value=metric_value,
                aggregation_type=aggregation_type,
                time_window=time_window,
                window_start=window_start,
                window_end=window_end,
                dimensions=dimensions
            )
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            
            return metric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recording metric: {e}")
            raise
    
    def get_metrics(
        self,
        organization_id: int,
        metric_name: Optional[str] = None,
        time_window: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[StreamingMetric]:
        """Get streaming metrics"""
        query = self.db.query(StreamingMetric).filter(
            StreamingMetric.organization_id == organization_id
        )
        
        if metric_name:
            query = query.filter(StreamingMetric.metric_name == metric_name)
        
        if time_window:
            query = query.filter(StreamingMetric.time_window == time_window)
        
        if start_time:
            query = query.filter(StreamingMetric.window_start >= start_time)
        
        if end_time:
            query = query.filter(StreamingMetric.window_end <= end_time)
        
        return query.order_by(desc(StreamingMetric.window_start)).limit(limit).all()
    
    # ============================================================================
    # DASHBOARD DATA
    # ============================================================================
    
    def get_dashboard_data(
        self,
        organization_id: int
    ) -> Dict[str, Any]:
        """Get streaming analytics dashboard data"""
        # Get active data sources
        active_sources = self.db.query(StreamingDataSource).filter(
            and_(
                StreamingDataSource.organization_id == organization_id,
                StreamingDataSource.is_active == True
            )
        ).count()
        
        # Get recent events count
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_events = self.db.query(StreamingEvent).filter(
            and_(
                StreamingEvent.organization_id == organization_id,
                StreamingEvent.event_timestamp >= recent_cutoff
            )
        ).count()
        
        # Get open alerts
        open_alerts = self.db.query(StreamingAlert).filter(
            and_(
                StreamingAlert.organization_id == organization_id,
                StreamingAlert.status == AlertStatus.OPEN
            )
        ).count()
        
        # Get recent predictions
        recent_predictions = self.db.query(LivePrediction).filter(
            and_(
                LivePrediction.organization_id == organization_id,
                LivePrediction.predicted_at >= recent_cutoff
            )
        ).count()
        
        return {
            "active_data_sources": active_sources,
            "recent_events_1h": recent_events,
            "open_alerts": open_alerts,
            "recent_predictions_1h": recent_predictions,
            "timestamp": datetime.utcnow().isoformat()
        }
