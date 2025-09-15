// components/tenant/TenantConfigurationManager.tsx
/**
 * Multi-Tenancy Configuration Manager - Phase 2&3 Integration
 * 
 * Comprehensive tenant management with role-based access and configuration
 * Integrates with backend tenant_config.py for complete multi-tenancy support
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Language as LanguageIcon,
  People as PeopleIcon,
  Analytics as AnalyticsIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { rbacService } from '../../services/rbacService';

// Tenant configuration interfaces based on backend tenant_config.py
interface TenantPlan {
  name: string;
  max_users: number;
  storage_limit_gb: number;
  api_calls_per_hour: number;
  features: Record<string, boolean>;
}

interface TenantFeatures {
  advanced_reporting: boolean;
  custom_fields: boolean;
  api_access: boolean;
  email_notifications: boolean;
  audit_logs: boolean;
  custom_branding: boolean;
  integrations: boolean;
  backup_restore: boolean;
  ai_analytics: boolean;
  predictive_analytics: boolean;
  anomaly_detection: boolean;
  ai_insights: boolean;
  intelligent_automation: boolean;
  natural_language_processing: boolean;
}

interface TenantConfiguration {
  id: number;
  name: string;
  subdomain: string;
  plan: string;
  status: 'active' | 'suspended' | 'trial' | 'expired';
  created_at: string;
  updated_at: string;
  features: TenantFeatures;
  limits: {
    max_users: number;
    storage_limit_gb: number;
    api_calls_per_hour: number;
  };
  usage: {
    current_users: number;
    storage_used_gb: number;
    api_calls_today: number;
  };
  localization: {
    language: string;
    currency: string;
    timezone: string;
    date_format: string;
  };
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
      id={`tenant-tabpanel-${index}`}
      aria-labelledby={`tenant-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Mock tenant service (replace with actual API calls)
const tenantService = {
  getTenantConfigurations: async (): Promise<TenantConfiguration[]> => {
    // Mock data - replace with actual API call
    return [
      {
        id: 1,
        name: "Acme Corporation",
        subdomain: "acme",
        plan: "enterprise",
        status: "active",
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-15T00:00:00Z",
        features: {
          advanced_reporting: true,
          custom_fields: true,
          api_access: true,
          email_notifications: true,
          audit_logs: true,
          custom_branding: true,
          integrations: true,
          backup_restore: true,
          ai_analytics: true,
          predictive_analytics: true,
          anomaly_detection: true,
          ai_insights: true,
          intelligent_automation: true,
          natural_language_processing: true,
        },
        limits: {
          max_users: 999,
          storage_limit_gb: 100,
          api_calls_per_hour: 10000,
        },
        usage: {
          current_users: 45,
          storage_used_gb: 23.5,
          api_calls_today: 1250,
        },
        localization: {
          language: "en",
          currency: "USD",
          timezone: "America/New_York",
          date_format: "MM/DD/YYYY",
        },
      },
    ];
  },

  updateTenantConfiguration: async (
    tenantId: number,
    config: Partial<TenantConfiguration>
  ): Promise<TenantConfiguration> => {
    // Mock implementation
    console.log('Updating tenant configuration:', tenantId, config);
    throw new Error('Update tenant configuration API not implemented');
  },
};

const TenantOverviewPanel: React.FC<{ tenant: TenantConfiguration }> = ({ tenant }) => {
  const storagePercentage = (tenant.usage.storage_used_gb / tenant.limits.storage_limit_gb) * 100;
  const userPercentage = (tenant.usage.current_users / tenant.limits.max_users) * 100;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Tenant Information" />
          <CardContent>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">Name</Typography>
              <Typography variant="h6">{tenant.name}</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">Subdomain</Typography>
              <Typography variant="body1">{tenant.subdomain}</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">Plan</Typography>
              <Chip label={tenant.plan} color="primary" size="small" />
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">Status</Typography>
              <Chip 
                label={tenant.status} 
                color={tenant.status === 'active' ? 'success' : 'warning'} 
                size="small" 
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Usage Statistics" />
          <CardContent>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Users ({tenant.usage.current_users} / {tenant.limits.max_users})
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={userPercentage} 
                color={userPercentage > 80 ? 'warning' : 'primary'}
              />
              <Typography variant="caption" color="textSecondary">
                {userPercentage.toFixed(1)}% used
              </Typography>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Storage ({tenant.usage.storage_used_gb}GB / {tenant.limits.storage_limit_gb}GB)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={storagePercentage} 
                color={storagePercentage > 80 ? 'warning' : 'primary'}
              />
              <Typography variant="caption" color="textSecondary">
                {storagePercentage.toFixed(1)}% used
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                API Calls Today
              </Typography>
              <Typography variant="h6" color="primary">
                {tenant.usage.api_calls_today.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Limit: {tenant.limits.api_calls_per_hour.toLocaleString()}/hour
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

const TenantFeaturesPanel: React.FC<{ tenant: TenantConfiguration }> = ({ tenant }) => {
  const [editMode, setEditMode] = useState(false);
  const [features, setFeatures] = useState(tenant.features);

  const handleFeatureToggle = (feature: keyof TenantFeatures) => {
    setFeatures(prev => ({
      ...prev,
      [feature]: !prev[feature],
    }));
  };

  const handleSave = () => {
    // Save changes
    console.log('Saving features:', features);
    setEditMode(false);
  };

  const handleCancel = () => {
    setFeatures(tenant.features);
    setEditMode(false);
  };

  const featureGroups = [
    {
      title: 'Core Features',
      features: ['advanced_reporting', 'custom_fields', 'api_access', 'email_notifications'],
    },
    {
      title: 'Security & Compliance',
      features: ['audit_logs', 'custom_branding', 'backup_restore'],
    },
    {
      title: 'Integrations',
      features: ['integrations'],
    },
    {
      title: 'AI & Analytics',
      features: ['ai_analytics', 'predictive_analytics', 'anomaly_detection', 'ai_insights', 'intelligent_automation', 'natural_language_processing'],
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Feature Configuration</Typography>
        <Box>
          {editMode ? (
            <>
              <Button onClick={handleSave} variant="contained" startIcon={<SaveIcon />} sx={{ mr: 1 }}>
                Save
              </Button>
              <Button onClick={handleCancel} variant="outlined" startIcon={<CancelIcon />}>
                Cancel
              </Button>
            </>
          ) : (
            <Button onClick={() => setEditMode(true)} variant="outlined" startIcon={<EditIcon />}>
              Edit Features
            </Button>
          )}
        </Box>
      </Box>

      {featureGroups.map((group) => (
        <Accordion key={group.title} defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">{group.title}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {group.features.map((feature) => (
                <Grid item xs={12} sm={6} md={4} key={feature}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={features[feature as keyof TenantFeatures]}
                        onChange={() => handleFeatureToggle(feature as keyof TenantFeatures)}
                        disabled={!editMode}
                      />
                    }
                    label={feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  />
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

const TenantLocalizationPanel: React.FC<{ tenant: TenantConfiguration }> = ({ tenant }) => {
  const [editMode, setEditMode] = useState(false);
  const [localization, setLocalization] = useState(tenant.localization);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'hi', name: 'Hindi' },
  ];

  const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR'];
  const timezones = [
    'America/New_York',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Kolkata',
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Localization Settings</Typography>
        <Box>
          {editMode ? (
            <>
              <Button variant="contained" startIcon={<SaveIcon />} sx={{ mr: 1 }}>
                Save
              </Button>
              <Button variant="outlined" startIcon={<CancelIcon />} onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </>
          ) : (
            <Button onClick={() => setEditMode(true)} variant="outlined" startIcon={<EditIcon />}>
              Edit Localization
            </Button>
          )}
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Language</InputLabel>
            <Select
              value={localization.language}
              onChange={(e) => setLocalization(prev => ({ ...prev, language: e.target.value }))}
              disabled={!editMode}
            >
              {languages.map((lang) => (
                <MenuItem key={lang.code} value={lang.code}>
                  {lang.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Currency</InputLabel>
            <Select
              value={localization.currency}
              onChange={(e) => setLocalization(prev => ({ ...prev, currency: e.target.value }))}
              disabled={!editMode}
            >
              {currencies.map((currency) => (
                <MenuItem key={currency} value={currency}>
                  {currency}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Timezone</InputLabel>
            <Select
              value={localization.timezone}
              onChange={(e) => setLocalization(prev => ({ ...prev, timezone: e.target.value }))}
              disabled={!editMode}
            >
              {timezones.map((tz) => (
                <MenuItem key={tz} value={tz}>
                  {tz}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            margin="normal"
            label="Date Format"
            value={localization.date_format}
            onChange={(e) => setLocalization(prev => ({ ...prev, date_format: e.target.value }))}
            disabled={!editMode}
            helperText="e.g., MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

const TenantConfigurationManager: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedTenant, setSelectedTenant] = useState<TenantConfiguration | null>(null);

  // Check user permissions
  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
  });

  // Fetch tenant configurations
  const { data: tenants = [], isLoading, error } = useQuery({
    queryKey: ['tenantConfigurations'],
    queryFn: tenantService.getTenantConfigurations,
    enabled: !!user && (userPermissions.includes('admin') || user?.role === 'super_admin'),
  });

  const canManageTenants = user?.role === 'super_admin' || userPermissions.includes('tenant_management');

  useEffect(() => {
    if (tenants.length > 0 && !selectedTenant) {
      setSelectedTenant(tenants[0]);
    }
  }, [tenants, selectedTenant]);

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Authentication required to access tenant management</Alert>
      </Container>
    );
  }

  if (!canManageTenants) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">
          Access denied. Super admin or tenant management permissions required.
        </Alert>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>Loading tenant configurations...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Failed to load tenant configurations</Alert>
      </Container>
    );
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <BusinessIcon color="primary" fontSize="large" />
          <Typography variant="h4" component="h1">
            Tenant Configuration Manager
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />}>
          Add Tenant
        </Button>
      </Box>

      {/* Tenant Selection */}
      {tenants.length > 1 && (
        <Paper sx={{ mb: 3, p: 2 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Select Tenant</InputLabel>
            <Select
              value={selectedTenant?.id || ''}
              onChange={(e) => {
                const tenant = tenants.find(t => t.id === e.target.value);
                setSelectedTenant(tenant || null);
              }}
            >
              {tenants.map((tenant) => (
                <MenuItem key={tenant.id} value={tenant.id}>
                  {tenant.name} ({tenant.subdomain})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Paper>
      )}

      {/* Tenant Management Tabs */}
      {selectedTenant && (
        <>
          <Paper sx={{ mb: 3 }}>
            <Tabs value={selectedTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
              <Tab icon={<AnalyticsIcon />} label="Overview" />
              <Tab icon={<SettingsIcon />} label="Features" />
              <Tab icon={<LanguageIcon />} label="Localization" />
              <Tab icon={<SecurityIcon />} label="Security" />
              <Tab icon={<PeopleIcon />} label="Users" />
            </Tabs>
          </Paper>

          <TabPanel value={selectedTab} index={0}>
            <TenantOverviewPanel tenant={selectedTenant} />
          </TabPanel>

          <TabPanel value={selectedTab} index={1}>
            <TenantFeaturesPanel tenant={selectedTenant} />
          </TabPanel>

          <TabPanel value={selectedTab} index={2}>
            <TenantLocalizationPanel tenant={selectedTenant} />
          </TabPanel>

          <TabPanel value={selectedTab} index={3}>
            <Alert severity="info">Security configuration panel - Implementation pending</Alert>
          </TabPanel>

          <TabPanel value={selectedTab} index={4}>
            <Alert severity="info">User management panel - Implementation pending</Alert>
          </TabPanel>
        </>
      )}
    </Container>
  );
};

export default TenantConfigurationManager;