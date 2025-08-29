# Integration Management System Documentation

## Overview

The Integration Management System provides a unified interface for managing all third-party integrations within the organization settings. It includes role-based access control, health monitoring, and centralized configuration management.

## Supported Integrations

### 1. Tally ERP Integration
- **Purpose**: Sync financial data, ledgers, and vouchers with Tally ERP
- **Features**: Bidirectional sync, real-time connection testing, error tracking
- **Access Level**: Super Admin configuration, with granular permission delegation

### 2. Email Integration
- **Purpose**: Send automated emails, notifications, and reports
- **Features**: SMTP/IMAP configuration, template management, delivery tracking
- **Access Level**: Super Admin configuration, all users can view status

### 3. Calendar Integration
- **Purpose**: Sync appointments, meetings, and schedules
- **Features**: Google Calendar, Outlook integration, automatic sync
- **Access Level**: Super Admin configuration, all users can view

### 4. Payment Gateway Integration
- **Purpose**: Process online payments and reconcile transactions
- **Features**: Multiple gateway support (Razorpay, Stripe, PayPal)
- **Access Level**: Super Admin only

### 5. Zoho Integration
- **Purpose**: Sync data with Zoho CRM, Books, and Inventory
- **Features**: Customer sync, invoice sync, product sync
- **Access Level**: Super Admin configuration with delegation

## Access Control and Permissions

### Permission Types
- **View**: Can see integration status and health
- **Manage**: Can configure and modify integration settings

### User Roles

#### Organization Super Admin
- Full access to all integrations
- Can grant/revoke permissions to other users
- Can configure all integration settings
- Access to security and audit features

#### Standard Users (Default)
- View-only access to email and calendar status
- No access to sensitive integrations (Tally, Payments, Zoho)
- Cannot modify any integration settings

#### Users with Granted Permissions
- Can view/manage specific integrations as granted by Super Admin
- Limited to delegated integration types
- Cannot grant permissions to others

### Permission Management

#### Grant Permission
```http
POST /api/v1/integrations/permissions/grant
Content-Type: application/json

{
  "user_id": 123,
  "integration": "tally",
  "permission_type": "manage"
}
```

#### Revoke Permission
```http
DELETE /api/v1/integrations/permissions/revoke
Content-Type: application/json

{
  "user_id": 123,
  "integration": "tally",
  "permission_type": "manage"
}
```

## Integration Configuration

### Tally ERP Configuration

#### Get Configuration
```http
GET /api/v1/integrations/tally/configuration
```

#### Create Configuration
```http
POST /api/v1/integrations/tally/configuration
Content-Type: application/json

{
  "tally_server_host": "localhost",
  "tally_server_port": 9000,
  "company_name_in_tally": "Demo Company",
  "is_enabled": true,
  "sync_frequency": "manual",
  "auto_sync_enabled": false
}
```

#### Test Connection
```http
POST /api/v1/integrations/tally/test-connection
Content-Type: application/json

{
  "host": "localhost",
  "port": 9000,
  "company_name": "Demo Company"
}
```

### Integration Health Monitoring

#### Unified Dashboard
```http
GET /api/v1/integrations/dashboard
```

**Response Structure:**
```json
{
  "tally_integration": {
    "integration_name": "Tally",
    "status": "healthy",
    "last_sync_at": "2024-08-29T10:30:00Z",
    "sync_frequency": "Manual/On-demand",
    "error_count": 0,
    "configuration_valid": true,
    "performance_metrics": {
      "last_sync_duration": "30s",
      "records_synced": 150
    }
  },
  "email_integration": {
    "integration_name": "Email",
    "status": "healthy",
    "last_sync_at": "2024-08-29T10:25:00Z",
    "sync_frequency": "Real-time",
    "error_count": 0,
    "configuration_valid": true,
    "performance_metrics": {
      "avg_response_time": "50ms"
    }
  },
  "system_health": {
    "database_status": "healthy",
    "api_response_time": "45ms",
    "last_backup": "2024-08-29T04:00:00Z",
    "storage_usage": "45%"
  }
}
```

### Integration Status Types

#### Status Levels
- **healthy**: Integration working properly
- **warning**: Minor issues, still functional
- **error**: Significant issues affecting functionality
- **disabled**: Integration turned off or not configured

#### Health Indicators
- Last sync timestamp
- Error count in last 24 hours
- Configuration validity
- Performance metrics
- Sync frequency information

## API Endpoints

### Permission Management
```http
GET    /api/v1/integrations/permissions           # Get current user permissions
POST   /api/v1/integrations/permissions/grant    # Grant permission (Super Admin)
DELETE /api/v1/integrations/permissions/revoke   # Revoke permission (Super Admin)
```

### Tally Integration
```http
GET    /api/v1/integrations/tally/configuration    # Get Tally config
POST   /api/v1/integrations/tally/configuration    # Create Tally config
PUT    /api/v1/integrations/tally/configuration    # Update Tally config
DELETE /api/v1/integrations/tally/configuration    # Delete Tally config
POST   /api/v1/integrations/tally/test-connection  # Test connection
```

### Integration Status
```http
GET /api/v1/integrations/dashboard           # Unified dashboard
GET /api/v1/integrations/email/status        # Email status
GET /api/v1/integrations/calendar/status     # Calendar status
GET /api/v1/integrations/payments/status     # Payment status
GET /api/v1/integrations/zoho/status         # Zoho status
```

## Configuration Management

### Organization Settings Integration

The integration settings are now part of the Organization Settings panel, providing:

1. **Centralized Management**: All integrations in one place
2. **Role-Based Access**: Proper permission controls
3. **Audit Trail**: Track all configuration changes
4. **Security**: Sensitive settings protected by admin access

### Configuration Security

#### Sensitive Data Protection
- API keys and passwords encrypted at rest
- Secure transmission using HTTPS/TLS
- Limited access to sensitive configuration fields
- Audit logging for all configuration changes

#### Access Control Matrix

| Integration | View (All Users) | View (Admin) | Manage (Super Admin) | Delegate Permissions |
|-------------|------------------|--------------|---------------------|---------------------|
| Email       | Status only      | Full status  | Full config         | Yes                 |
| Calendar    | Status only      | Full status  | Full config         | Yes                 |
| Tally       | No access        | Status only  | Full config         | Yes                 |
| Payments    | No access        | No access    | Full config         | No                  |
| Zoho        | No access        | Status only  | Full config         | Yes                 |

## Error Handling and Troubleshooting

### Common Integration Issues

#### Tally Integration
```
Problem: Connection timeout
Solution: Check Tally server is running and port is accessible
API: POST /api/v1/integrations/tally/test-connection
```

#### Email Integration
```
Problem: SMTP authentication failed
Solution: Verify SMTP credentials and server settings
Status: GET /api/v1/integrations/email/status
```

#### Calendar Integration
```
Problem: Sync stopped working
Solution: Re-authenticate with calendar provider
Status: GET /api/v1/integrations/calendar/status
```

### Error Response Format
```json
{
  "error": "integration_error",
  "message": "Failed to connect to Tally server",
  "details": {
    "integration": "tally",
    "error_code": "CONNECTION_TIMEOUT",
    "suggestion": "Check if Tally server is running on specified port"
  },
  "timestamp": "2024-08-29T10:30:00Z"
}
```

## Integration Workflows

### Setting Up Tally Integration

1. **Access Organization Settings**
   - Navigate to Organization Settings > Integrations
   - Locate Tally Integration section

2. **Configure Connection**
   - Enter Tally server host and port
   - Specify company name in Tally
   - Test connection to verify settings

3. **Enable Integration**
   - Set sync frequency (manual/automatic)
   - Configure sync options
   - Save configuration

4. **Monitor Health**
   - Check integration dashboard
   - Monitor sync logs
   - Address any errors promptly

### Delegating Integration Permissions

1. **Super Admin Access Required**
   - Only organization super admins can delegate permissions

2. **Select User and Integration**
   - Choose user from organization
   - Select integration type (tally, email, calendar, zoho)
   - Choose permission level (view, manage)

3. **Grant Permission**
   - Use permission grant API or UI
   - User receives immediate access
   - Audit log records the delegation

4. **Monitor and Revoke**
   - Track permission usage
   - Revoke permissions when no longer needed
   - Maintain principle of least privilege

## Performance and Monitoring

### Performance Metrics

#### Response Time Monitoring
- API endpoint response times
- Integration sync duration
- Database query performance

#### Throughput Metrics
- Records processed per sync
- API requests per minute
- Data transfer rates

#### Error Rate Tracking
- Failed sync attempts
- API error rates
- Connection failures

### Monitoring Dashboard

The integration dashboard provides real-time monitoring of:
- Integration health status
- Recent activity timeline
- Error summaries
- Performance trends

### Alerting and Notifications

#### Automatic Alerts
- Integration failures
- Performance degradation
- Configuration changes
- Security events

#### Notification Channels
- Email notifications for admins
- In-app notifications
- Dashboard status indicators

## Security Best Practices

### Access Control
1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Regular Access Review**: Periodically review and revoke unnecessary permissions
3. **Role Separation**: Separate configuration from operational access

### Data Protection
1. **Encryption**: All sensitive data encrypted at rest and in transit
2. **API Security**: Secure API endpoints with proper authentication
3. **Audit Logging**: Track all configuration changes and access

### Integration Security
1. **Secure Connections**: Use HTTPS/TLS for all external connections
2. **Credential Management**: Secure storage of API keys and passwords
3. **Regular Updates**: Keep integration components updated

## Compliance and Audit

### Audit Trail
- All integration configuration changes logged
- User access and permission changes tracked
- Data sync activities recorded
- Failed access attempts monitored

### Compliance Features
- Data retention policies
- GDPR compliance for personal data
- SOX compliance for financial integrations
- Role-based access controls

### Reporting
- Integration usage reports
- Security access reports
- Performance and availability reports
- Compliance audit reports