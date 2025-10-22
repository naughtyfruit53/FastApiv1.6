# Advanced Analytics Training Guide

## Overview

This comprehensive guide covers the advanced ML/AI analytics features in FastAPI v1.6, including predictive modeling, anomaly detection, and external data integration.

## Table of Contents

1. [Introduction](#introduction)
2. [Predictive Models](#predictive-models)
3. [Anomaly Detection](#anomaly-detection)
4. [External Data Sources](#external-data-sources)
5. [Making Predictions](#making-predictions)
6. [Dashboard and Visualization](#dashboard-and-visualization)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

The Advanced ML/AI Analytics module provides powerful machine learning capabilities to:
- Forecast future trends and outcomes
- Detect anomalies in business operations
- Integrate external data sources for enriched analytics
- Generate automated insights and recommendations

### Key Features

- **Predictive Models**: Build and deploy ML models for forecasting
- **Anomaly Detection**: Real-time monitoring for unusual patterns
- **Data Integration**: Connect external data sources
- **Role-Based Access**: Secure access control for analytics features
- **Performance Monitoring**: Track model accuracy and predictions

## Predictive Models

### Types of Predictive Models

1. **Sales Forecast**: Predict future sales revenue and volume
2. **Demand Prediction**: Forecast product demand and inventory needs
3. **Churn Prediction**: Identify customers at risk of churning
4. **Revenue Forecast**: Project future revenue streams
5. **Inventory Optimization**: Optimize stock levels
6. **Customer Lifetime Value**: Calculate CLV predictions
7. **Price Optimization**: Determine optimal pricing strategies
8. **Lead Scoring**: Score and prioritize sales leads

### Creating a Predictive Model

#### Step 1: Define the Model

Navigate to **Analytics > Advanced Analytics > Predictive Models** and click "Create Model".

```json
{
  "model_name": "sales_forecast_2024",
  "model_type": "sales_forecast",
  "description": "Monthly sales forecasting model",
  "algorithm": "random_forest",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 2
  },
  "feature_engineering": {
    "normalize": true,
    "handle_missing": "mean"
  },
  "training_config": {
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
  },
  "validation_split": 0.2,
  "test_split": 0.1
}
```

#### Step 2: Configure Features

Define which data fields to use as features:
- Historical sales data
- Seasonal indicators
- Marketing spend
- Economic indicators
- Customer demographics

#### Step 3: Train the Model

Click "Train Model" to start the training process. Monitor:
- Training progress
- Validation accuracy
- Loss metrics
- Estimated completion time

#### Step 4: Evaluate Performance

Review model performance metrics:
- **Accuracy Score**: Overall prediction accuracy
- **Precision**: Correctness of positive predictions
- **Recall**: Coverage of actual positives
- **F1 Score**: Harmonic mean of precision and recall
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **R² Score**: Coefficient of determination

#### Step 5: Deploy the Model

Once satisfied with performance:
1. Click "Deploy Model"
2. Set deployment configuration
3. Activate for production use

### Managing Predictive Models

#### Viewing Models

Access all models through the dashboard:
```
GET /api/v1/ml-analytics/models/predictive
```

Filter by:
- Model type
- Active/inactive status
- Performance metrics

#### Updating Models

Modify model configuration:
- Update hyperparameters
- Adjust feature engineering
- Change training settings
- Activate/deactivate model

#### Retraining Models

Schedule regular retraining to maintain accuracy:
1. Set retraining frequency (e.g., weekly, monthly)
2. Automatic retraining based on performance degradation
3. Manual retraining on demand

## Anomaly Detection

### Types of Anomalies

1. **Revenue Anomaly**: Unusual revenue patterns
2. **Inventory Anomaly**: Stock level irregularities
3. **Transaction Anomaly**: Suspicious transaction patterns
4. **Customer Behavior Anomaly**: Unusual customer activity
5. **Operational Anomaly**: Process inefficiencies
6. **Quality Anomaly**: Product quality issues

### Setting Up Anomaly Detection

#### Step 1: Create Detection Configuration

```json
{
  "detection_name": "revenue_monitoring",
  "anomaly_type": "revenue_anomaly",
  "description": "Monitor daily revenue for anomalies",
  "algorithm": "isolation_forest",
  "detection_config": {
    "contamination": 0.1,
    "n_estimators": 100
  },
  "threshold_config": {
    "severity_thresholds": {
      "low": 0.5,
      "medium": 0.7,
      "high": 0.85,
      "critical": 0.95
    }
  },
  "monitored_metrics": [
    "daily_revenue",
    "transaction_count",
    "average_order_value"
  ],
  "detection_frequency": "hourly"
}
```

#### Step 2: Configure Thresholds

Set appropriate thresholds based on:
- Historical data patterns
- Business tolerance for false positives
- Severity classification criteria
- Alert notification requirements

#### Step 3: Enable Monitoring

Activate the anomaly detection model to start monitoring.

### Responding to Anomalies

#### Viewing Detected Anomalies

Access anomalies through:
```
GET /api/v1/ml-analytics/anomaly-detection/results
```

Filter by:
- Severity level (low, medium, high, critical)
- Resolution status
- Detection model
- Date range

#### Analyzing Anomalies

Each anomaly includes:
- **Detected At**: Timestamp of detection
- **Severity**: Classification of impact
- **Anomaly Score**: Confidence level (0-1)
- **Affected Data**: Specific data points
- **Expected Range**: Normal value range
- **Actual Value**: Observed value
- **Context**: Additional contextual information
- **Root Cause Analysis**: Potential causes

#### Resolving Anomalies

To resolve an anomaly:

1. Investigate the anomaly details
2. Determine if it's a genuine issue or false positive
3. Take corrective action if needed
4. Mark as resolved with notes

```json
{
  "resolution_notes": "Revenue spike due to promotional campaign",
  "is_false_positive": false,
  "false_positive_reason": null
}
```

#### False Positive Management

Mark anomalies as false positives to improve detection:
- System learns from feedback
- Reduces future false positives
- Improves detection accuracy over time

## External Data Sources

### Supported Data Source Types

1. **Database**: Direct database connections
2. **API**: RESTful API integrations
3. **File Upload**: CSV, Excel, JSON files
4. **Cloud Storage**: S3, Azure Blob, Google Cloud Storage
5. **Streaming**: Real-time data streams

### Connecting a Data Source

#### Step 1: Configure Connection

```json
{
  "source_name": "google_analytics",
  "source_type": "api",
  "description": "Google Analytics data for customer insights",
  "connection_config": {
    "base_url": "https://analytics.googleapis.com/v4",
    "endpoints": {
      "traffic": "/reports/realtime",
      "conversions": "/reports/conversions"
    }
  },
  "authentication_config": {
    "type": "oauth2",
    "credentials": "encrypted_token_here"
  },
  "data_schema": {
    "fields": [
      {"name": "sessions", "type": "integer"},
      {"name": "pageviews", "type": "integer"},
      {"name": "conversion_rate", "type": "float"}
    ]
  },
  "field_mapping": {
    "external_field": "internal_field"
  },
  "sync_frequency": "hourly"
}
```

#### Step 2: Test Connection

Verify connectivity and data retrieval before activation.

#### Step 3: Configure Sync Schedule

Set sync frequency:
- **Real-time**: Continuous streaming
- **Hourly**: Every hour
- **Daily**: Once per day
- **Weekly**: Once per week

#### Step 4: Monitor Sync Status

Track synchronization:
- Last sync timestamp
- Records synced
- Sync duration
- Errors and warnings

### Data Mapping

Map external fields to internal schema:
- Field name mapping
- Data type conversion
- Value transformation rules
- Default values for missing data

## Making Predictions

### Single Prediction

Make a prediction using a trained model:

```json
POST /api/v1/ml-analytics/predictions
{
  "model_id": 1,
  "input_data": {
    "historical_sales": 150000,
    "marketing_spend": 25000,
    "season": "Q4",
    "economic_indicator": 1.05
  },
  "context_metadata": {
    "request_source": "dashboard",
    "user_notes": "Year-end forecast"
  }
}
```

Response:
```json
{
  "prediction_id": 12345,
  "model_id": 1,
  "predicted_value": {
    "forecasted_sales": 165000,
    "prediction_range": {
      "lower_bound": 155000,
      "upper_bound": 175000
    }
  },
  "confidence_score": 0.87,
  "prediction_timestamp": "2024-01-15T10:30:00Z"
}
```

### Batch Predictions

For multiple predictions:

```javascript
const predictions = await Promise.all(
  inputDataArray.map(data => 
    mlAnalyticsService.makePrediction({
      model_id: modelId,
      input_data: data
    })
  )
);
```

### Viewing Prediction History

Track all predictions:
```
GET /api/v1/ml-analytics/predictions/history?model_id=1&limit=100
```

Analyze:
- Prediction accuracy over time
- Actual vs. predicted values
- Model performance trends
- Common prediction errors

## Dashboard and Visualization

### ML Analytics Dashboard

The dashboard provides a comprehensive overview:

#### Key Metrics
- Total models (active and inactive)
- Total predictions made
- Anomalies detected and unresolved
- Active data sources

#### Model Performance
- Individual model accuracy
- Prediction volume by model
- Training status and history
- Deployment timeline

#### Recent Anomalies
- Latest detected anomalies
- Severity distribution
- Resolution status
- Trending patterns

#### Prediction Trends
- Daily prediction volume
- Model usage statistics
- Accuracy trends over time

### Customizing Views

Filter and customize dashboard views:
- Date range selection
- Model type filtering
- Anomaly severity filtering
- Performance metric selection

## Best Practices

### Model Development

1. **Start Simple**: Begin with basic models and iterate
2. **Feature Engineering**: Invest time in quality features
3. **Validation**: Always use separate validation and test sets
4. **Regular Retraining**: Schedule periodic model updates
5. **Monitor Performance**: Track accuracy and drift over time

### Anomaly Detection

1. **Baseline Establishment**: Understand normal patterns first
2. **Threshold Tuning**: Adjust based on business requirements
3. **False Positive Feedback**: Mark and learn from false positives
4. **Response Procedures**: Define clear resolution workflows
5. **Regular Review**: Periodically review detection configurations

### Data Integration

1. **Security First**: Encrypt sensitive credentials
2. **Test Connections**: Validate before production use
3. **Error Handling**: Implement robust error recovery
4. **Monitoring**: Track sync health and performance
5. **Data Quality**: Validate incoming data quality

### Performance Optimization

1. **Model Selection**: Choose appropriate algorithms
2. **Hyperparameter Tuning**: Optimize model parameters
3. **Feature Selection**: Remove irrelevant features
4. **Batch Processing**: Use batch predictions when possible
5. **Caching**: Cache frequently used predictions

## Troubleshooting

### Common Issues

#### Model Training Failures

**Problem**: Model training fails or doesn't complete

**Solutions**:
- Check data quality and completeness
- Reduce model complexity (fewer features, simpler algorithm)
- Increase timeout settings
- Review error logs for specific issues

#### Poor Prediction Accuracy

**Problem**: Model predictions are inaccurate

**Solutions**:
- Retrain with more recent data
- Add more relevant features
- Try different algorithms
- Adjust hyperparameters
- Increase training data volume

#### Too Many False Positives

**Problem**: Anomaly detection generates excessive false positives

**Solutions**:
- Adjust detection thresholds
- Refine monitored metrics
- Improve baseline data quality
- Mark false positives to help the system learn
- Consider different detection algorithms

#### Data Sync Issues

**Problem**: External data source sync fails

**Solutions**:
- Verify credentials and authentication
- Check network connectivity
- Review API rate limits
- Validate data schema compatibility
- Check error logs for specific failure reasons

### Getting Help

For additional support:
1. Check system logs in `/var/log/fastapi/`
2. Review API documentation at `/docs`
3. Contact technical support with:
   - Error messages and logs
   - Steps to reproduce the issue
   - System configuration details
   - Expected vs. actual behavior

## Advanced Topics

### Custom Algorithm Integration

For advanced users, integrate custom ML algorithms:

1. Implement algorithm interface
2. Register with model registry
3. Configure hyperparameters
4. Test with validation data
5. Deploy to production

### API Integration

Integrate ML analytics into external systems:

```python
import requests

# Make prediction from external system
response = requests.post(
    'https://your-api.com/api/v1/ml-analytics/predictions',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'model_id': 1,
        'input_data': {...}
    }
)
prediction = response.json()
```

### Scheduled Predictions

Set up automated prediction schedules:
1. Define prediction frequency
2. Configure input data sources
3. Set up result storage
4. Enable notifications for significant predictions

### Model Versioning

Manage multiple model versions:
- Track version history
- Compare performance across versions
- Rollback to previous versions
- A/B test different model versions

## Conclusion

The Advanced ML/AI Analytics module provides powerful tools for predictive insights and automated decision-making. By following this guide and best practices, you can leverage machine learning to drive business value and improve operational efficiency.

For updates and additional resources, refer to the main [User Guide](USER_GUIDE.md) and [API Documentation](../API_DOCUMENTATION.md).
