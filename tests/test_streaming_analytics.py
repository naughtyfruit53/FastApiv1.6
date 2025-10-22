"""
Tests for Streaming Analytics functionality
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.streaming_analytics import (
    StreamingDataSource,
    StreamingEvent,
    LivePrediction,
    StreamingAlert,
    StreamingMetric,
    StreamStatus,
    AlertSeverity,
    AlertStatus,
)
from app.services.streaming_analytics_service import StreamingAnalyticsService


@pytest.fixture
def streaming_service(db_session: Session):
    """Create a StreamingAnalyticsService instance"""
    return StreamingAnalyticsService(db_session)


@pytest.fixture
def sample_data_source(db_session: Session, sample_organization, sample_user):
    """Create a sample streaming data source"""
    source = StreamingDataSource(
        organization_id=sample_organization.id,
        created_by_id=sample_user.id,
        source_name="Test Source",
        source_type="kafka",
        description="Test data source",
        connection_config={"bootstrap_servers": ["localhost:9092"], "topic": "test"},
        status=StreamStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def sample_event(db_session: Session, sample_data_source, sample_organization):
    """Create a sample streaming event"""
    event = StreamingEvent(
        data_source_id=sample_data_source.id,
        organization_id=sample_organization.id,
        event_type="user_action",
        event_data={"action": "click", "item_id": 123},
        event_timestamp=datetime.utcnow(),
        processed=False,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


class TestStreamingAnalyticsService:
    """Test cases for StreamingAnalyticsService"""

    def test_create_data_source(self, streaming_service, sample_organization, sample_user):
        """Test creating a data source"""
        source = streaming_service.create_data_source(
            organization_id=sample_organization.id,
            created_by_id=sample_user.id,
            source_name="New Source",
            source_type="websocket",
            connection_config={"url": "wss://example.com"},
            description="Test WebSocket source",
        )

        assert source.id is not None
        assert source.source_name == "New Source"
        assert source.source_type == "websocket"
        assert source.status == StreamStatus.ACTIVE
        assert source.is_active is True

    def test_get_data_source(self, streaming_service, sample_data_source, sample_organization):
        """Test getting a data source"""
        source = streaming_service.get_data_source(
            sample_data_source.id, sample_organization.id
        )

        assert source is not None
        assert source.id == sample_data_source.id
        assert source.source_name == sample_data_source.source_name

    def test_list_data_sources(
        self, streaming_service, sample_data_source, sample_organization
    ):
        """Test listing data sources"""
        sources = streaming_service.list_data_sources(
            organization_id=sample_organization.id
        )

        assert len(sources) > 0
        assert any(s.id == sample_data_source.id for s in sources)

    def test_list_data_sources_by_status(
        self, streaming_service, sample_data_source, sample_organization
    ):
        """Test listing data sources filtered by status"""
        sources = streaming_service.list_data_sources(
            organization_id=sample_organization.id, status=StreamStatus.ACTIVE
        )

        assert len(sources) > 0
        assert all(s.status == StreamStatus.ACTIVE for s in sources)

    def test_update_data_source(
        self, streaming_service, sample_data_source, sample_organization
    ):
        """Test updating a data source"""
        updated = streaming_service.update_data_source(
            source_id=sample_data_source.id,
            organization_id=sample_organization.id,
            description="Updated description",
            status=StreamStatus.PAUSED,
        )

        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.status == StreamStatus.PAUSED

    def test_update_data_source_stats(
        self, streaming_service, sample_data_source, sample_organization
    ):
        """Test updating data source statistics"""
        initial_count = sample_data_source.message_count

        updated = streaming_service.update_data_source_stats(
            source_id=sample_data_source.id,
            organization_id=sample_organization.id,
            increment_messages=True,
        )

        assert updated is not None
        assert updated.message_count == initial_count + 1
        assert updated.last_message_at is not None

    def test_ingest_event(self, streaming_service, sample_data_source, sample_organization):
        """Test ingesting an event"""
        event = streaming_service.ingest_event(
            data_source_id=sample_data_source.id,
            organization_id=sample_organization.id,
            event_type="purchase",
            event_data={"product_id": 456, "amount": 99.99},
        )

        assert event.id is not None
        assert event.event_type == "purchase"
        assert event.processed is False
        assert event.event_data["product_id"] == 456

    def test_get_recent_events(
        self, streaming_service, sample_event, sample_organization
    ):
        """Test getting recent events"""
        events = streaming_service.get_recent_events(
            organization_id=sample_organization.id, minutes=60
        )

        assert len(events) > 0
        assert any(e.id == sample_event.id for e in events)

    def test_get_recent_events_by_type(
        self, streaming_service, sample_event, sample_organization
    ):
        """Test getting recent events filtered by type"""
        events = streaming_service.get_recent_events(
            organization_id=sample_organization.id,
            event_type="user_action",
            minutes=60,
        )

        assert len(events) > 0
        assert all(e.event_type == "user_action" for e in events)

    def test_mark_event_processed(
        self, streaming_service, sample_event, sample_organization
    ):
        """Test marking an event as processed"""
        processed = streaming_service.mark_event_processed(
            sample_event.id, sample_organization.id
        )

        assert processed is not None
        assert processed.processed is True
        assert processed.processed_at is not None

    def test_record_live_prediction(self, streaming_service, sample_organization):
        """Test recording a live prediction"""
        prediction = streaming_service.record_live_prediction(
            organization_id=sample_organization.id,
            prediction_type="churn_prediction",
            input_data={"customer_id": 789, "recent_activity": 3},
            prediction_result={"churn_probability": 0.65},
            confidence_score=0.85,
        )

        assert prediction.id is not None
        assert prediction.prediction_type == "churn_prediction"
        assert prediction.confidence_score == 0.85

    def test_get_recent_predictions(self, streaming_service, sample_organization):
        """Test getting recent predictions"""
        # Create some predictions
        streaming_service.record_live_prediction(
            organization_id=sample_organization.id,
            prediction_type="test_prediction",
            input_data={"test": "data"},
            prediction_result={"result": "success"},
        )

        predictions = streaming_service.get_recent_predictions(
            organization_id=sample_organization.id, minutes=60
        )

        assert len(predictions) > 0

    def test_create_alert(self, streaming_service, sample_organization):
        """Test creating an alert"""
        alert = streaming_service.create_alert(
            organization_id=sample_organization.id,
            alert_type="high_error_rate",
            alert_title="Error Rate Alert",
            alert_message="Error rate exceeded threshold",
            severity=AlertSeverity.WARNING,
        )

        assert alert.id is not None
        assert alert.alert_title == "Error Rate Alert"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.OPEN

    def test_get_alerts(self, streaming_service, sample_organization):
        """Test getting alerts"""
        # Create an alert
        streaming_service.create_alert(
            organization_id=sample_organization.id,
            alert_type="test_alert",
            alert_title="Test Alert",
            alert_message="Test message",
            severity=AlertSeverity.INFO,
        )

        alerts = streaming_service.get_alerts(organization_id=sample_organization.id)

        assert len(alerts) > 0

    def test_get_alerts_by_severity(self, streaming_service, sample_organization):
        """Test getting alerts filtered by severity"""
        # Create alerts with different severities
        streaming_service.create_alert(
            organization_id=sample_organization.id,
            alert_type="test",
            alert_title="Critical Alert",
            alert_message="Critical",
            severity=AlertSeverity.CRITICAL,
        )

        alerts = streaming_service.get_alerts(
            organization_id=sample_organization.id, severity=AlertSeverity.CRITICAL
        )

        assert len(alerts) > 0
        assert all(a.severity == AlertSeverity.CRITICAL for a in alerts)

    def test_acknowledge_alert(self, streaming_service, sample_organization, sample_user):
        """Test acknowledging an alert"""
        # Create an alert
        alert = streaming_service.create_alert(
            organization_id=sample_organization.id,
            alert_type="test",
            alert_title="Test Alert",
            alert_message="Test",
            severity=AlertSeverity.INFO,
        )

        # Acknowledge it
        acknowledged = streaming_service.acknowledge_alert(
            alert_id=alert.id,
            organization_id=sample_organization.id,
            acknowledged_by_id=sample_user.id,
        )

        assert acknowledged is not None
        assert acknowledged.status == AlertStatus.ACKNOWLEDGED
        assert acknowledged.acknowledged_by_id == sample_user.id
        assert acknowledged.acknowledged_at is not None

    def test_resolve_alert(self, streaming_service, sample_organization, sample_user):
        """Test resolving an alert"""
        # Create an alert
        alert = streaming_service.create_alert(
            organization_id=sample_organization.id,
            alert_type="test",
            alert_title="Test Alert",
            alert_message="Test",
            severity=AlertSeverity.INFO,
        )

        # Resolve it
        resolved = streaming_service.resolve_alert(
            alert_id=alert.id,
            organization_id=sample_organization.id,
            resolved_by_id=sample_user.id,
            resolution_notes="Fixed the issue",
        )

        assert resolved is not None
        assert resolved.status == AlertStatus.RESOLVED
        assert resolved.resolved_by_id == sample_user.id
        assert resolved.resolved_at is not None
        assert resolved.resolution_notes == "Fixed the issue"

    def test_record_metric(self, streaming_service, sample_organization):
        """Test recording a metric"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)

        metric = streaming_service.record_metric(
            organization_id=sample_organization.id,
            metric_name="request_count",
            metric_value=150.0,
            aggregation_type="sum",
            time_window="1m",
            window_start=window_start,
            window_end=now,
        )

        assert metric.id is not None
        assert metric.metric_name == "request_count"
        assert metric.metric_value == 150.0
        assert metric.aggregation_type == "sum"

    def test_get_metrics(self, streaming_service, sample_organization):
        """Test getting metrics"""
        # Create some metrics
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)

        streaming_service.record_metric(
            organization_id=sample_organization.id,
            metric_name="test_metric",
            metric_value=100.0,
            aggregation_type="avg",
            time_window="1m",
            window_start=window_start,
            window_end=now,
        )

        metrics = streaming_service.get_metrics(
            organization_id=sample_organization.id, metric_name="test_metric"
        )

        assert len(metrics) > 0

    def test_get_dashboard_data(self, streaming_service, sample_organization):
        """Test getting dashboard data"""
        dashboard = streaming_service.get_dashboard_data(sample_organization.id)

        assert dashboard is not None
        assert "active_data_sources" in dashboard
        assert "recent_events_1h" in dashboard
        assert "open_alerts" in dashboard
        assert "recent_predictions_1h" in dashboard
        assert "timestamp" in dashboard


class TestStreamingAnalyticsModels:
    """Test cases for Streaming Analytics database models"""

    def test_data_source_creation(self, db_session, sample_organization, sample_user):
        """Test creating a data source model"""
        source = StreamingDataSource(
            organization_id=sample_organization.id,
            created_by_id=sample_user.id,
            source_name="Model Test Source",
            source_type="kafka",
            connection_config={"test": "config"},
            status=StreamStatus.ACTIVE,
            is_active=True,
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)

        assert source.id is not None
        assert source.created_at is not None

    def test_event_creation(self, db_session, sample_data_source, sample_organization):
        """Test creating an event model"""
        event = StreamingEvent(
            data_source_id=sample_data_source.id,
            organization_id=sample_organization.id,
            event_type="test_event",
            event_data={"test": "data"},
            event_timestamp=datetime.utcnow(),
            processed=False,
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)

        assert event.id is not None
        assert event.received_at is not None

    def test_prediction_creation(self, db_session, sample_organization):
        """Test creating a live prediction model"""
        prediction = LivePrediction(
            organization_id=sample_organization.id,
            prediction_type="test_prediction",
            input_data={"input": "data"},
            prediction_result={"result": "value"},
            confidence_score=0.9,
        )
        db_session.add(prediction)
        db_session.commit()
        db_session.refresh(prediction)

        assert prediction.id is not None
        assert prediction.predicted_at is not None

    def test_alert_creation(self, db_session, sample_organization):
        """Test creating an alert model"""
        alert = StreamingAlert(
            organization_id=sample_organization.id,
            alert_type="test_alert",
            alert_title="Test Alert",
            alert_message="Test message",
            severity=AlertSeverity.INFO,
            status=AlertStatus.OPEN,
        )
        db_session.add(alert)
        db_session.commit()
        db_session.refresh(alert)

        assert alert.id is not None
        assert alert.triggered_at is not None

    def test_metric_creation(self, db_session, sample_organization):
        """Test creating a metric model"""
        now = datetime.utcnow()
        metric = StreamingMetric(
            organization_id=sample_organization.id,
            metric_name="test_metric",
            metric_value=123.45,
            aggregation_type="avg",
            time_window="1m",
            window_start=now - timedelta(minutes=1),
            window_end=now,
        )
        db_session.add(metric)
        db_session.commit()
        db_session.refresh(metric)

        assert metric.id is not None
        assert metric.calculated_at is not None
