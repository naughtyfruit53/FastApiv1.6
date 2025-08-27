# Inventory & Parts Management API Documentation

## Overview

The Inventory & Parts Management system provides comprehensive tracking of inventory items, parts usage in jobs, and automated alerts for low stock situations. This system integrates seamlessly with the existing Service CRM platform.

## API Endpoints

Base URL: `/api/v1/inventory`

### Inventory Transactions

#### GET /transactions
Get inventory transactions with filtering options.

**Parameters:**
- `skip` (int): Number of records to skip (pagination)
- `limit` (int): Maximum number of records to return (max 100)
- `product_id` (int, optional): Filter by product ID
- `transaction_type` (string, optional): Filter by transaction type ('receipt', 'issue', 'adjustment', 'transfer')
- `start_date` (datetime, optional): Filter transactions from this date
- `end_date` (datetime, optional): Filter transactions until this date

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "product_id": 1,
    "product_name": "Screws",
    "transaction_type": "receipt",
    "quantity": 100.0,
    "unit": "pcs",
    "location": "warehouse",
    "reference_type": "purchase",
    "reference_id": 123,
    "reference_number": "PO-2024-001",
    "notes": "Initial stock receipt",
    "unit_cost": 0.10,
    "total_cost": 10.00,
    "stock_before": 0.0,
    "stock_after": 100.0,
    "created_by_name": "John Manager",
    "transaction_date": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### POST /transactions
Create a new inventory transaction.

**Request Body:**
```json
{
  "product_id": 1,
  "transaction_type": "receipt",
  "quantity": 50.0,
  "unit": "pcs",
  "location": "warehouse",
  "reference_type": "purchase",
  "reference_id": 123,
  "reference_number": "PO-2024-001",
  "notes": "Stock replenishment",
  "unit_cost": 0.10,
  "total_cost": 5.00,
  "stock_before": 100.0,
  "stock_after": 150.0,
  "transaction_date": "2024-01-15T10:30:00Z"
}
```

### Job Parts Management

#### GET /job-parts
Get job parts assignments with filtering options.

**Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum number of records to return
- `job_id` (int, optional): Filter by job ID
- `product_id` (int, optional): Filter by product ID
- `status` (string, optional): Filter by status ('planned', 'allocated', 'used', 'returned')

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "job_id": 1,
    "job_number": "JOB-2024-001",
    "product_id": 1,
    "product_name": "Screws",
    "quantity_required": 25.0,
    "quantity_used": 20.0,
    "unit": "pcs",
    "status": "used",
    "location_used": "customer_site",
    "notes": "Screws for mounting",
    "unit_cost": 0.10,
    "total_cost": 2.00,
    "allocated_by_name": "John Manager",
    "used_by_name": "Mike Technician",
    "allocated_at": "2024-01-15T08:00:00Z",
    "used_at": "2024-01-15T14:30:00Z",
    "created_at": "2024-01-15T08:00:00Z"
  }
]
```

#### POST /job-parts
Assign parts to a job.

**Request Body:**
```json
{
  "job_id": 1,
  "product_id": 1,
  "quantity_required": 25.0,
  "unit": "pcs",
  "notes": "Screws for mounting brackets"
}
```

#### PUT /job-parts/{job_part_id}
Update job parts assignment (mark as used, update quantities, etc.).

**Request Body:**
```json
{
  "quantity_used": 20.0,
  "status": "used",
  "location_used": "customer_site",
  "notes": "Used 20 out of 25 allocated screws",
  "unit_cost": 0.10,
  "total_cost": 2.00
}
```

### Inventory Alerts

#### GET /alerts
Get inventory alerts with filtering options.

**Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum number of records to return
- `status` (string, optional): Filter by status ('active', 'acknowledged', 'resolved')
- `priority` (string, optional): Filter by priority ('low', 'medium', 'high', 'critical')
- `alert_type` (string, optional): Filter by type ('low_stock', 'out_of_stock', 'reorder')

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "product_id": 1,
    "product_name": "Screws",
    "alert_type": "low_stock",
    "current_stock": 15.0,
    "reorder_level": 100.0,
    "location": "warehouse",
    "status": "active",
    "priority": "high",
    "message": "Screws stock is below reorder level",
    "suggested_order_quantity": 200.0,
    "acknowledged_by_name": null,
    "acknowledged_at": null,
    "resolved_at": null,
    "created_at": "2024-01-15T15:00:00Z"
  }
]
```

#### PUT /alerts/{alert_id}/acknowledge
Acknowledge an inventory alert.

**Response:**
```json
{
  "message": "Alert acknowledged successfully"
}
```

### Reports

#### GET /reports/usage
Generate inventory usage report.

**Parameters:**
- `start_date` (datetime, optional): Report start date (default: 30 days ago)
- `end_date` (datetime, optional): Report end date (default: today)
- `product_id` (int, optional): Filter by product ID

**Response:**
```json
[
  {
    "product_id": 1,
    "product_name": "Screws",
    "total_issued": 150.0,
    "total_received": 200.0,
    "current_stock": 50.0,
    "reorder_level": 100,
    "total_jobs_used": 5,
    "unit": "pcs",
    "location": "warehouse"
  }
]
```

#### GET /reports/low-stock
Generate low stock report.

**Response:**
```json
[
  {
    "product_id": 1,
    "product_name": "Screws",
    "current_stock": 15.0,
    "reorder_level": 100,
    "stock_deficit": 85.0,
    "suggested_order_quantity": 200.0,
    "unit": "pcs",
    "location": "warehouse",
    "days_since_last_receipt": 15
  }
]
```

## Business Logic

### Automatic Stock Updates
- When parts are marked as "used" in a job, inventory transactions are automatically created
- Stock levels are decremented in real-time
- All changes maintain an audit trail

### Low Stock Alerts
- Alerts are automatically generated when stock falls below reorder levels
- Out-of-stock alerts are created when stock reaches zero
- Suggested order quantities are calculated automatically

### Multi-Location Support
- Inventory can be tracked across multiple locations
- Location-specific stock levels and transactions
- Support for inter-location transfers

### Role-Based Permissions
- `inventory_read`: View inventory transactions and reports
- `inventory_create`: Create inventory transactions
- `job_parts_read`: View job parts assignments
- `job_parts_create`: Assign parts to jobs
- `inventory_alerts_read`: View inventory alerts
- `inventory_alerts_update`: Acknowledge alerts
- `inventory_reports_read`: Access inventory reports

## Integration Points

### With Job Management
- Parts are assigned to installation jobs
- Usage is tracked when jobs are completed
- Automatic inventory deduction on job closure

### With Purchase Management
- Receipt transactions can reference purchase orders
- Cost tracking for inventory valuation

### With Reporting System
- Real-time inventory reports
- Usage analytics by product, job, technician
- Stock valuation reports

## Error Handling

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Insufficient stock. Current: 5.0, Requested: 10.0"
}
```

**404 Not Found**
```json
{
  "detail": "Product not found"
}
```

**403 Forbidden**
```json
{
  "detail": "Insufficient permissions"
}
```

## Best Practices

1. **Stock Transactions**: Always create transactions through the API to maintain proper audit trails
2. **Job Parts**: Assign parts to jobs before starting work to ensure proper tracking
3. **Alert Management**: Regularly review and acknowledge low stock alerts
4. **Reporting**: Use date ranges for large reports to improve performance
5. **Locations**: Use consistent location names for accurate tracking