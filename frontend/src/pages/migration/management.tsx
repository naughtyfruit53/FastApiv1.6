'use client';
/**
 * Migration Management Page
 * 
 * Main page for managing data migrations and integrations.
 * Only accessible to super admins.
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  Add,
  CloudUpload,
  Timeline,
  Settings,
  Refresh,
  Delete,
  Edit,
  PlayArrow,
  Stop,
  Undo,
  History,
  Integration
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/router';
import MigrationWizard from '../../components/MigrationWizard';
import IntegrationDashboard from '../../components/IntegrationDashboard';
import axios from 'axios';
interface MigrationJob {
  id: number;
  job_name: string;
  description: string;
  source_type: string;
  data_types: string[];
  status: string;
  created_at: string;
  updated_at: string;
  progress_percentage?: number;
  error_message?: string;
  created_by_name?: string;
}
const MigrationManagement: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [migrationJobs, setMigrationJobs] = useState<MigrationJob[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [jobToDelete, setJobToDelete] = useState<MigrationJob | null>(null);
  // Check if user is super admin
  const isSuperAdmin = user?.is_super_admin;
  useEffect(() => {
    if (!isSuperAdmin) {
      router.push('/settings'); // Redirect if not super admin
      return;
    }
// loadMigrationJobs is defined later in this file
    loadMigrationJobs();
  }, [isSuperAdmin, router]);
  const loadMigrationJobs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/migration/jobs');
      setMigrationJobs(response.data);
    } catch (err) {
      console.error(msg, err);
      setError('Failed to load migration jobs');
    } finally {
      setLoading(false);
    }
  };
  const deleteJob = async (job: MigrationJob) => {
    try {
      await axios.delete(`/api/v1/migration/jobs/${job.id}`);
      await loadMigrationJobs();
      setDeleteDialogOpen(false);
      setJobToDelete(null);
    } catch (err) {
      console.error(msg, err);
      setError('Failed to delete migration job');
    }
  };
  const executeJob = async (jobId: number) => {
    try {
      await axios.post(`/api/v1/migration/jobs/${jobId}/execute`);
      await loadMigrationJobs();
    } catch (err) {
      console.error(msg, err);
      setError('Failed to execute migration job');
    }
  };
  const rollbackJob = async (jobId: number) => {
    try {
      await axios.post(`/api/v1/migration/jobs/${jobId}/rollback`);
      await loadMigrationJobs();
    } catch (err) {
      console.error(msg, err);
      setError('Failed to rollback migration job');
    }
  };
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      case 'draft':
        return 'default';
      case 'approved':
        return 'primary';
      default:
        return 'default';
    }
  };
  const openWizard = (jobId?: number) => {
    setSelectedJobId(jobId || null);
    setWizardOpen(true);
  };
  const closeWizard = () => {
    setWizardOpen(false);
    setSelectedJobId(null);
    loadMigrationJobs(); // Refresh the list
  };
  if (!isSuperAdmin) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access denied. Only super administrators can access migration management.
        </Alert>
      </Container>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Migration & Integration Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Timeline />}
            onClick={() => setDashboardOpen(true)}
          >
            Integration Dashboard
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => openWizard()}
          >
            New Migration
          </Button>
        </Box>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {migrationJobs.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Migrations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                {migrationJobs.filter(job => job.status === 'completed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="info.main">
                {migrationJobs.filter(job => job.status === 'running').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Running
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="error.main">
                {migrationJobs.filter(job => job.status === 'failed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Migration Jobs Table */}
      <Paper sx={{ mb: 4 }}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Migration Jobs</Typography>
          <Button
            startIcon={<Refresh />}
            onClick={loadMigrationJobs}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Job Name</TableCell>
                  <TableCell>Source Type</TableCell>
                  <TableCell>Data Types</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {migrationJobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">{job.job_name}</Typography>
                        {job.description && (
                          <Typography variant="caption" color="text.secondary">
                            {job.description}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={job.source_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {job.data_types.map((type) => (
                          <Chip key={type} label={type} size="small" />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={job.status} 
                        color={getStatusColor(job.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {job.progress_percentage !== undefined ? (
                        <Box sx={{ width: 100 }}>
                          <LinearProgress
                            variant="determinate"
                            value={job.progress_percentage}
                            sx={{ height: 8, borderRadius: 1 }}
                          />
                          <Typography variant="caption">
                            {job.progress_percentage}%
                          </Typography>
                        </Box>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(job.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Open Wizard">
                          <IconButton
                            size="small"
                            onClick={() => openWizard(job.id)}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        {job.status === 'approved' && (
                          <Tooltip title="Execute Migration">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => executeJob(job.id)}
                            >
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        )}
                        {job.status === 'completed' && (
                          <Tooltip title="Rollback Migration">
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => rollbackJob(job.id)}
                            >
                              <Undo />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete Job">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => {
                              setJobToDelete(job);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
                {migrationJobs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4 }}>
                      <Typography color="text.secondary">
                        No migration jobs found. Click "New Migration" to create one.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
      {/* Recent Activity */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<CloudUpload />}
              onClick={() => openWizard()}
              sx={{ py: 2 }}
            >
              Import from Tally
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<CloudUpload />}
              onClick={() => openWizard()}
              sx={{ py: 2 }}
            >
              Import from Zoho
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Integration />}
              onClick={() => setDashboardOpen(true)}
              sx={{ py: 2 }}
            >
              Manage Integrations
            </Button>
          </Grid>
        </Grid>
      </Paper>
      {/* Migration Wizard Dialog */}
      <MigrationWizard
        open={wizardOpen}
        onClose={closeWizard}
        jobId={selectedJobId || undefined}
      />
      {/* Integration Dashboard */}
      <IntegrationDashboard
        open={dashboardOpen}
        onClose={() => setDashboardOpen(false)}
      />
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the migration job "{jobToDelete?.job_name}"? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button 
            color="error" 
            onClick={() => jobToDelete && deleteJob(jobToDelete)}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
export default MigrationManagement;