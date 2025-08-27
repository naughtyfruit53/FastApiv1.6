// frontend/src/components/CreateOrganizationLicenseModal.tsx

'use client';

import React, { useState, useEffect } from 'react';
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
  Divider,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { organizationService } from '../services/organizationService'; // Adjust if needed
import { authService } from '../services/authService'; // Add this import
import { usePincodeLookup } from '../hooks/usePincodeLookup';

interface CreateOrganizationLicenseModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: (result: any) => void;
}

interface LicenseFormData {
  organization_name: string;
  superadmin_email: string;
  primary_phone: string;
  address1: string;
  pin_code: string;
  city: string;
  state: string;
  state_code: string;
  gst_number?: string;
  max_users: number;
}

// Indian states for dropdown selection
const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir',
  'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
  'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands',
  'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Lakshadweep',
  'Delhi', 'Puducherry', 'Ladakh'
];

// State to GST state code mapping
const stateToCodeMap: { [key: string]: string } = {
  'Andhra Pradesh': '37',
  'Arunachal Pradesh': '12',
  'Assam': '18',
  'Bihar': '10',
  'Chhattisgarh': '22',
  'Goa': '30',
  'Gujarat': '24',
  'Haryana': '06',
  'Himachal Pradesh': '02',
  'Jammu and Kashmir': '01',
  'Jharkhand': '20',
  'Karnataka': '29',
  'Kerala': '32',
  'Madhya Pradesh': '23',
  'Maharashtra': '27',
  'Manipur': '14',
  'Meghalaya': '17',
  'Mizoram': '15',
  'Nagaland': '13',
  'Odisha': '21',
  'Punjab': '03',
  'Rajasthan': '08',
  'Sikkim': '11',
  'Tamil Nadu': '33',
  'Telangana': '36',
  'Tripura': '16',
  'Uttar Pradesh': '09',
  'Uttarakhand': '05',
  'West Bengal': '19',
  'Andaman and Nicobar Islands': '35',
  'Chandigarh': '04',
  'Dadra and Nagar Haveli and Daman and Diu': '26',
  'Lakshadweep': '31',
  'Delhi': '07',
  'Puducherry': '34',
  'Ladakh': '38',
};

const CreateOrganizationLicenseModal: React.FC<CreateOrganizationLicenseModalProps> = ({
  open,
  onClose,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<any | null>(null);
  const [moduleDialogOpen, setModuleDialogOpen] = useState(false);
  const [licenseActivationOpen, setLicenseActivationOpen] = useState(false);
  const [activationPeriod, setActivationPeriod] = useState<'month' | 'year' | 'perpetual'>('year');
  const [selectedModules, setSelectedModules] = useState({
    "CRM": true,
    "ERP": true,
    "HR": true,
    "Inventory": true,
    "Service": true,
    "Analytics": true,
    "Finance": true
  });
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm<LicenseFormData>({
    defaultValues: {
      max_users: 5, // Default value
    },
  });

  // Use the enhanced pincode lookup hook
  const { lookupPincode, pincodeData, loading: pincodeLoading, error: pincodeError } = usePincodeLookup();

  const pin_code = watch('pin_code');
  const state = watch('state');

  // Auto-populate city, state, and state_code when pin code changes
  useEffect(() => {
    if (pin_code && pin_code.length === 6 && /^\d{6}$/.test(pin_code)) {
      lookupPincode(pin_code);
    }
  }, [pin_code, lookupPincode]);

  // Auto-populate fields when pincode data is fetched
  useEffect(() => {
    if (pincodeData) {
      setValue('city', pincodeData.city, { shouldValidate: true });
      setValue('state', pincodeData.state, { shouldValidate: true });
      setValue('state_code', pincodeData.state_code, { shouldValidate: true });
    }
  }, [pincodeData, setValue]);

  // Auto-populate state_code when state changes
  useEffect(() => {
    if (state) {
      const code = stateToCodeMap[state];
      if (code) {
        setValue('state_code', code, { shouldValidate: true });
      }
    }
  }, [state, setValue]);

  const handleClose = () => {
    reset();
    setError(null);
    setSuccess(null);
    onClose();
  };

  const onSubmit = async (data: LicenseFormData) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    console.log('[LicenseModal] Starting license creation process');
    console.log('[LicenseModal] Current auth state before license creation:', {
      hasToken: !!localStorage.getItem('token'),
      userRole: localStorage.getItem('user_role'),
      timestamp: new Date().toISOString(),
      note: 'Organization context managed by backend session'
    });

    // Validate required fields that might not be caught by form validation
    if (!data.state) {
      setError('Please select a state');
      setLoading(false);
      return;
    }

    // Prepare the data for submission
    const submissionData = {
      organization_name: data.organization_name.trim(),
      superadmin_email: data.superadmin_email.trim(),
      primary_phone: data.primary_phone?.trim(),
      address1: data.address1.trim(),
      pin_code: data.pin_code.trim(),
      city: data.city.trim(),
      state: data.state.trim(),
      state_code: data.state_code.trim(),
      gst_number: data.gst_number?.trim() || undefined, // Optional field
      max_users: data.max_users,
      enabled_modules: selectedModules, // Include selected modules
    };

    console.log('[LicenseModal] Submitting license data:', submissionData);

    try {
      const result = await organizationService.createLicense(submissionData);
      if (!result || typeof result !== 'object') {
        throw new Error('Invalid response from server');
      }
      console.log('[LicenseModal] License creation successful:', {
        organizationName: result.organization_name,
        subdomain: result.subdomain,
        adminEmail: result.superadmin_email
      });
      
      // Verify current user's session is still intact
      console.log('[LicenseModal] Verifying session after license creation:', {
        hasToken: !!localStorage.getItem('token'),
        userRole: localStorage.getItem('user_role'),
        timestamp: new Date().toISOString(),
        note: 'Organization context managed by backend session'
      });
      
      setSuccess(result);
      if (onSuccess) {
        onSuccess(result);
      }
      
      // Show license activation dialog after successful creation
      setLicenseActivationOpen(true);
      
      // IMPORTANT: Auto-login functionality removed to preserve current user's session
      // The current super admin remains logged in and sees the success message
      console.log('[LicenseModal] License creation complete - current user session preserved');
    } catch (err: any) {
      console.error('[LicenseModal] License creation error:', err);
      console.error('[LicenseModal] Error details:', {
        message: err.message,
        status: err.status,
        userMessage: err.userMessage
      });
      setError(err.message || 'Failed to create organization license. Please check if RBAC initialization succeeded or run init_rbac_for_org.py manually.');
    } finally {
      setLoading(false);
    }
  };

  const handleModuleChange = (module: string, enabled: boolean) => {
    setSelectedModules(prev => ({
      ...prev,
      [module]: enabled
    }));
  };

  const handleOpenModuleDialog = () => {
    setModuleDialogOpen(true);
  };

  const handleCloseModuleDialog = () => {
    setModuleDialogOpen(false);
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
        <DialogTitle sx={{ 
          textAlign: 'center', 
          fontWeight: 'bold',
          pb: 1,
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}>
          Create Organization License
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
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'success.dark' }}>
                  🎉 License Created Successfully!
                </Typography>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'success.50', borderRadius: 1, border: '1px solid', borderColor: 'success.200' }}>
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
                    <strong>Temporary Password:</strong> 
                    <Box component="span" sx={{ 
                      ml: 1, 
                      p: 0.5, 
                      bgcolor: 'warning.100', 
                      borderRadius: 0.5,
                      fontFamily: 'monospace',
                      fontSize: '0.9em'
                    }}>
                      {success.temp_password}
                    </Box>
                  </Typography>
                </Box>
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    ⚠️ Important: Save these credentials immediately!
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    This password will not be displayed again. The admin must change it on first login.
                  </Typography>
                </Alert>
              </Alert>
            )}

            {!success && (
              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Organization Information Section */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ 
                    mb: 2, 
                    fontWeight: 'bold', 
                    color: 'primary.main',
                    borderBottom: '2px solid',
                    borderColor: 'primary.main',
                    pb: 0.5
                  }}>
                    📋 Organization Information
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid size={12}>
                      <TextField
                        fullWidth
                        label="Organization Name"
                        placeholder="Enter your organization's full legal name"
                        {...register('organization_name', {
                          required: 'Organization name is required',
                          minLength: {
                            value: 3,
                            message: 'Organization name must be at least 3 characters'
                          }
                        })}
                        error={!!errors.organization_name}
                        helperText={errors.organization_name?.message || 'This will be used for official documents and branding'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Primary/Admin Email"
                        type="email"
                        placeholder="admin@yourorganization.com"
                        {...register('superadmin_email', {
                          required: 'Primary email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Please enter a valid email address'
                          }
                        })}
                        error={!!errors.superadmin_email}
                        helperText={errors.superadmin_email?.message || 'This will be the admin login email'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Primary Phone Number"
                        placeholder="+91-1234567890"
                        {...register('primary_phone', {
                          required: 'Primary phone is required',
                          pattern: {
                            value: /^[+\0-9\s()-]{10,15}$/,
                            message: 'Enter a valid phone number (10-15 digits)'
                          }
                        })}
                        error={!!errors.primary_phone}
                        helperText={errors.primary_phone?.message || 'Include country code for international numbers'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="Maximum Users"
                        type="number"
                        inputProps={{ min: 1, max: 1000 }}
                        {...register('max_users', {
                          required: 'Maximum users is required',
                          min: {
                            value: 1,
                            message: 'Must allow at least 1 user'
                          },
                          max: {
                            value: 1000,
                            message: 'Cannot exceed 1000 users'
                          }
                        })}
                        error={!!errors.max_users}
                        helperText={errors.max_users?.message || 'Number of users allowed in this organization'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="GST Number (Optional)"
                        placeholder="22AAAAA0000A1Z5"
                        {...register('gst_number', {
                          pattern: {
                            value: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
                            message: 'Invalid GST format (15 characters: 22AAAAA0000A1Z5)'
                          }
                        })}
                        error={!!errors.gst_number}
                        helperText={errors.gst_number?.message || 'Leave empty if not applicable'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                  </Grid>
                </Box>

                {/* Address Information Section */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ 
                    mb: 2, 
                    fontWeight: 'bold', 
                    color: 'secondary.main',
                    borderBottom: '2px solid',
                    borderColor: 'secondary.main',
                    pb: 0.5
                  }}>
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
                        {...register('address1', {
                          required: 'Address is required',
                          minLength: {
                            value: 10,
                            message: 'Please provide a complete address'
                          }
                        })}
                        error={!!errors.address1}
                        helperText={errors.address1?.message || 'Include building name, street, and locality'}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 4 }}>
                      <TextField
                        fullWidth
                        label="PIN Code"
                        placeholder="123456"
                        {...register('pin_code', {
                          required: 'PIN code is required',
                          pattern: {
                            value: /^\d{6}$/,
                            message: 'PIN code must be exactly 6 digits'
                          }
                        })}
                        error={!!errors.pin_code || !!pincodeError}
                        helperText={
                          pincodeLoading ? 'Looking up location...' :
                          errors.pin_code?.message || pincodeError || 
                          '6-digit postal code (automatically fetches city & state)'
                        }
                        disabled={loading || pincodeLoading}
                        variant="outlined"
                        InputProps={{
                          endAdornment: pincodeLoading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', pr: 1 }}>
                              <CircularProgress size={20} />
                            </Box>
                          ) : null
                        }}
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 4 }}>
                      <TextField
                        fullWidth
                        label="City"
                        placeholder="Enter city name"
                        {...register('city', { 
                          required: 'City is required',
                          minLength: {
                            value: 2,
                            message: 'City name must be at least 2 characters'
                          }
                        })}
                        error={!!errors.city}
                        helperText={errors.city?.message || (pincodeData ? 'Auto-filled from PIN code' : 'Will be auto-filled when PIN is entered')}
                        disabled={loading}
                        variant="outlined"
                      />
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 4 }}>
                      <FormControl fullWidth error={!!errors.state} variant="outlined">
                        <InputLabel>State</InputLabel>
                        <Select
                          label="State"
                          value={watch('state') || ''}
                          onChange={(e) => setValue('state', e.target.value, { shouldValidate: true })}
                          disabled={loading}
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
                        <Typography variant="caption" color={errors.state ? 'error' : 'text.secondary'} sx={{ mt: 0.5, ml: 2 }}>
                          {errors.state?.message || (pincodeData ? 'Auto-filled from PIN code' : 'Will be auto-filled when PIN is entered')}
                        </Typography>
                      </FormControl>
                    </Grid>
                    
                    <Grid size={{ xs: 12, md: 6 }}>
                      <TextField
                        fullWidth
                        label="State Code"
                        {...register('state_code', {
                          required: 'State code is required',
                          pattern: {
                            value: /^\d{2}$/,
                            message: 'State code must be 2 digits'
                          }
                        })}
                        error={!!errors.state_code}
                        helperText={errors.state_code?.message || 'Automatically set based on selected state'}
                        disabled={loading}
                        variant="outlined"
                        InputProps={{
                          readOnly: true,
                        }}
                      />
                    </Grid>
                  </Grid>
                </Box>

                {/* Information Notice */}

              </form>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid', borderColor: 'divider' }}>
          <Button 
            onClick={handleClose} 
            disabled={loading}
            variant="outlined"
            size="large"
            sx={{ minWidth: 120 }}
          >
            {success ? 'Close' : 'Cancel'}
          </Button>
          {!success && (
            <>
              <Button
                onClick={handleOpenModuleDialog}
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
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {loading ? 'Creating...' : 'Create License'}
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Module Selection Dialog */}
      <Dialog 
        open={moduleDialogOpen} 
        onClose={handleCloseModuleDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Module Selection for New Organization
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Select which modules should be enabled for this organization. All modules are enabled by default.
          </Typography>
          <FormGroup>
            {Object.entries(selectedModules).map(([module, enabled]) => (
              <FormControlLabel
                key={module}
                control={
                  <Checkbox
                    checked={enabled}
                    onChange={(e) => handleModuleChange(module, e.target.checked)}
                    color="primary"
                  />
                }
                label={module}
              />
            ))}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModuleDialog}>
            Done
          </Button>
        </DialogActions>
      </Dialog>

      {/* License Activation Dialog */}
      <Dialog 
        open={licenseActivationOpen} 
        onClose={() => setLicenseActivationOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Activate License
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3 }}>
            The organization license has been created successfully. Please set the license activation period:
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="activation-period-label">License Period</InputLabel>
            <Select
              labelId="activation-period-label"
              value={activationPeriod}
              label="License Period"
              onChange={(e) => setActivationPeriod(e.target.value as 'month' | 'year' | 'perpetual')}
            >
              <MenuItem value="month">1 Month</MenuItem>
              <MenuItem value="year">1 Year</MenuItem>
              <MenuItem value="perpetual">Perpetual</MenuItem>
            </Select>
          </FormControl>
          
          {success && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
              <Typography variant="body2" color="success.dark">
                <strong>Organization:</strong> {success.organization_name}<br/>
                <strong>Subdomain:</strong> {success.subdomain}<br/>
                <strong>Admin Email:</strong> {success.superadmin_email}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLicenseActivationOpen(false)}>
            Skip
          </Button>
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
    </>
  );
};

export default CreateOrganizationLicenseModal;