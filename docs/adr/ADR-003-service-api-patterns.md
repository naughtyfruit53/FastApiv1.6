# ADR-003: API Design Patterns for Service Endpoints

## Status
Proposed

## Context

The Service CRM integration requires designing RESTful API endpoints that integrate seamlessly with the existing TRITIQ ERP API architecture. We need to establish consistent patterns for service management endpoints while supporting various client types:

- **Admin Dashboard**: Full CRUD operations for service management
- **Customer Portal**: Limited self-service operations for appointment booking
- **Mobile Workforce**: Technician-focused operations optimized for mobile usage
- **Third-party Integrations**: Webhook and API access for external systems

### Current API Architecture
- **FastAPI Framework**: Async Python with automatic OpenAPI documentation
- **Organization Scoping**: All endpoints include organization context
- **JWT Authentication**: Role-based access control with token validation
- **Consistent Patterns**: Standard CRUD operations with pagination
- **Error Handling**: Structured error responses with appropriate HTTP status codes

### Requirements
- Maintain consistency with existing ERP endpoint patterns
- Support high-frequency mobile app operations
- Enable customer self-service with appropriate restrictions
- Provide real-time updates for scheduling operations
- Support bulk operations for administrative efficiency

## Decision

We will implement a layered API design with three distinct access patterns:

### 1. Administrative APIs (Internal Management)
**Pattern**: `/api/v1/organizations/{org_id}/services/...`
**Target**: Admin dashboard, service managers
**Authentication**: Full organization member access with role validation

### 2. Customer Portal APIs (Self-Service)
**Pattern**: `/api/v1/customer-portal/...`
**Target**: Customer self-service interfaces
**Authentication**: Customer-specific access with limited scope

### 3. Mobile Workforce APIs (Field Operations)
**Pattern**: `/api/v1/mobile/technician/{technician_id}/...`
**Target**: Technician mobile applications
**Authentication**: Technician-specific access optimized for mobile

## API Endpoint Design

### Service Catalog Management (Administrative)

```python
# Service Categories
GET    /api/v1/organizations/{org_id}/services/categories
POST   /api/v1/organizations/{org_id}/services/categories
PUT    /api/v1/organizations/{org_id}/services/categories/{category_id}
DELETE /api/v1/organizations/{org_id}/services/categories/{category_id}

# Service Items  
GET    /api/v1/organizations/{org_id}/services/items
POST   /api/v1/organizations/{org_id}/services/items
PUT    /api/v1/organizations/{org_id}/services/items/{item_id}
DELETE /api/v1/organizations/{org_id}/services/items/{item_id}
GET    /api/v1/organizations/{org_id}/services/items/{item_id}/pricing

# Bulk Operations
POST   /api/v1/organizations/{org_id}/services/items/bulk-import
GET    /api/v1/organizations/{org_id}/services/items/export
POST   /api/v1/organizations/{org_id}/services/categories/bulk-update
```

### Technician Management (Administrative)

```python
# Technician CRUD
GET    /api/v1/organizations/{org_id}/technicians
POST   /api/v1/organizations/{org_id}/technicians
PUT    /api/v1/organizations/{org_id}/technicians/{tech_id}
DELETE /api/v1/organizations/{org_id}/technicians/{tech_id}

# Skills Management
GET    /api/v1/organizations/{org_id}/technicians/{tech_id}/skills
POST   /api/v1/organizations/{org_id}/technicians/{tech_id}/skills
PUT    /api/v1/organizations/{org_id}/technicians/{tech_id}/skills/{skill_id}
DELETE /api/v1/organizations/{org_id}/technicians/{tech_id}/skills/{skill_id}

# Schedule Management
GET    /api/v1/organizations/{org_id}/technicians/{tech_id}/schedule
PUT    /api/v1/organizations/{org_id}/technicians/{tech_id}/schedule
GET    /api/v1/organizations/{org_id}/technicians/availability
POST   /api/v1/organizations/{org_id}/technicians/bulk-schedule-update
```

### Appointment Management (Administrative)

```python
# Appointment CRUD
GET    /api/v1/organizations/{org_id}/appointments
POST   /api/v1/organizations/{org_id}/appointments
PUT    /api/v1/organizations/{org_id}/appointments/{appointment_id}
DELETE /api/v1/organizations/{org_id}/appointments/{appointment_id}

# Service Execution
GET    /api/v1/organizations/{org_id}/appointments/{appointment_id}/execution
POST   /api/v1/organizations/{org_id}/appointments/{appointment_id}/execution
PUT    /api/v1/organizations/{org_id}/appointments/{appointment_id}/execution/{exec_id}

# Notes and History
POST   /api/v1/organizations/{org_id}/appointments/{appointment_id}/notes
GET    /api/v1/organizations/{org_id}/appointments/{appointment_id}/history
GET    /api/v1/organizations/{org_id}/appointments/{appointment_id}/timeline

# Bulk Operations
POST   /api/v1/organizations/{org_id}/appointments/bulk-assign
POST   /api/v1/organizations/{org_id}/appointments/bulk-reschedule
GET    /api/v1/organizations/{org_id}/appointments/export
```

### Customer Portal APIs (Self-Service)

```python
# Customer Authentication (extends existing auth)
POST   /api/v1/customer-portal/auth/login
POST   /api/v1/customer-portal/auth/register
GET    /api/v1/customer-portal/auth/profile

# Service Discovery
GET    /api/v1/customer-portal/services
GET    /api/v1/customer-portal/services/{service_id}
GET    /api/v1/customer-portal/services/{service_id}/availability

# Self-Service Booking
POST   /api/v1/customer-portal/appointments
GET    /api/v1/customer-portal/appointments
PUT    /api/v1/customer-portal/appointments/{appointment_id}
DELETE /api/v1/customer-portal/appointments/{appointment_id}

# Customer History and Preferences
GET    /api/v1/customer-portal/service-history
GET    /api/v1/customer-portal/preferences
PUT    /api/v1/customer-portal/preferences
GET    /api/v1/customer-portal/technician-availability

# Real-time Updates
GET    /api/v1/customer-portal/appointments/{appointment_id}/status
POST   /api/v1/customer-portal/appointments/{appointment_id}/feedback
```

### Mobile Workforce APIs (Field Operations)

```python
# Technician Dashboard
GET    /api/v1/mobile/technician/{tech_id}/dashboard
GET    /api/v1/mobile/technician/{tech_id}/assignments
GET    /api/v1/mobile/technician/{tech_id}/schedule

# Assignment Management
PUT    /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/status
POST   /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/start
POST   /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/complete

# Work Documentation
POST   /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/notes
POST   /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/photos
POST   /api/v1/mobile/technician/{tech_id}/assignments/{appointment_id}/signature

# Offline Sync Support
GET    /api/v1/mobile/technician/{tech_id}/sync/assignments
POST   /api/v1/mobile/technician/{tech_id}/sync/updates
GET    /api/v1/mobile/technician/{tech_id}/sync/manifest
```

## Authentication and Authorization Patterns

### Role-Based Access Control

```python
# Administrative APIs - Organization Member Required
@require_organization_access(min_role="admin")
async def create_service_item(org_id: int, service_data: ServiceCreate):
    pass

# Customer Portal - Customer Identity Required  
@require_customer_auth()
async def book_appointment(customer_id: int, appointment_data: AppointmentCreate):
    pass

# Mobile Workforce - Technician Identity Required
@require_technician_auth()
async def update_assignment_status(tech_id: int, appointment_id: int, status: str):
    pass
```

### Access Pattern Matrix

| API Type | Authentication | Authorization | Rate Limiting |
|----------|---------------|---------------|---------------|
| Administrative | JWT Token | Organization + Role | 1000 req/hour |
| Customer Portal | Customer JWT | Customer Identity | 100 req/hour |
| Mobile Workforce | Technician JWT | Technician Identity | 500 req/hour |
| Public Booking | API Key + CAPTCHA | Service Visibility | 20 req/hour |

## Request/Response Patterns

### Standard Response Format

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 150,
      "total_pages": 8
    }
  },
  "message": "Success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid appointment time slot",
    "details": {
      "field": "appointment_time",
      "reason": "Technician not available at requested time"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Service-Specific Schemas

```python
# Appointment Response Schema
class AppointmentResponse(BaseModel):
    id: int
    customer: CustomerSummary
    service: ServiceSummary
    technician: TechnicianSummary
    appointment_date: date
    start_time: time
    end_time: time
    status: AppointmentStatus
    address: AddressModel
    estimated_duration: int
    created_at: datetime
    updated_at: datetime

# Mobile-Optimized Assignment Schema
class MobileAssignmentResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    service_name: str
    address: str
    scheduled_start: datetime
    estimated_duration: int
    status: str
    priority: str
    special_instructions: Optional[str]
    equipment_needed: List[str]
```

## Performance Optimization Patterns

### Caching Strategy

```python
# Service catalog caching (Redis)
@cache(expire=3600)  # 1 hour cache
async def get_organization_services(org_id: int):
    pass

# Technician availability caching
@cache(expire=300)   # 5 minute cache
async def get_technician_availability(org_id: int, date: date):
    pass

# Customer portal - aggressive caching
@cache(expire=1800)  # 30 minute cache
async def get_customer_service_history(customer_id: int):
    pass
```

### Database Query Optimization

```python
# Efficient appointment listing with joins
async def get_appointments(org_id: int, filters: AppointmentFilters):
    query = select(
        Appointment,
        Customer.name.label("customer_name"),
        ServiceItem.name.label("service_name"),
        User.full_name.label("technician_name")
    ).join(Customer).join(ServiceItem).join(Technician).join(User)
    
    # Apply filters and pagination
    return await paginate_query(query, filters)

# Mobile-optimized assignment queries
async def get_technician_assignments(tech_id: int, date: date):
    # Optimized for mobile bandwidth
    return await db.execute(
        select(
            Appointment.id,
            Customer.name,
            Customer.phone,
            ServiceItem.name,
            Appointment.address,
            Appointment.start_time,
            Appointment.estimated_duration
        ).where(
            Appointment.technician_id == tech_id,
            Appointment.appointment_date == date,
            Appointment.status.in_(["confirmed", "in_progress"])
        ).order_by(Appointment.start_time)
    )
```

### Real-Time Updates

```python
# WebSocket for real-time appointment updates
@websocket_endpoint("/ws/appointments/{org_id}")
async def appointment_updates(websocket: WebSocket, org_id: int):
    await websocket.accept()
    # Subscribe to appointment changes for organization
    await subscribe_to_appointment_updates(websocket, org_id)

# Mobile push notifications
async def notify_assignment_update(tech_id: int, appointment_id: int):
    # Send push notification to technician mobile app
    await push_notification_service.send(
        recipient=tech_id,
        title="Assignment Update",
        message=f"New assignment #{appointment_id}",
        data={"appointment_id": appointment_id, "action": "refresh"}
    )
```

## Bulk Operations and Integration

### Excel Import/Export Patterns

```python
# Service catalog bulk import
POST /api/v1/organizations/{org_id}/services/items/bulk-import
Content-Type: multipart/form-data
{
  "file": "services.xlsx",
  "mapping": {
    "name": "A",
    "category": "B", 
    "duration": "C",
    "price": "D"
  }
}

# Appointment export for reporting
GET /api/v1/organizations/{org_id}/appointments/export
?start_date=2024-01-01&end_date=2024-01-31&format=xlsx
```

### Webhook Support

```python
# Customer booking webhook
POST /api/v1/webhook/appointment-booked
{
  "organization_id": 123,
  "appointment_id": 456,
  "customer_id": 789,
  "service_id": 101,
  "scheduled_time": "2024-01-15T14:00:00Z"
}

# Technician assignment webhook  
POST /api/v1/webhook/technician-assigned
{
  "organization_id": 123,
  "appointment_id": 456,
  "technician_id": 202,
  "assigned_at": "2024-01-15T10:30:00Z"
}
```

## Testing Strategy

### API Testing Patterns

```python
# Unit tests for endpoint logic
class TestServiceCatalogAPI:
    async def test_create_service_item(self, client, auth_admin):
        response = await client.post(
            f"/api/v1/organizations/{ORG_ID}/services/items",
            json={"name": "AC Repair", "duration": 120},
            headers=auth_admin
        )
        assert response.status_code == 201

# Integration tests for workflow
class TestAppointmentWorkflow:
    async def test_complete_appointment_flow(self, client):
        # Create appointment
        # Assign technician  
        # Start service
        # Complete service
        # Verify billing integration
        pass

# Load testing for mobile endpoints
class TestMobilePerformance:
    async def test_technician_assignment_load(self):
        # Simulate 100 concurrent technicians fetching assignments
        pass
```

### Error Handling Testing

```python
# Test error scenarios
async def test_booking_conflicts():
    # Try to book technician at same time
    # Verify proper conflict detection
    pass

async def test_invalid_service_request():
    # Request non-existent service
    # Verify 404 response with proper error structure
    pass
```

## Monitoring and Observability

### API Metrics

```python
# Custom metrics for service operations
service_api_requests = Counter(
    "service_api_requests_total",
    "Total API requests",
    ["endpoint", "method", "status"]
)

appointment_operations = Histogram(
    "appointment_operation_duration_seconds",
    "Time spent on appointment operations",
    ["operation_type"]
)

mobile_sync_operations = Counter(
    "mobile_sync_operations_total", 
    "Mobile sync operations",
    ["technician_id", "operation", "success"]
)
```

### Health Checks

```python
# Service health endpoint
GET /api/v1/health/services
{
  "database": "healthy",
  "redis_cache": "healthy", 
  "notification_service": "healthy",
  "mobile_sync": "healthy",
  "response_time_ms": 45
}
```

## Consequences

### Positive
- **Consistency**: Follows established ERP API patterns
- **Scalability**: Optimized for different client types and usage patterns
- **Security**: Role-based access appropriate for each user type
- **Performance**: Caching and optimization strategies for high-frequency operations
- **Integration**: Seamless integration with existing financial and customer systems

### Negative
- **Complexity**: Multiple API patterns increase development and maintenance overhead
- **Documentation**: Extensive API surface requires comprehensive documentation
- **Testing**: Complex testing matrix across different client types
- **Versioning**: Need to maintain backwards compatibility across API versions

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| API proliferation | Strict design reviews, pattern consistency |
| Mobile performance | Optimized endpoints, caching, compression |
| Security vulnerabilities | Comprehensive auth testing, rate limiting |
| Version fragmentation | Careful versioning strategy, migration guides |

## Implementation Guidelines

### Development Standards
1. **OpenAPI Documentation**: All endpoints must have complete OpenAPI specs
2. **Error Handling**: Use consistent error response formats
3. **Input Validation**: Strict validation using Pydantic models
4. **Rate Limiting**: Implement appropriate limits for each API type
5. **Logging**: Comprehensive request/response logging for troubleshooting

### Code Review Checklist
- [ ] Follows established URL patterns
- [ ] Implements proper authentication/authorization
- [ ] Includes comprehensive error handling
- [ ] Has appropriate caching strategy
- [ ] Includes unit and integration tests
- [ ] Documents breaking changes

## Related ADRs
- ADR-001: Multi-Tenant Service CRM Architecture
- ADR-002: Database Schema Design for Service Management
- ADR-004: Mobile Workforce Application Strategy
- ADR-006: Authentication and Authorization for Service Module