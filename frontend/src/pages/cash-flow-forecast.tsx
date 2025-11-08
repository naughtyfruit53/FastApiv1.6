// frontend/src/pages/cash-flow-forecast.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  TextField,
} from "@mui/material";
import { Refresh, Download, Print } from "@mui/icons-material";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

import { ProtectedPage } from '../components/ProtectedPage';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface ForecastData {
  period: {
    start_date: string;
    end_date: string;
  };
  forecast: Array<{
    period: string;
    projected_inflow: number;
    projected_outflow: number;
    net_cash_flow: number;
    cumulative_cash: number;
  }>;
  summary: {
    total_projected_inflow: number;
    total_projected_outflow: number;
    net_cash_change: number;
    opening_balance: number;
    closing_balance: number;
  };
}

const CashFlowForecastPage: React.FC = () => {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [months, setMonths] = useState(6);

  const fetchForecastData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/cash-flow-forecast", {
        params: { months },
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch cash flow forecast");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecastData();
  }, [months]);

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
          <Button color="inherit" size="small" onClick={fetchForecastData}>
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
    labels: data.forecast.map((f) => f.period),
    datasets: [
      {
        label: "Projected Inflow",
        data: data.forecast.map((f) => f.projected_inflow),
        borderColor: "#4caf50",
        backgroundColor: "rgba(76, 175, 80, 0.1)",
        fill: true,
      },
      {
        label: "Projected Outflow",
        data: data.forecast.map((f) => f.projected_outflow),
        borderColor: "#f44336",
        backgroundColor: "rgba(244, 67, 54, 0.1)",
        fill: true,
      },
      {
        label: "Net Cash Flow",
        data: data.forecast.map((f) => f.net_cash_flow),
        borderColor: "#2196f3",
        backgroundColor: "rgba(33, 150, 243, 0.1)",
        fill: true,
      },
    ],
  };

  return (
    <ProtectedPage moduleKey="finance" action="read">
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Box sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4" component="h1">
              Cash Flow Forecast
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
              <TextField
                type="number"
                label="Forecast Months"
                value={months}
                onChange={(e) => setMonths(parseInt(e.target.value))}
                size="small"
                sx={{ width: 150 }}
              />
              <IconButton onClick={fetchForecastData} color="primary">
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
                    Total Projected Inflow
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {formatCurrency(data.summary.total_projected_inflow)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Projected Outflow
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {formatCurrency(data.summary.total_projected_outflow)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Net Cash Change
                  </Typography>
                  <Typography
                    variant="h5"
                    color={data.summary.net_cash_change >= 0 ? "success.main" : "error.main"}
                  >
                    {formatCurrency(Math.abs(data.summary.net_cash_change))}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Projected Closing Balance
                  </Typography>
                  <Typography variant="h5" color="primary.main">
                    {formatCurrency(data.summary.closing_balance)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Chart */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cash Flow Forecast Trend
              </Typography>
              <Box sx={{ height: 400 }}>
                <Line data={chartData} />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </LocalizationProvider>
    </ProtectedPage>
  );
};
export default CashFlowForecastPage;
