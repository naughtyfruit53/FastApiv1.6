// components/analytics/UnifiedAnalyticsDashboard.tsx
/**
 * Unified Analytics Dashboard - Phase 2&3 Integration
 * 
 * Consolidates all analytics modules into a single comprehensive interface
 * Supports role-based access, multi-tenancy, and real-time data
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Skeleton,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  ShoppingCart as ShoppingCartIcon,
  Build as BuildIcon,
  AccountBalance as FinanceIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { rbacService } from '../../services/rbacService';
import { analyticsService } from '../../services/analyticsService';

// Analytics module interfaces
interface AnalyticsModule {
  id: string;
  name: string;
  icon: React.ReactNode;
  permissions: string[];
  component: React.ComponentType<any>;
  enabled: boolean;
}

interface DashboardMetrics {
  totalCustomers: number;
  totalSales: number;
  totalRevenue: number;
  activeProjects: number;
  pendingTasks: number;
  lastUpdated: string;
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
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Analytics module components
const CustomerAnalyticsPanel: React.FC = () => {
  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['customerAnalytics'],
    queryFn: analyticsService.getDashboardMetrics,
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });

  if (isLoading) return <Skeleton variant="rectangular" height={300} />;
  if (error) return <Alert severity="error">Failed to load customer analytics</Alert>;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Customer Overview" />
          <CardContent>
            <Typography variant="h4" color="primary">
              {metrics?.total_customers || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Customers
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardHeader title="Recent Activity" />
          <CardContent>
            <Typography variant="h4" color="secondary">
              {metrics?.total_interactions_today || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Interactions Today
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

const SalesAnalyticsPanel: React.FC = () => (
  <Alert severity="info">
    Sales Analytics Panel - Connect to sales endpoints
  </Alert>
);

const ServiceAnalyticsPanel: React.FC = () => (
  <Alert severity="info">
    Service Analytics Panel - Connect to service endpoints
  </Alert>
);

const FinanceAnalyticsPanel: React.FC = () => (
  <Alert severity="info">
    Finance Analytics Panel - Connect to finance endpoints
  </Alert>
);

const ProjectAnalyticsPanel: React.FC = () => (
  <Alert severity="info">
    Project Analytics Panel - Connect to project endpoints
  </Alert>
);

const UnifiedAnalyticsDashboard: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  const [selectedTab, setSelectedTab] = useState(0);
  const [realTimeEnabled, setRealTimeEnabled] = useState(true);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);

  // Check user permissions for analytics modules
  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
  });

  // Define analytics modules with permissions
  const analyticsModules: AnalyticsModule[] = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: <DashboardIcon />,
      permissions: [],
      component: CustomerAnalyticsPanel,
      enabled: true,
    },
    {
      id: 'customer',
      name: 'Customer',
      icon: <PeopleIcon />,
      permissions: ['crm_view', 'customer_analytics_view'],
      component: CustomerAnalyticsPanel,
      enabled: true,
    },
    {
      id: 'sales',
      name: 'Sales',
      icon: <ShoppingCartIcon />,
      permissions: ['sales_view', 'sales_analytics_view'],
      component: SalesAnalyticsPanel,
      enabled: true,
    },
    {
      id: 'service',
      name: 'Service',
      icon: <BuildIcon />,
      permissions: ['service_view', 'service_analytics_view'],
      component: ServiceAnalyticsPanel,
      enabled: true,
    },
    {
      id: 'finance',
      name: 'Finance',
      icon: <FinanceIcon />,
      permissions: ['finance_view', 'finance_analytics_view'],
      component: FinanceAnalyticsPanel,
      enabled: true,
    },
    {
      id: 'projects',
      name: 'Projects',
      icon: <TrendingUpIcon />,
      permissions: ['project_view', 'project_analytics_view'],
      component: ProjectAnalyticsPanel,
      enabled: true,
    },
  ];

  // Filter modules based on user permissions
  const availableModules = analyticsModules.filter(module => {
    if (module.permissions.length === 0) return true; // Always accessible modules
    return module.permissions.some(permission => userPermissions.includes(permission));
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['analytics'] });
    queryClient.invalidateQueries({ queryKey: ['customerAnalytics'] });
  };

  const handleFilter = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleExport = () => {
    // Export functionality
    console.log('Exporting analytics data...');
  };

  useEffect(() => {
    // Set up real-time updates if enabled
    if (realTimeEnabled) {
      const interval = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['analytics'] });
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [realTimeEnabled, queryClient]);

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Authentication required to access analytics dashboard</Alert>
      </Container>
    );
  }

  if (availableModules.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">
          No analytics modules available. Contact your administrator to request analytics permissions.
        </Alert>
      </Container>
    );
  }

  const ActiveComponent = availableModules[selectedTab]?.component || CustomerAnalyticsPanel;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AnalyticsIcon color="primary" fontSize="large" />
          <Typography variant="h4" component="h1">
            Analytics Dashboard
          </Typography>
          <Chip 
            label={user.organization_id ? `Org: ${user.organization_id}` : 'Platform'} 
            size="small" 
            variant="outlined" 
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FormControlLabel
            control={
              <Switch
                checked={realTimeEnabled}
                onChange={(e) => setRealTimeEnabled(e.target.checked)}
                size="small"
              />
            }
            label="Real-time"
            sx={{ mr: 1 }}
          />
          
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Filter">
            <IconButton onClick={handleFilter} size="small">
              <FilterIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Export">
            <IconButton onClick={handleExport} size="small">
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
      >
        <MenuItem onClick={handleFilterClose}>Last 7 days</MenuItem>
        <MenuItem onClick={handleFilterClose}>Last 30 days</MenuItem>
        <MenuItem onClick={handleFilterClose}>Last 90 days</MenuItem>
        <MenuItem onClick={handleFilterClose}>Custom range</MenuItem>
      </Menu>

      {/* Analytics Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="analytics modules"
        >
          {availableModules.map((module, index) => (
            <Tab
              key={module.id}
              icon={module.icon}
              label={module.name}
              id={`analytics-tab-${index}`}
              aria-controls={`analytics-tabpanel-${index}`}
              sx={{ minHeight: 72 }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* Analytics Content */}
      {availableModules.map((module, index) => (
        <TabPanel key={module.id} value={selectedTab} index={index}>
          <ActiveComponent />
        </TabPanel>
      ))}

      {/* Organization Context Info */}
      {user.organization_id && (
        <Box sx={{ mt: 3 }}>
          <Alert severity="info" sx={{ backgroundColor: 'rgba(2, 136, 209, 0.1)' }}>
            <Typography variant="body2">
              Analytics data is scoped to your organization (ID: {user.organization_id}). 
              {user.role === 'super_admin' && ' Super admin access allows cross-organization analytics.'}
            </Typography>
          </Alert>
        </Box>
      )}
    </Container>
  );
};

export default UnifiedAnalyticsDashboard;