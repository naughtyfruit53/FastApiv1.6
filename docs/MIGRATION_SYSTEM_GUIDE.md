# Migration & Data Import System Documentation

## Overview

The Migration & Data Import System provides a comprehensive solution for importing data from various sources into the ERP system. It supports guided migration workflows, data validation, conflict resolution, and rollback capabilities.

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
POST /api/v1/migration/jobs/{job_id}/start
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