// frontend/src/pages/finance-dashboard.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
} from "@mui/material";
import {
  TrendingUp,
  AccountBalance,
  Payment,
  Analytics,
  Refresh,
  Download,
} from "@mui/icons-material";
import { Doughnut, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from "chart.js";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";
import { ProtectedPage } from "../components/ProtectedPage";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
);
interface FinancialRatios {
  current_ratio: number;
  debt_to_equity: number;
  working_capital: number;
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
}
interface CashFlow {
  inflow: number;
  outflow: number;
  net_flow: number;
}
interface CostCenter {
  name: string;
  budget: number;
  actual: number;
  variance_percent: number;
}
interface KPI {
  code: string;
  name: string;
  category: string;
  value: number;
  target?: number;
  variance?: number;
  period_end: string;
}
interface DashboardData {
  period: {
    start_date: string;
    end_date: string;
  };
  financial_ratios: FinancialRatios;
  cash_flow: CashFlow;
  accounts_aging: {
    overdue_payables: number;
    overdue_receivables: number;
  };
  cost_centers: CostCenter[];
  recent_kpis: KPI[];
}
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`finance-tabpanel-${index}`}
      aria-labelledby={`finance-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}
const FinanceDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/dashboard", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchDashboardData();
  }, []);
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };
  if (loading) {
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
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={fetchDashboardData}>
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }
  if (!data) {
    return null;
  }
  // Chart data for cash flow
  const cashFlowChartData = {
    labels: ["Inflow", "Outflow"],
    datasets: [
      {
        data: [data.cash_flow.inflow, data.cash_flow.outflow],
        backgroundColor: ["#4caf50", "#f44336"],
        borderWidth: 1,
      },
    ],
  };
  // Chart data for cost center performance
  const costCenterChartData = {
    labels: data.cost_centers.map((cc) => cc.name),
    datasets: [
      {
        label: "Budget",
        data: data.cost_centers.map((cc) => cc.budget),
        backgroundColor: "#2196f3",
        borderWidth: 1,
      },
      {
        label: "Actual",
        data: data.cost_centers.map((cc) => cc.actual),
        backgroundColor: "#ff9800",
        borderWidth: 1,
      },
    ],
  };
  return (
    <ProtectedPage moduleKey="finance" action="read">
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Finance Dashboard
          </Typography>
        <Box>
          <IconButton onClick={fetchDashboardData} color="primary">
            <Refresh />
          </IconButton>
          <Button startIcon={<Download />} variant="outlined" sx={{ ml: 1 }}>
            Export
          </Button>
        </Box>
      </Box>
      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountBalance color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Assets
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(data.financial_ratios.total_assets)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Payment color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Liabilities
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(data.financial_ratios.total_liabilities)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Working Capital
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(data.financial_ratios.working_capital)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Analytics color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Current Ratio
                  </Typography>
                  <Typography variant="h6">
                    {data.financial_ratios.current_ratio.toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Tabs for detailed views */}
      <Paper sx={{ width: "100%" }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="finance dashboard tabs"
        >
          <Tab label="Cash Flow" />
          <Tab label="Cost Centers" />
          <Tab label="KPIs" />
          <Tab label="Aging" />
        </Tabs>
        {/* Cash Flow Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cash Flow Overview
                  </Typography>
                  <Box sx={{ height: 300 }}>
                    <Doughnut data={cashFlowChartData} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cash Flow Details
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography>Inflow:</Typography>
                      <Typography color="success.main">
                        {formatCurrency(data.cash_flow.inflow)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography>Outflow:</Typography>
                      <Typography color="error.main">
                        {formatCurrency(data.cash_flow.outflow)}
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="h6">Net Flow:</Typography>
                      <Typography
                        variant="h6"
                        color={
                          data.cash_flow.net_flow >= 0
                            ? "success.main"
                            : "error.main"
                        }
                      >
                        {formatCurrency(data.cash_flow.net_flow)}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
        {/* Cost Centers Tab */}
        <TabPanel value={activeTab} index={1}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Center Performance
              </Typography>
              <Box sx={{ height: 400, mb: 3 }}>
                <Bar data={costCenterChartData} />
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Cost Center</TableCell>
                      <TableCell align="right">Budget</TableCell>
                      <TableCell align="right">Actual</TableCell>
                      <TableCell align="right">Variance %</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.cost_centers.map((cc, index) => (
                      <TableRow key={index}>
                        <TableCell>{cc.name}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(cc.budget)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(cc.actual)}
                        </TableCell>
                        <TableCell align="right">
                          {formatPercentage(cc.variance_percent)}
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={
                              cc.variance_percent > 10
                                ? "Over Budget"
                                : cc.variance_percent < -10
                                  ? "Under Budget"
                                  : "On Track"
                            }
                            color={
                              cc.variance_percent > 10
                                ? "error"
                                : cc.variance_percent < -10
                                  ? "warning"
                                  : "success"
                            }
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
        </TabPanel>
        {/* KPIs Tab */}
        <TabPanel value={activeTab} index={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Financial KPIs
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>KPI Name</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell align="right">Target</TableCell>
                      <TableCell align="right">Variance %</TableCell>
                      <TableCell>Period</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recent_kpis.map((kpi, index) => (
                      <TableRow key={index}>
                        <TableCell>{kpi.name}</TableCell>
                        <TableCell>
                          <Chip label={kpi.category} size="small" />
                        </TableCell>
                        <TableCell align="right">
                          {kpi.value.toFixed(2)}
                        </TableCell>
                        <TableCell align="right">
                          {kpi.target ? kpi.target.toFixed(2) : "N/A"}
                        </TableCell>
                        <TableCell align="right">
                          {kpi.variance ? (
                            <Typography
                              color={
                                kpi.variance >= 0
                                  ? "success.main"
                                  : "error.main"
                              }
                            >
                              {formatPercentage(kpi.variance)}
                            </Typography>
                          ) : (
                            "N/A"
                          )}
                        </TableCell>
                        <TableCell>
                          {new Date(kpi.period_end).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </TabPanel>
        {/* Aging Tab */}
        <TabPanel value={activeTab} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Overdue Receivables
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {formatCurrency(data.accounts_aging.overdue_receivables)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Amount past due date
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Overdue Payables
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {formatCurrency(data.accounts_aging.overdue_payables)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Amount past due date
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
    </ProtectedPage>
  );
};
export default FinanceDashboard;