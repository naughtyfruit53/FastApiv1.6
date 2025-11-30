// frontend/src/pages/vendor-aging.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
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
} from "@mui/material";
import Grid from '@mui/material/Grid';
import { Refresh, Download, Print } from "@mui/icons-material";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../services/api/client";
import { formatCurrency } from "../utils/currencyUtils";

import { ProtectedPage } from '../components/ProtectedPage';
ChartJS.register(ArcElement, Tooltip, Legend);

interface AgingBucket {
  amount: number;
  count: number;
  vendors: number;
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
    total_vendors: number;
    total_invoices: number;
    total_outstanding: number;
  };
}

const VendorAgingPage: React.FC = () => {
  const [data, setData] = useState<AgingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgingData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/finance/analytics/vendor-aging");
      setData(response.data);
      setError(null);
    } catch (err: any) {
      let errorMessage = "Failed to fetch vendor aging data";
      if (err.response?.data) {
        const data = err.response.data;
        if (typeof data === 'string') {
          errorMessage = data;
        } else if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (typeof data.detail === 'object' && data.detail !== null) {
            errorMessage = data.detail.message || data.detail.error || JSON.stringify(data.detail);
          }
        } else if (data.message) {
          errorMessage = data.message;
        } else if (data.error) {
          errorMessage = data.error;
        } else if (typeof data === 'object' && data !== null) {
          errorMessage = JSON.stringify(data);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgingData();
  }, []);

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
    <ProtectedPage moduleKey="finance" action="read">
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Vendor Aging Report
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
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Outstanding
              </Typography>
              <Typography variant="h5" color="error.main">
                {formatCurrency(data.summary.total_outstanding)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Vendors
              </Typography>
              <Typography variant="h5">
                {data.summary.total_vendors}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid xs={12} md={4}>
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
        <Grid xs={12} md={6}>
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
        <Grid xs={12} md={6}>
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
    </ProtectedPage>
  );
};
export default VendorAgingPage;
