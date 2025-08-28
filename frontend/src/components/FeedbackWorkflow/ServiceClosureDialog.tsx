'use client';

import React, { useState } from 'react';
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
  Box,
  Typography,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  Card,
  CardContent,
  Chip,
  FormControlLabel,
  Switch,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  Assignment as AssignmentIcon,
  VerifiedUser as VerifiedUserIcon,
  Lock as LockIcon
} from '@mui/icons-material';

interface ServiceClosureDialogProps {
  open: boolean;
  onClose: () => void;
  installationJobId: number;
  completionRecordId?: number;
  customerFeedbackId?: number;
  onSubmit: (closureData: any) => Promise<void>;
  currentClosure?: any;
  userRole: string;
}

const CLOSURE_REASONS = [
  { value: 'completed', label: 'Service Completed Successfully', icon: CheckCircleIcon, color: 'success' },
  { value: 'cancelled', label: 'Service Cancelled', icon: CancelIcon, color: 'error' },
  { value: 'customer_request', label: 'Customer Request', icon: AssignmentIcon, color: 'info' },
  { value: 'no_show', label: 'Customer No-Show', icon: WarningIcon, color: 'warning' }
];

const CLOSURE_STATUS_CONFIG = {
  pending: { label: 'Pending', color: 'warning', icon: WarningIcon },
  approved: { label: 'Approved', color: 'info', icon: VerifiedUserIcon },
  closed: { label: 'Closed', color: 'success', icon: CheckCircleIcon },
  reopened: { label: 'Reopened', color: 'error', icon: CancelIcon }
};

export const ServiceClosureDialog: React.FC<ServiceClosureDialogProps> = ({
  open,
  onClose,
  installationJobId,
  completionRecordId,
  customerFeedbackId,
  onSubmit,
  currentClosure,
  userRole
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [action, setAction] = useState<'create' | 'approve' | 'close' | 'reopen'>('create');
  const [formData, setFormData] = useState({
    closure_reason: 'completed',
    closure_notes: '',
    requires_manager_approval: true,
    approval_notes: '',
    final_closure_notes: '',
    escalation_required: false,
    escalation_reason: '',
    reopening_reason: ''
  });
  const [error, setError] = useState<string | null>(null);

  const isManager = userRole === 'manager' || userRole === 'admin';
  const canApprove = isManager && currentClosure?.closure_status === 'pending';
  const canClose = isManager && (currentClosure?.closure_status === 'approved' || currentClosure?.closure_status === 'pending');
  const canReopen = isManager && currentClosure?.closure_status === 'closed';

  const handleTextChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSelectChange = (field: string) => (event: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSwitchChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.checked
    }));
  };

  const getStepContent = () => {
    if (!currentClosure) {
      return 0; // Create new closure
    }
    
    switch (currentClosure.closure_status) {
      case 'pending':
        return 1;
      case 'approved':
        return 2;
      case 'closed':
        return 3;
      case 'reopened':
        return 1; // Back to pending
      default:
        return 0;
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);
    
    try {
      let submitData: any;
      
      switch (action) {
        case 'create':
          submitData = {
            installation_job_id: installationJobId,
            completion_record_id: completionRecordId,
            customer_feedback_id: customerFeedbackId,
            closure_reason: formData.closure_reason,
            closure_notes: formData.closure_notes,
            requires_manager_approval: formData.requires_manager_approval,
            escalation_required: formData.escalation_required,
            escalation_reason: formData.escalation_required ? formData.escalation_reason : undefined
          };
          break;
        
        case 'approve':
          submitData = {
            action: 'approve',
            approval_notes: formData.approval_notes
          };
          break;
        
        case 'close':
          submitData = {
            action: 'close',
            final_closure_notes: formData.final_closure_notes
          };
          break;
        
        case 'reopen':
          submitData = {
            action: 'reopen',
            reopening_reason: formData.reopening_reason
          };
          break;
      }
      
      await onSubmit(submitData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to process service closure');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      closure_reason: 'completed',
      closure_notes: '',
      requires_manager_approval: true,
      approval_notes: '',
      final_closure_notes: '',
      escalation_required: false,
      escalation_reason: '',
      reopening_reason: ''
    });
    setAction('create');
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const getDialogTitle = () => {
    if (currentClosure) {
      switch (action) {
        case 'approve':
          return 'Approve Service Closure';
        case 'close':
          return 'Close Service Ticket';
        case 'reopen':
          return 'Reopen Service Ticket';
        default:
          return 'Service Closure Details';
      }
    }
    return 'Create Service Closure';
  };

  const getSubmitButtonText = () => {
    switch (action) {
      case 'approve':
        return 'Approve Closure';
      case 'close':
        return 'Close Service';
      case 'reopen':
        return 'Reopen Service';
      default:
        return 'Create Closure Request';
    }
  };

  const renderWorkflowStepper = () => {
    const steps = [
      'Closure Requested',
      'Manager Review',
      'Service Closed'
    ];

    const activeStep = getStepContent();

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Closure Workflow
        </Typography>
        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Closure Requested</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                Service closure request has been created and is pending review.
              </Typography>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Manager Review</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                Manager is reviewing the closure request and customer feedback.
              </Typography>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Service Closed</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                Service has been officially closed and archived.
              </Typography>
            </StepContent>
          </Step>
        </Stepper>
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      scroll="paper"
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <AssignmentIcon color="primary" />
          <Typography variant="h6">{getDialogTitle()}</Typography>
          {currentClosure && (
            <Chip
              size="small"
              label={CLOSURE_STATUS_CONFIG[currentClosure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.label}
              color={CLOSURE_STATUS_CONFIG[currentClosure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.color as any}
              icon={React.createElement(CLOSURE_STATUS_CONFIG[currentClosure.closure_status as keyof typeof CLOSURE_STATUS_CONFIG]?.icon)}
            />
          )}
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {currentClosure && renderWorkflowStepper()}

        <Grid container spacing={3}>
          {/* Action Selection for Existing Closures */}
          {currentClosure && isManager && (
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Manager Actions
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {canApprove && (
                      <Button
                        variant={action === 'approve' ? 'contained' : 'outlined'}
                        color="success"
                        startIcon={<VerifiedUserIcon />}
                        onClick={() => setAction('approve')}
                      >
                        Approve
                      </Button>
                    )}
                    {canClose && (
                      <Button
                        variant={action === 'close' ? 'contained' : 'outlined'}
                        color="primary"
                        startIcon={<CheckCircleIcon />}
                        onClick={() => setAction('close')}
                      >
                        Close Service
                      </Button>
                    )}
                    {canReopen && (
                      <Button
                        variant={action === 'reopen' ? 'contained' : 'outlined'}
                        color="warning"
                        startIcon={<CancelIcon />}
                        onClick={() => setAction('reopen')}
                      >
                        Reopen
                      </Button>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Create New Closure Form */}
          {!currentClosure && (
            <>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Closure Reason</InputLabel>
                  <Select
                    value={formData.closure_reason}
                    onChange={handleSelectChange('closure_reason')}
                    label="Closure Reason"
                  >
                    {CLOSURE_REASONS.map((reason) => (
                      <MenuItem key={reason.value} value={reason.value}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <reason.icon color={reason.color as any} fontSize="small" />
                          {reason.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.requires_manager_approval}
                      onChange={handleSwitchChange('requires_manager_approval')}
                      color="primary"
                    />
                  }
                  label={
                    <Box display="flex" alignItems="center" gap={1}>
                      <LockIcon fontSize="small" />
                      Requires Manager Approval
                    </Box>
                  }
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Closure Notes"
                  placeholder="Describe the reason for closure..."
                  value={formData.closure_notes}
                  onChange={handleTextChange('closure_notes')}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.escalation_required}
                      onChange={handleSwitchChange('escalation_required')}
                      color="warning"
                    />
                  }
                  label={
                    <Box display="flex" alignItems="center" gap={1}>
                      <WarningIcon fontSize="small" />
                      Escalation Required
                    </Box>
                  }
                />
              </Grid>

              {formData.escalation_required && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Escalation Reason"
                    placeholder="Explain why escalation is required..."
                    value={formData.escalation_reason}
                    onChange={handleTextChange('escalation_reason')}
                  />
                </Grid>
              )}
            </>
          )}

          {/* Approval Form */}
          {action === 'approve' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Approval Notes"
                placeholder="Add notes about the approval..."
                value={formData.approval_notes}
                onChange={handleTextChange('approval_notes')}
              />
            </Grid>
          )}

          {/* Final Closure Form */}
          {action === 'close' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Final Closure Notes"
                placeholder="Add final notes before closing the service..."
                value={formData.final_closure_notes}
                onChange={handleTextChange('final_closure_notes')}
              />
            </Grid>
          )}

          {/* Reopen Form */}
          {action === 'reopen' && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Reopening Reason *"
                placeholder="Explain why the service needs to be reopened..."
                value={formData.reopening_reason}
                onChange={handleTextChange('reopening_reason')}
                required
              />
            </Grid>
          )}

          {/* Current Closure Details */}
          {currentClosure && action === 'create' && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Closure Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Reason
                      </Typography>
                      <Typography variant="body1">
                        {CLOSURE_REASONS.find(r => r.value === currentClosure.closure_reason)?.label || currentClosure.closure_reason}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Created At
                      </Typography>
                      <Typography variant="body1">
                        {new Date(currentClosure.created_at).toLocaleDateString()}
                      </Typography>
                    </Grid>
                    {currentClosure.closure_notes && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          Notes
                        </Typography>
                        <Typography variant="body1">
                          {currentClosure.closure_notes}
                        </Typography>
                      </Grid>
                    )}
                    {currentClosure.escalation_required && (
                      <Grid item xs={12}>
                        <Alert severity="warning">
                          <Typography variant="body2">
                            <strong>Escalation Required:</strong> {currentClosure.escalation_reason}
                          </Typography>
                        </Alert>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={isSubmitting}>
          Cancel
        </Button>
        {(action !== 'create' || !currentClosure) && (
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              isSubmitting || 
              (action === 'reopen' && !formData.reopening_reason.trim())
            }
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <AssignmentIcon />}
          >
            {isSubmitting ? 'Processing...' : getSubmitButtonText()}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ServiceClosureDialog;