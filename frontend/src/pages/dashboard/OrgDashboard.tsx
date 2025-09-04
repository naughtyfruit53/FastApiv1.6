// frontend/src/pages/dashboard/OrgDashboard.tsx
import React, { useState, useEffect } from "react";
import { Box, Typography, Chip, Alert, Paper, List, ListItem, ListItemText, ListItemAvatar, Avatar } from "@mui/material";
import {
  Business,
  People,
  Inventory,
  AttachMoney,
  TrendingUp,
} from "@mui/icons-material";
import adminService from "../../services/adminService";
import activityService, { RecentActivity } from "../../services/activityService";
import MetricCard from "../../components/MetricCard";
import DashboardLayout from "../../components/DashboardLayout";
import ModernLoading from "../../components/ModernLoading";
import { useAuth } from "../../context/AuthContext";
import { isAppSuperAdmin, isOrgSuperAdmin } from "../../types/user.types";
interface OrgStatistics {
  total_products: number;
  total_customers: number;
  total_vendors: number;
  active_users: number;
  monthly_sales: number;
  inventory_value: number;
  plan_type: string;
  storage_used_gb: number;
  generated_at: string;
  plan_expiry?: string;
  plan_status?: string;
  subscription_start?: string;
  subscription_validity_days?: number;
  total_org_users?: number; // For super admin view
  inactive_users?: number; // For super admin view
}
const OrgDashboard: React.FC = () => {
  const { user } = useAuth();
  const [statistics, setStatistics] = useState<OrgStatistics | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const isSuperAdmin = isAppSuperAdmin(user) || isOrgSuperAdmin(user);
  useEffect(() => {
    fetchOrgStatistics();
    fetchRecentActivities();
  }, []);
  const fetchOrgStatistics = async () => {
    try {
      const data = await adminService.getOrgStatistics();
      setStatistics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };
  const fetchRecentActivities = async () => {
    try {
      const response = await activityService.getRecentActivities(5);
      setRecentActivities(response.activities);
    } catch (err) {
      console.error("Failed to fetch recent activities:", err);
      // Keep empty array if fetch fails
    }
  };
  if (loading) {
    return (
      <DashboardLayout title="Organization Dashboard">
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading dashboard metrics..."
        />
      </DashboardLayout>
    );
  }
  if (error) {
    return (
      <DashboardLayout title="Organization Dashboard">
        <Alert
          severity="error"
          sx={{
            borderRadius: "var(--radius-lg)",
            "& .MuiAlert-message": {
              fontSize: "var(--font-size-sm)",
            },
          }}
        >
          Error loading dashboard: {error}
        </Alert>
      </DashboardLayout>
    );
  }
  if (!statistics) {
    return (
      <DashboardLayout title="Organization Dashboard">
        <Alert
          severity="info"
          sx={{
            borderRadius: "var(--radius-lg)",
            "& .MuiAlert-message": {
              fontSize: "var(--font-size-sm)",
            },
          }}
        >
          No statistics available
        </Alert>
      </DashboardLayout>
    );
  }
  const statsCards = [
    {
      title: "Total Products",
      value: statistics.total_products ?? 0,
      icon: <Inventory />,
      color: "primary" as const,
      description: "Products in inventory",
      href: "/masters/products",
      trend: {
        value: 12,
        period: "vs last month",
        direction: "up" as const,
      },
    },
    {
      title: "Total Customers",
      value: statistics.total_customers ?? 0,
      icon: <People />,
      color: "success" as const,
      description: "Active customers",
      href: "/masters/customers",
      trend: {
        value: 8,
        period: "vs last month",
        direction: "up" as const,
      },
    },
    {
      title: "Total Vendors",
      value: statistics.total_vendors ?? 0,
      icon: <Business />,
      color: "info" as const,
      description: "Registered vendors",
      href: "/masters/vendors",
      trend: {
        value: 3,
        period: "vs last month",
        direction: "up" as const,
      },
    },
    {
      title: "Active Users",
      value: statistics.active_users ?? 0,
      icon: <People />,
      color: "warning" as const,
      description: "Users in organization",
      href: "/settings/user-management",
      trend: {
        value: 5,
        period: "vs last month",
        direction: "up" as const,
      },
    },
    {
      title: "Monthly Sales",
      value: `₹${(statistics.monthly_sales ?? 0).toLocaleString()}`,
      icon: <AttachMoney />,
      color: "success" as const,
      description: "Sales in last 30 days",
      href: "/sales/dashboard",
      trend: {
        value: 15,
        period: "vs last month",
        direction: "up" as const,
      },
    },
    {
      title: "Inventory Value",
      value: `₹${(statistics.inventory_value ?? 0).toLocaleString()}`,
      icon: <TrendingUp />,
      color: "primary" as const,
      description: "Current stock value",
      href: "/inventory",
      trend: {
        value: 7,
        period: "vs last month",
        direction: "up" as const,
      },
    },
  ];
  return (
    <DashboardLayout title="Organization Dashboard">
      <Box className="modern-grid cols-3" sx={{ mb: 4 }}>
        {statsCards.map((stat, index) => (
          <MetricCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            color={stat.color}
            description={stat.description}
            trend={stat.trend}
            href={stat.href}
          />
        ))}
      </Box>
      <Box className="modern-grid cols-2" sx={{ mb: 4 }}>
        <Paper className="modern-card" sx={{ p: 3 }}>
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            Subscription Plan
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
            <Chip
              label={statistics.plan_type?.toUpperCase() ?? "N/A"}
              color={statistics.plan_type === "trial" ? "warning" : "primary"}
              variant="filled"
              sx={{
                fontWeight: 600,
                "&.MuiChip-colorPrimary": {
                  backgroundColor: "var(--primary-600)",
                  color: "white",
                },
                "&.MuiChip-colorWarning": {
                  backgroundColor: "var(--warning-500)",
                  color: "white",
                },
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
        </Paper>
        <Paper className="modern-card" sx={{ p: 3 }}>
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            Recent Activity
          </Typography>
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
        </Paper>
      </Box>
      <Paper className="modern-card" sx={{ p: 4 }}>
        <Typography
          variant="h6"
          className="modern-card-title"
          gutterBottom
          sx={{ mb: 3 }}
        >
          Organization Overview
        </Typography>
        <Box className="modern-grid cols-3">
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h3"
              sx={{
                color: "var(--primary-600)",
                fontWeight: 700,
                mb: 1,
              }}
            >
              {statistics.total_products ?? 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Products
            </Typography>
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h3"
              sx={{
                color: "var(--secondary-600)",
                fontWeight: 700,
                mb: 1,
              }}
            >
              {statistics.active_users ?? 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Active Users
            </Typography>
            {isSuperAdmin && statistics.total_org_users && (
              <Typography variant="caption" color="textSecondary" sx={{ display: "block", mt: 0.5 }}>
                of {statistics.total_org_users} total users
              </Typography>
            )}
          </Box>
          <Box sx={{ textAlign: "center" }}>
            <Typography
              variant="h3"
              sx={{
                color: "var(--success-600)",
                fontWeight: 700,
                mb: 1,
              }}
            >
              {statistics.monthly_sales !== undefined &&
              statistics.monthly_sales !== null
                ? Math.round((statistics.monthly_sales / 100000) * 100)
                : 0}
              %
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Monthly Growth
            </Typography>
          </Box>
        </Box>
        {isSuperAdmin && (
          <Box sx={{ mt: 3, pt: 3, borderTop: "1px solid", borderColor: "divider" }}>
            <Typography variant="h6" gutterBottom sx={{ color: "primary.main" }}>
              Super Admin View
            </Typography>
            <Box className="modern-grid cols-2">
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
            </Box>
          </Box>
        )}
      </Paper>
    </DashboardLayout>
  );
};
export default OrgDashboard;