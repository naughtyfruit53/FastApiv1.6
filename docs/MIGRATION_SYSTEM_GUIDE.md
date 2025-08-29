# Migration & Data Import System Documentation

## Overview

The Migration & Data Import System provides a comprehensive solution for importing data from various sources into the ERP system. It supports guided migration workflows, data validation, conflict resolution, and rollback capabilities.

**🆕 Recent Enhancements:**
- **Step-by-step Migration Wizard UI**: User-friendly guided interface for data import
- **Enhanced Integration Dashboard**: Centralized monitoring of all external integrations 
- **Super Admin Access Control**: Granular permission management for integration settings
- **Real-time Job Monitoring**: Live progress tracking with error handling
- **Rollback Support**: Complete migration undo functionality
- **Post-Release Monitoring**: Comprehensive error tracking and performance monitoring
- **User Feedback System**: Built-in feedback collection and issue reporting

## Quick Start Guide

### For System Administrators
1. **Access Migration Management**: Navigate to **Settings** → **Integration Management** → **Migration & Integrations**
2. **Review System Health**: Check the dashboard for integration status and system health
3. **Configure Permissions**: Grant migration access to trusted users as needed
4. **Monitor Performance**: Use the built-in monitoring tools to track system performance

### For Users with Migration Access
1. **Start New Migration**: Click "New Migration" button in the Migration Management page
2. **Follow the Wizard**: Use the step-by-step wizard to upload files and configure mappings
3. **Validate Data**: Review validation results before executing the migration
4. **Monitor Progress**: Track real-time progress and handle any errors that arise

## Features

### Supported Data Sources
- **Tally ERP**: Direct integration with Tally for importing ledgers, vouchers, and company data
- **Zoho**: Import from Zoho CRM, Books, and Inventory
- **Excel/CSV**: Import from structured Excel or CSV files
- **JSON**: Import from JSON data files
- **Manual**: Manual data entry with validation

### Data Types Supported
- Chart of Accounts / Ledgers
- Vouchers / Transactions
- Contacts (Customers/Vendors)
- Products / Items
- Stock / Inventory
- Company Information

### Key Capabilities
- **Guided Migration Wizard**: Step-by-step workflow for easy migration
- **Automatic Field Mapping**: Smart field mapping with AI suggestions
- **Data Validation**: Comprehensive data validation before import
- **Conflict Resolution**: Handle duplicates and data conflicts intelligently
- **Progress Tracking**: Real-time progress monitoring
- **Rollback Support**: Undo migrations if needed
- **Bulk Operations**: Process multiple migration jobs simultaneously
- **Template System**: Reusable migration templates for common scenarios

## User Roles and Permissions

### Organization Super Admin
- Create and manage migration jobs
- Configure integration settings
- Grant/revoke migration permissions to other users
- Access all migration features and settings

### Migration Users (Granted Permission)
- View migration jobs they created
- Monitor migration progress
- Access migration wizard

### Standard Users
- View migration statistics (read-only)
- No access to migration configuration
- Can submit feedback and bug reports

## Security and Access Control

### Access Control Features
- **Organization Isolation**: All migration data is isolated by organization
- **Role-Based Permissions**: Fine-grained control over migration features
- **Audit Logging**: Complete tracking of all migration activities
- **Session Management**: Secure session handling for migration operations

### Permission Management
Super admins can delegate specific migration permissions:
```bash
# Grant migration view permission
POST /api/v1/integration-settings/permissions/grant
{
  "user_id": 123,
  "integration": "migration",
  "permission_type": "view"
}

# Grant migration management permission
POST /api/v1/integration-settings/permissions/grant
{
  "user_id": 123,
  "integration": "migration", 
  "permission_type": "manage"
}
```

## Migration Workflow

### 1. Create Migration Job
```
POST /api/v1/migration/jobs
```
Create a new migration job specifying:
- Job name and description
- Source type (Tally, Zoho, Excel, etc.)
- Data types to migrate
- Conflict resolution strategy

### 2. Upload Source File
```
POST /api/v1/migration/jobs/{job_id}/upload
```
Upload the source data file. The system will:
- Detect file format and structure
- Analyze data quality
- Provide preview of data
- Suggest data types present in the file

### 3. Configure Field Mappings
```
POST /api/v1/migration/jobs/{job_id}/mappings/auto
```
Map source fields to target system fields:
- Automatic mapping suggestions based on templates
- Manual field mapping configuration
- Data transformation rules
- Validation rules for each field

### 4. Validate Data
```
POST /api/v1/migration/jobs/{job_id}/validate
```
Comprehensive data validation:
- Check required fields
- Validate data types and formats
- Identify potential conflicts
- Generate validation report

### 5. Execute Migration
```
POST /api/v1/migration/jobs/{job_id}/execute
```
Start the migration process:
- Background processing for large datasets
- Real-time progress updates
- Detailed logging of all operations
- Automatic conflict handling

### 6. Monitor Progress
```
GET /api/v1/migration/jobs/{job_id}/progress
```
Track migration progress:
- Percentage completion
- Records processed/successful/failed
- Estimated completion time
- Recent log entries

### 7. Rollback Migration (New!)
```
POST /api/v1/migration/jobs/{job_id}/rollback
```
Rollback completed migration:
- Validates rollback eligibility
- Reverses all changes made during migration
- Restores previous data state
- Provides detailed rollback summary

## 🆕 Migration Wizard UI

The system now includes a comprehensive step-by-step wizard accessible through:
- **Settings → Integration Management → Migration & Integrations**
- **Direct URL**: `/migration/management` (Super Admin only)

### Wizard Features:
- **Guided Workflow**: Step-by-step process with validation
- **File Upload**: Drag-and-drop interface with progress tracking
- **Smart Mapping**: AI-powered field mapping suggestions
- **Real-time Validation**: Pre-import data validation with detailed reports
- **Progress Monitoring**: Live migration status with error handling
- **Rollback Controls**: Easy migration undo with confirmation dialogs

### Access Control:
- **Super Admin Only**: Full migration management access
- **Granular Permissions**: Delegate specific integration rights
- **Audit Logging**: Complete tracking of all migration activities

## API Endpoints

### Migration Jobs
- `POST /api/v1/migration/jobs` - Create migration job
- `GET /api/v1/migration/jobs` - List migration jobs
- `GET /api/v1/migration/jobs/{job_id}` - Get job details
- `PUT /api/v1/migration/jobs/{job_id}` - Update job
- `DELETE /api/v1/migration/jobs/{job_id}` - Delete job

### File Processing
- `POST /api/v1/migration/jobs/{job_id}/upload` - Upload source file
- `POST /api/v1/migration/jobs/{job_id}/mappings/auto` - Auto-create mappings
- `POST /api/v1/migration/jobs/{job_id}/validate` - Validate data

### Migration Execution
- `POST /api/v1/migration/jobs/{job_id}/start` - Start migration
- `GET /api/v1/migration/jobs/{job_id}/progress` - Get progress
- `POST /api/v1/migration/jobs/{job_id}/rollback` - Rollback migration

### Data Mappings
- `GET /api/v1/migration/jobs/{job_id}/mappings` - Get mappings
- `POST /api/v1/migration/jobs/{job_id}/mappings` - Create mapping
- `PUT /api/v1/migration/mappings/{mapping_id}` - Update mapping
- `DELETE /api/v1/migration/mappings/{mapping_id}` - Delete mapping

### Logs and Monitoring
- `GET /api/v1/migration/jobs/{job_id}/logs` - Get migration logs
- `GET /api/v1/migration/jobs/{job_id}/conflicts` - Get conflicts
- `GET /api/v1/migration/statistics` - Get statistics

### Templates and Bulk Operations
- `GET /api/v1/migration/templates` - List templates
- `GET /api/v1/migration/templates/{template_id}` - Get template
- `POST /api/v1/migration/bulk` - Bulk operations

### Migration Wizard
- `GET /api/v1/migration/jobs/{job_id}/wizard` - Get wizard state

### Specialized Sources
- `GET /api/v1/migration/tally/data-types` - Get Tally data types
- `GET /api/v1/migration/zoho/data-types` - Get Zoho data types

## Data Mapping Examples

### Customer Data Mapping
```json
{
  "source_field": "Customer Name",
  "target_field": "name",
  "field_type": "string",
  "is_required": true,
  "transformation_rule": "trim|title_case"
}
```

### Product Data Mapping
```json
{
  "source_field": "Item Code",
  "target_field": "part_number",
  "field_type": "string",
  "validation_rule": "alphanumeric|max_length:20"
}
```

### Financial Data Mapping
```json
{
  "source_field": "Amount",
  "target_field": "amount",
  "field_type": "number",
  "transformation_rule": "abs|round:2",
  "validation_rule": "min:0|max:999999999"
}
```

## Conflict Resolution

### Conflict Types
1. **Duplicate Records**: Same record exists in target system
2. **Data Mismatch**: Conflicting data values
3. **Validation Error**: Data doesn't meet validation rules

### Resolution Strategies
- **Skip**: Skip conflicting records
- **Update**: Update existing records with new data
- **Create New**: Create new records with modified identifiers

### Conflict Resolution Workflow
```json
{
  "conflict_type": "duplicate",
  "source_record": {...},
  "existing_record": {...},
  "suggested_resolution": "update",
  "resolution_action": "update",
  "resolution_notes": "Updated with latest data"
}
```

## Error Handling and Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about migration progress
- **WARNING**: Potential issues that don't stop migration
- **ERROR**: Errors that affect specific records
- **CRITICAL**: Critical errors that stop migration

### Log Entry Example
```json
{
  "level": "ERROR",
  "message": "Failed to create customer record",
  "source_record_id": "CUST001",
  "error_code": "VALIDATION_FAILED",
  "error_details": {
    "field": "email",
    "error": "Invalid email format"
  },
  "operation": "create_customer"
}
```

## Performance Considerations

### Large Dataset Handling
- Background processing for jobs > 1000 records
- Batch processing in chunks of 100 records
- Progress tracking and estimated completion time
- Memory-efficient streaming for large files

### Optimization Tips
- Use templates for repeated migrations
- Validate data before starting migration
- Process during off-peak hours for large migrations
- Monitor system resources during migration

## Troubleshooting

### Common Issues

#### File Upload Problems
- **File too large**: Check file size limits (default: 10MB)
- **Unsupported format**: Ensure file is in supported format
- **Corrupted file**: Re-export data from source system

#### Mapping Issues
- **Missing required fields**: Ensure all required fields are mapped
- **Data type mismatch**: Check field type configurations
- **Transformation errors**: Verify transformation rules syntax

#### Migration Failures
- **Database errors**: Check database connectivity and permissions
- **Validation errors**: Review validation rules and source data
- **Memory issues**: Reduce batch size for large datasets

### Support and Diagnostics
1. Check migration logs for detailed error information
2. Review data validation report before migration
3. Test with small dataset first
4. Contact system administrator for database-related issues

## Best Practices

### Before Migration
1. **Backup Data**: Always backup existing data before migration
2. **Test Migration**: Test with small sample data first
3. **Data Cleanup**: Clean source data before import
4. **Template Usage**: Use or create templates for repeated migrations

### During Migration
1. **Monitor Progress**: Keep an eye on migration progress
2. **Resource Usage**: Monitor system resources
3. **Error Resolution**: Address conflicts and errors promptly

### After Migration
1. **Data Verification**: Verify migrated data accuracy
2. **Rollback if Needed**: Use rollback if data is incorrect
3. **Documentation**: Document successful migration patterns
4. **Template Creation**: Create templates for future use

## Security Considerations

### Access Control
- Migration access limited to authorized users only
- Organization-level data isolation
- Audit trail for all migration activities

### Data Protection
- Secure file upload and storage
- Data encryption in transit and at rest
- Automatic cleanup of temporary files

### Compliance
- Maintain audit logs for compliance requirements
- Data retention policies for migration logs
- GDPR compliance for personal data migration

## Advanced Troubleshooting Guide

### Migration Job Status Troubleshooting

#### "Migration Stuck in Running Status"
**Symptoms**: Migration shows as "running" but no progress for extended period
**Solutions**:
1. Check system logs: `GET /api/v1/migration/jobs/{job_id}/logs`
2. Verify database connectivity
3. Check available memory and disk space
4. If necessary, cancel job and retry with smaller batch size

#### "Rollback Not Available"
**Symptoms**: Cannot rollback completed migration
**Solutions**:
1. Verify migration completed successfully
2. Check if rollback timeout period has passed (default: 7 days)
3. Ensure no dependent data has been created since migration
4. Contact administrator if rollback is critically needed

#### "Permission Denied Errors"
**Symptoms**: Users cannot access migration features
**Solutions**:
1. Verify user has super admin role or granted migration permissions
2. Check organization membership
3. Refresh user session/login again
4. Contact super admin to grant appropriate permissions

### Integration Dashboard Troubleshooting

#### "Integration Status Shows as Error"
**Symptoms**: Red error status in integration dashboard
**Solutions**:
1. Check integration-specific error logs
2. Test connection using "Test Connection" button
3. Verify configuration parameters
4. Check network connectivity to external systems
5. Review API rate limits and quotas

#### "Sync Operations Failing"
**Symptoms**: Manual sync operations fail or timeout
**Solutions**:
1. Verify integration credentials are valid
2. Check external system availability
3. Review sync logs for specific error messages
4. Ensure no concurrent sync operations are running
5. Check data volume - large syncs may timeout

### Performance Troubleshooting

#### "Slow Migration Performance"
**Symptoms**: Migration taking much longer than expected
**Solutions**:
1. Check database performance and indexes
2. Reduce batch size in migration settings
3. Schedule migration during off-peak hours
4. Monitor system CPU and memory usage
5. Consider breaking large migration into smaller jobs

#### "High Memory Usage During Migration"
**Symptoms**: System memory usage spikes during migration
**Solutions**:
1. Reduce batch processing size
2. Enable streaming mode for large files
3. Clear temporary files and caches
4. Restart migration service if memory leaks suspected

## Error Codes Reference

### Migration Error Codes
- **MIG001**: Invalid file format
- **MIG002**: File size exceeds limit
- **MIG003**: Required fields missing
- **MIG004**: Data validation failed
- **MIG005**: Database connection error
- **MIG006**: Insufficient permissions
- **MIG007**: Rollback timeout expired
- **MIG008**: Concurrent migration detected
- **MIG009**: Template not found
- **MIG010**: Mapping configuration invalid

### Integration Error Codes
- **INT001**: Connection timeout
- **INT002**: Authentication failed
- **INT003**: API rate limit exceeded
- **INT004**: Invalid configuration
- **INT005**: External service unavailable
- **INT006**: Data sync conflict
- **INT007**: Permission denied
- **INT008**: Invalid response format
- **INT009**: Network connectivity error
- **INT010**: Service temporarily unavailable

## Monitoring and Alerting

### Health Check Endpoints
```bash
# System health check
GET /api/v1/migration/health

# Integration health check
GET /api/v1/integration-settings/health

# Migration job health
GET /api/v1/migration/jobs/{job_id}/health
```

### Performance Metrics
- Migration success rate
- Average migration duration
- Error rate per integration
- System resource utilization
- Database performance metrics

### Alert Thresholds
- **Error Rate > 10%**: Critical alert
- **Migration Duration > 2x Expected**: Warning alert
- **Failed Syncs > 5 in 1 hour**: Error alert
- **Memory Usage > 90%**: Critical alert
- **Disk Space < 10%**: Critical alert

## Feedback and Issue Reporting

### Built-in Feedback System
Users can report issues and provide feedback directly through the system:
1. Navigate to Migration Management page
2. Click "Report Issue" or "Provide Feedback"
3. Fill out the feedback form with details
4. Attach relevant screenshots or logs if needed
5. Submit for administrator review

### Issue Escalation Process
1. **Level 1**: User reports issue via feedback system
2. **Level 2**: System administrator reviews and attempts resolution
3. **Level 3**: Technical team investigates complex issues
4. **Level 4**: Vendor escalation for system-level problems

### Enhancement Requests
Users can submit enhancement requests for new features:
1. Use the feedback system to submit enhancement ideas
2. Provide detailed use case and business justification
3. Administrator reviews and prioritizes requests
4. Development team evaluates feasibility
5. Features are included in future releases based on priority

## API Rate Limits and Quotas

### Migration API Limits
- **File Upload**: 10 files per hour per user
- **Job Creation**: 5 jobs per day per organization
- **Rollback Operations**: 3 per month per organization
- **Bulk Operations**: 1 concurrent operation per organization

### Integration API Limits
- **Sync Operations**: 12 per hour per integration
- **Connection Tests**: 30 per hour per user
- **Configuration Changes**: 10 per day per integration

### Monitoring Usage
Check current usage via:
```bash
GET /api/v1/migration/usage/current
GET /api/v1/integration-settings/usage/current
```

## Data Retention Policies

### Migration Data
- **Migration Jobs**: Retained for 2 years
- **Migration Logs**: Retained for 1 year
- **Uploaded Files**: Retained for 90 days
- **Rollback Data**: Retained for 30 days

### Integration Data
- **Sync Logs**: Retained for 6 months
- **Error Logs**: Retained for 1 year
- **Performance Metrics**: Retained for 3 months
- **Audit Logs**: Retained for 7 years

### Data Cleanup
Automated cleanup processes run weekly to maintain storage limits and comply with retention policies.

## Version Information

**Current Version**: 1.6.0
**Last Updated**: December 2024
**Documentation Version**: 2.0

### Recent Changes
- Added comprehensive troubleshooting guide
- Enhanced error code reference
- Expanded monitoring and alerting documentation
- Added feedback system documentation
- Updated API rate limits and quotas