import React, { useState } from 'react';
import { Box, Grid, Typography, Chip, List, ListItem, ListItemIcon, ListItemText, Alert } from '@mui/material';
import { 
  AdminPanelSettings, 
  People, 
  Business, 
  Security, 
  Notifications,
  Analytics,
  Settings,
  Add,
  ManageAccounts,
  Shield,
  Backup,
  BugReport
} from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileSearchBar,
  MobilePullToRefresh,
  MobileBottomSheet,
  MobileContextualActions
} from '../../components/mobile';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { useAuth } from '../../context/AuthContext';
import ModernLoading from "../../components/ModernLoading";

// Mock data - TODO: Replace with real API integration
const mockAdminStats = {
  total_users: 145,
  active_users: 132,
  total_organizations: 28,
  active_organizations: 25,
  system_health: 98.5,
  storage_used: 67.3,
  recent_alerts: 3,
  pending_approvals: 8
};

const mockRecentActivity = [
  {
    id: 1,
    type: 'user_created',
    description: 'New user registered: john.doe@company.com',
    timestamp: '2024-01-25T10:30:00Z',
    severity: 'info'
  },
  {
    id: 2,
    type: 'security_alert',
    description: 'Multiple failed login attempts detected',
    timestamp: '2024-01-25T09:15:00Z',
    severity: 'warning'
  },
  {
    id: 3,
    type: 'system_update',
    description: 'System backup completed successfully',
    timestamp: '2024-01-25T08:00:00Z',
    severity: 'success'
  }
];

const adminModules = [
  {
    id: 'users',
    title: 'User Management',
    description: 'Manage users and permissions',
    icon: <People />,
    path: '/admin/users',
    badge: `${mockAdminStats.total_users} users`,
    color: 'primary'
  },
  {
    id: 'organizations',
    title: 'Organizations',
    description: 'Manage organizations and licenses',
    icon: <Business />,
    path: '/admin/organizations',
    badge: `${mockAdminStats.total_organizations} orgs`,
    color: 'secondary'
  },
  {
    id: 'rbac',
    title: 'Roles & Permissions',
    description: 'Configure role-based access',
    icon: <Security />,
    path: '/admin/rbac',
    badge: 'RBAC',
    color: 'warning'
  },
  {
    id: 'notifications',
    title: 'Notifications',
    description: 'System notifications and alerts',
    icon: <Notifications />,
    path: '/admin/notifications',
    badge: `${mockAdminStats.recent_alerts} alerts`,
    color: 'error'
  },
  {
    id: 'analytics',
    title: 'System Analytics',
    description: 'Platform usage and performance',
    icon: <Analytics />,
    path: '/admin/analytics',
    badge: 'Insights',
    color: 'info'
  },
  {
    id: 'settings',
    title: 'System Settings',
    description: 'Global system configuration',
    icon: <Settings />,
    path: '/admin/settings',
    badge: 'Config',
    color: 'success'
  }
];

const MobileAdmin: React.FC = () => {
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { isMobile } = useMobileDetection();
  const { user } = useAuth();

  // Check if user has admin permissions
  const isAdmin = user?.role === 'APP_SUPER_ADMIN' || user?.role === 'ORG_SUPER_ADMIN';

  const handleRefresh = async () => {
    setRefreshing(true);
    // TODO: Implement real refresh logic
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    // TODO: Implement real search logic
  };

  const handleModuleClick = (module: any) => {
    console.log('Navigate to admin module:', module.path);
    // TODO: Implement navigation to desktop admin routes
    // For now, show info that this goes to desktop
  };

  // Contextual actions for admin
  const contextualActions = [
    {
      icon: <Add />,
      name: 'Add User',
      onClick: () => console.log('Add user'),
      color: 'primary' as const
    },
    {
      icon: <Business />,
      name: 'Add Org',
      onClick: () => console.log('Add organization'),
      color: 'secondary' as const
    },
    {
      icon: <Backup />,
      name: 'Backup',
      onClick: () => console.log('System backup'),
      color: 'info' as const
    }
  ];

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<AdminPanelSettings />}
      size="small"
      onClick={() => setQuickActionsOpen(true)}
    >
      Actions
    </MobileButton>
  );

  if (!isAdmin) {
    return (
      <MobileDashboardLayout
        title="Access Denied"
        subtitle="Administrative access required"
        showBottomNav={true}
      >
        <Alert severity="error" sx={{ mt: 2 }}>
          You don't have permission to access administrative functions.
        </Alert>
      </MobileDashboardLayout>
    );
  }

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Administration"
        subtitle="System management"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading admin data..."
        />
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Administration"
      subtitle="System management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      <MobilePullToRefresh
        onRefresh={handleRefresh}
        isRefreshing={refreshing}
        enabled={true}
      >
        {/* Search */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <MobileSearchBar
              value={localSearchQuery}
              onChange={handleSearch}
              placeholder="Search admin functions..."
            />
          </Box>
        </Box>

        {/* System Health Overview */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <People sx={{ fontSize: '1.5rem', color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {mockAdminStats.total_users}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Users
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                  {mockAdminStats.active_users} active
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Business sx={{ fontSize: '1.5rem', color: 'secondary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'secondary.main' }}>
                  {mockAdminStats.total_organizations}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Organizations
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                  {mockAdminStats.active_organizations} active
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Shield sx={{ fontSize: '1.5rem', color: 'success.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {mockAdminStats.system_health}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  System Health
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'warning.main' }}>
                  {mockAdminStats.recent_alerts} alerts
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        </Grid>

        {/* Pending Actions Alert */}
        {mockAdminStats.pending_approvals > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            You have {mockAdminStats.pending_approvals} pending approvals requiring attention.
          </Alert>
        )}

        {/* Admin Modules */}
        <MobileCard title="Administrative Modules">
          <Grid container spacing={2}>
            {adminModules.map((module) => (
              <Grid item xs={6} key={module.id}>
                <Box
                  onClick={() => handleModuleClick(module)}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: `${module.color}.main`,
                      backgroundColor: 'action.hover',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ color: `${module.color}.main`, mr: 1 }}>
                      {module.icon}
                    </Box>
                    <Chip
                      label={module.badge}
                      size="small"
                      color={module.color as any}
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  </Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    {module.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {module.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Note:</strong> Admin modules will open in desktop view for full functionality.
            </Typography>
          </Alert>
        </MobileCard>

        {/* Recent Admin Activity */}
        <MobileCard title="Recent Activity">
          <List sx={{ p: 0 }}>
            {mockRecentActivity.map((activity, index) => (
              <ListItem
                key={activity.id}
                sx={{
                  px: 0,
                  py: 1.5,
                  borderBottom: index < mockRecentActivity.length - 1 ? '1px solid' : 'none',
                  borderColor: 'divider'
                }}
              >
                <ListItemIcon>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor:
                        activity.severity === 'success' ? 'success.main' :
                        activity.severity === 'warning' ? 'warning.main' :
                        activity.severity === 'error' ? 'error.main' : 'info.main'
                    }}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={activity.description}
                  secondary={new Date(activity.timestamp).toLocaleString()}
                  primaryTypographyProps={{
                    variant: 'body2',
                    fontWeight: 500
                  }}
                  secondaryTypographyProps={{
                    variant: 'caption',
                    color: 'text.secondary'
                  }}
                />
              </ListItem>
            ))}
          </List>
        </MobileCard>

        {/* TODO: Future implementations */}
        {/* TODO: Integrate with admin APIs */}
        {/* TODO: Add real-time system monitoring */}
        {/* TODO: Implement mobile user management interface */}
        {/* TODO: Add organization management tools */}
        {/* TODO: Implement security monitoring dashboard */}
        {/* TODO: Add system backup and restore interface */}
        {/* TODO: Implement audit log viewer */}
        {/* TODO: Add license management tools */}
        {/* TODO: Implement notification management */}
        {/* TODO: Add system configuration interface */}
      </MobilePullToRefresh>
      
      {/* Quick Actions Bottom Sheet */}
      <MobileBottomSheet
        open={quickActionsOpen}
        onClose={() => setQuickActionsOpen(false)}
        title="Admin Actions"
        height="auto"
        showHandle={true}
        dismissible={true}
      >
        <List sx={{ py: 0 }}>
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Add new user');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <ManageAccounts color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Add User"
              secondary="Create new user account"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Add organization');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Business color="secondary" />
            </ListItemIcon>
            <ListItemText
              primary="Add Organization"
              secondary="Create new organization"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('System backup');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Backup color="info" />
            </ListItemIcon>
            <ListItemText
              primary="System Backup"
              secondary="Create system backup"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('View system logs');
            }}
            sx={{ 
              borderRadius: 2,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <BugReport color="warning" />
            </ListItemIcon>
            <ListItemText
              primary="System Logs"
              secondary="View system logs and errors"
            />
          </ListItem>
        </List>
      </MobileBottomSheet>

      {/* Contextual Actions */}
      <MobileContextualActions
        actions={contextualActions}
        primaryAction={{
          icon: <AdminPanelSettings />,
          name: 'Admin Actions',
          onClick: () => setQuickActionsOpen(true),
          color: 'primary'
        }}
      />
    </MobileDashboardLayout>
  );
};

export default MobileAdmin;