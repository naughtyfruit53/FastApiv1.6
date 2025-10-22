# A/B Testing & Real-Time Streaming Analytics Guide

## Table of Contents

1. [Overview](#overview)
2. [A/B Testing Framework](#ab-testing-framework)
3. [Streaming Analytics](#streaming-analytics)
4. [Integration Guide](#integration-guide)
5. [API Reference](#api-reference)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive documentation for the A/B Testing and Real-Time Streaming Analytics features in the FastAPI ERP system.

### Key Features

- **A/B Testing**: Compare different AI model versions with statistical rigor
- **Real-Time Streaming**: Process and analyze data streams in real-time
- **Live Dashboards**: Visualize metrics, predictions, and alerts as they happen
- **WebSocket Support**: Maintain persistent connections for instant updates
- **Alert Management**: Automated alerting on anomalies and thresholds

---

## A/B Testing Framework

### Architecture

The A/B Testing framework consists of:

1. **Experiments**: Container for A/B tests
2. **Variants**: Different versions being tested (control, treatment)
3. **Assignments**: User-to-variant mappings
4. **Results**: Collected metrics and outcomes

### Experiment Lifecycle

```
DRAFT → RUNNING → PAUSED/COMPLETED → ARCHIVED
```

#### States Explained

- **DRAFT**: Experiment is being configured, not yet active
- **RUNNING**: Actively collecting data and assigning users
- **PAUSED**: Temporarily stopped, can be resumed
- **COMPLETED**: Data collection finished, ready for analysis
- **ARCHIVED**: Historical record, no longer active

### Creating Experiments

#### Backend API

```python
# Create experiment
POST /api/v1/ab-testing/experiments
{
    "experiment_name": "Model Version Comparison",
    "description": "Testing new ML model against baseline",
    "traffic_split": {
        "control": 50,
        "treatment": 50
    }
}
```

#### Frontend Usage

```typescript
import abTestingService from '@/services/abTestingService';

const experiment = await abTestingService.createExperiment({
    experiment_name: 'Model Version Comparison',
    description: 'Testing new ML model against baseline',
    traffic_split: { control: 50, treatment: 50 }
});
```

### Managing Variants

#### Creating Variants

```python
# Add variant to experiment
POST /api/v1/ab-testing/experiments/{experiment_id}/variants
{
    "variant_name": "Control",
    "variant_type": "control",
    "model_id": 123,
    "model_version": "v1.0",
    "traffic_percentage": 50.0
}
```

#### Variant Types

- **Control**: Baseline version (current production model)
- **Treatment**: New version being tested

### User Assignment

The system automatically assigns users to variants using:

1. **Deterministic Hashing**: Consistent assignment based on user ID or session
2. **Traffic Split**: Respects configured percentage splits
3. **Persistence**: Users remain in same variant across sessions

#### Assignment Logic

```python
# System automatically assigns on first request
assignment = await abTestingService.assignVariant(
    experiment_id=1,
    user_id=current_user.id
);
# Returns: { variant: {...}, assigned: true }
```

### Recording Results

Track experiment outcomes:

```python
# Record metric
POST /api/v1/ab-testing/results
{
    "experiment_id": 1,
    "variant_id": 2,
    "metric_name": "conversion_rate",
    "metric_value": 0.125,
    "metadata": {
        "session_duration": 240,
        "page_views": 5
    }
}
```

### Analyzing Results

#### Statistical Metrics

For each variant, the system calculates:

- **Sample Size**: Number of unique users
- **Mean**: Average metric value
- **Min/Max**: Range of values
- **Sum**: Total across all observations

#### Result Retrieval

```python
# Get aggregated results
GET /api/v1/ab-testing/experiments/{experiment_id}/results

Response:
{
    "experiment_id": 1,
    "experiment_name": "Model Version Comparison",
    "status": "completed",
    "variants": {
        "Control": {
            "sample_size": 1000,
            "metrics": {
                "conversion_rate": {
                    "count": 1000,
                    "mean": 0.105,
                    "min": 0.0,
                    "max": 1.0
                }
            }
        },
        "Treatment": {
            "sample_size": 1050,
            "metrics": {
                "conversion_rate": {
                    "count": 1050,
                    "mean": 0.125,
                    "min": 0.0,
                    "max": 1.0
                }
            }
        }
    }
}
```

### Best Practices

1. **Experiment Design**
   - Define clear success metrics upfront
   - Run for minimum 7 days
   - Aim for at least 1000 samples per variant

2. **Traffic Allocation**
   - Start with 50/50 split for initial tests
   - Use 90/10 for risky changes
   - Monitor for sample ratio mismatch

3. **Data Collection**
   - Record multiple metrics (primary and secondary)
   - Include metadata for deeper analysis
   - Implement proper error handling

4. **Analysis**
   - Check for statistical significance
   - Look for segment-specific effects
   - Document conclusions

---

## Streaming Analytics

### Architecture

The Streaming Analytics system consists of:

1. **Data Sources**: Connection to streaming data (Kafka, WebSocket, HTTP)
2. **Events**: Individual data points from streams
3. **Live Predictions**: Real-time model outputs
4. **Alerts**: Automated notifications on anomalies
5. **Metrics**: Aggregated time-series data

### Data Source Configuration

#### Kafka Source

```python
POST /api/v1/streaming-analytics/data-sources
{
    "source_name": "Production Events",
    "source_type": "kafka",
    "connection_config": {
        "bootstrap_servers": ["kafka-1:9092", "kafka-2:9092"],
        "topic": "production.events",
        "group_id": "erp-consumer",
        "auto_offset_reset": "latest"
    },
    "description": "Production event stream"
}
```

#### WebSocket Source

```python
POST /api/v1/streaming-analytics/data-sources
{
    "source_name": "Real-time Sensor Data",
    "source_type": "websocket",
    "connection_config": {
        "url": "wss://sensors.example.com/stream",
        "auth_token": "your-token-here"
    }
}
```

### Event Ingestion

#### Manual Event Ingestion

```python
POST /api/v1/streaming-analytics/events
{
    "data_source_id": 1,
    "event_type": "user_action",
    "event_data": {
        "action": "purchase",
        "amount": 99.99,
        "product_id": 456
    },
    "event_timestamp": "2024-10-22T10:30:00Z"
}
```

#### Event Processing

Events are:
1. Ingested via API or streaming source
2. Stored in database with processed=false
3. Processed by background workers
4. Marked as processed=true

### Live Predictions

Record model predictions in real-time:

```python
POST /api/v1/streaming-analytics/predictions
{
    "prediction_type": "customer_churn",
    "input_data": {
        "customer_id": 123,
        "recent_activity": 5,
        "days_since_purchase": 45
    },
    "prediction_result": {
        "churn_probability": 0.73,
        "risk_level": "high"
    },
    "model_id": 10,
    "confidence_score": 0.89
}
```

### Alert System

#### Creating Alerts

```python
POST /api/v1/streaming-analytics/alerts
{
    "alert_type": "anomaly_detection",
    "alert_title": "High Error Rate Detected",
    "alert_message": "Error rate exceeded 5% threshold",
    "severity": "warning",
    "data_source_id": 1,
    "alert_data": {
        "error_rate": 0.067,
        "threshold": 0.05
    }
}
```

#### Alert Severity Levels

- **INFO**: Informational, no action required
- **WARNING**: Potential issue, monitor closely
- **ERROR**: Issue requiring attention
- **CRITICAL**: Immediate action required

#### Managing Alerts

```python
# Acknowledge alert
POST /api/v1/streaming-analytics/alerts/acknowledge
{
    "alert_id": 123
}

# Resolve alert
POST /api/v1/streaming-analytics/alerts/resolve
{
    "alert_id": 123,
    "resolution_notes": "Issue resolved by restarting service"
}
```

### Metrics and Aggregation

#### Recording Metrics

```python
POST /api/v1/streaming-analytics/metrics
{
    "metric_name": "request_latency",
    "metric_value": 45.2,
    "aggregation_type": "avg",
    "time_window": "1m",
    "window_start": "2024-10-22T10:00:00Z",
    "window_end": "2024-10-22T10:01:00Z"
}
```

#### Aggregation Types

- **sum**: Total of all values
- **avg**: Average value
- **min**: Minimum value
- **max**: Maximum value
- **count**: Number of observations

#### Time Windows

- **1m**: 1-minute aggregations
- **5m**: 5-minute aggregations
- **15m**: 15-minute aggregations
- **1h**: 1-hour aggregations
- **1d**: Daily aggregations

### WebSocket Connection

#### Frontend Connection

```typescript
import streamingAnalyticsService from '@/services/streamingAnalyticsService';

// Create WebSocket connection
const ws = streamingAnalyticsService.createWebSocketConnection((data) => {
    console.log('Received:', data);
    // Handle real-time updates
    if (data.type === 'event') {
        updateEvents(data.event);
    } else if (data.type === 'alert') {
        showAlert(data.alert);
    }
});
```

#### Message Types

The WebSocket sends various message types:

```javascript
// Heartbeat
{ type: "heartbeat", timestamp: "2024-10-22T10:30:00Z" }

// Event notification
{ type: "event", event: {...} }

// Alert notification
{ type: "alert", alert: {...} }

// Metric update
{ type: "metric", metric: {...} }
```

---

## Integration Guide

### Backend Integration

#### 1. Import Required Modules

```python
from app.services.ab_testing_service import ABTestingService
from app.services.streaming_analytics_service import StreamingAnalyticsService
from sqlalchemy.orm import Session
```

#### 2. Use in Your Code

```python
def predict_with_ab_test(
    db: Session,
    user_id: int,
    experiment_id: int,
    input_data: dict
):
    # Get A/B test service
    ab_service = ABTestingService(db)
    
    # Assign user to variant
    variant = ab_service.assign_variant(
        experiment_id=experiment_id,
        organization_id=current_org_id,
        user_id=user_id
    )
    
    # Use the assigned model
    prediction = run_model(variant.model_id, input_data)
    
    # Record result
    ab_service.record_result(
        experiment_id=experiment_id,
        variant_id=variant.id,
        metric_name="prediction_accuracy",
        metric_value=prediction.confidence,
        user_id=user_id
    )
    
    return prediction
```

### Frontend Integration

#### 1. Import Services

```typescript
import abTestingService from '@/services/abTestingService';
import streamingAnalyticsService from '@/services/streamingAnalyticsService';
```

#### 2. Use in Components

```typescript
const MyComponent = () => {
    const [experiments, setExperiments] = useState([]);
    
    useEffect(() => {
        loadExperiments();
    }, []);
    
    const loadExperiments = async () => {
        const data = await abTestingService.listExperiments();
        setExperiments(data);
    };
    
    return (
        <div>
            {experiments.map(exp => (
                <ExperimentCard key={exp.id} experiment={exp} />
            ))}
        </div>
    );
};
```

---

## API Reference

### A/B Testing Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ab-testing/experiments` | POST | Create experiment |
| `/api/v1/ab-testing/experiments` | GET | List experiments |
| `/api/v1/ab-testing/experiments/{id}` | GET | Get experiment |
| `/api/v1/ab-testing/experiments/{id}` | PATCH | Update experiment |
| `/api/v1/ab-testing/experiments/{id}/start` | POST | Start experiment |
| `/api/v1/ab-testing/experiments/{id}/pause` | POST | Pause experiment |
| `/api/v1/ab-testing/experiments/{id}/complete` | POST | Complete experiment |
| `/api/v1/ab-testing/experiments/{id}/variants` | POST | Create variant |
| `/api/v1/ab-testing/experiments/{id}/variants` | GET | List variants |
| `/api/v1/ab-testing/assign` | POST | Assign variant |
| `/api/v1/ab-testing/results` | POST | Record result |
| `/api/v1/ab-testing/experiments/{id}/results` | GET | Get results |

### Streaming Analytics Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/streaming-analytics/data-sources` | POST | Create data source |
| `/api/v1/streaming-analytics/data-sources` | GET | List data sources |
| `/api/v1/streaming-analytics/data-sources/{id}` | GET | Get data source |
| `/api/v1/streaming-analytics/data-sources/{id}` | PATCH | Update data source |
| `/api/v1/streaming-analytics/events` | POST | Ingest event |
| `/api/v1/streaming-analytics/events` | GET | Get recent events |
| `/api/v1/streaming-analytics/predictions` | POST | Record prediction |
| `/api/v1/streaming-analytics/predictions` | GET | Get predictions |
| `/api/v1/streaming-analytics/alerts` | POST | Create alert |
| `/api/v1/streaming-analytics/alerts` | GET | List alerts |
| `/api/v1/streaming-analytics/alerts/acknowledge` | POST | Acknowledge alert |
| `/api/v1/streaming-analytics/alerts/resolve` | POST | Resolve alert |
| `/api/v1/streaming-analytics/metrics` | POST | Record metric |
| `/api/v1/streaming-analytics/metrics` | GET | Get metrics |
| `/api/v1/streaming-analytics/dashboard` | GET | Dashboard data |
| `/api/v1/streaming-analytics/ws/live-stream` | WebSocket | Live connection |

---

## Best Practices

### A/B Testing

1. **Statistical Rigor**
   - Use appropriate sample sizes
   - Run tests long enough for statistical significance
   - Avoid peeking at results too early

2. **Experiment Isolation**
   - Run one experiment at a time when possible
   - Document interactions between concurrent experiments
   - Use consistent user assignment

3. **Metrics Selection**
   - Choose metrics aligned with business goals
   - Track both primary and secondary metrics
   - Monitor for unexpected side effects

4. **Documentation**
   - Document hypothesis and expected outcomes
   - Record all configuration details
   - Share results with stakeholders

### Streaming Analytics

1. **Performance**
   - Use appropriate batch sizes for ingestion
   - Implement backpressure handling
   - Monitor memory usage

2. **Reliability**
   - Implement retry logic for failed events
   - Use dead letter queues for problematic events
   - Monitor data source health

3. **Scalability**
   - Partition data by organization/source
   - Use time-based retention policies
   - Archive old data regularly

4. **Monitoring**
   - Set up alerts for high error rates
   - Monitor processing lag
   - Track throughput metrics

---

## Troubleshooting

### A/B Testing Issues

#### Experiment Won't Start

**Problem**: Cannot start experiment
**Solutions**:
- Ensure at least 2 variants are configured
- Check that traffic percentages sum to 100%
- Verify experiment is in DRAFT status

#### Uneven Traffic Distribution

**Problem**: Traffic not splitting evenly
**Solutions**:
- Check variant traffic_percentage settings
- Verify user assignment logic
- Monitor for biased data sources

#### Missing Results

**Problem**: No results showing for experiment
**Solutions**:
- Confirm results are being recorded via API
- Check experiment status is RUNNING
- Verify user assignments are happening

### Streaming Analytics Issues

#### WebSocket Connection Fails

**Problem**: Cannot establish WebSocket connection
**Solutions**:
- Check browser console for errors
- Verify WebSocket endpoint is accessible
- Check authentication token

#### High Event Processing Lag

**Problem**: Events not processing in real-time
**Solutions**:
- Check worker process status
- Increase worker capacity
- Optimize event processing logic

#### Alerts Not Triggering

**Problem**: Expected alerts not appearing
**Solutions**:
- Verify alert thresholds are correctly configured
- Check data is flowing through system
- Review alert creation logic

---

## Support

For additional support:

- **Documentation**: Check this guide and USER_GUIDE.md
- **API Docs**: Visit `/api/docs` for interactive API documentation
- **Support**: Contact support@tritiq.com
- **Community**: Join our user forums

---

*Last Updated: October 2024*
*Version: 1.7.0*
