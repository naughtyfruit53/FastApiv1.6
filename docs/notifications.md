# Notification/Engagement Module Documentation

The Notification/Engagement Module provides a comprehensive system for managing multi-channel notifications in the Service CRM platform. This module supports email, SMS, push, and in-app notifications with template management, automated triggers, and detailed delivery tracking.

## Features

### 📧 Multi-Channel Support
- **Email**: Rich HTML emails with template support
- **SMS**: Text messages for quick alerts
- **Push Notifications**: Mobile and web push notifications
- **In-App**: Internal application notifications

### 🎨 Template Management
- Create reusable notification templates
- Variable substitution for dynamic content
- Template versioning and activation control
- Channel-specific template optimization

### 🚀 Automated Triggers
- Event-based notification triggers
- Customer interaction notifications
- Service completion alerts
- Appointment reminders

### 📊 Analytics & Tracking
- Delivery status tracking
- Open and click tracking for emails
- Comprehensive notification logs
- Performance analytics dashboard

### 🎯 Targeting & Segmentation
- Send to individual customers or users
- Bulk notifications to customer segments
- Integration with existing customer analytics

## API Endpoints

### Template Management

#### Get Templates
```http
GET /api/v1/notifications/templates?channel=email&template_type=appointment_reminder
```

#### Create Template
```http
POST /api/v1/notifications/templates
Content-Type: application/json

{
  "name": "Appointment Reminder",
  "template_type": "appointment_reminder", 
  "channel": "email",
  "subject": "Your appointment with {service_provider}",
  "body": "Hello {customer_name}, this is a reminder that you have an appointment scheduled for {appointment_date} with {service_provider}.",
  "variables": ["customer_name", "appointment_date", "service_provider"],
  "is_active": true
}
```

#### Update Template
```http
PUT /api/v1/notifications/templates/{template_id}
Content-Type: application/json

{
  "subject": "Updated appointment reminder for {customer_name}",
  "is_active": false
}
```

### Sending Notifications

#### Send Single Notification
```http
POST /api/v1/notifications/send
Content-Type: application/json

{
  "template_id": 1,
  "recipient_type": "customer",
  "recipient_id": 123,
  "channel": "email",
  "variables": {
    "customer_name": "John Doe",
    "appointment_date": "2024-01-15 10:00 AM",
    "service_provider": "ACME Repairs"
  }
}
```

#### Send Bulk Notification
```http
POST /api/v1/notifications/send-bulk
Content-Type: application/json

{
  "template_id": 2,
  "channel": "email",
  "recipient_type": "segment",
  "segment_name": "vip_customers",
  "variables": {
    "promotion_code": "VIP2024",
    "discount_percentage": "20"
  }
}
```

### Notification Logs

#### Get Logs
```http
GET /api/v1/notifications/logs?status=sent&channel=email&limit=50
```

#### Get Analytics
```http
GET /api/v1/notifications/analytics/summary?days=30
```

## Frontend Components

### NotificationDashboard
Main dashboard component providing tabbed interface for all notification features.

```tsx
import NotificationDashboard from '../components/NotificationDashboard';

function App() {
  return <NotificationDashboard />;
}
```

### NotificationTemplates
Template management interface with CRUD operations.

```tsx
import NotificationTemplates from '../components/NotificationTemplates';
```

### SendNotification
Interface for sending single and bulk notifications.

```tsx
import SendNotification from '../components/SendNotification';
```

### NotificationLogs
Logs viewer with filtering and analytics.

```tsx
import NotificationLogs from '../components/NotificationLogs';
```

## Usage Examples

### 1. Basic Email Template

```json
{
  "name": "Welcome Email",
  "template_type": "marketing",
  "channel": "email",
  "subject": "Welcome to {company_name}!",
  "body": "Dear {customer_name},\n\nWelcome to {company_name}! We're excited to serve you.\n\nBest regards,\nThe {company_name} Team",
  "html_body": "<h1>Welcome to {company_name}!</h1><p>Dear {customer_name},</p><p>Welcome to {company_name}! We're excited to serve you.</p><p>Best regards,<br>The {company_name} Team</p>",
  "variables": ["customer_name", "company_name"]
}
```

### 2. SMS Appointment Reminder

```json
{
  "name": "SMS Appointment Reminder",
  "template_type": "appointment_reminder",
  "channel": "sms",
  "body": "Hi {customer_name}! Reminder: You have an appointment tomorrow at {appointment_time}. Reply STOP to opt out.",
  "variables": ["customer_name", "appointment_time"]
}
```

### 3. Automated Trigger Configuration

```json
{
  "name": "Service Completion Follow-up",
  "template_type": "follow_up",
  "channel": "email",
  "trigger_event": "service_completion",
  "trigger_conditions": {
    "service_type": "repair",
    "delay_hours": 24
  },
  "subject": "How was your {service_type} experience?",
  "body": "Hi {customer_name},\n\nWe hope you're satisfied with your recent {service_type} service. Please let us know how we did!\n\nRate your experience: {feedback_link}",
  "variables": ["customer_name", "service_type", "feedback_link"]
}
```

### 4. Customer Segment Notification

```javascript
// Send marketing email to VIP customers
const bulkRequest = {
  template_id: 5,
  channel: "email",
  recipient_type: "segment",
  segment_name: "vip",
  variables: {
    promotion_title: "Exclusive VIP Offer",
    discount_code: "VIP50",
    expiry_date: "2024-02-28"
  }
};

await sendBulkNotification(bulkRequest);
```

## Service Integration

### Automated Notifications

The system can automatically trigger notifications based on various events:

```python
# In your service code
from app.services.notification_service import NotificationService

notification_service = NotificationService()

# Trigger after customer interaction
notification_service.trigger_automated_notifications(
    db=db,
    trigger_event="customer_interaction",
    organization_id=org_id,
    context_data={
        "customer_id": customer.id,
        "interaction_type": "service_request",
        "service_type": "AC Repair"
    }
)
```

### Customer Engagement Workflows

```python
# Example: Low engagement re-engagement campaign
def trigger_engagement_campaign(db: Session, organization_id: int):
    # Find customers with low engagement scores
    low_engagement_customers = get_low_engagement_customers(db, organization_id)
    
    for customer in low_engagement_customers:
        notification_service.trigger_automated_notifications(
            db=db,
            trigger_event="low_engagement",
            organization_id=organization_id,
            context_data={
                "customer_id": customer.id,
                "customer_name": customer.name,
                "last_interaction": customer.last_interaction_date,
                "special_offer": "20% off next service"
            }
        )
```

## Configuration

### Environment Variables

```bash
# Email service configuration
BREVO_API_KEY=your_brevo_api_key
BREVO_FROM_EMAIL=noreply@yourcompany.com
BREVO_FROM_NAME="Your Company"

# SMS service configuration (when implemented)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Push notification configuration (when implemented)
FIREBASE_SERVER_KEY=your_firebase_key
ONESIGNAL_APP_ID=your_onesignal_id
```

### Database Migration

Run the notification system migration:

```bash
alembic upgrade head
```

## Security & Privacy

### Data Protection
- All notification content is encrypted in transit
- Customer data is anonymized in logs where possible
- Opt-out mechanisms are provided for all channels
- GDPR-compliant data handling

### Access Control
- Organization-level isolation
- Role-based access control
- API authentication required
- Rate limiting on notification sending

## Best Practices

### Template Design
1. **Keep it concise**: Use clear, actionable language
2. **Personalize**: Always include customer name when available
3. **Mobile-friendly**: Ensure SMS and email work on mobile devices
4. **Test thoroughly**: Use the preview function before sending

### Automation Rules
1. **Respect frequency**: Don't overwhelm customers with notifications
2. **Time appropriately**: Send notifications at reasonable hours
3. **Segment wisely**: Target relevant customers only
4. **Monitor performance**: Track open rates and adjust accordingly

### Error Handling
1. **Retry logic**: Failed notifications are automatically retried
2. **Fallback channels**: Consider SMS fallback for critical email notifications
3. **Monitor logs**: Regularly check for delivery failures
4. **Update contact info**: Handle bounced emails and invalid phone numbers

## Troubleshooting

### Common Issues

#### Notifications Not Sending
1. Check template configuration
2. Verify recipient contact information
3. Review API credentials
4. Check notification logs for error messages

#### Low Delivery Rates
1. Review email authentication (SPF, DKIM, DMARC)
2. Check for spam content in templates
3. Verify sender reputation
4. Update bounced email addresses

#### Template Variables Not Substituting
1. Ensure variable names match exactly
2. Check that variables are provided in the request
3. Verify template syntax uses {variable_name} format

### Monitoring

Use the analytics dashboard to monitor:
- Delivery success rates
- Open and click rates
- Failed notification trends
- Channel performance comparison

## Support

For technical support or feature requests:
1. Check the logs first: `/api/v1/notifications/logs`
2. Review API documentation in Swagger UI
3. Monitor system health via analytics endpoints
4. Contact support with specific error messages and notification IDs