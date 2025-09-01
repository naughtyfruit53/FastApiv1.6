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
  Chip,
  InputAdornment
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
interface AddOpportunityModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (_data: any) => Promise<void>;
  loading?: boolean;
}
interface OpportunityFormData {
  name: string;
  account_name?: string;
  contact_name?: string;
  amount: number;
  probability: number;
  stage: string;
  source: string;
  close_date: string;
  description?: string;
  next_step?: string;
  lead_id?: number;
  assigned_to_id?: number;
}
const opportunityStages = [
  'prospecting',
  'qualification',
  'needs_analysis',
  'proposal',
  'negotiation',
  'closed_won',
  'closed_lost'
];
const opportunitySources = [
  'Website',
  'Social Media',
  'Email Campaign',
  'Cold Call',
  'Referral',
  'Trade Show',
  'Partner',
  'Lead Conversion',
  'Existing Customer',
  'Other'
];
const AddOpportunityModal: React.FC<AddOpportunityModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false
}) => {
  const { register, handleSubmit, reset, control, formState: { errors } } = useForm<OpportunityFormData>({
    defaultValues: {
      name: '',
      account_name: '',
      contact_name: '',
      amount: 0,
      probability: 50,
      stage: 'prospecting',
      source: 'Website',
      close_date: '',
      description: '',
      next_step: '',
      lead_id: undefined,
      assigned_to_id: undefined
    }
  });
  React.useEffect(() => {
    if (open) {
      reset({
        name: '',
        account_name: '',
        contact_name: '',
        amount: 0,
        probability: 50,
        stage: 'prospecting',
        source: 'Website',
        close_date: '',
        description: '',
        next_step: '',
        lead_id: undefined,
        assigned_to_id: undefined
      });
    }
  }, [open, reset]);
  const onSubmit = async (opportunityData: OpportunityFormData) => {
    try {
      // Remove empty fields to match backend schema
      const cleanData = Object.fromEntries(
        Object.entries(opportunityData).filter(([key, value]) => {
          if (key === 'amount' || key === 'probability') {
            return value !== undefined && value !== null;
          }
          return value !== undefined && value !== null && value !== '';
        })
      );
      await onAdd(cleanData);
      reset();
      onClose();
    } catch (err) {
      console.error(msg, err);
    }
  };
  const handleClose = () => {
    if (!loading) {
      reset();
      onClose();
    }
  };
  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'prospecting': return 'info';
      case 'qualification': return 'warning';
      case 'needs_analysis': return 'secondary';
      case 'proposal': return 'primary';
      case 'negotiation': return 'error';
      case 'closed_won': return 'success';
      case 'closed_lost': return 'default';
      default: return 'default';
    }
  };
  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6" component="div">
          Add New Opportunity
        </Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
                  Opportunity Details
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('name', { 
                    required: 'Opportunity name is required',
                    minLength: { value: 3, message: 'Name must be at least 3 characters' }
                  })}
                  label="Opportunity Name"
                  fullWidth
                  error={!!errors.name}
                  helperText={errors.name?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('account_name')}
                  label="Account Name"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('contact_name')}
                  label="Contact Name"
                  fullWidth
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('amount', { 
                    required: 'Amount is required',
                    min: { value: 0, message: 'Amount must be positive' }
                  })}
                  label="Opportunity Value"
                  type="number"
                  fullWidth
                  error={!!errors.amount}
                  helperText={errors.amount?.message}
                  disabled={loading}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                  inputProps={{ min: 0 }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('probability', {
                    required: 'Probability is required',
                    min: { value: 0, message: 'Probability must be at least 0%' },
                    max: { value: 100, message: 'Probability must be at most 100%' }
                  })}
                  label="Probability"
                  type="number"
                  fullWidth
                  error={!!errors.probability}
                  helperText={errors.probability?.message}
                  disabled={loading}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">%</InputAdornment>,
                  }}
                  inputProps={{ min: 0, max: 100 }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth disabled={loading}>
                  <InputLabel>Stage</InputLabel>
                  <Controller
                    name="stage"
                    control={control}
                    rules={{ required: 'Stage is required' }}
                    render={({ field }) => (
                      <Select
                        {...field}
                        label="Stage"
                        error={!!errors.stage}
                      >
                        {opportunityStages.map((stage) => (
                          <MenuItem key={stage} value={stage}>
                            <Chip 
                              label={stage.replace('_', ' ').toUpperCase()} 
                              size="small" 
                              color={getStageColor(stage) as any}
                              variant="outlined"
                              sx={{ textTransform: 'capitalize' }}
                            />
                          </MenuItem>
                        ))}
                      </Select>
                    )}
                  />
                  {errors.stage && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                      {errors.stage.message}
                    </Typography>
                  )}
                </FormControl>
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
                        {opportunitySources.map((source) => (
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
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('close_date', { 
                    required: 'Expected close date is required' 
                  })}
                  label="Expected Close Date"
                  type="date"
                  fullWidth
                  error={!!errors.close_date}
                  helperText={errors.close_date?.message}
                  disabled={loading}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              {/* Additional Information */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="h6" color="primary" sx={{ mb: 2, mt: 2 }}>
                  Additional Information
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('description')}
                  label="Description"
                  multiline
                  rows={3}
                  fullWidth
                  disabled={loading}
                  placeholder="Describe the opportunity details, requirements, and potential challenges..."
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  {...register('next_step')}
                  label="Next Step"
                  fullWidth
                  disabled={loading}
                  placeholder="What is the next next action required to move this opportunity forward?"
                />
              </Grid>
              {/* Optional Reference Fields */}
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('lead_id')}
                  label="Lead ID (if converted from lead)"
                  type="number"
                  fullWidth
                  disabled={loading}
                  inputProps={{ min: 1 }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  {...register('assigned_to_id')}
                  label="Assigned To (User ID)"
                  type="number"
                  fullWidth
                  disabled={loading}
                  inputProps={{ min: 1 }}
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
            {loading ? 'Adding...' : 'Add Opportunity'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
export default AddOpportunityModal;