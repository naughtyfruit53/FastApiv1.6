"use client";
import React, { useState, useEffect } from "react";
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
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Stack,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Menu,
  Tooltip,
  Divider,
  Tab,
  Tabs,
} from "@mui/material";
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  MoreVert as MoreVertIcon,
  Schedule as ScheduleIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  FilterList,
  Assessment,
  Campaign,
  Assignment,
  PersonAdd,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { crmService, Lead } from "../../services/crmService";
import AddLeadModal from "../../components/AddLeadModal";
import LeadsImportExportDropdown from "../../components/LeadsImportExportDropdown";
import { formatCurrency } from "../../utils/currencyUtils";

interface LeadActivity {
  id: number;
  lead_id: number;
  type: "call" | "email" | "meeting" | "note" | "task";
  description: string;
  created_at: string;
  created_by: string;
}

interface LeadStats {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  conversion_rate: number;
  avg_deal_size: number;
  pipeline_value: number;
}

const LeadManagement: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [temperatureFilter, setTemperatureFilter] = useState("all");
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [detailDialog, setDetailDialog] = useState(false);
  const [addDialog, setAddDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuLead, setMenuLead] = useState<Lead | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Fetch leads using real API
  const { data: leads = [], isLoading, error } = useQuery({
    queryKey: ['leads'],
    queryFn: async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No authentication token found. Please log in.");
      }
      return crmService.getLeads();
    },
    retry: false,
  });

  // Fetch analytics for stats
  const { data: analytics } = useQuery({
    queryKey: ['crmAnalytics'],
    queryFn: async () => {
      const periodEnd = new Date();
      const periodStart = new Date(periodEnd);
      periodStart.setDate(periodEnd.getDate() - 30);
      return crmService.getAnalytics({
        period_start: periodStart.toISOString().split('T')[0],
        period_end: periodEnd.toISOString().split('T')[0],
      });
    },
    retry: false,
  });

  const stats: LeadStats = {
    total_leads: analytics?.leads_total || 0,
    new_leads: analytics?.leads_by_status?.new || 0,
    qualified_leads: analytics?.leads_by_status?.qualified || 0,
    conversion_rate: analytics?.conversion_rate || 0,
    avg_deal_size: analytics?.average_deal_size || 0,
    pipeline_value: analytics?.pipeline_value || 0,
  };

  // Fetch activities for selected lead
  const { data: activities = [] } = useQuery({
    queryKey: ['leadActivities', selectedLead?.id],
    queryFn: () => crmService.getLeadActivities(selectedLead?.id || 0),
    enabled: !!selectedLead && detailDialog,
  });

  // Mutations
  const updateStatusMutation = useMutation({
    mutationFn: ({ leadId, status }: { leadId: number; status: Lead["status"] }) =>
      crmService.updateLead(leadId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead status updated");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to update lead status");
    },
  });

  const toggleStarredMutation = useMutation({
    mutationFn: (leadId: number) => {
      // TODO: Implement toggle starred API call
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead starred status updated");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to update starred status");
    },
  });

  const assignLeadMutation = useMutation({
    mutationFn: ({ leadId, userId }: { leadId: number; userId: number }) => {
      // TODO: Implement assign lead API call
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead assigned successfully");
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to assign lead");
    },
  });

  const createLeadMutation = useMutation({
    mutationFn: crmService.createLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead created successfully");
      setAddDialog(false);
    },
    onError: (err: any) => {
      toast.error(err.message || "Failed to create lead");
    },
  });

  const handleViewDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setDetailDialog(true);
    setAnchorEl(null);
  };

  const handleEditLead = (lead: Lead) => {
    toast.info("Edit lead functionality not implemented yet");
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, lead: Lead) => {
    setAnchorEl(event.currentTarget);
    setMenuLead(lead);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuLead(null);
  };

  const handleAddLead = () => {
    setAddDialog(true);
  };

  const handleImportLeads = (importedLeads: any[]) => {
    importedLeads.forEach(leadData => {
      createLeadMutation.mutate(leadData);
    });
  };

  const handleCall = () => {
    toast.info("Call functionality not implemented yet");
  };

  const handleEmail = () => {
    toast.info("Email functionality not implemented yet");
  };

  const handleScheduleFollowUp = () => {
    toast.info("Schedule Follow-up functionality not implemented yet");
  };

  const handleAddToCampaign = () => {
    toast.info("Add to Campaign functionality not implemented yet");
  };

  const handleConvertToOpportunity = () => {
    toast.info("Convert to Opportunity functionality not implemented yet");
  };

  const handleViewAnalytics = () => {
    try {
      router.push('/analytics/customer');
    } catch (error) {
      toast.error('Failed to navigate to analytics page');
      console.error('Navigation error:', error);
    }
  };

  const getStatusColor = (status: Lead["status"]) => {
    switch (status) {
      case "new":
        return "primary";
      case "contacted":
        return "info";
      case "qualified":
        return "warning";
      case "proposal_sent":
        return "secondary";
      case "negotiation":
        return "warning";
      case "won":
        return "success";
      case "lost":
        return "error";
      default:
        return "default";
    }
  };

  const getPriorityColor = (priority: Lead["priority"]) => {
    switch (priority) {
      case "urgent":
        return "error";
      case "high":
        return "warning";
      case "medium":
        return "info";
      case "low":
        return "default";
      default:
        return "default";
    }
  };

  const getTemperatureColor = (temperature: Lead["lead_temperature"]) => {
    switch (temperature) {
      case "hot":
        return "error";
      case "warm":
        return "warning";
      case "cold":
        return "info";
      default:
        return "default";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    if (score >= 40) return "info";
    return "error";
  };

  const filteredLeads = leads.filter((lead) => {
    const matchesSearch =
      lead.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "all" || lead.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || lead.priority === priorityFilter;
    const matchesTemperature = temperatureFilter === "all" || lead.lead_temperature === temperatureFilter;

    return matchesSearch && matchesStatus && matchesPriority && matchesTemperature;
  });

  // Redirect to login if no token
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token && !isLoading && error?.message.includes("No authentication token")) {
      router.push("/login");
    }
  }, [error, isLoading, router]);

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          {error.message || "Failed to load leads"}
          <Button
            variant="outlined"
            size="small"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['leads'] })}
            sx={{ ml: 2 }}
          >
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Lead Management
        </Typography>
        <Stack direction="row" spacing={2}>
          <LeadsImportExportDropdown leads={leads} onImport={handleImportLeads} />
          <Button variant="contained" startIcon={<PersonAdd />} onClick={handleAddLead}>
            Add Lead
          </Button>
        </Stack>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Leads
              </Typography>
              <Typography variant="h5" component="div">
                {stats.total_leads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                New This Week
              </Typography>
              <Typography variant="h5" component="div" color="primary.main">
                {stats.new_leads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Qualified
              </Typography>
              <Typography variant="h5" component="div" color="warning.main">
                {stats.qualified_leads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Conversion Rate
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {stats.conversion_rate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Avg Deal Size
              </Typography>
              <Typography variant="h5" component="div">
                {formatCurrency(stats.avg_deal_size)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Pipeline Value
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {formatCurrency(stats.pipeline_value)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              placeholder="Search leads..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="new">New</MenuItem>
                <MenuItem value="contacted">Contacted</MenuItem>
                <MenuItem value="qualified">Qualified</MenuItem>
                <MenuItem value="proposal_sent">Proposal Sent</MenuItem>
                <MenuItem value="negotiation">Negotiation</MenuItem>
                <MenuItem value="won">Won</MenuItem>
                <MenuItem value="lost">Lost</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={priorityFilter}
                label="Priority"
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <MenuItem value="all">All Priorities</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Temperature</InputLabel>
              <Select
                value={temperatureFilter}
                label="Temperature"
                onChange={(e) => setTemperatureFilter(e.target.value)}
              >
                <MenuItem value="all">All Temperatures</MenuItem>
                <MenuItem value="hot">Hot</MenuItem>
                <MenuItem value="warm">Warm</MenuItem>
                <MenuItem value="cold">Cold</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setStatusFilter("all");
                  setPriorityFilter("all");
                  setTemperatureFilter("all");
                  setSearchTerm("");
                }}
              >
                Clear Filters
              </Button>
              <Button variant="outlined" startIcon={<Assessment />} onClick={handleViewAnalytics}>
                Analytics
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {/* Leads Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox"></TableCell>
              <TableCell>Lead</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Temperature</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Value</TableCell>
              <TableCell>Assigned To</TableCell>
              <TableCell>Last Contact</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredLeads.map((lead) => (
              <TableRow key={lead.id} hover>
                <TableCell padding="checkbox">
                  <IconButton
                    size="small"
                    onClick={() => toggleStarredMutation.mutate(lead.id)}
                  >
                    {lead.is_starred ? <StarIcon color="warning" /> : <StarBorderIcon />}
                  </IconButton>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Avatar sx={{ mr: 2, width: 40, height: 40 }}>
                      {lead.first_name.charAt(0)}{lead.last_name.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2" fontWeight="medium">
                        {lead.first_name} {lead.last_name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {lead.email}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {lead.job_title}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {lead.company}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {lead.industry}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={lead.status.replace("_", " ")}
                    color={getStatusColor(lead.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={lead.priority}
                    color={getPriorityColor(lead.priority)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={lead.lead_temperature || "N/A"}
                    color={getTemperatureColor(lead.lead_temperature)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <LinearProgress
                      variant="determinate"
                      value={lead.score}
                      color={getScoreColor(lead.score)}
                      sx={{ width: 60, mr: 1 }}
                    />
                    <Typography variant="body2">{lead.score}</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {lead.estimated_value ? formatCurrency(lead.estimated_value) : "N/A"}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {lead.conversion_probability}% chance
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{lead.assigned_to_name || "Unassigned"}</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {lead.last_contact_date ? new Date(lead.last_contact_date).toLocaleDateString() : "Never"}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5}>
                    <Tooltip title="View Details">
                      <IconButton size="small" onClick={() => handleViewDetails(lead)}>
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Call">
                      <IconButton size="small" onClick={handleCall}>
                        <PhoneIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Email">
                      <IconButton size="small" onClick={handleEmail}>
                        <EmailIcon />
                      </IconButton>
                    </Tooltip>
                    <IconButton size="small" onClick={(e) => handleMenuClick(e, lead)}>
                      <MoreVertIcon />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredLeads.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No leads found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Try adjusting your search criteria or add new leads
          </Typography>
        </Box>
      )}

      {/* Action Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={() => menuLead && handleViewDetails(menuLead)}>
          <ViewIcon sx={{ mr: 1 }} fontSize="small" />
          View Details
        </MenuItem>
        <MenuItem onClick={() => menuLead && handleEditLead(menuLead)}>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          Edit Lead
        </MenuItem>
        <MenuItem onClick={handleScheduleFollowUp}>
          <ScheduleIcon sx={{ mr: 1 }} fontSize="small" />
          Schedule Follow-up
        </MenuItem>
        <MenuItem onClick={handleAddToCampaign}>
          <Campaign sx={{ mr: 1 }} fontSize="small" />
          Add to Campaign
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleConvertToOpportunity}>
          <Assignment sx={{ mr: 1 }} fontSize="small" />
          Convert to Opportunity
        </MenuItem>
      </Menu>

      {/* Add Lead Modal */}
      <AddLeadModal
        open={addDialog}
        onClose={() => setAddDialog(false)}
        onAdd={async (data) => {
          await createLeadMutation.mutateAsync(data);
        }}
        loading={createLeadMutation.isPending}
      />

      {/* Lead Detail Dialog */}
      <Dialog open={detailDialog} onClose={() => setDetailDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">
              {selectedLead?.first_name} {selectedLead?.last_name}
            </Typography>
            <Stack direction="row" spacing={1}>
              <Chip
                label={selectedLead?.status.replace("_", " ")}
                color={selectedLead ? getStatusColor(selectedLead.status) : "default"}
                size="small"
              />
              <Chip
                label={selectedLead?.priority}
                color={selectedLead ? getPriorityColor(selectedLead.priority) : "default"}
                size="small"
              />
            </Stack>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Overview" />
              <Tab label="Activities" />
              <Tab label="Notes" />
              <Tab label="Documents" />
            </Tabs>
          </Box>

          {activeTab === 0 && selectedLead && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Contact Information
                    </Typography>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Email
                        </Typography>
                        <Typography variant="body2">{selectedLead.email}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Phone
                        </Typography>
                        <Typography variant="body2">{selectedLead.phone || "N/A"}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Company
                        </Typography>
                        <Typography variant="body2">{selectedLead.company}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Job Title
                        </Typography>
                        <Typography variant="body2">{selectedLead.job_title}</Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Lead Details
                    </Typography>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Lead Score
                        </Typography>
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={selectedLead.score}
                            color={getScoreColor(selectedLead.score)}
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">{selectedLead.score}/100</Typography>
                        </Box>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Estimated Value
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.estimated_value ? formatCurrency(selectedLead.estimated_value) : "N/A"}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Expected Close Date
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.expected_close_date ? new Date(selectedLead.expected_close_date).toLocaleDateString() : "N/A"}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Conversion Probability
                        </Typography>
                        <Typography variant="body2">{selectedLead.conversion_probability}%</Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Assigned To
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.assigned_to_name || "Unassigned"}
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {activeTab === 1 && (
            <Stack spacing={2}>
              {activities.map((activity) => (
                <Card key={activity.id} variant="outlined">
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Chip label={activity.type} size="small" sx={{ mr: 2 }} />
                      <Typography variant="caption" color="textSecondary">
                        {new Date(activity.created_at).toLocaleString()} by {activity.created_by}
                      </Typography>
                    </Box>
                    <Typography variant="body2">{activity.description}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          )}

          {activeTab === 2 && (
            <Box textAlign="center" py={4}>
              <NotesOutlined sx={{ fontSize: 48, color: "grey.400", mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No notes yet
              </Typography>
              <Button variant="outlined">Add Note</Button>
            </Box>
  )}

  {activeTab === 3 && (
    <Box textAlign="center" py={4}>
      <Assignment sx={{ fontSize: 48, color: "grey.400", mb: 2 }} />
      <Typography variant="h6" color="textSecondary" gutterBottom>
        No documents attached
      </Typography>
      <Button variant="outlined">Upload Document</Button>
    </Box>
  )}
</DialogContent>
<DialogActions>
  <Button onClick={() => setDetailDialog(false)}>Close</Button>
  <Button variant="contained" onClick={() => selectedLead && handleEditLead(selectedLead)}>
    Edit Lead
  </Button>
</DialogActions>
</Dialog>
</Container>
  );
};

export default LeadManagement;