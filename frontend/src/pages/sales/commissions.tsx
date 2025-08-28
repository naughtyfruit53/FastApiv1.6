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
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  MonetizationOn as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  CalendarToday as CalendarIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface Commission {
  id: number;
  salesperson: string;
  customerName: string;
  dealName: string;
  dealAmount: number;
  commissionRate: number;
  commissionAmount: number;
  status: 'pending' | 'approved' | 'paid' | 'disputed';
  saleDate: string;
  paymentDate: string | null;
  quarter: string;
  year: number;
  territory: string;
  product: string;
  notes: string;
}

interface CommissionSummary {
  salesperson: string;
  totalCommissions: number;
  pendingCommissions: number;
  paidCommissions: number;
  numberOfDeals: number;
  avgDealSize: number;
  commissionRate: number;
}

const CommissionTracking: React.FC = () => {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [summaries, setSummaries] = useState<CommissionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterYear, setFilterYear] = useState('2024');
  const [selectedCommission, setSelectedCommission] = useState<Commission | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');
  const [tabValue, setTabValue] = useState(0);

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchCommissionData = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockCommissions: Commission[] = [
          {
            id: 1,
            salesperson: 'Sarah Johnson',
            customerName: 'TechCorp Ltd',
            dealName: 'Enterprise Software License',
            dealAmount: 150000,
            commissionRate: 8,
            commissionAmount: 12000,
            status: 'approved',
            saleDate: '2024-01-15',
            paymentDate: '2024-02-01',
            quarter: 'Q1',
            year: 2024,
            territory: 'West',
            product: 'ERP Software',
            notes: 'Large enterprise deal with 3-year contract'
          },
          {
            id: 2,
            salesperson: 'David Brown',
            customerName: 'Global Systems Inc',
            dealName: 'Cloud Migration Project',
            dealAmount: 300000,
            commissionRate: 10,
            commissionAmount: 30000,
            status: 'paid',
            saleDate: '2024-01-10',
            paymentDate: '2024-01-25',
            quarter: 'Q1',
            year: 2024,
            territory: 'East',
            product: 'Cloud Services',
            notes: 'Multi-year cloud migration and support'
          },
          {
            id: 3,
            salesperson: 'Sarah Johnson',
            customerName: 'Manufacturing Co',
            dealName: 'ERP Implementation',
            dealAmount: 75000,
            commissionRate: 8,
            commissionAmount: 6000,
            status: 'pending',
            saleDate: '2024-01-20',
            paymentDate: null,
            quarter: 'Q1',
            year: 2024,
            territory: 'West',
            product: 'ERP Software',
            notes: 'Manufacturing-specific customizations required'
          },
          {
            id: 4,
            salesperson: 'Mike Wilson',
            customerName: 'Retail Corp',
            dealName: 'POS System Upgrade',
            dealAmount: 25000,
            commissionRate: 6,
            commissionAmount: 1500,
            status: 'disputed',
            saleDate: '2024-01-05',
            paymentDate: null,
            quarter: 'Q1',
            year: 2024,
            territory: 'Central',
            product: 'POS Software',
            notes: 'Customer disputing some features delivered'
          },
          {
            id: 5,
            salesperson: 'Lisa Thompson',
            customerName: 'Data Solutions Ltd',
            dealName: 'Analytics Platform',
            dealAmount: 50000,
            commissionRate: 7,
            commissionAmount: 3500,
            status: 'approved',
            saleDate: '2024-01-18',
            paymentDate: null,
            quarter: 'Q1',
            year: 2024,
            territory: 'South',
            product: 'Analytics Software',
            notes: 'AI-powered analytics solution'
          }
        ];

        const mockSummaries: CommissionSummary[] = [
          {
            salesperson: 'Sarah Johnson',
            totalCommissions: 18000,
            pendingCommissions: 6000,
            paidCommissions: 12000,
            numberOfDeals: 2,
            avgDealSize: 112500,
            commissionRate: 8
          },
          {
            salesperson: 'David Brown',
            totalCommissions: 30000,
            pendingCommissions: 0,
            paidCommissions: 30000,
            numberOfDeals: 1,
            avgDealSize: 300000,
            commissionRate: 10
          },
          {
            salesperson: 'Mike Wilson',
            totalCommissions: 1500,
            pendingCommissions: 1500,
            paidCommissions: 0,
            numberOfDeals: 1,
            avgDealSize: 25000,
            commissionRate: 6
          },
          {
            salesperson: 'Lisa Thompson',
            totalCommissions: 3500,
            pendingCommissions: 3500,
            paidCommissions: 0,
            numberOfDeals: 1,
            avgDealSize: 50000,
            commissionRate: 7
          }
        ];
        
        setCommissions(mockCommissions);
        setSummaries(mockSummaries);
      } catch (err) {
        setError('Failed to load commission data');
        console.error('Error fetching commission data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCommissionData();
  }, [filterYear]);

  const filteredCommissions = commissions.filter(commission => {
    const matchesSearch = 
      commission.salesperson.toLowerCase().includes(searchTerm.toLowerCase()) ||
      commission.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      commission.dealName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || commission.status === filterStatus;
    const matchesYear = commission.year.toString() === filterYear;
    
    return matchesSearch && matchesStatus && matchesYear;
  });

  const handleViewCommission = (commission: Commission) => {
    setSelectedCommission(commission);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleEditCommission = (commission: Commission) => {
    setSelectedCommission(commission);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleCreateCommission = () => {
    setSelectedCommission(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedCommission(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'success';
      case 'approved': return 'primary';
      case 'pending': return 'warning';
      case 'disputed': return 'error';
      default: return 'default';
    }
  };

  const totalCommissions = summaries.reduce((sum, s) => sum + s.totalCommissions, 0);
  const totalPending = summaries.reduce((sum, s) => sum + s.pendingCommissions, 0);
  const totalPaid = summaries.reduce((sum, s) => sum + s.paidCommissions, 0);
  const totalDeals = summaries.reduce((sum, s) => sum + s.numberOfDeals, 0);

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
        Commission Tracking
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Commissions
              </Typography>
              <Typography variant="h4">
                ${totalCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {filterYear}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Paid Commissions
              </Typography>
              <Typography variant="h4" color="success.main">
                ${totalPaid.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="success.main">
                {totalCommissions > 0 ? Math.round((totalPaid / totalCommissions) * 100) : 0}% of total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Commissions
              </Typography>
              <Typography variant="h4" color="warning.main">
                ${totalPending.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="warning.main">
                {totalCommissions > 0 ? Math.round((totalPending / totalCommissions) * 100) : 0}% of total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Deals
              </Typography>
              <Typography variant="h4">
                {totalDeals}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Commissioned deals
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for different views */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Commission Details" />
          <Tab label="Salesperson Summary" />
        </Tabs>
      </Paper>

      {/* Commission Details Tab */}
      {tabValue === 0 && (
        <Box>
          {/* Filters and Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <TextField
                placeholder="Search commissions..."
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
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="paid">Paid</MenuItem>
                  <MenuItem value="disputed">Disputed</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 100 }}>
                <InputLabel>Year</InputLabel>
                <Select
                  value={filterYear}
                  label="Year"
                  onChange={(e) => setFilterYear(e.target.value)}
                >
                  <MenuItem value="2024">2024</MenuItem>
                  <MenuItem value="2023">2023</MenuItem>
                  <MenuItem value="2022">2022</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateCommission}
            >
              Add Commission
            </Button>
          </Box>

          {/* Commissions Table */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Salesperson</TableCell>
                  <TableCell>Deal</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell align="right">Deal Amount</TableCell>
                  <TableCell align="right">Rate</TableCell>
                  <TableCell align="right">Commission</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Sale Date</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCommissions.map((commission) => (
                  <TableRow key={commission.id} hover>
                    <TableCell>{commission.salesperson}</TableCell>
                    <TableCell>
                      <Typography variant="subtitle2">{commission.dealName}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {commission.product}
                      </Typography>
                    </TableCell>
                    <TableCell>{commission.customerName}</TableCell>
                    <TableCell align="right">${commission.dealAmount.toLocaleString()}</TableCell>
                    <TableCell align="right">{commission.commissionRate}%</TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle2" color="success.main">
                        ${commission.commissionAmount.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={commission.status}
                        color={getStatusColor(commission.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{new Date(commission.saleDate).toLocaleDateString()}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details">
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewCommission(commission)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Commission">
                        <IconButton 
                          size="small" 
                          onClick={() => handleEditCommission(commission)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Salesperson Summary Tab */}
      {tabValue === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Commission Summary by Salesperson
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Salesperson</TableCell>
                  <TableCell align="right">Total Commissions</TableCell>
                  <TableCell align="right">Paid</TableCell>
                  <TableCell align="right">Pending</TableCell>
                  <TableCell align="right">Deals</TableCell>
                  <TableCell align="right">Avg Deal Size</TableCell>
                  <TableCell align="right">Commission Rate</TableCell>
                  <TableCell>Payment Progress</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {summaries.map((summary, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                        {summary.salesperson}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle2">
                        ${summary.totalCommissions.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography color="success.main">
                        ${summary.paidCommissions.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography color="warning.main">
                        ${summary.pendingCommissions.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{summary.numberOfDeals}</TableCell>
                    <TableCell align="right">
                      ${summary.avgDealSize.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">{summary.commissionRate}%</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 120 }}>
                        <LinearProgress
                          variant="determinate"
                          value={summary.totalCommissions > 0 ? (summary.paidCommissions / summary.totalCommissions) * 100 : 0}
                          sx={{ flexGrow: 1, mr: 1, height: 8, borderRadius: 4 }}
                          color="success"
                        />
                        <Typography variant="body2" color="textSecondary">
                          {summary.totalCommissions > 0 ? Math.round((summary.paidCommissions / summary.totalCommissions) * 100) : 0}%
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Commission Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Add New Commission' : 
           dialogMode === 'edit' ? 'Edit Commission' : 'Commission Details'}
        </DialogTitle>
        <DialogContent>
          {selectedCommission && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Salesperson"
                    value={selectedCommission.salesperson}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Customer Name"
                    value={selectedCommission.customerName}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Deal Name"
                    value={selectedCommission.dealName}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Product"
                    value={selectedCommission.product}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Deal Amount"
                    type="number"
                    value={selectedCommission.dealAmount}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Commission Rate (%)"
                    type="number"
                    value={selectedCommission.commissionRate}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Commission Amount"
                    type="number"
                    value={selectedCommission.commissionAmount}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth disabled={dialogMode === 'view'}>
                    <InputLabel>Status</InputLabel>
                    <Select value={selectedCommission.status} label="Status">
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="approved">Approved</MenuItem>
                      <MenuItem value="paid">Paid</MenuItem>
                      <MenuItem value="disputed">Disputed</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Territory"
                    value={selectedCommission.territory}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sale Date"
                    type="date"
                    value={selectedCommission.saleDate}
                    disabled={dialogMode === 'view'}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Payment Date"
                    type="date"
                    value={selectedCommission.paymentDate || ''}
                    disabled={dialogMode === 'view'}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Notes"
                    multiline
                    rows={3}
                    value={selectedCommission.notes}
                    disabled={dialogMode === 'view'}
                  />
                </Grid>
              </Grid>
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

export default CommissionTracking;