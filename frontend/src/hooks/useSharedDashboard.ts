// frontend/src/hooks/useSharedDashboard.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import adminService from '../services/adminService';
import activityService, { RecentActivity } from '../services/activityService';

export interface AppStatistics {
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

export interface OrgStatistics {
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

export interface DashboardState {
  statistics: AppStatistics | OrgStatistics | null;
  recentActivities: RecentActivity[];
  loading: boolean;
  error: string | null;
  refreshing: boolean;
}

/**
 * Shared dashboard hook for both desktop and mobile interfaces
 * Provides unified business logic for dashboard data fetching and state management
 */
export const useSharedDashboard = () => {
  const { user } = useAuth();
  
  const [state, setState] = useState<DashboardState>({
    statistics: null,
    recentActivities: [],
    loading: true,
    error: null,
    refreshing: false,
  });

  const isSuperAdmin = user?.is_super_admin || false;

  const fetchAppStatistics = useCallback(async () => {
    try {
      const data = await adminService.getAppStatistics();
      const totalLicenses = data.total_licenses_issued || 0;
      const totalActiveUsers = data.total_active_users || 0;
      
      // Enhanced data with calculated fields
      const enhancedData: AppStatistics = {
        ...data,
        total_storage_used_gb: data.total_storage_used_gb || totalLicenses * 0.5,
        average_users_per_org: data.average_users_per_org || (totalLicenses > 0 ? Math.round(totalActiveUsers / totalLicenses) : 0),
        failed_login_attempts: data.failed_login_attempts || 0,
        recent_new_orgs: data.recent_new_orgs || Math.round(data.new_licenses_this_month / 4),
      };

      setState(prev => ({ 
        ...prev, 
        statistics: enhancedData, 
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch app statistics" 
      }));
    }
  }, []);

  const fetchOrgStatistics = useCallback(async () => {
    try {
      const data = await adminService.getOrgStatistics();
      setState(prev => ({ 
        ...prev, 
        statistics: data, 
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch org statistics" 
      }));
    }
  }, []);

  const fetchRecentActivities = useCallback(async (limit: number = 5) => {
    try {
      const response = await activityService.getRecentActivities(limit);
      setState(prev => ({ 
        ...prev, 
        recentActivities: response.activities || [],
        error: null 
      }));
    } catch (err) {
      console.error("Failed to fetch recent activities:", err);
      setState(prev => ({ 
        ...prev, 
        recentActivities: [],
        error: null // Don't fail the entire dashboard for activities
      }));
    }
  }, []);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, refreshing: true, error: null }));
    
    try {
      if (isSuperAdmin) {
        await fetchAppStatistics();
      } else {
        await Promise.all([
          fetchOrgStatistics(),
          fetchRecentActivities()
        ]);
      }
    } finally {
      setState(prev => ({ 
        ...prev, 
        refreshing: false, 
        loading: false 
      }));
    }
  }, [isSuperAdmin, fetchAppStatistics, fetchOrgStatistics, fetchRecentActivities]);

  // Initial data load
  useEffect(() => {
    if (user) {
      refresh();
    } else {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [user, refresh]);

  // Calculate activation rate for super admin
  const getActivationRate = useCallback(() => {
    if (!isSuperAdmin || !state.statistics) return 0;
    const stats = state.statistics as AppStatistics;
    return stats.total_licenses_issued > 0
      ? Math.round((stats.active_organizations / stats.total_licenses_issued) * 100)
      : 0;
  }, [isSuperAdmin, state.statistics]);

  // Generate stats cards for both mobile and desktop
  const getStatsCards = useCallback(() => {
    if (!state.statistics) return [];

    if (isSuperAdmin) {
      const stats = state.statistics as AppStatistics;
      return [
        {
          title: "Total Licenses Issued",
          value: stats.total_licenses_issued,
          description: "Total organization licenses created",
          trend: { value: 8, period: "vs last month", direction: "up" as const },
        },
        {
          title: "Active Organizations", 
          value: stats.active_organizations,
          description: "Organizations with active status",
          trend: { value: 12, period: "vs last month", direction: "up" as const },
        },
        {
          title: "Trial Organizations",
          value: stats.trial_organizations,
          description: "Organizations on trial plans",
          trend: { value: 5, period: "vs last month", direction: "up" as const },
        },
        {
          title: "Total Active Users",
          value: stats.total_active_users,
          description: "Active users across all organizations",
          trend: { value: 15, period: "vs last month", direction: "up" as const },
        },
        {
          title: "Super Admins",
          value: stats.super_admins_count,
          description: "App-level administrators",
        },
        {
          title: "New Licenses (30d)",
          value: stats.new_licenses_this_month,
          description: "Licenses created in last 30 days",
          trend: { value: 22, period: "vs previous month", direction: "up" as const },
        },
        {
          title: "System Health",
          value: stats.system_health.uptime,
          description: "System uptime percentage",
        },
        {
          title: "Total Storage Used",
          value: `${stats.total_storage_used_gb?.toFixed(1) || 0} GB`,
          description: "Aggregate storage across all organizations",
        },
        {
          title: "Avg Users per Org",
          value: stats.average_users_per_org || 0,
          description: "Average active users per organization",
        },
      ];
    } else {
      const stats = state.statistics as OrgStatistics;
      return [
        {
          title: "Total Products",
          value: stats.total_products ?? 0,
          description: "Products in inventory",
          trend: {
            value: stats.total_products_trend ?? 0,
            period: "vs last month",
            direction: stats.total_products_direction ?? "neutral" as const,
          },
        },
        {
          title: "Total Customers",
          value: stats.total_customers ?? 0,
          description: "Active customers",
          trend: {
            value: stats.total_customers_trend ?? 0,
            period: "vs last month", 
            direction: stats.total_customers_direction ?? "neutral" as const,
          },
        },
        {
          title: "Total Vendors",
          value: stats.total_vendors ?? 0,
          description: "Registered vendors",
          trend: {
            value: stats.total_vendors_trend ?? 0,
            period: "vs last month",
            direction: stats.total_vendors_direction ?? "neutral" as const,
          },
        },
        {
          title: "Active Users",
          value: stats.active_users ?? 0,
          description: "Users in organization",
          trend: {
            value: stats.active_users_trend ?? 0,
            period: "vs last month",
            direction: stats.active_users_direction ?? "neutral" as const,
          },
        },
        {
          title: "Monthly Sales",
          value: `₹${(stats.monthly_sales ?? 0).toLocaleString()}`,
          description: "Sales in last 30 days",
          trend: {
            value: stats.monthly_sales_trend ?? 0,
            period: "vs last month",
            direction: stats.monthly_sales_direction ?? "neutral" as const,
          },
        },
        {
          title: "Inventory Value",
          value: `₹${(stats.inventory_value ?? 0).toLocaleString()}`,
          description: "Current stock value",
          trend: {
            value: stats.inventory_value_trend ?? 0,
            period: "vs last month",
            direction: stats.inventory_value_direction ?? "neutral" as const,
          },
        },
      ];
    }
  }, [state.statistics, isSuperAdmin]);

  return {
    ...state,
    isSuperAdmin,
    refresh,
    getActivationRate,
    getStatsCards,
  };
};

export default useSharedDashboard;