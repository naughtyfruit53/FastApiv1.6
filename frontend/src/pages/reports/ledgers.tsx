// pages/reports/ledgers.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  IconButton
} from '@mui/material';
import { 
  AccountBalance, 
  Download, 
  Print,
  Search,
  DateRange,
  FilterList
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const LedgerReportsPage: React.FC = () => {
  const [accountFilter, setAccountFilter] = React.useState('all');
  const [dateRange, setDateRange] = React.useState('this-month');

  const ledgerEntries = [
    { 
      date: '2024-01-15',
      account: 'Cash in Hand',
      particulars: 'Sales Revenue',
      voucherNo: 'SV-001',
      debit: 15000,
      credit: 0,
      balance: 45000
    },
    { 
      date: '2024-01-16',
      account: 'Accounts Payable',
      particulars: 'Vendor Payment',
      voucherNo: 'PV-002',
      debit: 0,
      credit: 8000,
      balance: 12000
    },
    { 
      date: '2024-01-17',
      account: 'Sales Account',
      particulars: 'Product Sales',
      voucherNo: 'SV-003',
      debit: 0,
      credit: 25000,
      balance: 125000
    },
    { 
      date: '2024-01-18',
      account: 'Office Expenses',
      particulars: 'Office Supplies',
      voucherNo: 'EX-004',
      debit: 3500,
      credit: 0,
      balance: 18500
    },
  ];

  const accounts = [
    'All Accounts',
    'Cash in Hand',
    'Bank Account',
    'Accounts Receivable',
    'Accounts Payable',
    'Sales Account',
    'Purchase Account',
    'Office Expenses'
  ];

  return (
    <DashboardLayout
      title="Ledger Reports"
      subtitle="View detailed account ledgers and transaction history"
      actions={
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant="outlined" 
            startIcon={<Download />}
          >
            Export
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<Print />}
          >
            Print
          </Button>
        </Box>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            General ledger shows all transactions for each account. Use filters to view specific accounts or date ranges.
          </Alert>
        </Grid>
        
        {/* Filters */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Filters & Search
              </Typography>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    select
                    label="Account"
                    value={accountFilter}
                    onChange={(e) => setAccountFilter(e.target.value)}
                  >
                    {accounts.map((account, index) => (
                      <MenuItem key={index} value={account.toLowerCase().replace(' ', '-')}>
                        {account}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    select
                    label="Date Range"
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                  >
                    <MenuItem value="today">Today</MenuItem>
                    <MenuItem value="this-week">This Week</MenuItem>
                    <MenuItem value="this-month">This Month</MenuItem>
                    <MenuItem value="this-quarter">This Quarter</MenuItem>
                    <MenuItem value="this-year">This Year</MenuItem>
                    <MenuItem value="custom">Custom Range</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="From Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="To Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Button variant="contained" startIcon={<Search />}>
                  Apply Filters
                </Button>
                <Button variant="outlined" startIcon={<FilterList />}>
                  Clear All
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Ledger Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Summary
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Total Debit
                </Typography>
                <Typography variant="h5" color="error.main">
                  $18,500.00
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Total Credit
                </Typography>
                <Typography variant="h5" color="success.main">
                  $33,000.00
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary">
                  Net Balance
                </Typography>
                <Typography variant="h5" color="primary.main">
                  $14,500.00
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Links
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Button 
                    fullWidth 
                    variant="outlined" 
                    href="/reports/trial-balance"
                  >
                    Trial Balance
                  </Button>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Button 
                    fullWidth 
                    variant="outlined" 
                    href="/reports/balance-sheet"
                  >
                    Balance Sheet
                  </Button>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Button 
                    fullWidth 
                    variant="outlined" 
                    href="/reports/profit-loss"
                  >
                    P&L Statement
                  </Button>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Button 
                    fullWidth 
                    variant="outlined" 
                    href="/reports/cash-flow"
                  >
                    Cash Flow
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Ledger Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                General Ledger Entries
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Account</TableCell>
                      <TableCell>Particulars</TableCell>
                      <TableCell>Voucher No.</TableCell>
                      <TableCell align="right">Debit</TableCell>
                      <TableCell align="right">Credit</TableCell>
                      <TableCell align="right">Balance</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ledgerEntries.map((entry, index) => (
                      <TableRow key={index}>
                        <TableCell>{entry.date}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <AccountBalance sx={{ mr: 1, fontSize: 16 }} />
                            {entry.account}
                          </Box>
                        </TableCell>
                        <TableCell>{entry.particulars}</TableCell>
                        <TableCell>{entry.voucherNo}</TableCell>
                        <TableCell align="right">
                          {entry.debit > 0 ? `$${entry.debit.toLocaleString()}` : '-'}
                        </TableCell>
                        <TableCell align="right">
                          {entry.credit > 0 ? `$${entry.credit.toLocaleString()}` : '-'}
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            ${entry.balance.toLocaleString()}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
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

export default LedgerReportsPage;