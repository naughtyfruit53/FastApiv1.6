import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Chip,
  CircularProgress,
  Alert,
  Paper,
  Grid as MuiGrid,
} from '@mui/material';
import {
  Business,
  People,
  Inventory,
  AttachMoney,
  TrendingUp,
  SettingsApplications
} from '@mui/icons-material';
import adminService from '../../services/adminService';
import MetricCard from '../../components/MetricCard';
import DashboardLayout from '../../components/DashboardLayout';
import ModernLoading from '../../components/ModernLoading';
import { StickyNotesPanel } from '../../components/StickyNotes';
import useStickyNotes from '../../hooks/useStickyNotes';
import '../../styles/modern-theme.css';

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
}

const OrgDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<OrgStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { userSettings } = useStickyNotes();

  useEffect(() => {
    fetchOrgStatistics();
     
  }, []);

  const fetchOrgStatistics = async () => {
    try {
      const data = await adminService.getOrgStatistics();
      setStatistics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout 
        title="Organization Dashboard"
        subtitle="Monitor your organization's key performance metrics"
      >
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
      <DashboardLayout 
        title="Organization Dashboard"
        subtitle="Monitor your organization's key performance metrics"
      >
        <Alert 
          severity="error"
          sx={{ 
            borderRadius: 'var(--radius-lg)',
            '& .MuiAlert-message': {
              fontSize: 'var(--font-size-sm)'
            }
          }}
        >
          Error loading dashboard: {error}
        </Alert>
      </DashboardLayout>
    );
  }

  if (!statistics) {
    return (
      <DashboardLayout 
        title="Organization Dashboard"
        subtitle="Monitor your organization's key performance metrics"
      >
        <Alert 
          severity="info"
          sx={{ 
            borderRadius: 'var(--radius-lg)',
            '& .MuiAlert-message': {
              fontSize: 'var(--font-size-sm)'
            }
          }}
        >
          No statistics available
        </Alert>
      </DashboardLayout>
    );
  }

  const statsCards = [
    {
      title: 'Total Products',
      value: statistics.total_products ?? 0,
      icon: <Inventory />,
      color: 'primary' as const,
      description: 'Products in inventory',
      trend: {
        value: 12,
        period: 'vs last month',
        direction: 'up' as const
      }
    },
    {
      title: 'Total Customers',
      value: statistics.total_customers ?? 0,
      icon: <People />,
      color: 'success' as const,
      description: 'Active customers',
      trend: {
        value: 8,
        period: 'vs last month',
        direction: 'up' as const
      }
    },
    {
      title: 'Total Vendors',
      value: statistics.total_vendors ?? 0,
      icon: <Business />,
      color: 'info' as const,
      description: 'Registered vendors',
      trend: {
        value: 3,
        period: 'vs last month',
        direction: 'up' as const
      }
    },
    {
      title: 'Active Users',
      value: statistics.active_users ?? 0,
      icon: <People />,
      color: 'warning' as const,
      description: 'Users in organization',
      trend: {
        value: 5,
        period: 'vs last month',
        direction: 'up' as const
      }
    },
    {
      title: 'Monthly Sales',
      value: `$${(statistics.monthly_sales ?? 0).toLocaleString()}`,
      icon: <AttachMoney />,
      color: 'success' as const,
      description: 'Sales in last 30 days',
      trend: {
        value: 15,
        period: 'vs last month',
        direction: 'up' as const
      }
    },
    {
      title: 'Inventory Value',
      value: `$${(statistics.inventory_value ?? 0).toLocaleString()}`,
      icon: <TrendingUp />,
      color: 'primary' as const,
      description: 'Current stock value',
      trend: {
        value: 7,
        period: 'vs last month',
        direction: 'up' as const
      }
    }
  ];

  return (
    <DashboardLayout 
      title="Organization Dashboard"
      subtitle="Monitor your organization's key performance metrics"
    >
      {/* Sticky Notes Panel */}
      <StickyNotesPanel stickyNotesEnabled={userSettings.sticky_notes_enabled} />
      
      <Box className="modern-grid cols-3" sx={{ mb: 4 }}>
        {/* Statistics Cards */}
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
        {/* Plan Information */}
        <Paper 
          className="modern-card"
          sx={{ p: 3 }}
        >
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            Subscription Plan
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Chip 
              label={statistics.plan_type?.toUpperCase() ?? 'N/A'} 
              color={statistics.plan_type === 'trial' ? 'warning' : 'primary'}
              variant="filled"
              sx={{ 
                fontWeight: 600,
                '&.MuiChip-colorPrimary': {
                  backgroundColor: 'var(--primary-600)',
                  color: 'white'
                },
                '&.MuiChip-colorWarning': {
                  backgroundColor: 'var(--warning-500)',
                  color: 'white'
                }
              }}
            />
          </Box>
          <Typography variant="body2" color="textSecondary">
            Storage Used: {statistics.storage_used_gb ?? 0} GB
          </Typography>
        </Paper>

        {/* Recent Activity */}
        <Paper 
          className="modern-card"
          sx={{ p: 3 }}
        >
          <Typography variant="h6" className="modern-card-title" gutterBottom>
            Recent Activity
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {/* Placeholder for recent activity list */}
            No recent activity available
          </Typography>
        </Paper>
      </Box>

      {/* Growth Metrics */}
      <Paper 
        className="modern-card"
        sx={{ p: 4 }}
      >
        <Typography variant="h6" className="modern-card-title" gutterBottom sx={{ mb: 3 }}>
          Organization Overview
        </Typography>
        <Box className="modern-grid cols-3">
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              sx={{ 
                color: 'var(--primary-600)',
                fontWeight: 700,
                mb: 1
              }}
            >
              {statistics.total_products ?? 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Products
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              sx={{ 
                color: 'var(--secondary-600)',
                fontWeight: 700,
                mb: 1
              }}
            >
              {statistics.active_users ?? 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Active Users
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              sx={{ 
                color: 'var(--success-600)',
                fontWeight: 700,
                mb: 1
              }}
            >
              {statistics.monthly_sales !== undefined && statistics.monthly_sales !== null
                ? Math.round((statistics.monthly_sales / 100000) * 100)
                : 0
              }%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Monthly Growth
            </Typography>
          </Box>
        </Box>
      </Paper>
    </DashboardLayout>
  );
};

export default OrgDashboard;