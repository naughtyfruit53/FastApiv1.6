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
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  MonetizationOn as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import AddCommissionModal from '../../components/AddCommissionModal';

interface Commission {
  id: number;
  sales_person_id: number;
  sales_person_name?: string;
  opportunity_id?: number;
  lead_id?: number;
  commission_type: string;
  commission_rate?: number;
  commission_amount?: number;
  base_amount: number;
  commission_date: string;
  payment_status: string;
  notes?: string;
  created_at: string;
}

const CommissionTracking: React.FC = () => {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);

  // Fetch commissions from backend
  const fetchCommissions = async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Implement commission service when backend endpoint is available
      // For now, show empty state
      setCommissions([]);
    } catch (err) {
      console.error('Error fetching commissions:', err);
      setError('Failed to load commissions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommissions();
  }, []);

  const handleAddCommission = async (commissionData: any) => {
    try {
      setAddLoading(true);
      // TODO: Implement commission creation when backend endpoint is available
      console.log('Commission data:', commissionData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock adding to state for now
      const newCommission: Commission = {
        id: Date.now(),
        ...commissionData,
        created_at: new Date().toISOString()
      };
      
      setCommissions(prev => [newCommission, ...prev]);
      setDialogOpen(false);
    } catch (err) {
      console.error('Error adding commission:', err);
      throw err;
    } finally {
      setAddLoading(false);
    }
  };

  const filteredCommissions = commissions.filter(commission => {
    const matchesSearch = 
      (commission.sales_person_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (commission.notes || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || commission.payment_status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'info';
      case 'paid': return 'success';
      case 'rejected': return 'error';
      case 'on_hold': return 'default';
      default: return 'default';
    }
  };

  const totalCommissions = commissions.reduce((sum, c) => sum + (c.commission_amount || 0), 0);
  const pendingCommissions = commissions.filter(c => c.payment_status === 'pending').reduce((sum, c) => sum + (c.commission_amount || 0), 0);
  const paidCommissions = commissions.filter(c => c.payment_status === 'paid').reduce((sum, c) => sum + (c.commission_amount || 0), 0);

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
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MoneyIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Commissions</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                ${totalCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CalendarIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Pending</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                ${pendingCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Awaiting payment
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Paid</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                ${paidCommissions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed payments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Records</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {commissions.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total records
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
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
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Add Commission
        </Button>
      </Box>

      {/* Commissions Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Sales Person</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Base Amount</TableCell>
                <TableCell align="right">Rate/Amount</TableCell>
                <TableCell align="right">Commission</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCommissions.map((commission) => (
                <TableRow key={commission.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2">
                        User ID: {commission.sales_person_id}
                      </Typography>
                      {commission.sales_person_name && (
                        <Typography variant="body2" color="text.secondary">
                          {commission.sales_person_name}
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={commission.commission_type.replace('_', ' ').toUpperCase()} 
                      size="small"
                      variant="outlined"
                      sx={{ textTransform: 'capitalize' }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    ${commission.base_amount.toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    {commission.commission_type === 'percentage' ? (
                      `${commission.commission_rate}%`
                    ) : (
                      `$${commission.commission_amount?.toLocaleString() || 0}`
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" color="primary">
                      ${(commission.commission_amount || 
                        (commission.commission_rate ? 
                          (commission.base_amount * commission.commission_rate) / 100 : 0)
                        ).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {new Date(commission.commission_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={commission.payment_status.replace('_', ' ').toUpperCase()} 
                      color={getStatusColor(commission.payment_status) as any}
                      size="small"
                      sx={{ textTransform: 'capitalize' }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <IconButton size="small" title="View">
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" title="Edit">
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {filteredCommissions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      {commissions.length === 0 
                        ? 'No commission records found. Start by adding your first commission record!' 
                        : 'No records match your search criteria.'}
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Add Commission Modal */}
      <AddCommissionModal
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onAdd={handleAddCommission}
        loading={addLoading}
      />
    </Container>
  );
};

export default CommissionTracking;
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