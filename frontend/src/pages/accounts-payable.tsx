// frontend/src/pages/accounts-payable.tsx
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  LinearProgress
} from '@mui/material';
import { 
  Receipt,
  Payment,
  Visibility,
  TrendingUp,
  TrendingDown,
  AccessTime
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';
import api from '../lib/api';
import { useRouter } from 'next/router';

interface VendorBill {
  id: number;
  voucher_number: string;
  vendor_name: string;
  date: string;
  due_date: string;
  total_amount: number;
  paid_amount: number;
  status: string;
}

const AccountsPayablePage: React.FC = () => {
  const router = useRouter();
  const [bills, setBills] = useState<VendorBill[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    totalPayable: 0,
    overdue: 0,
    dueThisWeek: 0,
    dueThisMonth: 0
  });

  useEffect(() => {
    fetchAccountsPayable();
  }, []);

  const fetchAccountsPayable = async () => {
    try {
      setLoading(true);
      // Fetch purchase vouchers (vendor bills)
      const response = await api.get('/vouchers/purchase-vouchers?page=1&per_page=50');
      const purchaseVouchers = response.data.vouchers || response.data || [];
      
      // Transform to accounts payable format
      const billsData: VendorBill[] = purchaseVouchers.map((v: any) => ({
        id: v.id,
        voucher_number: v.voucher_number,
        vendor_name: v.vendor?.name || 'Unknown Vendor',
        date: v.voucher_date || v.date,
        due_date: v.due_date,
        total_amount: parseFloat(v.total_amount || 0),
        paid_amount: parseFloat(v.paid_amount || 0),
        status: v.payment_status || 'unpaid'
      }));

      setBills(billsData);

      // Calculate summary
      const now = new Date();
      const oneWeekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      const oneMonthFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

      const totalPayable = billsData.reduce((sum, bill) => 
        sum + (bill.total_amount - bill.paid_amount), 0);
      
      const overdue = billsData.filter(bill => {
        if (!bill.due_date || bill.status === 'paid') return false;
        return new Date(bill.due_date) < now;
      }).reduce((sum, bill) => sum + (bill.total_amount - bill.paid_amount), 0);

      const dueThisWeek = billsData.filter(bill => {
        if (!bill.due_date || bill.status === 'paid') return false;
        const dueDate = new Date(bill.due_date);
        return dueDate >= now && dueDate <= oneWeekFromNow;
      }).reduce((sum, bill) => sum + (bill.total_amount - bill.paid_amount), 0);

      const dueThisMonth = billsData.filter(bill => {
        if (!bill.due_date || bill.status === 'paid') return false;
        const dueDate = new Date(bill.due_date);
        return dueDate >= now && dueDate <= oneMonthFromNow;
      }).reduce((sum, bill) => sum + (bill.total_amount - bill.paid_amount), 0);

      setSummary({ totalPayable, overdue, dueThisWeek, dueThisMonth });
    } catch (error) {
      console.error('Error fetching accounts payable:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN');
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'paid':
        return 'success';
      case 'partial':
        return 'warning';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleViewBill = (billId: number) => {
    router.push(`/vouchers/purchase-vouchers/${billId}`);
  };

  const handleMakePayment = (billId: number) => {
    router.push(`/vouchers/payment-voucher?bill_id=${billId}`);
  };

  if (loading) {
    return (
      <DashboardLayout
        title="Accounts Payable"
        subtitle="Manage vendor bills and payables"
      >
        <LinearProgress />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Accounts Payable"
      subtitle="Track and manage vendor bills and payments"
    >
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Receipt color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Payable
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {formatCurrency(summary.totalPayable)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {bills.filter(b => b.status !== 'paid').length} unpaid bills
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingDown color="error" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Overdue
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="error">
                {formatCurrency(summary.overdue)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Requires immediate attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AccessTime color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Due This Week
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {formatCurrency(summary.dueThisWeek)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Next 7 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="info" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Due This Month
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="info.main">
                {formatCurrency(summary.dueThisMonth)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Next 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Bills Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Vendor Bills
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => router.push('/vouchers/purchase-vouchers/new')}
                >
                  Record New Bill
                </Button>
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Bill No.</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Bill Date</TableCell>
                      <TableCell>Due Date</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell align="right">Paid</TableCell>
                      <TableCell align="right">Balance</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bills.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} align="center">
                          <Typography color="textSecondary" py={4}>
                            No vendor bills found. Create a purchase voucher to track payables.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      bills.map((bill) => (
                        <TableRow key={bill.id} hover>
                          <TableCell>{bill.voucher_number}</TableCell>
                          <TableCell>{bill.vendor_name}</TableCell>
                          <TableCell>{formatDate(bill.date)}</TableCell>
                          <TableCell>{formatDate(bill.due_date)}</TableCell>
                          <TableCell align="right">{formatCurrency(bill.total_amount)}</TableCell>
                          <TableCell align="right">{formatCurrency(bill.paid_amount)}</TableCell>
                          <TableCell align="right" fontWeight="bold">
                            {formatCurrency(bill.total_amount - bill.paid_amount)}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={bill.status} 
                              color={getStatusColor(bill.status)} 
                              size="small" 
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Tooltip title="View Bill">
                              <IconButton size="small" onClick={() => handleViewBill(bill.id)}>
                                <Visibility fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            {bill.status !== 'paid' && (
                              <Tooltip title="Make Payment">
                                <IconButton 
                                  size="small" 
                                  color="primary"
                                  onClick={() => handleMakePayment(bill.id)}
                                >
                                  <Payment fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default AccountsPayablePage;