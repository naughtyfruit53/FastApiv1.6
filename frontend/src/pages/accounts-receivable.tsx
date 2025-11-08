// frontend/src/pages/accounts-receivable.tsx
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  ReceiptLong,
  Add,
  Visibility,
  Payment,
  Refresh
} from '@mui/icons-material';
import axios from 'axios';
import { formatCurrency } from '../utils/currencyUtils';

import { ProtectedPage } from '../components/ProtectedPage';
interface Receivable {
  id: number;
  invoice_number: string;
  customer_name: string;
  invoice_date: string;
  due_date: string;
  total_amount: number;
  outstanding_amount: number;
  payment_status: string;
}

const AccountsReceivablePage: React.FC = () => {
  const [receivables, setReceivables] = useState<Receivable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReceivables = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/erp/accounts-receivable', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReceivables(response.data || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch receivables');
      // Set demo data for display
      setReceivables([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReceivables();
  }, []);

  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning" => {
    switch (status) {
      case 'paid': return 'success';
      case 'partial': return 'warning';
      case 'pending': return 'error';
      default: return 'default';
    }
  };

  const totalOutstanding = receivables.reduce((sum, r) => sum + r.outstanding_amount, 0);
  const totalAmount = receivables.reduce((sum, r) => sum + r.total_amount, 0);

  if (loading) {
    return (
      <ProtectedPage moduleKey="finance" action="read">
      rotectedPage moduleKey="finance" action="read">
        ox display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
      </ProtectedPage>
    );
  }
  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Accounts Receivable
        </Typography>
        <Box>
          <Button startIcon={<Add />} variant="contained" sx={{ mr: 1 }}>
            New Invoice
          </Button>
          <IconButton onClick={fetchReceivables} color="primary">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Receivables
              </Typography>
              <Typography variant="h5" color="primary.main">
                {formatCurrency(totalAmount)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Outstanding Amount
              </Typography>
              <Typography variant="h5" color="error.main">
                {formatCurrency(totalOutstanding)}
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
                {receivables.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Receivables Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Customer Invoices
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Invoice Number</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Invoice Date</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell align="right">Total Amount</TableCell>
                  <TableCell align="right">Outstanding</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {receivables.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 4 }}>
                        <ReceiptLong sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography color="textSecondary">
                          No receivables found. Create your first invoice to get started.
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  receivables.map((receivable) => (
                    <TableRow key={receivable.id}>
                      <TableCell>{receivable.invoice_number}</TableCell>
                      <TableCell>{receivable.customer_name}</TableCell>
                      <TableCell>{new Date(receivable.invoice_date).toLocaleDateString()}</TableCell>
                      <TableCell>{new Date(receivable.due_date).toLocaleDateString()}</TableCell>
                      <TableCell align="right">{formatCurrency(receivable.total_amount)}</TableCell>
                      <TableCell align="right">{formatCurrency(receivable.outstanding_amount)}</TableCell>
                      <TableCell>
                        <Chip 
                          label={receivable.payment_status.toUpperCase()}
                          color={getStatusColor(receivable.payment_status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small">
                          <Visibility fontSize="small" />
                        </IconButton>
                        <IconButton size="small" color="primary">
                          <Payment fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
    </ProtectedPage>
  );
};
export default AccountsReceivablePage;