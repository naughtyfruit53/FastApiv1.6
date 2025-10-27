# Order Book - User Guide

## Overview

The Order Book module provides comprehensive order management and workflow tracking capabilities. It helps you monitor orders from placement through completion, manage production workflows, and ensure timely delivery.

## Features

### 1. Order Management (`/api/v1/order-book/orders`)

**Track All Orders:**
- View all orders with filtering and search
- Monitor order status and workflow stages
- Track order values and customer information
- Manage order items and quantities

**API Endpoints:**
- `GET /api/v1/order-book/orders` - List all orders with filters
- `GET /api/v1/order-book/orders/{id}` - Get order details
- `POST /api/v1/order-book/orders` - Create a new order
- `PATCH /api/v1/order-book/orders/{id}/workflow` - Update workflow stage
- `PATCH /api/v1/order-book/orders/{id}/status` - Update order status

### 2. Order Statuses

**Available Order Statuses:**
- `pending` - Order received, awaiting confirmation
- `confirmed` - Order confirmed and accepted
- `in_production` - Order is being manufactured/prepared
- `ready_to_dispatch` - Order ready for shipment
- `dispatched` - Order shipped to customer
- `completed` - Order delivered and closed
- `cancelled` - Order cancelled

**Status Transitions:**
```
pending → confirmed → in_production → ready_to_dispatch → dispatched → completed
         ↓
    cancelled (from any status except completed)
```

### 3. Workflow Stages

**Production Workflow Stages:**
1. `order_received` - Order entered into system
2. `in_production` - Manufacturing/assembly in progress
3. `quality_check` - QC inspection and approval
4. `ready_to_dispatch` - Packaging and dispatch preparation
5. `dispatched` - Shipped from warehouse
6. `completed` - Delivered to customer

**Workflow Features:**
- Automatic progression through stages
- Manual stage updates for custom workflows
- Timestamp tracking for each stage
- User tracking for stage changes
- Workflow history and audit trail

### 4. Order Filters and Search

**Filter Options:**
- By Status (`status` parameter)
- By Workflow Stage (`workflow_stage` parameter)
- By Customer (`customer_id` parameter)
- By Date Range (`start_date` and `end_date` parameters)
- By Order Number (search)

**Example Queries:**
```bash
# Get all pending orders
GET /api/v1/order-book/orders?status=pending

# Get all orders in production
GET /api/v1/order-book/orders?workflow_stage=in_production

# Get orders for specific customer
GET /api/v1/order-book/orders?customer_id=123

# Get orders in date range
GET /api/v1/order-book/orders?start_date=2025-01-01&end_date=2025-01-31
```

### 5. Dashboard Statistics (`/api/v1/order-book/dashboard-stats`)

**Key Metrics:**
- Total orders
- Active orders (not completed or cancelled)
- Completed orders
- Cancelled orders
- Total order value
- Orders by workflow stage
- Overdue orders
- Orders due this week

**Dashboard Features:**
- Real-time order counts
- Value summaries
- Stage distribution
- Due date tracking
- Quick access to critical orders

### 6. Order Details

**Information Tracked:**
- Order number (unique identifier)
- Customer name and ID
- Order date and due date
- Current status and workflow stage
- Total amount
- Order items (products, quantities, prices)
- Workflow history
- Notes and comments

### 7. Workflow Management

**Update Workflow Stage:**
```bash
PATCH /api/v1/order-book/orders/{id}/workflow
{
  "workflow_stage": "quality_check"
}
```

**Update Order Status:**
```bash
PATCH /api/v1/order-book/orders/{id}/status
{
  "status": "ready_to_dispatch"
}
```

**Best Practices:**
- Update workflow stage as work progresses
- Keep status synchronized with workflow
- Add notes when changing stages
- Review and approve stage changes

### 8. Available Workflow Stages and Statuses

**Get Workflow Stages:**
```bash
GET /api/v1/order-book/workflow-stages
```

Returns all available workflow stages with display labels and order.

**Get Order Statuses:**
```bash
GET /api/v1/order-book/order-statuses
```

Returns all available order statuses with display labels.

## Using the Order Book

### Creating an Order

1. Navigate to Order Book
2. Click "Create Order"
3. Fill in order details:
   - Customer (select from dropdown)
   - Order date
   - Due date
   - Order items (products, quantities, prices)
4. Review total amount
5. Click "Create Order"

### Updating Order Workflow

1. Open order details
2. View current workflow stage
3. Click "Update Stage"
4. Select next appropriate stage
5. Add notes if needed
6. Confirm stage update

### Monitoring Orders

1. **Dashboard View**:
   - Quick overview of all orders
   - See orders by stage
   - Identify overdue orders

2. **List View**:
   - Detailed order listing
   - Filter by status/stage/customer
   - Sort by date or value

3. **Detail View**:
   - Complete order information
   - Full workflow history
   - All order items
   - Customer details

### Tracking Order Progress

**Visual Indicators:**
- Color-coded status badges
- Progress bars for workflow stages
- Due date warnings
- Overdue alerts

**Notifications:**
- Stage change notifications
- Due date reminders
- Status update alerts

## Integration with Other Modules

### Sales Orders

Order Book integrates with Sales Order vouchers:
- Sales orders can create order book entries
- Workflow updates reflect in sales module
- Delivery status synchronized

### Production

Order Book connects with Manufacturing:
- Production orders link to order book
- Manufacturing progress updates workflow
- Quality check integration

### Inventory

Order Book affects inventory:
- Reserved inventory for pending orders
- Automatic inventory allocation
- Stock availability checking

## Reporting and Analytics

### Available Reports

1. **Order Summary Report**:
   - Total orders by period
   - Value by customer/product
   - Average order value

2. **Workflow Analysis**:
   - Time spent in each stage
   - Bottleneck identification
   - Efficiency metrics

3. **Customer Analysis**:
   - Top customers by value
   - Order frequency
   - Payment patterns

4. **Due Date Report**:
   - Upcoming deliveries
   - Overdue orders
   - On-time delivery rate

## Permissions

The Order Book module uses role-based access:

- Order view permissions
- Order create permissions
- Order update permissions
- Workflow management permissions

Contact your administrator to configure permissions.

## Best Practices

1. **Order Entry**:
   - Enter orders immediately upon receipt
   - Verify customer information
   - Confirm due dates with production

2. **Workflow Updates**:
   - Update stages promptly
   - Add context in notes
   - Review before stage changes

3. **Due Date Management**:
   - Set realistic due dates
   - Monitor approaching deadlines
   - Communicate delays early

4. **Data Quality**:
   - Keep order information accurate
   - Update statuses regularly
   - Archive completed orders

5. **Communication**:
   - Notify customers of status changes
   - Alert production of urgent orders
   - Coordinate with dispatch team

## Troubleshooting

**Issue: Cannot see orders**
- Check filter settings
- Verify date range
- Confirm permissions

**Issue: Cannot update workflow**
- Ensure order is not completed
- Check workflow permissions
- Verify valid stage transition

**Issue: Dashboard not loading**
- Clear browser cache
- Check API connectivity
- Verify backend is running

**Issue: Incorrect order totals**
- Recalculate order items
- Check product prices
- Review tax calculations

## Future Enhancements

The Order Book module is continuously being improved. Upcoming features include:

- Automated workflow progression
- Integration with delivery tracking
- Advanced analytics dashboards
- Mobile order management
- Customer portal access
- Automated notifications
- PDF order confirmations

## Support

For additional help or feature requests, contact your system administrator or refer to the [API Documentation](/docs).

## Quick Reference

### Common API Calls

```bash
# Get all orders
GET /api/v1/order-book/orders

# Get order details
GET /api/v1/order-book/orders/1

# Create order
POST /api/v1/order-book/orders
{
  "customer_id": 1,
  "order_date": "2025-01-20",
  "due_date": "2025-02-15",
  "items": [...]
}

# Update workflow
PATCH /api/v1/order-book/orders/1/workflow
{
  "workflow_stage": "in_production"
}

# Get dashboard stats
GET /api/v1/order-book/dashboard-stats
```
