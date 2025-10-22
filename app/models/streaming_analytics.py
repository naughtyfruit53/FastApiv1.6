"""
Streaming Analytics Models for Real-Time Data Processing
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime
import enum


class StreamStatus(str, enum.Enum):
    """Status of a streaming data source"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class AlertSeverity(str, enum.Enum):
    """Severity level for streaming alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """Status of a streaming alert"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class StreamingDataSource(Base):
    """
    Model for streaming data sources.
    Manages connections to real-time data streams (Kafka, WebSockets, etc.)
    """
    __tablename__ = "streaming_data_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_stream_source_org_id"), 
        nullable=False, 
        index=True
    )
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'kafka', 'websocket', 'http_stream', etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Connection configuration
    connection_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Status
    status: Mapped[StreamStatus] = mapped_column(
        SQLEnum(StreamStatus), 
        default=StreamStatus.ACTIVE,
        nullable=False,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metrics
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Metadata
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_stream_source_created_by"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    events: Mapped[List["StreamingEvent"]] = relationship("StreamingEvent", back_populates="data_source", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_stream_source_org_status', 'organization_id', 'status'),
    )


class StreamingEvent(Base):
    """
    Model for storing streaming events.
    Captures real-time events from streaming data sources.
    """
    __tablename__ = "streaming_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    data_source_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("streaming_data_sources.id", name="fk_event_data_source_id"), 
        nullable=False, 
        index=True
    )
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_stream_event_org_id"), 
        nullable=False, 
        index=True
    )
    
    # Event data
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source: Mapped["StreamingDataSource"] = relationship("StreamingDataSource", back_populates="events")
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    
    __table_args__ = (
        Index('idx_event_source_type', 'data_source_id', 'event_type'),
        Index('idx_event_timestamp', 'event_timestamp'),
        Index('idx_event_processed', 'processed', 'event_timestamp'),
    )


class LivePrediction(Base):
    """
    Model for storing live predictions from streaming data.
    Tracks real-time model predictions for dashboard display.
    """
    __tablename__ = "live_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_live_pred_org_id"), 
        nullable=False, 
        index=True
    )
    model_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("ai_models.id", name="fk_live_pred_model_id"), 
        nullable=True
    )
    
    # Prediction details
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    prediction_result: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    model: Mapped[Optional["AIModel"]] = relationship("AIModel", foreign_keys=[model_id])
    
    __table_args__ = (
        Index('idx_live_pred_org_type', 'organization_id', 'prediction_type'),
        Index('idx_live_pred_timestamp', 'predicted_at'),
    )


class StreamingAlert(Base):
    """
    Model for streaming analytics alerts.
    Manages real-time alerts based on streaming data patterns.
    """
    __tablename__ = "streaming_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_stream_alert_org_id"), 
        nullable=False, 
        index=True
    )
    data_source_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("streaming_data_sources.id", name="fk_alert_data_source_id"), 
        nullable=True
    )
    
    # Alert details
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    alert_title: Mapped[str] = mapped_column(String(255), nullable=False)
    alert_message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity), 
        default=AlertSeverity.INFO,
        nullable=False,
        index=True
    )
    
    # Status
    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus), 
        default=AlertStatus.OPEN,
        nullable=False,
        index=True
    )
    
    # Alert data
    alert_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Handling
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_alert_acknowledged_by"), 
        nullable=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", name="fk_alert_resolved_by"), 
        nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    data_source: Mapped[Optional["StreamingDataSource"]] = relationship("StreamingDataSource")
    acknowledged_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[acknowledged_by_id])
    resolved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by_id])
    
    __table_args__ = (
        Index('idx_alert_org_status', 'organization_id', 'status'),
        Index('idx_alert_severity', 'severity', 'status'),
        Index('idx_alert_triggered', 'triggered_at'),
    )


class StreamingMetric(Base):
    """
    Model for aggregated streaming metrics.
    Stores time-series metrics for dashboard visualization.
    """
    __tablename__ = "streaming_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("organizations.id", name="fk_stream_metric_org_id"), 
        nullable=False, 
        index=True
    )
    data_source_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("streaming_data_sources.id", name="fk_metric_data_source_id"), 
        nullable=True
    )
    
    # Metric details
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    aggregation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'sum', 'avg', 'min', 'max', 'count'
    
    # Time window
    time_window: Mapped[str] = mapped_column(String(50), nullable=False)  # '1m', '5m', '15m', '1h', '1d'
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Additional data
    dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[organization_id])
    data_source: Mapped[Optional["StreamingDataSource"]] = relationship("StreamingDataSource")
    
    __table_args__ = (
        Index('idx_metric_org_name', 'organization_id', 'metric_name'),
        Index('idx_metric_window', 'window_start', 'window_end'),
        Index('idx_metric_name_window', 'metric_name', 'window_start'),
    )
