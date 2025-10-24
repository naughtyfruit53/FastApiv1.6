import React, { useState } from 'react';
import { Box, Grid, Typography, IconButton, Chip, Alert, List, ListItem, ListItemText, ListItemAvatar, Avatar } from '@mui/material';
import { Refresh, Notifications, Business, People, Inventory, TrendingUp, MonitorHeart, Storage, Timeline, Security } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileSearchBar,
  MobilePullToRefresh 
} from '../../components/mobile';
import { useAuth } from '../../context/AuthContext';
import useSharedDashboard from '../../hooks/useSharedDashboard';
import activityService from "../../services/activityService";
import ModernLoading from "../../components/ModernLoading";



const MobileDashboard: React.FC = () => {
  const { user } = useAuth();
  const { isMobile } = useMobileDetection();
  const [searchQuery, setSearchQuery] = useState('');

  // Use shared dashboard business logic
  const {
    statistics,
    recentActivities,
    loading,
    error,
    refreshing,
    isSuperAdmin,
    refresh,
    getActivationRate,
    getStatsCards,
  } = useSharedDashboard();

  const isOrgSuperAdmin = user?.role === 'super_admin'; // Assuming 'super_admin' role for org super admin
  const activationRate = getActivationRate();
  const statsCards = getStatsCards();

  const rightActions = (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <IconButton 
        size="small" 
        onClick={refresh}
        disabled={refreshing || loading}
        sx={{ minWidth: 44, minHeight: 44 }}
      >
        <Refresh sx={{ 
          animation: refreshing ? 'spin 1s linear infinite' : 'none',
          '@keyframes spin': {
            '0%': { transform: 'rotate(0deg)' },
            '100%': { transform: 'rotate(360deg)' },
          }
        }} />
      </IconButton>
      <IconButton 
        size="small"
        sx={{ minWidth: 44, minHeight: 44 }}
      >
        <Notifications />
      </IconButton>
    </Box>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Dashboard"
        subtitle={`Welcome back, ${user?.name || 'User'}!`}
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={9}
          message="Loading platform metrics..."
        />
      </MobileDashboardLayout>
    );
  }

  if (error) {
    return (
      <MobileDashboardLayout
        title="Dashboard"
        subtitle={`Welcome back, ${user?.name || 'User'}!`}
        rightActions={rightActions}
        showBottomNav={true}
      >
        <Alert severity="error">
          Error loading dashboard: {error}
        </Alert>
      </MobileDashboardLayout>
    );
  }

  if (!statistics) {
    return (
      <MobileDashboardLayout
        title="Dashboard"
        subtitle={`Welcome back, ${user?.name || 'User'}!`}
        rightActions={rightActions}
        showBottomNav={true}
      >
        <Alert severity="info">
          No statistics available
        </Alert>
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Dashboard"
      subtitle={`Welcome back, ${user?.name || 'User'}!`}
      rightActions={rightActions}
      showBottomNav={true}
    >
      <MobilePullToRefresh
        onRefresh={refresh}
        isRefreshing={refreshing}
        enabled={true}
      >
        <MobileSearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search transactions, orders..."
        />
        <Grid container spacing={isMobile ? 2 : 3}>
          {statsCards.map((stat, index) => {
            let changeType: 'positive' | 'negative' | 'warning' | 'neutral' = 'neutral';
            if (stat.trend) {
              changeType = stat.trend.direction === 'up' ? 'positive' : stat.trend.direction === 'down' ? 'negative' : 'warning';
            }
            
            // Get appropriate icon based on stat title
            const getStatIcon = (title: string) => {
              switch (title.toLowerCase()) {
                case 'total licenses issued':
                case 'active organizations':
                case 'trial organizations':
                  return <Business />;
                case 'total active users':
                case 'super admins':
                case 'active users':
                case 'total customers':
                case 'avg users per org':
                  return <People />;
                case 'new licenses (30d)':
                case 'monthly sales':
                case 'inventory value':
                  return <TrendingUp />;
                case 'system health':
                  return <MonitorHeart />;
                case 'total storage used':
                  return <Storage />;
                case 'total products':
                  return <Inventory />;
                case 'total vendors':
                  return <Business />;
                default:
                  return <Timeline />;
              }
            };

            return (
              <Grid item xs={6} key={index}>
                <MobileCard>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h2" sx={{ fontSize: '2rem', marginBottom: 1 }}>
                      {getStatIcon(stat.title)}
                    </Typography>
                    <Typography variant="h4" sx={{ 
                      fontSize: isMobile ? '1.5rem' : '1.75rem',
                      fontWeight: 700,
                      marginBottom: 0.5,
                      color: 'text.primary',
                    }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: 'text.secondary',
                      marginBottom: 1,
                      fontSize: '0.875rem',
                    }}>
                      {stat.title}
                    </Typography>
                    {stat.trend && (
                      <Typography variant="caption" sx={{ 
                        color: changeType === 'positive' ? 'success.main' 
                              : changeType === 'negative' ? 'error.main'
                              : 'warning.main',
                        fontWeight: 600,
                      }}>
                        {stat.trend.direction === 'up' ? '+' : '-'} {stat.trend.value}% ({stat.trend.period})
                      </Typography>
                    )}
                  </Box>
                </MobileCard>
              </Grid>
            );
          })}
        </Grid>
        {isSuperAdmin ? (
          <>
            <MobileCard title="License Plan Distribution">
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(statistics.plan_breakdown).map(([plan, count]) => (
                  <Chip
                    key={plan}
                    label={`${plan}: ${count}`}
                    color={plan === "trial" ? "warning" : "primary"}
                    variant="filled"
                    sx={{
                      fontWeight: 500,
                    }}
                  />
                ))}
              </Box>
            </MobileCard>
            <MobileCard title="System Status">
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security sx={{ color: 'var(--success-600)', mr: 1 }} />
                <Typography>
                  Status:{" "}
                  <Chip
                    label={statistics.system_health.status}
                    color={
                      statistics.system_health.status === "healthy"
                        ? "success"
                        : "error"
                    }
                    size="small"
                    variant="filled"
                    sx={{
                      fontWeight: 500,
                    }}
                  />
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Last updated: {new Date(statistics.generated_at).toLocaleString()}
              </Typography>
            </MobileCard>
            <MobileCard title="Platform Growth Overview">
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--primary-600)', fontWeight: 700, mb: 1 }}>
                      {statistics.total_licenses_issued}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Organizations
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--secondary-600)', fontWeight: 700, mb: 1 }}>
                      {statistics.total_active_users}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Platform Users
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--success-600)', fontWeight: 700, mb: 1 }}>
                      {activationRate}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Activation Rate
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </MobileCard>
          </>
        ) : (
          <>
            <MobileCard title="Quick Actions">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <MobileButton variant="contained" fullWidth>
                    New Order
                  </MobileButton>
                </Grid>
                <Grid item xs={6}>
                  <MobileButton variant="outlined" fullWidth>
                    Add Customer
                  </MobileButton>
                </Grid>
                <Grid item xs={6}>
                  <MobileButton variant="outlined" fullWidth>
                    Check Inventory
                  </MobileButton>
                </Grid>
                <Grid item xs={6}>
                  <MobileButton variant="outlined" fullWidth>
                    View Reports
                  </MobileButton>
                </Grid>
              </Grid>
            </MobileCard>
            <MobileCard title="Subscription Plan">
              <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                <Chip
                  label={statistics.plan_type?.toUpperCase() ?? "N/A"}
                  color={statistics.plan_type === "trial" ? "warning" : "primary"}
                  variant="filled"
                  sx={{
                    fontWeight: 600,
                  }}
                />
                {statistics.plan_status && (
                  <Chip
                    label={statistics.plan_status.toUpperCase()}
                    color={statistics.plan_status === "active" ? "success" : "default"}
                    variant="outlined"
                    size="small"
                  />
                )}
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                Storage Used: {statistics.storage_used_gb ?? 0} GB
              </Typography>
              {statistics.plan_expiry && (
                <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                  Expires: {new Date(statistics.plan_expiry).toLocaleDateString()}
                </Typography>
              )}
              {statistics.subscription_validity_days !== undefined && (
                <Typography 
                  variant="body2" 
                  color={statistics.subscription_validity_days <= 30 ? "error" : "textSecondary"}
                  sx={{ fontWeight: statistics.subscription_validity_days <= 30 ? 600 : 400 }}
                >
                  {statistics.subscription_validity_days > 0 
                    ? `${statistics.subscription_validity_days} days remaining`
                    : "Subscription expired"}
                </Typography>
              )}
            </MobileCard>
            <MobileCard title="Recent Activity">
              {recentActivities.length > 0 ? (
                <List sx={{ pt: 0 }}>
                  {recentActivities.map((activity) => (
                    <ListItem key={activity.id} sx={{ px: 0, py: 1 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ width: 32, height: 32, fontSize: "1rem" }}>
                          {activityService.getActivityIcon(activity.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.title}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                              {activity.description}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {activityService.formatActivityTime(activity.timestamp)}
                              {activity.user_name && ` • by ${activity.user_name}`}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No recent activity available
                </Typography>
              )}
            </MobileCard>
            <MobileCard title="Organization Overview">
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--primary-600)', fontWeight: 700, mb: 1 }}>
                      {statistics.total_products ?? 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Products
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--secondary-600)', fontWeight: 700, mb: 1 }}>
                      {statistics.active_users ?? 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Active Users
                    </Typography>
                    {isOrgSuperAdmin && statistics.total_org_users && (
                      <Typography variant="caption" color="textSecondary" sx={{ display: "block", mt: 0.5 }}>
                        of {statistics.total_org_users} total users
                      </Typography>
                    )}
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h3" sx={{ color: 'var(--success-600)', fontWeight: 700, mb: 1 }}>
                      {statistics.monthly_sales_trend ?? 0}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Monthly Growth
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              {isOrgSuperAdmin && (
                <Box sx={{ mt: 3, pt: 3, borderTop: "1px solid", borderColor: "divider" }}>
                  <Typography variant="h6" gutterBottom sx={{ color: "primary.main" }}>
                    Super Admin View
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: "center" }}>
                        <Typography
                          variant="h4"
                          sx={{
                            color: "var(--warning-600)",
                            fontWeight: 600,
                            mb: 1,
                          }}
                        >
                          {statistics.inactive_users ?? 0}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Inactive Users
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: "center" }}>
                        <Typography
                          variant="h4"
                          sx={{
                            color: "var(--info-600)",
                            fontWeight: 600,
                            mb: 1,
                          }}
                        >
                          {((statistics.active_users / (statistics.total_org_users || 1)) * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          User Activity Rate
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </MobileCard>
          </>
        )}
      </MobilePullToRefresh>
    </MobileDashboardLayout>
  );
};

export default MobileDashboard;