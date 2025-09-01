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
  Chip
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
interface AddLeadModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (_data: any) => Promise<void>;
  loading?: boolean;
}
interface LeadFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  source: string;
  status: string;
  score: number;
  estimated_value?: number;
  expected_close_date?: string;
  notes?: string;
}
const leadSources = [
  'Website',
  'Social Media',
  'Email Campaign',
  'Cold Call',
  'Referral',
  'Trade Show',
  'Partner',
  'Advertisement',
  'Direct Mail',
  'Other'
];
const leadStatuses = [
  'new',
  'contacted',
  'qualified',
  'proposal_sent',
  'negotiation',
  'converted',
  'lost',
  'disqualified'
];
const AddLeadModal: React.FC<AddLeadModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false
}) => {
  const { register, handleSubmit, reset, control, formState: { errors } } = useForm<LeadFormData>({
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      company: '',
      job_title: '',
      website: '',
      address: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      source: 'Website',
      status: 'new',
      score: 0,
      estimated_value: 0,
      expected_close_date: '',
      notes: ''
    }
  });
  React.useEffect(() => {
    if (open) {
      reset({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        company: '',
        job_title: '',
        website: '',
        address: '',
        city: '',
        state: '',
        postal_code: '',
        country: '',
        source: 'Website',
        status: 'new',
        score: 0,
        estimated_value: 0,
        expected_close_date: '',
        notes: ''
      });
    }
  }, [open, reset]);
  const onSubmit = async (leadData: LeadFormData) => {
    try {
      // Remove empty fields to match backend schema
      const cleanData = Object.fromEntries(
        Object.entries(leadData).filter(([key, value]) => {
          if (key === 'score' || key === 'estimated_value') {
            return value !== undefined && value !== null;
          }
          return value !== undefined && value !== null && value !== '';
        })
      );
      await onAdd(cleanData);
      reset();
      onClose();
    } catch (error) {
      console.error('Error adding lead:', error);
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
          Add New Lead
        </Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
                  Basic Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('first_name', { 
                    required: 'First name is required',
                    minLength: { value: 2, message: 'First name must be at least 2 characters' }
                  })}
                  label="First Name"
                  fullWidth
                  error={!!errors.first_name}
                  helperText={errors.first_name?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('last_name', { 
                    required: 'Last name is required',
                    minLength: { value: 2, message: 'Last name must be at least 2 characters' }
                  })}
                  label="Last Name"
                  fullWidth
                  error={!!errors.last_name}
                  helperText={errors.last_name?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('email', { 
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address'
                    }
                  })}
                  label="Email"
                  type="email"
                  fullWidth
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('phone')}
                  label="Phone"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              {/* Company Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2, mt: 2 }}>
                  Company Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('company')}
                  label="Company"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('job_title')}
                  label="Job Title"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('website')}
                  label="Website"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              {/* Address Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2, mt: 2 }}>
                  Address Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('address')}
                  label="Address"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('city')}
                  label="City"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('state')}
                  label="State"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('postal_code')}
                  label="Postal Code"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('country')}
                  label="Country"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              {/* Lead Details */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2, mt: 2 }}>
                  Lead Details
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Source</InputLabel>
                  <Controller
                    name="source"
                    control={control}
                    rules={{ required: 'Source is required' }}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Source"
                        error={!!errors.source}
                      >
                        {leadSources.map((source) => (
                          <MenuItem key={source} value={source}>
                            {source}
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.source && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                      {errors.source.message}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Status</InputLabel>
                  <Controller
                    name="status"
                    control={control}
                    rules={{ required: 'Status is required' }}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Status"
                        error={!!errors.status}
                      >
                        {leadStatuses.map((status) => (
                          <MenuItem key={status} value={status}>
                            <Chip 
                              label={status.replace('_', ' ').toUpperCase()} 
                              size="small" 
                              variant="outlined"
                              sx={{ textTransform: 'capitalize' }}
                            />
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.status && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                      {errors.status.message}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('score', {
                    min: { value: 0, message: 'Score must be at least 0' },
                    max: { value: 100, message: 'Score must be at most 100' }
                  })}
                  label="Lead Score (0-100)"
                  type="number"
                  fullWidth
                  error={!!errors.score}
                  helperText={errors.score?.message}
                  disabled={loading}
                  inputProps={{ min: 0, max: 100 }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('estimated_value', {
                    min: { value: 0, message: 'Value must be positive' }
                  })}
                  label="Estimated Value"
                  type="number"
                  fullWidth
                  error={!!errors.estimated_value}
                  helperText={errors.estimated_value?.message}
                  disabled={loading}
                  inputProps={{ min: 0 }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <TextField
                  {...register('expected_close_date')}
                  label="Expected Close Date"
                  type="date"
                  fullWidth
                  disabled={loading}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('notes')}
                  label="Notes"
                  multiline
                  rows={3}
                  fullWidth
                  disabled={loading}
                />
              </Grid>
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
            {loading ? 'Adding...' : 'Add Lead'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
export default AddLeadModal;