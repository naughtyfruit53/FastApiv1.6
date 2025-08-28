// frontend/src/pages/general-ledger.tsx
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
  Pagination,
  Alert,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Edit,
  Visibility,
  FilterList,
  Download,
  Refresh
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import axios from 'axios';

interface Account {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
}

interface GeneralLedgerEntry {
  id: number;
  transaction_date: string;
  transaction_number: string;
  reference_type?: string;
  reference_number?: string;
  debit_amount: number;
  credit_amount: number;
  running_balance: number;
  description?: string;
  narration?: string;
  is_reconciled: boolean;
  created_at: string;
}

interface CreateEntryData {
  account_id: number;
  transaction_date: string;
  transaction_number: string;
  reference_type?: string;
  reference_number?: string;
  debit_amount: number;
  credit_amount: number;
  description?: string;
  narration?: string;
  cost_center_id?: number;
}

const GeneralLedger: React.FC = () => {
  const [entries, setEntries] = useState<GeneralLedgerEntry[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null);
  const [dateFilter, setDateFilter] = useState({ start: null as Date | null, end: null as Date | null });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Create entry form state
  const [createData, setCreateData] = useState<CreateEntryData>({
    account_id: 0,
    transaction_date: new Date().toISOString().split('T')[0],
    transaction_number: '',
    debit_amount: 0,
    credit_amount: 0,
    description: '',
    narration: ''
  });

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        skip: ((page - 1) * 50).toString(),
        limit: '50'
      });
      
      if (selectedAccount) params.append('account_id', selectedAccount.toString());
      if (dateFilter.start) params.append('start_date', dateFilter.start.toISOString().split('T')[0]);
      if (dateFilter.end) params.append('end_date', dateFilter.end.toISOString().split('T')[0]);

      const response = await axios.get(`/api/v1/erp/general-ledger?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setEntries(response.data);
      setTotalPages(Math.ceil(response.data.length / 50)); // Simplified pagination
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch entries');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/erp/chart-of-accounts', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAccounts(response.data);
    } catch (err: any) {
      console.error('Failed to fetch accounts:', err);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  useEffect(() => {
    fetchEntries();
  }, [page, selectedAccount, dateFilter]);

  const handleCreateEntry = async () => {
    try {
      if (createData.debit_amount === 0 && createData.credit_amount === 0) {
        setError('Either debit or credit amount must be greater than 0');
        return;
      }

      const token = localStorage.getItem('token');
      await axios.post('/api/v1/erp/general-ledger', createData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setCreateDialogOpen(false);
      setCreateData({
        account_id: 0,
        transaction_date: new Date().toISOString().split('T')[0],
        transaction_number: '',
        debit_amount: 0,
        credit_amount: 0,
        description: '',
        narration: ''
      });
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create entry');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  // Calculate totals
  const totalDebits = entries.reduce((sum, entry) => sum + entry.debit_amount, 0);
  const totalCredits = entries.reduce((sum, entry) => sum + entry.credit_amount, 0);

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            General Ledger
          </Typography>
          <Box>
            <Button
              startIcon={<Add />}
              variant="contained"
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              New Entry
            </Button>
            <IconButton onClick={fetchEntries} color="primary">
              <Refresh />
            </IconButton>
            <Button startIcon={<Download />} variant="outlined" sx={{ ml: 1 }}>
              Export
            </Button>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Debits
                </Typography>
                <Typography variant="h6" color="error.main">
                  {formatCurrency(totalDebits)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Credits
                </Typography>
                <Typography variant="h6" color="success.main">
                  {formatCurrency(totalCredits)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Difference
                </Typography>
                <Typography variant="h6" color={totalDebits === totalCredits ? 'success.main' : 'warning.main'}>
                  {formatCurrency(Math.abs(totalDebits - totalCredits))}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Account</InputLabel>
                <Select
                  value={selectedAccount || ''}
                  onChange={(e) => setSelectedAccount(e.target.value as number || null)}
                  label="Account"
                >
                  <MenuItem value="">All Accounts</MenuItem>
                  {accounts.map((account) => (
                    <MenuItem key={account.id} value={account.id}>
                      {account.account_code} - {account.account_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <DatePicker
                label="Start Date"
                value={dateFilter.start}
                onChange={(date) => setDateFilter(prev => ({ ...prev, start: date }))}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <DatePicker
                label="End Date"
                value={dateFilter.end}
                onChange={(date) => setDateFilter(prev => ({ ...prev, end: date }))}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setSelectedAccount(null);
                  setDateFilter({ start: null, end: null });
                }}
                fullWidth
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Entries Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Transaction #</TableCell>
                  <TableCell>Reference</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Debit</TableCell>
                  <TableCell align="right">Credit</TableCell>
                  <TableCell align="right">Balance</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : entries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      No entries found
                    </TableCell>
                  </TableRow>
                ) : (
                  entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell>{formatDate(entry.transaction_date)}</TableCell>
                      <TableCell>{entry.transaction_number}</TableCell>
                      <TableCell>
                        {entry.reference_type && (
                          <Chip 
                            label={`${entry.reference_type}${entry.reference_number ? `: ${entry.reference_number}` : ''}`}
                            size="small"
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{entry.description}</Typography>
                          {entry.narration && (
                            <Typography variant="caption" color="textSecondary">
                              {entry.narration}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {entry.debit_amount > 0 ? formatCurrency(entry.debit_amount) : '-'}
                      </TableCell>
                      <TableCell align="right">
                        {entry.credit_amount > 0 ? formatCurrency(entry.credit_amount) : '-'}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(entry.running_balance)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={entry.is_reconciled ? 'Reconciled' : 'Pending'}
                          color={entry.is_reconciled ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          {/* Pagination */}
          <Box display="flex" justifyContent="center" p={2}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(event, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </Paper>

        {/* Create Entry Dialog */}
        <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Create General Ledger Entry</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Account</InputLabel>
                  <Select
                    value={createData.account_id}
                    onChange={(e) => setCreateData(prev => ({ ...prev, account_id: e.target.value as number }))}
                    label="Account"
                  >
                    {accounts.map((account) => (
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
                  label="Transaction Number"
                  value={createData.transaction_number}
                  onChange={(e) => setCreateData(prev => ({ ...prev, transaction_number: e.target.value }))}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Transaction Date"
                  value={createData.transaction_date}
                  onChange={(e) => setCreateData(prev => ({ ...prev, transaction_date: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Reference Number"
                  value={createData.reference_number || ''}
                  onChange={(e) => setCreateData(prev => ({ ...prev, reference_number: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Debit Amount"
                  value={createData.debit_amount}
                  onChange={(e) => setCreateData(prev => ({ ...prev, debit_amount: parseFloat(e.target.value) || 0 }))}
                  inputProps={{ min: 0, step: 0.01 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Credit Amount"
                  value={createData.credit_amount}
                  onChange={(e) => setCreateData(prev => ({ ...prev, credit_amount: parseFloat(e.target.value) || 0 }))}
                  inputProps={{ min: 0, step: 0.01 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={createData.description || ''}
                  onChange={(e) => setCreateData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Narration"
                  value={createData.narration || ''}
                  onChange={(e) => setCreateData(prev => ({ ...prev, narration: e.target.value }))}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleCreateEntry} variant="contained">Create Entry</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default GeneralLedger;