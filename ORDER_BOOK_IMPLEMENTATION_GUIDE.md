# Order Book System - Implementation and Workflow Guide

## Overview

The Order Book system provides end-to-end order management with workflow tracking from order receipt through production, dispatch, and completion.

## System Architecture

### Components

1. **Frontend UI** (`/pages/order-book.tsx`)
   - Order listing and management
   - Workflow stage visualization
   - Status tracking
   - Quick actions for workflow progression

2. **Backend API** (To be implemented: `/api/v1/order-book/`)
   - Order CRUD operations
   - Workflow state management
   - Status transitions
   - Integration points

3. **Database Models** (To be implemented)
   - Order master table
   - Order line items
   - Workflow stage history
   - Status audit trail

## Workflow Stages

The Order Book implements a structured workflow with the following stages:

### 1. Order Received
- **Description**: Initial order entry and confirmation
- **Actions**:
  - Create new order
  - Assign order number
  - Set customer details
  - Define due date
  - Calculate totals
- **Next Stage**: In Production

### 2. In Production
- **Description**: Order is being manufactured
- **Actions**:
  - Create production order
  - Allocate materials
  - Assign to production line
  - Track progress
- **Integration**: Links to Manufacturing module
- **Next Stage**: Quality Check

### 3. Quality Check
- **Description**: Quality inspection and approval
- **Actions**:
  - Perform quality tests
  - Document results
  - Approve or reject
  - Return to production if needed
- **Integration**: Links to Quality Control module
- **Next Stage**: Ready to Dispatch

### 4. Ready to Dispatch
- **Description**: Order completed and awaiting dispatch
- **Actions**:
  - Generate packing list
  - Create shipping documents
  - Prepare for dispatch
  - Notify customer
- **Next Stage**: Dispatched

### 5. Dispatched
- **Description**: Order shipped to customer
- **Actions**:
  - Record dispatch details
  - Update inventory
  - Generate invoice
  - Track shipment
- **Integration**: Links to Dispatch and Inventory modules
- **Next Stage**: Completed

### 6. Completed
- **Description**: Order delivered and closed
- **Actions**:
  - Confirm delivery
  - Record payment
  - Close order
  - Archive documents
- **Final Stage**: Order lifecycle complete

## Order Statuses

Parallel to workflow stages, orders have statuses:

- **Pending**: Order created, awaiting confirmation
- **Confirmed**: Order approved and scheduled
- **In Production**: Manufacturing in progress
- **Ready to Dispatch**: Quality approved, ready to ship
- **Dispatched**: Shipped to customer
- **Completed**: Delivered and invoiced
- **Cancelled**: Order cancelled (at any stage)

## Frontend Features

### Order Book Page (`/order-book`)

#### Summary Dashboard
- Total Orders count
- In Production count
- Ready to Dispatch count
- Completed count

#### Order List Table
Columns:
- Order Number
- Customer Name
- Order Date
- Due Date
- Amount
- Status
- Workflow Stage
- Actions

#### Actions
- **Edit**: Update order details
- **Advance Workflow**: Move to next stage
- **View Details**: Full order information
- **Export**: Download order data
- **Print**: Generate order documents

#### Workflow Management Dialog
- Select workflow stage
- View stage history
- Add notes/comments
- Update stage with validation

## Backend API Structure (To Be Implemented)

### Endpoints

#### List Orders
```
GET /api/v1/order-book/orders
```
**Query Parameters:**
- `status`: Filter by status
- `workflow_stage`: Filter by workflow stage
- `from_date`: Start date filter
- `to_date`: End date filter
- `customer_id`: Filter by customer

**Response:**
```json
[
  {
    "id": 1,
    "order_number": "ORD-001",
    "customer_id": 123,
    "customer_name": "ABC Corp",
    "order_date": "2025-01-15",
    "due_date": "2025-02-15",
    "status": "in_production",
    "workflow_stage": "in_production",
    "total_amount": 50000.00,
    "line_items": [...],
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-20T14:30:00Z"
  }
]
```

#### Create Order
```
POST /api/v1/order-book/orders
```
**Request Body:**
```json
{
  "customer_id": 123,
  "order_date": "2025-01-15",
  "due_date": "2025-02-15",
  "reference_number": "PO-2025-001",
  "notes": "Urgent order",
  "line_items": [
    {
      "product_id": 456,
      "quantity": 100,
      "unit_price": 500.00,
      "discount_percent": 0,
      "tax_percent": 18
    }
  ]
}
```

#### Update Order
```
PUT /api/v1/order-book/orders/{order_id}
```
**Request Body:** Same as create, with optional fields

#### Get Order Details
```
GET /api/v1/order-book/orders/{order_id}
```

#### Delete Order
```
DELETE /api/v1/order-book/orders/{order_id}
```
Note: Only allowed for pending orders

#### Update Workflow Stage
```
PATCH /api/v1/order-book/orders/{order_id}/workflow
```
**Request Body:**
```json
{
  "workflow_stage": "quality_check",
  "notes": "Moving to QC",
  "updated_by": 1
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-001",
  "workflow_stage": "quality_check",
  "previous_stage": "in_production",
  "updated_at": "2025-01-20T15:00:00Z",
  "workflow_history": [...]
}
```

#### Get Workflow History
```
GET /api/v1/order-book/orders/{order_id}/workflow-history
```

## Database Schema (To Be Implemented)

### orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    organization_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    due_date DATE NOT NULL,
    reference_number VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    workflow_stage VARCHAR(50) NOT NULL DEFAULT 'order_received',
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);
```

### order_line_items Table
```sql
CREATE TABLE order_line_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    description TEXT,
    quantity DECIMAL(15,3) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    tax_percent DECIMAL(5,2) DEFAULT 0,
    line_total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### order_workflow_history Table
```sql
CREATE TABLE order_workflow_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    from_stage VARCHAR(50),
    to_stage VARCHAR(50) NOT NULL,
    changed_by INTEGER NOT NULL,
    notes TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);
```

## Integration Points

### 1. Customer Module
- Link orders to customers
- Display customer order history
- Track customer-specific terms

### 2. Product/Inventory Module
- Link order items to products
- Check inventory availability
- Reserve stock for orders
- Update inventory on dispatch

### 3. Manufacturing Module
- Create production orders from order book
- Link production progress
- Track material consumption
- Update completion status

### 4. Quality Control Module
- Initiate quality checks
- Record inspection results
- Approve/reject for dispatch
- Link QC documents

### 5. Dispatch Module
- Generate dispatch documents
- Create shipping records
- Track delivery status
- Update workflow on dispatch

### 6. Finance/Invoicing Module
- Generate invoices on dispatch
- Link payments to orders
- Track order profitability
- Revenue recognition

## Workflow Rules and Validations

### Stage Transition Rules
1. **Order Received → In Production**
   - Requires: Customer confirmation
   - Validates: Stock availability for materials
   - Creates: Production order

2. **In Production → Quality Check**
   - Requires: Production completion
   - Validates: All items manufactured
   - Creates: QC inspection request

3. **Quality Check → Ready to Dispatch**
   - Requires: QC approval
   - Validates: All tests passed
   - Creates: Packing list

4. **Ready to Dispatch → Dispatched**
   - Requires: Dispatch documents
   - Validates: Inventory updated
   - Creates: Shipping record, Invoice

5. **Dispatched → Completed**
   - Requires: Delivery confirmation
   - Validates: Payment received (optional)
   - Closes: Order

### Cancellation Rules
- Can cancel at any stage before dispatch
- Requires approval for orders in production
- Reverses all related transactions
- Releases reserved inventory

## User Interface Guidelines

### Design Principles
1. **Visual Clarity**: Use color-coded status chips
2. **Quick Actions**: One-click workflow advancement
3. **Information Density**: Show critical data at a glance
4. **Responsive Design**: Works on desktop and tablets
5. **Real-time Updates**: Reflect changes immediately

### Status Color Coding
- Pending: Gray
- Confirmed: Blue
- In Production: Purple
- Ready to Dispatch: Yellow
- Dispatched: Orange
- Completed: Green
- Cancelled: Red

### Workflow Stage Colors
- Order Received: Info (Blue)
- In Production: Primary (Purple)
- Quality Check: Secondary (Teal)
- Ready to Dispatch: Warning (Yellow)
- Dispatched: Warning (Orange)
- Completed: Success (Green)

## Reporting

### Available Reports (To Be Implemented)
1. **Order Status Report**: Summary by status
2. **Production Schedule**: Orders in production
3. **Dispatch Schedule**: Ready to dispatch orders
4. **Order Aging Report**: Overdue orders
5. **Customer Order History**: Per-customer analysis
6. **Order Value Analysis**: Revenue tracking

## Performance Considerations

1. **Indexing**: Index on order_number, customer_id, status, workflow_stage
2. **Pagination**: List orders with pagination (default 50 per page)
3. **Caching**: Cache frequently accessed order data
4. **Async Processing**: Use background jobs for heavy operations
5. **Audit Trail**: Log all workflow changes

## Security and Permissions

### Role-Based Access
- **Order Entry**: Create and edit orders
- **Production Manager**: Advance to production stages
- **QC Inspector**: Update quality check status
- **Dispatch Manager**: Mark as dispatched
- **Finance**: View all orders, mark as completed
- **Admin**: Full access including cancellation

### Data Security
- Organization-level isolation
- Audit trail for all changes
- Encrypted sensitive data
- Role-based field visibility

## Testing Checklist

- [ ] Create new order
- [ ] Update order details
- [ ] Advance workflow stage
- [ ] View workflow history
- [ ] Filter orders by status
- [ ] Filter orders by date
- [ ] Export order list
- [ ] Cancel order
- [ ] Generate production order
- [ ] Complete quality check
- [ ] Dispatch order
- [ ] Complete order
- [ ] View order reports

## Deployment Steps

1. **Database Setup**
   - Run migration scripts
   - Create indexes
   - Set up triggers

2. **Backend Deployment**
   - Deploy API endpoints
   - Configure permissions
   - Test integrations

3. **Frontend Deployment**
   - Deploy updated UI
   - Clear cache
   - Verify menu links

4. **Training**
   - User training sessions
   - Documentation handover
   - Support setup

## Support and Maintenance

### Common Issues
- **Stuck workflow**: Admin can manually update stage
- **Missing data**: Check organization context
- **Slow performance**: Review query optimization

### Maintenance Tasks
- Weekly: Review stuck orders
- Monthly: Archive completed orders
- Quarterly: Performance analysis
- Annually: Schema optimization

## Future Enhancements

Planned features:
- Automated workflow triggers
- Email notifications at stage transitions
- Mobile app for workflow updates
- Barcode scanning for tracking
- Customer portal for order status
- Predictive delivery dates
- Integration with shipping carriers
- Advanced analytics dashboard
