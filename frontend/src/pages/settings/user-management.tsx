// frontend/src/pages/settings/user-management.tsx
"use client";
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
  CircularProgress,
  Divider,
  FormGroup,
  FormControlLabel,
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
  Settings,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationService } from "../../services/organizationService";
import adminService from "../../services/adminService";  // Import admin service for super admin
import { useAuth } from "../../context/AuthContext";
import { getDisplayRole, canManageUsers, canResetPasswords } from "../../types/user.types";
import AddUserDialog from "../../components/AddUserDialog";
import { useRouter } from "next/navigation";
import { ProtectedPage } from "../../components/ProtectedPage";

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

const UserManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const router = useRouter();
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
  const displayRole = getDisplayRole(user?.role || "", user?.is_super_admin);

  // Debug logging
  console.log("UserManagement.tsx - Current user:", JSON.stringify(user, null, 2));
  console.log("UserManagement.tsx - Display Role:", displayRole);
  console.log("UserManagement.tsx - Can Manage Users:", canManage);

  // Get current organization (super_admin has null)
  const currentOrgId = user?.organization_id;
  const isSuperAdmin = user?.is_super_admin || false;

  // Fetch users: super_admin fetches all app users; org admins fetch org users
  const { data: users, isLoading: usersLoading, error: usersError } = useQuery<User[]>({
    queryKey: ["users", currentOrgId],
    queryFn: async () => {
      if (isSuperAdmin && !currentOrgId) {
        // Super admin: fetch all app users
        return adminService.getAllUsers();  // Assume adminService.getAllUsers() fetches all platform users
      } else if (currentOrgId) {
        // Org admin: fetch org users
        return organizationService.getOrganizationUsers(currentOrgId);
      } else {
        throw new Error("Invalid user context");
      }
    },
    enabled: canManage,
  });

  // Mutations: use org-scoped for org admins, platform for super_admin
  const createUserMutation = useMutation({
    mutationFn: (userData: any) => {
      if (isSuperAdmin && !currentOrgId) {
        return adminService.createUser(userData);  // Assume adminService.createUser for platform users
      } else {
        return organizationService.createUserInOrganization(currentOrgId!, userData);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", currentOrgId] });
      setCreateDialogOpen(false);
      resetForm();
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ userId, userData }: { userId: number; userData: any }) => {
      if (isSuperAdmin && !currentOrgId) {
        return adminService.updateUser(userId, userData);  // Assume adminService.updateUser
      } else {
        return organizationService.updateUserInOrganization(currentOrgId!, userId, userData);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", currentOrgId] });
      setEditDialogOpen(false);
      setSelectedUser(null);
      resetForm();
    },
  });

  const userActionMutation = useMutation({
    mutationFn: ({ userId, action }: { userId: number; action: string }) => {
      if (isSuperAdmin && !currentOrgId) {
        // Super admin actions on platform users
        switch (action) {
          case "delete":
            return adminService.deleteUser(userId);
          case "activate":
            return adminService.updateUser(userId, { is_active: true });
          case "deactivate":
            return adminService.updateUser(userId, { is_active: false });
          case "reset":
            return adminService.resetUserPassword(userId);
          default:
            throw new Error("Invalid action");
        }
      } else {
        // Org admin actions
        switch (action) {
          case "delete":
            return organizationService.deleteUserFromOrganization(currentOrgId!, userId);
          case "activate":
            return organizationService.updateUserInOrganization(currentOrgId!, userId, { is_active: true });
          case "deactivate":
            return organizationService.updateUserInOrganization(currentOrgId!, userId, { is_active: false });
          case "reset":
            return organizationService.resetUserPassword(currentOrgId!, userId);
          default:
            throw new Error("Invalid action");
        }
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users", currentOrgId] });
      setActionDialogOpen(false);
      setSelectedUser(null);
      setActionType(null);
    },
    onError: (error) => {
      console.error("Action failed:", error);
    },
  });

  // Title based on context
  const pageTitle = isSuperAdmin && !currentOrgId ? "App User Management" : "Organization User Management";

  // If loading or no context, show appropriate message
  if (usersLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  // If user doesn't have permission to manage users, show message
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

  // If no org context and not super admin, show error
  if (!isSuperAdmin && !currentOrgId) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Organization context not available. Please refresh the page.
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

  const handleCreateUser = (userData: any) => {
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
        masters: true,
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
    let color:
      | "default"
      | "primary"
      | "secondary"
      | "error"
      | "info"
      | "success"
      | "warning" = "default";
    if (is_super_admin || role === "super_admin") {
      color = "error";
    } else if (role === "management") {
      color = "secondary";
    } else if (role === "manager") {
      color = "primary";
    } else {
      color = "default";
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
    <ProtectedPage
      moduleKey="settings"
      action="read"
      accessDeniedMessage="You do not have permission to manage users. This requires settings access and role management capability."
    >
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
              {pageTitle}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Managing {isSuperAdmin && !currentOrgId ? "platform" : "organization"} users
              {currentOrgId ? ` (ID: ${currentOrgId})` : ""}
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
                      <IconButton
                        size="small"
                        color="secondary"
                        onClick={() => router.push(`/settings/user-permissions/${user.id}`)}
                        title="Manage Permissions"
                      >
                        <Settings />
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
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="h6">Edit User</Typography>
              <Button
                size="small"
                startIcon={<Settings />}
                onClick={() => {
                  setEditDialogOpen(false);
                  if (selectedUser) {
                    router.push(`/settings/user-permissions/${selectedUser.id}`);
                  }
                }}
              >
                Manage Permissions
              </Button>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mb: 2, mt: 1 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Module and permission access can now be managed in the dedicated Permissions page.
                  Use the "Manage Permissions" button above or the gear icon in the user table.
                </Typography>
              </Alert>
            </Box>
            
            {/* Basic Information Section */}
            <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 2 }}>
              Basic Information
            </Typography>
            <Grid container spacing={2}>
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
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            {/* Email and Account Section */}
            <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 2 }}>
              Email & Account
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, email: e.target.value }))
                  }
                  required
                  helperText="Changing email will require user to verify the new email address"
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
                  label="New Password (Optional)"
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, password: e.target.value }))
                  }
                  helperText="Leave blank to keep current password"
                />
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            {/* Organization Details Section */}
            <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 2 }}>
              Organization Details
            </Typography>
            <Grid container spacing={2}>
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
    </ProtectedPage>
  );
};

export default UserManagement;