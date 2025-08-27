// frontend/src/pages/crm/index.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
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
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  AttachMoney as AttachMoneyIcon,
} from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';

interface Lead {
  id: number;
  lead_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  status: string;
  source: string;
  score: number;
  estimated_value?: number;
  created_at: string;
}

interface Opportunity {
  id: number;
  opportunity_number: string;
  name: string;
  stage: string;
  amount: number;
  probability: number;
  expected_revenue: number;
  expected_close_date: string;
  customer_id?: number;
  created_at: string;
}

interface CRMAnalytics {
  leads_total: number;
  leads_by_status: Record<string, number>;
  opportunities_total: number;
  pipeline_value: number;
  weighted_pipeline_value: number;
  conversion_rate: number;
  win_rate: number;
}

const statusColors: Record<string, string> = {
  new: 'default',
  contacted: 'info',
  qualified: 'warning',
  converted: 'success',
  lost: 'error',
  nurturing: 'secondary',
};

const stageColors: Record<string, string> = {
  prospecting: 'default',
  qualification: 'info',
  proposal: 'warning',
  negotiation: 'secondary',
  closed_won: 'success',
  closed_lost: 'error',
};

export default function CRMDashboard() {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [analytics, setAnalytics] = useState<CRMAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [openLeadDialog, setOpenLeadDialog] = useState(false);
  const [openOpportunityDialog, setOpenOpportunityDialog] = useState(false);

  useEffect(() => {
    loadCRMData();
  }, []);

  const loadCRMData = async () => {
    setLoading(true);
    try {
      // Simulate API calls - in production these would be real API calls
      const mockLeads: Lead[] = [
        {
          id: 1,
          lead_number: 'LD000001',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          phone: '+1234567890',
          company: 'ABC Corp',
          status: 'qualified',
          source: 'website',
          score: 85,
          estimated_value: 50000,
          created_at: '2024-08-27T10:00:00Z',
        },
        {
          id: 2,
          lead_number: 'LD000002',
          first_name: 'Jane',
          last_name: 'Smith',
          email: 'jane.smith@example.com',
          company: 'XYZ Inc',
          status: 'contacted',
          source: 'referral',
          score: 65,
          estimated_value: 30000,
          created_at: '2024-08-26T14:30:00Z',
        },
      ];

      const mockOpportunities: Opportunity[] = [
        {
          id: 1,
          opportunity_number: 'OP000001',
          name: 'ABC Corp - ERP Implementation',
          stage: 'proposal',
          amount: 75000,
          probability: 60,
          expected_revenue: 45000,
          expected_close_date: '2024-09-15',
          created_at: '2024-08-20T09:00:00Z',
        },
        {
          id: 2,
          opportunity_number: 'OP000002',
          name: 'XYZ Inc - Software License',
          stage: 'negotiation',
          amount: 25000,
          probability: 80,
          expected_revenue: 20000,
          expected_close_date: '2024-08-30',
          created_at: '2024-08-22T11:15:00Z',
        },
      ];

      const mockAnalytics: CRMAnalytics = {
        leads_total: 15,
        leads_by_status: {
          new: 3,
          contacted: 5,
          qualified: 4,
          converted: 2,
          lost: 1,
        },
        opportunities_total: 8,
        pipeline_value: 250000,
        weighted_pipeline_value: 150000,
        conversion_rate: 13.3,
        win_rate: 75.0,
      };

      setLeads(mockLeads);
      setOpportunities(mockOpportunities);
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Error loading CRM data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(
    (lead) =>
      lead.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.company && lead.company.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const filteredOpportunities = opportunities.filter(
    (opportunity) =>
      opportunity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opportunity.opportunity_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderAnalyticsCards = () => {
    if (!analytics) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PeopleIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Leads
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.leads_total}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AssignmentIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Opportunities
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.opportunities_total}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AttachMoneyIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pipeline Value
                  </Typography>
                  <Typography variant="h5" component="div">
                    ${analytics.pipeline_value.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Conversion Rate
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.conversion_rate}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderLeadsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Lead #</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Company</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Score</TableCell>
            <TableCell>Est. Value</TableCell>
            <TableCell>Created</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredLeads.map((lead) => (
            <TableRow key={lead.id} hover>
              <TableCell>{lead.lead_number}</TableCell>
              <TableCell>
                {lead.first_name} {lead.last_name}
              </TableCell>
              <TableCell>{lead.company || '-'}</TableCell>
              <TableCell>{lead.email}</TableCell>
              <TableCell>
                <Chip
                  label={lead.status}
                  color={statusColors[lead.status] as any}
                  size="small"
                />
              </TableCell>
              <TableCell>{lead.score}</TableCell>
              <TableCell>
                {lead.estimated_value ? `$${lead.estimated_value.toLocaleString()}` : '-'}
              </TableCell>
              <TableCell>
                {new Date(lead.created_at).toLocaleDateString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderOpportunitiesTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Opportunity #</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Stage</TableCell>
            <TableCell>Amount</TableCell>
            <TableCell>Probability</TableCell>
            <TableCell>Expected Revenue</TableCell>
            <TableCell>Close Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredOpportunities.map((opportunity) => (
            <TableRow key={opportunity.id} hover>
              <TableCell>{opportunity.opportunity_number}</TableCell>
              <TableCell>{opportunity.name}</TableCell>
              <TableCell>
                <Chip
                  label={opportunity.stage}
                  color={stageColors[opportunity.stage] as any}
                  size="small"
                />
              </TableCell>
              <TableCell>${opportunity.amount.toLocaleString()}</TableCell>
              <TableCell>{opportunity.probability}%</TableCell>
              <TableCell>${opportunity.expected_revenue.toLocaleString()}</TableCell>
              <TableCell>
                {new Date(opportunity.expected_close_date).toLocaleDateString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          CRM Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenLeadDialog(true)}
          >
            Add Lead
          </Button>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setOpenOpportunityDialog(true)}
          >
            Add Opportunity
          </Button>
        </Box>
      </Box>

      {renderAnalyticsCards()}

      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab label="Leads" />
              <Tab label="Opportunities" />
            </Tabs>
          </Box>

          <Box sx={{ mb: 2 }}>
            <TextField
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ maxWidth: 300 }}
            />
          </Box>

          {currentTab === 0 && renderLeadsTable()}
          {currentTab === 1 && renderOpportunitiesTable()}
        </CardContent>
      </Card>

      {/* Add Lead Dialog - Placeholder */}
      <Dialog
        open={openLeadDialog}
        onClose={() => setOpenLeadDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add New Lead</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="First Name"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Last Name"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Email"
                  type="email"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Phone"
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Company"
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Source</InputLabel>
                  <Select defaultValue="website">
                    <MenuItem value="website">Website</MenuItem>
                    <MenuItem value="referral">Referral</MenuItem>
                    <MenuItem value="social_media">Social Media</MenuItem>
                    <MenuItem value="email_campaign">Email Campaign</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Estimated Value"
                  type="number"
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenLeadDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenLeadDialog(false)}>
            Create Lead
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Opportunity Dialog - Placeholder */}
      <Dialog
        open={openOpportunityDialog}
        onClose={() => setOpenOpportunityDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add New Opportunity</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Opportunity Name"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Amount"
                  type="number"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Stage</InputLabel>
                  <Select defaultValue="prospecting">
                    <MenuItem value="prospecting">Prospecting</MenuItem>
                    <MenuItem value="qualification">Qualification</MenuItem>
                    <MenuItem value="proposal">Proposal</MenuItem>
                    <MenuItem value="negotiation">Negotiation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Probability (%)"
                  type="number"
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Expected Close Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  multiline
                  rows={3}
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenOpportunityDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenOpportunityDialog(false)}>
            Create Opportunity
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}