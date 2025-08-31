'use client';

/**
 * Integration Dashboard Component
 * 
 * Centralized dashboard for managing all external integrations (Tally, email, calendar, payment, Zoho, etc.)
 * with health status, sync info, and access control.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel,
  Divider,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  Settings,
  CheckCircle,
  Error,
  Warning,
  Refresh,
  Edit,
  Add,
  Sync,
  Timeline,
  Security,
  Email,
  CalendarToday,
  Payment,
  AccountBalance,
  Cloud,
  Info,
  PlayArrow,
  History
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

export interface IntegrationHealthStatus {
  integration_name: string;
  status: 'healthy' | 'warning' | 'error' | 'disconnected';
  last_sync_at?: string;
  sync_frequency?: string;
  error_count: number;
  configuration_valid: boolean;
  performance_metrics?: {
    last_sync_duration?: string;
    records_synced?: number;
    avg_response_time?: string;
  };
}

export interface IntegrationDashboardData {
  tally_integration: IntegrationHealthStatus;
  email_integration: IntegrationHealthStatus;
  calendar_integration: IntegrationHealthStatus;
  payment_integration: IntegrationHealthStatus;
  zoho_integration: IntegrationHealthStatus;
  system_health: {
    database_status: string;
    api_response_time: string;
    last_backup: string;
    storage_usage: string;
  };
}

interface IntegrationDashboardProps {
  open: boolean;
  onClose: () => void;
}

const IntegrationDashboard: React.FC<IntegrationDashboardProps> = ({ open, onClose }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<IntegrationDashboardData | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);

  useEffect(() => {
    if (open) {
      loadDashboardData();
    }
  }, [open]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/integrations/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setErr('Failed to load integration dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const syncIntegration = async (integrationName: string) => {
    setLoading(true);
    try {
      await axios.post(`/api/v1/integrations/${integrationName}/sync`);
      await loadDashboardData();
    } catch (error) {
      console.error(`Failed to sync ${integrationName}:`, error);
      setErr(`Failed to sync ${integrationName}`);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (integrationName: string) => {
    setLoading(true);
    try {
      await axios.post(`/api/v1/integrations/${integrationName}/test`);
      await loadDashboardData();
    } catch (error) {
      console.error(`Failed to test ${integrationName}:`, error);
      setErr(`Failed to test connection for ${integrationName}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'disconnected':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      case 'disconnected':
        return <Error color="disabled" />;
      default:
        return <Info />;
    }
  };

  const getIntegrationIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'tally':
        return <AccountBalance />;
      case 'email':
        return <Email />;
      case 'calendar':
        return <CalendarToday />;
      case 'payment':
        return <Payment />;
      case 'zoho':
        return <Cloud />;
      default:
        return <Settings />;
    }
  };

  const renderIntegrationCard = (integration: IntegrationHealthStatus) => (
    <Card key={integration.integration_name} sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getIntegrationIcon(integration.integration_name)}
            <Typography variant="h6">
              {integration.integration_name}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getStatusIcon(integration.status)}
            <Chip 
              label={integration.status} 
              color={getStatusColor(integration.status) as any}
              size="small"
            />
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Last Sync: {integration.last_sync_at 
              ? new Date(integration.last_sync_at).toLocaleString()
              : 'Never'
            }
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Frequency: {integration.sync_frequency || 'Manual'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Errors: {integration.error_count}
          </Typography>
        </Box>

        {integration.performance_metrics && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              Performance Metrics:
            </Typography>
            {integration.performance_metrics.last_sync_duration && (
              <Typography variant="body2" fontSize="0.75rem">
                Last Sync: {integration.performance_metrics.last_sync_duration}
              </Typography>
            )}
            {integration.performance_metrics.records_synced && (
              <Typography variant="body2" fontSize="0.75rem">
                Records: {integration.performance_metrics.records_synced}
              </Typography>
            )}
            {integration.performance_metrics.avg_response_time && (
              <Typography variant="body2" fontSize="0.75rem">
                Response Time: {integration.performance_metrics.avg_response_time}
              </Typography>
            )}
          </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Tooltip title="Test Connection">
            <IconButton 
              size="small" 
              onClick={() => testConnection(integration.integration_name)}
              disabled={loading}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Sync Now">
            <IconButton 
              size="small" 
              onClick={() => syncIntegration(integration.integration_name)}
              disabled={loading}
            >
              <Sync />
            </IconButton>
          </Tooltip>
          <Tooltip title="Configure">
            <IconButton 
              size="small" 
              onClick={() => {
                setSelectedIntegration(integration.integration_name);
                setConfigDialogOpen(true);
              }}
            >
              <Settings />
            </IconButton>
          </Tooltip>
          <Tooltip title="View History">
            <IconButton 
              size="small"
              onClick={() => {
                // Navigate to integration history
              }}
            >
              <History />
            </IconButton>
          </Tooltip>
        </Box>
      </CardContent>
    </Card>
  );

  const renderSystemHealth = () => {
    if (!dashboardData?.system_health) {return null;}

    const { system_health } = dashboardData;

    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Timeline />
          System Health
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Database</Typography>
              <Typography variant="h6" color={system_health.database_status === 'healthy' ? 'success.main' : 'error.main'}>
                {system_health.database_status}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">API Response</Typography>
              <Typography variant="h6">
                {system_health.api_response_time}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Last Backup</Typography>
              <Typography variant="body2">
                {new Date(system_health.last_backup).toLocaleDateString()}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Storage Usage</Typography>
              <Typography variant="h6">
                {system_health.storage_usage}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    );
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="xl" 
      fullWidth
      PaperProps={{ sx: { minHeight: '80vh' } }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline />
            Integration Dashboard
          </Box>
          <Button
            startIcon={<Refresh />}
            onClick={loadDashboardData}
            disabled={loading}
          >
            Refresh All
          </Button>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && !dashboardData && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {err && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErr(null)}>
            {err}
          </Alert>
        )}

        {dashboardData && (
          <>
            {renderSystemHealth()}
            
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Settings />
              Active Integrations
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6} lg={4}>
                {renderIntegrationCard(dashboardData.tally_integration)}
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                {renderIntegrationCard(dashboardData.email_integration)}
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                {renderIntegrationCard(dashboardData.calendar_integration)}
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                {renderIntegrationCard(dashboardData.payment_integration)}
              </Grid>
              <Grid item xs={12} md={6} lg={4}>
                {renderIntegrationCard(dashboardData.zoho_integration)}
              </Grid>
            </Grid>

            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>Quick Actions</Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="outlined" startIcon={<Add />}>
                  Add Integration
                </Button>
                <Button variant="outlined" startIcon={<Security />}>
                  Manage Permissions
                </Button>
                <Button variant="outlined" startIcon={<Timeline />}>
                  View Analytics
                </Button>
              </Box>
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Configure {selectedIntegration}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Configuration interface for {selectedIntegration} would be loaded here.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default IntegrationDashboard;