// frontend/src/pages/mobile/integrations.tsx
/**
 * Mobile-Optimized Integrations Page
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Switch,
  IconButton,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Refresh,
  ChevronRight,
} from '@mui/icons-material';
import {
  MobileDashboardLayout,
  MobileCard,
  MobileSearchBar,
} from '../../components/mobile';
import integrationService, { IntegrationConfig } from '../../services/integrationService';
import ModernLoading from '../../components/ModernLoading';

const MobileIntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const data = await integrationService.getAllIntegrations();
      setIntegrations(data);
    } catch (_error: any) {
      setAlert({ type: 'error', message: 'Failed to load integrations' });
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      if (enabled) {
        await integrationService.enableIntegration(id);
      } else {
        await integrationService.disableIntegration(id);
      }
      loadIntegrations();
      setAlert({ type: 'success', message: `Integration ${enabled ? 'enabled' : 'disabled'}` });
    } catch (error: any) {
      setAlert({ type: 'error', message: 'Failed to update integration' });
    }
  };

  const filteredIntegrations = integrations.filter((integration) =>
    integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    integration.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getIntegrationIcon = (type: string) => {
    const icons: Record<string, string> = {
      slack: '💬',
      whatsapp: '📱',
      google_workspace: '🌐',
      custom: '🔌',
    };
    return icons[type] || '🔌';
  };

  const rightActions = (
    <IconButton
      onClick={loadIntegrations}
      disabled={loading}
      sx={{ minWidth: 44, minHeight: 44 }}
    >
      <Refresh />
    </IconButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Integrations"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="list"
          count={5}
          message="Loading integrations..."
        />
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Integrations"
      subtitle={`${integrations.length} integration${integrations.length !== 1 ? 's' : ''}`}
      rightActions={rightActions}
      showBottomNav={true}
    >
      {alert && (
        <Alert
          severity={alert.type}
          onClose={() => setAlert(null)}
          sx={{ mb: 2, borderRadius: 2 }}
        >
          {alert.message}
        </Alert>
      )}

      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search integrations..."
      />

      {/* Summary Cards */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, overflowX: 'auto' }}>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="primary">
            {integrations.length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total
          </Typography>
        </MobileCard>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="success.main">
            {integrations.filter((i) => i.enabled).length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Active
          </Typography>
        </MobileCard>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="text.secondary">
            {integrations.filter((i) => !i.enabled).length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Inactive
          </Typography>
        </MobileCard>
      </Box>

      {/* Integrations List */}
      <MobileCard>
        {filteredIntegrations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              {searchQuery ? 'No matching integrations' : 'No integrations configured'}
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {filteredIntegrations.map((integration, index) => (
              <React.Fragment key={integration.id}>
                {index > 0 && <Box sx={{ borderTop: 1, borderColor: 'divider' }} />}
                <ListItem
                  sx={{
                    py: 2,
                    px: 0,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: integration.enabled ? 'primary.main' : 'grey.400' }}>
                      {getIntegrationIcon(integration.type)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {integration.name}
                        </Typography>
                        <Chip
                          label={integration.enabled ? 'Active' : 'Inactive'}
                          size="small"
                          color={integration.enabled ? 'success' : 'default'}
                          icon={integration.enabled ? <CheckCircle /> : <Error />}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {integration.type.replace('_', ' ')}
                      </Typography>
                    }
                  />
                  <Switch
                    checked={integration.enabled}
                    onChange={(e) => handleToggle(integration.id!, e.target.checked)}
                    size="small"
                  />
                  <IconButton
                    size="small"
                    sx={{ ml: 1, minWidth: 36, minHeight: 36 }}
                  >
                    <ChevronRight />
                  </IconButton>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileIntegrationsPage;
