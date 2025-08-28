'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  MonetizationOn as MoneyIcon,
  ShoppingCart as ShoppingCartIcon,
  Timeline as TimelineIcon,
  Star as StarIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

interface CustomerMetric {
  customerId: number;
  name: string;
  totalRevenue: number;
  totalOrders: number;
  avgOrderValue: number;
  lastOrderDate: string;
  customerSince: string;
  status: 'active' | 'inactive' | 'churned';
  lifetimeValue: number;
  satisfactionScore: number;
}

interface AnalyticsData {
  totalCustomers: number;
  activeCustomers: number;
  newCustomers: number;
  churnedCustomers: number;
  totalRevenue: number;
  avgLifetimeValue: number;
  avgSatisfactionScore: number;
  topCustomers: CustomerMetric[];
  customerSegments: {
    segment: string;
    count: number;
    revenue: number;
    percentage: number;
  }[];
}

const CustomerAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('last_30_days');

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData: AnalyticsData = {
          totalCustomers: 1245,
          activeCustomers: 987,
          newCustomers: 156,
          churnedCustomers: 23,
          totalRevenue: 2450000,
          avgLifetimeValue: 12500,
          avgSatisfactionScore: 4.2,
          topCustomers: [
            {
              customerId: 1,
              name: 'TechCorp Ltd',
              totalRevenue: 450000,
              totalOrders: 23,
              avgOrderValue: 19565,
              lastOrderDate: '2024-01-15',
              customerSince: '2022-03-10',
              status: 'active',
              lifetimeValue: 450000,
              satisfactionScore: 4.8
            },
            {
              customerId: 2,
              name: 'Global Systems Inc',
              totalRevenue: 320000,
              totalOrders: 18,
              avgOrderValue: 17778,
              lastOrderDate: '2024-01-20',
              customerSince: '2021-07-15',
              status: 'active',
              lifetimeValue: 320000,
              satisfactionScore: 4.5
            },
            {
              customerId: 3,
              name: 'Manufacturing Co',
              totalRevenue: 275000,
              totalOrders: 31,
              avgOrderValue: 8871,
              lastOrderDate: '2024-01-18',
              customerSince: '2020-11-22',
              status: 'active',
              lifetimeValue: 275000,
              satisfactionScore: 4.3
            },
            {
              customerId: 4,
              name: 'Retail Corp',
              totalRevenue: 185000,
              totalOrders: 42,
              avgOrderValue: 4405,
              lastOrderDate: '2023-12-08',
              customerSince: '2022-01-18',
              status: 'inactive',
              lifetimeValue: 185000,
              satisfactionScore: 3.9
            },
            {
              customerId: 5,
              name: 'Data Solutions Ltd',
              totalRevenue: 165000,
              totalOrders: 15,
              avgOrderValue: 11000,
              lastOrderDate: '2024-01-22',
              customerSince: '2023-05-12',
              status: 'active',
              lifetimeValue: 165000,
              satisfactionScore: 4.7
            }
          ],
          customerSegments: [
            { segment: 'Enterprise', count: 45, revenue: 1500000, percentage: 61.2 },
            { segment: 'Mid-Market', count: 187, revenue: 650000, percentage: 26.5 },
            { segment: 'Small Business', count: 456, revenue: 250000, percentage: 10.2 },
            { segment: 'Startup', count: 557, revenue: 50000, percentage: 2.1 }
          ]
        };
        
        setAnalyticsData(mockData);
      } catch (err) {
        setError('Failed to load customer analytics');
        console.error('Error fetching analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, [timeRange]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'churned': return 'error';
      default: return 'default';
    }
  };

  const getSatisfactionIcon = (score: number) => {
    if (score >= 4.5) return <StarIcon color="success" />;
    if (score >= 3.5) return <StarIcon color="warning" />;
    return <WarningIcon color="error" />;
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Customer Analytics</Typography>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="last_7_days">Last 7 Days</MenuItem>
            <MenuItem value="last_30_days">Last 30 Days</MenuItem>
            <MenuItem value="last_90_days">Last 90 Days</MenuItem>
            <MenuItem value="last_year">Last Year</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {analyticsData && (
        <>
          {/* Key Metrics Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PeopleIcon color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Total Customers
                      </Typography>
                      <Typography variant="h4">
                        {analyticsData.totalCustomers.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        +{analyticsData.newCustomers} new
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <MoneyIcon color="success" sx={{ mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Total Revenue
                      </Typography>
                      <Typography variant="h4">
                        ${(analyticsData.totalRevenue / 1000000).toFixed(1)}M
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        This period
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TimelineIcon color="warning" sx={{ mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Avg Lifetime Value
                      </Typography>
                      <Typography variant="h4">
                        ${analyticsData.avgLifetimeValue.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        +12.5%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <StarIcon color="info" sx={{ mr: 2 }} />
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Satisfaction Score
                      </Typography>
                      <Typography variant="h4">
                        {analyticsData.avgSatisfactionScore}/5.0
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Average rating
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Tabs for different analytics views */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="Customer Overview" />
              <Tab label="Segmentation" />
              <Tab label="Top Customers" />
            </Tabs>
          </Paper>

          {/* Customer Overview Tab */}
          {tabValue === 0 && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Customer Status Distribution</Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Active Customers</Typography>
                        <Typography variant="body2">{analyticsData.activeCustomers}</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(analyticsData.activeCustomers / analyticsData.totalCustomers) * 100}
                        color="success"
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">New Customers</Typography>
                        <Typography variant="body2">{analyticsData.newCustomers}</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(analyticsData.newCustomers / analyticsData.totalCustomers) * 100}
                        color="primary"
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Churned Customers</Typography>
                        <Typography variant="body2">{analyticsData.churnedCustomers}</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={(analyticsData.churnedCustomers / analyticsData.totalCustomers) * 100}
                        color="error"
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid size={{ xs: 12, md: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Customer Health Metrics</Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUpIcon color="success" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Customer Retention Rate"
                          secondary="92.3% (up 2.1% from last period)"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <ShoppingCartIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Repeat Purchase Rate"
                          secondary="78.5% of customers made repeat purchases"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <WarningIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Churn Risk"
                          secondary="23 customers at risk of churning"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Customer Segmentation Tab */}
          {tabValue === 1 && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Customer Segments by Revenue</Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Segment</TableCell>
                            <TableCell align="right">Customer Count</TableCell>
                            <TableCell align="right">Total Revenue</TableCell>
                            <TableCell align="right">Revenue %</TableCell>
                            <TableCell align="right">Avg Revenue per Customer</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData.customerSegments.map((segment) => (
                            <TableRow key={segment.segment}>
                              <TableCell>
                                <Chip 
                                  label={segment.segment}
                                  color={segment.segment === 'Enterprise' ? 'success' : 
                                         segment.segment === 'Mid-Market' ? 'primary' :
                                         segment.segment === 'Small Business' ? 'warning' : 'default'}
                                />
                              </TableCell>
                              <TableCell align="right">{segment.count}</TableCell>
                              <TableCell align="right">${segment.revenue.toLocaleString()}</TableCell>
                              <TableCell align="right">{segment.percentage}%</TableCell>
                              <TableCell align="right">
                                ${Math.round(segment.revenue / segment.count).toLocaleString()}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Top Customers Tab */}
          {tabValue === 2 && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Top Customers by Revenue</Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Customer Name</TableCell>
                            <TableCell align="right">Total Revenue</TableCell>
                            <TableCell align="right">Total Orders</TableCell>
                            <TableCell align="right">Avg Order Value</TableCell>
                            <TableCell align="center">Status</TableCell>
                            <TableCell align="center">Satisfaction</TableCell>
                            <TableCell>Last Order</TableCell>
                            <TableCell>Customer Since</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData.topCustomers.map((customer) => (
                            <TableRow key={customer.customerId} hover>
                              <TableCell>{customer.name}</TableCell>
                              <TableCell align="right">${customer.totalRevenue.toLocaleString()}</TableCell>
                              <TableCell align="right">{customer.totalOrders}</TableCell>
                              <TableCell align="right">${customer.avgOrderValue.toLocaleString()}</TableCell>
                              <TableCell align="center">
                                <Chip 
                                  label={customer.status}
                                  color={getStatusColor(customer.status) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                  {getSatisfactionIcon(customer.satisfactionScore)}
                                  <Typography variant="body2" sx={{ ml: 1 }}>
                                    {customer.satisfactionScore}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                {new Date(customer.lastOrderDate).toLocaleDateString()}
                              </TableCell>
                              <TableCell>
                                {new Date(customer.customerSince).toLocaleDateString()}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </>
      )}
    </Container>
  );
};

export default CustomerAnalytics;