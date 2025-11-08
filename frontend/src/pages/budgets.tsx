// frontend/src/pages/budgets.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Chip,
  TextField,
} from "@mui/material";
import { Refresh, Download, Print } from "@mui/icons-material";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

import { ProtectedPage } from '../components/ProtectedPage';
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface BudgetData {
  budget_year: number;
  cost_centers: Array<{
    cost_center_id: number;
    cost_center_name: string;
    cost_center_code: string;
    budget_amount: number;
    actual_amount: number;
    variance: number;
    variance_percent: number;
    status: string;
  }>;
  summary: {
    total_budget: number;
    total_actual: number;
    total_variance: number;
    variance_percent: number;
  };
}

const BudgetsPage: React.FC = () => {
  const [data, setData] = useState<BudgetData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [budgetYear, setBudgetYear] = useState(new Date().getFullYear());

  const fetchBudgetData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/budgets", {
        params: { budget_year: budgetYear },
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch budget data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgetData();
  }, [budgetYear]);

  if (loading) {
    return (
      <ProtectedPage moduleKey="finance" action="read">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </ProtectedPage>
    );
  }

  if (error) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={fetchBudgetData}>
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

  const chartData = {
    labels: data.cost_centers.map((cc) => cc.cost_center_name),
    datasets: [
      {
        label: "Budget",
        data: data.cost_centers.map((cc) => cc.budget_amount),
        backgroundColor: "#2196f3",
      },
      {
        label: "Actual",
        data: data.cost_centers.map((cc) => cc.actual_amount),
        backgroundColor: "#ff9800",
      },
    ],
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "over_budget":
        return "error";
      case "under_budget":
        return "warning";
      default:
        return "success";
    }
  };

  return (
    <ProtectedPage moduleKey="finance" action="read">
      <Box sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Budget Management
          </Typography>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              type="number"
              label="Budget Year"
              value={budgetYear}
              onChange={(e) => setBudgetYear(parseInt(e.target.value))}
              size="small"
              sx={{ width: 150 }}
            />
            <IconButton onClick={fetchBudgetData} color="primary">
              <Refresh />
            </IconButton>
            <Button startIcon={<Download />} variant="outlined">
              Export
            </Button>
            <Button startIcon={<Print />} variant="outlined">
              Print
            </Button>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Budget
                </Typography>
                <Typography variant="h5" color="primary.main">
                  {formatCurrency(data.summary.total_budget)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Actual
                </Typography>
                <Typography variant="h5" color="warning.main">
                  {formatCurrency(data.summary.total_actual)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Variance
                </Typography>
                <Typography
                  variant="h5"
                  color={data.summary.total_variance > 0 ? "error.main" : "success.main"}
                >
                  {formatCurrency(Math.abs(data.summary.total_variance))}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Variance %
                </Typography>
                <Typography
                  variant="h5"
                  color={data.summary.variance_percent > 0 ? "error.main" : "success.main"}
                >
                  {data.summary.variance_percent.toFixed(2)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Chart */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Budget vs Actual by Cost Center
            </Typography>
            <Box sx={{ height: 400 }}>
              <Bar data={chartData} />
            </Box>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Cost Center Details
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Cost Center</TableCell>
                    <TableCell>Code</TableCell>
                    <TableCell align="right">Budget</TableCell>
                    <TableCell align="right">Actual</TableCell>
                    <TableCell align="right">Variance</TableCell>
                    <TableCell align="right">Variance %</TableCell>
                    <TableCell align="right">Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.cost_centers.map((cc) => (
                    <TableRow key={cc.cost_center_id}>
                      <TableCell>{cc.cost_center_name}</TableCell>
                      <TableCell>{cc.cost_center_code}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(cc.budget_amount)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(cc.actual_amount)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(Math.abs(cc.variance))}
                      </TableCell>
                      <TableCell align="right">
                        {cc.variance_percent.toFixed(2)}%
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={cc.status.replace("_", " ").toUpperCase()}
                          color={getStatusColor(cc.status)}
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
      </Box>
    </ProtectedPage>
  );
};
export default BudgetsPage;
