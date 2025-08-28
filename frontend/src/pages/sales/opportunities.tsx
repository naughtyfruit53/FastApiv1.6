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
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MoneyIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';

interface Opportunity {
  id: number;
  name: string;
  account: string;
  contact: string;
  stage: string;
  amount: number;
  probability: number;
  closeDate: string;
  owner: string;
  source: string;
  created_at: string;
}

const OpportunityTracking: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create'>('view');
  const [tabValue, setTabValue] = useState(0);

  // Mock data - replace with actual API call
  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        setLoading(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockData: Opportunity[] = [
          {
            id: 1,
            name: 'Enterprise Software License',
            account: 'TechCorp Ltd',
            contact: 'John Smith',
            stage: 'Proposal',
            amount: 150000,
            probability: 75,
            closeDate: '2024-02-15',
            owner: 'Sarah Johnson',
            source: 'Website',
            created_at: '2024-01-10'
          },
          {
            id: 2,
            name: 'Cloud Migration Project',
            account: 'Global Systems Inc',
            contact: 'Mike Wilson',
            stage: 'Negotiation',
            amount: 300000,
            probability: 85,
            closeDate: '2024-02-28',
            owner: 'David Brown',
            source: 'Referral',
            created_at: '2024-01-05'
          },
          {
            id: 3,
            name: 'ERP Implementation',
            account: 'Manufacturing Co',
            contact: 'Lisa Davis',
            stage: 'Qualification',
            amount: 75000,
            probability: 45,
            closeDate: '2024-03-30',
            owner: 'Sarah Johnson',
            source: 'Cold Call',
            created_at: '2024-01-15'
          }
        ];
        
        setOpportunities(mockData);
      } catch (err) {
        setError('Failed to load opportunities');
        console.error('Error fetching opportunities:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOpportunities();
  }, []);

  const filteredOpportunities = opportunities.filter(opportunity =>
    opportunity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    opportunity.account.toLowerCase().includes(searchTerm.toLowerCase()) ||
    opportunity.contact.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setDialogMode('view');
    setDialogOpen(true);
  };

  const handleEditOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setDialogMode('edit');
    setDialogOpen(true);
  };

  const handleCreateOpportunity = () => {
    setSelectedOpportunity(null);
    setDialogMode('create');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedOpportunity(null);
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'Qualification': return 'default';
      case 'Proposal': return 'primary';
      case 'Negotiation': return 'warning';
      case 'Closed Won': return 'success';
      case 'Closed Lost': return 'error';
      default: return 'default';
    }
  };

  const totalValue = opportunities.reduce((sum, opp) => sum + opp.amount, 0);
  const weightedValue = opportunities.reduce((sum, opp) => sum + (opp.amount * opp.probability / 100), 0);
  const avgProbability = opportunities.length > 0 
    ? opportunities.reduce((sum, opp) => sum + opp.probability, 0) / opportunities.length 
    : 0;

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
        Opportunity Tracking
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Opportunities
              </Typography>
              <Typography variant="h4">
                {opportunities.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4">
                ${totalValue.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Weighted Value
              </Typography>
              <Typography variant="h4">
                ${Math.round(weightedValue).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Probability
              </Typography>
              <Typography variant="h4">
                {Math.round(avgProbability)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions Bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <TextField
          placeholder="Search opportunities..."
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
          onClick={handleCreateOpportunity}
        >
          Add Opportunity
        </Button>
      </Box>

      {/* Opportunities Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Opportunity Name</TableCell>
              <TableCell>Account</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell align="right">Probability</TableCell>
              <TableCell>Close Date</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredOpportunities.map((opportunity) => (
              <TableRow key={opportunity.id} hover>
                <TableCell>{opportunity.name}</TableCell>
                <TableCell>{opportunity.account}</TableCell>
                <TableCell>{opportunity.contact}</TableCell>
                <TableCell>
                  <Chip 
                    label={opportunity.stage} 
                    color={getStageColor(opportunity.stage) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">${opportunity.amount.toLocaleString()}</TableCell>
                <TableCell align="right">{opportunity.probability}%</TableCell>
                <TableCell>{new Date(opportunity.closeDate).toLocaleDateString()}</TableCell>
                <TableCell>{opportunity.owner}</TableCell>
                <TableCell align="center">
                  <IconButton 
                    size="small" 
                    onClick={() => handleViewOpportunity(opportunity)}
                    title="View Details"
                  >
                    <ViewIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={() => handleEditOpportunity(opportunity)}
                    title="Edit Opportunity"
                  >
                    <EditIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Opportunity Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Add New Opportunity' : 
           dialogMode === 'edit' ? 'Edit Opportunity' : 'Opportunity Details'}
        </DialogTitle>
        <DialogContent>
          {selectedOpportunity && (
            <Box sx={{ mt: 2 }}>
              <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
                <Tab label="General Information" />
                <Tab label="Details" />
                <Tab label="Timeline" />
              </Tabs>
              
              {tabValue === 0 && (
                <Grid container spacing={3} sx={{ mt: 1 }}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Opportunity Name"
                      value={selectedOpportunity.name}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Account"
                      value={selectedOpportunity.account}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Contact"
                      value={selectedOpportunity.contact}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={dialogMode === 'view'}>
                      <InputLabel>Stage</InputLabel>
                      <Select value={selectedOpportunity.stage} label="Stage">
                        <MenuItem value="Qualification">Qualification</MenuItem>
                        <MenuItem value="Proposal">Proposal</MenuItem>
                        <MenuItem value="Negotiation">Negotiation</MenuItem>
                        <MenuItem value="Closed Won">Closed Won</MenuItem>
                        <MenuItem value="Closed Lost">Closed Lost</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Amount"
                      type="number"
                      value={selectedOpportunity.amount}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Probability (%)"
                      type="number"
                      value={selectedOpportunity.probability}
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
                      label="Close Date"
                      type="date"
                      value={selectedOpportunity.closeDate}
                      disabled={dialogMode === 'view'}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Owner"
                      value={selectedOpportunity.owner}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Source"
                      value={selectedOpportunity.source}
                      disabled={dialogMode === 'view'}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Description"
                      multiline
                      rows={4}
                      disabled={dialogMode === 'view'}
                      placeholder="Enter opportunity description..."
                    />
                  </Grid>
                </Grid>
              )}
              
              {tabValue === 2 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Activity Timeline</Typography>
                  <Typography color="textSecondary">
                    Timeline functionality will be implemented with backend integration.
                  </Typography>
                </Box>
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

export default OpportunityTracking;