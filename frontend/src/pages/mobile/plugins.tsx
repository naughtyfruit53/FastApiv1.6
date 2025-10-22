// frontend/src/pages/mobile/plugins.tsx
/**
 * Mobile-Optimized Plugins Page
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
  Extension,
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
import ModernLoading from '../../components/ModernLoading';

interface Plugin {
  id: number;
  name: string;
  version: string;
  description: string;
  author: string;
  enabled: boolean;
  status: 'active' | 'inactive' | 'error';
}

const MobilePluginsPage: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = () => {
    setLoading(true);
    // Mock data for demonstration
    setTimeout(() => {
      setPlugins([
        {
          id: 1,
          name: 'Payment Gateway',
          version: '1.2.0',
          description: 'Multiple payment gateway integration',
          author: 'Platform Team',
          enabled: true,
          status: 'active',
        },
        {
          id: 2,
          name: 'Advanced Reporting',
          version: '2.0.1',
          description: 'Comprehensive reports and analytics',
          author: 'Analytics Team',
          enabled: true,
          status: 'active',
        },
        {
          id: 3,
          name: 'Email Marketing',
          version: '1.5.0',
          description: 'Email marketing automation',
          author: 'Marketing Team',
          enabled: false,
          status: 'inactive',
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const handleToggle = (pluginId: number, enabled: boolean) => {
    setPlugins(plugins.map(p =>
      p.id === pluginId ? { ...p, enabled, status: enabled ? 'active' as const : 'inactive' as const } : p
    ));
    setAlert({
      type: 'success',
      message: `Plugin ${enabled ? 'enabled' : 'disabled'} successfully`,
    });
  };

  const filteredPlugins = plugins.filter((plugin) =>
    plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    plugin.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  const rightActions = (
    <IconButton
      onClick={loadPlugins}
      disabled={loading}
      sx={{ minWidth: 44, minHeight: 44 }}
    >
      <Refresh />
    </IconButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Plugins"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="list"
          count={5}
          message="Loading plugins..."
        />
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Plugins"
      subtitle={`${plugins.length} plugin${plugins.length !== 1 ? 's' : ''} installed`}
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
        placeholder="Search plugins..."
      />

      {/* Summary Cards */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, overflowX: 'auto' }}>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="primary">
            {plugins.length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Installed
          </Typography>
        </MobileCard>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="success.main">
            {plugins.filter((p) => p.enabled).length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Active
          </Typography>
        </MobileCard>
        <MobileCard sx={{ minWidth: 120, flex: 1 }}>
          <Typography variant="h4" color="text.secondary">
            {plugins.filter((p) => !p.enabled).length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Inactive
          </Typography>
        </MobileCard>
      </Box>

      {/* Plugins List */}
      <MobileCard>
        {filteredPlugins.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              {searchQuery ? 'No matching plugins' : 'No plugins installed'}
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {filteredPlugins.map((plugin, index) => (
              <React.Fragment key={plugin.id}>
                {index > 0 && <Box sx={{ borderTop: 1, borderColor: 'divider' }} />}
                <ListItem
                  sx={{
                    py: 2,
                    px: 0,
                    display: 'flex',
                    alignItems: 'flex-start',
                  }}
                >
                  <ListItemAvatar>
                    <Avatar
                      sx={{
                        bgcolor: plugin.enabled ? 'primary.main' : 'grey.400',
                        mt: 0.5,
                      }}
                    >
                      <Extension />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {plugin.name}
                          </Typography>
                          <Chip
                            label={plugin.status}
                            size="small"
                            color={getStatusColor(plugin.status)}
                            icon={plugin.status === 'active' ? <CheckCircle /> : <Error />}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary" display="block">
                          v{plugin.version} • {plugin.author}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {plugin.description}
                      </Typography>
                    }
                  />
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', ml: 1 }}>
                    <Switch
                      checked={plugin.enabled}
                      onChange={(e) => handleToggle(plugin.id, e.target.checked)}
                      size="small"
                    />
                    <IconButton
                      size="small"
                      sx={{ minWidth: 36, minHeight: 36 }}
                    >
                      <ChevronRight fontSize="small" />
                    </IconButton>
                  </Box>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobilePluginsPage;
