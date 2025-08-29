# Multi-Company Support Documentation

## Overview

The multi-company feature enables organizations to manage multiple companies within a single organizational structure. This feature is designed for businesses that operate multiple subsidiaries, divisions, or separate business entities under one organizational umbrella.

## Key Features

- **Multiple Companies per Organization**: Organizations can create multiple companies based on their license limit
- **Company-Scoped User Management**: Users can be assigned to one or more companies
- **Company Admin Role**: Dedicated role for company-level administration
- **Data Isolation**: Company-specific data access controls
- **Flexible User Assignment**: Users can belong to multiple companies with different permission levels

## Architecture

### Hierarchy Structure

```
App Super Admin (Platform Level)
└── Organization (Tenant Level)
    ├── Company A
    │   ├── Company Admin
    │   └── Standard Users
    ├── Company B
    │   ├── Company Admin
    │   └── Standard Users
    └── Company C
        ├── Company Admin
        └── Standard Users
```

### Database Schema

The multi-company support is implemented through several key database entities:

#### Organization Table Extensions
- `max_companies`: Maximum number of companies allowed (set by app super admin)

#### Company Table
- Stores company information (name, address, business details)
- Linked to organization via `organization_id`
- Supports multiple companies per organization (unique constraint on `organization_id + name`)

#### UserCompany Junction Table
- Many-to-many relationship between users and companies
- Tracks company admin status per user-company assignment
- Supports soft deletion for reassignment capabilities

## User Roles and Permissions

### Role Definitions

1. **App Super Admin**
   - Platform-wide access
   - Can set `max_companies` limits for organizations
   - Full access to all companies across all organizations

2. **Organization Admin**
   - Full access to all companies within their organization
   - Can create new companies (within limit)
   - Can assign users to companies
   - Can appoint company admins

3. **Company Admin**
   - Organization admin privileges scoped to assigned companies
   - Can manage users within their companies
   - Cannot create new companies
   - Cannot access other companies' data

4. **Standard User**
   - Basic access to assigned companies
   - Must be explicitly assigned to companies
   - Cannot manage other users

### Permission Matrix

| Action | App Super Admin | Org Admin | Company Admin | Standard User |
|--------|----------------|-----------|---------------|---------------|
| Create Companies | ✅ | ✅ | ❌ | ❌ |
| Assign Users to Companies | ✅ | ✅ | ❌ | ❌ |
| Manage Company Users | ✅ | ✅ | ✅ (own companies) | ❌ |
| Access Company Data | ✅ | ✅ | ✅ (assigned companies) | ✅ (assigned companies) |
| Set Max Companies Limit | ✅ | ❌ | ❌ | ❌ |
| View All Companies | ✅ | ✅ (own org) | ✅ (assigned only) | ✅ (assigned only) |

## API Reference

### Company Management

#### Create Company
```http
POST /api/v1/companies/
```

**Request Body:**
```json
{
  "name": "Acme Corp",
  "address1": "123 Business St",
  "city": "Business City",
  "state": "State",
  "pin_code": "123456",
  "state_code": "12",
  "gst_number": "22AAAAA0000A1Z5",
  "business_type": "Manufacturing",
  "industry": "Technology"
}
```

**Validations:**
- Checks organization's `max_companies` limit
- Validates unique company name per organization
- Requires organization admin permissions

#### List Companies
```http
GET /api/v1/companies/
```

Returns all companies accessible to the current user based on their role and assignments.

### User-Company Management

#### Assign User to Company
```http
POST /api/v1/companies/{company_id}/users
```

**Request Body:**
```json
{
  "user_id": 124,
  "company_id": 1,
  "is_company_admin": false
}
```

#### Update User Assignment
```http
PUT /api/v1/companies/{company_id}/users/{user_id}
```

**Request Body:**
```json
{
  "is_company_admin": true,
  "is_active": true
}
```

#### Remove User from Company
```http
DELETE /api/v1/companies/{company_id}/users/{user_id}
```

Performs soft deletion (sets `is_active` to false).

## Frontend Implementation

### Multi-Company Management Interface

The frontend provides a comprehensive interface for managing multiple companies:

- **Company Cards**: Visual representation of each company with key details
- **User Assignment Modal**: Interface for assigning users to companies
- **Company Admin Toggle**: Easy promotion/demotion of company admins
- **Limit Monitoring**: Visual indicators for `max_companies` limits

### Key Components

- `MultiCompanyManagement`: Main component for company overview and management
- `CompanyDetailsModal`: Reusable modal for creating/editing companies
- Enhanced `authService`: API integration for multi-company endpoints

## Configuration

### Organization License Setup

App super admins can set the `max_companies` limit when creating organization licenses:

```json
{
  "organization_name": "Example Corp",
  "superadmin_email": "admin@example.com",
  "max_companies": 5
}
```

### Default Values

- `max_companies`: 1 (maintains backward compatibility)
- `is_company_admin`: false (users are standard by default)
- `is_active`: true (active assignments by default)

## Migration Guide

### From Single Company to Multi-Company

1. **Database Migration**: Run the provided migration script to add the necessary tables and fields
2. **Existing Data**: Current single companies remain as the first company in each organization
3. **User Access**: Existing users maintain their current access levels
4. **API Compatibility**: Existing single-company endpoints continue to work

### Migration Script

```bash
# Run the database migration
python -m alembic upgrade head
```

The migration includes:
- Adding `max_companies` field to organizations
- Creating `user_companies` table
- Updating company unique constraints
- Creating necessary indexes

## Best Practices

### User Assignment Strategy

1. **Start Simple**: Begin with single company assignment for most users
2. **Strategic Multi-Assignment**: Only assign users to multiple companies when necessary
3. **Clear Admin Hierarchy**: Maintain clear company admin assignments
4. **Regular Audits**: Periodically review user-company assignments

### Permission Management

1. **Principle of Least Privilege**: Assign minimum necessary permissions
2. **Role Clarity**: Ensure users understand their role scope
3. **Company Boundaries**: Respect data isolation between companies
4. **Audit Trails**: Monitor permission changes and access patterns

### Data Organization

1. **Logical Company Structure**: Create companies that reflect business structure
2. **Consistent Naming**: Use clear, descriptive company names
3. **Complete Company Profiles**: Fill in all relevant company information
4. **Regular Maintenance**: Keep company information up to date

## Security Considerations

### Data Isolation

- Company data is strictly isolated by user assignments
- Users cannot access companies they're not assigned to
- Company admins cannot access other companies' data

### Permission Validation

- All API endpoints validate company access
- Role-based permissions are enforced at the company level
- Audit logs track all user-company assignment changes

### Access Control

- Multi-factor authentication recommended for company admins
- Regular review of user assignments required
- Automated alerts for permission changes

## Troubleshooting

### Common Issues

1. **Max Companies Reached**: Contact app super admin to increase limit
2. **User Cannot Access Company**: Check user-company assignment status
3. **Permission Denied**: Verify user's role and company assignments
4. **Company Creation Failed**: Check organization's remaining company quota

### Debug Steps

1. Verify user's current company assignments
2. Check organization's `max_companies` limit
3. Validate user's role and permissions
4. Review audit logs for recent changes

## Support

For technical support regarding multi-company features:

1. Check this documentation for common solutions
2. Review the API documentation for endpoint details
3. Contact your system administrator for permission issues
4. Reach out to technical support for complex problems