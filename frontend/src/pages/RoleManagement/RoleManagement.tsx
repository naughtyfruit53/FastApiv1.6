// frontend/src/pages/RoleManagement/RoleManagement.tsx
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
  FormControlLabel,
  Checkbox,
  Alert,
} from "@mui/material";
import { Add, Edit, Delete, Save } from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rbacService } from "../../services/rbacService"; // Assuming rbacService exists; implement if not
import { useAuth } from "../../context/AuthContext";

interface Role {
  id: number;
  name: string;
  display_name: string;
  description: string;
  permissions: string[]; // Array of permission names
}

interface Permission {
  id: number;
  name: string;
  display_name: string;
  description: string;
}

const RoleManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    display_name: "",
    description: "",
    permissions: [] as string[],
  });
  const currentOrgId = user?.organization_id;

  // Fetch roles
  const { data: roles, isLoading: rolesLoading, error: rolesError } = useQuery<Role[]>({
    queryKey: ["roles", currentOrgId],
    queryFn: () => rbacService.getOrganizationRoles(currentOrgId!),
    enabled: !!currentOrgId,
  });

  // Fetch all permissions
  const { data: permissions, isLoading: permissionsLoading, error: permissionsError } = useQuery<Permission[]>({
    queryKey: ["permissions", currentOrgId],
    queryFn: () => rbacService.getPermissions(),
    enabled: !!currentOrgId,
  });

  const createRoleMutation = useMutation({
    mutationFn: (roleData: any) => rbacService.createRole(currentOrgId!, roleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", currentOrgId] });
      setCreateDialogOpen(false);
      resetForm();
    },
    onError: (error) => {
      console.error("Failed to create role:", error);
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ roleId, roleData }: { roleId: number; roleData: any }) =>
      rbacService.updateRole(roleId, roleData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", currentOrgId] });
      setEditDialogOpen(false);
      setSelectedRole(null);
      resetForm();
    },
    onError: (error) => {
      console.error("Failed to update role:", error);
    },
  });

  const deleteRoleMutation = useMutation({
    mutationFn: (roleId: number) => rbacService.deleteRole(roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", currentOrgId] });
    },
    onError: (error) => {
      console.error("Failed to delete role:", error);
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      display_name: "",
      description: "",
      permissions: [],
    });
  };

  const handleEditRole = (role: Role) => {
    setSelectedRole(role);
    setFormData({
      name: role.name,
      display_name: role.display_name,
      description: role.description,
      permissions: role.permissions,
    });
    setEditDialogOpen(true);
  };

  const handleCreateRole = () => {
    createRoleMutation.mutate(formData);
  };

  const handleUpdateRole = () => {
    if (selectedRole) {
      updateRoleMutation.mutate({
        roleId: selectedRole.id,
        roleData: formData,
      });
    }
  };

  const handleDeleteRole = (roleId: number) => {
    if (window.confirm("Are you sure you want to delete this role?")) {
      deleteRoleMutation.mutate(roleId);
    }
  };

  const handlePermissionToggle = (permissionName: string, checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      permissions: checked
        ? [...prev.permissions, permissionName]
        : prev.permissions.filter((p) => p !== permissionName),
    }));
  };

  if (rolesLoading || permissionsLoading) {
    return <Typography>Loading roles and permissions...</Typography>;
  }

  if (rolesError || permissionsError) {
    return (
      <Alert severity="error">
        Failed to load data: {(rolesError || permissionsError)?.message}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Roles & Permissions</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Role
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Permissions</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {roles?.map((role) => (
              <TableRow key={role.id}>
                <TableCell>{role.display_name}</TableCell>
                <TableCell>{role.description}</TableCell>
                <TableCell>
                  {role.permissions.map((perm) => (
                    <Chip key={perm} label={perm} size="small" sx={{ m: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <IconButton onClick={() => handleEditRole(role)}>
                    <Edit />
                  </IconButton>
                  <IconButton color="error" onClick={() => handleDeleteRole(role.id)}>
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Role Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Role</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Role Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1">Permissions</Typography>
              <FormGroup>
                {permissions?.map((perm) => (
                  <FormControlLabel
                    key={perm.id}
                    control={
                      <Checkbox
                        checked={formData.permissions.includes(perm.name)}
                        onChange={(e) => handlePermissionToggle(perm.name, e.target.checked)}
                      />
                    }
                    label={perm.display_name}
                  />
                ))}
              </FormGroup>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateRole} disabled={createRoleMutation.isPending}>
            {createRoleMutation.isPending ? <CircularProgress size={24} /> : "Create"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Role Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Role</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Role Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1">Permissions</Typography>
              <FormGroup>
                {permissions?.map((perm) => (
                  <FormControlLabel
                    key={perm.id}
                    control={
                      <Checkbox
                        checked={formData.permissions.includes(perm.name)}
                        onChange={(e) => handlePermissionToggle(perm.name, e.target.checked)}
                      />
                    }
                    label={perm.display_name}
                  />
                ))}
              </FormGroup>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdateRole} disabled={updateRoleMutation.isPending}>
            {updateRoleMutation.isPending ? <CircularProgress size={24} /> : "Update"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RoleManagement;