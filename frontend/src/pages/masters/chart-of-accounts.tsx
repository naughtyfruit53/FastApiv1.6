import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  AccountBalance,
  AccountTree
} from '@mui/icons-material';
const ChartOfAccountsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<any>(null);
  const [formData, setFormData] = useState({
    account_code: '',
    account_name: '',
    account_type: 'asset',
    parent_account: '',
    description: '',
    is_active: true
  });
  // Mock data for demonstration
  const accounts = [
    {
      id: 1,
      account_code: '1000',
      account_name: 'Cash',
      account_type: 'asset',
      parent_account: null,
      balance: 50000,
      is_active: true
    },
    {
      id: 2,
      account_code: '1100',
      account_name: 'Accounts Receivable',
      account_type: 'asset',
      parent_account: null,
      balance: 25000,
      is_active: true
    },
    {
      id: 3,
      account_code: '2000',
      account_name: 'Accounts Payable',
      account_type: 'liability',
      parent_account: null,
      balance: 15000,
      is_active: true
    },
    {
      id: 4,
      account_code: '3000',
      account_name: 'Capital',
      account_type: 'equity',
      parent_account: null,
      balance: 100000,
      is_active: true
    },
    {
      id: 5,
      account_code: '4000',
      account_name: 'Sales Revenue',
      account_type: 'revenue',
      parent_account: null,
      balance: 75000,
      is_active: true
    },
    {
      id: 6,
      account_code: '5000',
      account_name: 'Cost of Goods Sold',
      account_type: 'expense',
      parent_account: null,
      balance: 30000,
      is_active: true
    }
  ];
  const accountTypes = [
    { value: 'asset', label: 'Asset', color: 'success' },
    { value: 'liability', label: 'Liability', color: 'error' },
    { value: 'equity', label: 'Equity', color: 'primary' },
    { value: 'revenue', label: 'Revenue', color: 'info' },
    { value: 'expense', label: 'Expense', color: 'warning' }
  ];
  const resetForm = () => {
    setFormData({
      account_code: '',
      account_name: '',
      account_type: 'asset',
      parent_account: '',
      description: '',
      is_active: true
    });
  };
  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };
  const handleEditClick = (account: any) => {
    setSelectedAccount(account);
    setFormData({
      account_code: account.account_code || '',
      account_name: account.account_name || '',
      account_type: account.account_type || 'asset',
      parent_account: account.parent_account || '',
      description: account.description || '',
      is_active: account.is_active
    });
    setEditDialog(true);
  };
  const handleSubmit = () => {
    if (selectedAccount) {
      // TODO: Implement update functionality
      console.log('Update account:', selectedAccount.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create account:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };
  const handleDeleteClick = (account: any) => {
    // TODO: Implement delete functionality
    console.log('Delete account:', account.id);
  };
  const filteredAccounts = accounts.filter((account: any) =>
    account.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.account_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.account_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const getAccountTypeColor = (type: string) => {
    const accountType = accountTypes.find(t => t.value === type);
    return accountType?.color || 'default';
  };
  const getTotalByType = (type: string) => {
    return accounts
      .filter(account => account.account_type === type)
      .reduce((sum, account) => sum + account.balance, 0);
  };
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Chart of Accounts
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Account
          </Button>
        </Box>
        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          The Chart of Accounts is the foundation of your financial system. It categorizes all 
          financial transactions and helps generate accurate financial reports.
        </Alert>
        {/* Account Type Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {accountTypes.map((type) => (
            <Grid item xs={12} sm={6} md={2.4} key={type.value}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="textSecondary" gutterBottom variant="body2">
                        {type.label}
                      </Typography>
                      <Typography variant="h6" component="h2">
                        ₹{getTotalByType(type.value).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {accounts.filter(acc => acc.account_type === type.value).length} accounts
                      </Typography>
                    </Box>
                    <AccountBalance sx={{ fontSize: 32, color: `${type.color}.main` }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search accounts by name, code, or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Account Code</TableCell>
                <TableCell>Account Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Balance</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAccounts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Box sx={{ py: 3 }}>
                      <AccountBalance sx={{ fontSize: 48, color: 'action.disabled', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary">
                        No accounts found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first account to start building your chart of accounts
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredAccounts.map((account: any) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {account.account_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <AccountTree sx={{ mr: 2, color: 'primary.main' }} />
                        <Typography variant="body1">
                          {account.account_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={account.account_type.charAt(0).toUpperCase() + account.account_type.slice(1)}
                        size="small"
                        color={getAccountTypeColor(account.account_type)}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        ₹{account.balance.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={account.is_active ? 'Active' : 'Inactive'}
                        color={account.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" color="primary" onClick={() => handleEditClick(account)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDeleteClick(account)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {/* Add/Edit Account Dialog */}
        <Dialog 
          open={addDialog || editDialog} 
          onClose={() => { setAddDialog(false); setEditDialog(false); }}
          maxWidth="sm" 
          fullWidth
        >
          <DialogTitle>
            {selectedAccount ? 'Edit Account' : 'Add New Account'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Account Code *"
                  value={formData.account_code}
                  onChange={(e) => setFormData(prev => ({ ...prev, account_code: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Account Type</InputLabel>
                  <Select
                    value={formData.account_type}
                    label="Account Type"
                    onChange={(e) => setFormData(prev => ({ ...prev, account_type: e.target.value }))}
                  >
                    {accountTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Account Name *"
                  value={formData.account_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, account_name: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Parent Account</InputLabel>
                  <Select
                    value={formData.parent_account}
                    label="Parent Account"
                    onChange={(e) => setFormData(prev => ({ ...prev, parent_account: e.target.value }))}
                  >
                    <MenuItem value="">
                      <em>None (Top Level Account)</em>
                    </MenuItem>
                    {accounts
                      .filter(acc => acc.account_type === formData.account_type)
                      .map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          {account.account_code} - {account.account_name}
                        </MenuItem>
                      ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setAddDialog(false); setEditDialog(false); }}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedAccount ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};
export default ChartOfAccountsPage;