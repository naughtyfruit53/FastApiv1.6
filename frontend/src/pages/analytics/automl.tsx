import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface AutoMLRun {
  id: number;
  run_name: string;
  task_type: string;
  framework: string;
  status: string;
  progress: number;
  current_trial: number;
  max_trials: number;
  best_model_name: string | null;
  best_score: number | null;
  created_at: string;
}

interface AutoMLDashboard {
  total_runs: number;
  completed_runs: number;
  running_runs: number;
  recent_runs: Array<{
    id: number;
    run_name: string;
    task_type: string;
    status: string;
    best_score: number | null;
    created_at: string;
  }>;
}

const AutoMLPage: React.FC = () => {
  const [dashboard, setDashboard] = useState<AutoMLDashboard | null>(null);
  const [runs, setRuns] = useState<AutoMLRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newRun, setNewRun] = useState({
    run_name: '',
    task_type: 'classification',
    target_column: '',
    feature_columns: [] as string[],
    metric: 'accuracy',
    framework: 'optuna',
    time_budget: 3600,
    max_trials: 100,
  });

  useEffect(() => {
    fetchDashboard();
    fetchRuns();
  }, []);

  const fetchDashboard = async () => {
    try {
      // API call to fetch dashboard data
      // const response = await fetch('/api/v1/automl/dashboard');
      // const data = await response.json();
      // setDashboard(data);
      
      // Mock data for demonstration
      setDashboard({
        total_runs: 15,
        completed_runs: 10,
        running_runs: 2,
        recent_runs: [
          {
            id: 1,
            run_name: 'Sales Forecast Model',
            task_type: 'regression',
            status: 'completed',
            best_score: 0.89,
            created_at: new Date().toISOString(),
          },
        ],
      });
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRuns = async () => {
    try {
      // API call to fetch runs
      // const response = await fetch('/api/v1/automl/runs');
      // const data = await response.json();
      // setRuns(data);
      
      // Mock data
      setRuns([
        {
          id: 1,
          run_name: 'Sales Forecast Model',
          task_type: 'regression',
          framework: 'optuna',
          status: 'completed',
          progress: 100,
          current_trial: 100,
          max_trials: 100,
          best_model_name: 'RandomForest',
          best_score: 0.89,
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          run_name: 'Customer Churn Prediction',
          task_type: 'classification',
          framework: 'optuna',
          status: 'running',
          progress: 45,
          current_trial: 45,
          max_trials: 100,
          best_model_name: 'XGBoost',
          best_score: 0.84,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error('Error fetching runs:', error);
    }
  };

  const handleCreateRun = async () => {
    try {
      // API call to create run
      // const response = await fetch('/api/v1/automl/runs', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(newRun),
      // });
      
      console.log('Creating AutoML run:', newRun);
      setOpenDialog(false);
      fetchRuns();
      fetchDashboard();
    } catch (error) {
      console.error('Error creating run:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">AutoML Dashboard</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => {
              fetchDashboard();
              fetchRuns();
            }}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={() => setOpenDialog(true)}
          >
            New AutoML Run
          </Button>
        </Box>
      </Box>

      {/* Dashboard Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Runs</Typography>
              </Box>
              <Typography variant="h3">{dashboard?.total_runs || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Completed</Typography>
              </Box>
              <Typography variant="h3">{dashboard?.completed_runs || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PlayIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Running</Typography>
              </Box>
              <Typography variant="h3">{dashboard?.running_runs || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SettingsIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Pending</Typography>
              </Box>
              <Typography variant="h3">
                {(dashboard?.total_runs || 0) - (dashboard?.completed_runs || 0) - (dashboard?.running_runs || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AutoML Runs Table */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          AutoML Runs
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Run Name</TableCell>
                <TableCell>Task Type</TableCell>
                <TableCell>Framework</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Best Model</TableCell>
                <TableCell>Best Score</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runs.map((run) => (
                <TableRow key={run.id}>
                  <TableCell>{run.run_name}</TableCell>
                  <TableCell>
                    <Chip label={run.task_type} size="small" />
                  </TableCell>
                  <TableCell>{run.framework}</TableCell>
                  <TableCell>
                    <Chip
                      label={run.status}
                      color={getStatusColor(run.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={run.progress}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {run.current_trial}/{run.max_trials}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{run.best_model_name || '-'}</TableCell>
                  <TableCell>
                    {run.best_score ? run.best_score.toFixed(4) : '-'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <AssessmentIcon />
                      </IconButton>
                    </Tooltip>
                    {run.status === 'running' && (
                      <Tooltip title="Cancel">
                        <IconButton size="small" color="error">
                          <StopIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create Run Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New AutoML Run</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Run Name"
                value={newRun.run_name}
                onChange={(e) => setNewRun({ ...newRun, run_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Task Type</InputLabel>
                <Select
                  value={newRun.task_type}
                  label="Task Type"
                  onChange={(e) => setNewRun({ ...newRun, task_type: e.target.value })}
                >
                  <MenuItem value="classification">Classification</MenuItem>
                  <MenuItem value="regression">Regression</MenuItem>
                  <MenuItem value="time_series">Time Series</MenuItem>
                  <MenuItem value="clustering">Clustering</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Framework</InputLabel>
                <Select
                  value={newRun.framework}
                  label="Framework"
                  onChange={(e) => setNewRun({ ...newRun, framework: e.target.value })}
                >
                  <MenuItem value="optuna">Optuna</MenuItem>
                  <MenuItem value="auto_sklearn">Auto-sklearn</MenuItem>
                  <MenuItem value="tpot">TPOT</MenuItem>
                  <MenuItem value="h2o">H2O</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Column"
                value={newRun.target_column}
                onChange={(e) => setNewRun({ ...newRun, target_column: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Metric"
                value={newRun.metric}
                onChange={(e) => setNewRun({ ...newRun, metric: e.target.value })}
                helperText="e.g., accuracy, f1, rmse, mae"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Max Trials"
                value={newRun.max_trials}
                onChange={(e) => setNewRun({ ...newRun, max_trials: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Time Budget (seconds)"
                value={newRun.time_budget}
                onChange={(e) => setNewRun({ ...newRun, time_budget: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateRun} variant="contained">
            Create Run
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutoMLPage;
