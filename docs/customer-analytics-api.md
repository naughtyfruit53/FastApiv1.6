# Customer Analytics API Documentation

## Overview

The Customer Analytics API provides comprehensive insights and metrics for customer data within the multi-tenant ERP system. This module calculates key performance indicators, interaction patterns, and segment analytics while maintaining strict organizational data isolation.

## Features

- **Customer Metrics**: Total interactions, last interaction date, interaction type breakdown
- **Segment Analytics**: Customer distribution, interaction patterns by segment
- **Organization Summary**: High-level analytics across all customers
- **Dashboard Metrics**: Quick KPIs for dashboard display
- **Multi-tenant Isolation**: All data is automatically scoped to user's organization
- **Performance Optimized**: Uses existing database indexes for fast queries

## API Endpoints

### Customer Analytics

#### Get Customer Analytics
```http
GET /api/v1/analytics/customers/{customer_id}/analytics
```

Retrieve comprehensive analytics for a specific customer.

**Parameters:**
- `customer_id` (path, required): Customer ID
- `include_recent_interactions` (query, optional): Include recent interactions (default: true)
- `recent_interactions_limit` (query, optional): Number of recent interactions (1-20, default: 5)

**Response:**
```json
{
  "customer_id": 123,
  "customer_name": "Acme Corp",
  "total_interactions": 15,
  "last_interaction_date": "2024-01-15T10:30:00Z",
  "interaction_types": {
    "call": 5,
    "email": 7,
    "meeting": 3
  },
  "interaction_status": {
    "completed": 12,
    "pending": 2,
    "in_progress": 1
  },
  "segments": [
    {
      "segment_name": "premium",
      "segment_value": 150.0,
      "assigned_date": "2024-01-01T00:00:00Z",
      "description": "Premium customer"
    }
  ],
  "recent_interactions": [
    {
      "interaction_type": "call",
      "subject": "Product inquiry",
      "status": "completed",
      "interaction_date": "2024-01-15T10:30:00Z"
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

### Segment Analytics

#### Get Segment Analytics
```http
GET /api/v1/analytics/segments/{segment_name}/analytics
```

Retrieve analytics for all customers in a specific segment.

**Parameters:**
- `segment_name` (path, required): Segment name (e.g., "premium", "vip")
- `include_timeline` (query, optional): Include activity timeline (default: true)
- `timeline_days` (query, optional): Number of days for timeline (7-365, default: 30)

**Response:**
```json
{
  "segment_name": "premium",
  "total_customers": 25,
  "total_interactions": 150,
  "avg_interactions_per_customer": 6.0,
  "interaction_distribution": {
    "call": 60,
    "email": 70,
    "meeting": 20
  },
  "activity_timeline": [
    {
      "date": "2024-01-15",
      "interaction_count": 8
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

#### List Available Segments
```http
GET /api/v1/analytics/segments
```

Get list of available customer segments in the organization.

**Response:**
```json
["premium", "vip", "regular", "new", "at_risk"]
```

### Organization Analytics

#### Get Organization Summary
```http
GET /api/v1/analytics/organization/summary
```

Get high-level analytics summary for the entire organization.

**Response:**
```json
{
  "organization_id": 1,
  "total_customers": 100,
  "total_interactions": 500,
  "segment_distribution": {
    "premium": 25,
    "regular": 60,
    "vip": 15
  },
  "interaction_trends": [
    {
      "date": "2024-01-15",
      "interaction_count": 12
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

### Dashboard Metrics

#### Get Dashboard Metrics
```http
GET /api/v1/analytics/dashboard/metrics
```

Get key metrics optimized for dashboard display.

**Response:**
```json
{
  "total_customers": 100,
  "total_interactions_today": 8,
  "total_interactions_week": 45,
  "total_interactions_month": 150,
  "top_segments": [
    {
      "segment_name": "regular",
      "customer_count": 60
    },
    {
      "segment_name": "premium", 
      "customer_count": 25
    }
  ],
  "recent_activity": [
    {
      "date": "2024-01-15",
      "interaction_count": 8
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

## Authentication & Authorization

All endpoints require authentication via Bearer token:

```http
Authorization: Bearer <access_token>
```

**Required permissions:** Standard user or above

All data is automatically scoped to the authenticated user's organization.

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 404 Not Found
```json
{
  "detail": "Customer with ID 123 not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "field": "recent_interactions_limit",
      "message": "recent_interactions_limit must be between 1 and 20"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error while retrieving customer analytics"
}
```

## Data Models

### Interaction Types
- `call` - Phone calls
- `email` - Email communications
- `meeting` - Face-to-face or virtual meetings
- `support_ticket` - Support requests
- `complaint` - Customer complaints
- `feedback` - Customer feedback

### Interaction Status
- `pending` - Not yet started
- `in_progress` - Currently being handled
- `completed` - Finished
- `cancelled` - Cancelled

### Common Segments
- `vip` - VIP customers
- `premium` - Premium tier customers
- `regular` - Standard customers
- `new` - New customers
- `high_value` - High-value customers
- `at_risk` - At-risk customers

## Performance Considerations

### Database Indexing

The following indexes are automatically created for optimal performance:

**CustomerInteraction indexes:**
- `idx_customer_interaction_org_customer` - (organization_id, customer_id)
- `idx_customer_interaction_type_status` - (interaction_type, status)
- `idx_customer_interaction_date` - (interaction_date)

**CustomerSegment indexes:**
- `idx_customer_segment_org_customer` - (organization_id, customer_id)
- `idx_customer_segment_name_active` - (segment_name, is_active)
- `idx_customer_segment_assigned_date` - (assigned_date)

### Query Optimization

- All queries automatically include organization-level filtering
- Aggregations use database-level grouping for efficiency
- Recent interactions are limited to prevent large response payloads
- Activity timelines default to 30 days to balance detail and performance

## Integration Examples

### Frontend Integration

```javascript
// Get customer analytics
const getCustomerAnalytics = async (customerId) => {
  const response = await fetch(
    `/api/v1/analytics/customers/${customerId}/analytics`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.json();
};

// Get dashboard metrics
const getDashboardMetrics = async () => {
  const response = await fetch('/api/v1/analytics/dashboard/metrics', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

### Service Integration

```python
# Using the service directly
from app.services.customer_analytics_service import CustomerAnalyticsService

# Initialize service
analytics = CustomerAnalyticsService(db, organization_id)

# Get customer metrics
metrics = analytics.get_customer_metrics(customer_id)

# Get segment analytics
segment_data = analytics.get_segment_analytics("premium")
```

## Multi-Tenant Security

### Data Isolation
- All queries automatically filter by organization_id
- Users can only access data from their own organization
- Cross-organization data access is prevented at the service level

### Authorization
- Standard users can view analytics for their organization
- Admin users have the same access (no additional privileges for analytics)
- Platform admins can specify organization_id parameter

### Audit Logging
- All analytics requests are logged with user and organization context
- Performance metrics are tracked for monitoring

## Backward Compatibility

This module is fully backward compatible with the existing system:

- No changes to existing database models
- Uses existing authentication and authorization patterns
- Follows established API response formats
- Maintains existing multi-tenant patterns
- No impact on existing functionality

## Future Enhancements

Planned future enhancements include:

1. **Advanced Filtering**: Date range filters, custom metrics
2. **Export Capabilities**: CSV/Excel export of analytics data
3. **Real-time Updates**: WebSocket-based live analytics
4. **Custom Dashboards**: User-configurable dashboard layouts
5. **Predictive Analytics**: ML-based customer insights
6. **Comparative Analytics**: Period-over-period comparisons