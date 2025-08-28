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
import AddOpportunityModal from '../../components/AddOpportunityModal';
import { crmService } from '../../services/crmService';

interface Opportunity {
  id: number;
  name: string;
  account_name?: string;
  contact_name?: string;
  stage: string;
  amount: number;
  probability: number;
  close_date: string;
  source: string;
  created_at: string;
  assigned_to_id?: number;
}

const OpportunityTracking: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  // Fetch opportunities from API
  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);
      const opportunitiesData = await crmService.getOpportunities();
      setOpportunities(opportunitiesData);
    } catch (err) {
      console.error('Error fetching opportunities:', err);
      setError('Failed to load opportunities. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const handleAddOpportunity = async (opportunityData: any) => {
    try {
      setAddLoading(true);
      await crmService.createOpportunity(opportunityData);
      await fetchOpportunities(); // Refresh the list
      setDialogOpen(false);
    } catch (err) {
      console.error('Error adding opportunity:', err);
      throw err; // Let the modal handle the error
    } finally {
      setAddLoading(false);
    }
  };

  const filteredOpportunities = opportunities.filter(opportunity =>
    opportunity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (opportunity.account_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (opportunity.contact_name || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    // Add view functionality if needed
  };

  const handleEditOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    // Add edit functionality if needed
  };

  const handleCreateOpportunity = () => {
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedOpportunity(null);
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'prospecting': return 'info';
      case 'qualification': return 'warning';
      case 'needs_analysis': return 'secondary';
      case 'proposal': return 'primary';
      case 'negotiation': return 'error';
      case 'closed_won': return 'success';
      case 'closed_lost': return 'default';
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
              <TableCell>Source</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredOpportunities.map((opportunity) => (
              <TableRow key={opportunity.id} hover>
                <TableCell>{opportunity.name}</TableCell>
                <TableCell>{opportunity.account_name || '-'}</TableCell>
                <TableCell>{opportunity.contact_name || '-'}</TableCell>
                <TableCell>
                  <Chip 
                    label={opportunity.stage.replace('_', ' ').toUpperCase()} 
                    color={getStageColor(opportunity.stage) as any}
                    size="small"
                    sx={{ textTransform: 'capitalize' }}
                  />
                </TableCell>
                <TableCell align="right">${opportunity.amount.toLocaleString()}</TableCell>
                <TableCell align="right">{opportunity.probability}%</TableCell>
                <TableCell>{new Date(opportunity.close_date).toLocaleDateString()}</TableCell>
                <TableCell>{opportunity.source}</TableCell>
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
            {filteredOpportunities.length === 0 && !loading && (
              <TableRow>
                <TableCell colSpan={9} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                    No opportunities found. {opportunities.length === 0 ? 'Start by adding your first opportunity!' : 'Try adjusting your search terms.'}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Opportunity Modal */}
      <AddOpportunityModal
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onAdd={handleAddOpportunity}
        loading={addLoading}
      />
    </Container>
  );
};

export default OpportunityTracking;