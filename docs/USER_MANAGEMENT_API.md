# User Management API Documentation

## Overview

This document describes the enhanced organization-scoped user management and invitation system API endpoints. These endpoints provide comprehensive user management capabilities within the multi-tenant architecture.

**🔄 Supabase Auth Integration**: All user creation operations now integrate with Supabase Auth to ensure users can log in through standard authentication flows.

## Authentication

All endpoints require valid JWT token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Supabase Auth Integration

### User Creation Flow

When creating users through the API, the system now follows this process:

1. **Supabase Auth User Creation**: First, the user is created in Supabase Auth using the Admin API
2. **Local Database User Creation**: Upon successful Supabase creation, the user profile is created in the application database
3. **Transaction Safety**: If either step fails, the entire operation is rolled back to maintain consistency

### Key Benefits

- **Unified Authentication**: Users created via API can immediately log in through Supabase Auth
- **Consistent User Experience**: No manual user activation required
- **Audit Trail**: Complete user lifecycle tracking across both systems
- **Failure Safety**: Automatic cleanup if any step fails

### Technical Details

- Uses `SUPABASE_SERVICE_KEY` for admin-level operations
- Stores Supabase UUID in local user profile for future reference
- Auto-confirms email addresses for admin-created users
- Includes user metadata in Supabase Auth profile

### Required Environment Variables

The following environment variables must be configured for Supabase Auth integration:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

**Important**: 
- The `SUPABASE_SERVICE_KEY` is the service role key (not the anon public key) and should be kept secure as it has admin privileges.
- The `SUPABASE_JWT_SECRET` is the JWT signing secret used by Supabase for token operations. When configured, all JWT encode/decode operations will use this secret for consistency with Supabase-issued tokens.
- If `SUPABASE_JWT_SECRET` is not provided, the system will fall back to using `SECRET_KEY` for backward compatibility.

## Authentication

All endpoints require valid JWT token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Permission Requirements

- **Super Admin**: Can manage users across all organizations
- **Organization Admin**: Can manage users within their own organization only
- **Standard User**: Can only view/update their own profile

## Organization-Scoped User Management

### List Organization Users

**GET** `/api/v1/organizations/{organization_id}/users`

Get all users in a specific organization.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `skip` (query, integer, optional): Number of users to skip for pagination (default: 0)
- `limit` (query, integer, optional): Maximum number of users to return (default: 100)
- `active_only` (query, boolean, optional): Filter to active users only (default: true)
- `role` (query, string, optional): Filter by user role

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
[
  {
    "id": 123,
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "role": "standard_user",
    "organization_id": 1,
    "is_active": true,
    "department": "IT",
    "designation": "Developer",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
]
```

### Create User in Organization

**POST** `/api/v1/organizations/{organization_id}/users`

Create a new user in the specified organization.

**Parameters:**
- `organization_id` (path, integer): Organization ID

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "full_name": "New User",
  "password": "SecurePassword123!",
  "role": "standard_user",
  "department": "Sales",
  "designation": "Sales Rep",
  "employee_id": "EMP001",
  "phone": "+1234567890",
  "is_active": true
}
```

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
{
  "id": 124,
  "email": "newuser@example.com",
  "username": "newuser",
  "full_name": "New User",
  "role": "standard_user",
  "organization_id": 1,
  "supabase_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "is_active": true,
  "department": "Sales",
  "designation": "Sales Rep",
  "employee_id": "EMP001",
  "phone": "+1234567890",
  "created_at": "2024-01-20T12:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: If Supabase Auth user creation fails
- `500 Internal Server Error`: If local database creation fails (Supabase user is automatically cleaned up)

### Update User in Organization

**PUT** `/api/v1/organizations/{organization_id}/users/{user_id}`

Update an existing user in the organization.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `user_id` (path, integer): User ID to update

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "department": "Engineering",
  "role": "admin"
}
```

**Permissions:** 
- Users can update their own basic information
- Organization Admin or Super Admin can update any user in the organization

**Response:**
```json
{
  "id": 124,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "role": "admin",
  "organization_id": 1,
  "is_active": true,
  "department": "Engineering",
  "created_at": "2024-01-20T12:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z"
}
```

### Delete User from Organization

**DELETE** `/api/v1/organizations/{organization_id}/users/{user_id}`

Remove a user from the organization.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `user_id` (path, integer): User ID to delete

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
{
  "message": "User user@example.com deleted successfully"
}
```

**Notes:**
- Users cannot delete themselves
- Cannot delete the last organization administrator

## Invitation Management

### List Organization Invitations

**GET** `/api/v1/organizations/{organization_id}/invitations`

Get all pending invitations for the organization.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `skip` (query, integer, optional): Pagination offset (default: 0)
- `limit` (query, integer, optional): Maximum results (default: 100)
- `status` (query, string, optional): Filter by invitation status

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
[
  {
    "id": 456,
    "email": "invited@example.com",
    "role": "standard_user",
    "status": "pending",
    "invited_at": "2024-01-20T10:00:00Z",
    "invited_by": "admin@example.com",
    "organization_id": 1,
    "organization_name": "Example Organization"
  }
]
```

### Resend Invitation

**POST** `/api/v1/organizations/{organization_id}/invitations/{invitation_id}/resend`

Resend an invitation email to a pending user.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `invitation_id` (path, integer): Invitation/User ID

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
{
  "message": "Invitation resent to invited@example.com"
}
```

### Cancel Invitation

**DELETE** `/api/v1/organizations/{organization_id}/invitations/{invitation_id}`

Cancel a pending invitation.

**Parameters:**
- `organization_id` (path, integer): Organization ID
- `invitation_id` (path, integer): Invitation/User ID

**Permissions:** Organization Admin or Super Admin

**Response:**
```json
{
  "message": "Invitation cancelled for invited@example.com"
}
```

## Legacy User Management Endpoints

The existing user management endpoints at `/api/v1/users/` continue to work for backward compatibility but are organization-scoped based on the current user's context.

- `GET /api/v1/users/` - List users in current user's organization
- `POST /api/v1/users/` - Create user in current user's organization
- `PUT /api/v1/users/{user_id}` - Update user in current user's organization
- `DELETE /api/v1/users/{user_id}` - Delete user from current user's organization

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Organization or user not found |
| 409 | Conflict - Email or username already exists |
| 500 | Internal Server Error - Server error |

## Rate Limiting

API endpoints are subject to rate limiting:
- 100 requests per minute per user for read operations
- 20 requests per minute per user for write operations

## Examples

### Create User Flow

1. **Organization Admin creates user:**
```bash
curl -X POST \
  https://api.example.com/api/v1/organizations/1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "SecurePass123!",
    "role": "standard_user"
  }'
```

2. **User receives invitation email** (if email service is configured)

3. **User logs in and must change password** (indicated by `must_change_password: true`)

### Invitation Management Flow

1. **List pending invitations:**
```bash
curl -X GET \
  https://api.example.com/api/v1/organizations/1/invitations \
  -H "Authorization: Bearer <token>"
```

2. **Resend invitation:**
```bash
curl -X POST \
  https://api.example.com/api/v1/organizations/1/invitations/456/resend \
  -H "Authorization: Bearer <token>"
```

3. **Cancel invitation:**
```bash
curl -X DELETE \
  https://api.example.com/api/v1/organizations/1/invitations/456 \
  -H "Authorization: Bearer <token>"
```

## Migration Notes

### From Previous Version

1. **New Endpoints Available**: Organization-scoped endpoints provide better organization context
2. **Backward Compatibility**: Existing `/api/v1/users/` endpoints continue to work
3. **Enhanced Permissions**: Role-based permissions are strictly enforced
4. **Invitation Management**: New invitation lifecycle management capabilities

### Breaking Changes

None. All changes are additive and maintain backward compatibility.

### Recommended Migration

1. Update frontend to use organization-scoped endpoints for better clarity
2. Update API clients to include organization context
3. Take advantage of new invitation management features
4. Update user management UIs to show organization context

## Support

For questions about these API endpoints, please refer to:
- API documentation at `/docs` or `/redoc`
- OpenAPI specification at `/openapi.json`
- Organization management documentation