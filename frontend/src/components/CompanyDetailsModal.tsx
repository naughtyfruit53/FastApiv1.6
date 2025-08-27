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
  Grid as Grid,
  InputAdornment,
  Divider,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { companyService } from '../services/authService';
import { usePincodeLookup } from '../hooks/usePincodeLookup';
import CompanyLogoUpload from './CompanyLogoUpload';

interface CompanyDetailsModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  isRequired?: boolean;
  companyData?: any; // For editing existing company
  mode?: 'create' | 'edit';
}

interface CompanyFormData {
  name: string;
  address1: string;
  address2?: string;
  city: string;
  state: string;
  pin_code: string;
  state_code: string;
  gst_number?: string;
  pan_number?: string;
  contact_number: string;
  email?: string;
}

const CompanyDetailsModal: React.FC<CompanyDetailsModalProps> = ({
  open,
  onClose,
  onSuccess,
  isRequired = false,
  companyData = null,
  mode = 'create'
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string }>({});
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm<CompanyFormData>();

  const { lookupPincode, pincodeData, loading: pincodeLoading, error: pincodeError, clearData } = usePincodeLookup();
  const watchedPincode = watch('pin_code');

  // Load existing company data when in edit mode
  useEffect(() => {
    if (mode === 'edit' && companyData) {
      Object.keys(companyData).forEach(key => {
        if (key in companyData) {
          setValue(key as keyof CompanyFormData, companyData[key]);
        }
      });
    }
  }, [mode, companyData, setValue]);

  // Auto-populate address fields when pincode data is available
  useEffect(() => {
    if (pincodeData) {
      setValue('city', pincodeData.city);
      setValue('state', pincodeData.state);
      setValue('state_code', pincodeData.state_code);
    }
  }, [pincodeData, setValue]);

  // Handle pincode change with debouncing
  useEffect(() => {
    if (watchedPincode && /^\d{6}$/.test(watchedPincode)) {
      const timeoutId = setTimeout(() => {
        lookupPincode(watchedPincode);
      }, 500); // 500ms debounce

      return () => clearTimeout(timeoutId);
    } else {
      clearData();
    }
  }, [watchedPincode, lookupPincode, clearData]);

  const handleClose = () => {
    if (!isRequired || success) {
      reset();
      setError(null);
      setSuccess(false);
      setFieldErrors({});
      clearData();
      onClose();
    }
  };

  const onSubmit = async (data: CompanyFormData) => {
    setLoading(true);
    setError(null);
    setFieldErrors({});

    // Ensure all required fields are properly formatted
    const mappedData = {
      name: data.name.trim(),
      address1: data.address1.trim(),
      address2: data.address2?.trim() || '',
      city: data.city.trim(),
      state: data.state.trim(),
      pin_code: data.pin_code.trim(),
      state_code: data.state_code.trim(),
      gst_number: data.gst_number?.trim() || null,
      pan_number: data.pan_number?.trim() || null,
      contact_number: data.contact_number.trim(),
      email: data.email?.trim() || null,
    };

    try {
      if (mode === 'edit' && companyData?.id) {
        await companyService.updateCompany(companyData.id, mappedData);
      } else {
        await companyService.createCompany(mappedData);
      }
      setSuccess(true);
      if (onSuccess) {
        onSuccess();
      }
      if (!isRequired) {
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    } catch (err: any) {
      if (err.status === 422 && err.response?.data?.detail) {
        const validationErrors = err.response.data.detail;
        const newFieldErrors: { [key: string]: string } = {};
        validationErrors.forEach((validationError: any) => {
          const field = validationError.loc[validationError.loc.length - 1];
          newFieldErrors[field] = validationError.msg;
        });
        setFieldErrors(newFieldErrors);
        setError('Please correct the validation errors below');
      } else {
        setError(err.userMessage || 'Failed to create company details');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      disableEscapeKeyDown={isRequired && !success}
    >
      <DialogTitle>
        {isRequired 
          ? 'Complete Company Information' 
          : mode === 'edit' 
            ? 'Edit Company Details' 
            : 'Company Details'
        }
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {isRequired && !success && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Please complete your company information to continue using the system.
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Company details created successfully!
              {isRequired && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  You can now access all features of the system.
                </Typography>
              )}
            </Alert>
          )}

          {!success && (
            <form onSubmit={handleSubmit(onSubmit)}>
              <Grid container spacing={2}>
                <Grid size={12}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    {...register('name', { required: 'Company name is required' })}
                    error={!!errors.name || !!fieldErrors.name}
                    helperText={errors.name?.message || fieldErrors.name}
                    disabled={loading}
                  />
                </Grid>

                {/* Company Logo Upload */}
                {mode === 'edit' && companyData?.id && (
                  <Grid size={12}>
                    <Divider sx={{ my: 2 }} />
                    <CompanyLogoUpload
                      companyId={companyData.id}
                      currentLogoPath={companyData.logo_path}
                      disabled={loading}
                    />
                    <Divider sx={{ my: 2 }} />
                  </Grid>
                )}

                <Grid size={12}>
                  <TextField
                    fullWidth
                    label="Address Line 1"
                    {...register('address1', { required: 'Address is required' })}
                    error={!!errors.address1 || !!fieldErrors.address1}
                    helperText={errors.address1?.message || fieldErrors.address1}
                    disabled={loading}
                  />
                </Grid>

                <Grid size={12}>
                  <TextField
                    fullWidth
                    label="Address Line 2"
                    {...register('address2')}
                    error={!!fieldErrors.address2}
                    helperText={fieldErrors.address2}
                    disabled={loading}
                  />
                </Grid>

                {/* PIN Code moved to be first after address lines */}
                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="Pin Code"
                    {...register('pin_code', {
                      required: 'Pin code is required',
                      pattern: {
                        value: /^\d{6}$/,
                        message: 'Pin code must be 6 digits'
                      }
                    })}
                    error={!!errors.pin_code || !!fieldErrors.pin_code}
                    helperText={errors.pin_code?.message || fieldErrors.pin_code || (pincodeError && pincodeError)}
                    disabled={loading}
                    InputProps={{
                      endAdornment: pincodeLoading ? (
                        <InputAdornment position="end">
                          <CircularProgress size={16} />
                        </InputAdornment>
                      ) : null,
                    }}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="City"
                    {...register('city', { required: 'City is required' })}
                    error={!!errors.city || !!fieldErrors.city}
                    helperText={errors.city?.message || fieldErrors.city}
                    disabled={loading || !!pincodeData}
                    InputProps={{
                      readOnly: !!pincodeData,
                    }}
                    InputLabelProps={{
                      shrink: !!watch('city') || !!pincodeData, // Force label shrink if value exists or auto-populated
                    }}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 4 }}>
                  <TextField
                    fullWidth
                    label="State"
                    {...register('state', { required: 'State is required' })}
                    error={!!errors.state || !!fieldErrors.state}
                    helperText={errors.state?.message || fieldErrors.state}
                    disabled={loading || !!pincodeData}
                    InputProps={{
                      readOnly: !!pincodeData,
                    }}
                    InputLabelProps={{
                      shrink: !!watch('state') || !!pincodeData, // Force label shrink if value exists or auto-populated
                    }}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
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
                    error={!!errors.state_code || !!fieldErrors.state_code}
                    helperText={errors.state_code?.message || fieldErrors.state_code}
                    disabled={loading || !!pincodeData}
                    InputProps={{
                      readOnly: !!pincodeData,
                    }}
                    InputLabelProps={{
                      shrink: !!watch('state_code') || !!pincodeData, // Force label shrink if value exists or auto-populated
                    }}
                  />
                </Grid>

                {/* Removed Alert for pincode auto-population as per request */}

                {pincodeError && (
                  <Grid size={12}>
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      {pincodeError}
                    </Alert>
                  </Grid>
                )}

                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="GST Number"
                    {...register('gst_number')}
                    error={!!fieldErrors.gst_number}
                    helperText={fieldErrors.gst_number}
                    disabled={loading}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="PAN Number"
                    {...register('pan_number')}
                    error={!!fieldErrors.pan_number}
                    helperText={fieldErrors.pan_number}
                    disabled={loading}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Contact Number"
                    {...register('contact_number', { required: 'Contact number is required' })}
                    error={!!errors.contact_number || !!fieldErrors.contact_number}
                    helperText={errors.contact_number?.message || fieldErrors.contact_number}
                    disabled={loading}
                  />
                </Grid>

                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    {...register('email', {
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    error={!!errors.email || !!fieldErrors.email}
                    helperText={errors.email?.message || fieldErrors.email}
                    disabled={loading}
                  />
                </Grid>
              </Grid>
            </form>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        {!isRequired && (
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
        )}
        {success && isRequired && (
          <Button onClick={handleClose} variant="contained">
            Continue
          </Button>
        )}
        {!success && (
          <Button
            onClick={handleSubmit(onSubmit)}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            Save Company Details
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CompanyDetailsModal;