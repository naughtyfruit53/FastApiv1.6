# Manufacturing Vouchers Guide

This comprehensive guide explains the manufacturing voucher system in FastAPI v1.6, covering stock management, production workflows, alerts, and best practices.

## Table of Contents

1. [Overview](#overview)
2. [Manufacturing Order Workflow](#manufacturing-order-workflow)
3. [Stock Deduction Process](#stock-deduction-process)
4. [Production Addition](#production-addition)
5. [Shortage Alerts](#shortage-alerts)
6. [Technician Assignment](#technician-assignment)
7. [Material Tracking](#material-tracking)
8. [Delivery Challan Integration](#delivery-challan-integration)
9. [Manufacturing Journal Vouchers](#manufacturing-journal-vouchers)
10. [Job Card Vouchers](#job-card-vouchers)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)
13. [Suggestions for Improvement](#suggestions-for-improvement)

---

## Overview

The manufacturing module provides comprehensive support for managing production operations including:

- **Manufacturing Orders (MO)**: Plan and track production runs
- **Material Issues (MI)**: Track raw material consumption
- **Manufacturing Journal Vouchers (MJV)**: Record production completion
- **Material Receipt Vouchers (MRV)**: Receive finished goods into inventory
- **Job Card Vouchers (JCV)**: Manage job work sent to external vendors
- **Stock Journals (SJ)**: Adjust inventory for production variances

### Key Features

✅ Automatic voucher numbering with organization-level prefixes  
✅ Bill of Materials (BOM) integration  
✅ Real-time stock tracking and deduction  
✅ Production cost calculation  
✅ Multi-level manufacturing support  
✅ Technician/operator assignment  
✅ Material shortage alerts  
✅ Delivery challan linkage for job work  

---

## Manufacturing Order Workflow

### Creating a Manufacturing Order

A Manufacturing Order (MO) is the starting point for any production activity.

**Step 1: Select BOM**
```
Navigate to: Manufacturing → Manufacturing Orders → Create New
- Select the Bill of Materials (BOM) for the product to manufacture
- System validates BOM exists and is active
```

**Step 2: Define Quantities and Schedule**
```
- Planned Quantity: How many units to produce
- Planned Start Date: When production should begin
- Planned End Date: Target completion date
- Priority: Low/Medium/High/Urgent
```

**Step 3: Assign Department and Location**
```
- Production Department: Which department will handle production
- Production Location: Specific production facility or floor
- Notes: Any special instructions
```

**Step 4: System Actions**
```
✓ Generates unique MO number (e.g., MO/2526/00001)
✓ Calculates estimated cost from BOM
✓ Creates MO in "planned" status
✓ Reserves materials (optional, based on settings)
```

### Manufacturing Order Statuses

| Status | Description | Actions Available |
|--------|-------------|-------------------|
| **Planned** | MO created but not started | Edit, Delete, Start |
| **In Progress** | Production has begun | Issue Materials, Update Progress |
| **Completed** | All planned quantity produced | View Only |
| **On Hold** | Temporarily paused | Resume, Cancel |
| **Cancelled** | Production cancelled | View Only |

---

## Stock Deduction Process

### Material Issue for Production

When materials are consumed in production, create a Material Issue (MI) voucher.

**Step 1: Link to Manufacturing Order**
```
Navigate to: Manufacturing → Material Issues → Create New
- Select Manufacturing Order
- System loads BOM materials automatically
```

**Step 2: Issue Materials**
```
For each material:
- Product: Auto-populated from BOM
- Quantity: Actual quantity being issued
- Unit: Unit of measure
- Unit Price: Current stock valuation
- Notes: Batch number, quality notes, etc.
```

**Step 3: System Stock Deduction**
```
✓ Validates sufficient stock is available
✓ Deducts quantity from inventory
✓ Updates product stock levels
✓ Records transaction in stock ledger
✓ Links to Manufacturing Order
✓ Updates MO material consumption tracking
```

### Stock Deduction Rules

**Automatic Deduction:**
- Stock is deducted immediately upon MI approval
- FIFO (First In First Out) method used by default
- Batch/serial tracking maintained if enabled
- Stock valuation updated in real-time

**Validation Checks:**
- Cannot issue more than available stock (unless negative stock allowed)
- Cannot issue to completed/cancelled Manufacturing Orders
- Requires appropriate user permissions

**Reversal Process:**
If materials need to be returned:
1. Create Material Receipt Voucher (Type: Return)
2. Link to original Material Issue
3. Stock is added back to inventory
4. Original MI marked as "Partially Returned" or "Fully Returned"

---

## Production Addition

### Recording Production Output

Use Manufacturing Journal Vouchers (MJV) to record completed production.

**Step 1: Create MJV**
```
Navigate to: Manufacturing → Manufacturing Journal → Create New
- Select Manufacturing Order
- Select BOM Version
- Enter Finished Product details
```

**Step 2: Record Finished Goods**
```
Finished Products:
- Product: The main output product
- Quantity Produced: Actual production quantity
- Unit Rate: Cost per unit (calculated from materials + overhead)
- Quality Grade: A/B/C grade (if applicable)
- Notes: Production notes, quality remarks
```

**Step 3: Record By-products (if any)**
```
By-products:
- Product: Secondary output
- Quantity: Amount produced
- Unit Rate: Valuation rate
- Notes: Quality, grade, etc.
```

**Step 4: Record Scrap/Waste (if any)**
```
Scrap Materials:
- Material: What was scrapped
- Quantity: Amount wasted
- Reason: Quality issue, spillage, etc.
- Value: Scrap value (if recoverable)
```

**Step 5: System Actions**
```
✓ Adds finished goods to inventory
✓ Adds by-products to inventory
✓ Deducts scrap value from production cost
✓ Updates Manufacturing Order progress
✓ Calculates actual vs. planned variance
✓ Updates product costing
```

### Production Costing

**Actual Production Cost Calculation:**
```
Total Production Cost = 
  Material Cost (from Material Issues)
  + Labor Cost (if tracked)
  + Overhead Cost (if allocated)
  - Scrap Value
  - By-product Value
  
Cost Per Unit = Total Production Cost / Quantity Produced
```

---

## Shortage Alerts

### Real-Time Shortage Detection

The system automatically monitors material availability for production.

**Alert Triggers:**

1. **Below Reorder Level**
   - Alert: 🟡 Yellow warning
   - Triggered when: Stock < Reorder Level
   - Action: Place purchase order

2. **Below Minimum Stock**
   - Alert: 🟠 Orange alert
   - Triggered when: Stock < Minimum Stock Level
   - Action: Urgent procurement needed

3. **Insufficient for MO**
   - Alert: 🔴 Red critical
   - Triggered when: Available stock < MO requirement
   - Action: Cannot start production, procure immediately

4. **Out of Stock**
   - Alert: 🔴 Red critical
   - Triggered when: Stock = 0
   - Action: Production blocked, emergency procurement

### Viewing Shortage Alerts

**Dashboard Widget:**
```
Manufacturing Dashboard → Material Shortages
- Shows all materials below reorder level
- Indicates which MOs are affected
- Links to create purchase requisitions
```

**Material-wise Alert:**
```
Navigate to: Inventory → Products → Low Stock
Filter by: "Required for Manufacturing"
- See all items needed for active MOs
- View shortage quantity
- Estimated impact on production schedule
```

### Configuring Alert Thresholds

```
Navigate to: Settings → Inventory Settings → Stock Levels

For each product:
- Reorder Level: Trigger for routine replenishment
- Minimum Stock: Safety stock threshold
- Lead Time: Days to procure
- Economic Order Quantity: Optimal order size

System calculates: 
Reorder Level = (Average Daily Usage × Lead Time) + Safety Stock
```

### Automated Actions

**Email Notifications:**
- Purchase Manager receives daily shortage report
- Production Manager notified of affected MOs
- Procurement team gets immediate alerts for critical items

**System Actions:**
- Auto-generate purchase requisitions (if enabled)
- Flag affected MOs as "Material Shortage"
- Block MI creation if stock insufficient (optional setting)
- Suggest alternate materials/suppliers (future enhancement)

---

## Technician Assignment

### Assigning Operators to Manufacturing Orders

**Method 1: Direct Assignment on MO**
```
Manufacturing Order → Edit → Assign Technician
- Select Primary Operator: Main person responsible
- Select Team Members: Supporting operators
- Assign Supervisor: Oversees the production
- Expected Hours: Estimated man-hours
```

**Method 2: Job Card Based Assignment**
```
For job work sent outside:
Job Card Voucher → Vendor/Technician
- Select Vendor: External job worker
- Assign Internal Coordinator: Tracks the job
- Define Deliverables: What should be received back
```

**Operator Performance Tracking:**
```
Navigate to: Manufacturing → Operator Reports
- Production by Operator
- Efficiency metrics (actual vs. planned time)
- Quality metrics (rejection rate)
- Cost per operator
```

### Operator Skill Matching

**Skill-Based Assignment (Future):**
```
Settings → Users → Skills Matrix
- Define operator skills (welding, assembly, etc.)
- Match MO requirements to operator skills
- System suggests best-fit operators
```

---

## Material Tracking

### End-to-End Material Traceability

**Tracking Material Flow:**

1. **Purchase Order (PO)**
   - Material ordered from vendor
   - PO Number: PO/2526/00123
   - Tracking: Vendor, quantity, expected date

2. **Goods Receipt Note (GRN)**
   - Material received into warehouse
   - GRN Number: GRN/2526/00456
   - Links to PO
   - Batch/Serial numbers recorded

3. **Material Issue (MI)**
   - Material issued to production
   - MI Number: MI/2526/00789
   - Links to MO
   - Consumes from specific batch/serial

4. **Manufacturing Journal (MJV)**
   - Production completed
   - MJV Number: MJV/2526/00234
   - Links materials consumed to finished goods produced

5. **Material Receipt (MRV)**
   - Finished goods added to inventory
   - MRV Number: MRV/2526/00567
   - Links to MJV

6. **Delivery Challan (DC)**
   - Finished goods dispatched
   - DC Number: DC/2526/00890
   - Links to MRV/Stock
   - Customer delivery tracking

### Batch/Lot Tracking

**Enable Batch Tracking:**
```
Settings → Inventory → Enable Batch Tracking
For each product: Enable "Track by Batch"
```

**Batch in Material Issue:**
```
When issuing materials:
- Select Batch Number
- System shows: Batch, Expiry Date, Available Qty
- FEFO (First Expiry First Out) can be enforced
```

**Batch in Production:**
```
Manufacturing Journal:
- Records which batches were consumed
- Generates new batch for finished goods
- Maintains batch genealogy
```

### Serial Number Tracking

**For serialized items:**
```
Material Issue:
- Select individual serial numbers being used
- System marks serials as "In Production"

Manufacturing Journal:
- Generate new serial numbers for output
- Link input serials to output serials
- Maintain complete serial history
```

### Material Tracking Reports

**Traceability Reports:**

1. **Forward Traceability**
   - Start from raw material batch
   - See all finished goods produced using it
   - Useful for quality issues, recalls

2. **Backward Traceability**
   - Start from finished goods batch/serial
   - See all raw materials used
   - Useful for root cause analysis

3. **Where-Used Report**
   - For any material/batch
   - Shows all MOs where it was used
   - Current location/status

---

## Delivery Challan Integration

### Linking Job Work to Delivery Challans

When manufacturing is outsourced, Job Card Vouchers link to Delivery Challans.

**Step 1: Create Job Card Voucher**
```
Navigate to: Manufacturing → Job Cards → Create New
- Job Type: "External Job Work"
- Vendor: Select job work vendor
- Manufacturing Order: Link to MO (optional)
- Job Description: Details of work
```

**Step 2: Record Supplied Materials**
```
Supplied Materials (sent to vendor):
- Material: Product being sent
- Quantity Supplied: Amount sent
- Unit Rate: Valuation
- Expected Return Date
```

**Step 3: Create Delivery Challan**
```
Navigate to: Sales → Delivery Challan → Create New
- Type: "Job Work"
- Vendor/Party: Same as Job Card vendor
- Link Job Card: Select JCV number
- Materials: Auto-filled from JCV
- Purpose: "For Job Work"
- Returnable: Yes
```

**Step 4: Track Outward Delivery**
```
Delivery Challan:
- DC Number: DC/2526/00123
- Transporter: Logistics partner
- Vehicle Number: Transport details
- e-Way Bill: If applicable
- Expected Return: Date materials should come back
```

**Step 5: Receive Processed Materials**
```
When job work is complete:
- Create Material Receipt Voucher
- Link to Job Card and Delivery Challan
- Record Received Outputs
- Record Material Returns (if any)
- Close Job Card
```

### Job Card Lifecycle

```
[Created] → [Materials Issued] → [DC Generated] → [Sent to Vendor] 
    ↓
[Work in Progress] → [QC at Vendor] → [Dispatched Back] → [Received] 
    ↓
[Quality Check] → [Accepted/Rejected] → [Completed/Closed]
```

### DC Tracking Features

**Real-Time Status:**
- View all outward job work DCs
- Track which are pending return
- Alert for overdue returns
- GPS tracking integration (if available)

**Cost Tracking:**
- Material cost sent out
- Job work charges
- Transportation cost
- Total job cost
- Link to MO costing

---

## Manufacturing Journal Vouchers

### Complete MJV Guide

Manufacturing Journal Vouchers (MJV) are the most critical vouchers that record production completion.

**When to Create MJV:**
- When a production batch is completed
- When doing partial production receipt
- When recording by-products or scrap
- When updating actual vs. planned costs

**MJV Components:**

1. **Header Information**
   - MJV Number: Auto-generated (e.g., MJV/2526/00001)
   - Date: Production completion date
   - Manufacturing Order: Link to MO
   - BOM: Bill of Materials used
   - Shift: Production shift (if tracked)
   - Operator: Person who completed production

2. **Finished Products Section**
   - Product: Main output
   - Quantity: Actual produced
   - Unit Rate: Production cost per unit
   - Total Value: Quantity × Rate
   - Quality Grade: If quality grading is used
   - Warehouse Location: Where to store

3. **By-products Section**
   - Product: Secondary outputs
   - Quantity: Amount produced
   - Rate: Valuation rate
   - Account Treatment: How to value in accounts

4. **Scrap/Waste Section**
   - Material: What was wasted
   - Quantity: Amount scrapped
   - Reason: Quality, spillage, etc.
   - Scrap Value: Recoverable value

5. **Material Consumption**
   - Lists all materials used (from MI)
   - Shows planned vs. actual usage
   - Variance analysis

**Accounting Impact:**
```
Debit:  Finished Goods Inventory
Debit:  By-products Inventory
Debit:  Scrap Account (if negative value)
Credit: Work in Progress (WIP) Account
Credit: Material Consumed Account
Credit: Scrap Account (if positive value)
```

---

## Job Card Vouchers

### Managing External Job Work

Job Card Vouchers (JCV) manage production work outsourced to vendors.

**Types of Job Work:**

1. **Processing Job Work**
   - Material sent for processing (heat treatment, painting, etc.)
   - Material returns in processed form
   - Example: Raw casting → Machined part

2. **Assembly Job Work**
   - Components sent for assembly
   - Assembled product received back
   - Example: PCB + components → Assembled board

3. **Finishing Job Work**
   - Products sent for final finishing
   - Finished products received
   - Example: Rough product → Polished product

**JCV Creation Process:**

```
Step 1: Create Job Card
- Vendor: Job work vendor
- Job Type: Processing/Assembly/Finishing
- Manufacturing Order: Link if part of MO
- Expected Completion: Due date
- Job Rate: Cost per unit or total job cost

Step 2: Define Supplied Materials
For each material:
- Material: What you're sending
- Quantity: Amount
- Rate: Valuation
- Expected Return %: How much should come back

Step 3: Define Expected Outputs
For each output:
- Product: What you expect to receive
- Quantity: Expected amount
- Rate: Valuation rate
- Quality Parameters: Acceptance criteria

Step 4: Issue Materials (via MI)
- Create Material Issue
- Link to Job Card
- Materials physically sent to vendor

Step 5: Generate Delivery Challan
- Create DC for job work
- Link to Job Card
- Track shipment to vendor

Step 6: Receive Outputs (via MRV)
- Create Material Receipt Voucher
- Link to Job Card
- QC check received items
- Accept or reject

Step 7: Settle Job Card
- Record job work charges
- Record any material losses
- Close Job Card
```

**Job Card Tracking:**

```
Dashboard View:
- Active Job Cards: Currently with vendors
- Overdue Job Cards: Past expected return date
- Pending QC: Received but quality check pending
- Rejected Items: Did not meet quality standards
```

---

## Best Practices

### 1. Manufacturing Order Management

✅ **Always link MOs to BOMs** - Ensures accurate material and cost calculation  
✅ **Set realistic lead times** - Account for material procurement + production time  
✅ **Review shortage alerts daily** - Prevents production delays  
✅ **Update MO status regularly** - Keeps everyone informed  
✅ **Close completed MOs promptly** - Maintains clean production queue  

### 2. Material Management

✅ **Issue materials just-in-time** - Reduces WIP inventory holding cost  
✅ **Enable batch tracking** - Essential for traceability and quality control  
✅ **Perform cycle counts** - Regular physical verification prevents discrepancies  
✅ **Set appropriate reorder levels** - Balance between stock-outs and excess inventory  
✅ **Track material wastage** - Identify areas for process improvement  

### 3. Production Recording

✅ **Record production daily** - Don't wait for batch completion  
✅ **Document quality issues** - Helps in continuous improvement  
✅ **Track actual time spent** - Improves future planning  
✅ **Record by-products and scrap** - Accurate inventory and costing  
✅ **Link all documents** - MO → MI → MJV → MRV provides full traceability  

### 4. Job Work Management

✅ **Clear job descriptions** - Prevents misunderstandings with vendors  
✅ **Document quality parameters** - Define acceptance criteria upfront  
✅ **Track return timelines** - Follow up on overdue job work  
✅ **Maintain vendor performance records** - Quality, timeliness, cost  
✅ **Insure valuable materials** - When sending expensive materials to vendors  

### 5. System Configuration

✅ **Configure voucher prefixes** - Organization-level for easy identification  
✅ **Set user permissions carefully** - Not everyone should approve production  
✅ **Enable email notifications** - Keep stakeholders informed automatically  
✅ **Regular data backups** - Production data is critical  
✅ **Train users thoroughly** - Reduces errors and improves adoption  

---

## Troubleshooting

### Common Issues and Solutions

**Issue 1: "Insufficient Stock" error when issuing materials**
```
Problem: Stock level shows insufficient quantity
Solutions:
1. Check if stock is allocated to other orders
2. Verify if correct warehouse is selected
3. Check if batch/serial selection is correct
4. Create emergency purchase or transfer from another location
```

**Issue 2: Manufacturing Order stuck in "In Progress"**
```
Problem: Cannot close MO even after production complete
Solutions:
1. Ensure all Material Issues are accounted for
2. Create Manufacturing Journal for all produced quantity
3. Check if there are pending approvals
4. Verify all linked documents are in "Completed" status
```

**Issue 3: Incorrect production cost calculation**
```
Problem: Cost per unit doesn't match expected value
Solutions:
1. Verify all Material Issues are linked to the MO
2. Check if labor and overhead are properly allocated
3. Ensure by-product and scrap values are recorded
4. Review BOM cost calculation
5. Check for any manual adjustments
```

**Issue 4: Job Card not closing**
```
Problem: Cannot close Job Card Voucher
Solutions:
1. Ensure Delivery Challan is marked "Returned"
2. Verify all expected outputs are received
3. Check if job work invoice is recorded
4. Ensure all material reconciliation is complete
```

**Issue 5: Batch tracking not working**
```
Problem: System not asking for batch selection
Solutions:
1. Check if "Track by Batch" is enabled for the product
2. Ensure batches are created in the system
3. Verify user has permission to view batches
4. Check if batch tracking is enabled at org level
```

---

## Suggestions for Improvement

### Immediate Improvements (Can be implemented now)

1. **Auto-Material Reservation**
   - Reserve materials when MO is created
   - Prevents allocation of same stock to multiple orders
   - Release reservation if MO is cancelled

2. **Production Scheduling Dashboard**
   - Gantt chart view of all active MOs
   - Resource (machine/operator) utilization view
   - Critical path highlighting
   - Drag-and-drop rescheduling

3. **Quality Control Integration**
   - QC checkpoints in production flow
   - Rejection tracking and analysis
   - Auto-generate corrective action requests
   - Link quality issues to suppliers/operators

4. **Mobile App for Shop Floor**
   - Operators can view their assigned MOs
   - Scan barcodes for material issue
   - Record production quantity in real-time
   - Capture photos of quality issues

5. **Advanced Costing Features**
   - Machine hour rate allocation
   - Power consumption tracking
   - Overhead allocation by cost center
   - Standard vs. actual cost variance reports

### Medium-Term Enhancements (Requires development)

1. **AI-Powered Production Planning**
   - ML model to predict optimal production schedule
   - Considers demand forecast, material availability, capacity
   - Suggests best sequence to minimize changeover time

2. **IoT Integration**
   - Connect to production machines
   - Real-time production count
   - Machine downtime alerts
   - Predictive maintenance alerts

3. **Advanced Material Planning (MRP)**
   - Multi-level BOM explosion
   - Capacity planning
   - What-if scenario analysis
   - Vendor performance-based lead times

4. **Blockchain for Traceability**
   - Immutable record of material flow
   - Useful for regulated industries (pharma, food)
   - Customer-visible traceability portal

5. **AR/VR for Training**
   - Virtual training for complex assembly
   - AR overlay of assembly instructions
   - Remote expert assistance

### Long-Term Vision (Future releases)

1. **Fully Automated Factory (Lights-Out Manufacturing)**
   - Robots execute MOs automatically
   - AI quality inspection
   - Automated material handling
   - Zero human intervention

2. **Digital Twin**
   - Virtual replica of production floor
   - Simulate production scenarios
   - Optimize before physical implementation

3. **Sustainable Manufacturing**
   - Carbon footprint tracking per product
   - Waste reduction targets and monitoring
   - Energy efficiency optimization
   - Circular economy support (recycling, reuse)

---

## API Reference

### Key Endpoints

**Manufacturing Orders:**
- `GET /api/v1/manufacturing/manufacturing-orders/` - List all MOs
- `POST /api/v1/manufacturing/manufacturing-orders/` - Create MO
- `GET /api/v1/manufacturing/manufacturing-orders/{id}` - Get MO details
- `GET /api/v1/manufacturing/manufacturing-orders/next-number` - Get next MO number

**Material Issues:**
- `GET /api/v1/manufacturing/material-issues/` - List all MIs
- `POST /api/v1/manufacturing/material-issues/` - Create MI
- `GET /api/v1/manufacturing/material-issues/next-number` - Get next MI number

**Manufacturing Journal:**
- `GET /api/v1/manufacturing/manufacturing-journal-vouchers/` - List all MJVs
- `POST /api/v1/manufacturing/manufacturing-journal-vouchers/` - Create MJV
- `GET /api/v1/manufacturing/manufacturing-journal-vouchers/next-number` - Get next MJV number

**Job Cards:**
- `GET /api/v1/manufacturing/job-card-vouchers/` - List all JCVs
- `POST /api/v1/manufacturing/job-card-vouchers/` - Create JCV
- `GET /api/v1/manufacturing/job-card-vouchers/next-number` - Get next JCV number

---

## Support

For issues, questions, or feature requests:
1. Check this guide's troubleshooting section
2. Review API documentation
3. Contact system administrator
4. Create a support ticket

---

**Last Updated:** 2024-12-19  
**Version:** 2.0  
**Author:** FastAPI v1.6 Team
