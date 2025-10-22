// frontend/src/pages/plugins/index.tsx
/**
 * Plugin Management Page
 * Manage system plugins and extensions
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
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  Paper,
} from '@mui/material';
import {
  Add,
  Settings,
  Delete,
  CheckCircle,
  Error,
  Refresh,
  Extension,
  Info,
  CloudUpload,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';

interface Plugin {
  id: number;
  name: string;
  version: string;
  description: string;
  author: string;
  enabled: boolean;
  status: 'active' | 'inactive' | 'error';
  dependencies?: string[];
  config?: Record<string, any>;
  installed_at: string;
  updated_at?: string;
}

const PluginsPage: React.FC = () => {
  const { user } = useAuth();
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    // Simulate API call with mock data
    setTimeout(() => {
      setPlugins([
        {
          id: 1,
          name: 'Payment Gateway Plugin',
          version: '1.2.0',
          description: 'Integrate multiple payment gateways including Stripe, PayPal, and Square',
          author: 'Platform Team',
          enabled: true,
          status: 'active',
          dependencies: ['core-api'],
          installed_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 2,
          name: 'Advanced Reporting',
          version: '2.0.1',
          description: 'Generate comprehensive reports with advanced analytics',
          author: 'Analytics Team',
          enabled: true,
          status: 'active',
          dependencies: ['analytics-service'],
          installed_at: '2024-02-01T14:30:00Z',
        },
        {
          id: 3,
          name: 'Email Marketing Suite',
          version: '1.5.0',
          description: 'Full-featured email marketing automation and campaign management',
          author: 'Marketing Team',
          enabled: false,
          status: 'inactive',
          dependencies: ['email-service'],
          installed_at: '2024-03-10T09:15:00Z',
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const handleTogglePlugin = (pluginId: number, enabled: boolean) => {
    setPlugins(plugins.map(p => 
      p.id === pluginId ? { ...p, enabled, status: enabled ? 'active' : 'inactive' } : p
    ));
    setAlert({ 
      type: 'success', 
      message: `Plugin ${enabled ? 'enabled' : 'disabled'} successfully` 
    });
  };

  const handleDeletePlugin = (pluginId: number) => {
    if (!confirm('Are you sure you want to uninstall this plugin?')) return;
    
    setPlugins(plugins.filter(p => p.id !== pluginId));
    setAlert({ type: 'success', message: 'Plugin uninstalled successfully' });
  };

  const handleConfigurePlugin = (plugin: Plugin) => {
    setSelectedPlugin(plugin);
    setDialogOpen(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Plugin Management</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<CloudUpload />}
            onClick={() => setAlert({ type: 'info', message: 'Plugin upload feature coming soon' })}
          >
            Upload Plugin
          </Button>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={loadPlugins}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {alert && (
        <Alert severity={alert.type} onClose={() => setAlert(null)} sx={{ mb: 3 }}>
          {alert.message}
        </Alert>
      )}

      {/* Plugin Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary">{plugins.length}</Typography>
            <Typography variant="body2" color="text.secondary">Total Plugins</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="success.main">
              {plugins.filter(p => p.enabled).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">Active Plugins</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="text.secondary">
              {plugins.filter(p => !p.enabled).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">Inactive Plugins</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Plugin List */}
      <Grid container spacing={3}>
        {plugins.map((plugin) => (
          <Grid item xs={12} md={6} lg={4} key={plugin.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    <Extension />
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">{plugin.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      v{plugin.version}
                    </Typography>
                  </Box>
                  <Chip
                    label={plugin.status}
                    size="small"
                    color={getStatusColor(plugin.status)}
                    icon={plugin.status === 'active' ? <CheckCircle /> : <Error />}
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" paragraph>
                  {plugin.description}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="caption" color="text.secondary" display="block">
                  Author: {plugin.author}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Installed: {new Date(plugin.installed_at).toLocaleDateString()}
                </Typography>

                {plugin.dependencies && plugin.dependencies.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Dependencies:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                      {plugin.dependencies.map((dep, idx) => (
                        <Chip key={idx} label={dep} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>

              <CardActions>
                <FormControlLabel
                  control={
                    <Switch
                      checked={plugin.enabled}
                      onChange={(e) => handleTogglePlugin(plugin.id, e.target.checked)}
                    />
                  }
                  label="Enabled"
                />
                <Box sx={{ flexGrow: 1 }} />
                <IconButton
                  size="small"
                  onClick={() => handleConfigurePlugin(plugin)}
                  title="Configure"
                >
                  <Settings />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDeletePlugin(plugin.id)}
                  title="Uninstall"
                >
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}

        {plugins.length === 0 && !loading && (
          <Grid item xs={12}>
            <Alert severity="info">
              No plugins installed. Upload a plugin to get started.
            </Alert>
          </Grid>
        )}
      </Grid>

      {/* Configure Plugin Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>Configure {selectedPlugin?.name}</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Plugin configuration UI will be dynamically generated based on plugin schema.
          </Alert>
          {selectedPlugin && (
            <List>
              <ListItem>
                <ListItemText 
                  primary="Version" 
                  secondary={selectedPlugin.version} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Status" 
                  secondary={selectedPlugin.status} 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Author" 
                  secondary={selectedPlugin.author} 
                />
              </ListItem>
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => {
            setAlert({ type: 'success', message: 'Configuration saved' });
            setDialogOpen(false);
          }}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PluginsPage;
