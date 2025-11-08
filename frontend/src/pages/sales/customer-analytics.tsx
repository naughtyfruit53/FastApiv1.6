"use client";
import React, { useState, useEffect } from "react";
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
  Divider,
} from "@mui/material";
import {
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  MonetizationOn as MoneyIcon,
  ShoppingCart as ShoppingCartIcon,
  Timeline as TimelineIcon,
  Star as StarIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { crmService, CustomerAnalytics } from "../../services/crmService";
import { formatCurrency } from "../../utils/currencyUtils";
import { ProtectedPage } from "../../components/ProtectedPage";

const CustomerAnalytics: React.FC = () => {
  const router = useRouter();
  const [analyticsData, setAnalyticsData] = useState<CustomerAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState("last_30_days");

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        const periodEnd = new Date();
        let periodStart = new Date();
        switch (timeRange) {
          case "last_7_days":
            periodStart.setDate(periodEnd.getDate() - 7);
            break;
          case "last_30_days":
            periodStart.setDate(periodEnd.getDate() - 30);
            break;
          case "last_90_days":
            periodStart.setDate(periodEnd.getDate() - 90);
            break;
          case "last_year":
            periodStart.setFullYear(periodEnd.getFullYear() - 1);
            break;
        }
        const data = await crmService.getCustomerAnalytics({
          period_start: periodStart.toISOString().split("T")[0],
          period_end: periodEnd.toISOString().split("T")[0],
        });
        setAnalyticsData(data);
      } catch (err: any) {
        if (err.response?.status === 401) {
          router.push('/login');
          return;
        }
        setError(err.message || "Failed to load customer analytics");
        console.error("Error fetching analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyticsData();
  }, [timeRange, router]);

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
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

  if (!analyticsData) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="info">No analytics data available</Alert>
      </Container>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "inactive":
        return "warning";
      case "churned":
        return "error";
      default:
        return "default";
    }
  };

  const getSatisfactionIcon = (score: number) => {
    if (score >= 4.5) {
      return <StarIcon color="success" />;
    }
    if (score >= 3.5) {
      return <StarIcon color="warning" />;
    }
    return <WarningIcon color="error" />;
  };

  return (
    <ProtectedPage moduleKey="sales" action="read">
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
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
      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <PeopleIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Customers
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData.total_customers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5 }} />+
                    {analyticsData.new_customers} new
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <MoneyIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Revenue
                  </Typography>
                  <Typography variant="h4">
                    {formatCurrency(analyticsData.total_revenue)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    This period
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <TimelineIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Lifetime Value
                  </Typography>
                  <Typography variant="h4">
                    {formatCurrency(analyticsData.average_lifetime_value)}
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
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <StarIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Satisfaction Score
                  </Typography>
                  <Typography variant="h4">
                    {analyticsData.average_satisfaction_score}/5.0
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
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
        >
          <Tab label="Customer Overview" />
          <Tab label="Segmentation" />
          <Tab label="Top Customers" />
        </Tabs>
      </Paper>
      {/* Customer Overview Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Customer Status Distribution
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">
                      Active Customers
                    </Typography>
                    <Typography variant="body2">
                      {analyticsData.active_customers}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={
                      (analyticsData.active_customers /
                        analyticsData.total_customers) *
                      100
                    }
                    color="success"
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">New Customers</Typography>
                    <Typography variant="body2">
                      {analyticsData.new_customers}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={
                      (analyticsData.new_customers /
                        analyticsData.total_customers) *
                      100
                    }
                    color="primary"
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Box>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">
                      Churned Customers
                    </Typography>
                    <Typography variant="body2">
                      {analyticsData.churned_customers}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={
                      (analyticsData.churned_customers /
                        analyticsData.total_customers) *
                      100
                    }
                    color="error"
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Customer Health Metrics
                </Typography>
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
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Customer Segments by Revenue
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Segment</TableCell>
                        <TableCell align="right">Customer Count</TableCell>
                        <TableCell align="right">Total Revenue</TableCell>
                        <TableCell align="right">Revenue %</TableCell>
                        <TableCell align="right">
                          Avg Revenue per Customer
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(analyticsData.customers_by_segment || {}).map(([segment, count]) => {
                        // Placeholder calculations since backend might not provide all data
                        const revenue = 0; // Would come from backend
                        const percentage = 0;
                        return (
                          <TableRow key={segment}>
                            <TableCell>
                              <Chip
                                label={segment}
                                color={
                                  segment === "Enterprise"
                                    ? "success"
                                    : segment === "Mid-Market"
                                      ? "primary"
                                      : segment === "Small Business"
                                        ? "warning"
                                        : "default"
                                }
                              />
                            </TableCell>
                            <TableCell align="right">
                              {count}
                            </TableCell>
                            <TableCell align="right">
                              {formatCurrency(revenue)}
                            </TableCell>
                            <TableCell align="right">
                              {percentage}%
                            </TableCell>
                            <TableCell align="right">
                              {formatCurrency(revenue / (count as number))}
                            </TableCell>
                          </TableRow>
                        );
                      })}
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
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Customers by Revenue
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Customer Name</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                        <TableCell align="center">Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analyticsData.top_customers.map((customer) => (
                        <TableRow key={customer.id} hover>
                          <TableCell>{customer.name}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(customer.revenue)}
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label="active" // Placeholder
                              color={getStatusColor("active") as any}
                              size="small"
                            />
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
    </Container>
    </ProtectedPage>
  );
};
export default CustomerAnalytics;