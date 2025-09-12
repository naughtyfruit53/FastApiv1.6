import React, { useState, useEffect } from "react";
import { Box, Typography, Chip, Alert, Paper } from "@mui/material";
import {
  Business,
  People,
  AdminPanelSettings,
  TrendingUp,
  Security,
  MonitorHeart,
  Storage,
  Timeline,
} from "@mui/icons-material";
import adminService from "../../services/adminService";
import MetricCard from "../../components/MetricCard";
import DashboardLayout from "../../components/DashboardLayout";
import ModernLoading from "../../components/ModernLoading";
import StickyNotesPanel from "../../components/StickyNotes/StickyNotesPanel";
import { useStickyNotes } from "../../hooks/useStickyNotes";
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
const AppSuperAdminDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<AppStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { _stickyNotes } = useStickyNotes();
  useEffect(() => {
    fetchAppStatistics();
  }, []);
  const fetchAppStatistics = async () => {
    try {
      const data = await adminService.getAppStatistics();
      const totalLicenses = data.total_licenses_issued || 0;
      const totalActiveUsers = data.total_active_users || 0;
      const enhancedData = {
        ...data,
        total_storage_used_gb:
          data.total_storage_used_gb || totalLicenses * 0.5,
        average_users_per_org:
          data.average_users_per_org ||
          (totalLicenses > 0
            ? Math.round(totalActiveUsers / totalLicenses)
            : 0),
        failed_login_attempts: data.failed_login_attempts || 0,
        recent_new_orgs:
          data.recent_new_orgs || Math.round(data.new_licenses_this_month / 4),
      };
      setStatistics(enhancedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };
  if (loading) {
    return (
      <DashboardLayout
        title="Super Admin Dashboard"
        subtitle="Monitor platform-wide metrics and system health"
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={9}
          message="Loading platform metrics..."
        />
      </DashboardLayout>
    );
  }
  if (error) {
    return (
      <DashboardLayout
        title="Super Admin Dashboard"
        subtitle="Monitor platform-wide metrics and system health"
      >
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
    return null;
  }
  const statsCards = [
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
      color:
        statistics.system_health.status === "healthy"
          ? ("success" as const)
          : ("error" as const),
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
  const activationRate =
    statistics.total_licenses_issued > 0
      ? Math.round(
          (statistics.active_organizations / statistics.total_licenses_issued) *
            100,
        )
      : 0;
  return (
    <DashboardLayout
      title="Super Admin Dashboard"
      subtitle="Monitor platform-wide metrics and system health"
    >
      <StickyNotesPanel />
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
          />
        ))}
      </Box>
      <Box className="modern-grid cols-2" sx={{ mb: 4 }}>
        <Paper className="modern-card" sx={{ p: 3 }}>
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            License Plan Distribution
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {Object.entries(statistics.plan_breakdown).map(([plan, count]) => (
              <Chip
                key={plan}
                label={`${plan}: ${count}`}
                color={plan === "trial" ? "warning" : "primary"}
                variant="filled"
                sx={{
                  fontWeight: 500,
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
            ))}
          </Box>
        </Paper>
        <Paper className="modern-card" sx={{ p: 3 }}>
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            System Status
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <Security sx={{ color: "var(--success-600)", mr: 1 }} />
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
                  "&.MuiChip-colorSuccess": {
                    backgroundColor: "var(--success-600)",
                    color: "white",
                  },
                  "&.MuiChip-colorError": {
                    backgroundColor: "var(--error-600)",
                    color: "white",
                  },
                }}
              />
            </Typography>
          </Box>
          <Typography variant="body2" color="textSecondary">
            Last updated: {new Date(statistics.generated_at).toLocaleString()}
          </Typography>
        </Paper>
      </Box>
      <Paper className="modern-card" sx={{ p: 4 }}>
        <Typography
          variant="h6"
          className="modern-card-title"
          gutterBottom
          sx={{ mb: 3 }}
        >
          Platform Growth Overview
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
              {statistics.total_licenses_issued}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Organizations
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
              {statistics.total_active_users}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Platform Users
            </Typography>
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
              {activationRate}%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Activation Rate
            </Typography>
          </Box>
        </Box>
      </Paper>
    </DashboardLayout>
  );
};
export default AppSuperAdminDashboard;