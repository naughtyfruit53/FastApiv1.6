// frontend/src/pages/integrations/index.tsx
/**
 * Integrations Management Page
 * Manage external service integrations (Slack, WhatsApp, Google Workspace)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add,
  Delete,
  CheckCircle,
  Error,
  Refresh,
  Send,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { ProtectedPage } from '../../components/ProtectedPage';
import integrationService, {
  IntegrationConfig,
} from '../../services/integrationService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const IntegrationsPage: React.FC = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [integrations, setIntegrations] = useState<IntegrationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentIntegrationType, setCurrentIntegrationType] = useState<string>('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const data = await integrationService.getAllIntegrations();
      setIntegrations(data);
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Failed to load integrations' });
    } finally {
      setLoading(false);
    }
  };

  const handleAddIntegration = (type: string) => {
    setCurrentIntegrationType(type);
    setDialogOpen(true);
  };

  const handleDeleteIntegration = async (id: number) => {
    if (!confirm('Are you sure you want to delete this integration?')) return;
    
    try {
      await integrationService.deleteIntegration(id);
      setAlert({ type: 'success', message: 'Integration deleted successfully' });
      loadIntegrations();
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Failed to delete integration' });
    }
  };

  const handleToggleIntegration = async (id: number, enabled: boolean) => {
    try {
      if (enabled) {
        await integrationService.enableIntegration(id);
      } else {
        await integrationService.disableIntegration(id);
      }
      setAlert({ type: 'success', message: `Integration ${enabled ? 'enabled' : 'disabled'} successfully` });
      loadIntegrations();
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Failed to toggle integration' });
    }
  };

  const handleTestIntegration = async (id: number, type: string) => {
    try {
      let result;
      if (type === 'slack') {
        result = await integrationService.testSlackConnection(id);
      } else if (type === 'whatsapp') {
        result = await integrationService.testWhatsAppConnection(id);
      }
      setAlert({ 
        type: result?.success ? 'success' : 'error', 
        message: result?.message || 'Test completed' 
      });
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Test failed' });
    }
  };

  const renderIntegrationCard = (integration: IntegrationConfig) => (
    <Card key={integration.id}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{integration.name}</Typography>
          <Chip
            label={integration.enabled ? 'Active' : 'Inactive'}
            color={integration.enabled ? 'success' : 'default'}
            size="small"
            icon={integration.enabled ? <CheckCircle /> : <Error />}
          />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Type: {integration.type}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Created: {new Date(integration.created_at || '').toLocaleDateString()}
        </Typography>
      </CardContent>
      <CardActions>
        <FormControlLabel
          control={
            <Switch
              checked={integration.enabled}
              onChange={(e) => handleToggleIntegration(integration.id!, e.target.checked)}
            />
          }
          label="Enabled"
        />
        <IconButton
          size="small"
          onClick={() => handleTestIntegration(integration.id!, integration.type)}
        >
          <Send />
        </IconButton>
        <IconButton
          size="small"
          onClick={() => handleDeleteIntegration(integration.id!)}
        >
          <Delete />
        </IconButton>
      </CardActions>
    </Card>
  );

  const slackIntegrations = integrations.filter((i) => i.type === 'slack');
  const whatsappIntegrations = integrations.filter((i) => i.type === 'whatsapp');
  const googleIntegrations = integrations.filter((i) => i.type === 'google_workspace');

  return (
    <ProtectedPage moduleKey="admin" action="read">
      ontainer maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Integrations</Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={loadIntegrations}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 3 }}>
          {alert.message}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(_e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="Slack" />
        <Tab label="WhatsApp" />
        <Tab label="Google Workspace" />
        <Tab label="All Integrations" />
      </Tabs>

      {/* Slack Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleAddIntegration('slack')}
          >
            Add Slack Integration
          </Button>
        </Box>
        <Grid container spacing={3}>
          {slackIntegrations.map((integration) => (
            <Grid item xs={12} md={6} lg={4} key={integration.id}>
              {renderIntegrationCard(integration)}
            </Grid>
          ))}
          {slackIntegrations.length === 0 && (
            <Grid item xs={12}>
              <Alert severity="info">No Slack integrations configured</Alert>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* WhatsApp Tab */}
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleAddIntegration('whatsapp')}
          >
            Add WhatsApp Integration
          </Button>
        </Box>
        <Grid container spacing={3}>
          {whatsappIntegrations.map((integration) => (
            <Grid item xs={12} md={6} lg={4} key={integration.id}>
              {renderIntegrationCard(integration)}
            </Grid>
          ))}
          {whatsappIntegrations.length === 0 && (
            <Grid item xs={12}>
              <Alert severity="info">No WhatsApp integrations configured</Alert>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* Google Workspace Tab */}
      <TabPanel value={tabValue} index={2}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleAddIntegration('google_workspace')}
          >
            Add Google Workspace Integration
          </Button>
        </Box>
        <Grid container spacing={3}>
          {googleIntegrations.map((integration) => (
            <Grid item xs={12} md={6} lg={4} key={integration.id}>
              {renderIntegrationCard(integration)}
            </Grid>
          ))}
          {googleIntegrations.length === 0 && (
            <Grid item xs={12}>
              <Alert severity="info">No Google Workspace integrations configured</Alert>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* All Integrations Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          {integrations.map((integration) => (
            <Grid item xs={12} md={6} lg={4} key={integration.id}>
              {renderIntegrationCard(integration)}
            </Grid>
          ))}
          {integrations.length === 0 && (
            <Grid item xs={12}>
              <Alert severity="info">No integrations configured</Alert>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* Add Integration Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add {currentIntegrationType} Integration</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Integration configuration UI will be implemented in the next phase.
            Please use the API directly for now.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
    </ProtectedPage>
  );
};
export default IntegrationsPage;
