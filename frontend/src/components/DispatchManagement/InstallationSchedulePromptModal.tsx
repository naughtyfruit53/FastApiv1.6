'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  TextField,
  Alert,
  Grid,
  InputLabel,
  Select,
  MenuItem,
  Divider
} from '@mui/material';
import {
  Build as InstallationIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { dispatchService, InstallationJobCreate } from '../../services/dispatchService';
import { INSTALLATION_JOB_PRIORITIES } from '../../types/dispatch.types';

interface InstallationSchedulePromptModalProps {
  open: boolean;
  onClose: () => void;
  onSave: () => void;
  dispatchOrderId?: number;
  customerId?: number;
  customerName?: string;
  deliveryAddress?: string;
}

const InstallationSchedulePromptModal: React.FC<InstallationSchedulePromptModalProps> = ({
  open,
  onClose,
  onSave,
  dispatchOrderId,
  customerId,
  customerName,
  deliveryAddress
}) => {
  const [createSchedule, setCreateSchedule] = useState<string>('yes');
  const [scheduledDate, setScheduledDate] = useState<Date | null>(null);
  const [priority, setPriority] = useState<keyof typeof INSTALLATION_JOB_PRIORITIES>('medium');
  const [estimatedDuration, setEstimatedDuration] = useState<number>(2);
  const [installationAddress, setInstallationAddress] = useState<string>(deliveryAddress || '');
  const [contactPerson, setContactPerson] = useState<string>('');
  const [contactNumber, setContactNumber] = useState<string>('');
  const [installationNotes, setInstallationNotes] = useState<string>('');
  const [assignedTechnician, setAssignedTechnician] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (createSchedule === 'no') {
      onClose();
      return;
    }

    if (!dispatchOrderId || !customerId) {
      setError('Missing required dispatch order or customer information');
      return;
    }

    if (!installationAddress.trim()) {
      setError('Installation address is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const installationJobData: InstallationJobCreate = {
        dispatch_order_id: dispatchOrderId,
        customer_id: customerId,
        status: 'scheduled',
        priority,
        scheduled_date: scheduledDate?.toISOString() || null,
        estimated_duration_hours: estimatedDuration,
        installation_address: installationAddress.trim(),
        contact_person: contactPerson.trim() || null,
        contact_number: contactNumber.trim() || null,
        installation_notes: installationNotes.trim() || null,
        assigned_technician_id: assignedTechnician ? parseInt(assignedTechnician) : null
      };

      const response = await dispatchService.handleInstallationSchedulePrompt({
        create_installation_schedule: true,
        installation_job: installationJobData
      });

      console.log('Installation job created:', response);
      onSave();
    } catch (err: any) {
      console.error('Error creating installation schedule:', err);
      setError(err.message || 'Failed to create installation schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (createSchedule === 'yes') {
      // User chose to create schedule but clicked cancel, so we skip schedule creation
      dispatchService.handleInstallationSchedulePrompt({
        create_installation_schedule: false
      }).catch(console.error);
    }
    onClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <InstallationIcon color="primary" />
            <Typography variant="h6">
              Create Installation Schedule
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          <Box sx={{ mb: 3 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              A delivery challan or service voucher has been created for {customerName}. 
              Would you like to schedule an installation for the delivered items?
            </Alert>

            <FormControl component="fieldset" sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Do you want to create an installation schedule for this customer?
              </Typography>
              <RadioGroup
                value={createSchedule}
                onChange={(e) => setCreateSchedule(e.target.value)}
                row
              >
                <FormControlLabel
                  value="yes"
                  control={<Radio />}
                  label="Yes, schedule installation"
                />
                <FormControlLabel
                  value="no"
                  control={<Radio />}
                  label="No, skip installation scheduling"
                />
              </RadioGroup>
            </FormControl>

            {createSchedule === 'yes' && (
              <>
                <Divider sx={{ mb: 3 }} />
                
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ScheduleIcon />
                  Installation Details
                </Typography>

                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Priority</InputLabel>
                      <Select
                        value={priority}
                        onChange={(e) => setPriority(e.target.value as keyof typeof INSTALLATION_JOB_PRIORITIES)}
                        label="Priority"
                      >
                        {Object.entries(INSTALLATION_JOB_PRIORITIES).map(([key, value]) => (
                          <MenuItem key={key} value={key}>
                            {value.charAt(0).toUpperCase() + value.slice(1)}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <DateTimePicker
                      label="Scheduled Date & Time"
                      value={scheduledDate}
                      onChange={(newValue) => setScheduledDate(newValue)}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          helperText: 'Select the preferred installation date and time'
                        }
                      }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Estimated Duration (hours)"
                      value={estimatedDuration}
                      onChange={(e) => setEstimatedDuration(parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0.5, step: 0.5 }}
                      helperText="Expected time to complete installation"
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Assigned Technician ID"
                      value={assignedTechnician}
                      onChange={(e) => setAssignedTechnician(e.target.value)}
                      helperText="Optional: Enter technician ID if known"
                      type="number"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Installation Address"
                      value={installationAddress}
                      onChange={(e) => setInstallationAddress(e.target.value)}
                      required
                      helperText="Where the installation will take place"
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Contact Person"
                      value={contactPerson}
                      onChange={(e) => setContactPerson(e.target.value)}
                      helperText="Primary contact for installation"
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Contact Number"
                      value={contactNumber}
                      onChange={(e) => setContactNumber(e.target.value)}
                      helperText="Phone number for coordination"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      label="Installation Notes"
                      value={installationNotes}
                      onChange={(e) => setInstallationNotes(e.target.value)}
                      helperText="Any special instructions or requirements"
                    />
                  </Grid>
                </Grid>
              </>
            )}
          </Box>
        </DialogContent>

        <DialogActions>
          <Button 
            onClick={handleCancel}
            disabled={loading}
          >
            {createSchedule === 'yes' ? 'Cancel' : 'Skip'}
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || (createSchedule === 'yes' && !installationAddress.trim())}
            startIcon={createSchedule === 'yes' ? <InstallationIcon /> : undefined}
          >
            {loading ? 'Creating...' : createSchedule === 'yes' ? 'Create Installation Schedule' : 'Continue'}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default InstallationSchedulePromptModal;