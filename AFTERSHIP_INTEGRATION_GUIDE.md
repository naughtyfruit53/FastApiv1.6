# AfterShip Integration Guide

This guide explains the AfterShip API integration for real-time shipment tracking in FastAPI v1.6.

## Table of Contents

1. [Overview](#overview)
2. [Setup and Configuration](#setup-and-configuration)
3. [Real-Time Tracking](#real-time-tracking)
4. [Webhook Support](#webhook-support)
5. [Bulk Tracking](#bulk-tracking)
6. [Advanced Filters](#advanced-filters)
7. [Email Notifications](#email-notifications)
8. [BOM Versioning](#bom-versioning)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

AfterShip is a shipment tracking platform that provides real-time tracking updates for over 1,100 carriers worldwide. This integration enables:

✅ **Real-time tracking** for purchase orders and delivery challans  
✅ **Automatic status updates** via webhooks  
✅ **Bulk tracking operations** for multiple shipments  
✅ **Email notifications** to customers on status changes  
✅ **Multi-carrier support** (Blue Dart, DHL, FedEx, India Post, etc.)  
✅ **Delivery exceptions** and delay alerts  
✅ **Estimated delivery dates**  
✅ **Proof of delivery** storage  

### Key Features

- **900+ Couriers Supported**: Global coverage including all major Indian carriers
- **Real-time Updates**: Get notified the moment a shipment status changes
- **Predicted Delivery Dates**: AI-powered ETA predictions
- **Exception Handling**: Alerts for delivery delays, failed attempts, etc.
- **Multi-language**: Support for 100+ languages
- **Mobile Tracking Page**: Customer-friendly tracking interface

---

## Setup and Configuration

### Step 1: Get AfterShip API Key

1. Sign up at [AfterShip](https://www.aftership.com/)
2. Navigate to **Settings → API**
3. Create a new API key
4. Copy the API key (starts with `asat_...`)

### Step 2: Configure in FastAPI

```
Navigate to: Settings → Integrations → AfterShip

Enter your credentials:
- API Key: Your AfterShip API key
- Webhook URL: https://yourdomain.com/api/v1/webhooks/aftership
- Enable: Toggle to activate integration

Save configuration
```

### Step 3: Environment Variables

Add to your `.env` file:

```bash
# AfterShip Configuration
AFTERSHIP_API_KEY=asat_xxxxxxxxxxxxxxxxxxxxxxxx
AFTERSHIP_WEBHOOK_SECRET=your_webhook_secret_here
AFTERSHIP_ENABLED=true
```

### Step 4: Verify Integration

```
Navigate to: Settings → Integrations → AfterShip → Test Connection

System will:
✓ Validate API key
✓ Check webhook connectivity
✓ Verify courier detection
✓ Display status: Connected ✅
```

---

## Real-Time Tracking

### Adding Tracking to Purchase Orders

**Method 1: Manual Entry**

```
Purchase Order Details → Tracking Information
- Transporter Name: Blue Dart
- Tracking Number: BD123456789
- Click "Add Tracking"

System Actions:
✓ Auto-detects courier from tracking number format
✓ Creates tracking in AfterShip
✓ Starts real-time monitoring
✓ Links tracking to PO
✓ Sends confirmation email to vendor
```

**Method 2: Bulk Upload**

```
Purchase Orders List → Select Multiple → Bulk Actions → Add Tracking
- Upload CSV with columns: PO Number, Tracking Number, Courier
- System processes all entries
- Creates AfterShip trackings
- Sends notifications
```

**Method 3: API Integration**

```python
# Using the API
POST /api/v1/purchase-orders/{id}/tracking
{
  "transporter_name": "Blue Dart",
  "tracking_number": "BD123456789",
  "carrier_code": "blue-dart",  # Optional, auto-detected if not provided
  "tracking_link": "https://track.aftership.com/blue-dart/BD123456789"
}
```

### Tracking Statuses

AfterShip provides detailed status updates:

| Status | Description | Actions |
|--------|-------------|---------|
| **InfoReceived** | Carrier has the info but hasn't picked up yet | Wait for pickup |
| **InTransit** | Package is moving through the network | Monitor progress |
| **OutForDelivery** | Package is out for delivery today | Notify customer |
| **AttemptFail** | Delivery attempt failed | Contact customer |
| **Delivered** | Successfully delivered | Close shipment |
| **Exception** | Delivery issue (delay, damage, etc.) | Take action |
| **Expired** | Tracking info no longer available | Manual follow-up |

### Viewing Tracking Details

**Dashboard Widget:**
```
Dashboard → Shipment Tracking
- Active Shipments: 15
- Out for Delivery Today: 3
- Delivered Today: 8
- Delayed: 2 (requires attention)
```

**Individual Tracking:**
```
Purchase Order → Tracking Tab
Shows:
- Current Status: In Transit
- Last Update: 2 hours ago
- Location: Mumbai Distribution Center
- Expected Delivery: Dec 20, 2024
- Transit Time: 2 days
- Checkpoints: 5 scan events
- Map View: Visual representation of journey
```

**Checkpoint History:**
```
Checkpoint 1: Dec 18, 10:00 AM
  Status: Picked up
  Location: Delhi Warehouse
  
Checkpoint 2: Dec 18, 3:00 PM
  Status: Arrived at sorting facility
  Location: Delhi Hub
  
Checkpoint 3: Dec 19, 8:00 AM
  Status: In transit
  Location: Panipat Transit Point
  
Checkpoint 4: Dec 19, 6:00 PM
  Status: Arrived at destination city
  Location: Mumbai Hub
  
Checkpoint 5: Dec 20, 9:00 AM
  Status: Out for delivery
  Location: Mumbai - Andheri
```

---

## Webhook Support

Webhooks allow AfterShip to push real-time updates to your system automatically.

### Setting Up Webhooks

**Step 1: Configure Webhook URL**
```
AfterShip Dashboard → Settings → Notifications → Webhooks
- Webhook URL: https://yourdomain.com/api/v1/webhooks/aftership
- Events: Select all relevant events
- Secret: Generate and save (used to verify webhook authenticity)
```

**Step 2: Enable in FastAPI**
```
Settings → Integrations → AfterShip → Webhook Settings
- Webhook Secret: Enter secret from AfterShip
- Enable Webhook: Toggle ON
- Test Webhook: Send test event
```

### Webhook Events

**Supported Events:**
- `tracking.created`: New tracking created
- `tracking.updated`: Tracking status changed
- `tracking.delivered`: Package delivered
- `tracking.exception`: Delivery issue detected
- `tracking.expired`: Tracking no longer available

**Webhook Payload Example:**
```json
{
  "event": "tracking.updated",
  "msg": {
    "id": "5b7658cec7c33c0e007de3c5",
    "tracking_number": "BD123456789",
    "slug": "blue-dart",
    "tag": "InTransit",
    "subtag": "InTransit_001",
    "title": "Package is in transit",
    "location": "Mumbai Hub",
    "last_updated_at": "2024-12-19T10:30:00Z",
    "expected_delivery": "2024-12-20T18:00:00Z",
    "checkpoints": [
      {
        "slug": "blue-dart",
        "city": "Mumbai",
        "location": "Mumbai Hub",
        "country_name": "India",
        "message": "Package arrived at destination city",
        "tag": "InTransit",
        "checkpoint_time": "2024-12-19T10:30:00Z",
        "coordinates": []
      }
    ]
  }
}
```

### Webhook Processing

**System Actions on Webhook Receipt:**

1. **Verify Webhook Signature**
   - Validate secret to ensure it's from AfterShip
   - Reject if signature doesn't match

2. **Update Purchase Order**
   - Find PO by tracking number
   - Update tracking status
   - Add checkpoint to history
   - Update expected delivery date

3. **Send Notifications**
   - Email to vendor on status change
   - Email to receiving department
   - WhatsApp notification if enabled
   - Push notification to mobile app

4. **Trigger Workflows**
   - If "Out for Delivery": Alert receiving team
   - If "Delivered": Create GRN reminder
   - If "Exception": Create alert ticket
   - If "AttemptFail": Notify vendor to contact carrier

### Webhook Security

**Verifying Webhook Authenticity:**

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify AfterShip webhook signature"""
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)
```

**Best Practices:**
- Always verify webhook signatures
- Use HTTPS for webhook URL
- Log all webhook events
- Implement retry logic for failed processing
- Set up monitoring and alerts

---

## Bulk Tracking

### Bulk Add Tracking

**CSV Upload:**
```
Navigate to: Purchase Orders → Bulk Operations → Import Tracking

CSV Format:
po_number,tracking_number,courier_name
PO/2526/00001,BD123456789,Blue Dart
PO/2526/00002,FDX987654321,FedEx
PO/2526/00003,IP567890123,India Post

Upload CSV:
✓ System validates all entries
✓ Creates trackings in AfterShip
✓ Links to purchase orders
✓ Sends confirmation email
✓ Shows summary report
```

**API Bulk Create:**
```python
POST /api/v1/aftership/trackings/bulk
{
  "trackings": [
    {
      "tracking_number": "BD123456789",
      "slug": "blue-dart",
      "title": "PO/2526/00001",
      "reference_number": "PO/2526/00001"
    },
    {
      "tracking_number": "FDX987654321",
      "slug": "fedex",
      "title": "PO/2526/00002",
      "reference_number": "PO/2526/00002"
    }
  ]
}
```

### Bulk Status Check

**Check Multiple Trackings:**
```
Navigate to: Reports → Shipment Tracking → Bulk Status

Options:
- Date Range: Last 7 days
- Status Filter: All / In Transit / Delivered / Exception
- Carrier Filter: All / Specific courier
- Export: CSV / Excel / PDF

Report Shows:
- PO Number
- Tracking Number
- Courier
- Current Status
- Current Location
- Expected Delivery
- Days in Transit
- Alert Status
```

### Bulk Operations via API

**Get Multiple Trackings:**
```python
GET /api/v1/aftership/trackings?reference_numbers=PO/2526/00001,PO/2526/00002

Response:
{
  "count": 2,
  "trackings": [
    {
      "tracking_number": "BD123456789",
      "status": "InTransit",
      "location": "Mumbai Hub",
      "expected_delivery": "2024-12-20"
    },
    {
      "tracking_number": "FDX987654321",
      "status": "Delivered",
      "delivered_at": "2024-12-19T14:30:00Z"
    }
  ]
}
```

---

## Advanced Filters

### Filter by Status

```
Purchase Orders → Tracking Dashboard → Filters

Status Filters:
☐ Info Received
☐ In Transit
☐ Out for Delivery
☐ Delivered
☐ Exception
☐ Attempt Failed
☐ Expired

Apply filter to see matching shipments
```

### Filter by Delivery Timeframe

```
Filters:
- Expected Delivery: Today / Tomorrow / This Week / Custom Range
- Overdue: Show only shipments past expected delivery
- Transit Time: < 3 days / 3-7 days / > 7 days
```

### Filter by Carrier

```
Carrier Filters:
- Blue Dart
- FedEx
- DHL
- India Post
- DTDC
- Custom (all others)

Useful for:
- Carrier performance analysis
- Identifying problematic carriers
- Route optimization
```

### Filter by Exception Type

```
Exception Filters:
- Delivery Delay
- Address Issue
- Customer Not Available
- Damaged Package
- Lost Package
- Weather Delay
- Custom Clearance Delay
```

### Saved Filters

```
Save commonly used filters:
Name: "Urgent Deliveries Due Today"
Criteria: Status=OutForDelivery AND ExpectedDelivery=Today AND Priority=High

Save and access from Quick Filters menu
```

### API Filtering

```python
GET /api/v1/aftership/trackings?filters={
  "status": ["InTransit", "OutForDelivery"],
  "expected_delivery": {
    "start": "2024-12-20",
    "end": "2024-12-22"
  },
  "couriers": ["blue-dart", "fedex"],
  "has_exception": true
}
```

---

## Email Notifications

### Automatic Email Triggers

**Customer Notifications:**

1. **Shipment Dispatched**
   ```
   To: Customer email
   Subject: Your order has been shipped - Tracking #BD123456789
   
   Content:
   - Order details
   - Tracking number and link
   - Expected delivery date
   - Carrier information
   ```

2. **Out for Delivery**
   ```
   To: Customer email
   Subject: Your order is out for delivery today
   
   Content:
   - Delivery address
   - Expected time window
   - Carrier contact
   - Special instructions
   ```

3. **Delivered**
   ```
   To: Customer email
   Subject: Your order has been delivered
   
   Content:
   - Delivery confirmation
   - Delivered time
   - Received by (if available)
   - Feedback request
   ```

4. **Delivery Exception**
   ```
   To: Customer email
   Subject: Update on your shipment - Action required
   
   Content:
   - Issue description
   - What to do next
   - Contact information
   - Alternative delivery options
   ```

**Internal Notifications:**

1. **Receiving Team**
   - Notified when shipment is out for delivery
   - Reminder to prepare receiving area
   - Alert on delivery exceptions

2. **Purchasing Team**
   - Summary of all incoming shipments
   - Delayed shipments requiring follow-up
   - Delivered shipments pending GRN

3. **Management**
   - Daily summary of shipment status
   - Exception report
   - Carrier performance metrics

### Customizing Email Templates

```
Navigate to: Settings → Email Templates → Shipment Notifications

Available Templates:
- Shipment Dispatched
- Out for Delivery
- Delivered
- Delivery Exception
- Delivery Attempt Failed

Customize:
- Subject line
- Email body (HTML supported)
- Variables: {tracking_number}, {expected_delivery}, {customer_name}, etc.
- Attachments: POD (Proof of Delivery)
```

### Email Frequency Settings

```
Settings → Notifications → Shipment Tracking

Notification Preferences:
- Immediate: Send email on every status change
- Daily Digest: Once per day summary
- Critical Only: Only for exceptions and delivery
- Custom: Select specific events

Quiet Hours:
- Don't send emails between 10 PM - 8 AM
- Weekend notifications: Yes / No
```

---

## BOM Versioning

### Version Control for BOMs

**Why BOM Versioning?**
- Track changes to Bill of Materials over time
- Link production runs to specific BOM versions
- Audit trail for engineering changes
- Rollback to previous versions if needed

### Creating BOM Versions

**Version Naming Convention:**
```
BOM for Product: Laptop Computer
- Version 1.0: Initial version (Dec 2023)
- Version 1.1: Changed supplier for LCD screen (Feb 2024)
- Version 1.2: Added SSD, removed HDD (Jun 2024)
- Version 2.0: Major redesign (Dec 2024)
```

**Creating a New Version:**
```
Navigate to: Manufacturing → BOM → Select BOM → Create Version

Options:
1. Minor Version (x.Y): Small changes, compatible
2. Major Version (X.0): Significant changes, not backward compatible

Enter Changes:
- Change Description: "Switched to faster processor"
- Reason: "Performance improvement"
- Effective Date: When this version becomes active
- Auto-activate: Yes / No

System Actions:
✓ Creates new BOM version
✓ Copies all items from previous version
✓ Links to parent BOM
✓ Maintains history
✓ Notifies stakeholders
```

### Linking Manufacturing Orders to BOM Versions

```
Manufacturing Order Creation:
- Select Product
- System shows available BOM versions
- Default: Latest active version
- Option to select specific version

MO Details show:
- BOM Version Used: v1.2
- Effective Date: Jun 2024
- Items: All materials from that specific version
```

### BOM Change Impact Analysis

```
BOM Details → Impact Analysis

Shows:
- Active Manufacturing Orders using this BOM
- Stock requirements change (new vs. old version)
- Cost impact (new vs. old version)
- Lead time impact
- Vendor changes

Useful before activating new version!
```

### BOM Version History

```
BOM → Version History Tab

Table shows:
Version | Created By | Created Date | Status | Changes
v1.0    | John       | Dec 1, 2023  | Inactive | Initial
v1.1    | Sarah      | Feb 5, 2024  | Inactive | LCD supplier change
v1.2    | Mike       | Jun 10, 2024 | Active   | SSD added
v2.0    | John       | Dec 15, 2024 | Draft    | Major redesign

Click any version to:
- View details
- Compare with another version
- Restore (make active)
- Export
```

### BOM Comparison

```
Compare Versions: v1.1 vs v1.2

Changes:
➕ Added Items:
   - 256GB SSD (Qty: 1)
   
➖ Removed Items:
   - 1TB HDD (Qty: 1)
   
✏️ Modified Items:
   - RAM: Changed from 8GB to 16GB
   - Processor: Upgraded from i5 to i7

Cost Impact: +₹5,000 per unit
Lead Time Impact: -2 days (SSD faster to procure than HDD)
```

---

## API Reference

### Create Tracking

```python
POST /api/v1/aftership/trackings
{
  "tracking_number": "BD123456789",
  "slug": "blue-dart",  # Optional, auto-detected
  "title": "Purchase Order PO/2526/00001",
  "order_id": "PO/2526/00001",
  "customer_name": "Acme Corp",
  "destination_country": "IN"
}

Response:
{
  "tracking": {
    "id": "5b7658cec7c33c0e007de3c5",
    "tracking_number": "BD123456789",
    "slug": "blue-dart",
    "active": true,
    "tag": "Pending",
    "tracking_link": "https://track.aftership.com/blue-dart/BD123456789"
  }
}
```

### Get Tracking

```python
GET /api/v1/aftership/trackings/{slug}/{tracking_number}

Response:
{
  "tracking": {
    "id": "5b7658cec7c33c0e007de3c5",
    "tracking_number": "BD123456789",
    "slug": "blue-dart",
    "tag": "InTransit",
    "subtag": "InTransit_001",
    "expected_delivery": "2024-12-20",
    "origin_country": "IN",
    "destination_country": "IN",
    "checkpoints": [...],
    "location": "Mumbai Hub"
  }
}
```

### Update Tracking

```python
PUT /api/v1/aftership/trackings/{slug}/{tracking_number}
{
  "title": "Updated title",
  "customer_name": "New customer name"
}
```

### Delete Tracking

```python
DELETE /api/v1/aftership/trackings/{slug}/{tracking_number}
```

### Get Couriers

```python
GET /api/v1/aftership/couriers

Response:
{
  "couriers": [
    {
      "slug": "blue-dart",
      "name": "Blue Dart",
      "phone": "+91-1860-233-1234",
      "website": "https://www.bluedart.com"
    },
    {
      "slug": "dhl",
      "name": "DHL Express",
      "phone": "+91-124-3456000",
      "website": "https://www.dhl.com"
    }
  ]
}
```

### Detect Courier

```python
POST /api/v1/aftership/couriers/detect
{
  "tracking_number": "BD123456789"
}

Response:
{
  "couriers": [
    {
      "slug": "blue-dart",
      "name": "Blue Dart"
    }
  ]
}
```

---

## Best Practices

### 1. Tracking Number Management

✅ **Always validate** tracking numbers before adding  
✅ **Auto-detect courier** when possible  
✅ **Use reference numbers** to link trackings to POs  
✅ **Unique tracking per shipment** - don't reuse  
✅ **Archive old trackings** after 90 days  

### 2. Webhook Reliability

✅ **Verify signatures** on all webhooks  
✅ **Idempotent processing** - handle duplicate webhooks  
✅ **Retry logic** for failed webhook processing  
✅ **Monitor webhook failures** - set up alerts  
✅ **Log all webhooks** for debugging  

### 3. Customer Communication

✅ **Proactive notifications** - don't wait for customers to ask  
✅ **Clear, simple language** in emails  
✅ **Multiple channels** - email, SMS, WhatsApp  
✅ **Self-service tracking** - provide tracking links  
✅ **Set expectations** - communicate delays promptly  

### 4. Exception Handling

✅ **Immediate action** on delivery exceptions  
✅ **Escalation workflow** for unresolved issues  
✅ **Customer communication** on all exceptions  
✅ **Root cause analysis** for recurring issues  
✅ **Carrier performance** tracking and accountability  

### 5. Data Management

✅ **Regular cleanup** of expired trackings  
✅ **Archive historical data** for compliance  
✅ **Performance monitoring** - tracking API response times  
✅ **Cost tracking** - monitor AfterShip usage vs. plan limits  
✅ **Backup** tracking data regularly  

---

## Troubleshooting

### Issue 1: Tracking not updating

**Problem:** Tracking stuck in "Pending" or "InfoReceived" status

**Solutions:**
1. Check if carrier has actually picked up the package
2. Verify tracking number is correct
3. Ensure courier slug is correctly detected
4. Check AfterShip account limits (free tier has restrictions)
5. Try manual refresh via AfterShip dashboard

### Issue 2: Webhook not receiving updates

**Problem:** System not getting webhook notifications

**Solutions:**
1. Verify webhook URL is accessible from internet
2. Check webhook secret is correctly configured
3. Ensure HTTPS is enabled (AfterShip requires HTTPS)
4. Check firewall rules
5. Review webhook logs in AfterShip dashboard

### Issue 3: Incorrect courier detection

**Problem:** System selects wrong courier

**Solutions:**
1. Manually specify courier slug when creating tracking
2. Update courier detection rules
3. Contact AfterShip support to add tracking number pattern
4. Use carrier-specific tracking links instead of auto-detect

### Issue 4: API rate limits exceeded

**Problem:** AfterShip API returns 429 (Too Many Requests)

**Solutions:**
1. Implement exponential backoff
2. Cache tracking data to reduce API calls
3. Upgrade AfterShip plan for higher limits
4. Batch requests when possible
5. Use webhooks instead of polling

### Issue 5: Missing expected delivery date

**Problem:** AfterShip not providing estimated delivery

**Solutions:**
1. This is carrier-dependent, not all carriers provide ETAs
2. Use average transit times as fallback
3. Configure business rules for ETA calculation
4. Contact carrier for delivery commitments

---

## Support

For AfterShip-related issues:
1. Check AfterShip status page: https://status.aftership.com
2. Review AfterShip API documentation: https://docs.aftership.com
3. Contact AfterShip support: support@aftership.com
4. Check your AfterShip dashboard for account-specific issues

For integration issues with FastAPI v1.6:
1. Check system logs
2. Review webhook event logs
3. Test API connectivity
4. Contact system administrator

---

**Last Updated:** 2024-12-19  
**Version:** 1.0  
**Author:** FastAPI v1.6 Team
