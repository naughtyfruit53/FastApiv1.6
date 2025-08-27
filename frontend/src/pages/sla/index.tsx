// frontend/src/pages/sla/index.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  InputLabel,
  Select,
  MenuItem,
  FormControl,
  InputAdornment,
  Stack,
  Grid,
  Alert,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Refresh,
  Warning,
  CheckCircle,
  Schedule,
  TrendingUp,
  Assessment,
  Policy,
  Timeline,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { slaService, SLAPolicy, SLAPolicyCreate, SLAPolicyUpdate, SLAMetrics } from '../../services/slaService';

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
      id={`sla-tabpanel-${index}`}
      aria-labelledby={`sla-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const SLAManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [policyDialog, setPolicyDialog] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<SLAPolicy | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const queryClient = useQueryClient();

  // Get organization ID from context/auth
  const organizationId = 1; // This should come from auth context

  // Form state for policy dialog
  const [policyForm, setPolicyForm] = useState<SLAPolicyCreate>({
    name: '',
    description: '',
    priority: '',
    ticket_type: '',
    response_time_hours: 2,
    resolution_time_hours: 24,
    escalation_enabled: true,
    escalation_threshold_percent: 80,
    is_active: true,
    is_default: false,
  });

  // API calls
  const {
    data: policies = [],
    isLoading: policiesLoading,
    refetch: refetchPolicies,
  } = useQuery({
    queryKey: ['sla-policies', organizationId],
    queryFn: () => slaService.getPolicies(organizationId),
  });

  const {
    data: metrics,
    isLoading: metricsLoading,
  } = useQuery({
    queryKey: ['sla-metrics', organizationId],
    queryFn: () => slaService.getSLAMetrics(organizationId, undefined, undefined, 30),
  });

  const {
    data: breachedSLAs = [],
    isLoading: breachedLoading,
  } = useQuery({
    queryKey: ['breached-slas', organizationId],
    queryFn: () => slaService.getBreachedSLAs(organizationId, 20),
  });

  // Mutations
  const createPolicyMutation = useMutation({
    mutationFn: (policy: SLAPolicyCreate) => slaService.createPolicy(organizationId, policy),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sla-policies'] });
      setPolicyDialog(false);
      resetForm();
    },
  });

  const updatePolicyMutation = useMutation({
    mutationFn: ({ id, policy }: { id: number; policy: SLAPolicyUpdate }) =>
      slaService.updatePolicy(organizationId, id, policy),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sla-policies'] });
      setPolicyDialog(false);
      resetForm();
    },
  });

  const deletePolicyMutation = useMutation({
    mutationFn: (id: number) => slaService.deletePolicy(organizationId, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sla-policies'] });
      setDeleteDialog(false);
      setSelectedPolicy(null);
    },
  });

  // Event handlers
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCreatePolicy = () => {
    setSelectedPolicy(null);
    resetForm();
    setPolicyDialog(true);
  };

  const handleEditPolicy = (policy: SLAPolicy) => {
    setSelectedPolicy(policy);
    setPolicyForm({
      name: policy.name,
      description: policy.description || '',
      priority: policy.priority || '',
      ticket_type: policy.ticket_type || '',
      response_time_hours: policy.response_time_hours,
      resolution_time_hours: policy.resolution_time_hours,
      escalation_enabled: policy.escalation_enabled,
      escalation_threshold_percent: policy.escalation_threshold_percent,
      is_active: policy.is_active,
      is_default: policy.is_default,
    });
    setPolicyDialog(true);
  };

  const handleDeletePolicy = (policy: SLAPolicy) => {
    setSelectedPolicy(policy);
    setDeleteDialog(true);
  };

  const handleSubmitPolicy = () => {
    if (selectedPolicy) {
      updatePolicyMutation.mutate({ id: selectedPolicy.id, policy: policyForm });
    } else {
      createPolicyMutation.mutate(policyForm);
    }
  };

  const resetForm = () => {
    setPolicyForm({
      name: '',
      description: '',
      priority: '',
      ticket_type: '',
      response_time_hours: 2,
      resolution_time_hours: 24,
      escalation_enabled: true,
      escalation_threshold_percent: 80,
      is_active: true,
      is_default: false,
    });
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'met': return 'success';
      case 'breached': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  // Render summary cards
  const renderSummaryCards = () => {
    if (!metrics) return null;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tickets
              </Typography>
              <Typography variant="h4" component="div">
                {metrics.total_tickets}
              </Typography>
              <Typography variant="body2">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Response SLA
              </Typography>
              <Typography variant="h4" component="div" color={metrics.response_sla_percentage >= 95 ? 'success.main' : 'warning.main'}>
                {metrics.response_sla_percentage.toFixed(1)}%
              </Typography>
              <Typography variant="body2">
                {metrics.response_sla_met} / {metrics.total_tickets} met
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Resolution SLA
              </Typography>
              <Typography variant="h4" component="div" color={metrics.resolution_sla_percentage >= 95 ? 'success.main' : 'warning.main'}>
                {metrics.resolution_sla_percentage.toFixed(1)}%
              </Typography>
              <Typography variant="body2">
                {metrics.resolution_sla_met} / {metrics.total_tickets} met
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Escalated Tickets
              </Typography>
              <Typography variant="h4" component="div" color={metrics.escalated_tickets > 0 ? 'error.main' : 'success.main'}>
                {metrics.escalated_tickets}
              </Typography>
              <Typography variant="body2">
                Requiring attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            SLA Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage service level agreements and track performance
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => {
            refetchPolicies();
            queryClient.invalidateQueries({ queryKey: ['sla-metrics'] });
            queryClient.invalidateQueries({ queryKey: ['breached-slas'] });
          }}
        >
          Refresh
        </Button>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ mb: 4 }}>
        {renderSummaryCards()}
      </Box>

      {/* SLA Tabs */}
      <Paper sx={{ mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="SLA management tabs">
            <Tab label="SLA Policies" icon={<Policy />} />
            <Tab label="Performance Dashboard" icon={<Assessment />} />
            <Tab label="Breached SLAs" icon={<Warning />} />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {/* SLA Policies Tab */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">SLA Policies</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreatePolicy}
            >
              Create Policy
            </Button>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Response Time</TableCell>
                  <TableCell>Resolution Time</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {policies.map((policy) => (
                  <TableRow key={policy.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body1">{policy.name}</Typography>
                        {policy.is_default && (
                          <Chip label="Default" size="small" color="primary" sx={{ mt: 0.5 }} />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {policy.priority ? (
                        <Chip
                          label={policy.priority}
                          size="small"
                          color={getPriorityColor(policy.priority) as any}
                        />
                      ) : (
                        'All'
                      )}
                    </TableCell>
                    <TableCell>{policy.ticket_type || 'All'}</TableCell>
                    <TableCell>{policy.response_time_hours}h</TableCell>
                    <TableCell>{policy.resolution_time_hours}h</TableCell>
                    <TableCell>
                      <Chip
                        label={policy.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={policy.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleEditPolicy(policy)} size="small">
                        <Edit />
                      </IconButton>
                      <IconButton onClick={() => handleDeletePolicy(policy)} size="small" color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Performance Dashboard Tab */}
          <Typography variant="h6" gutterBottom>
            SLA Performance Dashboard
          </Typography>
          {metrics && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Average Response Time
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {metrics.avg_response_time_hours?.toFixed(1) || 'N/A'}h
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Average Resolution Time
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {metrics.avg_resolution_time_hours?.toFixed(1) || 'N/A'}h
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Breached SLAs Tab */}
          <Typography variant="h6" gutterBottom>
            Breached SLAs
          </Typography>
          {breachedSLAs.length === 0 ? (
            <Alert severity="success">
              <Typography>No SLA breaches found. Great job!</Typography>
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Ticket ID</TableCell>
                    <TableCell>Response Status</TableCell>
                    <TableCell>Resolution Status</TableCell>
                    <TableCell>Response Breach</TableCell>
                    <TableCell>Resolution Breach</TableCell>
                    <TableCell>Escalated</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {breachedSLAs.map((tracking) => (
                    <TableRow key={tracking.id}>
                      <TableCell>{tracking.ticket_id}</TableCell>
                      <TableCell>
                        <Chip
                          label={tracking.response_status}
                          size="small"
                          color={getStatusColor(tracking.response_status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={tracking.resolution_status}
                          size="small"
                          color={getStatusColor(tracking.resolution_status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {tracking.response_breach_hours && tracking.response_breach_hours > 0
                          ? `+${tracking.response_breach_hours.toFixed(1)}h`
                          : 'On time'}
                      </TableCell>
                      <TableCell>
                        {tracking.resolution_breach_hours && tracking.resolution_breach_hours > 0
                          ? `+${tracking.resolution_breach_hours.toFixed(1)}h`
                          : 'On time'}
                      </TableCell>
                      <TableCell>
                        {tracking.escalation_triggered ? (
                          <Chip label={`Level ${tracking.escalation_level}`} size="small" color="error" />
                        ) : (
                          'No'
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>
      </Paper>

      {/* Policy Create/Edit Dialog */}
      <Dialog open={policyDialog} onClose={() => setPolicyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedPolicy ? 'Edit SLA Policy' : 'Create SLA Policy'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Policy Name"
                value={policyForm.name}
                onChange={(e) => setPolicyForm({ ...policyForm, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={policyForm.priority}
                  onChange={(e) => setPolicyForm({ ...policyForm, priority: e.target.value })}
                >
                  <MenuItem value="">All Priorities</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={policyForm.description}
                onChange={(e) => setPolicyForm({ ...policyForm, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Response Time"
                type="number"
                value={policyForm.response_time_hours}
                onChange={(e) => setPolicyForm({ ...policyForm, response_time_hours: Number(e.target.value) })}
                InputProps={{
                  endAdornment: <InputAdornment position="end">hours</InputAdornment>,
                }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Resolution Time"
                type="number"
                value={policyForm.resolution_time_hours}
                onChange={(e) => setPolicyForm({ ...policyForm, resolution_time_hours: Number(e.target.value) })}
                InputProps={{
                  endAdornment: <InputAdornment position="end">hours</InputAdornment>,
                }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Escalation Threshold"
                type="number"
                value={policyForm.escalation_threshold_percent}
                onChange={(e) => setPolicyForm({ ...policyForm, escalation_threshold_percent: Number(e.target.value) })}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Stack spacing={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={policyForm.escalation_enabled}
                      onChange={(e) => setPolicyForm({ ...policyForm, escalation_enabled: e.target.checked })}
                    />
                  }
                  label="Enable Escalation"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={policyForm.is_active}
                      onChange={(e) => setPolicyForm({ ...policyForm, is_active: e.target.checked })}
                    />
                  }
                  label="Active"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={policyForm.is_default}
                      onChange={(e) => setPolicyForm({ ...policyForm, is_default: e.target.checked })}
                    />
                  }
                  label="Default Policy"
                />
              </Stack>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPolicyDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitPolicy}
            variant="contained"
            disabled={createPolicyMutation.isPending || updatePolicyMutation.isPending}
          >
            {selectedPolicy ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Delete SLA Policy</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the SLA policy "{selectedPolicy?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button
            onClick={() => selectedPolicy && deletePolicyMutation.mutate(selectedPolicy.id)}
            color="error"
            variant="contained"
            disabled={deletePolicyMutation.isPending}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SLAManagement;