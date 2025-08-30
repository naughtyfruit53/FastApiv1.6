// frontend/src/components/AddCommissionModal.tsx

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  CircularProgress,
  Box,
  Grid,
  InputAdornment
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';

interface AddCommissionModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (commissionData: any) => Promise<void>;
  loading?: boolean;
}

interface CommissionFormData {
  sales_person_id: number;
  opportunity_id?: number;
  lead_id?: number;
  commission_type: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount: number;
  commission_date: string;
  payment_status: string;
  notes?: string;
}

const commissionTypes = [
  'percentage',
  'fixed_amount',
  'tiered',
  'bonus'
];

const paymentStatuses = [
  'pending',
  'paid',
  'approved',
  'rejected',
  'on_hold'
];

const AddCommissionModal: React.FC<AddCommissionModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false
}) => {
  const { register, handleSubmit, reset, control, watch, formState: { errors } } = useForm<CommissionFormData>({
    defaultValues: {
      sales_person_id: 0,
      opportunity_id: undefined,
      lead_id: undefined,
      commission_type: 'percentage',
      commission_rate: 0,
      commission_amount: 0,
      base_amount: 0,
      commission_date: new Date().toISOString().split('T')[0],
      payment_status: 'pending',
      notes: ''
    }
  });

  const commissionType = watch('commission_type');
  const baseAmount = watch('base_amount');
  const commissionRate = watch('commission_rate');

  React.useEffect(() => {
    if (open) {
      reset({
        sales_person_id: 0,
        opportunity_id: undefined,
        lead_id: undefined,
        commission_type: 'percentage',
        commission_rate: 0,
        commission_amount: 0,
        base_amount: 0,
        commission_date: new Date().toISOString().split('T')[0],
        payment_status: 'pending',
        notes: ''
      });
    }
  }, [open, reset]);

  // Calculate commission amount automatically for percentage type
  React.useEffect(() => {
    if (commissionType === 'percentage' && baseAmount && commissionRate) {
      const calculatedAmount = (baseAmount * commissionRate) / 100;
      // Don't use setValue here to avoid infinite loops
    }
  }, [commissionType, baseAmount, commissionRate]);

  const onSubmit = async (data: CommissionFormData) => {
    try {
      // Clean and prepare data
      const cleanData = {
        ...data,
        // Ensure numeric fields are properly typed
        sales_person_id: Number(data.sales_person_id),
        opportunity_id: data.opportunity_id ? Number(data.opportunity_id) : null,
        lead_id: data.lead_id ? Number(data.lead_id) : null,
        commission_rate: data.commission_rate ? Number(data.commission_rate) : null,
        commission_amount: data.commission_amount ? Number(data.commission_amount) : null,
        base_amount: Number(data.base_amount)
      };

      // Remove undefined/empty fields
      Object.keys(cleanData).forEach(key => {
        if (cleanData[key as keyof typeof cleanData] === undefined || cleanData[key as keyof typeof cleanData] === '') {
          delete cleanData[key as keyof typeof cleanData];
        }
      });

      await onAdd(cleanData);
      reset();
      onClose();
    } catch (error) {
      console.error('Error adding commission:', error);
    }
  };

  const handleClose = () => {
    if (!loading) {
      reset();
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6" component="div">
          Add New Commission Record
        </Typography>
      </DialogTitle>

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid size={12}>
                <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
                  Commission Details
                </Typography>
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('sales_person_id', { 
                    required: 'Sales person ID is required',
                    min: { value: 1, message: 'Please enter a valid sales person ID' }
                  })}
                  label="Sales Person ID"
                  type="number"
                  fullWidth
                  error={!!errors.sales_person_id}
                  helperText={errors.sales_person_id?.message}
                  disabled={loading}
                  inputProps={{ min: 1 }}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Commission Type</InputLabel>
                  <Controller
                    name="commission_type"
                    control={control}
                    rules={{ required: 'Commission type is required' }}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Commission Type"
                        error={!!errors.commission_type}
                      >
                        {commissionTypes.map((type) => (
                          <MenuItem key={type} value={type}>
                            {type.replace('_', ' ').toUpperCase()}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.commission_type && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                      {errors.commission_type.message}
                    </Typography>
                  )}
                </FormControl>
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('base_amount', { 
                    required: 'Base amount is required',
                    min: { value: 0, message: 'Base amount must be positive' }
                  })}
                  label="Base Amount"
                  type="number"
                  fullWidth
                  error={!!errors.base_amount}
                  helperText={errors.base_amount?.message}
                  disabled={loading}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                  inputProps={{ min: 0, step: 0.01 }}
                />
              </Grid>

              {commissionType === 'percentage' && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    {...register('commission_rate', {
                      min: { value: 0, message: 'Rate must be positive' },
                      max: { value: 100, message: 'Rate cannot exceed 100%' }
                    })}
                    label="Commission Rate"
                    type="number"
                    fullWidth
                    error={!!errors.commission_rate}
                    helperText={errors.commission_rate?.message}
                    disabled={loading}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">%</InputAdornment>,
                    }}
                    inputProps={{ min: 0, max: 100, step: 0.1 }}
                  />
                </Grid>
              )}

              {(commissionType === 'fixed_amount' || commissionType === 'bonus') && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    {...register('commission_amount', {
                      min: { value: 0, message: 'Amount must be positive' }
                    })}
                    label="Commission Amount"
                    type="number"
                    fullWidth
                    error={!!errors.commission_amount}
                    helperText={errors.commission_amount?.message}
                    disabled={loading}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                    inputProps={{ min: 0, step: 0.01 }}
                  />
                </Grid>
              )}

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('commission_date', { 
                    required: 'Commission date is required' 
                  })}
                  label="Commission Date"
                  type="date"
                  fullWidth
                  error={!!errors.commission_date}
                  helperText={errors.commission_date?.message}
                  disabled={loading}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Payment Status</InputLabel>
                  <Controller
                    name="payment_status"
                    control={control}
                    rules={{ required: 'Payment status is required' }}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Payment Status"
                        error={!!errors.payment_status}
                      >
                        {paymentStatuses.map((status) => (
                          <MenuItem key={status} value={status}>
                            {status.replace('_', ' ').toUpperCase()}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.payment_status && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                      {errors.payment_status.message}
                    </Typography>
                  )}
                </FormControl>
              </Grid>

              {/* Reference Fields */}
              <Grid size={12}>
                <Typography variant="h6" color="primary" sx={{ mb: 2, mt: 2 }}>
                  Reference Information (Optional)
                </Typography>
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('opportunity_id')}
                  label="Opportunity ID"
                  type="number"
                  fullWidth
                  disabled={loading}
                  inputProps={{ min: 1 }}
                  helperText="Link to a specific opportunity"
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('lead_id')}
                  label="Lead ID"
                  type="number"
                  fullWidth
                  disabled={loading}
                  inputProps={{ min: 1 }}
                  helperText="Link to a specific lead"
                />
              </Grid>

              <Grid size={12}>
                <TextField
                  {...register('notes')}
                  label="Notes"
                  multiline
                  rows={3}
                  fullWidth
                  disabled={loading}
                  placeholder="Add any additional notes about this commission..."
                />
              </Grid>

              {/* Calculation Display */}
              {commissionType === 'percentage' && baseAmount && commissionRate && (
                <Grid size={12}>
                  <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Calculated Commission Amount
                    </Typography>
                    <Typography variant="h6" color="primary">
                      ${((baseAmount * commissionRate) / 100).toFixed(2)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {commissionRate}% of ${baseAmount}
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button 
            onClick={handleClose} 
            disabled={loading}
            color="inherit"
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Adding...' : 'Add Commission'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddCommissionModal;