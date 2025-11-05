// frontend/src/pages/dashboard/OrgDashboard.tsx
import React, { useState, useEffect } from "react";
import { Box, Typography, Chip, Alert, Paper, List, ListItem, ListItemText, ListItemAvatar, Avatar, Button } from "@mui/material";
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
import CompanyDetailsModal from "../../components/CompanyDetailsModal";
import { usePermissions } from "../../context/PermissionContext";  // Added import for permissions

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
  license_status: string | null; // Allow null for undefined cases
  license_issued_date: string | null;
  license_expiry_date: string | null;
  total_org_users?: number;
  inactive_users?: number;
}

const OrgDashboard: React.FC = () => {
  const { user } = useAuth();
  const { hasPermission } = usePermissions();  // Added hook for permission check
  const [statistics, setStatistics] = useState<OrgStatistics | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCompanyDetailsModal, setShowCompanyDetailsModal] = useState(false);
  const [companyDetailsSkipped, setCompanyDetailsSkipped] = useState(false);
  
  const isSuperAdmin = isAppSuperAdmin(user) || isOrgSuperAdmin(user);
  
  useEffect(() => {
    fetchOrgStatistics();
    fetchRecentActivities();
    
    // Check if company details need to be completed before allowing access
    const checkCompanyDetails = () => {
      if (isOrgSuperAdmin(user) && user?.company_details_completed === false) {
        const skippedFlag = localStorage.getItem('company_details_skipped');
        if (!skippedFlag) {
          setShowCompanyDetailsModal(true);
        } else {
          setCompanyDetailsSkipped(true);
        }
      }
    };
    
    checkCompanyDetails();
  }, [user]);

  const fetchOrgStatistics = async () => {
    try {
      setLoading(true);
      const data = await adminService.getOrgStatistics();
      console.log("Org statistics response:", data); // Debug API response
      let inventoryValue = 0;
      // Removed permission check to always fetch inventory value
      try {
        inventoryValue = await adminService.getInventoryValue();
      } catch (invError) {
        console.error("Inventory value fetch failed:", invError);
        // Set to 0 on error, continue loading
      }
      setStatistics({
        ...data,
        inventory_value: inventoryValue,
        license_status: data.license_status || (data.plan_type === "trial" ? "trial" : "active"),
        license_issued_date: data.license_issued_date,
        license_expiry_date: data.license_expiry_date,
      });
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

  const calculateValidityDays = (expiryDate: string | null): number | null => {
    if (!expiryDate) return null; // Perpetual licenses have no expiry
    const expiry = new Date(expiryDate);
    const now = new Date();
    const diffTime = expiry.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
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
      href: "/masters/customers",
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
      href: "/masters/vendors",
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
      href: "/settings/user-management",
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
      href: "/sales/dashboard",
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
      href: "/inventory",
      trend: {
        value: statistics.inventory_value_trend ?? 0,
        period: "vs last month",
        direction: statistics.inventory_value_direction ?? "neutral" as const,
      },
    },
  ];

  const validityDays = calculateValidityDays(statistics.license_expiry_date);

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
            <Chip
              label={statistics.license_status ? statistics.license_status.toUpperCase() : "UNKNOWN"}
              color={statistics.license_status === "active" ? "success" : "default"}
              variant="outlined"
              size="small"
            />
          </Box>
          {statistics.license_issued_date && (
            <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
              <strong>Started:</strong> {new Date(statistics.license_issued_date).toLocaleDateString()}
            </Typography>
          )}
          {statistics.license_expiry_date && (
            <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
              <strong>Valid Up To:</strong> {new Date(statistics.license_expiry_date).toLocaleDateString()}
            </Typography>
          )}
          <Typography 
            variant="body2" 
            color={validityDays && validityDays <= 30 ? "error" : "textSecondary"}
            sx={{ fontWeight: validityDays && validityDays <= 30 ? 600 : 400 }}
          >
            {validityDays === null 
              ? "Perpetual License"
              : validityDays > 0 
                ? `${validityDays} days remaining`
                : "Subscription expired"}
          </Typography>
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
                      <React.Fragment>
                        <Typography
                          component="span"
                          variant="body2"
                          sx={{ display: 'block', mb: 0.5 }}
                          color="text.primary"
                        >
                          {activity.description}
                        </Typography>
                        <Typography
                          component="span"
                          variant="caption"
                          sx={{ display: 'block' }}
                          color="text.secondary"
                        >
                          {activityService.formatActivityTime(activity.timestamp)}
                          {activity.user_name && ` • by ${activity.user_name}`}
                        </Typography>
                      </React.Fragment>
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
              {statistics.monthly_sales_trend ?? 0}%
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
      
      {/* Show alert if company details were skipped */}
      {companyDetailsSkipped && (
        <Alert
          severity="warning"
          sx={{ mt: 2 }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => {
                setShowCompanyDetailsModal(true);
                setCompanyDetailsSkipped(false);
              }}
            >
              Complete Now
            </Button>
          }
        >
          Company details are not complete. Click "Complete Now" to add your company information.
        </Alert>
      )}
      
      {/* Company Details Modal */}
      <CompanyDetailsModal
        open={showCompanyDetailsModal}
        onClose={() => {
          // If skipped, set flag in localStorage
          if (user?.company_details_completed === false) {
            localStorage.setItem('company_details_skipped', 'true');
            setCompanyDetailsSkipped(true);
          }
          setShowCompanyDetailsModal(false);
        }}
        onSuccess={() => {
          // Clear skipped flag on successful completion
          localStorage.removeItem('company_details_skipped');
          setShowCompanyDetailsModal(false);
          setCompanyDetailsSkipped(false);
          // Refresh user context to update company_details_completed flag
          window.location.reload();
        }}
        isRequired={user?.company_details_completed === false && isOrgSuperAdmin(user)}
        mode="create"
      />
    </DashboardLayout>
  );
};

export default OrgDashboard;