import React, { useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Grid,
  Alert,
  InputAdornment,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { usePincodeLookup } from '../hooks/usePincodeLookup';
import debounce from 'lodash/debounce';
interface AddShippingAddressModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: any) => Promise<void>;
  loading?: boolean;
}
interface ShippingAddressFormData {
  address1: string;
  address2?: string;
  city: string;
  state: string;
  pin_code: string;
  state_code: string;
  country: string;
}
const AddShippingAddressModal: React.FC<AddShippingAddressModalProps> = ({ 
  open, 
  onClose, 
  onAdd, 
  loading = false 
}) => {
  const { register, handleSubmit, reset, formState: { errors }, setValue, watch } = useForm<ShippingAddressFormData>({
    defaultValues: {
      address1: '',
      address2: '',
      city: '',
      state: '',
      pin_code: '',
      state_code: '',
      country: 'India',
    }
  });
  const { lookupPincode, pincodeData, loading: pincodeLoading, error: pincodeError, clearData } = usePincodeLookup();
  // Auto-populate address fields when pincode data is available
  useEffect(() => {
    if (pincodeData) {
      console.log('Auto-populating fields with PIN data:', pincodeData);
      setValue('city', pincodeData.city, { shouldDirty: true, shouldTouch: true, shouldValidate: true });
      setValue('state', pincodeData.state, { shouldDirty: true, shouldTouch: true, shouldValidate: true });
      setValue('state_code', pincodeData.state_code, { shouldDirty: true, shouldTouch: true, shouldValidate: true });
    }
  }, [pincodeData, setValue]);
  // Debounced lookup function
  const debouncedLookup = useCallback(
    debounce((pin: string) => {
      console.log('Executing debounced lookup for PIN:', pin);
      lookupPincode(pin);
    }, 500),
    [lookupPincode]
  );
  // Handle PIN change
  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const pin = e.target.value;
    console.log('PIN field onChange triggered, value:', pin);
    if (pin && /^\d{6}$/.test(pin)) {
      debouncedLookup(pin);
    } else {
      clearData();
    }
  };
  // Handle form submission
  const onSubmit = async (shippingData: ShippingAddressFormData) => {
    try {
      const cleanData = Object.fromEntries(
        Object.entries(shippingData).filter(([key, value]) => value && value.trim() !== '')
      );
      await onAdd(cleanData);
      reset();
      onClose();
    } catch (error) {
      console.error('Error adding shipping address:', error);
    }
  };
  const handleClose = () => {
    reset();
    clearData();
    onClose();
  };
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">Add Shipping Address</Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 1"
                {...register('address1', { required: 'Address is required' })}
                error={!!errors.address1}
                helperText={errors.address1?.message}
                margin="normal"
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                label="Address Line 2"
                {...register('address2')}
                margin="normal"
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
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
                onChange={handlePinChange}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                fullWidth
                label="City"
                {...register('city', { required: 'City is required' })}
                error={!!errors.city}
                helperText={errors.city?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink: !!watch('city') || !!pincodeData,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <TextField
                fullWidth
                label="State"
                {...register('state', { required: 'State is required' })}
                error={!!errors.state}
                helperText={errors.state?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink: !!watch('state') || !!pincodeData,
                }}
                sx={{
                  '& .MuiInputBase-root': {
                    height: '40px',
                  },
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="State Code"
                {...register('state_code', { required: 'State code is required' })}
                error={!!errors.state_code}
                helperText={errors.state_code?.message}
                margin="normal"
                InputProps={{
                  readOnly: !!pincodeData,
                }}
                InputLabelProps={{
                  shrink: !!watch('state_code') || !!pincodeData,
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Country"
                {...register('country', { required: 'Country is required' })}
                error={!!errors.country}
                helperText={errors.country?.message}
                margin="normal"
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
            {loading ? 'Adding...' : 'Add Address'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
export default AddShippingAddressModal;