// frontend/src/pages/reports/cash-flow.tsx
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
  TextField,
  MenuItem,
  IconButton,
  Paper,
  Chip
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { Refresh, Download, Print, TrendingUp, TrendingDown } from '@mui/icons-material';
import api from "../../services/api/client";
import { formatCurrency } from '../../utils/currencyUtils';
import { ProtectedPage } from '../../components/ProtectedPage';

interface CashFlowData {
  period: { start_date: string; end_date: string };
  cash_flow: {
    inflow: number;
    outflow: number;
    net_flow: number;
  };
}

const CashFlowPage: React.FC = () => {
  const [data, setData] = useState<CashFlowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodDays, setPeriodDays] = useState(30);

  const fetchCashFlow = async () => {
    try {
      setLoading(true);
      const response = await api.get('/finance/analytics/dashboard', {
        params: { period_days: periodDays }
      });
      setData({
        period: response.data.period,
        cash_flow: response.data.cash_flow
      });
      setError(null);
    } catch (err: any) {
      let errorMessage = "Failed to fetch cash flow data";
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
      // Demo data
      setData({
        period: { start_date: '2024-12-01', end_date: '2024-12-31' },
        cash_flow: {
          inflow: 850000,
          outflow: 620000,
          net_flow: 230000
        }
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCashFlow();
  }, [periodDays]);

  const handleExport = () => {
    alert('Export functionality to be implemented');
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <ProtectedPage moduleKey="reports" action="read">
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage moduleKey="reports" action="read">
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Cash Flow Statement
        </Typography>
        <Box>
          <TextField
            select
            label="Period"
            value={periodDays}
            onChange={(e) => setPeriodDays(parseInt(e.target.value))}
            size="small"
            sx={{ mr: 1, minWidth: 120 }}
          >
            <MenuItem value={7}>7 Days</MenuItem>
            <MenuItem value={30}>30 Days</MenuItem>
            <MenuItem value={90}>90 Days</MenuItem>
            <MenuItem value={365}>1 Year</MenuItem>
          </TextField>
          <IconButton onClick={fetchCashFlow} color="primary">
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
            <Grid xs={12} sm={6} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Cash Inflow
                      </Typography>
                      <Typography variant="h5" color="success.main">
                        {formatCurrency(data.cash_flow.inflow)}
                      </Typography>
                    </Box>
                    <TrendingUp sx={{ fontSize: 48, color: 'success.main', opacity: 0.3 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid xs={12} sm={6} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Cash Outflow
                      </Typography>
                      <Typography variant="h5" color="error.main">
                        {formatCurrency(data.cash_flow.outflow)}
                      </Typography>
                    </Box>
                    <TrendingDown sx={{ fontSize: 48, color: 'error.main', opacity: 0.3 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid xs={12} sm={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>
                        Net Cash Flow
                      </Typography>
                      <Typography 
                        variant="h5" 
                        color={data.cash_flow.net_flow >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatCurrency(data.cash_flow.net_flow)}
                      </Typography>
                    </Box>
                    <Chip 
                      label={data.cash_flow.net_flow >= 0 ? 'Positive' : 'Negative'}
                      color={data.cash_flow.net_flow >= 0 ? 'success' : 'error'}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cash Flow Summary
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Period: {data.period.start_date} to {data.period.end_date}
              </Typography>
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Category</strong></TableCell>
                      <TableCell align="right"><strong>Amount</strong></TableCell>
                      <TableCell align="right"><strong>Percentage</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                          Cash Inflow
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'success.main' }}>
                        {formatCurrency(data.cash_flow.inflow)}
                      </TableCell>
                      <TableCell align="right">
                        100%
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <TrendingDown sx={{ mr: 1, color: 'error.main' }} />
                          Cash Outflow
                        </Box>
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'error.main' }}>
                        {formatCurrency(data.cash_flow.outflow)}
                      </TableCell>
                      <TableCell align="right">
                        {((data.cash_flow.outflow / data.cash_flow.inflow) * 100).toFixed(2)}%
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ backgroundColor: 'grey.100' }}>
                      <TableCell>
                        <strong>Net Cash Flow</strong>
                      </TableCell>
                      <TableCell 
                        align="right" 
                        sx={{ color: data.cash_flow.net_flow >= 0 ? 'success.main' : 'error.main' }}
                      >
                        <strong>{formatCurrency(data.cash_flow.net_flow)}</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>
                          {((data.cash_flow.net_flow / data.cash_flow.inflow) * 100).toFixed(2)}%
                        </strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Additional Info */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                {data.cash_flow.net_flow >= 0 
                  ? 'Your business is generating positive cash flow, indicating healthy operations and the ability to meet financial obligations.'
                  : 'Your business is experiencing negative cash flow. Consider reviewing expenses and accelerating receivables collection.'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Cash flow efficiency: {((data.cash_flow.net_flow / data.cash_flow.inflow) * 100).toFixed(2)}% of inflow retained
              </Typography>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
    </ProtectedPage>
  );
};

export default CashFlowPage;
