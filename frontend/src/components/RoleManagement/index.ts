// frontend/src/components/RoleManagement/index.ts

/**
 * Service CRM Role Management Components
 * 
 * This module provides a comprehensive set of React components for managing
 * Service CRM roles and permissions in the frontend application.
 */

export { default as RoleManagement } from './RoleManagement';
export { default as RoleFormDialog } from './RoleFormDialog';
export { default as UserRoleAssignmentDialog } from './UserRoleAssignmentDialog';
export { default as PermissionMatrixDialog } from './PermissionMatrixDialog';

// Re-export enhanced role gate components
export { 
  default as ServiceRoleGate,
  ServiceCreateGate,
  ServiceReadGate,
  ServiceManageGate,
  TechnicianManageGate,
  AppointmentManageGate,
  ServiceReportsGate,
  CRMAdminGate
} from '../ServiceRoleGate';

// Component Documentation and Usage Examples
export const COMPONENT_DOCS = {
  RoleManagement: {
    description: 'Main role management interface with tabbed view for roles, user assignments, and permission matrix',
    props: {
      organizationId: 'number - ID of the organization to manage roles for'
    },
    usage: `
      import { RoleManagement } from '@/components/RoleManagement';
      
      function AdminPage() {
        const { user } = useAuth();
        return (
          <RoleManagement organizationId={user.organization_id} />
        );
      }
    `
  },
  
  RoleFormDialog: {
    description: 'Dialog for creating and editing service roles with permission assignment',
    props: {
      open: 'boolean - Controls dialog visibility',
      onClose: 'function - Called when dialog should close',
      role: 'ServiceRoleWithPermissions | null - Role to edit (null for create)',
      permissions: 'ServicePermission[] - Available permissions to assign',
      organizationId: 'number - Organization ID',
      onSubmit: 'function - Called when form is submitted'
    },
    usage: `
      import { RoleFormDialog } from '@/components/RoleManagement';
      
      function MyComponent() {
        const [open, setOpen] = useState(false);
        const [permissions, setPermissions] = useState([]);
        
        return (
          <RoleFormDialog
            open={open}
            onClose={() => setOpen(false)}
            permissions={permissions}
            organizationId={1}
            onSubmit={(data) => console.log('Role data:', data)}
          />
        );
      }
    `
  },
  
  ServiceRoleGate: {
    description: 'Enhanced role gate component supporting both system roles and service permissions',
    props: {
      requiredPermissions: 'string[] - Service permissions required',
      requiredRoles: 'string[] - System roles required',
      requireAll: 'boolean - Whether all permissions/roles are required (default: true)',
      fallbackComponent: 'ReactNode - Component to show when access denied',
      children: 'ReactNode - Content to render when access granted'
    },
    usage: `
      import { ServiceRoleGate, SERVICE_PERMISSIONS } from '@/components/RoleManagement';
      
      function ProtectedComponent() {
        return (
          <ServiceRoleGate 
            requiredPermissions={[SERVICE_PERMISSIONS.SERVICE_CREATE]}
            fallbackComponent={<div>Access denied</div>}
          >
            <CreateServiceButton />
          </ServiceRoleGate>
        );
      }
    `
  }
};

// Permission Gate Components - Convenient wrappers
export const PERMISSION_GATES = {
  ServiceCreateGate: 'Requires service_create permission',
  ServiceReadGate: 'Requires service_read permission', 
  ServiceManageGate: 'Requires any service management permission (create/update/delete)',
  TechnicianManageGate: 'Requires any technician management permission',
  AppointmentManageGate: 'Requires any appointment management permission',
  ServiceReportsGate: 'Requires service_reports_read permission',
  CRMAdminGate: 'Requires crm_admin permission'
};