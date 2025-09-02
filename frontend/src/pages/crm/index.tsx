// frontend/src/pages/crm/index.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Tab,
  Tabs,
} from "@mui/material";
import {
  Add as AddIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  AttachMoney as AttachMoneyIcon,
} from "@mui/icons-material";
import { useAuth } from "@/context/AuthContext";
import { crmService, Lead, Opportunity, CRMAnalytics } from "../../services";
const statusColors: Record<string, string> = {
  new: "default",
  contacted: "info",
  qualified: "warning",
  converted: "success",
  lost: "error",
  nurturing: "secondary",
};
const stageColors: Record<string, string> = {
  prospecting: "default",
  qualification: "info",
  proposal: "warning",
  negotiation: "secondary",
  closed_won: "success",
  closed_lost: "error",
};
export default function CRMDashboard() {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [analytics, setAnalytics] = useState<CRMAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [openLeadDialog, setOpenLeadDialog] = useState(false);
  const [openOpportunityDialog, setOpenOpportunityDialog] = useState(false);
  useEffect(() => {
    loadCRMData();
  }, []);
  const loadCRMData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [leadsData, opportunitiesData, analyticsData] = await Promise.all([
        crmService.getLeads(),
        crmService.getOpportunities(),
        crmService.getAnalytics(),
      ]);
      setLeads(leadsData);
      setOpportunities(opportunitiesData);
      setAnalytics(analyticsData);
    } catch (err: any) {
      console.error("Error loading CRM data:", err);
      setError(err.userMessage || "Failed to load CRM data");
      // Fallback to empty data to prevent crashes
      setLeads([]);
      setOpportunities([]);
      setAnalytics({
        total_leads: 0,
        qualified_leads: 0,
        total_opportunities: 0,
        won_opportunities: 0,
        total_pipeline_value: 0,
        avg_deal_size: 0,
        lead_conversion_rate: 0,
        sales_cycle_length: 0,
        monthly_sales_target: 0,
        monthly_sales_actual: 0,
      });
    } finally {
      setLoading(false);
    }
  };
  const filteredLeads = leads.filter(
    (lead) =>
      (lead.contact_person || "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      lead.lead_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (lead.contact_email || "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      (lead.company_name || "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase()),
  );
  const filteredOpportunities = opportunities.filter(
    (opportunity) =>
      opportunity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opportunity.opportunity_number
        .toLowerCase()
        .includes(searchTerm.toLowerCase()),
  );
  const renderAnalyticsCards = () => {
    if (!analytics) {
      return null;
    }
    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
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
              <Box sx={{ display: "flex", alignItems: "center" }}>
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
              <Box sx={{ display: "flex", alignItems: "center" }}>
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
              <Box sx={{ display: "flex", alignItems: "center" }}>
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
              <TableCell>{lead.company || "-"}</TableCell>
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
                {lead.estimated_value
                  ? `$${lead.estimated_value.toLocaleString()}`
                  : "-"}
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
              <TableCell>
                ${opportunity.expected_revenue.toLocaleString()}
              </TableCell>
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
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          CRM Dashboard
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
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
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button size="small" onClick={loadCRMData} sx={{ ml: 1 }}>
            Retry
          </Button>
        </Alert>
      )}
      {renderAnalyticsCards()}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
            <Tabs
              value={currentTab}
              onChange={(_, newValue) => setCurrentTab(newValue)}
            >
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
                <TextField label="First Name" fullWidth required />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Last Name" fullWidth required />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Email" type="email" fullWidth required />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Phone" fullWidth />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Company" fullWidth />
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
                <TextField label="Estimated Value" type="number" fullWidth />
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
                <TextField label="Opportunity Name" fullWidth required />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField label="Amount" type="number" fullWidth required />
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
                <TextField label="Probability (%)" type="number" fullWidth />
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
                <TextField label="Description" multiline rows={3} fullWidth />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenOpportunityDialog(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => setOpenOpportunityDialog(false)}
          >
            Create Opportunity
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
