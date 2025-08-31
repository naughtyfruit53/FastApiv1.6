// frontend/src/components/AddUserDialog.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Grid as Grid,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import { PersonAdd as PersonAddIcon, ExpandMore } from '@mui/icons-material';
import { toast } from 'react-toastify';

interface AddUserDialogProps {
  open: boolean;
  onClose: () => void;
  organizationId: number;
  organizationName: string;
  onSuccess?: () => void;
}

interface UserFormData {
  email: string;
  full_name: string;
  password: string;
  confirm_password: string;
  role: string;
  phone?: string;
  department?: string;
}

const AddUserDialog: React.FC<AddUserDialogProps> = ({
  open,
  onClose,
  organizationId,
  organizationName,
  onSuccess
}) => {
  const [formData, setFormData] = useState<UserFormData>({
    email: '',
    full_name: '',
    password: '',
    confirm_password: '',
    role: 'standard_user',
    phone: '',
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<UserFormData>>({});
  const [assignedModules, setAssignedModules] = useState({
    "CRM": true,
    "ERP": true,
    "HR": true,
    "Inventory": true,
    "Service": true,
    "Analytics": true,
    "Finance": true
  });
  const [currentUserRole, setCurrentUserRole] = useState<string | null>(null);

  const roles = [
    { value: 'standard_user', label: 'Standard User' },
    { value: 'admin', label: 'Admin' },
    { value: 'org_admin', label: 'Organization Admin' }
  ];

  // Check current user role for permission to assign modules
  React.useEffect(() => {
    const role = localStorage.getItem('user_role');
    setCurrentUserRole(role);
  }, []);

  // Check if current user can assign modules (HR role or org admin)
  const canAssignModules = (): boolean => {
    return currentUserRole === 'HR' || currentUserRole === 'org_admin' || currentUserRole === 'admin';
  };

  const handleModuleChange = (module: string, enabled: boolean) => {
    setAssignedModules(prev => ({
      ...prev,
      [module]: enabled
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<UserFormData> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Full name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    // Confirm password validation
    if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    // Role validation
    if (!formData.role) {
      newErrors.role = 'Role is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof UserFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const handleClose = () => {
    setFormData({
      email: '',
      full_name: '',
      password: '',
      confirm_password: '',
      role: 'standard_user',
      phone: '',
      department: ''
    });
    setErrors({});
    setLoading(false);
    onClose();
  };

  const handleAddUser = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);

      const userData = {
        email: formData.email.trim(),
        full_name: formData.full_name.trim(),
        password: formData.password,
        role: formData.role,
        phone: formData.phone?.trim() || undefined,
        department: formData.department?.trim() || undefined,
        organization_id: organizationId
      };

      const response = await fetch('/api/v1/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add user');
      }

      const newUser = await response.json();

      // If current user can assign modules and has permission, update user modules
      if (canAssignModules()) {
        try {
          const moduleResponse = await fetch(`/api/v1/organizations/${organizationId}/users/${newUser.id}/modules`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({ assigned_modules: assignedModules }),
          });

          if (!moduleResponse.ok) {
            console.warn('Failed to assign modules to user, but user was created successfully');
          }
        } catch (moduleError) {
          console.warn('Module assignment failed:', moduleError);
          // Don't fail the entire operation if module assignment fails
        }
      }

      toast.success(`User "${formData.full_name}" added successfully`);
      
      if (onSuccess) {
        onSuccess();
      }
      
      handleClose();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to add user');
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = formData.email && formData.full_name && formData.password && 
                     formData.confirm_password && formData.role &&
                     formData.password === formData.confirm_password;

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <PersonAddIcon color="primary" />
        Add User to {organizationName}
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Add a new user to the organization "{organizationName}". The user will receive 
            login credentials and access based on their assigned role.
          </Typography>
        </Alert>

        <Grid container spacing={2}>
          <Grid size={12}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              error={Boolean(errors.email)}
              helperText={errors.email}
              disabled={loading}
              required
            />
          </Grid>

          <Grid size={12}>
            <TextField
              fullWidth
              label="Full Name"
              value={formData.full_name}
              onChange={(e) => handleInputChange('full_name', e.target.value)}
              error={Boolean(errors.full_name)}
              helperText={errors.full_name}
              disabled={loading}
              required
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              error={Boolean(errors.password)}
              helperText={errors.password || 'Minimum 8 characters'}
              disabled={loading}
              required
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              value={formData.confirm_password}
              onChange={(e) => handleInputChange('confirm_password', e.target.value)}
              error={Boolean(errors.confirm_password)}
              helperText={errors.confirm_password}
              disabled={loading}
              required
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth required error={Boolean(errors.role)}>
              <InputLabel>Role</InputLabel>
              <Select
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
                label="Role"
                disabled={loading}
              >
                {roles.map((role) => (
                  <MenuItem key={role.value} value={role.value}>
                    {role.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              disabled={loading}
            />
          </Grid>

          <Grid size={12}>
            <TextField
              fullWidth
              label="Department"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
              disabled={loading}
            />
          </Grid>
        </Grid>

        {/* Module Assignment Section - Only show for HR role or admins */}
        {canAssignModules() && (
          <>
            <Divider sx={{ my: 3 }} />
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">Module Assignment</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Select which modules this user should have access to:
                </Typography>
                <FormGroup row>
                  {Object.entries(assignedModules).map(([module, enabled]) => (
                    <FormControlLabel
                      key={module}
                      control={
                        <Checkbox
                          checked={enabled}
                          onChange={(e) => handleModuleChange(module, e.target.checked)}
                          color="primary"
                          disabled={loading}
                        />
                      }
                      label={module}
                      sx={{ minWidth: '150px' }}
                    />
                  ))}
                </FormGroup>
              </AccordionDetails>
            </Accordion>
          </>
        )}

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Role Permissions:</strong>
          </Typography>
          <ul>
            <li><strong>Standard User:</strong> Basic access to view and create records</li>
            <li><strong>Admin:</strong> Full access to manage organization data</li>
            <li><strong>Organization Admin:</strong> Complete control including user management</li>
          </ul>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={handleClose} 
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleAddUser}
          variant="contained"
          disabled={!isFormValid || loading}
          startIcon={loading ? <CircularProgress size={16} /> : <PersonAddIcon />}
        >
          {loading ? 'Adding User...' : 'Add User'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddUserDialog;