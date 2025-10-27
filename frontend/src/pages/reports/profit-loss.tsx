// frontend/src/pages/reports/profit-loss.tsx
import React, { useState, useEffect } from 'react';
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
  Grid,
  TextField,
  MenuItem,
  IconButton,
  Paper
} from '@mui/material';
import { Refresh, Download, Print } from '@mui/icons-material';
import axios from 'axios';
import { formatCurrency } from '../../utils/currencyUtils';

interface ProfitLossData {
  period: { start_date: string; end_date: string };
  trend_data: Array<{
    period: string;
    income: number;
    expenses: number;
    net_profit: number;
    profit_margin: number;
  }>;
  summary: {
    total_income: number;
    total_expenses: number;
    total_net_profit: number;
    average_monthly_profit: number;
    overall_profit_margin: number;
  };
}

const ProfitLossPage: React.FC = () => {
  const [data, setData] = useState<ProfitLossData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [months, setMonths] = useState(12);

  const fetchProfitLoss = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/finance/analytics/profit-loss-trend', {
        params: { months },
        headers: { Authorization: `Bearer ${token}` }
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch profit & loss data');
      // Demo data
      setData({
        period: { start_date: '2024-01-01', end_date: '2024-12-31' },
        trend_data: [
          { period: '2024-01', income: 500000, expenses: 350000, net_profit: 150000, profit_margin: 30 },
          { period: '2024-02', income: 550000, expenses: 380000, net_profit: 170000, profit_margin: 30.9 },
          { period: '2024-03', income: 600000, expenses: 400000, net_profit: 200000, profit_margin: 33.3 },
          { period: '2024-04', income: 580000, expenses: 390000, net_profit: 190000, profit_margin: 32.8 },
          { period: '2024-05', income: 620000, expenses: 410000, net_profit: 210000, profit_margin: 33.9 },
          { period: '2024-06', income: 650000, expenses: 430000, net_profit: 220000, profit_margin: 33.8 }
        ],
        summary: {
          total_income: 3500000,
          total_expenses: 2360000,
          total_net_profit: 1140000,
          average_monthly_profit: 190000,
          overall_profit_margin: 32.6
        }
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfitLoss();
  }, [months]);

  const handleExport = () => {
    alert('Export functionality to be implemented');
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Profit & Loss Statement
        </Typography>
        <Box>
          <TextField
            select
            label="Period"
            value={months}
            onChange={(e) => setMonths(parseInt(e.target.value))}
            size="small"
            sx={{ mr: 1, minWidth: 120 }}
          >
            <MenuItem value={3}>3 Months</MenuItem>
            <MenuItem value={6}>6 Months</MenuItem>
            <MenuItem value={12}>12 Months</MenuItem>
          </TextField>
          <IconButton onClick={fetchProfitLoss} color="primary">
            <Refresh />
          </IconButton>
          <IconButton onClick={handlePrint} color="primary">
            <Print />
          </IconButton>
          <Button startIcon={<Download />} variant="outlined" onClick={handleExport}>
            Export
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error} (Showing demo data)
        </Alert>
      )}

      {data && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Income
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {formatCurrency(data.summary.total_income)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Expenses
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {formatCurrency(data.summary.total_expenses)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Net Profit
                  </Typography>
                  <Typography variant="h5" color="primary.main">
                    {formatCurrency(data.summary.total_net_profit)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Profit Margin
                  </Typography>
                  <Typography variant="h5" color="primary.main">
                    {data.summary.overall_profit_margin.toFixed(2)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Period: {data.period.start_date} to {data.period.end_date}
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Period</strong></TableCell>
                      <TableCell align="right"><strong>Income</strong></TableCell>
                      <TableCell align="right"><strong>Expenses</strong></TableCell>
                      <TableCell align="right"><strong>Net Profit</strong></TableCell>
                      <TableCell align="right"><strong>Margin %</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.trend_data.map((row) => (
                      <TableRow key={row.period}>
                        <TableCell>{row.period}</TableCell>
                        <TableCell align="right" sx={{ color: 'success.main' }}>
                          {formatCurrency(row.income)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: 'error.main' }}>
                          {formatCurrency(row.expenses)}
                        </TableCell>
                        <TableCell align="right" sx={{ color: row.net_profit >= 0 ? 'primary.main' : 'error.main' }}>
                          {formatCurrency(row.net_profit)}
                        </TableCell>
                        <TableCell align="right">
                          {row.profit_margin.toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow sx={{ backgroundColor: 'grey.100' }}>
                      <TableCell><strong>Total</strong></TableCell>
                      <TableCell align="right" sx={{ color: 'success.main' }}>
                        <strong>{formatCurrency(data.summary.total_income)}</strong>
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'error.main' }}>
                        <strong>{formatCurrency(data.summary.total_expenses)}</strong>
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'primary.main' }}>
                        <strong>{formatCurrency(data.summary.total_net_profit)}</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>{data.summary.overall_profit_margin.toFixed(2)}%</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
};

export default ProfitLossPage;
