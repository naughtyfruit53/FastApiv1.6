// Revised: frontend/src/pages/admin/organizations/[id].tsx
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Snackbar from "@mui/material/Snackbar";
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { ProtectedPage } from '../../../components/ProtectedPage';
import api from "../../../utils/api";  // Import the axios api instance
interface Organization {
  id: number;
  name: string;
  subdomain: string;
  status: string;
  business_type?: string;
  industry?: string;
  website?: string;
  description?: string;
  primary_email: string;
  primary_phone: string;
  address1: string;
  address2?: string;
  city: string;
  state: string;
  pin_code: string;
  state_code?: string;
  country: string;
  gst_number?: string;
  pan_number?: string;
  cin_number?: string;
  plan_type: string;
  max_users: number;
  storage_limit_gb: number;
  timezone: string;
  currency: string;
  created_at: string;
  updated_at?: string;
  superadmin_full_name?: string;  // Added full name field
}
interface AdminUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
}
const OrganizationDetailPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [userLoading, setUserLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editedOrg, setEditedOrg] = useState<Organization | null>(null);
  const [editedFullName, setEditedFullName] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);
  const [openResetDialog, setOpenResetDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [resetPassword, setResetPassword] = useState<string | null>(null);
  const [resetSnackbarOpen, setResetSnackbarOpen] = useState(false);
  const [pincodeLoading, setPincodeLoading] = useState(false);
  useEffect(() => {
    if (id) {
      // fetchOrganization is defined later in this file
      fetchOrganization();
      fetchAdminUser();
    }
  }, [id]);
  useEffect(() => {
    /**
     * @deprecated Organization context should be accessed via React user context instead of localStorage instead
     * The organization context is automatically managed by the backend session
     */
    if (organization) {
      console.log("Organization details loaded:", organization.id);
      // Organization context is managed by backend session only
    }
  }, [organization]);
  const fetchOrganization = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/organizations/${id}`, {
        headers: { 'X-Organization-ID': `${id}` }
      });
      const data = response.data;
      setOrganization(data);
      setEditedOrg(data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Failed to load organization details",
      );
    } finally {
      setLoading(false);
    }
  };
  const fetchAdminUser = async () => {
    try {
      setUserLoading(true);
      // Fetch organization users and find the org_admin
      const response = await api.get(`/organizations/${id}/members`, {
        headers: { 'X-Organization-ID': `${id}` }
      });
      const users = response.data;
      const orgAdmin = users.find((user: AdminUser) => user.role === 'org_admin');
      setAdminUser(orgAdmin || null);
      setUserError(null);
      setEditedFullName(orgAdmin?.full_name || '');
    } catch (err: any) {
      console.error(err);
      setUserError(
        err.response?.data?.detail || "Failed to load admin user details",
      );
    } finally {
      setUserLoading(false);
    }
  };
  const handleEdit = () => {
    setEditing(true);
    setEditedOrg({ ...organization! });
    setEditedFullName(adminUser?.full_name || '');
  };
  const handleCancel = () => {
    setEditing(false);
    setEditedOrg({ ...organization! });
    setEditedFullName(adminUser?.full_name || '');
  };
  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await api.put(`/organizations/${id}`, editedOrg, {
        headers: { 'X-Organization-ID': `${id}` }
      });
      const updatedOrg = response.data;
      setOrganization(updatedOrg);
      // Update admin full name if changed
      if (adminUser && editedFullName !== adminUser.full_name) {
        await api.put(`/users/${adminUser.id}`, { full_name: editedFullName }, {
          headers: { 'X-Organization-ID': `${id}` }
        });
        setAdminUser({ ...adminUser, full_name: editedFullName });
      }
      setEditing(false);
      toast.success("Organization updated successfully");
    } catch (err) {
      toast.error("Failed to update organization");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };
  const handleDelete = async () => {
    try {
      const response = await api.delete(`/organizations/${id}`);
      toast.success("Organization deleted successfully");
      router.push("/admin/license-management");
    } catch (error: any) {
      let errorMessage = "Failed to delete organization";
      if (error.response?.data) {
        errorMessage = error.response.data.detail || error.response.data.message || errorMessage;
      } else {
        errorMessage = error.message || errorMessage;
      }
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setOpenDeleteDialog(false);
    }
  };
  const handleInputChange = (
    field: keyof Organization,
    value: string | number,
  ) => {
    if (editedOrg) {
      setEditedOrg({
        ...editedOrg,
        [field]: value,
      });
    }
  };
  const handlePincodeChange = async (value: string) => {
    handleInputChange("pin_code", value);
    if (value.length === 6 && editing) {
      setPincodeLoading(true);
      try {
        const response = await api.get(`/pincode/lookup/${value}`);
        const { city, state, state_code } = response.data;
        handleInputChange("city", city);
        handleInputChange("state", state);
        handleInputChange("state_code", state_code);
      } catch (err) {
        console.error(err);
        toast.error("Failed to autofill city and state from PIN code");
      } finally {
        setPincodeLoading(false);
      }
    }
  };
  const handleResetPassword = async () => {
    try {
      const response = await api.post(`/password/admin-reset`, {
        user_email: organization?.primary_email
      });
      const data = response.data;
      setResetPassword(data.new_password);
      setOpenResetDialog(false);
      setResetSnackbarOpen(true);
      toast.success("Password reset successfully");
    } catch (err: any) {
      toast.error(
        err.response?.data?.detail || "Failed to reset password",
      );
      console.error(err);
    }
  };
  const getStatusColor = (
    status: string,
  ): "success" | "error" | "warning" | "default" => {
    switch (status) {
      case "active":
        return "success";
      case "suspended":
        return "error";
      case "trial":
        return "warning";
      default:
        return "default";
    }
  };
  if (loading || userLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="200px"
      >
        <CircularProgress />
      </Box>
    );
  }
  if (error || userError || !organization) {
    return (
      <Box p={3}>
        <Alert severity="error">{error || userError || "Organization not found"}</Alert>
        <Button
          variant="contained"
          onClick={() => router.push("/admin/organizations")}
          sx={{ mt: 2 }}
        >
          Back to Organizations
        </Button>
      </Box>
    );
  }
  const currentOrg = editing ? editedOrg! : organization;
  return (
    <ProtectedPage moduleKey="admin" action="read" customCheck={(pc) => pc.checkIsSuperAdmin()}>
    <Box p={3}>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Organization Details
        </Typography>
        <Box>
          {!editing ? (
            <>
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={handleEdit}
                sx={{ mr: 1 }}
              >
                Edit
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => setOpenResetDialog(true)}
                sx={{ mr: 1 }}
              >
                Reset Password
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => setOpenDeleteDialog(true)}
              >
                Delete License
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
                sx={{ mr: 1 }}
              >
                {saving ? "Saving..." : "Save"}
              </Button>
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
                disabled={saving}
              >
                Cancel
              </Button>
            </>
          )}
        </Box>
      </Box>
      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Organization Name"
                    value={currentOrg.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Subdomain"
                    value={currentOrg.subdomain}
                    onChange={(e) =>
                      handleInputChange("subdomain", e.target.value)
                    }
                    disabled={!editing}
                    helperText="Used for subdomain-specific access"
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Super Admin Full Name"
                    value={editing ? editedFullName : (adminUser?.full_name || currentOrg.superadmin_full_name || "")}
                    onChange={(e) => setEditedFullName(e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="body2">Status:</Typography>
                    <Chip
                      label={currentOrg.status}
                      color={getStatusColor(currentOrg.status)}
                      size="small"
                    />
                  </Box>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Business Type"
                    value={currentOrg.business_type || ""}
                    onChange={(e) =>
                      handleInputChange("business_type", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Industry"
                    value={currentOrg.industry || ""}
                    onChange={(e) =>
                      handleInputChange("industry", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Website"
                    value={currentOrg.website || ""}
                    onChange={(e) =>
                      handleInputChange("website", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={3}
                    value={currentOrg.description || ""}
                    onChange={(e) =>
                      handleInputChange("description", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        {/* Contact Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Primary Email"
                    value={currentOrg.primary_email}
                    onChange={(e) =>
                      handleInputChange("primary_email", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Primary Phone"
                    value={currentOrg.primary_phone}
                    onChange={(e) =>
                      handleInputChange("primary_phone", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Address Line 1"
                    value={currentOrg.address1}
                    onChange={(e) =>
                      handleInputChange("address1", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Address Line 2"
                    value={currentOrg.address2 || ""}
                    onChange={(e) =>
                      handleInputChange("address2", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="PIN Code"
                    value={currentOrg.pin_code}
                    onChange={(e) => handlePincodeChange(e.target.value)}
                    disabled={!editing}
                    InputProps={{
                      endAdornment: pincodeLoading ? (
                        <CircularProgress size={20} />
                      ) : null,
                    }}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="City"
                    value={currentOrg.city}
                    onChange={(e) => handleInputChange("city", e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="State"
                    value={currentOrg.state}
                    onChange={(e) => handleInputChange("state", e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    fullWidth
                    label="Country"
                    value={currentOrg.country}
                    onChange={(e) =>
                      handleInputChange("country", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        {/* Legal & Subscription Information */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Legal & Subscription Information
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="GST Number"
                    value={currentOrg.gst_number || ""}
                    onChange={(e) =>
                      handleInputChange("gst_number", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="PAN Number"
                    value={currentOrg.pan_number || ""}
                    onChange={(e) =>
                      handleInputChange("pan_number", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="CIN Number"
                    value={currentOrg.cin_number || ""}
                    onChange={(e) =>
                      handleInputChange("cin_number", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 3 }}>
                  <TextField
                    fullWidth
                    label="Plan Type"
                    value={currentOrg.plan_type}
                    onChange={(e) =>
                      handleInputChange("plan_type", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 3 }}>
                  <TextField
                    fullWidth
                    label="Max Users"
                    type="number"
                    value={currentOrg.max_users}
                    onChange={(e) =>
                      handleInputChange("max_users", parseInt(e.target.value))
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 3 }}>
                  <TextField
                    fullWidth
                    label="Storage Limit (GB)"
                    type="number"
                    value={currentOrg.storage_limit_gb}
                    onChange={(e) =>
                      handleInputChange(
                        "storage_limit_gb",
                        parseInt(e.target.value),
                      )
                    }
                    disabled={!editing}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 3 }}>
                  <TextField
                    fullWidth
                    label="Currency"
                    value={currentOrg.currency}
                    onChange={(e) =>
                      handleInputChange("currency", e.target.value)
                    }
                    disabled={!editing}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Reset Password Confirmation Dialog */}
      <Dialog open={openResetDialog} onClose={() => setOpenResetDialog(false)}>
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to reset the password for this organization's
            admin? The new password will be emailed and also shown here for
            manual sharing.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenResetDialog(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleResetPassword} color="secondary">
            Reset
          </Button>
        </DialogActions>
      </Dialog>
      {/* Password Display Snackbar */}
      <Snackbar
        open={resetSnackbarOpen}
        autoHideDuration={null}
        onClose={() => setResetSnackbarOpen(false)}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        action={
          <Button
            color="secondary"
            size="small"
            onClick={() => setResetSnackbarOpen(false)}
          >
            Close
          </Button>
        }
      >
        <Alert severity="info" onClose={() => setResetSnackbarOpen(false)}>
          New Password: {resetPassword} (Copy this for manual sharing)
        </Alert>
      </Snackbar>
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
      >
        <DialogTitle>Delete License</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this organization's license? This
            action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </ProtectedPage>

  );
};
export default OrganizationDetailPage;
