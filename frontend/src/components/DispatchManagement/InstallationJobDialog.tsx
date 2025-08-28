// frontend/src/components/DispatchManagement/InstallationJobDialog.tsx

'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Typography,
  Box,
  Chip,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
  Tabs,
  Tab,
  Divider,
  FormControlLabel,
  Checkbox,
  Rating
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Check as CompleteIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { useAuth } from '../../context/AuthContext';
import { 
  dispatchService,
  InstallationJobInDB,
  InstallationJobWithDetails,
  InstallationTaskInDB,
  CompletionRecordInDB,
  INSTALLATION_TASK_STATUSES,
  INSTALLATION_TASK_PRIORITIES,
  COMPLETION_STATUSES
} from '../../services/dispatchService';
import {
  INSTALLATION_JOB_STATUSES,
  INSTALLATION_JOB_PRIORITIES
} from '../../types/dispatch.types';

interface InstallationJobDialogProps {
  open: boolean;
  onClose: () => void;
  jobId?: number;
  onJobUpdated?: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`job-tabpanel-${index}`}
      aria-labelledby={`job-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const InstallationJobDialog: React.FC<InstallationJobDialogProps> = ({
  open,
  onClose,
  jobId,
  onJobUpdated
}) => {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [job, setJob] = useState<InstallationJobWithDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Task management state
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: INSTALLATION_TASK_PRIORITIES.MEDIUM,
    estimated_duration_minutes: 60,
    sequence_order: 1
  });
  const [editingTask, setEditingTask] = useState<InstallationTaskInDB | null>(null);
  
  // Completion form state
  const [completionForm, setCompletionForm] = useState({
    work_performed: '',
    issues_encountered: '',
    resolution_notes: '',
    materials_used: '',
    parts_replaced: '',
    quality_check_passed: false,
    verification_notes: '',
    photos_attached: false,
    customer_present: true,
    customer_signature_received: false,
    customer_feedback_notes: '',
    customer_rating: 5,
    follow_up_required: false,
    follow_up_notes: '',
    actual_start_time: new Date(),
    actual_end_time: new Date()
  });

  // Load job details
  useEffect(() => {
    if (open && jobId) {
      loadJobDetails();
    }
  }, [open, jobId]);

  const loadJobDetails = async () => {
    if (!jobId) return;
    
    try {
      setLoading(true);
      setError(null);
      const jobDetails = await dispatchService.getInstallationJobWithDetails(jobId);
      setJob(jobDetails);
      
      // Initialize completion form if completion record exists
      if (jobDetails.completion_record) {
        const record = jobDetails.completion_record;
        setCompletionForm({
          work_performed: record.work_performed || '',
          issues_encountered: record.issues_encountered || '',
          resolution_notes: record.resolution_notes || '',
          materials_used: record.materials_used || '',
          parts_replaced: record.parts_replaced || '',
          quality_check_passed: record.quality_check_passed || false,
          verification_notes: record.verification_notes || '',
          photos_attached: record.photos_attached || false,
          customer_present: record.customer_present || true,
          customer_signature_received: record.customer_signature_received || false,
          customer_feedback_notes: record.customer_feedback_notes || '',
          customer_rating: record.customer_rating || 5,
          follow_up_required: record.follow_up_required || false,
          follow_up_notes: record.follow_up_notes || '',
          actual_start_time: record.actual_start_time ? new Date(record.actual_start_time) : new Date(),
          actual_end_time: record.actual_end_time ? new Date(record.actual_end_time) : new Date()
        });
      }
    } catch (err) {
      setError('Failed to load job details');
      console.error('Error loading job details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (!job || !newTask.title.trim()) return;
    
    try {
      const task = await dispatchService.createInstallationTask({
        installation_job_id: job.id,
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        estimated_duration_minutes: newTask.estimated_duration_minutes,
        sequence_order: newTask.sequence_order
      });
      
      // Refresh job details
      await loadJobDetails();
      
      // Reset form
      setNewTask({
        title: '',
        description: '',
        priority: INSTALLATION_TASK_PRIORITIES.MEDIUM,
        estimated_duration_minutes: 60,
        sequence_order: (job.tasks?.length || 0) + 1
      });
    } catch (err) {
      setError('Failed to create task');
      console.error('Error creating task:', err);
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, status: string) => {
    try {
      await dispatchService.updateInstallationTask(taskId, { status });
      await loadJobDetails();
    } catch (err) {
      setError('Failed to update task status');
      console.error('Error updating task status:', err);
    }
  };

  const handleAssignTask = async (taskId: number, technicianId: number) => {
    try {
      await dispatchService.updateInstallationTask(taskId, { assigned_technician_id: technicianId });
      await loadJobDetails();
    } catch (err) {
      setError('Failed to assign task');
      console.error('Error assigning task:', err);
    }
  };

  const handleCompleteJob = async () => {
    if (!job) return;
    
    try {
      setLoading(true);
      await dispatchService.completeInstallationJob(job.id, {
        completion_date: new Date().toISOString(),
        completion_status: COMPLETION_STATUSES.COMPLETED,
        ...completionForm
      });
      
      await loadJobDetails();
      if (onJobUpdated) onJobUpdated();
      setCurrentTab(0); // Switch back to overview tab
    } catch (err) {
      setError('Failed to complete job');
      console.error('Error completing job:', err);
    } finally {
      setLoading(false);
    }
  };

  const canAssignTasks = user?.role === 'admin' || user?.role === 'manager';
  const canCompleteJob = job?.assigned_technician_id === user?.id || user?.role === 'admin';
  const isJobCompleted = job?.status === INSTALLATION_JOB_STATUSES.COMPLETED;

  if (!job && !loading) return null;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog
        open={open}
        onClose={onClose}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { minHeight: '80vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Installation Job Details - {job?.job_number}
            </Typography>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <Typography>Loading...</Typography>
            </Box>
          ) : job ? (
            <>
              <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
                <Tab label="Overview" />
                <Tab label="Tasks" />
                {!isJobCompleted && canCompleteJob && <Tab label="Complete Job" />}
                {isJobCompleted && <Tab label="Completion Details" />}
              </Tabs>

              <TabPanel value={currentTab} index={0}>
                {/* Overview Tab */}
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>Job Information</Typography>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Status</Typography>
                        <Chip 
                          label={job.status}
                          color={job.status === 'completed' ? 'success' : job.status === 'in_progress' ? 'warning' : 'default'}
                        />
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Priority</Typography>
                        <Chip 
                          label={job.priority}
                          color={job.priority === 'urgent' ? 'error' : job.priority === 'high' ? 'warning' : 'default'}
                        />
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Scheduled Date</Typography>
                        <Typography>{job.scheduled_date ? new Date(job.scheduled_date).toLocaleDateString() : 'Not scheduled'}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Installation Address</Typography>
                        <Typography>{job.installation_address}</Typography>
                      </Box>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>Progress Summary</Typography>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Total Tasks</Typography>
                        <Typography>{job.tasks?.length || 0}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Completed Tasks</Typography>
                        <Typography>
                          {job.tasks?.filter(task => task.status === 'completed').length || 0}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="textSecondary">Estimated Duration</Typography>
                        <Typography>
                          {job.tasks?.reduce((total, task) => total + (task.estimated_duration_minutes || 0), 0) || 0} minutes
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                {/* Tasks Tab */}
                <Box>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">Installation Tasks</Typography>
                    {canAssignTasks && !isJobCompleted && (
                      <Button
                        startIcon={<AddIcon />}
                        variant="contained"
                        onClick={() => {/* Open task creation form */}}
                        size="small"
                      >
                        Add Task
                      </Button>
                    )}
                  </Box>

                  {/* New Task Form */}
                  {canAssignTasks && !isJobCompleted && (
                    <Card sx={{ mb: 3 }}>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>Create New Task</Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Task Title"
                              value={newTask.title}
                              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                              size="small"
                            />
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <FormControl fullWidth size="small">
                              <InputLabel>Priority</InputLabel>
                              <Select
                                value={newTask.priority}
                                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as any })}
                              >
                                {Object.values(INSTALLATION_TASK_PRIORITIES).map(priority => (
                                  <MenuItem key={priority} value={priority}>{priority}</MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12} md={3}>
                            <TextField
                              fullWidth
                              type="number"
                              label="Est. Duration (min)"
                              value={newTask.estimated_duration_minutes}
                              onChange={(e) => setNewTask({ ...newTask, estimated_duration_minutes: parseInt(e.target.value) })}
                              size="small"
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <TextField
                              fullWidth
                              multiline
                              rows={2}
                              label="Description"
                              value={newTask.description}
                              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                              size="small"
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <Button 
                              variant="contained" 
                              onClick={handleCreateTask}
                              disabled={!newTask.title.trim()}
                              size="small"
                            >
                              Create Task
                            </Button>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  )}

                  {/* Task List */}
                  <Box display="flex" flexDirection="column" gap={2}>
                    {job.tasks?.map((task, index) => (
                      <Card key={task.id}>
                        <CardContent>
                          <Box display="flex" justifyContent="between" alignItems="start">
                            <Box flex={1}>
                              <Typography variant="subtitle1">{task.title}</Typography>
                              <Typography variant="body2" color="textSecondary" gutterBottom>
                                {task.description}
                              </Typography>
                              <Box display="flex" gap={1} mt={1}>
                                <Chip 
                                  label={task.status} 
                                  size="small"
                                  color={task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'warning' : 'default'}
                                />
                                <Chip label={task.priority} size="small" />
                                <Chip label={`${task.estimated_duration_minutes || 0} min`} size="small" />
                              </Box>
                            </Box>
                            <Box display="flex" gap={1}>
                              {task.status === 'pending' && (
                                <Tooltip title="Start Task">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleUpdateTaskStatus(task.id, 'in_progress')}
                                  >
                                    <StartIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                              {task.status === 'in_progress' && (
                                <Tooltip title="Complete Task">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleUpdateTaskStatus(task.id, 'completed')}
                                  >
                                    <CompleteIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    ))}
                    
                    {(!job.tasks || job.tasks.length === 0) && (
                      <Typography variant="body2" color="textSecondary" textAlign="center" py={4}>
                        No tasks created yet
                      </Typography>
                    )}
                  </Box>
                </Box>
              </TabPanel>

              {!isJobCompleted && canCompleteJob && (
                <TabPanel value={currentTab} index={2}>
                  {/* Complete Job Tab */}
                  <Typography variant="h6" gutterBottom>Complete Installation Job</Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        label="Work Performed *"
                        value={completionForm.work_performed}
                        onChange={(e) => setCompletionForm({ ...completionForm, work_performed: e.target.value })}
                        required
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Issues Encountered"
                        value={completionForm.issues_encountered}
                        onChange={(e) => setCompletionForm({ ...completionForm, issues_encountered: e.target.value })}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Resolution Notes"
                        value={completionForm.resolution_notes}
                        onChange={(e) => setCompletionForm({ ...completionForm, resolution_notes: e.target.value })}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <DateTimePicker
                        label="Actual Start Time"
                        value={completionForm.actual_start_time}
                        onChange={(date) => setCompletionForm({ ...completionForm, actual_start_time: date || new Date() })}
                        renderInput={(params) => <TextField {...params} fullWidth />}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <DateTimePicker
                        label="Actual End Time"
                        value={completionForm.actual_end_time}
                        onChange={(date) => setCompletionForm({ ...completionForm, actual_end_time: date || new Date() })}
                        renderInput={(params) => <TextField {...params} fullWidth />}
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Box display="flex" flexDirection="column" gap={2}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={completionForm.quality_check_passed}
                              onChange={(e) => setCompletionForm({ ...completionForm, quality_check_passed: e.target.checked })}
                            />
                          }
                          label="Quality Check Passed"
                        />
                        
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={completionForm.customer_present}
                              onChange={(e) => setCompletionForm({ ...completionForm, customer_present: e.target.checked })}
                            />
                          }
                          label="Customer Present"
                        />
                        
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={completionForm.customer_signature_received}
                              onChange={(e) => setCompletionForm({ ...completionForm, customer_signature_received: e.target.checked })}
                            />
                          }
                          label="Customer Signature Received"
                        />
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Customer Feedback"
                        value={completionForm.customer_feedback_notes}
                        onChange={(e) => setCompletionForm({ ...completionForm, customer_feedback_notes: e.target.value })}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Box>
                        <Typography variant="body2" gutterBottom>Customer Rating</Typography>
                        <Rating
                          value={completionForm.customer_rating}
                          onChange={(_, value) => setCompletionForm({ ...completionForm, customer_rating: value || 5 })}
                        />
                      </Box>
                    </Grid>
                  </Grid>
                </TabPanel>
              )}
              
              {isJobCompleted && job.completion_record && (
                <TabPanel value={currentTab} index={isJobCompleted ? 2 : 3}>
                  {/* Completion Details Tab */}
                  <Typography variant="h6" gutterBottom>Completion Details</Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>Work Performed</Typography>
                      <Typography variant="body2" paragraph>
                        {job.completion_record.work_performed}
                      </Typography>
                      
                      {job.completion_record.issues_encountered && (
                        <>
                          <Typography variant="subtitle2" gutterBottom>Issues Encountered</Typography>
                          <Typography variant="body2" paragraph>
                            {job.completion_record.issues_encountered}
                          </Typography>
                        </>
                      )}
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>Quality & Customer</Typography>
                      <Box display="flex" flexDirection="column" gap={1}>
                        <Chip 
                          label={job.completion_record.quality_check_passed ? "Quality Check Passed" : "Quality Check Failed"}
                          color={job.completion_record.quality_check_passed ? "success" : "error"}
                          size="small"
                        />
                        <Chip 
                          label={job.completion_record.customer_present ? "Customer Present" : "Customer Not Present"}
                          color={job.completion_record.customer_present ? "success" : "default"}
                          size="small"
                        />
                        {job.completion_record.customer_rating && (
                          <Box>
                            <Typography variant="body2">Customer Rating:</Typography>
                            <Rating value={job.completion_record.customer_rating} readOnly />
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  </Grid>
                </TabPanel>
              )}
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>Close</Button>
          {!isJobCompleted && canCompleteJob && currentTab === 2 && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleCompleteJob}
              disabled={!completionForm.work_performed.trim() || loading}
            >
              Complete Job
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default InstallationJobDialog;