'use client';

/**
 * Migration Wizard Component
 * 
 * A comprehensive step-by-step wizard for importing data from external ERPs like Tally, Zoho.
 * Provides guided migration workflow with data mapping, validation, and progress monitoring.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Upload,
  CheckCircle,
  Error,
  Warning,
  Refresh,
  CloudUpload,
  Settings,
  PlayArrow,
  Undo,
  Download,
  Info
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

export interface MigrationJob {
  id: number;
  job_name: string;
  description: string;
  source_type: string;
  data_types: string[];
  status: string;
  created_at: string;
  progress_percentage?: number;
  error_message?: string;
}

export interface MigrationWizardStep {
  step_number: number;
  step_name: string;
  is_completed: boolean;
  is_current: boolean;
  can_skip: boolean;
  data?: any;
}

export interface MigrationWizardState {
  job_id: number;
  current_step: number;
  total_steps: number;
  steps: MigrationWizardStep[];
  can_proceed: boolean;
  validation_errors: string[];
}

interface MigrationWizardProps {
  open: boolean;
  onClose: () => void;
  jobId?: number;
}

const MigrationWizard: React.FC<MigrationWizardProps> = ({ open, onClose, jobId }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [wizardState, setWizardState] = useState<MigrationWizardState | null>(null);
  const [currentJob, setCurrentJob] = useState<MigrationJob | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [err, setErr] = useState<string | null>(null);
  
  // Form data for creating new migration job
  const [newJobData, setNewJobData] = useState({
    job_name: '',
    description: '',
    source_type: 'tally',
    data_types: [] as string[],
    conflict_resolution_strategy: 'skip_existing'
  });

  // Step definitions
  const stepNames = [
    'Create Migration Job',
    'Upload Source File',
    'Configure Data Mapping',
    'Validate Data',
    'Execute Migration'
  ];

  useEffect(() => {
    if (open && jobId) {
      loadWizardState();
    }
  }, [open, jobId]);

  const loadWizardState = async () => {
    if (!jobId) {return;}
    
    setLoading(true);
    try {
      const response = await axios.get(`/api/v1/migration/jobs/${jobId}/wizard`);
      setWizardState(response.data);
      
      // Also load job details
      const jobResponse = await axios.get(`/api/v1/migration/jobs/${jobId}`);
      setCurrentJob(jobResponse.data);
    } catch (error) {
      console.error('Failed to load wizard state:', error);
      setErr('Failed to load migration wizard state');
    } finally {
      setLoading(false);
    }
  };

  const createMigrationJob = async () => {
    if (!newJobData.job_name || newJobData.data_types.length === 0) {
      setErr('Please provide job name and select at least one data type');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/v1/migration/jobs', newJobData);
      const newJob = response.data;
      setCurrentJob(newJob);
      
      // Load wizard state for the new job
      const wizardResponse = await axios.get(`/api/v1/migration/jobs/${newJob.id}/wizard`);
      setWizardState(wizardResponse.data);
    } catch (error) {
      console.error('Failed to create migration job:', error);
      setErr('Failed to create migration job');
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = async () => {
    if (!selectedFile || !currentJob) {
      setErr('Please select a file to upload');
      return;
    }

    setLoading(true);
    setUploadProgress(0);
    
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await axios.post(`/api/v1/migration/jobs/${currentJob.id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          setUploadProgress(percentCompleted);
        },
      });
      
      // Reload wizard state
      await loadWizardState();
    } catch (error) {
      console.error('Failed to upload file:', error);
      setErr('Failed to upload file');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const executeMigration = async () => {
    if (!currentJob) {return;}

    setLoading(true);
    try {
      await axios.post(`/api/v1/migration/jobs/${currentJob.id}/execute`);
      await loadWizardState();
    } catch (error) {
      console.error('Failed to execute migration:', error);
      setErr('Failed to execute migration');
    } finally {
      setLoading(false);
    }
  };

  const rollbackMigration = async () => {
    if (!currentJob) {return;}

    setLoading(true);
    try {
      await axios.post(`/api/v1/migration/jobs/${currentJob.id}/rollback`);
      await loadWizardState();
    } catch (error) {
      console.error('Failed to rollback migration:', error);
      setErr('Failed to rollback migration');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    if (!wizardState) {return null;}

    const currentStep = wizardState.current_step;

    switch (currentStep) {
      case 1:
        return renderCreateJobStep();
      case 2:
        return renderUploadStep();
      case 3:
        return renderMappingStep();
      case 4:
        return renderValidationStep();
      case 5:
        return renderExecutionStep();
      default:
        return <Typography>Unknown step</Typography>;
    }
  };

  const renderCreateJobStep = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>Create Migration Job</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Job Name"
            value={newJobData.job_name}
            onChange={(e) => setNewJobData({ ...newJobData, job_name: e.target.value })}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            value={newJobData.description}
            onChange={(e) => setNewJobData({ ...newJobData, description: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Source Type</InputLabel>
            <Select
              value={newJobData.source_type}
              onChange={(e) => setNewJobData({ ...newJobData, source_type: e.target.value })}
            >
              <MenuItem value="tally">Tally ERP</MenuItem>
              <MenuItem value="zoho">Zoho</MenuItem>
              <MenuItem value="excel">Excel/CSV</MenuItem>
              <MenuItem value="json">JSON</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>Data Types to Import</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {['ledgers', 'vouchers', 'contacts', 'products', 'customers', 'vendors', 'stock'].map((type) => (
              <Chip
                key={type}
                label={type.charAt(0).toUpperCase() + type.slice(1)}
                clickable
                color={newJobData.data_types.includes(type) ? 'primary' : 'default'}
                onClick={() => {
                  const newTypes = newJobData.data_types.includes(type)
                    ? newJobData.data_types.filter(t => t !== type)
                    : [...newJobData.data_types, type];
                  setNewJobData({ ...newJobData, data_types: newTypes });
                }}
              />
            ))}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );

  const renderUploadStep = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>Upload Source File</Typography>
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', p: 3, border: '2px dashed #ccc', borderRadius: 1 }}>
            <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {selectedFile ? selectedFile.name : 'Select File to Upload'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Supported formats: CSV, Excel, JSON, Tally XML
            </Typography>
            <Button
              variant="contained"
              component="label"
              startIcon={<Upload />}
            >
              Choose File
              <input
                type="file"
                hidden
                accept=".csv,.xlsx,.xls,.json,.xml"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
            </Button>
          </Box>
          {uploadProgress > 0 && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Uploading... {uploadProgress}%
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );

  const renderMappingStep = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>Configure Data Mapping</Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Map source fields to target system fields. Auto-mapping suggestions are provided.
      </Alert>
      {/* Placeholder for mapping interface */}
      <Typography variant="body2">
        Data mapping interface will be implemented based on uploaded file structure.
      </Typography>
    </Box>
  );

  const renderValidationStep = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>Validate Data</Typography>
      <Alert severity="warning" sx={{ mb: 2 }}>
        Review validation results before proceeding with migration.
      </Alert>
      {/* Placeholder for validation results */}
      <Typography variant="body2">
        Data validation results will be displayed here.
      </Typography>
    </Box>
  );

  const renderExecutionStep = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>Execute Migration</Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<PlayArrow />}
          onClick={executeMigration}
          disabled={loading}
        >
          Start Migration
        </Button>
        {currentJob?.status === 'completed' && (
          <Button
            variant="outlined"
            startIcon={<Undo />}
            onClick={rollbackMigration}
            disabled={loading}
          >
            Rollback
          </Button>
        )}
      </Box>
      {currentJob?.progress_percentage !== undefined && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={currentJob.progress_percentage} 
          />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Progress: {currentJob.progress_percentage}%
          </Typography>
        </Box>
      )}
    </Box>
  );

  const getStepStatus = (stepIndex: number) => {
    if (!wizardState) {return 'pending';}
    
    const step = wizardState.steps[stepIndex];
    if (step?.is_completed) {return 'completed';}
    if (step?.is_current) {return 'active';}
    return 'pending';
  };

  const canProceedToNext = () => {
    if (!wizardState) {return false;}
    
    const currentStep = wizardState.current_step;
    
    switch (currentStep) {
      case 1:
        return newJobData.job_name && newJobData.data_types.length > 0;
      case 2:
        return selectedFile !== null;
      default:
        return wizardState.can_proceed;
    }
  };

  const handleNext = async () => {
    if (!wizardState) {return;}
    
    const currentStep = wizardState.current_step;
    
    switch (currentStep) {
      case 1:
        await createMigrationJob();
        break;
      case 2:
        await uploadFile();
        break;
      default:
        // For other steps, just reload the wizard state
        await loadWizardState();
        break;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{ sx: { minHeight: '600px' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings />
          Migration Wizard
          {currentJob && (
            <Chip 
              label={currentJob.status} 
              size="small" 
              color={currentJob.status === 'completed' ? 'success' : 'primary'} 
            />
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && !wizardState && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {err && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErr(null)}>
            {err}
          </Alert>
        )}

        {wizardState && (
          <>
            <Stepper activeStep={wizardState.current_step - 1} sx={{ mb: 4 }}>
              {stepNames.map((label, index) => (
                <Step key={label}>
                  <StepLabel 
                    error={getStepStatus(index) === 'error'}
                    completed={getStepStatus(index) === 'completed'}
                  >
                    {label}
                  </StepLabel>
                </Step>
              ))}
            </Stepper>

            {wizardState.validation_errors.length > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Validation Issues:</Typography>
                <ul>
                  {wizardState.validation_errors.map((validationError, index) => (
                    <li key={index}>{validationError}</li>
                  ))}
                </ul>
              </Alert>
            )}

            {renderStepContent()}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {wizardState && wizardState.current_step > 1 && (
          <Button onClick={() => loadWizardState()}>
            <Refresh />
            Refresh
          </Button>
        )}
        {wizardState && wizardState.current_step < wizardState.total_steps && (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={!canProceedToNext() || loading}
          >
            {wizardState.current_step === 1 ? 'Create Job' : 
             wizardState.current_step === 2 ? 'Upload File' : 'Next'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default MigrationWizard;