# Customer Analytics Module - Implementation Guide

## Overview

The Customer Analytics Module provides comprehensive insights and metrics for customer data within the TRITIQ ERP system. This module calculates key performance indicators, interaction patterns, and segment analytics while maintaining strict organizational data isolation.

## 🌟 Features

### Backend Analytics
- **Customer Metrics**: Total interactions, last interaction date, interaction type breakdown
- **Segment Analytics**: Customer distribution, interaction patterns by segment  
- **Organization Summary**: High-level analytics across all customers
- **Dashboard Metrics**: Quick KPIs for dashboard display
- **Multi-tenant Isolation**: All data automatically scoped to user's organization
- **Performance Optimized**: Uses existing database indexes for fast queries

### Frontend Components
- **Customer Analytics Component**: Full-featured React component with interactive displays
- **Modal Integration**: Clean modal wrapper for analytics viewing
- **Real-time Data**: React Query integration with proper caching and loading states
- **Responsive Design**: Material-UI components with mobile-friendly layouts

## 🏗️ Architecture

### Database Models

#### CustomerInteraction
```sql
- id: Primary key
- organization_id: Multi-tenant isolation
- customer_id: Foreign key to customers table
- interaction_type: 'call', 'email', 'meeting', 'support_ticket', 'complaint', 'feedback'
- subject: Interaction subject line
- description: Optional detailed description
- status: 'pending', 'in_progress', 'completed', 'cancelled'
- interaction_date: When the interaction occurred
- created_by: User who logged the interaction
- created_at/updated_at: Audit timestamps
```

#### CustomerSegment
```sql
- id: Primary key
- organization_id: Multi-tenant isolation
- customer_id: Foreign key to customers table
- segment_name: 'vip', 'premium', 'regular', 'new', 'high_value', 'at_risk'
- segment_value: Optional numeric value for the segment
- segment_description: Optional description
- is_active: Whether the segment assignment is active
- assigned_date: When the segment was assigned
- assigned_by: User who assigned the segment
```

### API Endpoints

All endpoints require authentication and are automatically scoped to the user's organization:

#### Customer Analytics
```
GET /api/v1/analytics/customers/{customer_id}/analytics
```
Query Parameters:
- `include_recent_interactions` (bool): Include recent interactions in response
- `recent_interactions_limit` (int): Number of recent interactions (1-20)

#### Segment Analytics
```
GET /api/v1/analytics/segments/{segment_name}/analytics
```
Query Parameters:
- `include_timeline` (bool): Include activity timeline
- `timeline_days` (int): Number of days for timeline (7-365)

#### Dashboard Metrics
```
GET /api/v1/analytics/dashboard/metrics
```
Returns quick KPIs for dashboard display.

#### Organization Summary
```
GET /api/v1/analytics/organization/summary
```
Returns organization-wide analytics summary.

#### Available Segments
```
GET /api/v1/analytics/segments
```
Returns list of available segment names.

## 📊 Sample Data Structures

### Customer Analytics Response
```json
{
  "customer_id": 1,
  "customer_name": "ABC Corporation",
  "total_interactions": 25,
  "last_interaction_date": "2024-01-15T14:30:00Z",
  "interaction_types": {
    "call": 8,
    "email": 12,
    "meeting": 3,
    "support_ticket": 2
  },
  "interaction_status": {
    "completed": 18,
    "pending": 4,
    "in_progress": 3
  },
  "segments": [
    {
      "segment_name": "premium",
      "segment_value": 250.0,
      "assigned_date": "2024-01-01T00:00:00Z",
      "description": "Premium tier customer"
    }
  ],
  "recent_interactions": [
    {
      "interaction_type": "call",
      "subject": "Product inquiry",
      "status": "completed",
      "interaction_date": "2024-01-15T14:30:00Z"
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

### Dashboard Metrics Response
```json
{
  "total_customers": 150,
  "total_interactions_today": 8,
  "total_interactions_week": 45,
  "total_interactions_month": 180,
  "top_segments": [
    {
      "segment_name": "premium",
      "customer_count": 25
    }
  ],
  "recent_activity": [
    {
      "customer_name": "ABC Corp",
      "interaction_type": "call",
      "interaction_date": "2024-01-16T10:30:00Z"
    }
  ],
  "calculated_at": "2024-01-16T12:00:00Z"
}
```

## 🚀 Setup and Installation

### Backend Setup

1. **Database Migration**
   ```bash
   # The migration already exists: b4f8c2d1a9e0_add_customer_interactions_and_segments.py
   python -m alembic upgrade head
   ```

2. **Start FastAPI Server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Test API Endpoints**
   ```bash
   # Get dashboard metrics
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/analytics/dashboard/metrics
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install @tanstack/react-query  # Already included
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Access Analytics**
   - Navigate to Masters → Customers
   - Click the Analytics (📊) button next to any customer
   - View comprehensive analytics in the modal

## 🎯 Usage Examples

### Using the Analytics Service
```typescript
import { analyticsService } from '../services/analyticsService';

// Get customer analytics
const analytics = await analyticsService.getCustomerAnalytics(customerId, true, 10);

// Get segment analytics
const segmentData = await analyticsService.getSegmentAnalytics('premium', true, 30);

// Get dashboard metrics
const dashboard = await analyticsService.getDashboardMetrics();
```

### Using the React Components
```tsx
import CustomerAnalytics from '../components/CustomerAnalytics';
import CustomerAnalyticsModal from '../components/CustomerAnalyticsModal';

// Direct component usage
<CustomerAnalytics customerId={123} customerName="ABC Corp" />

// Modal usage
<CustomerAnalyticsModal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  customerId={123}
  customerName="ABC Corp"
/>
```

## 🔒 Security Features

### Multi-Tenant Data Isolation
- All queries automatically filter by `organization_id`
- Users can only access data from their own organization
- Cross-organization data access is prevented at the service level

### Authentication & Authorization
- Standard JWT token authentication required
- Uses existing `get_current_active_user` dependency
- Follows established authorization patterns
- Platform admins can specify organization_id parameter

### Performance Optimizations
- Database-level aggregations using SQLAlchemy functions
- Efficient filtering with compound indexes
- Limited result sets to prevent performance issues
- React Query caching for optimal frontend performance

## 📈 Database Indexes

The following indexes are automatically created for optimal performance:

**CustomerInteraction indexes:**
- `idx_customer_interaction_org_customer` - (organization_id, customer_id)
- `idx_customer_interaction_type_status` - (interaction_type, status)
- `idx_customer_interaction_date` - (interaction_date)

**CustomerSegment indexes:**
- `idx_customer_segment_org_customer` - (organization_id, customer_id)
- `idx_customer_segment_name_active` - (segment_name, is_active)
- `idx_customer_segment_assigned_date` - (assigned_date)

## 🧪 Testing

### Run Backend Tests
```bash
python -m pytest tests/test_customer_analytics.py -v
```

### Run Demo Script
```bash
python demo_customer_analytics_complete.py
```

### Manual Testing
1. Start the backend server
2. Use a tool like Postman or curl to test API endpoints
3. Start the frontend and test the UI components
4. Verify data isolation by testing with different organizations

## 🔮 Future Enhancements

Planned improvements include:
1. **Advanced Filtering**: Date range filters, custom metrics
2. **Export Capabilities**: CSV/Excel export of analytics data
3. **Real-time Updates**: WebSocket-based live analytics
4. **Custom Dashboards**: User-configurable dashboard layouts
5. **Predictive Analytics**: ML-based customer insights
6. **Comparative Analytics**: Period-over-period comparisons

## 📝 API Documentation

Complete API documentation is available at:
- **File**: `docs/customer-analytics-api.md`
- **Interactive Docs**: http://localhost:8000/docs (when server is running)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### Common Issues

1. **Database Migration Errors**
   ```bash
   # Check current migration status
   python -m alembic current
   
   # Run specific migration
   python -m alembic upgrade b4f8c2d1a9e0
   ```

2. **API Authentication Issues**
   - Ensure valid JWT token in Authorization header
   - Check token expiration (default 2 hours)
   - Verify user has access to the organization

3. **Frontend TypeScript Errors**
   - Ensure all dependencies are installed: `npm install`
   - Check TypeScript configuration in `tsconfig.json`
   - Verify API service imports are correct

4. **Performance Issues**
   - Check database indexes are created
   - Monitor query execution times
   - Consider increasing pagination limits
   - Review React Query cache settings

## 📧 Support

For questions or issues with the Customer Analytics Module:
1. Check existing documentation in `/docs`
2. Review test cases in `/tests/test_customer_analytics.py`
3. Run the demo script for troubleshooting
4. Check server logs for API errors

---

**Note**: This module integrates seamlessly with the existing TRITIQ ERP system and maintains backward compatibility with all existing functionality.