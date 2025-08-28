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
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">
          Error loading dashboard: {error}
        </Alert>
      </Container>
    );
  }

  if (!statistics) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">
          No statistics available
        </Alert>
      </Container>
    );
  }

  const statsCards = [
    {
      title: 'Total Products',
      value: statistics.total_products ?? 0,
      icon: <Inventory />,
      color: '#1976D2',
      description: 'Products in inventory'
    },
    {
      title: 'Total Customers',
      value: statistics.total_customers ?? 0,
      icon: <People />,
      color: '#2E7D32',
      description: 'Active customers'
    },
    {
      title: 'Total Vendors',
      value: statistics.total_vendors ?? 0,
      icon: <Business />,
      color: '#7B1FA2',
      description: 'Registered vendors'
    },
    {
      title: 'Active Users',
      value: statistics.active_users ?? 0,
      icon: <People />,
      color: '#F57C00',
      description: 'Users in organization'
    },
    {
      title: 'Monthly Sales',
      value: `$${(statistics.monthly_sales ?? 0).toLocaleString()}`,
      icon: <AttachMoney />,
      color: '#5E35B1',
      description: 'Sales in last 30 days'
    },
    {
      title: 'Inventory Value',
      value: `$${(statistics.inventory_value ?? 0).toLocaleString()}`,
      icon: <TrendingUp />,
      color: '#D81B60',
      description: 'Current stock value'
    }
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
          Organization Dashboard
        </Typography>
        
        <MuiGrid container spacing={3}>
          {/* Statistics Cards */}
          {statsCards.map((stat, index) => (
            <MuiGrid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ color: stat.color, mr: 2 }}>
                      {stat.icon}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography color="textSecondary" variant="body2">
                        {stat.title}
                      </Typography>
                      <Typography variant="h4" component="h2">
                        {stat.value}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {stat.description}
                  </Typography>
                </CardContent>
              </Card>
            </MuiGrid>
          ))}

          {/* Plan Information */}
          <MuiGrid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Subscription Plan
              </Typography>
              <Chip 
                label={statistics.plan_type?.toUpperCase() ?? 'N/A'} 
                color={statistics.plan_type === 'trial' ? 'warning' : 'primary'} 
                sx={{ mb: 2 }}
              />
              <Typography variant="body2" color="textSecondary">
                Storage Used: {statistics.storage_used_gb ?? 0} GB
              </Typography>
            </Paper>
          </MuiGrid>

          {/* Recent Activity */}
          <MuiGrid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {/* Placeholder for recent activity list */}
                No recent activity available
              </Typography>
            </Paper>
          </MuiGrid>

          {/* Growth Metrics */}
          <MuiGrid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Organization Overview
              </Typography>
              <MuiGrid container spacing={2}>
                <MuiGrid item xs={12} sm={4}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="primary">
                      {statistics.total_products ?? 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Products
                    </Typography>
                  </Box>
                </MuiGrid>
                <MuiGrid item xs={12} sm={4}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="secondary">
                      {statistics.active_users ?? 0}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Active Users
                    </Typography>
                  </Box>
                </MuiGrid>
                <MuiGrid item xs={12} sm={4}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="success.main">
                      {statistics.monthly_sales !== undefined && statistics.monthly_sales !== null
                        ? Math.round((statistics.monthly_sales / 100000) * 100)
                        : 0
                      }%  {/* Example calculation */}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Monthly Growth
                    </Typography>
                  </Box>
                </MuiGrid>
              </MuiGrid>
            </Paper>
          </MuiGrid>
        </MuiGrid>
      </Container>
    </Box>
  );
};

export default OrgDashboard;