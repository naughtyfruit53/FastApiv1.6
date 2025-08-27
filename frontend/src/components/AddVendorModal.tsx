// frontend/src/components/AddVendorModal.tsx

import React, { useEffect, useState, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Grid as Grid,
  Alert,
  InputAdornment,
  Box,
  Paper,
  Chip,
  Tooltip,
  LinearProgress,
  IconButton,
} from '@mui/material';
import { CloudUpload, Description, CheckCircle, Error, Search } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { usePincodeLookup } from '../hooks/usePincodeLookup';  // Assume this is the correct path; adjust if needed
import api from '../lib/api';  // Axios instance for API calls

interface AddVendorModalProps {
  open: boolean;
  onClose: () => void;
  onAdd?: (vendorData: any) => Promise<void>;  // Optional
  loading?: boolean;
  initialName?: string;
}

interface VendorFormData {
  name: string;
  contact_number: string;
  email: string;
  address1: string;
  address2: string;
  city: string;
  state: string;
  pin_code: string;
  gst_number: string;
  pan_number: string;
  state_code: string;
}

const AddVendorModal: React.FC<AddVendorModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false,
  initialName = ''
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [gstFile, setGstFile] = useState<File | null>(null);
  const [gstUploadLoading, setGstUploadLoading] = useState(false);
  const [gstExtractedData, setGstExtractedData] = useState<any>(null);
  const [gstUploadError, setGstUploadError] = useState<string | null>(null);
  const [gstSearchLoading, setGstSearchLoading] = useState(false);

  const { register, handleSubmit, reset, formState: { errors }, setValue, watch } = useForm<VendorFormData>({
    defaultValues: {
      name: initialName,
      contact_number: '',
      email: '',
      address1: '',
      address2: '',
      city: '',
      state: '',
      pin_code: '',
      gst_number: '',
      pan_number: '',
      state_code: '',
    }
  });

  const { lookupPincode, pincodeData, loading: pincodeLoading, error: pincodeError, clearData } = usePincodeLookup();
  const watchedPincode = watch('pin_code');
  const watchedGstNumber = watch('gst_number');

  // Auto-populate form fields when pincode data is available
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

  // Handle GST certificate upload with actual API call
  const handleGstFileUpload = async (file: File) => {
    setGstUploadLoading(true);
    setGstUploadError(null);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Call backend PDF extraction API
      const response = await api.post('/pdf-extraction/extract/vendor', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.success) {
        const extractedData = response.data.extracted_data;
        
        // Auto-populate form fields with processed extracted data
        Object.entries(extractedData).forEach(([key, value]) => {
          if (value) {
            setValue(key as keyof VendorFormData, value as string);
          }
        });
        
        setGstExtractedData(extractedData);
        setGstFile(file);
      } else {
        const errorMessage = (response.data as any)?.detail || 'Extraction failed';
        throw new globalThis.Error(errorMessage);
      }
      
    } catch (error: any) {
      console.error('Error processing GST certificate:', error);
      setGstUploadError(error.response?.data?.detail || 'Failed to process GST certificate. Please try again.');
    } finally {
      setGstUploadLoading(false);
    }
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setGstUploadError('Please upload a PDF file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setGstUploadError('File size should be less than 10MB');
        return;
      }
      handleGstFileUpload(file);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const removeGstFile = () => {
    setGstFile(null);
    setGstExtractedData(null);
    setGstUploadError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGstSearch = async () => {
    if (!watchedGstNumber || !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(watchedGstNumber)) {
      setGstUploadError('Please enter a valid GSTIN');
      return;
    }
    
    setGstSearchLoading(true);
    setGstUploadError(null);
    
    try {
      const response = await api.get(`/gst/search/${watchedGstNumber}`);
      const data = response.data;
      
      // Auto-populate fields from API response
      Object.entries(data).forEach(([key, value]) => {
        if (value) {
          setValue(key as keyof VendorFormData, value as string);
        }
      });
      
    } catch (error: any) {
      setGstUploadError(error.response?.data?.detail || 'Failed to fetch GST details. Please check GSTIN.');
    } finally {
      setGstSearchLoading(false);
    }
  };

  const onSubmit = async (data: VendorFormData) => {
    try {
      // Remove empty fields and exclude unexpected fields like 'is_active'
      const allowedFields = ['name', 'contact_number', 'email', 'address1', 'address2', 'city', 'state', 'pin_code', 'gst_number', 'pan_number', 'state_code'];
      const cleanData = Object.fromEntries(
        Object.entries(data).filter(([key, value]) => allowedFields.includes(key) && value != null && String(value).trim() !== '')
      );
      
      // Direct API call to save vendor
      const response = await api.post('/vendors', cleanData);
      console.log('Vendor added successfully:', response.data);
      
      // Call onAdd if provided and is a function
      if (typeof onAdd === 'function') {
        await onAdd(response.data);
      }
      
      reset();
      onClose();  // Close modal on success
    } catch (error: any) {
      console.error('Error adding vendor:', error);
      // Set more specific error message
      const errorMessage = error.response?.data?.detail || 'Failed to add vendor. Please try again.';
      setGstUploadError(errorMessage);
    }
  };

  const handleClose = () => {
    reset();
    clearData();
    removeGstFile();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">Add New Vendor</Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Vendor Name *"
                {...register('name', { required: 'Vendor name is required' })}
                error={!!errors.name}
                helperText={errors.name?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('name') || !!gstExtractedData?.name,
                }}
              />
            </Grid>
            
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Contact Number"
                {...register('contact_number')}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('contact_number') || !!gstExtractedData?.phone,
                }}
              />
            </Grid>
            
            <Grid size={{ xs: 12, md: 6 }}>
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
                error={!!errors.email}
                helperText={errors.email?.message}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('email') || !!gstExtractedData?.email,
                }}
              />
            </Grid>
            
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="GST Number"
                {...register('gst_number')}
                margin="normal"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {gstSearchLoading ? (
                        <CircularProgress size={16} />
                      ) : (
                        <IconButton
                          onClick={handleGstSearch}
                          disabled={!watchedGstNumber || gstSearchLoading}
                          aria-label="Search GST"
                        >
                          <Search />
                        </IconButton>
                      )}
                    </InputAdornment>
                  ),
                }}
                InputLabelProps={{
                  shrink: !!watch('gst_number') || !!gstExtractedData?.gst_number,
                }}
              />
            </Grid>

            {/* GST Certificate Upload Section */}
            <Grid size={12}>
              <Paper sx={{ p: 2, bgcolor: 'grey.50', border: '1px dashed', borderColor: 'grey.300' }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="subtitle2" color="textSecondary">
                    GST Certificate Upload (Optional)
                  </Typography>
                  <Tooltip title="Upload GST certificate PDF to auto-fill vendor details">
                    <Typography variant="caption" color="textSecondary">
                      PDF Auto-Extract
                    </Typography>
                  </Tooltip>
                </Box>
                
                {!gstFile && !gstUploadLoading && (
                  <Box
                    sx={{
                      border: '2px dashed',
                      borderColor: 'grey.300',
                      borderRadius: 1,
                      p: 3,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': {
                        borderColor: 'primary.main',
                        bgcolor: 'action.hover'
                      }
                    }}
                    onClick={triggerFileUpload}
                  >
                    <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Click to upload GST certificate (PDF only)
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Maximum file size: 10MB
                    </Typography>
                  </Box>
                )}
                
                {gstUploadLoading && (
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <CircularProgress size={40} sx={{ mb: 2 }} />
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Processing GST certificate...
                    </Typography>
                    <LinearProgress sx={{ mt: 1 }} />
                  </Box>
                )}
                
                {gstFile && !gstUploadLoading && (
                  <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Description color="primary" />
                        <Typography variant="body2" fontWeight="medium">
                          {gstFile.name}
                        </Typography>
                        <Chip
                          icon={<CheckCircle />}
                          label="Processed"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Box>
                      <Button
                        size="small"
                        onClick={removeGstFile}
                        color="error"
                        variant="outlined"
                      >
                        Remove
                      </Button>
                    </Box>
                    {gstExtractedData && (
                      <Alert severity="success" sx={{ mt: 1 }}>
                        <Typography variant="caption">
                          Auto-populated: {Object.keys(gstExtractedData).join(', ')}
                        </Typography>
                      </Alert>
                    )}
                  </Box>
                )}
                
                {gstUploadError && (
                  <Alert severity="error" sx={{ mt: 1 }} onClose={() => setGstUploadError(null)}>
                    {gstUploadError}
                  </Alert>
                )}
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  style={{ display: 'none' }}
                  onChange={handleFileInputChange}
                />
              </Paper>
            </Grid>
            
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="PAN Number"
                {...register('pan_number')}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('pan_number') || !!gstExtractedData?.pan_number,
                }}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 1"
                {...register('address1')}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('address1') || !!gstExtractedData?.address1,
                }}
              />
            </Grid>
            
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 2"
                {...register('address2')}
                margin="normal"
                InputLabelProps={{
                  shrink: !!watch('address2') || !!gstExtractedData?.address2,
                }}
              />
            </Grid>
            
            {/* PIN Code moved to be first after address lines */}
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="PIN Code *"
                {...register('pin_code', { 
                  required: 'PIN code is required',
                  pattern: {
                    value: /^\d{6}$/,
                    message: 'Please enter a valid 6-digit PIN code'
                  }
                })}
                error={!!errors.pin_code}
                helperText={errors.pin_code?.message || (pincodeError && pincodeError)}
                margin="normal"
                InputProps={{
                  endAdornment: pincodeLoading ? (
                    <InputAdornment position="end">
                      <CircularProgress size={16} />
                    </InputAdornment>
                  ) : null,
                }}
                InputLabelProps={{
                  shrink: !!watch('pin_code') || !!gstExtractedData?.pin_code,
                }}
              />
            </Grid>
            
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="City"
                {...register('city', { required: 'City is required' })}
                error={!!errors.city}
                helperText={errors.city?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData, // Make readonly when auto-populated
                }}
                InputLabelProps={{
                  shrink: !!watch('city') || !!pincodeData || !!gstExtractedData?.city, // Force label shrink if value exists or auto-populated
                }}
              />
            </Grid>
            
            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="State"
                {...register('state', { required: 'State is required' })}
                error={!!errors.state}
                helperText={errors.state?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData, // Make readonly when auto-populated
                }}
                InputLabelProps={{
                  shrink: !!watch('state') || !!pincodeData || !!gstExtractedData?.state, // Force label shrink if value exists or auto-populated
                }}
              />
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
              <TextField
                fullWidth
                label="State Code"
                {...register('state_code', { required: 'State code is required' })}
                error={!!errors.state_code}
                helperText={errors.state_code?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData, // Make readonly when auto-populated
                }}
                InputLabelProps={{
                  shrink: !!watch('state_code') || !!pincodeData || !!gstExtractedData?.state_code, // Force label shrink if value exists or auto-populated
                }}
              />
            </Grid>

            {pincodeError && (
              <Grid size={12}>
                <Alert severity="warning" sx={{ mt: 1 }}>
                  {pincodeError}
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Adding...' : 'Add Vendor'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddVendorModal;