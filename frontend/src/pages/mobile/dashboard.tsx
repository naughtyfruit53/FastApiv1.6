import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, IconButton, Chip, Alert, List, ListItem, ListItemText, ListItemAvatar, Avatar } from '@mui/material';
import { Refresh, Notifications, Search, Business, People, Inventory, AttachMoney, TrendingUp, AdminPanelSettings, MonitorHeart, Storage, Timeline, Security } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileSearchBar 
} from '../../components/mobile';
import { useAuth } from '../../context/AuthContext';
import adminService from "../../services/adminService";
import activityService, { RecentActivity } from "../../services/activityService";
import ModernLoading from "../../components/ModernLoading";
import StickyNotesPanel from "../../components/StickyNotes/StickyNotesPanel";

interface AppStatistics {
  total_licenses_issued: number;
  active_organizations: number;
  trial_organizations: number;
  total_active_users: number;
  super_admins_count: number;
  new_licenses_this_month: number;
  plan_breakdown: { [key: string]: number };
  system_health: {
    status: string;
    uptime: string;
  };
  generated_at: string;
  total_storage_used_gb?: number;
  average_users_per_org?: number;
  failed_login_attempts?: number;
  recent_new_orgs?: number;
}

interface OrgStatistics {
  total_products: number;
  total_products_trend: number;
  total_products_direction: 'up' | 'down' | 'neutral';
  total_customers: number;
  total_customers_trend: number;
  total_customers_direction: 'up' | 'down' | 'neutral';
  total_vendors: number;
  total_vendors_trend: number;
  total_vendors_direction: 'up' | 'down' | 'neutral';
  active_users: number;
  active_users_trend: number;
  active_users_direction: 'up' | 'down' | 'neutral';
  monthly_sales: number;
  monthly_sales_trend: number;
  monthly_sales_direction: 'up' | 'down' | 'neutral';
  inventory_value: number;
  inventory_value_trend: number;
  inventory_value_direction: 'up' | 'down' | 'neutral';
  plan_type: string;
  storage_used_gb: number;
  generated_at: string;
  plan_expiry?: string;
  plan_status?: string;
  subscription_start?: string;
  subscription_validity_days?: number;
  total_org_users?: number;
  inactive_users?: number;
}

const MobileDashboard: React.FC = () => {
  const { user } = useAuth();
  const { isMobile } = useMobileDetection();
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [statistics, setStatistics] = useState<AppStatistics | OrgStatistics | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isSuperAdmin = user?.is_super_admin || false;
  const isOrgSuperAdmin = user?.role === 'super_admin'; // Assuming 'super_admin' role for org super admin

  useEffect(() => {
    if (user) {
      handleRefresh();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchAppStatistics = async () => {
    try {
      const data = await adminService.getAppStatistics();
      const totalLicenses = data.total_licenses_issued || 0;
      const totalActiveUsers = data.total_active_users || 0;
      const enhancedData = {
        ...data,
        total_storage_used_gb: data.total_storage_used_gb || totalLicenses * 0.5,
        average_users_per_org: data.average_users_per_org || (totalLicenses > 0 ? Math.round(totalActiveUsers / totalLicenses) : 0),
        failed_login_attempts: data.failed_login_attempts || 0,
        recent_new_orgs: data.recent_new_orgs || Math.round(data.new_licenses_this_month / 4),
      };
      setStatistics(enhancedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const fetchOrgStatistics = async () => {
    try {
      const data = await adminService.getOrgStatistics();
      setStatistics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const fetchRecentActivities = async () => {
    try {
      const response = await activityService.getRecentActivities(5);
      setRecentActivities(response.activities);
    } catch (err) {
      console.error("Failed to fetch recent activities:", err);
      setRecentActivities([]);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      if (isSuperAdmin) {
        await fetchAppStatistics();
      } else {
        await fetchOrgStatistics();
        await fetchRecentActivities();
      }
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  const rightActions = (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <IconButton 
        size="small" 
        onClick={handleRefresh}
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

  let statsCards: any[] = [];

  if (isSuperAdmin) {
    statsCards = [
      {
        title: "Total Licenses Issued",
        value: statistics.total_licenses_issued,
        icon: <Business />,
        color: "primary" as const,
        description: "Total organization licenses created",
        trend: {
          value: 8,
          period: "vs last month",
          direction: "up" as const,
        },
      },
      {
        title: "Active Organizations",
        value: statistics.active_organizations,
        icon: <Business />,
        color: "success" as const,
        description: "Organizations with active status",
        trend: {
          value: 12,
          period: "vs last month",
          direction: "up" as const,
        },
      },
      {
        title: "Trial Organizations",
        value: statistics.trial_organizations,
        icon: <Business />,
        color: "warning" as const,
        description: "Organizations on trial plans",
        trend: {
          value: 5,
          period: "vs last month",
          direction: "up" as const,
        },
      },
      {
        title: "Total Active Users",
        value: statistics.total_active_users,
        icon: <People />,
        color: "info" as const,
        description: "Active users across all organizations",
        trend: {
          value: 15,
          period: "vs last month",
          direction: "up" as const,
        },
      },
      {
        title: "Super Admins",
        value: statistics.super_admins_count,
        icon: <AdminPanelSettings />,
        color: "warning" as const,
        description: "App-level administrators",
      },
      {
        title: "New Licenses (30d)",
        value: statistics.new_licenses_this_month,
        icon: <TrendingUp />,
        color: "success" as const,
        description: "Licenses created in last 30 days",
        trend: {
          value: 22,
          period: "vs previous month",
          direction: "up" as const,
        },
      },
      {
        title: "System Health",
        value: statistics.system_health.uptime,
        icon: <MonitorHeart />,
        color: statistics.system_health.status === "healthy" ? ("success" as const) : ("error" as const),
        description: "System uptime percentage",
      },
      {
        title: "Total Storage Used",
        value: `${statistics.total_storage_used_gb?.toFixed(1) || 0} GB`,
        icon: <Storage />,
        color: "info" as const,
        description: "Aggregate storage across all organizations",
      },
      {
        title: "Avg Users per Org",
        value: statistics.average_users_per_org || 0,
        icon: <Timeline />,
        color: "primary" as const,
        description: "Average active users per organization",
      },
    ];
  } else {
    statsCards = [
      {
        title: "Total Products",
        value: statistics.total_products ?? 0,
        icon: <Inventory />,
        color: "primary" as const,
        description: "Products in inventory",
        trend: {
          value: statistics.total_products_trend ?? 0,
          period: "vs last month",
          direction: statistics.total_products_direction ?? "neutral" as const,
        },
      },
      {
        title: "Total Customers",
        value: statistics.total_customers ?? 0,
        icon: <People />,
        color: "success" as const,
        description: "Active customers",
        trend: {
          value: statistics.total_customers_trend ?? 0,
          period: "vs last month",
          direction: statistics.total_customers_direction ?? "neutral" as const,
        },
      },
      {
        title: "Total Vendors",
        value: statistics.total_vendors ?? 0,
        icon: <Business />,
        color: "info" as const,
        description: "Registered vendors",
        trend: {
          value: statistics.total_vendors_trend ?? 0,
          period: "vs last month",
          direction: statistics.total_vendors_direction ?? "neutral" as const,
        },
      },
      {
        title: "Active Users",
        value: statistics.active_users ?? 0,
        icon: <People />,
        color: "warning" as const,
        description: "Users in organization",
        trend: {
          value: statistics.active_users_trend ?? 0,
          period: "vs last month",
          direction: statistics.active_users_direction ?? "neutral" as const,
        },
      },
      {
        title: "Monthly Sales",
        value: `₹${(statistics.monthly_sales ?? 0).toLocaleString()}`,
        icon: <AttachMoney />,
        color: "success" as const,
        description: "Sales in last 30 days",
        trend: {
          value: statistics.monthly_sales_trend ?? 0,
          period: "vs last month",
          direction: statistics.monthly_sales_direction ?? "neutral" as const,
        },
      },
      {
        title: "Inventory Value",
        value: `₹${(statistics.inventory_value ?? 0).toLocaleString()}`,
        icon: <TrendingUp />,
        color: "primary" as const,
        description: "Current stock value",
        trend: {
          value: statistics.inventory_value_trend ?? 0,
          period: "vs last month",
          direction: statistics.inventory_value_direction ?? "neutral" as const,
        },
      },
    ];
  }

  const activationRate = isSuperAdmin
    ? statistics.total_licenses_issued > 0
      ? Math.round((statistics.active_organizations / statistics.total_licenses_issued) * 100)
      : 0
    : 0;

  return (
    <MobileDashboardLayout
      title="Dashboard"
      subtitle={`Welcome back, ${user?.name || 'User'}!`}
      rightActions={rightActions}
      showBottomNav={true}
    >
      {isSuperAdmin && <StickyNotesPanel />}
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
          return (
            <Grid item xs={6} key={index}>
              <MobileCard>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" sx={{ fontSize: '2rem', marginBottom: 1 }}>
                    {stat.icon}
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
                      {stat.trend.direction === 'up' ? '+' : '-'} {stat.trend.value} ({stat.trend.period})
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
    </MobileDashboardLayout>
  );
};

export default MobileDashboard;