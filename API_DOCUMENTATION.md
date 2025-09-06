# API_DOCUMENTATION.md

# FastAPI v1.6 - Advanced Business Logic and Integrations API Documentation

## Overview

This document provides comprehensive documentation for the advanced business logic, workflows, automation, RBAC enhancements, external API integrations, and analytics capabilities implemented in FastAPI v1.6.

## Table of Contents

1. [Master Data Management APIs](#master-data-management-apis)
2. [Workflow Automation APIs](#workflow-automation-apis)
3. [Enhanced RBAC System](#enhanced-rbac-system)
4. [External Integration Services](#external-integration-services)
5. [Advanced Analytics and Reporting](#advanced-analytics-and-reporting)
6. [Security Enhancements](#security-enhancements)
7. [Testing and Validation](#testing-and-validation)

---

## Master Data Management APIs

### Categories API

Manage hierarchical categories for products, services, and other business entities.

#### Base URL: `/api/v1/master-data/categories`

#### Endpoints

##### GET /categories
Retrieve categories with filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100, max: 1000)
- `category_type` (string): Filter by category type (product, service, expense, asset, general)
- `parent_category_id` (int): Filter by parent category
- `is_active` (boolean): Filter by active status
- `search` (string): Search in name, code, or description

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "organization_id": 1,
      "company_id": 1,
      "name": "Electronics",
      "code": "ELEC",
      "category_type": "product",
      "parent_category_id": null,
      "level": 0,
      "path": "/1/",
      "description": "Electronic products and components",
      "is_active": true,
      "sort_order": 0,
      "default_income_account_id": 101,
      "default_expense_account_id": 201,
      "default_tax_code_id": 301,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "sub_categories": []
    }
  ],
  "total": 150,
  "page": 1,
  "size": 100,
  "pages": 2
}
```

##### POST /categories
Create a new category.

**Request Body:**
```json
{
  "name": "Smartphones",
  "code": "SMART",
  "category_type": "product",
  "parent_category_id": 1,
  "description": "Mobile smartphones and accessories",
  "sort_order": 1,
  "default_income_account_id": 101,
  "default_tax_code_id": 301,
  "company_id": 1
}
```

**Response:** Returns the created category object.

##### PUT /categories/{category_id}
Update an existing category.

**Request Body:** Same as POST but all fields are optional.

##### DELETE /categories/{category_id}
Delete a category (only if no subcategories exist).

---

### Units API

Manage units of measurement with conversion support.

#### Base URL: `/api/v1/master-data/units`

#### Key Features
- Base units and derived units with conversion factors
- Unit type classification (quantity, weight, volume, length, area, time, custom)
- Automatic unit conversion calculations
- Decimal place precision control

#### Endpoints

##### GET /units
Retrieve units with filtering.

**Query Parameters:**
- `unit_type` (string): Filter by unit type
- `is_base_unit` (boolean): Filter base units
- `is_active` (boolean): Filter by active status
- `search` (string): Search in name, symbol, or description

##### POST /units
Create a new unit.

**Request Body:**
```json
{
  "name": "Kilogram",
  "symbol": "kg",
  "unit_type": "weight",
  "description": "Standard unit of mass",
  "is_base_unit": true,
  "conversion_factor": 1.000000,
  "decimal_places": 3,
  "company_id": 1
}
```

##### POST /units/convert
Convert values between units.

**Request Body:**
```json
{
  "from_unit_id": 1,
  "to_unit_id": 2,
  "value": 1000.0
}
```

**Response:**
```json
{
  "from_unit_id": 1,
  "to_unit_id": 2,
  "value": 1000.0,
  "converted_value": 1.0
}
```

---

### Tax Codes API

Manage tax codes with complex tax calculations and GST compliance.

#### Base URL: `/api/v1/master-data/tax-codes`

#### Key Features
- Multiple tax types (GST, VAT, Service Tax, etc.)
- Tax component breakdown (CGST, SGST, IGST)
- HSN/SAC code integration
- Effective date management
- Tax calculation engine

#### Endpoints

##### POST /tax-codes/calculate
Calculate tax for a given amount.

**Request Body:**
```json
{
  "amount": 1000.00,
  "tax_code_id": 1
}
```

**Response:**
```json
{
  "amount": 1000.00,
  "tax_code_id": 1,
  "calculated_tax": 180.00,
  "tax_breakdown": {
    "cgst": 90.00,
    "sgst": 90.00
  }
}
```

---

### Payment Terms API

Manage advanced payment terms with early payment discounts and penalty calculations.

#### Base URL: `/api/v1/master-data/payment-terms`

#### Key Features
- Standard payment days configuration
- Early payment discount terms
- Late payment penalty calculation
- Installment payment schedules
- Credit limit management
- Integration with accounting systems

#### Example Payment Terms with Schedule:
```json
{
  "name": "Split Payment 30-60",
  "code": "SPLIT3060",
  "payment_days": 60,
  "early_payment_discount_days": 10,
  "early_payment_discount_rate": 2.00,
  "payment_schedule": [
    {"days": 30, "percentage": 50.00},
    {"days": 60, "percentage": 50.00}
  ],
  "credit_limit_amount": 50000.00,
  "requires_approval": true
}
```

---

## Workflow Automation APIs

### Business Rules Engine

Create and manage dynamic business rules for validation, calculation, and automation.

#### Base URL: `/api/v1/workflow-automation/business-rules`

#### Key Features
- Rule expression engine with custom syntax
- Multiple rule types (condition, calculation, validation)
- Entity-specific rule application
- Performance monitoring and optimization
- Error handling and recovery

#### Example Business Rule:
```json
{
  "name": "Credit Limit Validation",
  "category": "validation",
  "rule_expression": "customer.credit_limit >= order.total_amount",
  "rule_type": "condition",
  "applicable_entities": ["sales_order"],
  "conditions": {
    "entity_type": "sales_order",
    "status": "pending"
  },
  "actions": {
    "on_success": "approve_order",
    "on_failure": "require_approval"
  }
}
```

### Advanced Workflow Templates

Create sophisticated workflows with parallel execution, conditional branching, and error handling.

#### Base URL: `/api/v1/workflow-automation/templates`

#### Key Features
- Parallel and sequential step execution
- Conditional step execution with business rules
- Advanced approval mechanisms
- Timeout and retry configuration
- Workflow inheritance and templates

#### Example Workflow Template:
```json
{
  "name": "Purchase Order Approval",
  "category": "procurement",
  "trigger_type": "event_based",
  "trigger_events": ["purchase_order.created"],
  "input_schema": {
    "purchase_order_id": "integer",
    "amount": "decimal",
    "vendor_id": "integer"
  },
  "steps": [
    {
      "step_name": "Amount Validation",
      "step_type": "validation",
      "execution_condition": "amount > 1000",
      "business_rule_id": 1
    },
    {
      "step_name": "Manager Approval",
      "step_type": "approval",
      "approver_roles": ["manager", "supervisor"],
      "approval_method": "any"
    }
  ]
}
```

---

## Enhanced RBAC System

### Advanced Permission Matrix

Create sophisticated permission systems with inheritance, conditions, and dynamic permissions.

#### Base URL: `/api/v1/rbac-enhanced`

#### Key Features
- Role inheritance with override capabilities
- Conditional permissions based on context
- Resource-specific permissions
- Permission caching for performance
- Analytics and usage tracking

#### Permission Matrix Creation:
```json
{
  "modules": {
    "customers": {
      "category": "core",
      "actions": {
        "read": {
          "scope": "organization",
          "resources": ["customer", "customer_file"],
          "conditions": {
            "data_scope": "department_only"
          }
        },
        "write": {
          "scope": "company",
          "resources": ["customer"]
        }
      }
    }
  },
  "roles": {
    "Sales Manager": {
      "type": "functional",
      "description": "Manages sales operations",
      "permissions": ["customers.*", "orders.read", "reports.sales"]
    }
  }
}
```

#### Advanced Permission Checking:
```python
# Check permission with context
result = rbac_service.check_permission_advanced(
    user_id=123,
    permission_name="customers.read",
    resource_type="customer",
    resource_id=456,
    context={
        "department": "sales",
        "ip_address": "192.168.1.100",
        "resource_owner_id": 789
    }
)
```

---

## External Integration Services

### Payment Gateway Integration

Support for multiple payment processors with unified API.

#### Supported Gateways:
- **Stripe**: Credit cards, ACH, international payments
- **Razorpay**: Indian market focus, UPI, wallets
- **PayPal**: Global e-commerce integration
- **Square**: Point-of-sale and online payments

#### Usage Example:
```python
from app.services.external_integrations_service import PaymentGatewayService

payment_service = PaymentGatewayService(db)
result = await payment_service.process_payment(
    integration_id=1,
    payment_data={
        "amount": 100.00,
        "currency": "USD",
        "payment_method": "pm_1234567890",
        "description": "Order #12345",
        "metadata": {"order_id": "12345"}
    }
)
```

### ERP Connector Integration

Connect with major ERP systems for data synchronization.

#### Supported ERP Systems:
- **QuickBooks**: Chart of accounts, customers, vendors
- **SAP**: Financial data, master data synchronization
- **Oracle ERP**: Comprehensive business data integration
- **Tally**: Indian accounting software integration

#### Chart of Accounts Sync:
```python
from app.services.external_integrations_service import ERPConnectorService

erp_service = ERPConnectorService(db)
result = await erp_service.sync_chart_of_accounts(integration_id=2)
```

### Third-Party Analytics Integration

Push business analytics to external platforms.

#### Supported Platforms:
- **Google Analytics**: E-commerce and user behavior tracking
- **Mixpanel**: Product analytics and user journeys
- **Amplitude**: Behavioral analytics and cohort analysis
- **Segment**: Customer data platform integration

#### Analytics Event Tracking:
```python
from app.services.external_integrations_service import ThirdPartyAnalyticsService

analytics_service = ThirdPartyAnalyticsService(db)
result = await analytics_service.push_analytics_data(
    integration_id=3,
    analytics_data={
        "event_name": "purchase_completed",
        "user_id": "user_123",
        "properties": {
            "amount": 150.00,
            "currency": "USD",
            "product_category": "electronics"
        }
    }
)
```

---

## Advanced Analytics and Reporting

### Executive Dashboard

Comprehensive business intelligence dashboard with real-time metrics.

#### Base URL: `/api/v1/analytics/executive-dashboard`

#### Key Metrics:
- **Financial**: Revenue, profit margins, cash flow, A/R, A/P
- **Operational**: Order processing, inventory turnover, efficiency scores
- **Customer**: Acquisition, retention, satisfaction, lifetime value
- **Project**: Success rates, resource utilization, completion metrics
- **Service**: Ticket resolution, SLA compliance, quality scores
- **Integration**: API usage, sync success rates, data volume

#### Dashboard Response:
```json
{
  "organization_summary": {
    "total_users": 150,
    "total_companies": 5,
    "active_integrations": 12,
    "data_volume_processed": 1500000
  },
  "financial_metrics": {
    "total_revenue": 2500000.00,
    "total_expenses": 1800000.00,
    "net_profit": 700000.00,
    "profit_margin_percent": 28.0,
    "cash_flow": 450000.00
  },
  "performance_trends": {
    "daily_trends": [
      {
        "date": "2024-01-01",
        "revenue": 85000.00,
        "orders": 145,
        "tickets": 23
      }
    ]
  }
}
```

### Cross-Module Analytics

Get insights across multiple business modules.

#### Available Insights:
- **Customer-Service Correlation**: Relationship between customer satisfaction and service quality
- **Sales-Finance Integration**: Revenue recognition and financial impact analysis
- **Project-Resource Utilization**: Resource allocation efficiency across projects
- **Integration-Performance Impact**: How integrations affect system performance

### Predictive Analytics

Machine learning-powered predictions for business planning.

#### Available Predictions:
- **Revenue Forecasting**: Predict future revenue based on historical patterns
- **Customer Churn**: Identify customers at risk of churning
- **Resource Demand**: Predict future resource requirements
- **Service Load**: Forecast service ticket volume and capacity needs

---

## Security Enhancements

### Encryption and Data Protection

- **Authentication Config Encryption**: All integration credentials are encrypted at rest
- **API Key Management**: Secure API key generation and rotation
- **Audit Logging**: Comprehensive audit trails for all operations
- **Rate Limiting**: Configurable rate limits for API endpoints

### Access Control Enhancements

- **Context-Aware Permissions**: Permissions that consider user context (IP, time, location)
- **Dynamic Permission Assignment**: Runtime permission calculation based on business rules
- **Session Management**: Enhanced session security with automatic timeout
- **Multi-Factor Authentication**: Integration with MFA providers

---

## Testing and Validation

### Test Coverage

Comprehensive test suite covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Service Tests**: Business logic validation
- **End-to-End Tests**: Complete workflow testing

### API Testing Examples

```python
# Master Data API Testing
def test_create_category():
    category_data = {
        "name": "Electronics",
        "code": "ELEC",
        "category_type": "product"
    }
    response = client.post("/api/v1/master-data/categories", json=category_data)
    assert response.status_code == 201

# Payment Gateway Testing
def test_stripe_payment():
    payment_data = {
        "amount": 100.00,
        "payment_method": "test_token",
        "currency": "USD"
    }
    result = await payment_service.process_payment(1, payment_data)
    assert result["success"] == True

# RBAC Testing
def test_permission_inheritance():
    role = rbac_service.create_role_with_inheritance(
        organization_id=1,
        name="Junior Manager",
        parent_role_id=2
    )
    assert role.parent_role_id == 2
```

### Performance Testing

- **Load Testing**: API endpoints under high concurrency
- **Stress Testing**: System behavior under extreme loads
- **Analytics Performance**: Large dataset processing efficiency
- **Integration Reliability**: External service failure handling

---

## API Versioning and Compatibility

### Version Strategy
- **Semantic Versioning**: Following semantic versioning principles
- **Backward Compatibility**: Maintaining compatibility for at least 2 major versions
- **Deprecation Notices**: 6-month notice period for deprecated features
- **Migration Guides**: Comprehensive guides for version upgrades

### Error Handling

Standardized error responses across all APIs:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_1234567890"
  }
}
```

---

## Rate Limiting and Quotas

### Default Limits
- **Standard Users**: 1000 requests/hour
- **Premium Users**: 5000 requests/hour
- **Enterprise**: Custom limits based on agreement
- **Integration APIs**: Separate limits for high-volume operations

### Quota Management
- **Real-time Monitoring**: Current usage tracking
- **Burst Allowance**: Temporary limit increases for legitimate use
- **Automatic Scaling**: Dynamic limit adjustment based on usage patterns

---

## Monitoring and Observability

### Metrics Collection
- **API Performance**: Response times, error rates, throughput
- **Business Metrics**: Transaction volumes, user engagement, feature usage
- **System Health**: Resource utilization, database performance, integration status
- **Security Metrics**: Authentication failures, permission denials, suspicious activity

### Alerting
- **Threshold-based Alerts**: Automatic alerts for metric thresholds
- **Anomaly Detection**: ML-powered anomaly detection
- **Integration Health**: Monitoring external service availability
- **Performance Degradation**: Early warning system for performance issues

---

## Support and Documentation

### API Documentation
- **Interactive API Explorer**: Swagger/OpenAPI documentation
- **Code Examples**: Sample implementations in multiple languages
- **SDK Libraries**: Official client libraries for popular languages
- **Postman Collections**: Ready-to-use API collections

### Developer Resources
- **Getting Started Guide**: Quick setup and first API call
- **Best Practices**: Recommended patterns and practices
- **Troubleshooting Guide**: Common issues and solutions
- **Community Forum**: Developer community support

---

This documentation provides a comprehensive overview of the advanced features implemented in FastAPI v1.6. For specific implementation details, refer to the source code and inline documentation.