// frontend/src/pages/financial-kpis.tsx
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
import { Refresh, Download, Print, TrendingUp, TrendingDown } from "@mui/icons-material";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

interface KPIData {
  period: {
    start_date: string;
    end_date: string;
  };
  kpis: Array<{
    kpi_code: string;
    kpi_name: string;
    kpi_category: string;
    value: number;
    target: number | null;
    variance: number | null;
    period_end: string;
    status: string;
  }>;
  financial_ratios: {
    current_ratio: number;
    debt_to_equity: number;
    working_capital: number;
    total_assets: number;
    total_liabilities: number;
    total_equity: number;
  };
  summary: {
    total_kpis: number;
    on_track_count: number;
    needs_attention_count: number;
  };
}

const FinancialKPIsPage: React.FC = () => {
  const [data, setData] = useState<KPIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodMonths, setPeriodMonths] = useState(3);

  const fetchKPIData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/financial-kpis", {
        params: { period_months: periodMonths },
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch KPI data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKPIData();
  }, [periodMonths]);

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
          <Button color="inherit" size="small" onClick={fetchKPIData}>
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

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Financial KPIs Dashboard
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            type="number"
            label="Period (Months)"
            value={periodMonths}
            onChange={(e) => setPeriodMonths(parseInt(e.target.value))}
            size="small"
            sx={{ width: 150 }}
          />
          <IconButton onClick={fetchKPIData} color="primary">
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

      {/* Financial Ratios */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Current Ratio
              </Typography>
              <Typography variant="h5" color="primary.main">
                {data.financial_ratios.current_ratio.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Debt to Equity
              </Typography>
              <Typography variant="h5" color="warning.main">
                {data.financial_ratios.debt_to_equity.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Working Capital
              </Typography>
              <Typography variant="h5" color="success.main">
                {formatCurrency(data.financial_ratios.working_capital)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Assets
              </Typography>
              <Typography variant="h5" color="info.main">
                {formatCurrency(data.financial_ratios.total_assets)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* KPI Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total KPIs
              </Typography>
              <Typography variant="h5">{data.summary.total_kpis}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                On Track
              </Typography>
              <Typography variant="h5" color="success.main">
                {data.summary.on_track_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Needs Attention
              </Typography>
              <Typography variant="h5" color="error.main">
                {data.summary.needs_attention_count}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* KPI Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            KPI Performance
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
                  <TableCell>Period End</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.kpis.map((kpi, index) => (
                  <TableRow key={index}>
                    <TableCell>{kpi.kpi_name}</TableCell>
                    <TableCell>
                      <Chip label={kpi.kpi_category} size="small" />
                    </TableCell>
                    <TableCell align="right">{kpi.value.toFixed(2)}</TableCell>
                    <TableCell align="right">
                      {kpi.target ? kpi.target.toFixed(2) : "N/A"}
                    </TableCell>
                    <TableCell align="right">
                      {kpi.variance !== null ? (
                        <Box display="flex" alignItems="center" justifyContent="flex-end">
                          {kpi.variance >= 0 ? (
                            <TrendingUp color="success" fontSize="small" />
                          ) : (
                            <TrendingDown color="error" fontSize="small" />
                          )}
                          <Typography
                            color={kpi.variance >= 0 ? "success.main" : "error.main"}
                            sx={{ ml: 0.5 }}
                          >
                            {Math.abs(kpi.variance).toFixed(2)}%
                          </Typography>
                        </Box>
                      ) : (
                        "N/A"
                      )}
                    </TableCell>
                    <TableCell>{new Date(kpi.period_end).toLocaleDateString()}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={kpi.status.replace("_", " ").toUpperCase()}
                        color={kpi.status === "on_track" ? "success" : "warning"}
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
  );
};

export default FinancialKPIsPage;
