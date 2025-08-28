'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
  Visibility as ViewIcon,
  Assignment as AssignmentIcon,
  AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { rbacService } from '../../services/rbacService';
import {
  ServiceRole,
  ServiceRoleWithPermissions,
  ServicePermission,
  UserWithServiceRoles,
  ServiceRoleType,
  ROLE_BADGE_COLORS,
  MODULE_DISPLAY_NAMES,
  PERMISSION_DISPLAY_NAMES
} from '../../types/rbac.types';
import { canManageUsers } from '../../types/user.types';
import RoleFormDialog from './RoleFormDialog';
import UserRoleAssignmentDialog from './UserRoleAssignmentDialog';
import PermissionMatrixDialog from './PermissionMatrixDialog';

interface RoleManagementProps {
  organizationId: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`role-tabpanel-${index}`}
      aria-labelledby={`role-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const RoleManagement: React.FC<RoleManagementProps> = ({ organizationId }) => {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [roles, setRoles] = useState<ServiceRoleWithPermissions[]>([]);
  const [permissions, setPermissions] = useState<ServicePermission[]>([]);
  const [users, setUsers] = useState<UserWithServiceRoles[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [roleFormOpen, setRoleFormOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<ServiceRoleWithPermissions | null>(null);
  const [userAssignmentOpen, setUserAssignmentOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserWithServiceRoles | null>(null);
  const [permissionMatrixOpen, setPermissionMatrixOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState<ServiceRole | null>(null);
  
  // Filters
  const [showInactiveRoles, setShowInactiveRoles] = useState(false);
  const [filterByRole, setFilterByRole] = useState<ServiceRoleType | 'all'>('all');

  // Check permissions
  const canManage = canManageUsers(user);

  useEffect(() => {
    if (!canManage) {
      setError('Insufficient permissions to access role management');
      setLoading(false);
      return;
    }
    
    loadData();
  }, [organizationId, canManage]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [rolesData, permissionsData] = await Promise.all([
        rbacService.getRolesWithPermissions(organizationId),
        rbacService.getPermissions()
      ]);
      
      setRoles(rolesData);
      setPermissions(permissionsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load role management data');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      // For now, we'll need to get users from a different endpoint
      // This would typically come from the user management service
      setUsers([]);
    } catch (err: any) {
      console.warn('Failed to load users:', err);
    }
  };

  const handleCreateRole = () => {
    setEditingRole(null);
    setRoleFormOpen(true);
  };

  const handleEditRole = (role: ServiceRoleWithPermissions) => {
    setEditingRole(role);
    setRoleFormOpen(true);
  };

  const handleDeleteRole = (role: ServiceRole) => {
    setRoleToDelete(role);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteRole = async () => {
    if (!roleToDelete) return;
    
    try {
      await rbacService.deleteRole(roleToDelete.id);
      await loadData();
      setDeleteDialogOpen(false);
      setRoleToDelete(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete role');
    }
  };

  const handleRoleSubmit = async (roleData: any) => {
    try {
      if (editingRole) {
        await rbacService.updateRole(editingRole.id, roleData);
      } else {
        await rbacService.createRole(organizationId, roleData);
      }
      
      await loadData();
      setRoleFormOpen(false);
      setEditingRole(null);
    } catch (err: any) {
      setError(err.message || 'Failed to save role');
    }
  };

  const handleUserAssignment = (user: UserWithServiceRoles) => {
    setSelectedUser(user);
    setUserAssignmentOpen(true);
  };

  const handleAssignRoles = async (userId: number, roleIds: number[]) => {
    try {
      await rbacService.assignRolesToUser(userId, { user_id: userId, role_ids: roleIds });
      await loadUsers();
      setUserAssignmentOpen(false);
      setSelectedUser(null);
    } catch (err: any) {
      setError(err.message || 'Failed to assign roles');
    }
  };

  const handleRemoveRole = async (userId: number, roleId: number) => {
    try {
      await rbacService.removeRoleFromUser(userId, roleId);
      await loadUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to remove role');
    }
  };

  const handleInitializeDefaults = async () => {
    try {
      await rbacService.initializeDefaultRoles(organizationId);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to initialize default roles');
    }
  };

  const getRoleIcon = (roleType: ServiceRoleType) => {
    switch (roleType) {
      case ServiceRoleType.ADMIN:
        return <AdminIcon />;
      case ServiceRoleType.MANAGER:
        return <SettingsIcon />;
      case ServiceRoleType.SUPPORT:
        return <PeopleIcon />;
      case ServiceRoleType.VIEWER:
        return <ViewIcon />;
      default:
        return <SecurityIcon />;
    }
  };

  const filteredRoles = roles.filter(role => {
    if (!showInactiveRoles && !role.is_active) return false;
    if (filterByRole !== 'all' && role.name !== filterByRole) return false;
    return true;
  });

  if (!canManage) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          You do not have permission to access role management.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Service CRM Role Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={handleInitializeDefaults}
            startIcon={<SecurityIcon />}
          >
            Initialize Defaults
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateRole}
            startIcon={<AddIcon />}
          >
            Create Role
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Role Overview" />
          <Tab label="User Assignments" />
          <Tab label="Permission Matrix" />
        </Tabs>
      </Box>

      <TabPanel value={currentTab} index={0}>
        {/* Role Overview Tab */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={showInactiveRoles}
                onChange={(e) => setShowInactiveRoles(e.target.checked)}
              />
            }
            label="Show Inactive Roles"
          />
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Filter by Role</InputLabel>
            <Select
              value={filterByRole}
              onChange={(e) => setFilterByRole(e.target.value as ServiceRoleType | 'all')}
              label="Filter by Role"
            >
              <MenuItem value="all">All Roles</MenuItem>
              {Object.values(ServiceRoleType).map(role => (
                <MenuItem key={role} value={role}>
                  {role.charAt(0).toUpperCase() + role.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Grid container spacing={3}>
          {filteredRoles.map((role) => (
            <Grid item xs={12} md={6} lg={4} key={role.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getRoleIcon(role.name)}
                    <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
                      {role.display_name}
                    </Typography>
                    <Chip
                      label={role.name}
                      color={ROLE_BADGE_COLORS[role.name] as any}
                      size="small"
                    />
                  </Box>
                  
                  {role.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {role.description}
                    </Typography>
                  )}
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Permissions: {role.permissions.length}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Edit Role">
                      <IconButton
                        size="small"
                        onClick={() => handleEditRole(role)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Role">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteRole(role)}
                        color="error"
                        disabled={!role.is_active}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {filteredRoles.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No roles found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {roles.length === 0 
                ? 'Create your first service role or initialize default roles.'
                : 'Try adjusting the filters or create a new role.'
              }
            </Typography>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        {/* User Assignments Tab */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">User Role Assignments</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage service role assignments for users in your organization.
          </Typography>
        </Box>
        
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Service Roles</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No users found. User assignments will be displayed here.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.full_name || 'Unknown'}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {user.service_roles.map((role) => (
                          <Chip
                            key={role.id}
                            label={role.display_name}
                            size="small"
                            color={ROLE_BADGE_COLORS[role.name] as any}
                          />
                        ))}
                        {user.service_roles.length === 0 && (
                          <Typography variant="caption" color="text.secondary">
                            No service roles assigned
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleUserAssignment(user)}
                        color="primary"
                      >
                        <AssignmentIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        {/* Permission Matrix Tab */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">Permission Matrix</Typography>
          <Typography variant="body2" color="text.secondary">
            View and manage permissions for each role across different modules.
          </Typography>
        </Box>
        
        <Button
          variant="outlined"
          onClick={() => setPermissionMatrixOpen(true)}
          startIcon={<SecurityIcon />}
          sx={{ mb: 3 }}
        >
          View Detailed Permission Matrix
        </Button>
        
        {/* Simplified permission overview */}
        <Grid container spacing={2}>
          {roles.map((role) => (
            <Grid item xs={12} md={6} key={role.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    {role.display_name}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {role.permissions.slice(0, 6).map((permission) => (
                      <Chip
                        key={permission.id}
                        label={permission.display_name}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {role.permissions.length > 6 && (
                      <Chip
                        label={`+${role.permissions.length - 6} more`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Dialogs */}
      <RoleFormDialog
        open={roleFormOpen}
        onClose={() => setRoleFormOpen(false)}
        role={editingRole}
        permissions={permissions}
        organizationId={organizationId}
        onSubmit={handleRoleSubmit}
      />

      {selectedUser && (
        <UserRoleAssignmentDialog
          open={userAssignmentOpen}
          onClose={() => setUserAssignmentOpen(false)}
          user={selectedUser}
          availableRoles={roles.filter(r => r.is_active)}
          onAssign={handleAssignRoles}
          onRemove={handleRemoveRole}
        />
      )}

      <PermissionMatrixDialog
        open={permissionMatrixOpen}
        onClose={() => setPermissionMatrixOpen(false)}
        roles={roles}
        permissions={permissions}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Role</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the role "{roleToDelete?.display_name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={confirmDeleteRole} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RoleManagement;