// frontend/src/components/AddUserDialog.tsx
import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { Close, Person, Save, Cancel } from "@mui/icons-material";
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api"; // Adjusted path since this is now in components/
import { useAuth } from "../context/AuthContext"; // Adjusted path
import {
  getDisplayRole,
  canManageUsers,
} from "../types/user.types"; // Adjusted path

interface AddUserDialogProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  onAdd: (userData: any) => void; // Callback to handle form submission in parent
  organizationId: number; // Added prop for organization scoping
}

const AddUserDialog: React.FC<AddUserDialogProps> = ({
  open,
  onClose,
  loading,
  onAdd,
  organizationId,
}) => {
  const { user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    email: "",
    full_name: "",
    role: "executive",
    department: "",
    designation: "",
    employee_id: "",
    phone: "",
  });
  // Get user info for authorization
  const canAddUser = canManageUsers(user);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    // Basic validation
    if (!formData.email || !formData.full_name) {
      setError("Please fill in all required fields");
      return;
    }
    // Pass data to parent for mutation (no password included)
    onAdd({ ...formData, organization_id: organizationId });
  };

  const handleInputChange =
    (field: string) =>
    (
      e:
        | React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
        | { target: { value: string } },
    ) => {
      setFormData((prev) => ({
        ...prev,
        [field]: e.target.value,
      }));
    };

  const resetForm = () => {
    setFormData({
      email: "",
      full_name: "",
      role: "executive",
      department: "",
      designation: "",
      employee_id: "",
      phone: "",
    });
    setError(null);
    setSuccess(null);
  };

  // Check authorization
  if (!canAddUser) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Add New User</DialogTitle>
        <DialogContent>
          <Alert severity="error">
            You don&apos;t have permission to add users. Only organization
            administrators can add users.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Add New User
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ position: "absolute", right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {success}
          </Alert>
        )}
        <Paper sx={{ p: 4 }}>
          <form onSubmit={handleSubmit}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{ display: "flex", alignItems: "center" }}
            >
              <Person sx={{ mr: 1 }} />
              User Information
            </Typography>
            <Divider sx={{ mb: 3 }} />
            {/* Basic Information */}
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                gap: 3,
                mb: 3,
              }}
            >
              <TextField
                fullWidth
                label="Email *"
                type="email"
                value={formData.email}
                onChange={handleInputChange("email")}
                required
                helperText="User's login email address (username will be auto-generated)"
              />
              <TextField
                fullWidth
                label="Full Name *"
                value={formData.full_name}
                onChange={handleInputChange("full_name")}
                required
              />
            </Box>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                gap: 3,
                mb: 3,
              }}
            >
              <FormControl fullWidth>
                <InputLabel>Role *</InputLabel>
                <Select
                  value={formData.role}
                  label="Role *"
                  onChange={handleInputChange("role")}
                >
                  <MenuItem value="executive">Executive</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                </Select>
              </FormControl>
            </Box>
            {/* Additional Information */}
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                gap: 3,
                mb: 4,
              }}
            >
              <TextField
                fullWidth
                label="Department"
                value={formData.department}
                onChange={handleInputChange("department")}
              />
              <TextField
                fullWidth
                label="Designation"
                value={formData.designation}
                onChange={handleInputChange("designation")}
              />
            </Box>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                gap: 3,
                mb: 4,
              }}
            >
              <TextField
                fullWidth
                label="Employee ID"
                value={formData.employee_id}
                onChange={handleInputChange("employee_id")}
              />
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={handleInputChange("phone")}
              />
            </Box>
          </form>
        </Paper>
      </DialogContent>
      <DialogActions sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
        <Button
          variant="outlined"
          startIcon={<Cancel />}
          onClick={onClose}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          variant="outlined"
          onClick={resetForm}
          disabled={loading}
        >
          Reset
        </Button>
        <Button
          type="submit"
          variant="contained"
          startIcon={
            loading ? (
              <CircularProgress size={20} />
            ) : (
              <Save />
            )
          }
          onClick={handleSubmit} // Trigger submit on click
          disabled={loading}
        >
          {loading ? "Creating..." : "Create User"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddUserDialog;