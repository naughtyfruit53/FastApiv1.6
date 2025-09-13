import React, { useState } from 'react';
import { Box, Grid, Typography, IconButton } from '@mui/material';
import { Refresh, Notifications, Search } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileSearchBar 
} from '../../components/mobile';
import { useAuth } from '../../context/AuthContext';

// Sample metric data
const mobileMetrics = [
  {
    title: 'Today\'s Sales',
    value: '₹1,24,500',
    change: '+12.5%',
    changeType: 'positive' as const,
    icon: '💰',
  },
  {
    title: 'Pending Orders',
    value: '23',
    change: '-5',
    changeType: 'negative' as const,
    icon: '📋',
  },
  {
    title: 'New Customers',
    value: '8',
    change: '+3',
    changeType: 'positive' as const,
    icon: '👥',
  },
  {
    title: 'Low Stock Items',
    value: '12',
    change: '+2',
    changeType: 'warning' as const,
    icon: '📦',
  },
];

const recentActivities = [
  {
    id: 1,
    title: 'New order #INV-2024-001',
    description: 'Customer: John Doe',
    time: '2 min ago',
    type: 'order',
  },
  {
    id: 2,
    title: 'Payment received',
    description: '₹45,000 from ABC Corp',
    time: '15 min ago',
    type: 'payment',
  },
  {
    id: 3,
    title: 'Low stock alert',
    description: 'Product: Widget A',
    time: '1 hour ago',
    type: 'alert',
  },
  {
    id: 4,
    title: 'New customer registered',
    description: 'Jane Smith - Premium Plan',
    time: '2 hours ago',
    type: 'customer',
  },
];

const MobileDashboard: React.FC = () => {
  const { user } = useAuth();
  const { isMobile } = useMobileDetection();
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const rightActions = (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <IconButton 
        size="small" 
        onClick={handleRefresh}
        disabled={refreshing}
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

  return (
    <MobileDashboardLayout
      title="Dashboard"
      subtitle={`Welcome back, ${user?.name || 'User'}!`}
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search Bar */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search transactions, orders..."
      />

      {/* Metrics Grid */}
      <Grid container spacing={isMobile ? 2 : 3}>
        {mobileMetrics.map((metric, index) => (
          <Grid item xs={6} key={index}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h2" sx={{ fontSize: '2rem', marginBottom: 1 }}>
                  {metric.icon}
                </Typography>
                <Typography variant="h4" sx={{ 
                  fontSize: isMobile ? '1.5rem' : '1.75rem',
                  fontWeight: 700,
                  marginBottom: 0.5,
                  color: 'text.primary',
                }}>
                  {metric.value}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: 'text.secondary',
                  marginBottom: 1,
                  fontSize: '0.875rem',
                }}>
                  {metric.title}
                </Typography>
                <Typography variant="caption" sx={{ 
                  color: metric.changeType === 'positive' ? 'success.main' 
                        : metric.changeType === 'negative' ? 'error.main'
                        : 'warning.main',
                  fontWeight: 600,
                }}>
                  {metric.change}
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
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

      {/* Recent Activity */}
      <MobileCard title="Recent Activity">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {recentActivities.map((activity) => (
            <Box key={activity.id} sx={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              padding: 1.5,
              borderRadius: 2,
              backgroundColor: 'grey.50',
              border: '1px solid',
              borderColor: 'divider',
            }}>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body1" sx={{ 
                  fontWeight: 600,
                  marginBottom: 0.5,
                  fontSize: '0.95rem',
                }}>
                  {activity.title}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: 'text.secondary',
                  fontSize: '0.875rem',
                }}>
                  {activity.description}
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ 
                color: 'text.secondary',
                fontSize: '0.75rem',
                whiteSpace: 'nowrap',
                marginLeft: 1,
              }}>
                {activity.time}
              </Typography>
            </Box>
          ))}
        </Box>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileDashboard;