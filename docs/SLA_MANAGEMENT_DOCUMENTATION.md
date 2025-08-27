# SLA Management System Documentation

## Overview

The SLA (Service Level Agreement) Management system provides comprehensive tracking and management of service level commitments for customer support tickets. It automatically tracks response times, resolution times, escalations, and provides detailed analytics on SLA performance.

## Key Features

### 1. SLA Policy Management
- **Flexible Policy Definition**: Create policies with specific response and resolution time requirements
- **Multi-Criteria Matching**: Policies can be matched based on ticket priority, type, and customer tier
- **Escalation Rules**: Configurable escalation thresholds and automatic escalation triggers
- **Default Policies**: Set fallback policies for unmatched tickets

### 2. Automatic SLA Tracking
- **Real-time Monitoring**: Automatic SLA assignment when tickets are created
- **Breach Detection**: Real-time calculation of SLA breaches and remaining time
- **Status Tracking**: Track response and resolution status separately
- **Escalation Management**: Automatic escalation triggers when thresholds are reached

### 3. Performance Analytics
- **SLA Metrics**: Comprehensive metrics on SLA performance
- **Breach Analysis**: Detailed analysis of SLA breaches
- **Response Time Analytics**: Average response and resolution time tracking
- **Escalation Reporting**: Track escalated tickets and escalation levels

### 4. Role-Based Access Control
- **Admin/Manager**: Full CRUD access to SLA policies and tracking
- **Support Agents**: Read-only access to SLA information
- **Organization Scoping**: All SLA data is organization-scoped for multi-tenancy

## SLA Policy Structure

### Basic Policy Fields
```typescript
interface SLAPolicy {
  name: string;                           // Policy name (e.g., "Critical Support")
  description?: string;                   // Optional description
  response_time_hours: number;            // Time to first response (hours)
  resolution_time_hours: number;         // Time to resolution (hours)
  escalation_enabled: boolean;           // Whether escalation is enabled
  escalation_threshold_percent: number;  // Escalation trigger percentage (default: 80%)
  is_active: boolean;                    // Whether policy is active
  is_default: boolean;                   // Whether this is the default policy
}
```

### Matching Criteria
Policies can be configured to match specific ticket characteristics:
- **priority**: 'low', 'medium', 'high', 'urgent' (null = all priorities)
- **ticket_type**: 'support', 'maintenance', 'installation', etc. (null = all types)
- **customer_tier**: 'premium', 'standard', etc. (null = all tiers)

### Policy Matching Logic
1. **Exact Match**: Find policies that exactly match ticket priority, type, and customer tier
2. **Partial Match**: Find policies that match some criteria (more specific matches preferred)
3. **Default Policy**: Use the default policy if no specific matches found
4. **Fallback**: If no default policy exists, SLA tracking is not created

## SLA Tracking Process

### 1. Automatic Assignment
When a ticket is created:
1. System finds the best matching SLA policy
2. Calculates response and resolution deadlines
3. Creates SLA tracking record
4. Starts monitoring SLA status

### 2. Response Tracking
- **First Response Time**: Tracked when first response is made to customer
- **Response Status**: 'pending', 'met', or 'breached'
- **Breach Calculation**: Hours over/under the response deadline

### 3. Resolution Tracking
- **Resolution Time**: Tracked when ticket is marked as resolved
- **Resolution Status**: 'pending', 'met', or 'breached'  
- **Breach Calculation**: Hours over/under the resolution deadline

### 4. Escalation Process
- **Threshold Monitoring**: Continuously check if escalation threshold is reached
- **Automatic Escalation**: Trigger escalation when threshold percentage is reached
- **Escalation Levels**: Track escalation level (1, 2, 3, etc.)
- **Escalation Timestamps**: Record when escalations occur

## API Endpoints

### SLA Policy Management
```
GET    /api/v1/sla/organizations/{org_id}/policies
POST   /api/v1/sla/organizations/{org_id}/policies
GET    /api/v1/sla/organizations/{org_id}/policies/{policy_id}
PUT    /api/v1/sla/organizations/{org_id}/policies/{policy_id}
DELETE /api/v1/sla/organizations/{org_id}/policies/{policy_id}
```

### SLA Tracking
```
POST   /api/v1/sla/organizations/{org_id}/tickets/{ticket_id}/sla
GET    /api/v1/sla/organizations/{org_id}/tickets/{ticket_id}/sla
PUT    /api/v1/sla/organizations/{org_id}/tracking/{tracking_id}
```

### SLA Monitoring
```
GET    /api/v1/sla/organizations/{org_id}/sla/breached
GET    /api/v1/sla/organizations/{org_id}/sla/escalation-candidates
POST   /api/v1/sla/organizations/{org_id}/tracking/{tracking_id}/escalate
```

### SLA Analytics
```
GET    /api/v1/sla/organizations/{org_id}/sla/metrics
```

### Ticket Processing
```
POST   /api/v1/sla/organizations/{org_id}/tickets/{ticket_id}/response
POST   /api/v1/sla/organizations/{org_id}/tickets/{ticket_id}/resolution
```

## Database Schema

### SLA Policies Table
```sql
CREATE TABLE sla_policies (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    priority VARCHAR,
    ticket_type VARCHAR,
    customer_tier VARCHAR,
    response_time_hours FLOAT NOT NULL,
    resolution_time_hours FLOAT NOT NULL,
    escalation_enabled BOOLEAN DEFAULT TRUE,
    escalation_threshold_percent FLOAT DEFAULT 80.0,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    created_by_id INTEGER,
    FOREIGN KEY(organization_id) REFERENCES organizations(id),
    FOREIGN KEY(created_by_id) REFERENCES users(id),
    UNIQUE(organization_id, name)
);
```

### SLA Tracking Table
```sql
CREATE TABLE sla_tracking (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL UNIQUE,
    policy_id INTEGER NOT NULL,
    response_deadline DATETIME NOT NULL,
    resolution_deadline DATETIME NOT NULL,
    first_response_at DATETIME,
    resolved_at DATETIME,
    response_status VARCHAR DEFAULT 'pending',
    resolution_status VARCHAR DEFAULT 'pending',
    escalation_triggered BOOLEAN DEFAULT FALSE,
    escalation_triggered_at DATETIME,
    escalation_level INTEGER DEFAULT 0,
    response_breach_hours FLOAT,
    resolution_breach_hours FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY(organization_id) REFERENCES organizations(id),
    FOREIGN KEY(ticket_id) REFERENCES tickets(id),
    FOREIGN KEY(policy_id) REFERENCES sla_policies(id)
);
```

## Frontend Components

### 1. SLA Management Page (`/sla`)
Main interface for managing SLA policies and viewing performance:
- **SLA Policies Tab**: CRUD operations for SLA policies
- **Performance Dashboard**: Analytics and metrics
- **Breached SLAs Tab**: View tickets with SLA breaches

### 2. SLA Status Component
Reusable component for displaying SLA status on tickets:
- **Compact View**: Chips showing response/resolution status
- **Detailed View**: Progress bars, timelines, and detailed metrics

### 3. SLA Service (`slaService.ts`)
TypeScript service for API integration:
- Policy management operations
- SLA tracking operations
- Analytics and reporting
- Error handling and validation

## Usage Examples

### Creating an SLA Policy
```typescript
const policy: SLAPolicyCreate = {
  name: "Critical Support",
  description: "Critical priority support tickets",
  priority: "urgent",
  response_time_hours: 1,
  resolution_time_hours: 4,
  escalation_enabled: true,
  escalation_threshold_percent: 80,
  is_active: true,
  is_default: false
};

const created = await slaService.createPolicy(organizationId, policy);
```

### Assigning SLA to Ticket
```typescript
// Automatic assignment (finds best matching policy)
const assignment = await slaService.assignSLAToTicket(organizationId, ticketId);

// Force reassignment
const reassignment = await slaService.assignSLAToTicket(organizationId, ticketId, true);
```

### Processing Ticket Events
```typescript
// Mark first response
await slaService.processTicketResponse(organizationId, ticketId);

// Mark resolution
await slaService.processTicketResolution(organizationId, ticketId);
```

### Getting SLA Metrics
```typescript
// Last 30 days metrics
const metrics = await slaService.getSLAMetrics(organizationId, undefined, undefined, 30);

console.log(`Response SLA: ${metrics.response_sla_percentage}%`);
console.log(`Resolution SLA: ${metrics.resolution_sla_percentage}%`);
```

## Permission Requirements

### Backend Permissions
- `sla_create`: Create SLA policies and assign to tickets
- `sla_read`: View SLA policies and tracking data
- `sla_update`: Update SLA policies and tracking
- `sla_delete`: Delete SLA policies
- `sla_escalate`: Trigger manual escalations

### Default Role Mapping
- **Service Admin**: All SLA permissions
- **Service Manager**: sla_create, sla_read, sla_update, sla_escalate
- **Support Agent**: sla_read only
- **Viewer**: sla_read only

## Best Practices

### 1. Policy Design
- **Keep it Simple**: Start with basic policies and add complexity as needed
- **Clear Naming**: Use descriptive names that indicate policy purpose
- **Default Policy**: Always have a default policy for unmatched tickets
- **Regular Review**: Review and update policies based on performance data

### 2. SLA Configuration
- **Realistic Targets**: Set achievable response and resolution times
- **Escalation Thresholds**: Use 80% threshold as starting point, adjust based on experience
- **Priority Alignment**: Ensure SLA times align with business priority levels
- **Customer Tiers**: Use customer tiers for differentiated service levels

### 3. Monitoring and Analytics
- **Regular Monitoring**: Check SLA performance daily
- **Trend Analysis**: Look for patterns in SLA breaches
- **Escalation Review**: Review escalated tickets for process improvements
- **Performance Reporting**: Regular reporting to stakeholders

### 4. Integration
- **Ticket Workflow**: Integrate SLA status into ticket management workflow
- **Notifications**: Set up alerts for SLA breaches and escalations
- **Automation**: Automate response and resolution marking where possible
- **Training**: Train support staff on SLA concepts and importance

## Troubleshooting

### Common Issues

#### SLA Not Assigned to Ticket
- Check if ticket matches any active SLA policy
- Verify default policy exists and is active
- Check ticket priority, type, and customer tier values

#### Incorrect SLA Calculation
- Verify policy response/resolution times are correct
- Check ticket creation timestamp
- Ensure timezone handling is correct

#### Escalation Not Triggering
- Verify escalation is enabled in policy
- Check escalation threshold percentage
- Ensure SLA tracking status is 'pending'

#### Performance Issues
- Check database indexes on SLA tables
- Optimize queries for large datasets
- Consider archiving old SLA tracking data

### Monitoring Queries

```sql
-- Check SLA policies
SELECT * FROM sla_policies WHERE organization_id = ? AND is_active = true;

-- Find tickets without SLA tracking
SELECT t.* FROM tickets t 
LEFT JOIN sla_tracking st ON t.id = st.ticket_id 
WHERE t.organization_id = ? AND st.id IS NULL;

-- Current SLA breaches
SELECT * FROM sla_tracking 
WHERE organization_id = ? 
AND (response_status = 'breached' OR resolution_status = 'breached');

-- Escalation candidates
SELECT st.*, sp.escalation_threshold_percent
FROM sla_tracking st
JOIN sla_policies sp ON st.policy_id = sp.id
WHERE st.organization_id = ? 
AND sp.escalation_enabled = true
AND st.escalation_triggered = false;
```

## Future Enhancements

### Planned Features
1. **Custom SLA Formulas**: Support for complex SLA calculations
2. **Business Hours**: SLA calculation based on business hours only
3. **Holiday Calendar**: Exclude holidays from SLA calculations
4. **SLA Templates**: Pre-built SLA policy templates
5. **Advanced Analytics**: Predictive SLA analytics and trends
6. **Webhook Integration**: Real-time SLA event notifications
7. **Mobile Notifications**: Push notifications for SLA events
8. **Customer Portal**: Customer-facing SLA status visibility

### Integration Opportunities
1. **Calendar Integration**: Sync with calendar systems for business hours
2. **ITSM Integration**: Integration with IT Service Management tools
3. **CRM Integration**: Enhanced customer tier management
4. **Reporting Tools**: Integration with BI and reporting platforms
5. **Communication Tools**: Integration with Slack, Teams, etc.

---

For additional support or questions about the SLA Management system, please refer to the API documentation at `/docs` or contact the development team.