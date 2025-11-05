// frontend/src/pages/settings/general-settings.tsx
"use client";
/**
 * General Settings Page Component
 *
 * This component provides the main settings interface for users with different roles.
 * It uses centralized role and permission functions from user.types.ts to ensure
 * consistent behavior across the application.
 *
 * Role Display:
 * - Uses getDisplayRole(user.role, user.is_super_admin) for consistent role naming
 * - Prioritizes is_super_admin flag over role string for App Super Admin detection
 *
 * Permission Checks:
 * - isAppSuperAdmin(user): Determines if user is an app-level super admin
 * - canFactoryReset(user): Determines if user can perform reset operations
 * - canManageUsers(user): Determines if user can manage other users
 *
 * Features shown based on permissions:
 * - App Super Admin: All features including cross-org management
 * - Org Admin: Organization-level management and reset options
 * - Standard User: Basic profile and company detail access only
 */
import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert as MuiAlert,
  CircularProgress,
  Divider,
  DialogContentText,
  Snackbar,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import {
  Warning,
  DeleteSweep,
  Security,
  Business,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { apiClient } from "../../services/api/client";
import { useAuth } from "../../context/AuthContext";
import {
  getDisplayRole,
  isAppSuperAdmin,
  canFactoryReset,
  canAccessOrganizationSettings,
  canShowFactoryResetOnly,
  canShowOrgDataResetOnly,
} from "../../types/user.types";
import OrganizationSettings from "../../components/OrganizationSettings";
import { ProtectedPage } from "../../components/ProtectedPage";

export default function GeneralSettings() {
  const router = useRouter();
  const { user } = useAuth();
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [factoryResetDialogOpen, setFactoryResetDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [factoryLoading, setFactoryLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error";
  }>({ open: false, message: "", severity: "success" });

  // Use centralized permission and role functions
  const displayRole = getDisplayRole(user?.role || "", user?.is_super_admin);
  const isSuperAdmin = isAppSuperAdmin(user);
  const canReset = canFactoryReset(user);
  const canAccessOrgSettings = canAccessOrganizationSettings(user);
  const showFactoryResetOnly = canShowFactoryResetOnly(user);
  const showOrgDataResetOnly = canShowOrgDataResetOnly(user);

  // Debug logging
  console.log("GeneralSettings.tsx - Current user:", JSON.stringify(user, null, 2));
  console.log("GeneralSettings.tsx - Display Role:", displayRole);
  console.log("GeneralSettings.tsx - Is Super Admin:", isSuperAdmin);
  console.log("GeneralSettings.tsx - Can Access Org Settings:", canAccessOrgSettings);

  /**
   * @deprecated Organization name should come from React user context, not localStorage
   * Organization context is automatically managed by the backend session
   */
  const organizationName = user?.organization_id
    ? "Current Organization"
    : null;

  const handleResetData = async () => {
    setLoading(true);
    setSnackbar({ open: false, message: "", severity: "success" });
    try {
      const response = await apiClient.post("/organizations/reset-data", {});
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: "success",
      });
      setResetDialogOpen(false);
      // For organization admins, refresh the page to reflect changes
      if (!isSuperAdmin) {
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || "Failed to reset data",
        severity: "error",
      });
      setResetDialogOpen(false);
    } finally {
      setLoading(false);
    }
  };

  const handleFactoryReset = async () => {
    setFactoryLoading(true);
    setSnackbar({ open: false, message: "", severity: "success" });
    try {
      const response = await apiClient.post("/organizations/factory-default", {});
      setSnackbar({
        open: true,
        message: response.data.message,
        severity: "success",
      });
      setFactoryResetDialogOpen(false);
      // Refresh the page to reflect changes
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || "Failed to perform factory reset",
        severity: "error",
      });
      setFactoryResetDialogOpen(false);
    } finally {
      setFactoryLoading(false);
    }
  };

  return (
    <ProtectedPage moduleKey="settings" action="read">
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          General Settings
        </Typography>
      {/* User Role Information */}
      <Paper
        sx={{ p: 2, mb: 3, bgcolor: "info.main", color: "info.contrastText" }}
      >
        <Typography variant="body1">
          <strong>Current Role:</strong> {displayRole}{" "}
          {organizationName && `• Organization: ${organizationName}`}
        </Typography>
      </Paper>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <MuiAlert
          severity={snackbar.severity}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          {snackbar.message}
        </MuiAlert>
      </Snackbar>
      <Grid container spacing={3}>
        {/* Admin Section - For App Admin User Creation */}
        {isSuperAdmin && (
          <Grid
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center" }}
              >
                <Security sx={{ mr: 1 }} />
                Admin Management
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <MuiAlert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  App admins can create organization licenses but cannot create
                  other app admin users.
                </Typography>
              </MuiAlert>
              <Button
                variant="contained"
                onClick={() => router.push("/admin/license-management")}
                sx={{ mb: 2, mr: 2 }}
                startIcon={<Business />}
                color="primary"
              >
                License Management
              </Button>
              <Button
                variant="outlined"
                onClick={() => router.push("/admin/organizations")}
                sx={{ mb: 2 }}
                startIcon={<Business />}
              >
                Manage Organizations
              </Button>
            </Paper>
          </Grid>
        )}
        {/* Organization Settings Component - Includes Tally Sync for Org Admins */}
        {canAccessOrgSettings && (
          <Grid size={{ xs: 12 }}>
            <OrganizationSettings />
          </Grid>
        )}
        {/* User Profile for App Super Admins (when Organization Settings is hidden) */}
        {!canAccessOrgSettings && (
          <Grid
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center" }}
              >
                <Business sx={{ mr: 1 }} />
                User Profile
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Button
                variant="outlined"
                onClick={() => router.push("/profile")}
                sx={{ mb: 2 }}
              >
                Edit Profile
              </Button>
            </Paper>
          </Grid>
        )}
        {/* Data Management */}
        {canReset && (
          <Grid
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center" }}
              >
                <Security sx={{ mr: 1 }} />
                Data Management
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <MuiAlert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Warning:</strong> Database reset will permanently
                  delete data
                  {showFactoryResetOnly
                    ? " for all organizations"
                    : " for your organization"}
                  . This action cannot be undone.
                </Typography>
              </MuiAlert>
              {/* App Super Admin: Only Factory Reset */}
              {showFactoryResetOnly && (
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Warning />}
                  onClick={() => setFactoryResetDialogOpen(true)}
                  disabled={loading || factoryLoading}
                  sx={{ mt: 1 }}
                >
                  {factoryLoading ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    "Restore to Factory Defaults"
                  )}
                </Button>
              )}
              {/* Org Super Admin: Only Reset Organization Data */}
              {showOrgDataResetOnly && (
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<DeleteSweep />}
                  onClick={() => setResetDialogOpen(true)}
                  disabled={loading || factoryLoading}
                  sx={{ mt: 1 }}
                >
                  {loading ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    "Reset Organization Data"
                  )}
                </Button>
              )}
              {/* Legacy: Both options for other admin types */}
              {!showFactoryResetOnly && !showOrgDataResetOnly && (
                <>
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<DeleteSweep />}
                    onClick={() => setResetDialogOpen(true)}
                    disabled={loading || factoryLoading}
                    sx={{ mt: 1, mr: 2 }}
                  >
                    {loading ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      `Reset ${isSuperAdmin ? "All" : "Organization"} Data`
                    )}
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    startIcon={<Warning />}
                    onClick={() => setFactoryResetDialogOpen(true)}
                    disabled={loading || factoryLoading}
                    sx={{ mt: 1 }}
                  >
                    {factoryLoading ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      "Factory Default Reset"
                    )}
                  </Button>
                </>
              )}
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {showFactoryResetOnly
                  ? "Restore to Factory Defaults: Wipes all app data including organizations, licenses, and license holders"
                  : showOrgDataResetOnly
                    ? "Reset Organization Data: Removes all business data but not organization settings"
                    : isSuperAdmin
                      ? "As app super admin, this will reset all organization data"
                      : "Reset data: removes all business data but keeps organization settings"}
              </Typography>
            </Paper>
          </Grid>
        )}
        {/* System Administration - App-level controls only */}
        {isSuperAdmin && (
          <Grid size={12}>
            <Paper sx={{ p: 3 }}>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center" }}
              >
                <Warning sx={{ mr: 1, color: "warning.main" }} />
                System Administration
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <MuiAlert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  System-level controls for application management. Use with
                  caution.
                </Typography>
              </MuiAlert>
              <Button
                variant="outlined"
                onClick={() => router.push("/dashboard")}
                sx={{ mr: 2, mb: 2 }}
                startIcon={<Business />}
              >
                App Dashboard
              </Button>
            </Paper>
          </Grid>
        )}
      </Grid>
      {/* Reset Confirmation Dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)}>
        <DialogTitle sx={{ display: "flex", alignItems: "center" }}>
          <Warning sx={{ mr: 1, color: "error.main" }} />
          Confirm Data Reset
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to reset{" "}
            {showOrgDataResetOnly
              ? "your organization&apos;s"
              : isSuperAdmin
                ? "all"
                : "your organization&apos;s"}{" "}
            data? This action will permanently delete:
          </DialogContentText>
          <Box component="ul" sx={{ mt: 2, mb: 2 }}>
            <li>All companies</li>
            <li>All vendors and customers</li>
            <li>All products and inventory</li>
            <li>All vouchers and transactions</li>
            <li>All audit logs</li>
            {isSuperAdmin && !showOrgDataResetOnly && (
              <>
                <li>All organization users (except super admin)</li>
                <li>All organizations</li>
              </>
            )}
          </Box>
          <DialogContentText color="error">
            <strong>This action cannot be undone!</strong>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleResetData}
            color="error"
            variant="contained"
            disabled={loading}
            startIcon={
              loading ? <CircularProgress size={16} /> : <DeleteSweep />
            }
          >
            {loading ? "Resetting..." : "Reset Data"}
          </Button>
        </DialogActions>
      </Dialog>
      {/* Factory Default Confirmation Dialog */}
      <Dialog
        open={factoryResetDialogOpen}
        onClose={() => setFactoryResetDialogOpen(false)}
      >
        <DialogTitle sx={{ display: "flex", alignItems: "center" }}>
          <Warning sx={{ mr: 1, color: "warning.main" }} />
          {showFactoryResetOnly
            ? "Confirm Restore to Factory Defaults"
            : "Confirm Factory Default Reset"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {showFactoryResetOnly ? (
              <>
                Are you sure you want to restore the entire application to
                factory defaults? This action will permanently delete:
              </>
            ) : (
              <>
                Are you sure you want to perform a factory default reset? This
                action will permanently restore your organization to its initial
                state:
              </>
            )}
          </DialogContentText>
          <Box component="ul" sx={{ mt: 2, mb: 2 }}>
            {showFactoryResetOnly ? (
              <>
                <li>All organizations and their data</li>
                <li>All licenses and license holders</li>
                <li>All users (except the primary super admin)</li>
                <li>All companies, vendors, customers</li>
                <li>All products and inventory</li>
                <li>All vouchers and transactions</li>
                <li>All audit logs</li>
                <li>System returns to initial installation state</li>
              </>
            ) : (
              <>
                <li>All business data will be deleted (same as data reset)</li>
                <li>Organization settings will be reset to defaults</li>
                <li>Business type will be set to &quot;Other&quot;</li>
                <li>Timezone will be set to &quot;Asia/Kolkata&quot;</li>
                <li>Currency will be set to &quot;INR&quot;</li>
                <li>Company details status will be reset</li>
              </>
            )}
          </Box>
          <DialogContentText
            color={showFactoryResetOnly ? "error" : "warning.main"}
          >
            <strong>
              {showFactoryResetOnly
                ? "This action cannot be undone and will completely reset the entire application!"
                : "This action cannot be undone and will reset both data and settings!"}
            </strong>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setFactoryResetDialogOpen(false)}
            disabled={factoryLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleFactoryReset}
            color={showFactoryResetOnly ? "error" : "warning"}
            variant="contained"
            disabled={factoryLoading}
            startIcon={
              factoryLoading ? <CircularProgress size={16} /> : <Warning />
            }
          >
            {factoryLoading
              ? "Resetting..."
              : showFactoryResetOnly
                ? "Restore to Factory Defaults"
                : "Factory Default Reset"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
    </ProtectedPage>
  );
}