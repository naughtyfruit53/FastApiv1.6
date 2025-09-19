// frontend/src/pages/settings/user-management.tsx
import React, { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  Alert,
  Divider,
  FormGroup,
  FormControlLabel,
  Tabs,
  Tab,
  Checkbox,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Lock,
  LockOpen,
  RestartAlt,
  Person,
  Group,
  CheckCircle,
  Block,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationService } from "../../services/organizationService";
import { useAuth } from "../../context/AuthContext";
import {
  getDisplayRole,
  canManageUsers,
  canResetPasswords,
  canManageRoles,
} from "../../types/user.types";
import AddUserDialog from "../../components/AddUserDialog"; // Now points to the updated modal
import RoleManagement from "../../components/RoleManagement/RoleManagement"; // Corrected path to components/RoleManagement/RoleManagement.tsx; assuming default export
interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_super_admin?: boolean;
  department?: string;
  designation?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
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
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const UserManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [actionType, setActionType] = useState<
    "reset" | "activate" | "deactivate" | "delete" | null
  >(null);
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    full_name: "",
    password: "",
    role: "executive",
    department: "",
    designation: "",
    modules: {
      masters: false,
      inventory: false,
      vouchers: false,
      reports: false,
    },
  });
  // Permission checks
  const canManage = canManageUsers(user);
  const canReset = canResetPasswords(user);
  const canManageRolesPerm = canManageRoles(user);
  // Get current organization ID from auth context
  const currentOrgId = user?.organization_id;
  // Real API calls using organization-scoped endpoints - all hooks must be at the top
  const { data: users, isLoading: usersLoading, error: usersError } = useQuery<User[]>({
    queryKey: ["organization-users", currentOrgId],
    queryFn: () => organizationService.getOrganizationUsers(currentOrgId!),
    enabled: canManage && !!currentOrgId, // Only fetch if user has permission and org ID exists
  });
  const createUserMutation = useMutation({
    mutationFn: (userData: any) =>
      organizationService.createUserInOrganization(currentOrgId!, userData),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organization-users", currentOrgId],
      });
      setCreateDialogOpen(false);
      resetForm();
    },
  });
  const updateUserMutation = useMutation({
    mutationFn: ({ userId, userData }: { userId: number; userData: any }) =>
      organizationService.updateUserInOrganization(
        currentOrgId!,
        userId,
        userData,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organization-users", currentOrgId],
      });
      setEditDialogOpen(false);
      setSelectedUser(null);
      resetForm();
    },
  });
  const userActionMutation = useMutation({
    mutationFn: ({ userId, action }: { userId: number; action: string }) => {
      switch (action) {
        case "delete":
          return organizationService.deleteUserFromOrganization(
            currentOrgId!,
            userId,
          );
        case "activate":
          return organizationService.updateUserInOrganization(
            currentOrgId!,
            userId,
            { is_active: true }
          );
        case "deactivate":
          return organizationService.updateUserInOrganization(
            currentOrgId!,
            userId,
            { is_active: false }
          );
        case "reset":
          // Assuming organizationService has a resetUserPassword method; implement if not
          return organizationService.resetUserPassword(currentOrgId!, userId);
        default:
          throw new Error("Invalid action");
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organization-users", currentOrgId],
      });
      setActionDialogOpen(false);
      setSelectedUser(null);
      setActionType(null);
    },
    onError: (error) => {
      console.error("Action failed:", error);
      // Optionally show a snackbar or alert for error
    },
  });
  // Ensure we have a valid organization ID
  if (!currentOrgId) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Organization context not available. Please refresh the page.
        </Alert>
      </Container>
    );
  }
  // If user doesn't have permission to manage users, redirect or show message
  if (!canManage) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          You don&apos;t have permission to manage users. Only organization
          administrators can manage users.
        </Alert>
      </Container>
    );
  }
  const resetForm = () => {
    setFormData({
      email: "",
      username: "",
      full_name: "",
      password: "",
      role: "executive",
      department: "",
      designation: "",
      modules: {
        masters: false,
        inventory: false,
        vouchers: false,
        reports: false,
      },
    });
  };
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  const handleCreateUser = (userData: any) => {
    // No password included; backend will auto-generate and email it
    createUserMutation.mutate(userData);
  };
  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setFormData({
      email: user.email,
      username: user.username,
      full_name: user.full_name,
      password: "",
      role: user.role,
      department: user.department || "",
      designation: user.designation || "",
      modules: {
        masters: true, // These would come from user permissions
        inventory: true,
        vouchers: user.role === "manager",
        reports: true,
      },
    });
    setEditDialogOpen(true);
  };
  const handleUpdateUser = () => {
    if (selectedUser) {
      const userData: any = {
        email: formData.email,
        username: formData.username,
        full_name: formData.full_name,
        role: formData.role,
        department: formData.department,
        designation: formData.designation,
      };
      // Only include password if provided
      if (formData.password) {
        userData.password = formData.password;
      }
      updateUserMutation.mutate({
        userId: selectedUser.id,
        userData: userData,
      });
    }
  };
  const handleAction = (
    user: User,
    action: "reset" | "activate" | "deactivate" | "delete",
  ) => {
    setSelectedUser(user);
    setActionType(action);
    setActionDialogOpen(true);
  };
  const confirmAction = () => {
    if (selectedUser && actionType) {
      userActionMutation.mutate({
        userId: selectedUser.id,
        action: actionType,
      });
    }
  };
  const getRoleChip = (role: string, is_super_admin?: boolean) => {
    const displayRole = getDisplayRole(role, is_super_admin);
    // Color mapping based on actual role levels
    let color:
      | "default"
      | "primary"
      | "secondary"
      | "error"
      | "info"
      | "success"
      | "warning" = "default";
    if (is_super_admin || role === "super_admin") {
      color = "error"; // Red for highest privilege
    } else if (role === "management") {
      color = "secondary"; // Purple for management
    } else if (role === "manager") {
      color = "primary"; // Blue for manager
    } else {
      color = "default"; // Gray for executive
    }
    return <Chip label={displayRole} color={color} size="small" />;
  };
  const getStatusChip = (isActive: boolean) => {
    return (
      <Chip
        label={isActive ? "Active" : "Inactive"}
        color={isActive ? "success" : "error"}
        size="small"
        icon={isActive ? <CheckCircle /> : <Block />}
      />
    );
  };
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography variant="h4" component="h1">
            User Management
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Managing users for{" "}
            {user?.is_super_admin
              ? "all organizations"
              : "your organization"}
            {currentOrgId > 0 &&
              !user?.is_super_admin &&
              ` (ID: ${currentOrgId})`}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Add New User
        </Button>
      </Box>
      <Tabs
        value={tabValue}
        onChange={handleTabChange}
        sx={{ mb: 3, borderBottom: 1, borderColor: "divider" }}
      >
        <Tab label="Users" />
        {canManageRolesPerm && <Tab label="Roles & Permissions" />}
      </Tabs>
      <TabPanel value={tabValue} index={0}>
        <Paper sx={{ mb: 3, p: 2 }}>
          <Typography
            variant="h6"
            gutterBottom
            sx={{ display: "flex", alignItems: "center" }}
          >
            <Group sx={{ mr: 1 }} />
            Users Overview
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" color="primary">
                  {users?.length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Users
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" color="success.main">
                  {users?.filter((user: User) => user.is_active).length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Users
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" color="info.main">
                  {users?.filter((user: User) => user.role === "manager").length ||
                    0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Manager Users
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" color="secondary.main">
                  {users?.filter((user: User) => user.role === "executive")
                    .length || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Executive Users
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {usersLoading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : usersError ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Alert severity="error">Failed to load users: {usersError.message}</Alert>
                  </TableCell>
                </TableRow>
              ) : users?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No users found. Add your first user to get started.
                  </TableCell>
                </TableRow>
              ) : (
                users?.map((user: User) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Person sx={{ mr: 1, color: "primary.main" }} />
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {user.full_name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            @{user.username}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{user.email}</Typography>
                    </TableCell>
                    <TableCell>
                      {getRoleChip(user.role, user.is_super_admin)}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {user.department || "-"}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {user.designation || ""}
                      </Typography>
                    </TableCell>
                    <TableCell>{getStatusChip(user.is_active)}</TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {user.last_login
                          ? new Date(user.last_login).toLocaleDateString()
                          : "Never"}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditUser(user)}
                        title="Edit User"
                      >
                        <Edit />
                      </IconButton>
                      {canReset && (
                        <IconButton
                          size="small"
                          color="info"
                          onClick={() => handleAction(user, "reset")}
                          title="Reset Password"
                        >
                          <RestartAlt />
                        </IconButton>
                      )}
                      {user.is_active ? (
                        <IconButton
                          size="small"
                          color="warning"
                          onClick={() => handleAction(user, "deactivate")}
                          title="Deactivate User"
                        >
                          <Lock />
                        </IconButton>
                      ) : (
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleAction(user, "activate")}
                          title="Activate User"
                        >
                          <LockOpen />
                        </IconButton>
                      )}
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleAction(user, "delete")}
                        title="Delete User"
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      {canManageRolesPerm && (
        <TabPanel value={tabValue} index={1}>
          <RoleManagement />
        </TabPanel>
      )}
      {/* Create User Dialog */}
      <AddUserDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        loading={createUserMutation.isPending}
        onAdd={handleCreateUser}
        organizationId={user?.organization_id || 0}
      />
      {/* Edit User Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.full_name}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    full_name: e.target.value,
                  }))
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                value={formData.username}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, username: e.target.value }))
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, email: e.target.value }))
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={formData.role}
                  label="Role"
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      role: e.target.value as string,
                    }))
                  }
                >
                  <MenuItem value="executive">Executive</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="management">Management</MenuItem>
                  <MenuItem value="super_admin">Super Admin</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                value={formData.department}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    department: e.target.value,
                  }))
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Designation"
                value={formData.designation}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    designation: e.target.value,
                  }))
                }
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Module Access
              </Typography>
              <FormGroup row>
                {Object.entries(formData.modules).map(([module, checked]) => (
                  <FormControlLabel
                    key={module}
                    control={
                      <Checkbox
                        checked={checked}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            modules: {
                              ...prev.modules,
                              [module]: e.target.checked,
                            },
                          }))
                        }
                        disabled={formData.role === "manager"} // Manager gets all modules
                      />
                    }
                    label={module.charAt(0).toUpperCase() + module.slice(1)}
                  />
                ))}
              </FormGroup>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateUser}
            variant="contained"
            disabled={updateUserMutation.isPending}
          >
            {updateUserMutation.isPending ? "Updating..." : "Update User"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Action Confirmation Dialog */}
      <Dialog
        open={actionDialogOpen}
        onClose={() => setActionDialogOpen(false)}
      >
        <DialogTitle>
          Confirm{" "}
          {actionType === "reset"
            ? "Password Reset"
            : actionType === "activate"
              ? "User Activation"
              : actionType === "deactivate"
                ? "User Deactivation"
                : "User Deletion"}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {actionType} user
            <strong> {selectedUser?.full_name}</strong>?
          </Typography>
          {actionType === "reset" && (
            <Alert severity="info" sx={{ mt: 2 }}>
              A new temporary password will be generated and sent to the
              user&apos;s email.
            </Alert>
          )}
          {actionType === "delete" && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This action cannot be undone. The user will lose access
              permanently.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmAction}
            variant="contained"
            color={actionType === "delete" ? "error" : "primary"}
            disabled={userActionMutation.isPending}
          >
            {userActionMutation.isPending ? "Processing..." : "Confirm"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
export default UserManagement;