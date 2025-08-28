'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MoneyIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';

interface Account {
  id: number;
  name: string;
  type: 'customer' | 'prospect' | 'partner' | 'vendor';
  industry: string;
  size: 'small' | 'medium' | 'large' | 'enterprise';
  revenue: number;
  employees: number;
  website: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  status: 'active' | 'inactive' | 'prospect';
  parentAccount: string | null;
  accountManager: string;
  source: string;
  created_at: string;
  lastActivity: string;
  description: string;
  totalContracts: number;
  totalRevenue: number;
  primaryContact: string;
}

const AccountManagement: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');
  const [tabValue, setTabValue] = useState(0);

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData: Account[] = [
          {
            id: 1,
            name: 'TechCorp Ltd',
            type: 'customer',
            industry: 'Technology',
            size: 'large',
            revenue: 50000000,
            employees: 500,
            website: 'www.techcorp.com',
            phone: '+1-555-0123',
            email: 'info@techcorp.com',
            address: '123 Tech Street',
            city: 'San Francisco',
            state: 'CA',
            zipCode: '94105',
            country: 'USA',
            status: 'active',
            parentAccount: null,
            accountManager: 'Sarah Johnson',
            source: 'Website',
            created_at: '2022-03-10',
            lastActivity: '2024-01-20',
            description: 'Leading technology company specializing in enterprise software solutions.',
            totalContracts: 3,
            totalRevenue: 450000,
            primaryContact: 'John Smith'
          },
          {
            id: 2,
            name: 'Global Systems Inc',
            type: 'customer',
            industry: 'Manufacturing',
            size: 'enterprise',
            revenue: 200000000,
            employees: 2000,
            website: 'www.globalsystems.com',
            phone: '+1-555-0124',
            email: 'contact@globalsystems.com',
            address: '456 Business Ave',
            city: 'New York',
            state: 'NY',
            zipCode: '10001',
            country: 'USA',
            status: 'active',
            parentAccount: null,
            accountManager: 'David Brown',
            source: 'Referral',
            created_at: '2021-07-15',
            lastActivity: '2024-01-18',
            description: 'Global manufacturing conglomerate with operations in 50+ countries.',
            totalContracts: 5,
            totalRevenue: 850000,
            primaryContact: 'Mike Wilson'
          },
          {
            id: 3,
            name: 'Manufacturing Co',
            type: 'prospect',
            industry: 'Manufacturing',
            size: 'medium',
            revenue: 25000000,
            employees: 250,
            website: 'www.manufacturing.com',
            phone: '+1-555-0125',
            email: 'info@manufacturing.com',
            address: '789 Industrial Blvd',
            city: 'Detroit',
            state: 'MI',
            zipCode: '48201',
            country: 'USA',
            status: 'prospect',
            parentAccount: null,
            accountManager: 'Sarah Johnson',
            source: 'Cold Call',
            created_at: '2024-01-10',
            lastActivity: '2024-01-15',
            description: 'Mid-size manufacturing company looking to modernize their ERP systems.',
            totalContracts: 0,
            totalRevenue: 0,
            primaryContact: 'Lisa Davis'
          },
          {
            id: 4,
            name: 'Retail Corp',
            type: 'customer',
            industry: 'Retail',
            size: 'medium',
            revenue: 15000000,
            employees: 150,
            website: 'www.retailcorp.com',
            phone: '+1-555-0126',
            email: 'contact@retailcorp.com',
            address: '321 Commerce St',
            city: 'Los Angeles',
            state: 'CA',
            zipCode: '90210',
            country: 'USA',
            status: 'inactive',
            parentAccount: null,
            accountManager: 'Mike Wilson',
            source: 'Trade Show',
            created_at: '2022-01-18',
            lastActivity: '2023-12-08',
            description: 'Regional retail chain with 25 locations across the west coast.',
            totalContracts: 2,
            totalRevenue: 125000,
            primaryContact: 'Robert Chen'
          },
          {
            id: 5,
            name: 'Data Solutions Ltd',
            type: 'customer',
            industry: 'Technology',
            size: 'small',
            revenue: 5000000,
            employees: 50,
            website: 'www.datasolutions.com',
            phone: '+1-555-0127',
            email: 'hello@datasolutions.com',
            address: '654 Data Drive',
            city: 'Austin',
            state: 'TX',
            zipCode: '73301',
            country: 'USA',
            status: 'active',
            parentAccount: null,
            accountManager: 'Lisa Thompson',
            source: 'LinkedIn',
            created_at: '2023-05-12',
            lastActivity: '2024-01-22',
            description: 'Data analytics startup focusing on AI-powered business intelligence.',
            totalContracts: 1,
            totalRevenue: 75000,
            primaryContact: 'Emily Rodriguez'
          }
        ];
        
        setAccounts(mockData);
      } catch (err) {
        setError('Failed to load accounts');
        console.error('Error fetching accounts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  const filteredAccounts = accounts.filter(account => {
    const matchesSearch = 
      account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.accountManager.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || account.type === filterType;
    const matchesStatus = filterStatus === 'all' || account.status === filterStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const handleViewAccount = (account: Account) => {
    setSelectedAccount(account);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleEditAccount = (account: Account) => {
    setSelectedAccount(account);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleCreateAccount = () => {
    setSelectedAccount(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedAccount(null);
    setTabValue(0);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'customer': return 'success';
      case 'prospect': return 'primary';
      case 'partner': return 'warning';
      case 'vendor': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'prospect': return 'primary';
      case 'inactive': return 'default';
      default: return 'default';
    }
  };

  const getSizeColor = (size: string) => {
    switch (size) {
      case 'enterprise': return 'error';
      case 'large': return 'warning';
      case 'medium': return 'primary';
      case 'small': return 'success';
      default: return 'default';
    }
  };

  const accountStats = {
    total: accounts.length,
    customers: accounts.filter(a => a.type === 'customer').length,
    prospects: accounts.filter(a => a.type === 'prospect').length,
    totalRevenue: accounts.reduce((sum, a) => sum + a.totalRevenue, 0)
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={40} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Account Management
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Accounts
              </Typography>
              <Typography variant="h4">
                {accountStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Customers
              </Typography>
              <Typography variant="h4" color="success.main">
                {accountStats.customers}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Prospects
              </Typography>
              <Typography variant="h4" color="primary.main">
                {accountStats.prospects}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h4" color="success.main">
                ${(accountStats.totalRevenue / 1000).toFixed(0)}K
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            placeholder="Search accounts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300 }}
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filterType}
              label="Type"
              onChange={(e) => setFilterType(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="customer">Customer</MenuItem>
              <MenuItem value="prospect">Prospect</MenuItem>
              <MenuItem value="partner">Partner</MenuItem>
              <MenuItem value="vendor">Vendor</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              label="Status"
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="prospect">Prospect</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateAccount}
        >
          Add Account
        </Button>
      </Box>

      {/* Accounts Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Account Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Industry</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Revenue</TableCell>
              <TableCell>Account Manager</TableCell>
              <TableCell>Last Activity</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAccounts.map((account) => (
              <TableRow key={account.id} hover>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      {account.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {account.city}, {account.state}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={account.type}
                    color={getTypeColor(account.type) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{account.industry}</TableCell>
                <TableCell>
                  <Chip 
                    label={account.size}
                    color={getSizeColor(account.size) as any}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={account.status}
                    color={getStatusColor(account.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  ${account.totalRevenue.toLocaleString()}
                </TableCell>
                <TableCell>{account.accountManager}</TableCell>
                <TableCell>{new Date(account.lastActivity).toLocaleDateString()}</TableCell>
                <TableCell align="center">
                  <IconButton 
                    size="small" 
                    onClick={() => handleViewAccount(account)}
                    title="View Details"
                  >
                    <ViewIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={() => handleEditAccount(account)}
                    title="Edit Account"
                  >
                    <EditIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Account Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Add New Account' : 
           dialogMode === 'edit' ? 'Edit Account' : 'Account Details'}
        </DialogTitle>
        <DialogContent>
          {selectedAccount && (
            <Box sx={{ mt: 2 }}>
              <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
                <Tab label="General Information" />
                <Tab label="Contact Details" />
                <Tab label="Business Information" />
                <Tab label="Activity & Notes" />
              </Tabs>
              
              {tabValue === 0 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account Name"
                      value={selectedAccount.name}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === 'view'}>
                      <InputLabel>Account Type</InputLabel>
                      <Select value={selectedAccount.type} label="Account Type">
                        <MenuItem value="customer">Customer</MenuItem>
                        <MenuItem value="prospect">Prospect</MenuItem>
                        <MenuItem value="partner">Partner</MenuItem>
                        <MenuItem value="vendor">Vendor</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Industry"
                      value={selectedAccount.industry}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === 'view'}>
                      <InputLabel>Company Size</InputLabel>
                      <Select value={selectedAccount.size} label="Company Size">
                        <MenuItem value="small">Small (1-50)</MenuItem>
                        <MenuItem value="medium">Medium (51-500)</MenuItem>
                        <MenuItem value="large">Large (501-5000)</MenuItem>
                        <MenuItem value="enterprise">Enterprise (5000+)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === 'view'}>
                      <InputLabel>Status</InputLabel>
                      <Select value={selectedAccount.status} label="Status">
                        <MenuItem value="active">Active</MenuItem>
                        <MenuItem value="prospect">Prospect</MenuItem>
                        <MenuItem value="inactive">Inactive</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account Manager"
                      value={selectedAccount.accountManager}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                </Grid>
              )}
              
              {tabValue === 1 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={selectedAccount.phone}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={selectedAccount.email}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Website"
                      value={selectedAccount.website}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Primary Contact"
                      value={selectedAccount.primaryContact}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      value={selectedAccount.address}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="City"
                      value={selectedAccount.city}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="State"
                      value={selectedAccount.state}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Zip Code"
                      value={selectedAccount.zipCode}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                </Grid>
              )}
              
              {tabValue === 2 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Annual Revenue"
                      type="number"
                      value={selectedAccount.revenue}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Number of Employees"
                      type="number"
                      value={selectedAccount.employees}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Total Contracts"
                      type="number"
                      value={selectedAccount.totalContracts}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Total Revenue with Us"
                      type="number"
                      value={selectedAccount.totalRevenue}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Description"
                      multiline
                      rows={4}
                      value={selectedAccount.description}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                </Grid>
              )}
              
              {tabValue === 3 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Source"
                      value={selectedAccount.source}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Last Activity Date"
                      type="date"
                      value={selectedAccount.lastActivity}
                      disabled={dialogMode === 'view'}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>Recent Activities</Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <AssignmentIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Contract Renewal Discussion"
                          secondary="Meeting scheduled with decision makers - Jan 20, 2024"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <EmailIcon color="success" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Proposal Sent"
                          secondary="Detailed proposal sent for Q2 implementation - Jan 15, 2024"
                        />
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemIcon>
                          <PhoneIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Follow-up Call"
                          secondary="Discussed technical requirements - Jan 10, 2024"
                        />
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === 'view' ? 'Close' : 'Cancel'}
          </Button>
          {dialogMode !== 'view' && (
            <Button variant="contained" onClick={handleCloseDialog}>
              {dialogMode === 'create' ? 'Create' : 'Save'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AccountManagement;