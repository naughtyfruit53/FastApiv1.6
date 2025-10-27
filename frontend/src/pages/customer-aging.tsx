// frontend/src/pages/customer-aging.tsx
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
  Paper,
  CircularProgress,
  Alert,
  Button,
  IconButton,
} from "@mui/material";
import { Refresh, Download, Print } from "@mui/icons-material";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

ChartJS.register(ArcElement, Tooltip, Legend);

interface AgingBucket {
  amount: number;
  count: number;
  customers: number;
}

interface AgingData {
  as_of_date: string;
  aging_buckets: {
    current: AgingBucket;
    "30_days": AgingBucket;
    "60_days": AgingBucket;
    "90_days": AgingBucket;
    over_90: AgingBucket;
  };
  total_outstanding: number;
  summary: {
    total_customers: number;
    total_invoices: number;
    total_outstanding: number;
  };
}

const CustomerAgingPage: React.FC = () => {
  const [data, setData] = useState<AgingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgingData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/customer-aging", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch customer aging data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgingData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={fetchAgingData}>
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
    labels: ["Current", "1-30 Days", "31-60 Days", "61-90 Days", "Over 90 Days"],
    datasets: [
      {
        data: [
          data.aging_buckets.current.amount,
          data.aging_buckets["30_days"].amount,
          data.aging_buckets["60_days"].amount,
          data.aging_buckets["90_days"].amount,
          data.aging_buckets.over_90.amount,
        ],
        backgroundColor: [
          "#4caf50",
          "#2196f3",
          "#ff9800",
          "#f44336",
          "#9c27b0",
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Customer Aging Report
        </Typography>
        <Box>
          <IconButton onClick={fetchAgingData} color="primary">
            <Refresh />
          </IconButton>
          <Button startIcon={<Download />} variant="outlined" sx={{ ml: 1 }}>
            Export
          </Button>
          <Button startIcon={<Print />} variant="outlined" sx={{ ml: 1 }}>
            Print
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Outstanding
              </Typography>
              <Typography variant="h5" color="warning.main">
                {formatCurrency(data.summary.total_outstanding)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Customers
              </Typography>
              <Typography variant="h5">
                {data.summary.total_customers}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Invoices
              </Typography>
              <Typography variant="h5">
                {data.summary.total_invoices}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Chart and Table */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Aging Distribution
              </Typography>
              <Box sx={{ height: 300 }}>
                <Pie data={chartData} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Aging Summary
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Aging Period</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Current</TableCell>
                      <TableCell align="right">
                        {formatCurrency(data.aging_buckets.current.amount)}
                      </TableCell>
                      <TableCell align="right">
                        {data.aging_buckets.current.count}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>1-30 Days</TableCell>
                      <TableCell align="right">
                        {formatCurrency(data.aging_buckets["30_days"].amount)}
                      </TableCell>
                      <TableCell align="right">
                        {data.aging_buckets["30_days"].count}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>31-60 Days</TableCell>
                      <TableCell align="right">
                        {formatCurrency(data.aging_buckets["60_days"].amount)}
                      </TableCell>
                      <TableCell align="right">
                        {data.aging_buckets["60_days"].count}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>61-90 Days</TableCell>
                      <TableCell align="right">
                        {formatCurrency(data.aging_buckets["90_days"].amount)}
                      </TableCell>
                      <TableCell align="right">
                        {data.aging_buckets["90_days"].count}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Over 90 Days</TableCell>
                      <TableCell align="right">
                        {formatCurrency(data.aging_buckets.over_90.amount)}
                      </TableCell>
                      <TableCell align="right">
                        {data.aging_buckets.over_90.count}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CustomerAgingPage;
