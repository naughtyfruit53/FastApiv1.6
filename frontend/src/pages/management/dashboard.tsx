"use client";
import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import {
  TrendingUp,
  Analytics,
  AccountBalance,
  People,
  Inventory,
  Assessment,
  Download,
  Refresh,
} from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
interface DashboardData {
  period: string;
  date_range: {
    start_date: string;
    end_date: string;
  };
  revenue_metrics: {
    total_revenue: number;
    sales_count: number;
    average_sale_value: number;
  };
  cost_metrics: {
    total_costs: number;
    purchase_count: number;
    average_purchase_value: number;
  };
  profitability: {
    gross_profit: number;
    profit_margin: number;
  };
  customer_metrics: {
    total_active_customers: number;
    new_customers: number;
    customer_growth_rate: number;
  };
  inventory_metrics: {
    total_products: number;
    low_stock_items: number;
    stock_health_percentage: number;
  };
  cash_flow: {
    pending_receivables: number;
    pending_payables: number;
    net_outstanding: number;
  };
}
const ManagementDashboard: React.FC = () => {
  const [period, setPeriod] = useState<string>("month");
  const [refreshKey, setRefreshKey] = useState<number>(0);
  // Fetch dashboard data
  const {
    data: dashboardData,
    isLoading,
    error,
    refetch,
  } = useQuery<DashboardData>({
    queryKey: ["management-dashboard", period, refreshKey],
    queryFn: async () => {
      const response = await axios.get(
        `/api/v1/management-reports/executive-dashboard?period=${period}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        },
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
  const handlePeriodChange = (event: any) => {
    setPeriod(event.target.value);
  };
  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
    refetch();
  };
  const handleExportExcel = async () => {
    try {
      const response = await axios.get(
        `/api/v1/management-reports/export/executive-dashboard?format=excel&period=${period}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          responseType: "blob",
        },
      );
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `executive_dashboard_${period}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(msg, err);
    }
  };
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };
  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };
  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: "primary" | "secondary" | "success" | "error" | "warning" | "info";
    subtitle?: string;
  }> = ({ title, value, icon, color, subtitle }) => (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h5" component="div">
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box color={`${color}.main`}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
      </Box>
    );
  }
  if (error) {
    return (
      <Alert severity="error">
        Failed to load management dashboard. Please check your permissions and
        try again.
      </Alert>
    );
  }
  if (!dashboardData) {
    return (
      <Alert severity="info">
        No dashboard data available for the selected period.
      </Alert>
    );
  }
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Executive Management Dashboard
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Period</InputLabel>
            <Select value={period} label="Period" onChange={handlePeriodChange}>
              <MenuItem value="day">Today</MenuItem>
              <MenuItem value="week">This Week</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
              <MenuItem value="quarter">This Quarter</MenuItem>
              <MenuItem value="year">This Year</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            size="small"
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExportExcel}
            size="small"
          >
            Export Excel
          </Button>
        </Box>
      </Box>
      {/* Date Range */}
      <Typography variant="body2" color="textSecondary" mb={3}>
        Reporting Period: {dashboardData.date_range.start_date} to{" "}
        {dashboardData.date_range.end_date}
      </Typography>
      {/* Revenue Metrics */}
      <Typography variant="h6" gutterBottom>
        Revenue & Sales Performance
      </Typography>
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Total Revenue"
            value={formatCurrency(dashboardData.revenue_metrics.total_revenue)}
            icon={<TrendingUp fontSize="large" />}
            color="success"
            subtitle={`${dashboardData.revenue_metrics.sales_count} sales`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Average Sale Value"
            value={formatCurrency(
              dashboardData.revenue_metrics.average_sale_value,
            )}
            icon={<AccountBalance fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Gross Profit"
            value={formatCurrency(dashboardData.profitability.gross_profit)}
            icon={<Analytics fontSize="large" />}
            color={
              dashboardData.profitability.gross_profit >= 0
                ? "success"
                : "error"
            }
            subtitle={`${formatPercentage(dashboardData.profitability.profit_margin)} margin`}
          />
        </Grid>
      </Grid>
      {/* Customer & Growth Metrics */}
      <Typography variant="h6" gutterBottom>
        Customer & Growth Metrics
      </Typography>
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Active Customers"
            value={dashboardData.customer_metrics.total_active_customers.toLocaleString()}
            icon={<People fontSize="large" />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="New Customers"
            value={dashboardData.customer_metrics.new_customers.toLocaleString()}
            icon={<TrendingUp fontSize="large" />}
            color="success"
            subtitle={`${formatPercentage(dashboardData.customer_metrics.customer_growth_rate)} growth`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Stock Health"
            value={formatPercentage(
              dashboardData.inventory_metrics.stock_health_percentage,
            )}
            icon={<Inventory fontSize="large" />}
            color={
              dashboardData.inventory_metrics.stock_health_percentage >= 80
                ? "success"
                : "warning"
            }
            subtitle={`${dashboardData.inventory_metrics.low_stock_items} low stock items`}
          />
        </Grid>
      </Grid>
      {/* Cash Flow Analysis */}
      <Typography variant="h6" gutterBottom>
        Cash Flow Analysis
      </Typography>
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Outstanding Amounts
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="center">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Pending Receivables</TableCell>
                      <TableCell align="right">
                        {formatCurrency(
                          dashboardData.cash_flow.pending_receivables,
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Chip label="To Receive" color="success" size="small" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Pending Payables</TableCell>
                      <TableCell align="right">
                        {formatCurrency(
                          dashboardData.cash_flow.pending_payables,
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Chip label="To Pay" color="warning" size="small" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <strong>Net Position</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>
                          {formatCurrency(
                            dashboardData.cash_flow.net_outstanding,
                          )}
                        </strong>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={
                            dashboardData.cash_flow.net_outstanding >= 0
                              ? "Positive"
                              : "Negative"
                          }
                          color={
                            dashboardData.cash_flow.net_outstanding >= 0
                              ? "success"
                              : "error"
                          }
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  fullWidth
                  onClick={() => (window.location.href = "/reports")}
                >
                  View Detailed Reports
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  fullWidth
                  onClick={() => (window.location.href = "/analytics")}
                >
                  Business Intelligence
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<People />}
                  fullWidth
                  onClick={() => (window.location.href = "/customers")}
                >
                  Customer Management
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Summary Statistics */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Period Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {dashboardData.revenue_metrics.sales_count}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Sales
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="secondary">
                  {dashboardData.cost_metrics.purchase_count}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Purchases
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {dashboardData.customer_metrics.new_customers}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  New Customers
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {dashboardData.inventory_metrics.low_stock_items}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Low Stock Alerts
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};
export default ManagementDashboard;
