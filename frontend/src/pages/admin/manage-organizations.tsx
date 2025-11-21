// frontend/src/pages/admin/manage-organizations.tsx

"use client";
import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  TableContainer,
  Tooltip,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import {
  Lock,
  LockOpen,
  RestartAlt,
  Visibility,
  Business,
  Add,
  Settings,
  DataUsage,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { organizationService } from "../../services/organizationService";
import { useAuth } from "../../context/AuthContext";
import ModuleSelectionModal from '../../components/ModuleSelectionModal';

import { ProtectedPage } from '@/components/ProtectedPage';
interface Organization {
  id: number;
  name: string;
  subdomain: string;
  status: string;
  primary_email: string;
  primary_phone: string;
  plan_type: string;
  max_users: number;
  created_at: string;
  company_details_completed: boolean;
  enabled_modules: { [key: string]: boolean }; // Object for modules
}
const ManageOrganizations: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isSuperAdmin = user?.is_super_admin || false;
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [resetDataDialogOpen, setResetDataDialogOpen] = useState(false);
  const [moduleControlDialogOpen, setModuleControlDialogOpen] = useState(false);
  const [actionType, setActionType] = useState<
    "hold" | "activate" | "reset" | "delete" | null
  >(null);
  const [orgModules, setOrgModules] = useState<{ [key: string]: boolean }>({});
  
  // API calls using real service
  const { data: organizations, isLoading, error } = useQuery({
    queryKey: ["organizations"],
    queryFn: organizationService.getAllOrganizations,
  });
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          {error.message || "Failed to load organizations"}
        </Alert>
      </Container>
    );
  }
  
  const updateOrganizationMutation = useMutation({
    mutationFn: async ({
      orgId,
      action,
      data,
      config,
    }: {
      orgId: number;
      action: string;
      data?: any;
      config?: any;
    }) => {
      // Map actions to appropriate API calls
      if (action === "activate") {
        return organizationService.updateOrganizationById(orgId, {
          status: "active",
        }, config);
      } else if (action === "hold") {
        return organizationService.updateOrganizationById(orgId, {
          status: "suspended",
        }, config);
      } else if (action === "reset") {
        // TODO: Implement password reset API call
        console.log("Password reset for org:", orgId);
        return { message: "Password reset successfully" };
      }
      return { message: `Organization ${action} successfully` };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      setActionDialogOpen(false);
      setSelectedOrg(null);
      setActionType(null);
    },
  });
  const resetOrgDataMutation = useMutation({
    mutationFn: async ({config}: {config?: any}) => {
      return organizationService.resetOrganizationData(config);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      setResetDataDialogOpen(false);
      setSelectedOrg(null);
    },
  });
  const handleAction = (
    org: Organization,
    action: "hold" | "activate" | "reset" | "delete",
  ) => {
    setSelectedOrg(org);
    setActionType(action);
    setActionDialogOpen(true);
  };
  const handleResetData = (org: Organization) => {
    setSelectedOrg(org);
    setResetDataDialogOpen(true);
  };
  const handleModuleControl = async (org: Organization) => {
    setSelectedOrg(org);
    // Fetch current organization modules using service
    try {
      const config = isSuperAdmin ? {headers: {'X-Organization-ID': `${org.id}`}} : undefined;
      const data = await organizationService.getOrganizationModules(org.id, config);
      setOrgModules(data.enabled_modules || {});
    } catch (err) {
      console.error("Failed to fetch organization modules:", err);
      setOrgModules({});
    }
    setModuleControlDialogOpen(true);
  };
  const confirmAction = () => {
    if (selectedOrg && actionType) {
      const config = isSuperAdmin ? {headers: {'X-Organization-ID': `${selectedOrg.id}`}} : undefined;
      updateOrganizationMutation.mutate({
        orgId: selectedOrg.id,
        action: actionType,
        config,
      });
    }
  };
  const confirmResetData = () => {
    if (selectedOrg) {
      const config = isSuperAdmin ? {headers: {'X-Organization-ID': `${selectedOrg.id}`}} : undefined;
      resetOrgDataMutation.mutate({config});
    }
  };
  const getStatusChip = (status: string) => {
    const statusConfig = {
      active: { label: "Active", color: "success" as const },
      trial: { label: "Trial", color: "info" as const },
      suspended: { label: "Suspended", color: "error" as const },
      hold: { label: "On Hold", color: "warning" as const },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || {
      label: status,
      color: "default" as const,
    };
    return <Chip label={config.label} color={config.color} size="small" />;
  };
  return (

    <ProtectedPage moduleKey="admin" action="read">
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          Manage Organizations
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Add />}
          onClick={() => router.push("/admin/license-management")}
        >
          Create New License
        </Button>
      </Box>
      <Paper sx={{ mb: 3, p: 2 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <Settings sx={{ mr: 1 }} />
          Organization Management Overview
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="primary">
                {organizations?.length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Organizations
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="success.main">
                {organizations?.filter(
                  (org: Organization) => org.status === "active",
                ).length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Active Organizations
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="warning.main">
                {organizations?.filter(
                  (org: Organization) => org.status === "suspended",
                ).length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Suspended Organizations
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="info.main">
                {organizations?.filter(
                  (org: Organization) => org.status === "trial",
                ).length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Trial Organizations
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Organization</TableCell>
              <TableCell>Subdomain</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan= {7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : organizations?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No organizations found.
                </TableCell>
              </TableRow>
            ) : (
              organizations?.map((org: Organization) => (
                <TableRow key={org.id}>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Business sx={{ mr: 1, color: "primary.main" }} />
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {org.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          ID: {org.id}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="primary">
                      {org.subdomain}.trtiq.com
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        {org.primary_email}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {org.primary_phone}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{ textTransform: "capitalize" }}
                    >
                      {org.plan_type} ({org.max_users} users)
                    </Typography>
                  </TableCell>
                  <TableCell>{getStatusChip(org.status)}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(org.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="info"
                      onClick={() =>
                        router.push(`/admin/organizations/${org.id}`)
                      }
                      title="View Details"
                    >
                      <Visibility />
                    </IconButton>
                    {isSuperAdmin ? (
                      <Tooltip title="Manage module entitlements (Super Admin only)">
                        <IconButton
                          size="small"
                          color="secondary"
                          onClick={() => handleModuleControl(org)}
                        >
                          <Settings />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      <Tooltip title="Module entitlement management requires Super Admin access">
                        <span>
                          <IconButton
                            size="small"
                            color="secondary"
                            disabled
                          >
                            <Settings />
                          </IconButton>
                        </span>
                      </Tooltip>
                    )}
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleAction(org, "reset")}
                      title="Reset Password"
                    >
                      <RestartAlt />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="warning"
                      onClick={() => handleResetData(org)}
                      title="Reset Organization Data"
                    >
                      <DataUsage />
                    </IconButton>
                    {org.status === "active" ? (
                      <IconButton
                        size="small"
                        color="warning"
                        onClick={() => handleAction(org, "hold")}
                        title="Suspend Organization"
                      >
                        <Lock />
                      </IconButton>
                    ) : (
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => handleAction(org, "activate")}
                        title="Activate Organization"
                      >
                        <LockOpen />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {/* Action Confirmation Dialog */}
      <Dialog
        open={actionDialogOpen}
        onClose={() => setActionDialogOpen(false)}
      >
        <DialogTitle>
          Confirm{" "}
          {actionType === "hold"
            ? "Suspend Organization"
            : actionType === "activate"
              ? "Activate Organization"
              : "Reset Password"}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to{" "}
            {actionType === "hold"
              ? "suspend"
              : actionType === "activate"
                ? "activate"
                : "reset password for"}
            <strong> {selectedOrg?.name}</strong>?
          </Typography>
          {actionType === "reset" && (
            <Alert severity="info" sx={{ mt: 2 }}>
              A new temporary password will be generated and sent to the
              organization admin.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmAction}
            variant="contained"
            color={actionType === "hold" ? "warning" : "primary"}
            disabled={updateOrganizationMutation.isPending}
          >
            {updateOrganizationMutation.isPending ? "Processing..." : "Confirm"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Reset Organization Data Dialog */}
      <Dialog
        open={resetDataDialogOpen}
        onClose={() => setResetDataDialogOpen(false)}
      >
        <DialogTitle>Reset Organization Data</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Are you sure you want to reset all business data for
            <strong> {selectedOrg?.name}</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This will permanently delete all business data including:
            <ul>
              <li>Products and inventory</li>
              <li>Vendors and customers</li>
              <li>Vouchers and transactions</li>
              <li>Reports and analytics data</li>
            </ul>
            User accounts and organization settings will be preserved.
          </Alert>
          <Alert severity="error" sx={{ mt: 1 }}>
            This action cannot be undone!
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDataDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmResetData}
            variant="contained"
            color="error"
            disabled={resetOrgDataMutation.isPending}
          >
            {resetOrgDataMutation.isPending ? "Resetting..." : "Reset All Data"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Module Control Modal */}
      <ModuleSelectionModal
        open={moduleControlDialogOpen}
        onClose={() => setModuleControlDialogOpen(false)}
        orgId={selectedOrg?.id}
        orgName={selectedOrg?.name}
        isSuperAdmin={isSuperAdmin}
      />
    </Container>

    </ProtectedPage>

  
  );
};
export default ManageOrganizations;