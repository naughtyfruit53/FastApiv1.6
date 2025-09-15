"use client";
import React, { useState } from "react";
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
  Download,
  Upload,
  PersonAdd,
  Campaign,
  NotesOutlined,
  Assignment,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";

interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source: string;
  status: "new" | "contacted" | "qualified" | "proposal_sent" | "negotiation" | "won" | "lost";
  score: number;
  priority: "low" | "medium" | "high" | "urgent";
  created_at: string;
  estimated_value?: number;
  expected_close_date?: string;
  last_contact_date?: string;
  assigned_to?: number;
  assigned_to_name?: string;
  tags?: string[];
  notes_count?: number;
  activities_count?: number;
  is_starred?: boolean;
  conversion_probability?: number;
  industry?: string;
  lead_temperature?: "cold" | "warm" | "hot";
}

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

// Mock API functions
const enhancedLeadsApi = {
  getLeads: async (): Promise<Lead[]> => {
    return [
      {
        id: 1,
        first_name: "John",
        last_name: "Smith",
        email: "john.smith@techcorp.com",
        phone: "+1-555-0123",
        company: "TechCorp Solutions",
        job_title: "CTO",
        source: "website",
        status: "qualified",
        score: 85,
        priority: "high",
        created_at: "2024-01-15T10:00:00Z",
        estimated_value: 150000,
        expected_close_date: "2024-03-15",
        last_contact_date: "2024-01-20T14:30:00Z",
        assigned_to: 1,
        assigned_to_name: "Sarah Johnson",
        tags: ["enterprise", "technology", "urgent"],
        notes_count: 5,
        activities_count: 12,
        is_starred: true,
        conversion_probability: 75,
        industry: "Technology",
        lead_temperature: "hot"
      },
      {
        id: 2,
        first_name: "Emily",
        last_name: "Chen",
        email: "emily.chen@retailplus.com",
        phone: "+1-555-0456",
        company: "RetailPlus Inc",
        job_title: "Operations Manager",
        source: "referral",
        status: "contacted",
        score: 65,
        priority: "medium",
        created_at: "2024-01-18T09:15:00Z",
        estimated_value: 75000,
        expected_close_date: "2024-04-01",
        last_contact_date: "2024-01-19T11:00:00Z",
        assigned_to: 2,
        assigned_to_name: "Mike Wilson",
        tags: ["retail", "medium-deal"],
        notes_count: 3,
        activities_count: 7,
        is_starred: false,
        conversion_probability: 45,
        industry: "Retail",
        lead_temperature: "warm"
      }
    ];
  },

  getLeadStats: async (): Promise<LeadStats> => {
    return {
      total_leads: 247,
      new_leads: 23,
      qualified_leads: 45,
      conversion_rate: 23.5,
      avg_deal_size: 125000,
      pipeline_value: 2450000
    };
  },

  getLeadActivities: async (leadId: number): Promise<LeadActivity[]> => {
    return [
      {
        id: 1,
        lead_id: leadId,
        type: "call",
        description: "Initial discovery call - discussed requirements",
        created_at: "2024-01-20T14:30:00Z",
        created_by: "Sarah Johnson"
      },
      {
        id: 2,
        lead_id: leadId,
        type: "email",
        description: "Sent product demo information",
        created_at: "2024-01-19T16:45:00Z",
        created_by: "Sarah Johnson"
      }
    ];
  },

  updateLeadStatus: async (leadId: number, status: Lead["status"]): Promise<void> => {
    console.log("Updating lead status:", leadId, status);
  },

  toggleStarred: async (leadId: number): Promise<void> => {
    console.log("Toggling starred status:", leadId);
  },

  assignLead: async (leadId: number, userId: number): Promise<void> => {
    console.log("Assigning lead:", leadId, "to user:", userId);
  }
};

const EnhancedLeadManagement: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [temperatureFilter, setTemperatureFilter] = useState("all");
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [detailDialog, setDetailDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuLead, setMenuLead] = useState<Lead | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const queryClient = useQueryClient();

  // Fetch leads
  const { data: leads = [], isLoading, error } = useQuery({
    queryKey: ['leads'],
    queryFn: enhancedLeadsApi.getLeads,
  });

  // Fetch lead statistics
  const { data: stats } = useQuery({
    queryKey: ['leadStats'],
    queryFn: enhancedLeadsApi.getLeadStats,
  });

  // Fetch activities for selected lead
  const { data: activities = [] } = useQuery({
    queryKey: ['leadActivities', selectedLead?.id],
    queryFn: () => selectedLead ? enhancedLeadsApi.getLeadActivities(selectedLead.id) : Promise.resolve([]),
    enabled: !!selectedLead && detailDialog,
  });

  // Mutations
  const updateStatusMutation = useMutation({
    mutationFn: ({ leadId, status }: { leadId: number; status: Lead["status"] }) =>
      enhancedLeadsApi.updateLeadStatus(leadId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead status updated");
    },
  });

  const toggleStarredMutation = useMutation({
    mutationFn: enhancedLeadsApi.toggleStarred,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  const assignLeadMutation = useMutation({
    mutationFn: ({ leadId, userId }: { leadId: number; userId: number }) =>
      enhancedLeadsApi.assignLead(leadId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      toast.success("Lead assigned successfully");
    },
  });

  const handleViewDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setDetailDialog(true);
    setAnchorEl(null);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, lead: Lead) => {
    setAnchorEl(event.currentTarget);
    setMenuLead(lead);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuLead(null);
  };

  const getStatusColor = (status: Lead["status"]) => {
    switch (status) {
      case "new": return "primary";
      case "contacted": return "info";
      case "qualified": return "warning";
      case "proposal_sent": return "secondary";
      case "negotiation": return "warning";
      case "won": return "success";
      case "lost": return "error";
      default: return "default";
    }
  };

  const getPriorityColor = (priority: Lead["priority"]) => {
    switch (priority) {
      case "urgent": return "error";
      case "high": return "warning";
      case "medium": return "info";
      case "low": return "default";
      default: return "default";
    }
  };

  const getTemperatureColor = (temperature: Lead["lead_temperature"]) => {
    switch (temperature) {
      case "hot": return "error";
      case "warm": return "warning";
      case "cold": return "info";
      default: return "default";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "success";
    if (score >= 60) return "warning";
    if (score >= 40) return "info";
    return "error";
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Filter leads
  const filteredLeads = leads.filter(lead => {
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
        <Alert severity="error">Failed to load leads</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Advanced Lead Management
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<Upload />}>
            Import Leads
          </Button>
          <Button variant="outlined" startIcon={<Download />}>
            Export
          </Button>
          <Button variant="contained" startIcon={<PersonAdd />}>
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
                {stats?.total_leads || 0}
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
                {stats?.new_leads || 0}
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
                {stats?.qualified_leads || 0}
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
                {stats?.conversion_rate || 0}%
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
                {stats ? formatCurrency(stats.avg_deal_size) : '$0'}
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
                {stats ? formatCurrency(stats.pipeline_value) : '$0'}
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
              <Button variant="outlined" startIcon={<Assessment />}>
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
                    {lead.is_starred ? 
                      <StarIcon color="warning" /> : 
                      <StarBorderIcon />
                    }
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
                    label={lead.status.replace('_', ' ')}
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
                    label={lead.lead_temperature || 'N/A'}
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
                    {lead.estimated_value ? formatCurrency(lead.estimated_value) : 'N/A'}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {lead.conversion_probability}% chance
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {lead.assigned_to_name || 'Unassigned'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {lead.last_contact_date ? 
                      new Date(lead.last_contact_date).toLocaleDateString() : 
                      'Never'
                    }
                  </Typography>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5}>
                    <Tooltip title="View Details">
                      <IconButton 
                        size="small"
                        onClick={() => handleViewDetails(lead)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Call">
                      <IconButton size="small">
                        <PhoneIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Email">
                      <IconButton size="small">
                        <EmailIcon />
                      </IconButton>
                    </Tooltip>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuClick(e, lead)}
                    >
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
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => menuLead && handleViewDetails(menuLead)}>
          <ViewIcon sx={{ mr: 1 }} fontSize="small" />
          View Details
        </MenuItem>
        <MenuItem>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          Edit Lead
        </MenuItem>
        <MenuItem>
          <ScheduleIcon sx={{ mr: 1 }} fontSize="small" />
          Schedule Follow-up
        </MenuItem>
        <MenuItem>
          <Campaign sx={{ mr: 1 }} fontSize="small" />
          Add to Campaign
        </MenuItem>
        <Divider />
        <MenuItem>
          <Assignment sx={{ mr: 1 }} fontSize="small" />
          Convert to Opportunity
        </MenuItem>
      </Menu>

      {/* Lead Detail Dialog */}
      <Dialog
        open={detailDialog}
        onClose={() => setDetailDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">
              {selectedLead?.first_name} {selectedLead?.last_name}
            </Typography>
            <Stack direction="row" spacing={1}>
              <Chip
                label={selectedLead?.status.replace('_', ' ')}
                color={selectedLead ? getStatusColor(selectedLead.status) : 'default'}
                size="small"
              />
              <Chip
                label={selectedLead?.priority}
                color={selectedLead ? getPriorityColor(selectedLead.priority) : 'default'}
                size="small"
              />
            </Stack>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
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
                        <Typography variant="body2">
                          {selectedLead.email}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Phone
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.phone || 'N/A'}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Company
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.company}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Job Title
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.job_title}
                        </Typography>
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
                          {selectedLead.estimated_value ? formatCurrency(selectedLead.estimated_value) : 'N/A'}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Expected Close Date
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.expected_close_date ? 
                            new Date(selectedLead.expected_close_date).toLocaleDateString() : 
                            'N/A'
                          }
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Conversion Probability
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.conversion_probability}%
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Assigned To
                        </Typography>
                        <Typography variant="body2">
                          {selectedLead.assigned_to_name || 'Unassigned'}
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
                      <Chip
                        label={activity.type}
                        size="small"
                        sx={{ mr: 2 }}
                      />
                      <Typography variant="caption" color="textSecondary">
                        {new Date(activity.created_at).toLocaleString()} by {activity.created_by}
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      {activity.description}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          )}

          {activeTab === 2 && (
            <Box textAlign="center" py={4}>
              <NotesOutlined sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No notes yet
              </Typography>
              <Button variant="outlined">Add Note</Button>
            </Box>
          )}

          {activeTab === 3 && (
            <Box textAlign="center" py={4}>
              <Assignment sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No documents attached
              </Typography>
              <Button variant="outlined">Upload Document</Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>
            Close
          </Button>
          <Button variant="contained">
            Edit Lead
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EnhancedLeadManagement;