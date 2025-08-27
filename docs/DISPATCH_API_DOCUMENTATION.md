# Dispatch Management API Documentation

## Overview

The Dispatch Management System provides comprehensive APIs for managing material dispatch orders and installation job scheduling. This system integrates with the existing ERP voucher system and provides end-to-end material dispatch and installation management.

## Base URL

All dispatch endpoints are available under:
```
/api/v1/dispatch
```

## Authentication & Authorization

All endpoints require authentication and proper RBAC permissions:

- **Authentication**: Bearer token required in Authorization header
- **RBAC Permissions Required**:
  - `dispatch_create` - Create dispatch orders
  - `dispatch_read` - View dispatch orders
  - `dispatch_update` - Update dispatch orders  
  - `dispatch_delete` - Delete dispatch orders
  - `installation_create` - Create installation jobs
  - `installation_read` - View installation jobs
  - `installation_update` - Update installation jobs
  - `installation_delete` - Delete installation jobs

## Dispatch Orders API

### Create Dispatch Order
**POST** `/api/v1/dispatch/orders`

Creates a new dispatch order with items.

**Required Permission**: `dispatch_create`

**Request Body**:
```json
{
  "customer_id": 123,
  "ticket_id": 456,
  "delivery_address": "123 Main St, City, State 12345",
  "delivery_contact_person": "John Doe",
  "delivery_contact_number": "+1234567890",
  "expected_delivery_date": "2024-08-25T10:00:00Z",
  "notes": "Handle with care",
  "items": [
    {
      "product_id": 789,
      "quantity": 5,
      "unit": "PCS",
      "description": "AC Unit Model XYZ",
      "serial_numbers": "[\"SN001\", \"SN002\"]",
      "batch_numbers": "[\"B001\"]"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "order_number": "DO/24/00001",
  "customer_id": 123,
  "ticket_id": 456,
  "status": "pending",
  "dispatch_date": null,
  "expected_delivery_date": "2024-08-25T10:00:00Z",
  "actual_delivery_date": null,
  "delivery_address": "123 Main St, City, State 12345",
  "delivery_contact_person": "John Doe",
  "delivery_contact_number": "+1234567890",
  "notes": "Handle with care",
  "tracking_number": null,
  "courier_name": null,
  "created_by_id": 1,
  "updated_by_id": null,
  "created_at": "2024-08-23T10:00:00Z",
  "updated_at": null,
  "items": [
    {
      "id": 1,
      "dispatch_order_id": 1,
      "product_id": 789,
      "quantity": 5,
      "unit": "PCS",
      "description": "AC Unit Model XYZ",
      "serial_numbers": "[\"SN001\", \"SN002\"]",
      "batch_numbers": "[\"B001\"]",
      "status": "pending",
      "created_at": "2024-08-23T10:00:00Z",
      "updated_at": null
    }
  ]
}
```

### List Dispatch Orders
**GET** `/api/v1/dispatch/orders`

Retrieves dispatch orders for the organization with filtering and pagination.

**Required Permission**: `dispatch_read`

**Query Parameters**:
- `skip` (int, default: 0) - Number of records to skip for pagination
- `limit` (int, default: 100, max: 100) - Number of records to return
- `status` (string) - Filter by status: pending, in_transit, delivered, cancelled
- `customer_id` (int) - Filter by customer ID
- `ticket_id` (int) - Filter by ticket ID
- `from_date` (string) - Filter from date (YYYY-MM-DD)
- `to_date` (string) - Filter to date (YYYY-MM-DD)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "order_number": "DO/24/00001",
    "customer_id": 123,
    "status": "pending",
    "dispatch_date": null,
    "expected_delivery_date": "2024-08-25T10:00:00Z",
    "delivery_address": "123 Main St, City, State 12345",
    "created_at": "2024-08-23T10:00:00Z",
    "items": [...]
  }
]
```

### Get Dispatch Order
**GET** `/api/v1/dispatch/orders/{order_id}`

Retrieves a specific dispatch order by ID.

**Required Permission**: `dispatch_read`

**Response** (200 OK): Same structure as create response

### Update Dispatch Order
**PUT** `/api/v1/dispatch/orders/{order_id}`

Updates a dispatch order. Status changes trigger automatic date updates.

**Required Permission**: `dispatch_update`

**Request Body** (all fields optional):
```json
{
  "status": "in_transit",
  "tracking_number": "TRK123456789",
  "courier_name": "Express Delivery Co",
  "notes": "Updated delivery instructions"
}
```

**Auto-behavior**:
- Setting status to "in_transit" automatically sets `dispatch_date` if not already set
- Setting status to "delivered" automatically sets `actual_delivery_date` if not already set

**Response** (200 OK): Updated dispatch order object

### Delete Dispatch Order
**DELETE** `/api/v1/dispatch/orders/{order_id}`

Deletes a dispatch order. Only orders with status "pending" can be deleted.

**Required Permission**: `dispatch_delete`

**Response** (204 No Content)

## Installation Jobs API

### Create Installation Job
**POST** `/api/v1/dispatch/installation-jobs`

Creates a new installation job linked to a dispatch order.

**Required Permission**: `installation_create`

**Request Body**:
```json
{
  "dispatch_order_id": 1,
  "customer_id": 123,
  "ticket_id": 456,
  "scheduled_date": "2024-08-26T14:00:00Z",
  "estimated_duration_hours": 4.5,
  "installation_address": "123 Main St, City, State 12345",
  "contact_person": "John Doe",
  "contact_number": "+1234567890",
  "installation_notes": "Requires special equipment",
  "priority": "high",
  "assigned_technician_id": 789
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "job_number": "IJ/24/00001",
  "dispatch_order_id": 1,
  "customer_id": 123,
  "ticket_id": 456,
  "status": "scheduled",
  "priority": "high",
  "scheduled_date": "2024-08-26T14:00:00Z",
  "estimated_duration_hours": 4.5,
  "actual_start_time": null,
  "actual_end_time": null,
  "installation_address": "123 Main St, City, State 12345",
  "contact_person": "John Doe",
  "contact_number": "+1234567890",
  "installation_notes": "Requires special equipment",
  "completion_notes": null,
  "customer_feedback": null,
  "customer_rating": null,
  "assigned_technician_id": 789,
  "created_by_id": 1,
  "updated_by_id": null,
  "created_at": "2024-08-23T10:00:00Z",
  "updated_at": null
}
```

### List Installation Jobs
**GET** `/api/v1/dispatch/installation-jobs`

Retrieves installation jobs for the organization with filtering and pagination.

**Required Permission**: `installation_read`

**Query Parameters**:
- `skip` (int, default: 0) - Number of records to skip for pagination
- `limit` (int, default: 100, max: 100) - Number of records to return
- `status` (string) - Filter by status: scheduled, in_progress, completed, cancelled, rescheduled
- `priority` (string) - Filter by priority: low, medium, high, urgent
- `customer_id` (int) - Filter by customer ID
- `assigned_technician_id` (int) - Filter by assigned technician
- `dispatch_order_id` (int) - Filter by dispatch order
- `from_date` (string) - Filter from date (YYYY-MM-DD)
- `to_date` (string) - Filter to date (YYYY-MM-DD)

### Get Installation Job
**GET** `/api/v1/dispatch/installation-jobs/{job_id}`

Retrieves a specific installation job by ID.

**Required Permission**: `installation_read`

### Update Installation Job
**PUT** `/api/v1/dispatch/installation-jobs/{job_id}`

Updates an installation job. Status changes trigger automatic timestamp updates.

**Required Permission**: `installation_update`

**Auto-behavior**:
- Setting status to "in_progress" automatically sets `actual_start_time` if not already set
- Setting status to "completed" automatically sets `actual_end_time` if not already set

### Delete Installation Job
**DELETE** `/api/v1/dispatch/installation-jobs/{job_id}`

Deletes an installation job.

**Required Permission**: `installation_delete`

**Response** (204 No Content)

## Installation Schedule Prompt Workflow

### Handle Installation Schedule Prompt
**POST** `/api/v1/dispatch/installation-schedule-prompt`

Handles the installation schedule prompt response after delivery challan/service voucher creation.

**Required Permission**: `installation_create`

**Request Body**:
```json
{
  "create_installation_schedule": true,
  "installation_job": {
    "dispatch_order_id": 1,
    "customer_id": 123,
    "installation_address": "123 Main St, City, State 12345",
    "scheduled_date": "2024-08-26T14:00:00Z",
    "priority": "medium",
    "contact_person": "John Doe",
    "contact_number": "+1234567890"
  }
}
```

**Response** (200 OK): Installation job object (same as create response)

## Status Workflows

### Dispatch Order Status Progression
1. **pending** → **in_transit** → **delivered**
2. **pending** → **cancelled**
3. **in_transit** → **cancelled**

### Installation Job Status Progression
1. **scheduled** → **in_progress** → **completed**
2. **scheduled** → **cancelled**
3. **scheduled** → **rescheduled** → **scheduled**
4. **in_progress** → **cancelled**

## Error Responses

All endpoints return standard HTTP status codes:

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Integration with Delivery Challan

The dispatch system integrates with the delivery challan workflow:

1. When a delivery challan is created and marked as delivered
2. System can trigger creation of a dispatch order
3. Frontend shows installation schedule prompt modal
4. User can choose to create installation schedule
5. Installation job is created and linked to the dispatch order

This workflow ensures seamless transition from delivery to installation scheduling.