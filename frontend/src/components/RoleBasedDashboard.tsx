// frontend/src/components/RoleBasedDashboard.tsx
/**
 * Role-Based Dashboard Component
 * Provides different KPIs and tiles based on user role:
 * - Management: High-level business metrics, P&L, strategic KPIs
 * - Manager: Team performance, department metrics, operational KPIs
 * - Executive: Personal tasks, daily activities, transaction counts
 * - Admin: System health, user management, configuration stats
 */

import React from "react";
import {
  Box,
  Grid,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Divider,
} from "@mui/material";
import {
  TrendingUp,
  People,
  Assessment,
  AttachMoney,
  Inventory,
  Assignment,
  Speed,
  Schedule,
  Settings,
  Security,
} from "@mui/icons-material";
import MetricCard from "./MetricCard";
import { useAuth } from "../context/AuthContext";
import { useCurrency } from "../hooks/useCurrency";
import activityService, { RecentActivity } from "../services/activityService";
import { ROLE_HIERARCHY, DashboardRole as RoleType } from "../constants/ui";

export type DashboardRole = RoleType;

interface RoleBasedDashboardProps {
  /** Override the auto-detected role */
  role?: DashboardRole;
  /** Statistics data from API */
  statistics: any;
  /** Recent activities */
  recentActivities: RecentActivity[];
}

// Role-specific KPI configurations
const ROLE_KPIS: Record<DashboardRole, { title: string; metrics: string[] }> = {
  management: {
    title: "Executive Summary",
    metrics: ["revenue", "profit_margin", "yoy_growth", "market_share", "customer_retention", "employee_satisfaction"],
  },
  manager: {
    title: "Department Overview",
    metrics: ["team_productivity", "department_revenue", "pending_approvals", "team_attendance", "targets_achieved", "open_issues"],
  },
  executive: {
    title: "My Dashboard",
    metrics: ["my_tasks", "pending_items", "today_activities", "completed_tasks", "upcoming_deadlines", "performance_score"],
  },
  admin: {
    title: "System Administration",
    metrics: ["active_users", "system_health", "storage_usage", "pending_configs", "security_alerts", "api_usage"],
  },
  viewer: {
    title: "Reports Dashboard",
    metrics: ["available_reports", "recent_views", "bookmarked_items", "shared_with_me"],
  },
};

/**
 * Determine dashboard role from user context using centralized role hierarchy
 */
const getDashboardRole = (user: any): DashboardRole => {
  if (!user) return "viewer";
  
  const role = user.role?.toLowerCase() || "";
  
  // Check against centralized role hierarchy
  for (const [dashboardRole, roles] of Object.entries(ROLE_HIERARCHY)) {
    if ((roles as readonly string[]).includes(role)) {
      return dashboardRole as DashboardRole;
    }
  }
  
  return "viewer";
};

const RoleBasedDashboard: React.FC<RoleBasedDashboardProps> = ({
  role: overrideRole,
  statistics,
  recentActivities,
}) => {
  const { user } = useAuth();
  const { formatCurrency } = useCurrency();
  
  const dashboardRole = overrideRole || getDashboardRole(user);
  const roleConfig = ROLE_KPIS[dashboardRole];

  // Generate metrics based on role
  const getMetricsForRole = () => {
    if (!statistics) return [];

    switch (dashboardRole) {
      case "management":
        return [
          {
            title: "Monthly Revenue",
            value: formatCurrency(statistics.monthly_sales ?? 0),
            icon: <AttachMoney />,
            color: "success" as const,
            description: "Total revenue this month",
            trend: { value: statistics.monthly_sales_trend ?? 0, period: "vs last month", direction: statistics.monthly_sales_direction ?? "neutral" as const },
          },
          {
            title: "Gross Margin",
            value: `${(statistics.gross_margin ?? 25).toFixed(1)}%`,
            icon: <TrendingUp />,
            color: "primary" as const,
            description: "Profit margin percentage",
          },
          {
            title: "Total Customers",
            value: statistics.total_customers ?? 0,
            icon: <People />,
            color: "info" as const,
            description: "Active customer base",
            trend: { value: statistics.total_customers_trend ?? 0, period: "vs last month", direction: statistics.total_customers_direction ?? "neutral" as const },
          },
          {
            title: "Inventory Value",
            value: formatCurrency(statistics.inventory_value ?? 0),
            icon: <Inventory />,
            color: "warning" as const,
            description: "Current stock value",
          },
        ];

      case "manager":
        return [
          {
            title: "Team Performance",
            value: `${statistics.team_performance ?? 85}%`,
            icon: <Speed />,
            color: "success" as const,
            description: "Average team productivity",
          },
          {
            title: "Department Revenue",
            value: formatCurrency(statistics.department_revenue ?? statistics.monthly_sales ?? 0),
            icon: <AttachMoney />,
            color: "primary" as const,
            description: "Department contribution",
          },
          {
            title: "Pending Approvals",
            value: statistics.pending_approvals ?? 5,
            icon: <Assignment />,
            color: "warning" as const,
            description: "Items awaiting your approval",
          },
          {
            title: "Active Team Members",
            value: statistics.active_users ?? 0,
            icon: <People />,
            color: "info" as const,
            description: "Team members online today",
          },
        ];

      case "executive":
        return [
          {
            title: "My Tasks",
            value: statistics.my_tasks ?? 12,
            icon: <Assignment />,
            color: "primary" as const,
            description: "Pending tasks assigned to you",
          },
          {
            title: "Completed Today",
            value: statistics.completed_today ?? 5,
            icon: <Assessment />,
            color: "success" as const,
            description: "Tasks completed today",
          },
          {
            title: "Upcoming Deadlines",
            value: statistics.upcoming_deadlines ?? 3,
            icon: <Schedule />,
            color: "warning" as const,
            description: "Deadlines this week",
          },
          {
            title: "Performance Score",
            value: `${statistics.performance_score ?? 92}%`,
            icon: <TrendingUp />,
            color: "info" as const,
            description: "Your performance rating",
          },
        ];

      case "admin":
        return [
          {
            title: "Active Users",
            value: statistics.active_users ?? 0,
            icon: <People />,
            color: "primary" as const,
            description: "Users online now",
          },
          {
            title: "System Health",
            value: statistics.system_health?.status ?? "Healthy",
            icon: <Security />,
            color: "success" as const,
            description: "Overall system status",
          },
          {
            title: "Storage Used",
            value: `${statistics.storage_used_gb ?? 0} GB`,
            icon: <Settings />,
            color: "info" as const,
            description: "Storage consumption",
          },
          {
            title: "Total Products",
            value: statistics.total_products ?? 0,
            icon: <Inventory />,
            color: "warning" as const,
            description: "Products in system",
          },
        ];

      default:
        return [
          {
            title: "Available Reports",
            value: statistics.available_reports ?? 15,
            icon: <Assessment />,
            color: "primary" as const,
            description: "Reports you can access",
          },
          {
            title: "Recent Views",
            value: statistics.recent_views ?? 8,
            icon: <Assignment />,
            color: "info" as const,
            description: "Recently viewed items",
          },
        ];
    }
  };

  const metrics = getMetricsForRole();

  return (
    <Box>
      {/* Role indicator */}
      <Box sx={{ mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
        <Typography variant="h5" fontWeight={600}>
          {roleConfig.title}
        </Typography>
        <Chip
          label={dashboardRole.charAt(0).toUpperCase() + dashboardRole.slice(1)}
          color="primary"
          size="small"
          variant="outlined"
        />
      </Box>

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <MetricCard
              title={metric.title}
              value={metric.value}
              icon={metric.icon}
              color={metric.color}
              description={metric.description}
              trend={metric.trend}
            />
          </Grid>
        ))}
      </Grid>

      {/* Recent Activity Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {recentActivities.length > 0 ? (
          <List>
            {recentActivities.slice(0, 5).map((activity) => (
              <ListItem key={activity.id} sx={{ px: 0 }}>
                <ListItemAvatar>
                  <Avatar sx={{ width: 36, height: 36, bgcolor: "primary.light" }}>
                    {activityService.getActivityIcon(activity.type)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={activity.title}
                  secondary={
                    <>
                      <Typography component="span" variant="body2" color="text.primary">
                        {activity.description}
                      </Typography>
                      <br />
                      <Typography component="span" variant="caption" color="text.secondary">
                        {activityService.formatActivityTime(activity.timestamp)}
                        {activity.user_name && ` • ${activity.user_name}`}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
            No recent activity to display
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default RoleBasedDashboard;
export { getDashboardRole };
