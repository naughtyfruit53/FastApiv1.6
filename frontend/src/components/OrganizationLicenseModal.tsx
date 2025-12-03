// frontend/src/components/OrganizationLicenseModal.tsx
"use client";
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid as Grid,
  Snackbar,
} from "@mui/material";
import { Delete as DeleteIcon, Edit as EditIcon } from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { organizationService } from "../services/organizationService"; // Adjust if needed
import { usePincodeLookup } from "../hooks/usePincodeLookup";
import ModuleSelectionModal from './ModuleSelectionModal'; // Import reusable modal
import { useAuth } from "../context/AuthContext";  // Add this to get user context
import { useRouter } from "next/navigation"; // For redirect after delete
import api from "../utils/api"; // Import api for fetching admin user

interface OrganizationLicenseModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: (_result: any) => void;
  mode: 'create' | 'view' | 'edit'; // New: Mode prop
  selectedOrg?: any; // New: Pre-populated org data for view/edit
}

interface LicenseFormData {
  organization_name: string;
  superadmin_email: string;
  superadmin_full_name: string;
  primary_phone: string;
  address1: string;
  pin_code: string;
  city: string;
  state: string;
  state_code: string;
  gst_number?: string;
  max_users: number;
  subdomain?: string; // Added from [id].tsx
  business_type?: string;
  industry?: string;
  website?: string;
  description?: string;
  country?: string;
  pan_number?: string;
  cin_number?: string;
  plan_type?: string;
  storage_limit_gb?: number;
  timezone?: string;
  currency?: string;
}

// Indian states for dropdown selection
const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jammu and Kashmir",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Lakshadweep",
  "Delhi",
  "Puducherry",
  "Ladakh",
];
// State to GST state code mapping
const stateToCodeMap: { [key: string]: string } = {
  "Andhra Pradesh": "37",
  "Arunachal Pradesh": "12",
  Assam: "18",
  Bihar: "10",
  Chhattisgarh: "22",
  Goa: "30",
  Gujarat: "24",
  Haryana: "06",
  "Himachal Pradesh": "02",
  "Jammu and Kashmir": "01",
  Jharkhand: "20",
  Karnataka: "29",
  Kerala: "32",
  "Madhya Pradesh": "23",
  Maharashtra: "27",
  Manipur: "14",
  Meghalaya: "17",
  Mizoram: "15",
  Nagaland: "13",
  Odisha: "21",
  Punjab: "03",
  Rajasthan: "08",
  Sikkim: "11",
  "Tamil Nadu": "33",
  Telangana: "36",
  Tripura: "16",
  "Uttar Pradesh": "09",
  Uttarakhand: "05",
  "West Bengal": "19",
  "Andaman and Nicobar Islands": "35",
  Chandigarh: "04",
  "Dadra and Nagar Haveli and Daman and Diu": "26",
  Lakshadweep: "31",
  Delhi: "07",
  Puducherry: "34",
  Ladakh: "38",
};
const OrganizationLicenseModal: React.FC<
  OrganizationLicenseModalProps
> = ({ open, onClose, onSuccess, mode: propMode, selectedOrg }) => {
  const { user } = useAuth();  // Add this to get user context
  const router = useRouter(); // For redirect after delete
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<any | null>(null);
  const [moduleDialogOpen, setModuleDialogOpen] = useState(false);
  const [licenseActivationOpen, setLicenseActivationOpen] = useState(false);
  const [activationPeriod, setActivationPeriod] = useState<string>("trial_7"); // Default to 7-day trial
  const [selectedModules, setSelectedModules] = useState<{ [key: string]: boolean }>({
    crm: true,
    erp: true,
    manufacturing: true,
    finance: true,
    service: true,
    hr: true,
    analytics: true
  }); // Pre-ticked object
  const [openResetDialog, setOpenResetDialog] = useState(false); // From [id].tsx
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false); // From [id].tsx
  const [resetPassword, setResetPassword] = useState<string | null>(null); // From [id].tsx
  const [resetSnackbarOpen, setResetSnackbarOpen] = useState(false); // From [id].tsx
  const [adminFullName, setAdminFullName] = useState<string>(''); // New state for fetched full name
  const [internalMode, setInternalMode] = useState<'create' | 'view' | 'edit'>(propMode); // Internal mode for view -> edit switch
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<LicenseFormData>({
    defaultValues: {
      max_users: 5, // Default value
    },
  });
  // Use the enhanced pincode lookup hook
  const {
    lookupPincode,
    pincodeData,
    loading: pincodeLoading,
    error: pincodeError,
  } = usePincodeLookup();
  const pin_code = watch("pin_code");
  const state = watch("state");
  const state_code = watch("state_code");
  // Auto-populate city, state, and state_code when pin code changes
  useEffect(() => {
    if (pin_code && pin_code.length === 6 && /^\d{6}$/.test(pin_code)) {
      lookupPincode(pin_code);
    }
  }, [pin_code, lookupPincode]);
  // Auto-populate fields when pincode data is fetched
  useEffect(() => {
    if (pincodeData) {
      setValue("city", pincodeData.city, { shouldValidate: true });
      setValue("state", pincodeData.state, { shouldValidate: true });
      setValue("state_code", pincodeData.state_code || stateToCodeMap[pincodeData.state.trim()] || '', { shouldValidate: true });
    }
  }, [pincodeData, setValue]);
  // Enhanced state change handler: always set state_code if missing
  useEffect(() => {
    if (state && !state_code) {
      const trimmedState = state.trim();
      const code = stateToCodeMap[trimmedState];
      if (code) {
        setValue("state_code", code, { shouldValidate: true });
      } else {
        setError(`No state code found for "${trimmedState}". Please select a valid state.`);
      }
    }
  }, [state, state_code, setValue]);
  // Fetch admin full name for view/edit modes
  useEffect(() => {
    const fetchAdminFullName = async () => {
      if (selectedOrg?.id && (internalMode === 'view' || internalMode === 'edit')) {
        try {
          const response = await api.get(`/organizations/${selectedOrg.id}/members`, {
            headers: { 'X-Organization-ID': `${selectedOrg.id}` }
          });
          const users = response.data;
          const orgAdmin = users.find((user: any) => user.role === 'org_admin');
          if (orgAdmin) {
            setAdminFullName(orgAdmin.full_name || '');
            setValue("superadmin_full_name", orgAdmin.full_name || '');
          }
        } catch (err: any) {
          setError(err.message || "Failed to fetch admin full name");
        }
      }
    };
    fetchAdminFullName();
  }, [selectedOrg, internalMode, setValue]);
  // Pre-populate form for view/edit modes
  useEffect(() => {
    if (selectedOrg && (internalMode === 'view' || internalMode === 'edit')) {
      reset({
        organization_name: selectedOrg.name || '',
        superadmin_email: selectedOrg.primary_email || '',
        superadmin_full_name: adminFullName, // Use fetched name
        primary_phone: selectedOrg.primary_phone || '',
        address1: selectedOrg.address1 || '',
        pin_code: selectedOrg.pin_code || '',
        city: selectedOrg.city || '',
        state: selectedOrg.state || '',
        state_code: selectedOrg.state_code || '',
        gst_number: selectedOrg.gst_number || '',
        max_users: selectedOrg.max_users || 5,
        subdomain: selectedOrg.subdomain || '',
        business_type: selectedOrg.business_type || '',
        industry: selectedOrg.industry || '',
        website: selectedOrg.website || '',
        description: selectedOrg.description || '',
        country: selectedOrg.country || '',
        pan_number: selectedOrg.pan_number || '',
        cin_number: selectedOrg.cin_number || '',
        plan_type: selectedOrg.plan_type || '',
        storage_limit_gb: selectedOrg.storage_limit_gb || 0,
        timezone: selectedOrg.timezone || '',
        currency: selectedOrg.currency || '',
      });
      // Load modules if available
      if (selectedOrg.enabled_modules) {
        setSelectedModules(selectedOrg.enabled_modules);
      }
    } else if (internalMode === 'create') {
      reset({
        organization_name: '',
        superadmin_email: '',
        superadmin_full_name: '',
        primary_phone: '',
        address1: '',
        pin_code: '',
        city: '',
        state: '',
        state_code: '',
        gst_number: '',
        max_users: 5,
        subdomain: '',
        business_type: '',
        industry: '',
        website: '',
        description: '',
        country: '',
        pan_number: '',
        cin_number: '',
        plan_type: '',
        storage_limit_gb: 0,
        timezone: '',
        currency: '',
      });
      setSelectedModules({
        crm: true,
        erp: true,
        manufacturing: true,
        finance: true,
        service: true,
        hr: true,
        analytics: true
      });
      setAdminFullName('');
    }
  }, [selectedOrg, internalMode, reset, adminFullName]);
  // Reset internalMode when propMode changes (e.g., new open)
  useEffect(() => {
    setInternalMode(propMode);
  }, [propMode]);
  // Force reset for create mode when modal opens
  useEffect(() => {
    if (open && propMode === 'create') {
      reset({
        organization_name: '',
        superadmin_email: '',
        superadmin_full_name: '',
        primary_phone: '',
        address1: '',
        pin_code: '',
        city: '',
        state: '',
        state_code: '',
        gst_number: '',
        max_users: 5,
        subdomain: '',
        business_type: '',
        industry: '',
        website: '',
        description: '',
        country: '',
        pan_number: '',
        cin_number: '',
        plan_type: '',
        storage_limit_gb: 0,
        timezone: '',
        currency: '',
      });
      setSelectedModules({
        crm: true,
        erp: true,
        manufacturing: true,
        finance: true,
        service: true,
        hr: true,
        analytics: true
      });
      setAdminFullName('');
      setError(null);
      setSuccess(null);
    }
  }, [open, propMode, reset]);
  const handleClose = () => {
    reset({
      organization_name: '',
      superadmin_email: '',
      superadmin_full_name: '',
      primary_phone: '',
      address1: '',
      pin_code: '',
      city: '',
      state: '',
      state_code: '',
      gst_number: '',
      max_users: 5,
      subdomain: '',
      business_type: '',
      industry: '',
      website: '',
      description: '',
      country: '',
      pan_number: '',
      cin_number: '',
      plan_type: '',
      storage_limit_gb: 0,
      timezone: '',
      currency: '',
    });
    setError(null);
    setSuccess(null);
    setAdminFullName('');
    setSelectedModules({
      crm: true,
      erp: true,
      manufacturing: true,
      finance: true,
      service: true,
      hr: true,
      analytics: true
    });
    onClose();
  };
  const onSubmit = async (data: LicenseFormData) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    // Enhanced validation before submission
    if (!data.state_code) {
      if (data.state) {
        const code = stateToCodeMap[data.state.trim()];
        if (code) {
          data.state_code = code;
        } else {
          setError("Invalid state selected - no matching state code found.");
          setLoading(false);
          return;
        }
      } else {
        setError("State and state code are required.");
        setLoading(false);
        return;
      }
    }
    // Prepare the data for submission
    const submissionData = {
      ...data,
      organization_name: data.organization_name.trim(),
      superadmin_email: data.superadmin_email.trim(),
      superadmin_full_name: data.superadmin_full_name.trim(),
      primary_phone: data.primary_phone?.trim(),
      address1: data.address1.trim(),
      pin_code: data.pin_code.trim(),
      city: data.city.trim(),
      state: data.state.trim(),
      state_code: data.state_code.trim(),
      gst_number: data.gst_number?.trim() || undefined, // Optional field
      enabled_modules: selectedModules, // Send object {crm: true, ...}
    };
    try {
      let result;
      if (internalMode === 'create') {
        result = await organizationService.createLicense(submissionData);
      } else if (internalMode === 'edit' && selectedOrg?.id) {
        result = await organizationService.updateOrganizationById(selectedOrg.id, submissionData);
      }
      if (!result || typeof result !== "object") {
        throw new Error("Invalid response from server");
      }
      setSuccess(result);
      if (onSuccess) {
        onSuccess(result);
      }
      // Show license activation dialog after successful creation/update
      setLicenseActivationOpen(true);
    } catch (err: any) {
      setError(
        err.message ||
          "Failed to process organization license. Please check if RBAC initialization succeeded or run init_rbac_for_org.py manually.",
      );
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async () => {
    if (selectedOrg?.id) {
      try {
        await organizationService.deleteOrganizationById(selectedOrg.id);
        setOpenDeleteDialog(false);
        handleClose();
        router.push("/admin/manage-organizations"); // Redirect to list
      } catch (err: any) {
        setError(err.message || "Failed to delete organization");
      }
    }
  };
  const handleResetPassword = async () => {
    if (selectedOrg?.primary_email) {
      try {
        const result = await passwordService.adminResetPassword(selectedOrg.primary_email);
        setResetPassword(result.new_password);
        setOpenResetDialog(false);
        setResetSnackbarOpen(true);
      } catch (err: any) {
        setError(err.message || "Failed to reset password");
      }
    }
  };
  const handleStartEdit = () => {
    setInternalMode('edit');
  };
  const isViewMode = internalMode === 'view';
  const isEditMode = internalMode === 'edit';
  const isCreateMode = internalMode === 'create';
  const disabled = loading || isViewMode;
  return (
    <>
      <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
        <DialogTitle
          sx={{
            textAlign: "center",
            fontWeight: "bold",
            pb: 1,
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          {isCreateMode ? 'Create Organization License' : isViewMode ? 'View Organization License' : 'Edit Organization License'}
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Box>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" sx={{ mb: 3 }}>
                <Typography
                  variant="h6"
                  gutterBottom
                  sx={{ fontWeight: "bold", color: "success.dark" }}
                >
                  🎉 License {isCreateMode ? 'Created' : 'Updated'} Successfully!
                </Typography>
                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    bgcolor: "success.50",
                    borderRadius: 1,
                    border: "1px solid",
                    borderColor: "success.200",
                  }}
                >
                  <Typography variant="body2" gutterBottom>
                    <strong>Organization:</strong> {success.organization_name}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Subdomain:</strong> {success.subdomain}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Admin Email:</strong> {success.superadmin_email}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Super Admin Name:</strong> {success.superadmin_full_name}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Temporary Password:</strong>
                    <Box
                      component="span"
                      sx={{
                        ml: 1,
                        p: 0.5,
                        bgcolor: "warning.100",
                        borderRadius: 0.5,
                        fontFamily: "monospace",
                        fontSize: "0.9em",
                      }}
                    >
                      {success.temp_password}
                    </Box>
                  </Typography>
                </Box>
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                    ⚠️ Important: Save these credentials immediately!
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    This password will not be displayed again. The admin must
                    change it on first login.
                  </Typography>
                </Alert>
              </Alert>
            )}
            {!success && (
              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Organization Information Section */}
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      mb: 2,
                      fontWeight: "bold",
                      color: "primary.main",
                      borderBottom: "2px solid",
                      borderColor: "primary.main",
                      pb: 0.5,
                    }}
                  >
                    📋 Organization Information
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid size={12}>
                      <TextField
                        fullWidth
                        label="Organization Name"
                        placeholder="Enter your organization's full legal name"
                        {...register("organization_name", {
                          required: "Organization name is required",
                          minLength: {
                            value: 3,
                            message:
                              "Organization name must be at least 3 characters",
                          },
                        })}
                        error={!!errors.organization_name}
                        helperText={
                          errors.organization_name?.message ||
                          "This will be used for official documents and branding"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Super Admin Full Name"
                        placeholder="John Doe"
                        {...register("superadmin_full_name", {
                          required: "Super admin full name is required",
                          minLength: {
                            value: 3,
                            message: "Full name must be at least 3 characters",
                          },
                        })}
                        error={!!errors.superadmin_full_name}
                        helperText={
                          errors.superadmin_full_name?.message ||
                          "Full name of the organization admin"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Primary/Admin Email"
                        type="email"
                        placeholder="admin@yourorganization.com"
                        {...register("superadmin_email", {
                          required: "Primary email is required",
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: "Please enter a valid email address",
                          },
                        })}
                        error={!!errors.superadmin_email}
                        helperText={
                          errors.superadmin_email?.message ||
                          "This will be the admin login email"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Primary Phone Number"
                        placeholder="+91-1234567890"
                        {...register("primary_phone", {
                          required: "Primary phone is required",
                          pattern: {
                            value: /^[+\0-9\s()-]{10,15}$/,
                            message:
                              "Enter a valid phone number (10-15 digits)",
                          },
                        })}
                        error={!!errors.primary_phone}
                        helperText={
                          errors.primary_phone?.message ||
                          "Include country code for international numbers"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Maximum Users"
                        type="number"
                        inputProps={{ min: 1, max: 1000 }}
                        {...register("max_users", {
                          required: "Maximum users is required",
                          min: {
                            value: 1,
                            message: "Must allow at least 1 user",
                          },
                          max: {
                            value: 1000,
                            message: "Cannot exceed 1000 users",
                          },
                        })}
                        error={!!errors.max_users}
                        helperText={
                          errors.max_users?.message ||
                          "Number of users allowed in this organization"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="GST Number (Optional)"
                        placeholder="22AAAAA0000A1Z5"
                        {...register("gst_number", {
                          pattern: {
                            value:
                              /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
                            message:
                              "Invalid GST format (15 characters: 22AAAAA0000A1Z5)",
                          },
                        })}
                        error={!!errors.gst_number}
                        helperText={
                          errors.gst_number?.message ||
                          "Leave empty if not applicable"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Subdomain"
                        {...register("subdomain")}
                        error={!!errors.subdomain}
                        helperText={errors.subdomain?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Business Type"
                        {...register("business_type")}
                        error={!!errors.business_type}
                        helperText={errors.business_type?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Industry"
                        {...register("industry")}
                        error={!!errors.industry}
                        helperText={errors.industry?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Website"
                        {...register("website")}
                        error={!!errors.website}
                        helperText={errors.website?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="PAN Number"
                        {...register("pan_number")}
                        error={!!errors.pan_number}
                        helperText={errors.pan_number?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="CIN Number"
                        {...register("cin_number")}
                        error={!!errors.cin_number}
                        helperText={errors.cin_number?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Plan Type"
                        {...register("plan_type")}
                        error={!!errors.plan_type}
                        helperText={errors.plan_type?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Storage Limit (GB)"
                        type="number"
                        {...register("storage_limit_gb")}
                        error={!!errors.storage_limit_gb}
                        helperText={errors.storage_limit_gb?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Timezone"
                        {...register("timezone")}
                        error={!!errors.timezone}
                        helperText={errors.timezone?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Currency"
                        {...register("currency")}
                        error={!!errors.currency}
                        helperText={errors.currency?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={12}>
                      <TextField
                        fullWidth
                        label="Description"
                        multiline
                        rows={3}
                        {...register("description")}
                        error={!!errors.description}
                        helperText={errors.description?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                  </Grid>
                </Box>
                {/* Address Information Section */}
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    sx={{
                      mb: 2,
                      fontWeight: "bold",
                      color: "secondary.main",
                      borderBottom: "2px solid",
                      borderColor: "secondary.main",
                      pb: 0.5,
                    }}
                  >
                    🏢 Address Information
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid size={12}>
                      <TextField
                        fullWidth
                        label="Full Address"
                        multiline
                        rows={3}
                        placeholder="Enter complete address including building, street, and area"
                        {...register("address1", {
                          required: "Address is required",
                          minLength: {
                            value: 10,
                            message: "Please provide a complete address",
                          },
                        })}
                        error={!!errors.address1}
                        helperText={
                          errors.address1?.message ||
                          "Include building name, street, and locality"
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <TextField
                        fullWidth
                        label="PIN Code"
                        placeholder="123456"
                        {...register("pin_code", {
                          required: "PIN code is required",
                          pattern: {
                            value: /^\d{6}$/,
                            message: "PIN code must be exactly 6 digits",
                          },
                        })}
                        error={!!errors.pin_code || !!pincodeError}
                        helperText={
                          pincodeLoading
                            ? "Looking up location..."
                            : errors.pin_code?.message ||
                              pincodeError ||
                              "6-digit postal code (automatically fetches city & state)"
                        }
                        disabled={disabled || pincodeLoading}
                        variant="outlined"
                        InputProps={{
                          endAdornment: pincodeLoading ? (
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                pr: 1,
                              }}
                            >
                              <CircularProgress size={20} />
                            </Box>
                          ) : null,
                        }}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <TextField
                        fullWidth
                        label="City"
                        placeholder="Enter city name"
                        {...register("city", {
                          required: "City is required",
                          minLength: {
                            value: 2,
                            message: "City name must be at least 2 characters",
                          },
                        })}
                        error={!!errors.city}
                        helperText={
                          errors.city?.message ||
                          (pincodeData
                            ? "Auto-filled from PIN code"
                            : "Will be auto-filled when PIN is entered")
                        }
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                      <FormControl
                        fullWidth
                        error={!!errors.state}
                        variant="outlined"
                      >
                        <InputLabel>State</InputLabel>
                        <Select
                          label="State"
                          value={watch("state") || ""}
                          onChange={(e) =>
                            setValue("state", e.target.value as string, {
                              shouldValidate: true,
                            })
                          }
                          disabled={disabled}
                        >
                          <MenuItem value="">
                            <em>Select a state</em>
                          </MenuItem>
                          {INDIAN_STATES.map((stateName) => (
                            <MenuItem key={stateName} value={stateName}>
                              {stateName}
                            </MenuItem>
                          ))}
                        </Select>
                        <Typography
                          variant="caption"
                          color={errors.state ? "error" : "text.secondary"}
                          sx={{ mt: 0.5, ml: 2 }}
                        >
                          {errors.state?.message ||
                            (pincodeData
                              ? "Auto-filled from PIN code"
                              : "Will be auto-filled when PIN is entered")}
                        </Typography>
                      </FormControl>
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="State Code"
                        {...register("state_code", {
                          required: "State code is required",
                          pattern: {
                            value: /^\d{2}$/,
                            message: "State code must be 2 digits",
                          },
                        })}
                        error={!!errors.state_code}
                        helperText={
                          errors.state_code?.message ||
                          "Automatically set based on selected state"
                        }
                        disabled={disabled}
                        variant="outlined"
                        InputProps={{
                          readOnly: true,
                        }}
                      />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Country"
                        {...register("country", { required: "Country is required" })}
                        error={!!errors.country}
                        helperText={errors.country?.message}
                        disabled={disabled}
                        variant="outlined"
                      />
                    </Grid>
                  </Grid>
                </Box>
                {/* Information Notice */}
              </form>
            )}
          </Box>
        </DialogContent>
        <DialogActions
          sx={{ p: 3, borderTop: "1px solid", borderColor: "divider" }}
        >
          <Button
            onClick={handleClose}
            disabled={loading}
            variant="outlined"
            size="large"
            sx={{ minWidth: 120 }}
          >
            {success ? "Close" : "Cancel"}
          </Button>
          {!success && (
            <>
              {!isViewMode && (
                <>
                  <Button
                    onClick={() => setModuleDialogOpen(true)}
                    variant="text"
                    disabled={loading}
                    size="large"
                    sx={{ minWidth: 150 }}
                  >
                    Manage Modules
                  </Button>
                  <Button
                    onClick={handleSubmit(onSubmit)}
                    variant="contained"
                    disabled={loading}
                    size="large"
                    sx={{ minWidth: 150 }}
                    startIcon={
                      loading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : null
                    }
                  >
                    {loading ? "Processing..." : isCreateMode ? "Create License" : "Save Changes"}
                  </Button>
                </>
              )}
              {isViewMode && (
                <Button
                  onClick={handleStartEdit}
                  variant="contained"
                  startIcon={<EditIcon />}
                  disabled={loading}
                  size="large"
                  sx={{ minWidth: 150 }}
                >
                  Edit
                </Button>
              )}
            </>
          )}
          {!isCreateMode && isViewMode && (
            <>
              <Button
                onClick={() => setOpenResetDialog(true)}
                variant="outlined"
                color="secondary"
                disabled={loading}
                size="large"
                sx={{ minWidth: 150 }}
              >
                Reset Password
              </Button>
              <Button
                onClick={() => setOpenDeleteDialog(true)}
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                disabled={loading}
                size="large"
                sx={{ minWidth: 150 }}
              >
                Delete License
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
      {loading && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000, // High z-index to overlay everything
          }}
        >
          <Box
            sx={{
              bgcolor: 'background.paper',
              p: 4,
              borderRadius: 2,
              textAlign: 'center',
            }}
          >
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="h6">
              Processing license...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This may take up to 30 seconds. Please wait...
            </Typography>
          </Box>
        </Box>
      )}
      <ModuleSelectionModal
        open={moduleDialogOpen}
        onClose={() => setModuleDialogOpen(false)}
        selectedModules={selectedModules}
        onChange={setSelectedModules}
        isSuperAdmin={user?.is_super_admin}  // Add this prop
      />
      {/* License Activation Dialog */}
      <Dialog
        open={licenseActivationOpen}
        onClose={() => setLicenseActivationOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Activate License</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3 }}>
            The organization license has been {isCreateMode ? 'created' : 'updated'} successfully. Please set
            the license activation period:
          </Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="activation-period-label">License Period</InputLabel>
            <Select
              labelId="activation-period-label"
              value={activationPeriod}
              label="License Period"
              onChange={(e) =>
                setActivationPeriod(
                  e.target.value as string,
                )
              }
            >
              <MenuItem value="trial_7">Trial (7 Days)</MenuItem>
              <MenuItem value="trial_15">Trial (15 Days)</MenuItem>
              <MenuItem value="month_1">1 Month</MenuItem>
              <MenuItem value="month_3">3 Months</MenuItem>
              <MenuItem value="year_1">1 Year</MenuItem>
              <MenuItem value="perpetual">Perpetual</MenuItem>
            </Select>
          </FormControl>
          {success && (
            <Box
              sx={{ mt: 2, p: 2, bgcolor: "success.light", borderRadius: 1 }}
            >
              <Typography variant="body2" color="success.dark">
                <strong>Organization:</strong> {success.organization_name}
                <br />
                <strong>Subdomain:</strong> {success.subdomain}
                <br />
                <strong>Admin Email:</strong> {success.superadmin_email}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLicenseActivationOpen(false)}>Skip</Button>
          <Button
            onClick={() => {
              // Here you would typically make an API call to activate the license
              console.log(`Activating license for ${activationPeriod}`);
              setLicenseActivationOpen(false);
            }}
            variant="contained"
            color="primary"
          >
            Activate License
          </Button>
        </DialogActions>
      </Dialog>
      {/* Reset Password Dialog from [id].tsx */}
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
      {/* Password Display Snackbar from [id].tsx */}
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
      {/* Delete Confirmation Dialog from [id].tsx */}
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
    </>
  );
};
export default OrganizationLicenseModal;
