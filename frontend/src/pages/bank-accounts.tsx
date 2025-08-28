// frontend/src/pages/bank-accounts.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  AccountBalance,
  Star,
  StarBorder,
  Refresh,
  Sync,
  Visibility
} from '@mui/icons-material';
import axios from 'axios';

interface ChartAccount {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
}

interface BankAccount {
  id: number;
  chart_account_id: number;
  bank_name: string;
  branch_name?: string;
  account_number: string;
  ifsc_code?: string;
  swift_code?: string;
  account_type: string;
  currency: string;
  opening_balance: number;
  current_balance: number;
  is_active: boolean;
  is_default: boolean;
  auto_reconcile: boolean;
  created_at: string;
  updated_at: string;
}

interface CreateBankAccountData {
  chart_account_id: number;
  bank_name: string;
  branch_name?: string;
  account_number: string;
  ifsc_code?: string;
  swift_code?: string;
  account_type: string;
  currency: string;
  opening_balance: number;
  is_default: boolean;
  auto_reconcile: boolean;
}

const BankAccounts: React.FC = () => {
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [chartAccounts, setChartAccounts] = useState<ChartAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<BankAccount | null>(null);

  // Create bank account form state
  const [createData, setCreateData] = useState<CreateBankAccountData>({
    chart_account_id: 0,
    bank_name: '',
    account_number: '',
    account_type: 'Savings',
    currency: 'INR',
    opening_balance: 0,
    is_default: false,
    auto_reconcile: false
  });

  const accountTypes = [
    'Savings',
    'Current',
    'Fixed Deposit',
    'Recurring Deposit',
    'NRI Account',
    'Overdraft',
    'Cash Credit'
  ];

  const currencies = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SAR'];

  const fetchBankAccounts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/erp/bank-accounts', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBankAccounts(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch bank accounts');
    } finally {
      setLoading(false);
    }
  };

  const fetchChartAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/erp/chart-of-accounts?account_type=bank', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setChartAccounts(response.data);
    } catch (err: any) {
      console.error('Failed to fetch chart accounts:', err);
    }
  };

  useEffect(() => {
    fetchChartAccounts();
    fetchBankAccounts();
  }, []);

  const handleCreateBankAccount = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/v1/erp/bank-accounts', createData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setCreateDialogOpen(false);
      setCreateData({
        chart_account_id: 0,
        bank_name: '',
        account_number: '',
        account_type: 'Savings',
        currency: 'INR',
        opening_balance: 0,
        is_default: false,
        auto_reconcile: false
      });
      fetchBankAccounts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create bank account');
    }
  };

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatAccountNumber = (accountNumber: string) => {
    // Mask account number for security (show only last 4 digits)
    if (accountNumber.length <= 4) return accountNumber;
    return '*'.repeat(accountNumber.length - 4) + accountNumber.slice(-4);
  };

  const handleSetDefault = async (accountId: number) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`/api/v1/erp/bank-accounts/${accountId}`, {
        is_default: true
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchBankAccounts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to set default account');
    }
  };

  // Calculate totals
  const totalBalance = bankAccounts
    .filter(acc => acc.is_active)
    .reduce((sum, acc) => sum + acc.current_balance, 0);
  
  const activeAccounts = bankAccounts.filter(acc => acc.is_active).length;
  const defaultAccount = bankAccounts.find(acc => acc.is_default);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Bank Accounts
        </Typography>
        <Box>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Account
          </Button>
          <IconButton onClick={fetchBankAccounts} color="primary">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountBalance color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Balance
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(totalBalance)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountBalance color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Accounts
                  </Typography>
                  <Typography variant="h6">
                    {activeAccounts}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Star color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Default Account
                  </Typography>
                  <Typography variant="h6">
                    {defaultAccount?.bank_name || 'None'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Bank Accounts Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Bank Name</TableCell>
                <TableCell>Account Number</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Branch</TableCell>
                <TableCell>IFSC</TableCell>
                <TableCell align="right">Current Balance</TableCell>
                <TableCell>Currency</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Auto Reconcile</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={11} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : bankAccounts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={11} align="center">
                    No bank accounts found
                  </TableCell>
                </TableRow>
              ) : (
                bankAccounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {account.bank_name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Created: {new Date(account.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {formatAccountNumber(account.account_number)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={account.account_type} size="small" />
                    </TableCell>
                    <TableCell>{account.branch_name || '-'}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {account.ifsc_code || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        variant="body2" 
                        color={account.current_balance >= 0 ? 'success.main' : 'error.main'}
                        fontWeight="medium"
                      >
                        {formatCurrency(account.current_balance, account.currency)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={account.currency} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={account.is_active ? 'Active' : 'Inactive'}
                        color={account.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title={account.is_default ? 'Default Account' : 'Set as Default'}>
                        <IconButton
                          size="small"
                          onClick={() => !account.is_default && handleSetDefault(account.id)}
                          disabled={account.is_default}
                        >
                          {account.is_default ? <Star color="warning" /> : <StarBorder />}
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={<Sync />}
                        label={account.auto_reconcile ? 'Yes' : 'No'}
                        color={account.auto_reconcile ? 'primary' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton 
                          size="small"
                          onClick={() => {
                            setSelectedAccount(account);
                            setEditDialogOpen(true);
                          }}
                        >
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" color="error">
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create Bank Account Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Bank Account</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Chart Account</InputLabel>
                <Select
                  value={createData.chart_account_id}
                  onChange={(e) => setCreateData(prev => ({ ...prev, chart_account_id: e.target.value as number }))}
                  label="Chart Account"
                >
                  {chartAccounts.map((account) => (
                    <MenuItem key={account.id} value={account.id}>
                      {account.account_code} - {account.account_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Bank Name"
                value={createData.bank_name}
                onChange={(e) => setCreateData(prev => ({ ...prev, bank_name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Account Number"
                value={createData.account_number}
                onChange={(e) => setCreateData(prev => ({ ...prev, account_number: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Account Type</InputLabel>
                <Select
                  value={createData.account_type}
                  onChange={(e) => setCreateData(prev => ({ ...prev, account_type: e.target.value }))}
                  label="Account Type"
                >
                  {accountTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Branch Name"
                value={createData.branch_name || ''}
                onChange={(e) => setCreateData(prev => ({ ...prev, branch_name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="IFSC Code"
                value={createData.ifsc_code || ''}
                onChange={(e) => setCreateData(prev => ({ ...prev, ifsc_code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="SWIFT Code"
                value={createData.swift_code || ''}
                onChange={(e) => setCreateData(prev => ({ ...prev, swift_code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={createData.currency}
                  onChange={(e) => setCreateData(prev => ({ ...prev, currency: e.target.value }))}
                  label="Currency"
                >
                  {currencies.map((currency) => (
                    <MenuItem key={currency} value={currency}>
                      {currency}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Opening Balance"
                value={createData.opening_balance}
                onChange={(e) => setCreateData(prev => ({ ...prev, opening_balance: parseFloat(e.target.value) || 0 }))}
                inputProps={{ step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={createData.is_default}
                    onChange={(e) => setCreateData(prev => ({ ...prev, is_default: e.target.checked }))}
                  />
                }
                label="Set as Default Account"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={createData.auto_reconcile}
                    onChange={(e) => setCreateData(prev => ({ ...prev, auto_reconcile: e.target.checked }))}
                  />
                }
                label="Enable Auto Reconciliation"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateBankAccount} variant="contained">Create Account</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BankAccounts;