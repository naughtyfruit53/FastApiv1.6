# Service CRM RBAC (Role-Based Access Control) Documentation

## Overview

The Service CRM RBAC system provides comprehensive role-based access control for the Service CRM integration. It enables fine-grained permission management across different modules while maintaining backward compatibility with the existing user role system.

## Key Features

- **Granular Permissions**: 30+ permissions covering all Service CRM modules
- **Four Default Roles**: Admin, Manager, Support, and Viewer roles
- **Multi-Tenant Support**: Roles and permissions are organization-scoped
- **Fallback Security**: Integration with existing permission system
- **Real-time Permission Checking**: Dynamic permission validation
- **Comprehensive UI**: Full management interface with role assignment

## Architecture

### Backend Components

#### Models
- **ServiceRole**: Service CRM roles (admin, manager, support, viewer)
- **ServicePermission**: Granular permissions for CRUD operations per module
- **ServiceRolePermission**: Many-to-many relationship between roles and permissions
- **UserServiceRole**: Many-to-many relationship between users and service roles

#### Services
- **RBACService**: Core service for role and permission management
- **RBACDependency**: FastAPI dependency for permission checking

#### API Endpoints
- `/api/v1/rbac/permissions` - Permission management
- `/api/v1/rbac/organizations/{org_id}/roles` - Role management per organization
- `/api/v1/rbac/users/{user_id}/roles` - User role assignments
- `/api/v1/rbac/roles/{role_id}/users` - Users with specific roles

### Frontend Components

#### Services
- **rbacService**: Client-side service for RBAC operations
- **ServiceRoleGate**: Enhanced role gate supporting service permissions

#### Components
- **RoleManagement**: Main role management interface
- **RoleFormDialog**: Create/edit roles with permission assignment
- **UserRoleAssignmentDialog**: Assign roles to users
- **PermissionMatrixDialog**: View permission matrix across roles

## Permissions Model

### Service Modules
- **Service Management**: service_create, service_read, service_update, service_delete
- **Technician Management**: technician_create, technician_read, technician_update, technician_delete
- **Appointment Management**: appointment_create, appointment_read, appointment_update, appointment_delete
- **Customer Service**: customer_service_create, customer_service_read, customer_service_update, customer_service_delete
- **Work Orders**: work_order_create, work_order_read, work_order_update, work_order_delete
- **Service Reports**: service_reports_read, service_reports_export
- **CRM Administration**: crm_admin, crm_settings

### Default Roles

#### Service Admin
- **Permissions**: All permissions (30+ permissions)
- **Use Case**: Full system administration
- **Access Level**: Complete access to all Service CRM functionality

#### Service Manager
- **Permissions**: 15 permissions covering management operations
- **Use Case**: Department managers and supervisors
- **Access Level**: Can manage services, technicians, appointments, and view reports

#### Support Agent
- **Permissions**: 11 permissions focused on customer service
- **Use Case**: Customer service representatives and support staff
- **Access Level**: Can handle customer service, create appointments, update work orders

#### Viewer
- **Permissions**: 6 read-only permissions
- **Use Case**: Stakeholders who need visibility without edit access
- **Access Level**: Read-only access to service information and reports

## API Usage Examples

### Initialize Default Roles for Organization

```bash
POST /api/v1/rbac/organizations/1/roles/initialize
Authorization: Bearer {token}
```

Response:
```json
{
  "message": "Initialized 4 default roles",
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "display_name": "Service Admin",
      "organization_id": 1,
      "is_active": true
    }
  ]
}
```

### Create Custom Role

```bash
POST /api/v1/rbac/organizations/1/roles
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "support",
  "display_name": "Customer Support",
  "description": "Handles customer inquiries and basic service operations",
  "permission_ids": [1, 2, 5, 8, 11]
}
```

### Assign Role to User

```bash
POST /api/v1/rbac/users/123/roles
Content-Type: application/json
Authorization: Bearer {token}

{
  "user_id": 123,
  "role_ids": [1, 2]
}
```

### Check User Permission

```bash
POST /api/v1/rbac/permissions/check
Content-Type: application/json
Authorization: Bearer {token}

{
  "user_id": 123,
  "permission": "service_create",
  "organization_id": 1
}
```

Response:
```json
{
  "has_permission": true,
  "user_id": 123,
  "permission": "service_create",
  "source": "service_role"
}
```

## Frontend Usage Examples

### Role Management Interface

```tsx
import { RoleManagement } from '@/components/RoleManagement';
import { useAuth } from '@/context/AuthContext';

function AdminPage() {
  const { user } = useAuth();
  
  return (
    <div>
      <h1>Service CRM Administration</h1>
      <RoleManagement organizationId={user.organization_id} />
    </div>
  );
}
```

### Permission-Based UI Components

```tsx
import { 
  ServiceRoleGate, 
  ServiceCreateGate, 
  SERVICE_PERMISSIONS 
} from '@/components/RoleManagement';

function ServiceManagementPage() {
  return (
    <div>
      <h1>Service Management</h1>
      
      {/* Show create button only if user has create permission */}
      <ServiceCreateGate fallback={<div>Create access not available</div>}>
        <Button>Create New Service</Button>
      </ServiceCreateGate>
      
      {/* Complex permission check */}
      <ServiceRoleGate
        requiredPermissions={[
          SERVICE_PERMISSIONS.SERVICE_UPDATE,
          SERVICE_PERMISSIONS.SERVICE_DELETE
        ]}
        requireAll={false} // User needs either update OR delete
        fallbackComponent={<div>Advanced features not available</div>}
      >
        <AdvancedServiceActions />
      </ServiceRoleGate>
    </div>
  );
}
```

### Using RBAC Service

```tsx
import { rbacService, SERVICE_PERMISSIONS } from '@/services/rbacService';

function useServicePermissions() {
  const [permissions, setPermissions] = useState<string[]>([]);
  
  useEffect(() => {
    const loadPermissions = async () => {
      try {
        const userPermissions = await rbacService.getCurrentUserPermissions();
        setPermissions(userPermissions);
      } catch (error) {
        console.error('Failed to load permissions:', error);
      }
    };
    
    loadPermissions();
  }, []);
  
  const canCreateService = permissions.includes(SERVICE_PERMISSIONS.SERVICE_CREATE);
  const canManageTechnicians = permissions.includes(SERVICE_PERMISSIONS.TECHNICIAN_CREATE);
  
  return { permissions, canCreateService, canManageTechnicians };
}
```

## Database Schema

### Service Permissions Table
```sql
CREATE TABLE service_permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    display_name VARCHAR NOT NULL,
    description TEXT,
    module VARCHAR NOT NULL,
    action VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

### Service Roles Table
```sql
CREATE TABLE service_roles (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    name VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    UNIQUE(organization_id, name)
);
```

### User Service Roles Table
```sql
CREATE TABLE user_service_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES service_roles(id),
    assigned_by_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    UNIQUE(user_id, role_id)
);
```

## Migration Guide

### Running the Migration

```bash
# Apply the RBAC migration
alembic upgrade rbac_service_crm_001
```

### Initialize Default Data

```bash
# Initialize default permissions (super admin only)
curl -X POST http://localhost:8000/api/v1/rbac/permissions/initialize \
  -H "Authorization: Bearer {super_admin_token}"

# Initialize default roles for an organization
curl -X POST http://localhost:8000/api/v1/rbac/organizations/1/roles/initialize \
  -H "Authorization: Bearer {admin_token}"
```

## Security Considerations

### Permission Hierarchy
1. **Super Admin**: Bypasses all Service CRM permission checks
2. **Service Roles**: Checked via RBAC system
3. **System Roles**: Fallback permission checking for backward compatibility

### Organization Isolation
- All service roles are scoped to organizations
- Users can only be assigned roles within their organization
- Cross-organization access requires super admin privileges

### Audit Trail
- All role assignments are logged with assigned_by_id
- Permission checks are logged for security monitoring
- Role changes trigger audit events

## Testing

### Backend Tests
- **Unit Tests**: 300+ lines of comprehensive test coverage
- **Permission Checking**: Validates all permission scenarios
- **Role Management**: Tests role CRUD operations
- **User Assignment**: Tests role assignment workflows

### Frontend Tests
```tsx
// Example test for ServiceRoleGate
import { render, screen } from '@testing-library/react';
import { ServiceRoleGate, SERVICE_PERMISSIONS } from '@/components/RoleManagement';

test('ServiceRoleGate shows children when user has permission', async () => {
  // Mock user with service_create permission
  mockAuth({ 
    user: { id: 1, role: 'standard_user' },
    permissions: [SERVICE_PERMISSIONS.SERVICE_CREATE]
  });
  
  render(
    <ServiceRoleGate requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_CREATE]}>
      <div>Protected Content</div>
    </ServiceRoleGate>
  );
  
  expect(screen.getByText('Protected Content')).toBeInTheDocument();
});
```

## Performance Considerations

### Permission Caching
- User permissions are cached in the frontend context
- Cache invalidation on role changes
- Efficient batch permission checks

### Database Optimization
- Indexed foreign keys for fast lookups
- Optimized queries for permission checking
- Minimal database calls for common operations

## Future Enhancements

### Planned Features
1. **Time-based Permissions**: Temporary role assignments with expiration
2. **Permission Delegation**: Allow users to delegate specific permissions
3. **Advanced Audit**: Enhanced audit trail with detailed permission history
4. **Role Templates**: Predefined role templates for common use cases
5. **Dynamic Permissions**: Context-aware permissions based on business rules

### API Extensions
- GraphQL support for complex permission queries
- Webhook notifications for role changes
- Bulk operations for large-scale permission management
- Permission analytics and reporting

## Troubleshooting

### Common Issues

#### Permission Not Working
1. Check if user has the service role assigned
2. Verify role has the required permission
3. Ensure permission is active
4. Check organization context

#### Role Assignment Fails
1. Verify user and role are in same organization
2. Check if current user has role management permissions
3. Ensure role is active and exists

#### Frontend Permission Gate Not Working
1. Check if rbacService is properly configured
2. Verify API endpoints are accessible
3. Check browser console for permission loading errors
4. Ensure auth context is properly set up

### Debug Mode
```tsx
// Enable debug logging for permission checks
localStorage.setItem('RBAC_DEBUG', 'true');

// This will log all permission checks to console
```

This comprehensive RBAC system provides enterprise-grade access control for the Service CRM integration while maintaining simplicity and ease of use.