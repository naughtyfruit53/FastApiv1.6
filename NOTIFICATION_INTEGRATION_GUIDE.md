# Notification System Integration Guide

## Service CRM Notification & Alerts Vertical Slice

This guide explains how to integrate the notification system with existing Service CRM modules.

## 🎯 Overview

The notification system provides:
- **Multi-channel notifications** (Email, SMS, Push, In-App)
- **User preference management** (Granular opt-in/out controls)
- **Automated workflow triggers** (Job assignment, SLA breach, completion, etc.)
- **Real-time updates** (WebSocket/polling support)
- **Template management** (Customizable notification templates)

## 🔧 Backend Integration

### 1. Import Notification Workflow

```python
from app.services.notification_service import NotificationService
from frontend.src.services.notificationWorkflow import NotificationWorkflow

# Initialize service
notification_service = NotificationService()
```

### 2. Trigger Notifications from Modules

#### Job Management Integration

```python
# In your job assignment logic
from frontend.src.services.notificationWorkflow import NotificationWorkflow

async def assign_job_to_technician(job_id: int, technician_id: int, customer_id: int):
    # Your existing job assignment logic
    # ...
    
    # Trigger notification
    await NotificationWorkflow.triggerJobAssignment({
        "job_id": job_id,
        "job_title": job.title,
        "customer_id": customer_id,
        "customer_name": customer.name,
        "technician_id": technician_id,
        "technician_name": technician.name,
        "due_date": job.due_date.isoformat(),
        "priority": job.priority,
        "service_type": job.service_type
    })
```

#### SLA Management Integration

```python
# In your SLA monitoring logic
async def check_sla_breach(job_id: int, sla_id: int):
    # Your SLA checking logic
    # ...
    
    if sla_at_risk:
        await NotificationWorkflow.triggerSLABreach({
            "sla_id": sla_id,
            "job_id": job_id,
            "customer_id": job.customer_id,
            "breach_type": "warning",  # or "critical", "overdue"
            "time_remaining": time_remaining_minutes,
            "expected_completion": expected_completion.isoformat()
        })
```

#### Feedback System Integration

```python
# In your feedback request logic
async def request_feedback(job_id: int, customer_id: int):
    # Your feedback request logic
    # ...
    
    await NotificationWorkflow.triggerFeedbackRequest({
        "feedback_id": feedback.id,
        "job_id": job_id,
        "customer_id": customer_id,
        "customer_name": customer.name,
        "technician_id": job.technician_id
    })
```

### 3. API Endpoints Usage

```python
# Send custom notification
POST /api/v1/notifications/send
{
    "template_id": 1,
    "recipient_type": "user",
    "recipient_id": 123,
    "channel": "email",
    "variables": {
        "customer_name": "John Doe",
        "job_id": "12345"
    }
}

# Trigger automated notifications
POST /api/v1/notifications/trigger
{
    "trigger_event": "job_assignment",
    "context_data": {
        "job_id": 12345,
        "customer_id": 1,
        "technician_id": 5
    }
}

# Manage user preferences
GET /api/v1/notifications/preferences/user/123
POST /api/v1/notifications/preferences
{
    "subject_type": "user",
    "subject_id": 123,
    "notification_type": "job_assignment",
    "channel": "email",
    "is_enabled": true
}
```

## 🎨 Frontend Integration

### 1. Add Notification Bell to Layout

```tsx
import NotificationBell from '../components/NotificationBell';
import NotificationSettingsModal from '../components/NotificationSettingsModal';

function AppLayout() {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <AppBar position="static">
      <Toolbar>
        {/* Other toolbar items */}
        <NotificationBell onSettingsClick={() => setSettingsOpen(true)} />
      </Toolbar>
      
      <NotificationSettingsModal
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        userId={currentUser.id}
        userType="user"
      />
    </AppBar>
  );
}
```

### 2. Add Alerts Feed to Dashboard

```tsx
import AlertsFeed from '../components/AlertsFeed';

function Dashboard() {
  return (
    <Grid container spacing={3}>
      {/* Other dashboard items */}
      <Grid item xs={12} lg={8}>
        <AlertsFeed 
          showFilters={true}
          maxHeight={600}
          autoRefresh={true}
          refreshInterval={30000}
        />
      </Grid>
    </Grid>
  );
}
```

### 3. Use Notification Workflow in Components

```tsx
import { useNotificationWorkflow } from '../services/notificationWorkflow';

function JobManagement() {
  const { triggerJobAssignment, triggerJobUpdate } = useNotificationWorkflow();

  const handleJobAssignment = async (jobData) => {
    // Your job assignment logic
    // ...
    
    // Trigger notification
    await triggerJobAssignment({
      job_id: job.id,
      job_title: job.title,
      customer_id: job.customer_id,
      customer_name: job.customer.name,
      technician_id: selectedTechnician.id,
      technician_name: selectedTechnician.name,
      due_date: job.due_date,
      priority: job.priority
    });
  };

  // Component JSX...
}
```

## 📱 Real-Time Updates

### Polling Implementation (Current)

```tsx
const { data: notifications } = useQuery({
  queryKey: notificationQueryKeys.logsFiltered({ limit: 20 }),
  queryFn: () => getNotificationLogs({ limit: 20 }),
  refetchInterval: 30000, // Poll every 30 seconds
});
```

### WebSocket Implementation (Future)

```typescript
// Future WebSocket implementation
class NotificationWebSocket {
  private ws: WebSocket;
  
  connect(userId: number) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/notifications/${userId}`);
    
    this.ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      // Update notification state
      queryClient.setQueryData(
        notificationQueryKeys.logs(),
        (oldData) => [notification, ...oldData]
      );
    };
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Backend (.env)
EMAIL_MOCK_MODE=true              # Enable email mocking for development
SMS_MOCK_MODE=true                # Enable SMS mocking for development  
PUSH_MOCK_MODE=true               # Enable push notification mocking
IN_APP_MOCK_MODE=true             # Enable in-app notification mocking

# Production settings
EMAIL_MOCK_MODE=false
SMS_PROVIDER=twilio               # or aws_sns
PUSH_PROVIDER=firebase            # or onesignal
```

### Frontend Configuration

```typescript
// src/config/notifications.ts
export const notificationConfig = {
  autoRefreshInterval: 30000,     // 30 seconds
  maxNotificationsInBell: 20,
  defaultPreferences: {
    job_assignment: { email: true, sms: false, push: true, in_app: true },
    sla_breach: { email: true, sms: true, push: true, in_app: true },
    marketing: { email: false, sms: false, push: false, in_app: false }
  }
};
```

## 📋 Module Integration Checklist

### For Each Module Integration:

- [ ] **Identify trigger points** (where notifications should be sent)
- [ ] **Import NotificationWorkflow** utility
- [ ] **Add trigger calls** to appropriate functions
- [ ] **Test notification delivery** in development
- [ ] **Configure user preferences** for new notification types
- [ ] **Update notification templates** if needed
- [ ] **Add integration tests**

### Example: Dispatch Module Integration

```python
# In app/services/dispatch_service.py
from frontend.src.services.notificationWorkflow import NotificationWorkflow

class DispatchService:
    async def assign_technician_to_job(self, job_id: int, technician_id: int):
        # Existing dispatch logic
        dispatch = self.create_dispatch_record(job_id, technician_id)
        
        # NEW: Trigger notification
        await NotificationWorkflow.triggerDispatchUpdate({
            "dispatch_id": dispatch.id,
            "technician_id": technician_id,
            "job_id": job_id,
            "status": "assigned",
            "eta": dispatch.estimated_arrival
        })
        
        return dispatch
```

## 🧪 Testing

### Backend Tests

```python
def test_notification_trigger():
    # Test notification service
    service = NotificationService()
    
    # Test variable substitution
    result = service.substitute_variables(
        "Hello {name}", {"name": "World"}
    )
    assert result == "Hello World"
    
    # Test user preferences
    assert service.check_user_preference(
        db, org_id, "user", 1, "job_assignment", "email"
    ) == True
```

### Frontend Tests

```typescript
import { render, screen } from '@testing-library/react';
import NotificationBell from '../NotificationBell';

test('renders notification bell with badge', () => {
  render(<NotificationBell />);
  
  const bellIcon = screen.getByLabelText('notifications');
  expect(bellIcon).toBeInTheDocument();
});
```

## 🚀 Deployment Notes

1. **Database Migration**: Ensure notification tables are created
2. **Environment Variables**: Configure mock modes appropriately
3. **Email/SMS Services**: Set up real providers for production
4. **Monitoring**: Add logging for notification delivery
5. **Performance**: Consider notification queue for high volume

## 📞 Support

For integration questions or issues:
1. Check the notification service logs
2. Verify user preferences are configured
3. Test with mock mode enabled
4. Review template variables and content

The notification system is designed to be flexible and easily integrated with existing Service CRM modules while providing a consistent user experience across all channels.