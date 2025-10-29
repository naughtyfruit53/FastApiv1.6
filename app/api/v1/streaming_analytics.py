"""
Streaming Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import asyncio

from app.core.database import get_db
from app.core.enforcement import require_access
from app.services.streaming_analytics_service import StreamingAnalyticsService
from app.models.streaming_analytics import StreamStatus, AlertSeverity, AlertStatus

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class DataSourceCreate(BaseModel):
    """Schema for creating a data source"""
    source_name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., min_length=1, max_length=50)
    connection_config: Dict[str, Any]
    description: Optional[str] = None


class DataSourceUpdate(BaseModel):
    """Schema for updating a data source"""
    source_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    status: Optional[StreamStatus] = None
    is_active: Optional[bool] = None


class DataSourceResponse(BaseModel):
    """Schema for data source response"""
    id: int
    organization_id: int
    source_name: str
    source_type: str
    description: Optional[str]
    status: StreamStatus
    is_active: bool
    message_count: int
    error_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """Schema for creating an event"""
    data_source_id: int
    event_type: str
    event_data: Dict[str, Any]
    event_timestamp: Optional[datetime] = None


class EventResponse(BaseModel):
    """Schema for event response"""
    id: int
    data_source_id: int
    event_type: str
    event_data: Dict[str, Any]
    event_timestamp: datetime
    processed: bool
    received_at: datetime
    
    class Config:
        from_attributes = True


class LivePredictionCreate(BaseModel):
    """Schema for creating a live prediction"""
    prediction_type: str
    input_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    model_id: Optional[int] = None
    confidence_score: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


class LivePredictionResponse(BaseModel):
    """Schema for live prediction response"""
    id: int
    organization_id: int
    model_id: Optional[int]
    prediction_type: str
    prediction_result: Dict[str, Any]
    confidence_score: Optional[float]
    predicted_at: datetime
    
    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Schema for creating an alert"""
    alert_type: str
    alert_title: str
    alert_message: str
    severity: AlertSeverity = AlertSeverity.INFO
    data_source_id: Optional[int] = None
    alert_data: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    organization_id: int
    alert_type: str
    alert_title: str
    alert_message: str
    severity: AlertSeverity
    status: AlertStatus
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert"""
    alert_id: int


class AlertResolve(BaseModel):
    """Schema for resolving an alert"""
    alert_id: int
    resolution_notes: Optional[str] = None


class MetricCreate(BaseModel):
    """Schema for creating a metric"""
    metric_name: str
    metric_value: float
    aggregation_type: str
    time_window: str
    window_start: datetime
    window_end: datetime
    data_source_id: Optional[int] = None
    dimensions: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """Schema for metric response"""
    id: int
    organization_id: int
    metric_name: str
    metric_value: float
    aggregation_type: str
    time_window: str
    window_start: datetime
    window_end: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# DATA SOURCE ENDPOINTS
# ============================================================================

@router.post("/data-sources", response_model=DataSourceResponse)
async def create_data_source(
    source_data: DataSourceCreate,
    auth: tuple = Depends(require_access("streaming_analytics", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new streaming data source"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    data_source = await service.create_data_source(
        organization_id=org_id,
        created_by_id=current_user.id,
        source_name=source_data.source_name,
        source_type=source_data.source_type,
        connection_config=source_data.connection_config,
        description=source_data.description
    )
    
    return DataSourceResponse.model_validate(data_source)


@router.get("/data-sources", response_model=List[DataSourceResponse])
async def list_data_sources(
    status: Optional[StreamStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List streaming data sources"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    sources = await service.list_data_sources(
        organization_id=org_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return [DataSourceResponse.model_validate(s) for s in sources]


@router.get("/data-sources/{source_id}", response_model=DataSourceResponse)
async def get_data_source(
    source_id: int,
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a data source by ID"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    source = await service.get_data_source(source_id, org_id)
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse.model_validate(source)


@router.patch("/data-sources/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: int,
    source_data: DataSourceUpdate,
    auth: tuple = Depends(require_access("streaming_analytics", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a data source"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    updates = source_data.model_dump(exclude_unset=True)
    source = await service.update_data_source(
        source_id=source_id,
        organization_id=org_id,
        **updates
    )
    
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return DataSourceResponse.model_validate(source)


# ============================================================================
# EVENT ENDPOINTS
# ============================================================================

@router.post("/events", response_model=EventResponse)
async def ingest_event(
    event_data: EventCreate,
    auth: tuple = Depends(require_access("streaming_analytics", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Ingest a streaming event"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    event = await service.ingest_event(
        data_source_id=event_data.data_source_id,
        organization_id=org_id,
        event_type=event_data.event_type,
        event_data=event_data.event_data,
        event_timestamp=event_data.event_timestamp
    )
    
    return EventResponse.model_validate(event)


@router.get("/events", response_model=List[EventResponse])
async def get_recent_events(
    data_source_id: Optional[int] = None,
    event_type: Optional[str] = None,
    minutes: int = Query(60, ge=1, le=1440),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get recent streaming events"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    events = await service.get_recent_events(
        organization_id=org_id,
        data_source_id=data_source_id,
        event_type=event_type,
        minutes=minutes,
        limit=limit
    )
    
    return [EventResponse.model_validate(e) for e in events]


# ============================================================================
# LIVE PREDICTION ENDPOINTS
# ============================================================================

@router.post("/predictions", response_model=LivePredictionResponse)
async def record_live_prediction(
    prediction_data: LivePredictionCreate,
    auth: tuple = Depends(require_access("streaming_analytics", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Record a live prediction"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    prediction = await service.record_live_prediction(
        organization_id=org_id,
        prediction_type=prediction_data.prediction_type,
        input_data=prediction_data.input_data,
        prediction_result=prediction_data.prediction_result,
        model_id=prediction_data.model_id,
        confidence_score=prediction_data.confidence_score,
        context=prediction_data.context
    )
    
    return LivePredictionResponse.model_validate(prediction)


@router.get("/predictions", response_model=List[LivePredictionResponse])
async def get_recent_predictions(
    prediction_type: Optional[str] = None,
    model_id: Optional[int] = None,
    minutes: int = Query(60, ge=1, le=1440),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get recent live predictions"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    predictions = await service.get_recent_predictions(
        organization_id=org_id,
        prediction_type=prediction_type,
        model_id=model_id,
        minutes=minutes,
        limit=limit
    )
    
    return [LivePredictionResponse.model_validate(p) for p in predictions]


# ============================================================================
# ALERT ENDPOINTS
# ============================================================================

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    auth: tuple = Depends(require_access("streaming_analytics", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a streaming alert"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    alert = await service.create_alert(
        organization_id=org_id,
        alert_type=alert_data.alert_type,
        alert_title=alert_data.alert_title,
        alert_message=alert_data.alert_message,
        severity=alert_data.severity,
        data_source_id=alert_data.data_source_id,
        alert_data=alert_data.alert_data
    )
    
    return AlertResponse.model_validate(alert)


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get streaming alerts"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    alerts = await service.get_alerts(
        organization_id=org_id,
        status=status,
        severity=severity,
        skip=skip,
        limit=limit
    )
    
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("/alerts/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_data: AlertAcknowledge,
    auth: tuple = Depends(require_access("streaming_analytics", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an alert"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    alert = await service.acknowledge_alert(
        alert_id=alert_data.alert_id,
        organization_id=org_id,
        acknowledged_by_id=current_user.id
    )
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.model_validate(alert)


@router.post("/alerts/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_data: AlertResolve,
    auth: tuple = Depends(require_access("streaming_analytics", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Resolve an alert"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    alert = await service.resolve_alert(
        alert_id=alert_data.alert_id,
        organization_id=org_id,
        resolved_by_id=current_user.id,
        resolution_notes=alert_data.resolution_notes
    )
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.model_validate(alert)


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@router.post("/metrics", response_model=MetricResponse)
async def record_metric(
    metric_data: MetricCreate,
    auth: tuple = Depends(require_access("streaming_analytics", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Record a streaming metric"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    metric = await service.record_metric(
        organization_id=org_id,
        metric_name=metric_data.metric_name,
        metric_value=metric_data.metric_value,
        aggregation_type=metric_data.aggregation_type,
        time_window=metric_data.time_window,
        window_start=metric_data.window_start,
        window_end=metric_data.window_end,
        data_source_id=metric_data.data_source_id,
        dimensions=metric_data.dimensions
    )
    
    return MetricResponse.model_validate(metric)


@router.get("/metrics", response_model=List[MetricResponse])
async def get_metrics(
    metric_name: Optional[str] = None,
    time_window: Optional[str] = None,
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get streaming metrics"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    metrics = await service.get_metrics(
        organization_id=org_id,
        metric_name=metric_name,
        time_window=time_window,
        limit=limit
    )
    
    return [MetricResponse.model_validate(m) for m in metrics]


# ============================================================================
# DASHBOARD ENDPOINT
# ============================================================================

@router.get("/dashboard")
async def get_dashboard_data(
    auth: tuple = Depends(require_access("streaming_analytics", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get streaming analytics dashboard data"""
    current_user, org_id = auth
    service = StreamingAnalyticsService(db)
    
    dashboard_data = await service.get_dashboard_data(org_id)
    
    return dashboard_data


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws/live-stream")
async def websocket_live_stream(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for live streaming data"""
    await websocket.accept()
    
    try:
        while True:
            # Keep connection alive and send updates
            # In a real implementation, this would stream actual data
            data = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()