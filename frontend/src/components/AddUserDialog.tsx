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
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import { Close, Person, Save, Cancel } from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext"; // Adjusted path
import {
  canManageUsers,
} from "../types/user.types"; // Adjusted path
import organizationService from "../services/organizationService"; // Import to get managers
// To get modules
// NEW: Import userService
import { useSnackbar } from "notistack"; // NEW: For toast notifications (assume notistack is installed)

interface AddUserDialogProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  onAdd: (userData: any) => void; // Callback to handle form submission in parent
  organizationId: number; // Added prop for organization scoping
}

const MODULES = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance", "Mail"];

const SUB_MODULES = {
  CRM: ["Leads", "Contacts", "Opportunities", "Campaigns"],
  ERP: ["Vouchers", "Ledgers", "Reports", "Inventory"],
  HR: ["Employees", "Payroll", "Recruitment", "Performance"],
  Inventory: ["Stock", "Warehouses", "Movements", "Adjustments"],
  Service: ["Tickets", "SLAs", "Technicians", "Feedback"],
  Analytics: ["Dashboards", "Reports", "Forecasting", "AI Insights"],
  Finance: ["Accounts", "Budgets", "Taxes", "Audits"],
  Mail: ["Inbox", "Compose", "Templates", "Rules"]
};

const AddUserDialog: React.FC<AddUserDialogProps> = ({
  open,
  onClose,
  loading,
  onAdd,
  organizationId,
}) => {
  const { user } = useAuth();
  const { enqueueSnackbar } = useSnackbar(); // NEW: For toast notifications
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
    assigned_modules: MODULES.reduce((acc, mod) => ({ ...acc, [mod]: false }), {}),
    reporting_manager_id: null,
    sub_module_permissions: MODULES.reduce((acc, mod) => ({ ...acc, [mod]: [] }), {}),
  });
  // Get user info for authorization
  const canAddUser = canManageUsers(user);
  const isSuperAdmin = user?.role === "super_admin";

  // Modal states
  const [moduleModalOpen, setModuleModalOpen] = useState(false);
  const [executiveModalOpen, setExecutiveModalOpen] = useState(false);

  // Fetch managers for executive dropdown
  const { data: managers } = useQuery({
    queryKey: ["managers", organizationId],
    queryFn: () => organizationService.getOrganizationUsers(organizationId, { role: "manager" }),
    enabled: open,
  });

  // Fetch selected manager's modules when selected
  const [selectedManager, setSelectedManager] = useState(null);
  const { data: managerModules } = useQuery({
    queryKey: ["managerModules", selectedManager],
    queryFn: async () => {
      if (!selectedManager) return {};
      const user = await organizationService.getOrganizationUsers(organizationId, { user_id: selectedManager });
      return user[0]?.assigned_modules || {};
    },
    enabled: !!selectedManager,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    // Basic validation
    if (!formData.email || !formData.full_name) {
      setError("Please fill in all required fields");
      return;
    }
    const username = formData.email.split("@")[0];
    const submitData = { ...formData, username, organization_id: organizationId };
    if (formData.role === "manager") {
      setModuleModalOpen(true); // Open module selection modal
      return;
    } else if (formData.role === "executive") {
      setExecutiveModalOpen(true); // Open executive config modal
      return;
    }
    // For other roles, submit directly
    onAdd(submitData);
  };

  const handleSaveManagerModules = () => {
    if (!Object.values(formData.assigned_modules).some((v) => v)) {
      setError("Select at least one module");
      return;
    }
    setModuleModalOpen(false);
    const username = formData.email.split("@")[0];
    onAdd({ ...formData, username, organization_id: organizationId });
  };

  const handleSaveExecutiveConfig = () => {
    if (!formData.reporting_manager_id) {
      setError("Select a reporting manager");
      return;
    }
    setExecutiveModalOpen(false);
    const username = formData.email.split("@")[0];
    onAdd({ ...formData, username, organization_id: organizationId });
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
      if (field === "reporting_manager_id") {
        setSelectedManager(e.target.value);
      }
    };

  const handleModuleCheckbox = (module: string) => {
    setFormData((prev) => ({
      ...prev,
      assigned_modules: {
        ...prev.assigned_modules,
        [module]: !prev.assigned_modules[module],
      },
    }));
  };

  const handleSubModuleCheckbox = (module: string, subModule: string) => {
    setFormData((prev) => {
      const subs = prev.sub_module_permissions[module] || [];
      const newSubs = subs.includes(subModule)
        ? subs.filter((s) => s !== subModule)
        : [...subs, subModule];
      return {
        ...prev,
        sub_module_permissions: {
          ...prev.sub_module_permissions,
          [module]: newSubs,
        },
      };
    });
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
      assigned_modules: MODULES.reduce((acc, mod) => ({ ...acc, [mod]: false }), {}),
      reporting_manager_id: null,
      sub_module_permissions: MODULES.reduce((acc, mod) => ({ ...acc, [mod]: [] }), {}),
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

  const availableRoles = (() => {
    if (isSuperAdmin) {
      return [
        { value: "super_admin", label: "Super Admin" },
        { value: "org_admin", label: "Org Admin" },
        { value: "management", label: "Management" },
        { value: "manager", label: "Manager" },
        { value: "executive", label: "Executive" },
      ];
    } else if (user?.role === "org_admin") {
      return [
        { value: "org_admin", label: "Org Admin" },
        { value: "management", label: "Management" },
        { value: "manager", label: "Manager" },
        { value: "executive", label: "Executive" },
      ];
    } else if (user?.role === "management") {
      return [
        { value: "management", label: "Management" },
        { value: "manager", label: "Manager" },
        { value: "executive", label: "Executive" },
      ];
    } else if (user?.role === "manager") {
      return [
        { value: "executive", label: "Executive" },
      ];
    } else {
      return [];
    }
  })();

  return (
    <>
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
                    {availableRoles.map((role) => (
                      <MenuItem key={role.value} value={role.value}>
                        {role.label}
                      </MenuItem>
                    ))}
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

      {/* Manager Module Selection Modal */}
      <Dialog open={moduleModalOpen} onClose={() => setModuleModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Select Modules for Manager</DialogTitle>
        <DialogContent>
          {MODULES.map((module) => (
            <FormControlLabel
              key={module}
              control={
                <Checkbox
                  checked={formData.assigned_modules[module]}
                  onChange={() => handleModuleCheckbox(module)}
                />
              }
              label={module}
            />
          ))}
          {error && <Alert severity="error">{error}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModuleModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveManagerModules} variant="contained">Save Modules</Button>
        </DialogActions>
      </Dialog>

      {/* Executive Config Modal */}
      <Dialog open={executiveModalOpen} onClose={() => setExecutiveModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Configure Executive</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Reporting Manager *</InputLabel>
            <Select
              value={formData.reporting_manager_id || ""}
              label="Reporting Manager *"
              onChange={handleInputChange("reporting_manager_id")}
            >
              {managers?.map((manager: any) => (
                <MenuItem key={manager.id} value={manager.id}>
                  {manager.full_name} ({manager.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {selectedManager && managerModules && (
            <Box>
              {Object.entries(managerModules)
                .filter(([_, hasAccess]) => hasAccess)
                .map(([module]) => (
                  <Box key={module} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1">{module} Sub-Modules</Typography>
                    {SUB_MODULES[module].map((sub) => (
                      <FormControlLabel
                        key={sub}
                        control={
                          <Checkbox
                            checked={formData.sub_module_permissions[module]?.includes(sub) || false}
                            onChange={() => handleSubModuleCheckbox(module, sub)}
                          />
                        }
                        label={sub}
                      />
                    ))}
                  </Box>
                ))}
            </Box>
          )}
          {error && <Alert severity="error">{error}</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecutiveModalOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveExecutiveConfig} variant="contained">Save Configuration</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AddUserDialog;